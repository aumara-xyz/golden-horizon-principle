# LANDMINE — this build path is RETIRED for observatory.html (2026-08-02)

**Do not run `node src/build.mjs`.** It would overwrite `public/observatory.html` and
**destroy the entire v3 UI** (Torus Room, bottom tab bar, Auma bubble, guided narration,
container-responsive layout). The v3 shell was authored directly in the built artifact;
`src/shell.html` predates it and has no `torusRoom`, `tabBar`, or `aumaBubble`.

Status of each file here:
- `math.js` — **still canonical.** The validated engine; `public/observatory.html`'s inlined
  `zh-math` block is byte-identical to it and the fixture harness proves it on every check.
  Edit math HERE and re-inline deliberately; never the reverse.
- everything else (`shell.html`, `panels.js`, `render3d.js`, `audio.js`, `style.css`,
  `app_state.js`, `main.js`, `build.mjs`) — **superseded**, kept for provenance only.

To resume a source-based build, someone must first back-port the v3 shell into `src/` and
prove byte-equivalence of the built output against the current `public/observatory.html`.
Until that is done and recorded, `public/observatory.html` is the source of truth.
