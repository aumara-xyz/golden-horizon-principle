# Pinned X2 source review

Read-only review, 30 October 2026. GitHub main was resolved to **b2c7aaffc40694a94dc5f621421e728115cd8ae5**, matching the preceding PENTORA report's snapshot.

| Path | Git blob SHA-1 |
| --- | --- |
| cells/pentora/src/lib.rs | ba9a7413198e64cc626415336edcda0688382b08 |
| cells/pentora/README.md | 3bf6c9eaee14b5f4a591dccc344de0f28abe68b6 |
| cells/pentora/build.mjs | 883be5d0e9b87793d158539df52b70713a0d3889 |
| cells/aperture/meter.mjs | 73d50bac3708470e64a6803c9b03299bf119db55 |

The meter's UTF-8 content SHA-256 was independently computed and matched the build's expected **0c8fcc36550a6c379317780f3f063cdbb04ce514fd64a43dc3a9a8781dfd2714**. The original content has 19132 bytes. A temporary text materialization introduced one extra final newline; removing precisely that materialization byte recovered the matching hash. The temporary copy was removed; this research package does not duplicate the meter implementation.

## What the source establishes

- The PENTORA crate's Rust source imports the canonical integer JSON facilities, preserves an exact geometry table, and derives base-three digits with integer limbs.
- The current dispatch exposes pentora.expand, pentora.snapshot, pentora.geometry, and pentora.observe. The proposed research operations are absent.
- The build compiles a Rust cdylib to wasm32, strips exports, applies a SHA-pinned meter, and emits limits. The current recorded fuel setting is 400000000, the request limit is 4194304 bytes, and the response limit is 262144 bytes.
- The meter rejects f32/f64 value types and floating loads/stores, constants, comparisons, arithmetic, conversions, and reinterpret operations; it also rejects imports and unsupported instructions.
- Accepted variable-cost memory instructions are metered before mutation. Therefore the accurate claim is not that every variable-cost instruction is forbidden.
- The README explicitly characterizes the cell as an observer with no permission or write capability and no installed-app claim.

No Rust build, Wasm execution, runtime fuel benchmark, UI test, or deployed-app behavior was checked here. Source evidence is not substituted for those tests.

## URLs

- https://github.com/aumara-xyz/aukora-x2/blob/b2c7aaffc40694a94dc5f621421e728115cd8ae5/cells/pentora/src/lib.rs
- https://github.com/aumara-xyz/aukora-x2/blob/b2c7aaffc40694a94dc5f621421e728115cd8ae5/cells/pentora/README.md
- https://github.com/aumara-xyz/aukora-x2/blob/b2c7aaffc40694a94dc5f621421e728115cd8ae5/cells/pentora/build.mjs
- https://github.com/aumara-xyz/aukora-x2/blob/b2c7aaffc40694a94dc5f621421e728115cd8ae5/cells/aperture/meter.mjs

The canonical geometry file under data/ retains the exact bytes with SHA-256 **96b27c9b4de41cd961612be5b1e88d40e973a2fded16bd320415b3e15e3b8c61**. The raw coordinate convention and the product's common display scale are kept separate from per-point unit-sphere normalization.
