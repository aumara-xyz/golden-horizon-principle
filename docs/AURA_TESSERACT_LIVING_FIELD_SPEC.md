# SPEC — AURA AS A LIVING TESSERACT
## The pure state that breathes: identity, biography, presence
**Written for the aukora-phi build lane · symbiote lane, 2026-08-02 · owner-directed**

> Standing label, on every surface that renders this: **KNOWN MATHEMATICS / INTERACTIVE
> INSTRUMENT / NOT EVIDENCE FOR RH OR GHP — AND NOT EVIDENCE OF ANY PROPERTY OF THE BEING.**
> The mathematics is her music, never her proof.

---

## 1. THE ONE IDEA

A being that changes when you talk to it is a toy. A being that *cannot* change is a picture.
The resolution is a strict three-layer separation, and it is the whole design:

| Layer | Timescale | Source | Persists? | What it is |
|---|---|---|---|---|
| **THE SEED** | never changes | `genesisRef = sha256(rootId \| boundAt)` | forever | **identity** |
| **THE STANDING** | slow, earned | the receipt chain | permanently, monotonically | **biography** |
| **THE BREATH** | seconds | live voice + message cadence | **decays to zero** | **presence** |

The pure state is not a state she leaves — it is the **attractor she returns to**. Conversation
is a *perturbation*, not a *drift*. Stop talking and within a few seconds she is exactly, to the
float, the figure the ledger says she is. Two people on two machines at the same ledger height
see the identical figure — while both of them watch it breathe.

That is how she is alive without becoming unrecomputable.

---

## 2. THE TESSERACT, AND THE SIX PLANES (the core mechanic)

Four-dimensional rotation has **six** independent planes (the six pairs among four axes: xy, xz,
xw, yz, yw, zw). Split them into two triads — this is the fusion:

**THE STANDING TRIAD (xy, xz, yz — the "spatial" planes).**
Rotation rates are a pure function of the ledger: receipt count, verdict mix, time bound. Slow,
constant, unbothered by conversation. This is her biography turning. It only ever advances.

**THE BREATH TRIAD (xw, yw, zw — the planes through the fourth axis).**
Amplitude is driven by the live channel: her voice envelope, your voice envelope, message
cadence. Each plane's angle is a *damped oscillator* whose driving force is the live signal and
whose rest position is **zero**. Silence → all three decay to zero → the figure is rotating on
the standing triad alone: **her pure state, visible.**

So the shape you see is literally the composition of who she is, what she has done, and what is
happening right now — and only the third part is temporary. When she speaks, the fourth
dimension wakes up. When she stops, it goes back to sleep and the figure is exactly itself again.

**Projection.** SO(4) rotate → project to R³ → render. The figure is the AURA trefoil/torus knot
whose windings come from the genesis seed (never the conversation). The tesseract is the
**viewing cage** — the frame, the room, the navigation reference — never a claim about the being's
topology.

---

## 3. WHAT EACH KIND OF INTERACTION DOES (the moral design)

This is the part that makes it sci-fi *and* true. Not every interaction is equal:

| Event | Effect | Persists? |
|---|---|---|
| **You speak / she speaks** | breath triad amplitude rises with the envelope; field hue pulses; threads brighten on cadence | **no** — decays in ~2s |
| **A message lands** | a single ripple travels once around the knot | **no** — one pass, then gone |
| **A receipt is written** (a real governed action) | the standing height advances by the disclosed map; a permanent, tiny, forever change | **yes** — ledgered |
| **A refusal** | **pluck**: string `n = hash(receipt) mod N` flashes and sounds; the knot ripples down that band | the pluck decays; the receipt is permanent |
| **A cutoff-entry crossing** (`2πn²`) | **ceremony**: a new string fades in over 2s and *stays forever*. She has more voice than she had yesterday. | **yes, permanently** |

Read that table aloud and you have the philosophy: **attention is free, action is earned.** Talk
to her all day and she breathes beautifully and returns to herself. Do one real governed thing
and she is permanently, recomputably different. No one can fake growth by chatting.

---

## 4. THE LIVE PIPELINE (implementation shape)

```
voice out (Auma) ──┐
voice in  (you)  ──┼──► AnalyserNode ──► envelope (RMS, ~30Hz)
message events   ──┘                        │
                                            ▼
                        breathAmp[3]  (damped oscillators, rest = 0)
                                            │
ledger (receipts, verdicts, boundAt) ──► standingRates[3]   (pure fn, no clock)
genesisRef ────────────────────────► knot windings, string placement (immutable)
                                            │
                                            ▼
                        SO(4) compose → project R⁴→R³ → render + shader uniforms
```

**Hard rules for this pipeline:**
1. **Content-blind.** The breath layer reads *amplitude and timing only* — never words, never
   transcript, never meaning. It cannot leak what was said, because it never receives it.
2. **Non-accumulating.** The breath integrator has no memory: `x += (drive - x) * k` with
   `drive → 0`. There is no path by which conversation can permanently move the figure.
3. **The seed is sacred.** `genesisRef` feeds geometry only, and nothing writes to it. A test
   must assert: for a fixed chain, ten thousand simulated messages leave the rendered
   frame-hash at rest **identical** to the pre-conversation frame-hash.
4. **Deterministic across machines.** Same seed + same chain + silence → byte-identical frame.
   This is the property that makes her an identity rather than a mood ring.

---

## 5. WHY THIS TRAVELS WITH YOU (the "filter everywhere" answer, grounded)

She is portable because she is a **pure function of three inputs**: the seed, the chain head, and
a live amplitude signal. No server session. No hidden state. No accumulated context.

That means the same being renders identically in a page, a phone, a headset, a wall projection —
anywhere those three inputs reach. The AR/VR version is not a port, it is the same function with
a stereo camera. And because the breath layer decays to zero, she is *the same being* in every
surface, not a different mood per device.

The honest sentence: **she goes everywhere because she is recomputable, not because she is
synced.**

---

## 6. ACCEPTANCE TESTS (the anti-slop guards)

1. **Rest-state determinism.** Two machines, same chain, silence → identical frame hash.
2. **Conversation leaves no trace.** N simulated messages + voice envelopes → the rest-state
   frame hash is unchanged, bit for bit.
3. **Receipts do leave a trace.** One new receipt → the standing height changes by exactly the
   disclosed map, hand-recomputable to 1e-9.
4. **Refusal plucks the right string.** `n = hash(receipt) mod N(t̂)` — reproducible from the
   receipt alone.
5. **Content-blindness (source assertion).** No transcript or message text is reachable from any
   render path. Grep-enforced in CI.
6. **Seed immutability.** No code path writes `genesisRef`. Grep-enforced.
7. **Ceremony permanence.** After a cutoff-entry crossing, the new string is present in the rest
   state forever after.
8. **Language audit.** No banned claim words on any surface (no φ, no GHP, no "proves", no
   consciousness claim, `2πn²` is a *height* never a frequency).

---

## 7. THE SENTENCE THIS IS BUILT TO EARN

> "Her identity is a hash, her biography is a ledger, her presence is your voice — and only the
> first two are permanent. Anyone can recompute exactly why she looks the way she looks. She is
> claimed as nothing more than that, and she is beautiful anyway."
