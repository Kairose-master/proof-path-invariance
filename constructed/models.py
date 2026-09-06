"""Three constructed recognizers.

A. SetRecognizer: each clause is encoded independently by a small
   transformer; clause vectors are max-pooled (permutation-invariant and
   idempotent), concatenated with the query encoding, and read out.  By
   construction, permuting or repeating clauses cannot change the output.
B/C. SeqRecognizer: a causal transformer over the full token sequence,
   read at the last position.  B is trained with permutation/repetition
   augmentation, C without.  Same parameter count.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from horn_data import VOCAB, TOK


class Block(nn.Module):
    def __init__(self, d, heads, causal):
        super().__init__()
        self.attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        self.n1 = nn.LayerNorm(d)
        self.n2 = nn.LayerNorm(d)
        self.causal = causal

    def forward(self, x, pad_mask=None):
        h = self.n1(x)
        L = x.shape[1]
        mask = torch.triu(torch.ones(L, L, dtype=torch.bool, device=x.device), 1) if self.causal else None
        a, _ = self.attn(h, h, h, attn_mask=mask, key_padding_mask=pad_mask, need_weights=False)
        x = x + a
        return x + self.ff(self.n2(x))


class SeqRecognizer(nn.Module):
    def __init__(self, d=64, heads=4, layers=2, max_len=64):
        super().__init__()
        self.emb = nn.Embedding(len(VOCAB), d)
        self.pos = nn.Embedding(max_len, d)
        self.blocks = nn.ModuleList([Block(d, heads, causal=True) for _ in range(layers)])
        self.norm = nn.LayerNorm(d)
        self.out = nn.Linear(d, 2)

    def forward(self, ids):
        L = ids.shape[1]
        x = self.emb(ids) + self.pos(torch.arange(L, device=ids.device))[None]
        for b in self.blocks:
            x = b(x)
        return self.out(self.norm(x[:, -1]))


class SetRecognizer(nn.Module):
    def __init__(self, d=64, heads=4, layers=2, clause_len=6):
        super().__init__()
        self.emb = nn.Embedding(len(VOCAB), d)
        self.pos = nn.Embedding(clause_len, d)
        self.clause_blocks = nn.ModuleList([Block(d, heads, causal=False) for _ in range(layers)])
        self.qpos = nn.Embedding(4, d)
        self.query_blocks = nn.ModuleList([Block(d, heads, causal=False) for _ in range(1)])
        self.norm = nn.LayerNorm(d)
        self.head = nn.Sequential(nn.Linear(2 * d, 2 * d), nn.GELU(), nn.Linear(2 * d, 2))

    def forward(self, clause_ids, query_ids):
        # clause_ids: (B, C, T); query_ids: (B, 4)
        B, C, T = clause_ids.shape
        x = clause_ids.reshape(B * C, T)
        pad = x == TOK["<pad>"]
        h = self.emb(x) + self.pos(torch.arange(T, device=x.device))[None]
        for b in self.clause_blocks:
            h = b(h, pad_mask=pad)
        h = h.masked_fill(pad[..., None], 0).sum(1) / (~pad).sum(1, keepdim=True).clamp(min=1)
        h = h.reshape(B, C, -1)
        valid = (clause_ids != TOK["<pad>"]).any(-1)              # (B, C)
        h = h.masked_fill(~valid[..., None], -1e4).max(1).values   # max-pool: invariant + idempotent
        q = self.emb(query_ids) + self.qpos(torch.arange(4, device=query_ids.device))[None]
        for b in self.query_blocks:
            q = b(q)
        q = q.mean(1)
        return self.head(torch.cat([self.norm(h), self.norm(q)], -1))
