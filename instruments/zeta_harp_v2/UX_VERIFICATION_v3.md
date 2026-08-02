# UX_VERIFICATION_v3.md — adversarial verification of Observatory v3

Branch: `instrument/observatory-v3-clean` @ `24fb0b0`
Artifact under test: `instruments/zeta_harp_v2/public/observatory.html` (206 KiB, single file)
Baseline for all identity claims: `origin/main:instruments/zeta_harp_v2/public/observatory.html`
Method: static parse of the extracted CSS / markup / script blocks, plus a **live browser
audit** (Chromium, page served over `http://127.0.0.1:8731`) at two width bands and eight
UI states, using a hit-test occlusion probe rather than eyeballing.

Verdict: **BLOCK** — rules 1 through 8 PASS. Rule 9 FAILS on the binding not-list in
`CLAIM_BOUNDARY.md`. The failure is a governance/document inconsistency, **not** a UI
regression: none of the owner's original layout complaints survive.

---

## Summary table

| # | Owner rule | Result |
|---|---|---|
| 1 | math untouched; fixture harness passes | PASS |
| 2 | `node --check` clean on every inline script | PASS |
| 3 | no control can render over another control | PASS |
| 4 | persistent bottom tab bar; top-right menu not pinned | PASS (one documented exception) |
| 5 | preset cards carry plain-language second lines | PASS |
| 6 | torus is a full-stage mode with ladder + SHADOW/SLICE/UNFOLD | PASS |
| 7 | Auma bubble bottom-right, field-responsive, honest fallback | PASS |
| 8 | container-driven responsive rules; no body text below 14px | PASS (with a re-band robustness gap) |
| 9 | fence text + claim boundary verbatim; banned phrases absent | **FAIL** |

---

## Rule 1 — the mathematics is untouched

Independent SHA-256 of each `<script id=...>` block, branch vs `origin/main`:

```
zh-math        base e1d9b009f26be73e   new e1d9b009f26be73e   SAME
zh-fixtures    base 8cf83900be3371a6   new 8cf83900be3371a6   SAME
zh-app         base f533a5293e39aa8d   new e71491a19d12405d   DIFF   (UI layer — expected)
zh-guide       base 13aa592a990fa6f2   new —ABSENT—                  (folded into zh-app)
zh-auma        base —ABSENT—           new dbeb808be9020baf          (new presence layer)
```

The math core and the embedded fixture excerpts are byte-identical. Only the UI layer moved.

`node reference/check_inline_math.mjs` — extracts the inline core from the shipped HTML and
validates it against the full-precision frozen Gate-2 fixtures at every grid point:

```
window  pts  max|dTheta|  max|dTheta'|  max|dM|     max|embed-full|  N-mismatch  verdict
W1      241  5.684e-14    2.220e-15     2.203e-13   4.980e-13        0           PASS
W2      141  1.091e-11    8.882e-16     5.569e-11   4.672e-12        0           PASS
W3      141  9.313e-10    1.776e-15     9.502e-09   3.830e-12        0           PASS
W4       41  1.192e-07    1.776e-15     1.697e-06   4.967e-12        0           PASS
cutoff entry n=4 / n=5 ....................................................... PASS
audio-law derivative check (W1+W2): worst 8.304e-10 rad/unit-t ................ PASS
ALL CHECKS PASS
```

**PASS.**

## Rule 2 — `node --check` clean

Three non-JSON inline script blocks were extracted and syntax-checked individually:

```
node --check zh-math.js  OK
node --check zh-app.js   OK
node --check zh-auma.js  OK
```

Live console during the browser session: zero errors.

**PASS.**

## Rule 3 — overlap audit (the loudest complaint)

### 3a. Static: what is taken out of flow at all

Every element in the live DOM whose *computed* position is `absolute` or `fixed`:

| element | position | z-index | rect | pointer-events |
|---|---|---|---|---|
| `canvas#gl` | fixed | 0 | 0,0,1440,900 | auto |
| `#vignette` | fixed | 1 | 0,0,1440,900 | none |
| `#chrome` | fixed | 5 | 0,0,1440,900 | **none** |
| `#fencePanel` | fixed | 50 | full-bleed overlay | auto |
| `#welcome` | fixed | 60 | full-bleed overlay | auto |

Five, and only five. Every one is a full-bleed layer alone on its own z-layer. **No
interactive control anywhere in the build is absolutely positioned into another element's
coordinate space.** All chrome is a grid child of `#chrome` in a reserved lane (`top /
stage / rail / dock / foot`), and `#chrome` itself is `pointer-events: none` with
`auto` re-enabled only on real controls, so the field canvas keeps the gaps.

### 3b. Live: hit-test occlusion probe

For every painted, enabled control the probe intersects its rect with the client rect of
every clipping ancestor (so a control merely *scrolled out* of a column is correctly
excluded rather than reported as an overlap — the naive rect-only version of this test
produces four false positives here), then calls `document.elementFromPoint` at nine sample
points and reports any element that is neither the control, its ancestor, nor its
descendant. It separately reports every geometric intersection between two non-nested
painted controls.

| state | viewport | painted controls | occluded | intersecting control pairs |
|---|---|---|---|---|
| explore, default | 1440×900 | 21 | 0 | 0 |
| all five sheets open | 1440×900 | 28 | 0 | 0 |
| menu sheet open | 1440×900 | 27 | 0 | 0 |
| torus room + ladder | 1440×900 | 22 | 0 | 0 |
| Auma rail open (420px) | 1440×900 | 24 | 0 | 0 |
| welcome overlay | 560×900 | 14 | modal only | 0 |
| explore, narrow | 560×900 | 16 | 0 | 0 |
| all sheets + menu, narrow | 560×900 | 14 | 0 | 0 |

The only states with reported occlusions are welcome-open and fence-open, where every
control underneath is blocked by exactly one element — `#welcome` or `#fencePanel` — which
is the intended modal behaviour of a full-bleed own-layer overlay.

**Zero intersecting control pairs in every state at both bands. PASS.**

## Rule 4 — persistent bottom tab bar; menu not pinned

`#tabBar` lives in the `dock` grid lane and is present and non-zero-height in every state
measured, including inside the torus room (rect `12,715,536,117` at 560px; the row wraps
rather than clipping).

Panel keys vs tab-bar coverage:

```
all panels      ribbon terms zeros sound guide menu torus
tab bar         ribbon terms zeros sound guide      torus
missing         menu
```

Six of the seven panels have a bottom-bar re-open control. Each sheet's close control is
literally labelled `close → tab`, and closing removes the sheet to `#sheetStore` so a
closed panel *is* exactly its tab.

**Exception, recorded honestly:** the menu panel has no tab-bar entry. Its only re-open
control is the top-right `#menuBtn`. Nothing is lost — that button is always present — but
"a re-open control in the tab bar for *every* closable panel" is true for 6/7, not 7/7.

Menu is *not* pinned: on load `#menuSheet` is parented to `#sheetStore` and paints at
0×0; `TABS.menu === false`. What sits top-right is a 70×30 button chip in its own reserved
grid cell, not a panel.

**PASS**, with the 6/7 exception on record.

## Rule 5 — preset cards carry plain-language second lines

All four cards, read from the live DOM:

| card | plain-language line (`.pteach`) | numeric line (`.psub`) |
|---|---|---|
| THE FIRST FOUR | the formula starts with just 4 waves — watch them beat against each other | t = 130 · 4 threads |
| THE CHOIR | ten thousand up, 39 waves are singing together | t = 10,000 · 39 threads |
| THE CATHEDRAL | climb to a million and 398 waves are singing at once | t = 1,000,000 · 398 threads |
| THE WALL | 3,989 waves — and the edge where float64 phase accuracy runs out | t = 10⁸ = 100,000,000 · 3,989 threads |

4/4. **PASS.**

## Rule 6 — the torus is a full-stage mode with the ladder and the three views

With the TORUS tab on at 1440×900:

- `#stageLane` rect `0,55,1440,556`; `#torusRoom` rect `16,67,1408,532` — it takes the
  entire stage.
- all three `.stageCol` elements report `display: none` (`#stageLane[data-room="torus"]`),
  so no sheet can sit beside or behind the room.
- the dock and the tab bar remain visible, so the room is *escapable*; it is a full-stage
  mode rather than a browser-fullscreen takeover.
- dimensional ladder present on first open, six rungs read off the live DOM:
  `POINT | LINE | SQUARE | CUBE | TESSERACT | THE REAL THING`, with `next` and
  `skip the ladder`.
- the three view buttons exist and each changes the live caption:
  - SHADOW — "the flat picture a four-dimensional object throws when you light it from one side…"
  - SLICE — "hold the two turning phases still and cut. What is left is a single pair of circles…"
  - UNFOLD — "cut both circles and lay them flat. The square is the (φ₁, φ₂) fundamental domain…"
- the honest label renders in full: "the full state at this height lives on a 398-torus —
  one circle for every thread in the sum. This is a four-torus window onto it… Standard
  geometry, presentation only. No claim rides on this picture; see the fence."
- the wireframe four-torus renders (visually confirmed in a screenshot at 1440×900).

**PASS.**

## Rule 7 — Auma is a bottom-right pinned bubble, field-responsive, with a fallback

Geometry at 1440×900: `#aumaBubble` rect `1378,809,46,46`, parent `#tabBar`, 16 px from
the right edge and 45 px from the bottom (the fence footer sits below). Bottom-right
pinned by construction, not by absolute positioning.

Amplitude wiring, proven live end to end:

```
ZH_FIELD.setAmp(0.95)
  -> GLR.FIELD.amp
  -> FIELD.smooth += (amp - smooth) * min(1, dt*9)      [per frame]
  -> gl.uniform1f(uPulse, FIELD.smooth)                  [helix shader tint + brightness]
  -> camBreath = 1 - 0.030*smooth + 0.010*sin(t*1.7)*smooth   [camera]
  -> aumaBubbleTick(): core r = 4.4 + 4.6*smooth, opacity = 0.60 + 0.40*smooth

measured after the call:  getAmp() 0 -> 0.6234
                          #aumaCore r  "4.4" -> "7.27"
                          #aumaCore opacity   -> "0.849"
                          field visibly brighter in the screenshot
```

Source of the amplitude: an `AnalyserNode` tapped onto the mounted surface's own media
element when one appears, otherwise a synthetic envelope from message timing; the mode is
reported on the bubble tooltip, and any failure leaves her audio untouched.

Graceful fallback, exercised live (no node running on `:7091` during this audit): the rail
opened to its reserved 420 px column (`#railLane` rect `1020,55,420,556`, `--railW: 420px`
— never over the stage), and the fallback panel rendered

> **Auma is not reachable from here.** the node's voice service (127.0.0.1:7091) is not
> answering right now — Nothing is lost: everything she would say aloud is written down…

with an "open the written guide" escape button, and the bubble tooltip carrying the same
reason. Nothing hangs and nothing is silently dead.

**PASS.**

## Rule 8 — container-driven responsive rules; 14 px floor

**Mechanism.** There is no native CSS `@container` at-rule in this build (verified: the
style block contains neither `@container` nor `container-type`). The equivalent is a
`ResizeObserver` on `document.body` that stamps `data-w = narrow | mid | wide` on `<html>`,
driving 21 `:root[data-w="narrow"]` rules and 1 `:root[data-w="mid"]` rule. It is
container-driven in the sense that matters — it measures the page's own box, not the
viewport, so a 1/3-width spatial column collapses to the phone layout on a 5K display.

**Verified on load at 560×900:** `data-w === "narrow"`; `#chrome` grid areas collapse to
`"top" "stage" "rail" "dock" "foot"`; `#orient` and `#presets` are *moved* (not duplicated,
so their listeners survive) into `#guideNarrow` inside the Guide sheet; `#orientMini`
carries the one-line orientation in the tab bar; zero occlusions and zero intersecting
control pairs in all three narrow states.

**Gap found, reported not waived:** the `window.addEventListener('resize', …)` fallback in
`bindResponsive()` is bound *only* in the `else` branch when `window.ResizeObserver` is
absent. If `ResizeObserver` exists but does not deliver, the page never re-bands after
load. That is exactly what was observed in this automation harness, where neither
`ResizeObserver` callbacks nor `resize` events fire at all (a fresh observer on a div whose
width was changed also never fired) — so live re-banding on resize could **not** be
verified here, only the on-load band. Binding the `resize` listener unconditionally would
close the gap for about one line of code.

**14 px floor.** Three independent sweeps:
- CSS declarations below 14 px in the `<style>` block: **0**.
- Live DOM sweep over every element carrying a text node, at both bands, including hidden
  sheet templates: **0** below 14 px. Body is 15 px. `sub`/`sup` are pinned to 14 px so the
  browser default `font-size: smaller` cannot shrink math subscripts to ~11 px.
- Canvas text: four `ctx.font` literals at `14px ui-monospace`, one at `15px Georgia`, and
  the one computed size is floored — `Math.max(14, Math.round(S / 30)) + 'px Georgia'`.
- No inline `style="… font-size …"` anywhere in the markup.

**PASS**, with the re-band robustness gap on record.

## Rule 9 — fence text and claim boundary verbatim; banned phrases absent

**Fence text: verbatim. PASS.**
`#fenceInner` is byte-identical to `origin/main` over its whole extent, including the
closing "The Riemann fence" section and the return button, which the shipped self-check's
range stops short of and which was therefore diffed separately here — also identical. The
only delta inside the `#fencePanel` wrapper is its class attribute (`panel hidden` →
`hidden`) and two characters of indentation; no prose changed. `#welcomeLaw` is identical.
The standing label

> KNOWN MATHEMATICS / INTERACTIVE SCIENTIFIC AND ARTISTIC INSTRUMENT / NOT EVIDENCE FOR RH OR GHP

is present in the footer lane, the welcome card, the menu sheet, and the fence.

**Claim-boundary file: unchanged.** `git diff origin/main...HEAD -- CLAIM_BOUNDARY.md` is
empty.

**Banned phrases — the shipped lint: no new occurrence.**
```
Trinity 0/0 · 54-observers 0/0 · holograph 0/0 · GHP 6/6 · golden ratio 0/0 ·
phi 18/18 · φ-horizon 0/0 · proves/supports RH 0/0 · evidence for RH 6/6 · first-ever 0/0
```
(`GHP` and `evidence for RH` occur only inside the standing label itself; `phi` occurs only
as the phase symbol φₙ.)

**FAIL — the binding not-list in `CLAIM_BOUNDARY.md` is violated.** That file states, and
still states on this branch:

> CLAIM BOUNDARY is absolute: no cube · no Trinity · no 54-observers · **no torus** ·
> no holography · no phi · no GHP · no "proves/supports RH" · no "first ever" —
> anywhere in this build.

Measured against `origin/main`:

```
\btorus\b   base 18   new 42     +24
\bcube\w*   base  1   new  6      +5
```

The Torus Room is the headline feature of this branch (owner rule 6 explicitly commissions
it) and the dimensional ladder's rungs are literally `SQUARE → CUBE → TESSERACT`. The
shipped `tools/v3_selfcheck.sh` lint cannot see this: its `BANNED` array omits `torus` and
`cube` entirely, so the harness reports a clean claim-boundary pass while two items on the
binding not-list are the most prominent text in the build.

This is a contradiction between two owner directives, and only the owner can resolve it. It
is **not** a UI defect and it does not touch the mathematics or the fence. The cheapest
honest resolution is one commit:

1. amend `CLAIM_BOUNDARY.md` to record that `torus` and `cube` are exempted for the
   dimensional-ladder and torus-room presentation, with the "presentation only, no claim
   rides on this picture" honest label as the binding condition; **and**
2. add `\btorus\b` and `\bcube` to the `BANNED` array in `tools/v3_selfcheck.sh` with a
   baseline-count exemption, so the lint tracks them instead of ignoring them.

Until then, rule 9 is recorded **FAIL**.

---

## Advisories (outside the nine rules, no verdict attached)

1. **`src/` is stale and is now a live landmine.** The whole v3 UI exists only in the built
   file `public/observatory.html`. `src/shell.html` contains no `torusRoom`, no `tabBar`,
   no `aumaBubble`. Running `node src/build.mjs` — the documented build path — would
   overwrite `public/observatory.html` and destroy the entire v3 layout. Either back-port
   the build to `src/`, or mark `src/build.mjs` as retired for this artifact.
2. **`resize` fallback** — see rule 8; bind it unconditionally.
3. Two `vw`-based clamps survive in an otherwise container-driven sheet:
   `#titleChip { max-width: min(430px, 46vw) }` and `:root[data-w="narrow"] #titleChip
   { max-width: 62vw }`, plus `:root[data-w="narrow"] #railLane { max-height: 54vh }`.
   Harmless today because the grid track bounds them and `.tname` ellipsises, but they are
   viewport units inside a container-driven layout.

---

## Reproduction

```bash
cd instruments/zeta_harp_v2
node reference/check_inline_math.mjs          # fixture harness
bash tools/v3_selfcheck.sh "$(git rev-parse --show-toplevel)"
python3 -m http.server 8731 --directory public # then audit in a browser at 1440x900 and 560x900
```
