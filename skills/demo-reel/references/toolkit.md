# Toolkit reference

`reel.py` is stdlib-only Python 3.10+ and shells out to FFmpeg/ffprobe (list arguments, never a shell).

```
python3 skills/demo-reel/scripts/reel.py lint     reel-output/reel-plan.json
python3 skills/demo-reel/scripts/reel.py finish   work/A-vertical.mp4 --format vertical --poster-t 1.4 --out reel-output/reel-A-vertical.mp4
python3 skills/demo-reel/scripts/reel.py captions reel-output/reel-plan.json --variant A --out reel-output/reel-A-vertical.srt
python3 skills/demo-reel/scripts/reel.py check    reel-output/reel-plan.json --renders reel-output
python3 skills/demo-reel/scripts/reel.py hotspots recording.mov --window 20
python3 skills/demo-reel/scripts/reel.py sheet    reel-output/reel-A-vertical.mp4 --cuts
python3 skills/demo-reel/scripts/reel.py beats    reel-output/work/audio.wav --out reel-output/work/audio-events.json
python3 skills/demo-reel/scripts/reel.py compare  brag-output/brag.mp4 reel-output/reel-A-vertical.mp4
python3 skills/demo-reel/scripts/reel.py learn    reel-output/metrics.csv --objective hook_rate
python3 skills/demo-reel/scripts/reel.py gates
```

| Command | Does |
|---|---|
| `lint` | Runs the 29 plan gates on `reel-plan.json` and prints the hook leaderboard (plus the beat-grid advisory when `music.bpm` is set) |
| `finish` | Frames the video to the exact format, normalizes to −14 LUFS with a true-peak limiter, converts to limited-range BT.709 yuv420p with color tags (so brand colors don't shift in players), bakes the poster into frame 0, and sets faststart |
| `captions` | Writes the SRT for one variant from the plan |
| `check` | Runs the full gate pass (plan + every variant × format) and writes `qa-report.md` and `qa-report.json` |
| `hotspots` | Ranks the strongest windows of a long recording (motion, cuts, loudness, hook motion) |
| `sheet` | Contact sheet PNG of a render: `--n` evenly spaced frames, or `--cuts` for the frame either side of every cut the `visual.shot_length` detector counts |
| `beats` | Analyzes a soundtrack: tempo, beat grid, downbeats, kick/snare/hat (low/mid/high) onsets, and loudness envelopes, written as `audio-events.json` for the runtime. Prints the `plan.music` values. `--bpm` fixes a known tempo |
| `compare` | Scores any videos side by side on the media gates, such as a /brag render against a reel |
| `learn` | Reads post-launch `metrics.csv` and reports P(best) per variant plus the next traffic split |
| `gates` | Lists every gate with its category, severity, and description (`--count` for the total) |

The skill is exposed at `.claude/skills/`, `.agents/skills/`, and `.github/skills/` via symlinks to `skills/demo-reel/`.

## Renderer (Node + Playwright)

| File | Does |
|---|---|
| `scripts/runtime/reel-runtime.js` | Browser timeline for compositions: deterministic frames, eases/keyframes/springs, beat grid and onset pulses, seeded RNG, a scrubbable preview with keyboard controls |
| `scripts/runtime/template.html` | Starter composition: palette and type voices, safe-zone stage, hook slot, beat-synced arrival, a through-line motif |
| `scripts/render.mjs` | Renders every variant × format master or a set of stills, with optional cut-aware motion blur (`--samples`), lossless capture (`--png`), and segments (`--from`/`--to`) |

See [build.md](build.md#bundled-runtime-and-renderer) for usage.

## Tests

```sh
cd skills/demo-reel/scripts && python3 -m unittest discover -s tests -v
```

The media tests render synthetic videos with FFmpeg and take about a minute. The renderer test runs `render.mjs` end to end when `DEMO_REEL_NODE_DIR` points to a directory with Playwright installed, and is skipped otherwise.
