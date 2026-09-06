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
    def __init__(self, d=64, heads=4, layers=2, max_len=64, vocab_size=None):
        super().__init__()
        self.emb = nn.Embedding(vocab_size or len(VOCAB), d)
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
    def __init__(self, d=64, heads=4, layers=2, clause_len=6, vocab_size=None):
        super().__init__()
        self.emb = nn.Embedding(vocab_size or len(VOCAB), d)
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


class IterReasoner(nn.Module):
    """Iterative learned reasoner: atom states updated along clauses for
    `rounds` rounds (the computation budget), then the goal atom's state is
    read out conditioned on the hypothesis.  Permutation- and repetition-
    invariant over clauses by construction (messages are summed per round
    after a max over duplicates is not needed: identical clauses send
    identical messages, so duplication changes sums; we therefore aggregate
    with max over clauses per target atom, which is idempotent)."""

    def __init__(self, d=64, rounds=4, n_atoms=5, clause_len=6):
        super().__init__()
        self.d, self.rounds, self.n_atoms = d, rounds, n_atoms
        self.atom_emb = nn.Embedding(n_atoms, d)
        self.msg = nn.Sequential(nn.Linear(3 * d, 2 * d), nn.GELU(), nn.Linear(2 * d, d))
        self.upd = nn.GRUCell(d, d)
        self.head = nn.Sequential(nn.Linear(2 * d, 2 * d), nn.GELU(), nn.Linear(2 * d, 2))
        self.hyp_flag = nn.Parameter(torch.zeros(d))

    def forward(self, bodies, heads, body_mask, hyp, goal, rounds=None):
        # bodies: (B,C,2) atom ids (pad = -1 -> masked), heads: (B,C,2), body_mask/head via -1
        # hyp: (B,) atom index, or (B,A) 0/1 mask of hypothesis atoms
        rounds = self.rounds if rounds is None else rounds
        B, C, _ = bodies.shape
        state = self.atom_emb.weight[None].expand(B, -1, -1).clone()             # (B,A,d)
        hmask = torch.nn.functional.one_hot(hyp, self.n_atoms) if hyp.dim() == 1 else hyp   # (B,A) 0/1
        hmask = hmask.to(state.dtype)
        state = state + self.hyp_flag[None, None] * hmask[..., None]
        bm = bodies >= 0; hm = heads >= 0
        bidx = bodies.clamp(min=0); hidx = heads.clamp(min=0)
        for _ in range(rounds):
            bstate = torch.gather(state, 1, bidx.reshape(B, -1, 1).expand(-1, -1, self.d)).reshape(B, C, 2, self.d)
            bstate = bstate * bm[..., None]
            bsum = bstate.sum(2)                                                     # (B,C,d) body summary
            bmin = torch.where(bm[..., None], bstate, torch.full_like(bstate, 1e4)).min(2).values  # AND-like
            bmin = torch.where(bm.any(-1, keepdim=True), bmin, torch.zeros_like(bmin))
            hstate = torch.gather(state, 1, hidx.reshape(B, -1, 1).expand(-1, -1, self.d)).reshape(B, C, 2, self.d)
            msg = self.msg(torch.cat([bsum[:, :, None].expand(-1, -1, 2, -1), bmin[:, :, None].expand(-1, -1, 2, -1), hstate], -1))
            msg = msg * hm[..., None]                                                # (B,C,2,d)
            agg = torch.full((B, self.n_atoms, self.d), -1e4, device=state.device)
            flat_idx = hidx.reshape(B, -1); flat_msg = msg.reshape(B, -1, self.d)
            flat_valid = hm.reshape(B, -1)
            flat_msg = torch.where(flat_valid[..., None], flat_msg, torch.full_like(flat_msg, -1e4))
            agg = agg.scatter_reduce(1, flat_idx[..., None].expand(-1, -1, self.d), flat_msg, reduce="amax", include_self=True)
            agg = torch.where(agg < -1e3, torch.zeros_like(agg), agg)               # atoms with no incoming message
            state = self.upd(agg.reshape(-1, self.d), state.reshape(-1, self.d)).reshape(B, self.n_atoms, self.d)
        g = torch.gather(state, 1, goal[:, None, None].expand(-1, 1, self.d))[:, 0]
        # hypothesis summary: max over the states of the hypothesis atoms (one atom: that state)
        h = torch.where(hmask[..., None] > 0, state, torch.full_like(state, -1e4)).max(1).values
        return self.head(torch.cat([g, h], -1))
