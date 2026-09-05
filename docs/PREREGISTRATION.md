# Phase 1 Preregistration Draft

Status: **DRAFT — no confirmatory model run should be interpreted until this file is frozen.**

## Research question

For a fixed formally certified entailment problem, does reversing the serialization order of the same premise multiset change an LLM's final binary entailment judgment?

This phase tests presentation stability only. It does not test proof identity, decomposition, composition, functoriality, category structure, or internal semantics.

## Experimental unit

A paired item consists of:

- one certified formal case `q`;
- a base rendering `E(q)`;
- a premise-reversed rendering `E_rev(q)`.

The two renderings must have:

- the same case identifier;
- the same formal certificate;
- the same gold label;
- the same query;
- the same premise multiset;
- no added or removed premise;
- no lexical rewrite other than list order.

## Primary outcome

For each pair:

`flip(q) = 1[answer_base != answer_reverse]`

where answers are valid only when they normalize exactly to `YES` or `NO`.

Primary descriptive statistic:

`mean_flip = sum flip(q) / number_of_valid_pairs`

Invalid-format responses are reported separately and are not silently coerced.

## Secondary outcomes

These are exploratory unless this document is frozen with a more specific plan:

- accuracy of base renderings;
- accuracy of reversed renderings;
- directional flips `YES -> NO` and `NO -> YES`;
- flip rate stratified by gold label;
- flip rate stratified by certificate family.

## Confirmatory transformation

Only `premise_reverse` is confirmatory in benchmark v0.

Other transformations in the registry are disabled for Phase 1 unless this preregistration is explicitly revised before model outputs are collected.

## Model protocol to freeze before evaluation

Record for every run:

- provider;
- exact model identifier/version;
- access date;
- system prompt, if any;
- user prompt template;
- temperature;
- top-p;
- max output tokens;
- seed, if supported;
- number of repeated samples per prompt;
- any constrained-decoding or response-format setting.

Do not mix silent model-version changes inside one confirmatory analysis.

## Sampling plan

Not yet frozen.

Before confirmatory evaluation, specify:

- number of distinct certified cases;
- positive/negative balance;
- number of repeated samples per prompt;
- rationale for the chosen sample size;
- whether cases are generated or manually authored;
- exclusion rules.

## Exclusions

A response is invalid only for a preregistered mechanical reason such as failure to output exactly `YES` or `NO` after whitespace trimming and case normalization.

Do not exclude a pair because its result is surprising.

## Interpretation boundary

A nonzero flip rate supports only the statement that observed judgments depend on premise serialization order under the tested protocol.

It does **not** by itself establish:

- failure of logical composition;
- failure of proof invariance;
- categorical non-functoriality;
- an internal representation defect;
- lack of logical competence in general.

Any stronger claim requires a separate experimental design.
