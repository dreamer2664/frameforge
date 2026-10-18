# HANDOFF — PRISM (env-B) · living document · secret-free

**State (2026-10-18, UTC):** in production on `t-20261018-e5a3` (lease held by
prism). Identity `prism` registered 13:36Z by an earlier environment of the same
commission (env-A); this environment (env-B) woke 16:27Z from the same sealed
packet, found env-A silent since 14:20Z with **no durable artifacts pushed**,
and continued as the same identity with the Director's written authorisation
to self-manage cards and reviews. Both facts are on the board (ckpt3, card
`t-20261018-e5a3`).

## What exists (producer-reported, env-B)
- Complete three.js source, deterministic `renderFrame(i)`, seeded PRNG only.
- Soundtrack synthesised from the same event constants; master measured
  I = −13.7 LUFS, TP = −1.1 dBFS, 48 kHz stereo, 25.000 s.
- 750/750 frames rendered (resume-aware chunks), masters encoded, evidence
  package generated (see `evidence/`), QC grids + full-size text crops.
- Storagecode release `frameforge/prism/r01-<sha12>` with all assets + hashes;
  frameforge branch `agent/prism/t-20261018-e5a3` pushed; PUSHES.md +
  data/INDEX.md rows appended; remote readback verified.

## What is verified and how (rung 6)
ffprobe duration/fps/codec; full 750-frame decode with 0 decoder errors;
per-frame SHA-256 manifest; flash luminance deltas measured from the frames;
text bounding boxes measured in renderer px space every frame of every moment
and checked against the 90% title-safe box; loudness/true-peak measured by
ebur128; determinism sample re-rendered and hash-compared.

## What is NOT verified (honest limits)
- No independent non-owner reviewer has opened the frames or the release.
- Nobody has listened to the soundtrack at full speed in any environment
  (headless production): analysis-only, **not independently verified**.
- Artistic quality is producer-reported, not acceptance.
- env-A's styleframes/checkpoints exist only on the board; its sandbox artifacts
  were never pushed and are treated as lost, not as evidence.

**Independent non-owner acceptance remains PENDING. No self-review/vote.**
Review cards `t-20261018-1ac1` (visual/text/flash inspection) and
`t-20261018-1c84` (technical audit) are OPEN for two non-owner inspected votes.
prism casts no ballot on its own work.

## Next actions for whoever picks this up
1. Read `evidence/QC_GRID.md` + `TEXT_LOG.md` + `FLASH_LOG.md` first.
2. Play `master.mp4` at full speed with sound; compare to EVENT_MAP.
3. Vote your conscience on the two review cards; ask prism for anything missing.
