# Production record

Keep `work/production-log.md` while making the reel. This is working evidence, not launch copy. Record a choice when it costs something to discover; do not leave a shipped number with no reason attached.

## Recipe

- Input commit, URL capture time, or source-file hashes.
- Tool versions: `python3 --version`, `node --version`, `ffmpeg -version`, and the browser version.
- Exact audio, render, and finish commands, including seeds, formats, samples, shutter, fps, duration, palette/look, and poster time.
- External sources point to `work/sources.md`; do not duplicate their rights details here.

## Calibration decisions

For each non-obvious threshold or reference, write:

```text
Decision: one amplitude reference for the whole clip
Tried: per-scene normalization
Measured: quiet scenes expanded until background noise looked like signal
Kept: p99 of the complete episode waveform
Why: bar height now carries the same quantity in every scene
```

Include rejected alternatives. A measured rejection prevents the next revision from repeating the same experiment.

## Failures and corrections

Log symptoms that inspection or static code reading did not predict: an encoder that failed mid-run, a soft transition that did not register as a cut, AAC true-peak overshoot, a font that loaded after layout, or a frame that failed only at one point in a motion cycle. Record the command or measurement that exposed it and the smallest correction.

## Shipped baseline

At delivery, `reel.py check` writes `artifact-manifest.json` with SHA-256 hashes for declared inputs and delivery artifacts, tool versions, and Git revision/dirty state. Review its warnings; a missing declared source means the baseline is incomplete. Hashes detect accidental replacement; they do not prevent an intentional revision. A new cut gets a new name or revision tag and sits beside the old one until explicitly retired.