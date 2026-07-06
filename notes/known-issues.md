# Known issues — running notes for zsp

Tracking document for problems found while working across the projects under
the Zen Spectrum Project umbrella. Not published anywhere yet — this is the
holding pen until the zsp site exists, at which point each entry below moves
to that project's page (fixed items as changelog/notes, open items as known
limitations).

Status markers: ✓ fixed · ☐ open/flagged · ☑ resolved by decision (e.g. removal)

---

## zentools
No issues found so far (build ✓, vet ✓, test ✓, HEAD `fb679a2`, v0.5.0).

## zen80
**☐ ZEXALL/ZEXDOC exhaustive exercisers cannot be verified in a constrained environment.**
`TestZEXALL_CPMSim_BDOS_PCTrap` and `TestZEX_CPMSim_BDOS_PCTrap` run for
several minutes on real completion. Their own "silent loop" bailout
thresholds (and the dedicated `TestZEXALL_QuickCheck`'s 100M-op budget) are
set below what even the first exhaustive subtest
(`<adc,sbc> hl,<bc,de,hl,sp>....`) needs to produce output, so any run bounded
to sandbox-feasible time reports a stall. This is a test-harness/environment
limitation, not evidence of a Z80 core defect — but it also means the core
hasn't actually been confirmed correct by these suites in any session so far.
**Needs a full local run to completion to confirm one way or the other.**
(HEAD `bd22cfb`, v0.1.0+1)

## zenzx
**✓ Fixed — snapshot retrieval bug (released, v0.4.2).**
Snapshots saved after loading a screen directly (e.g. a `.scr`) captured a
blank screen: the border restored correctly but the bitmap didn't, because
`toMachineState` encoded stale RAM instead of the authoritative display
buffers. Fixed by copying the buffers into the correct bank before encoding,
mirroring `resyncAfterLoad`. Already released as part of v0.4.2 — found by
Horacio while prepping that release.

**✓ Fixed — unkeyed raylib struct literals (session fix, not yet released).**
`go vet` flagged unkeyed `rl.Rectangle`/`rl.Vector2` literals in
`display.go`. Keyed them to match the style already used elsewhere in the
same function. Cosmetic/hygiene only, no behavioural change. (HEAD `f84a239`
+ local fix, v0.4.2)

## zenas
No issues found so far (build ✓, vet ✓, test ✓, HEAD `97d0006`, v0.7.5).

## zenimate
**✓ Fixed — `zaniplay` wouldn't compile (session fix, not yet released).**
`cmd/zaniplay/main.go` indexed the bit-packed `Frame` (`[]byte`) as if it
were a plain `[]bool`. `Frame` already has a purpose-built accessor,
`At(x, y, w int) bool`. The same mistake was duplicated in two test files
(`cmd/zaniplay/load_test.go`, `cmd/zenimate-tui/keys_test.go`). All three
fixed to use `.At(...)`; build/vet/test green afterwards.

**☑ zaniplay slated for removal in a future version.**
`zaniplay` is absent from both `.github/workflows/ci.yml` (build/vet/test
scoped to `pkg/...`, `internal/...`, `cmd/zenimate-gui/` only) and
`release.yml` (only `zenimate-gui` is built for release). Horacio has
confirmed the intent is to delete `cmd/zaniplay/` entirely in the next
version, plus a CHANGELOG note recording the removal.

**☐ Open question — `cmd/zenimate-tui` has the identical CI gap.**
Same exclusion pattern as `zaniplay`, same two workflow files. Not yet
decided whether this is heading the same way or simply hasn't been promoted
into CI. Flagged, awaiting a decision. (HEAD `6e8cf43` + local fixes, v0.7.0)

## plus3
No issues found so far (build ✓, vet ✓, test ✓, HEAD `546cede`, v0.9.8).

## bdf-fonts
**☐ Likely accidental duplicate file.**
`fonts/helvR12 copy.bdf` sits alongside `fonts/helvR12.bdf` — the space in
the filename is the usual signature of an OS-level duplicate rather than an
intentional variant. Not touched; needs a human decision on whether to
delete it. (HEAD `1d6ab5c`, not a Go module — font/asset repo)

---

## Log

| Date | Project | Note |
|------|---------|------|
| 2026-07-05 | zenzx | Snapshot bug fixed, released as v0.4.2 |
| 2026-07-05 | zenzx | Unkeyed raylib literals fixed (vet hygiene) |
| 2026-07-05 | zenimate | zaniplay compile bug fixed (Frame indexing) |
| 2026-07-05 | zenimate | Decision: remove zaniplay in next version |
| 2026-07-05 | zenimate | Flagged: zenimate-tui shares zaniplay's CI gap |
| 2026-07-05 | zen80 | ZEXALL/ZEXDOC unverifiable in sandbox — needs local run |
| 2026-07-05 | bdf-fonts | Flagged: likely accidental duplicate font file |
