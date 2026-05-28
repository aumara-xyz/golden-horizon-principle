# Golden Zipper Observer-Memory Experiment Audit

Toy telemetry only. Not physics evidence. Not proof of GHP. Do not harden the master from this note.

## Executive Summary

The early Golden Zipper tests did not support exact phi uniqueness. Later tests moved away from "which number wins?" and toward "what makes an observer write memory?" That shift was productive.

The strongest surviving primitive is:

> memory-like writing appears when surprise causes model revision, not when surprise is merely intense.

The weakest surviving claim is:

> golden/phi or torus geometry is necessary for the effect.

Current recommendation: ledger-only candidate after one more targeted null, no master hardening, no core-paper change.

## What Failed

Exact phi did not robustly win. It sometimes performed well, but near-golden, noble, bounded-CF, rational approximants, constants, and random-CF controls repeatedly competed or beat it.

Binary/Sturmian balance was not the right target. Rationals often won clean balance because they repeat, which is readable but phase-locked.

Torus/contact-ring geometry did not become decisive. Some sphere/torus projections helped compared with flat string models, but random projection and phase scrambling could match or beat the real geometry.

Afterglow/persistence did not help in the naive form. Broad glow smeared the signal and made surrogates easier to match.

Hard identity gating failed. It protected the observer so strongly that almost nothing useful was admitted.

Short-horizon predictive usefulness failed. Asking whether a surprise helps predict the next few steps was too narrow for big memory events.

## What Survived

Two-light/appearance alignment was a better toy than raw binary strings, but it was not enough by itself.

Observer-first framing improved the questions. The right target became "what does the observer admit and write?" rather than "which alpha wins?"

Assimilated surprise beat raw writing but did not beat surprise-only. That suggested surprise matters, but surprise must be made meaningful.

Model revision was the first clean positive:

- v19: model revision beat surprise-only and had a strong positive surrogate gap.
- v19b: model revision survived a wider robustness sweep and beat density/block surrogates.
- v19c: real sequences beat their own density, block, and Markov surrogates, but random projection and phase scrambling beat the real geometry.
- v20: adding a simple embodied instability cost did not separate real geometry from random projection.

## Plain-Language Interpretation

An ordinary surprise is just a loud flash.

A memory is different: it is a flash that makes the observer change the rules it thinks it is living by.

The current toy supports this kind of sentence:

> In observer-memory telemetry, a write is better modeled as surprise-driven model revision than as raw surprise or raw recurrence.

It does not support:

> Phi uniquely causes memory.

It also does not yet support:

> Torus/sphere geometry is necessary for memory.

## Current Best Hypothesis

The best current hypothesis is not Golden Zipper as a phi-specific mechanism. It is:

> Observer memory forms when an appearance crosses the observer boundary as a surprise that can revise the observer's model without collapsing coherence.

Phi may still belong as an anti-locking architectural motif, but the toy has not shown phi as the write-point.

## Strongest Skeptical Objection

The model-revision score may still reward generic novelty under another name. Random projection and phase scrambling beating real flow in v19c/v20 is the warning sign.

If a scrambled or random projection creates the same or better model-revision score, then the toy is not measuring special observer geometry. It is measuring an abstract revision event that can happen in many signal streams.

## What Would Falsify The Current Direction

The model-revision direction should be weakened or dropped if:

- Markov or phase-randomized controls keep matching or beating real sequences after better coherence costs.
- Model revision only wins because the composite score rewards revision directly.
- Removing the explicit revision-score term collapses the advantage.
- Real sequences do not improve under more realistic observer coherence constraints.
- The effect disappears when the observer has a richer baseline model.

## What To Test Next

The next test should not add another decorative geometry. It should attack the scoring itself.

Recommended next test:

`golden_zipper_v21_revision_ablation_panel.py`

Core question:

> Does model revision still win if we remove the explicit reward for revision and score only downstream behavior?

Compare:

- surprise-only
- model-revision
- model-revision-witness
- random projection
- phase scrambled
- Markov surrogate

Remove or sharply reduce direct scoring of:

- revision rate
- revision size

Keep only downstream metrics:

- delayed retention
- pollution
- phase-lock resistance
- write/witness balance
- stability/coherence after write
- surrogate gaps

Success:

> Model revision still beats surprise-only and nulls when revision itself is not directly rewarded.

Failure:

> Model revision was partly score-selected and should remain symbolic only.

## Hardening Recommendation

No master hardening.

No Core Share Paper change.

Research-ledger note is reasonable only after v21 if model revision survives the scoring ablation.

Current status:

> promising toy lane, not a canon result.

