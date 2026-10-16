# Known pipeline bug and its fix (recorded, not hidden)

**Symptom.** `work/render_hero.sh` writes the concat list to
`work/renders/hero-list.txt` but lists the segments with paths relative to the
repository root (`work/renders/hero-seg-0.mp4`). The ffmpeg concat demuxer
resolves relative paths against the **list file's own directory**, so it looked
for `work/renders/work/renders/hero-seg-0.mp4` and the join failed with
`Impossible to open '…/work/renders/work/renders/hero-seg-0.mp4'`.

**Cause.** A path convention mismatch between the script and the concat
demuxer.

**Fix.** The list is written with absolute paths (`$PWD/hero-seg-N.mp4`) and the
join is run from the directory that holds the list. The script was corrected
after the render finished (the running copy could not be edited safely while
it was executing); the five rendered segments were joined with the corrected
command and the result was verified (960 frames, 40.000 s, 24 fps).

**Why it is recorded here:** the five segments were rendered and verified
individually (each is a complete, playable 1920×1080 8-second H.264 file with
its own `moov` atom), so nothing was lost — but the first automated join would
have failed silently enough to look like a render problem, and the real cause
was a path bug, not a render bug.
