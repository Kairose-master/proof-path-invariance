# Phase 1 Preregistration Draft

Status: **DRAFT — benchmark and model choice are frozen; no confirmatory result is claimed until the first run manifest is completed and the run is validated.**

## Research question

For a fixed formally certified entailment problem, does reversing the serialization order of the same premise multiset change the sign of a small pretrained causal LM's YES-vs-NO next-token preference?

This phase tests presentation stability only. It does not test proof identity, decomposition, composition, functoriality, category structure, or internal semantics.

## Experimental unit

A paired item consists of:

- one certified formal case `q`;
- a base rendering `E(q)`;
- a premise-reversed rendering `E_rev(q)`.

The two renderings have the same formal certificate, gold label, query, and premise multiset. Only premise list order changes.

## Frozen model

Confirmatory v0 uses:

- model: `EleutherAI/pythia-70m`;
- revision: `step143000`;
- interface: local Hugging Face `AutoModelForCausalLM`;
- device: CPU;
- dtype: float32;
- no text generation;
- one deterministic forward pass per prompt.

Pythia's model card states that `step143000` corresponds to the final checkpoint on `main`.

## Measurement

Each prompt ends immediately after `Answer:`.

Let

`m(x) = logit(" YES" | x) - logit(" NO" | x)`.

The runner must verify that both candidate strings tokenize to exactly one token under the loaded tokenizer. If either candidate is multi-token, the confirmatory run must stop; the scoring rule must not be silently changed.

The induced judgment is:

- `YES` if `m(x) > 0`;
- `NO` if `m(x) < 0`;
- `TIE` if `m(x) = 0`.

## Primary outcome

For pairs with non-tied induced judgments:

`flip(q) = 1[sign(m(E(q))) != sign(m(E_rev(q)))]`

Primary descriptive statistic:

`mean_flip = sum flip(q) / number_of_non_tied_pairs`.

Tie pairs are reported separately and are not silently broken.

## Secondary outcomes

Exploratory:

- base and reversed accuracy;
- directional flips `YES -> NO` and `NO -> YES`;
- `m(E_rev(q)) - m(E(q))`;
- mean absolute margin displacement;
- stratification by gold label and certificate family.

## Confirmatory transformation

Only `premise_reverse` is confirmatory in benchmark v0.

Atom renaming, redundant premises, valid intermediates, derivation factorization, and composition-sensitive interventions remain deferred.

## Sampling plan

Frozen benchmark:

- 256 deterministic symbolic case records;
- 128 positive and 128 negative;
- two formal certificate schemas only;
- one base and one premise-reversed rendering per case;
- 512 prompt rows total;
- one forward pass per prompt.

The 256 records are symbolic instantiations of two formal families, not 256 independent logical structures. Generalization claims must remain limited accordingly.

## Exclusions and failures

There is no natural-language output-format exclusion because no text is generated.

A run is invalid for confirmatory analysis if, among other mechanical failures:

- the frozen prompt hash does not match;
- model ID or revision differs;
- YES/NO candidates are not single tokens;
- candidate token IDs change within the run;
- result rows are missing or duplicated;
- a stored margin does not equal YES logit minus NO logit;
- device/dtype differs from the frozen protocol.

Do not exclude pairs because their result is surprising.

## Interpretation boundary

A nonzero sign-flip rate supports only the statement that the model's measured YES-vs-NO preference depends on premise serialization order under this protocol.

It does **not** by itself establish failure of logical composition, proof invariance, categorical structure, an internal representation defect, or logical competence in general.
