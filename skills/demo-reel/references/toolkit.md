# Toolkit reference

`reel.py` is stdlib-only Python 3.10+ and shells out to FFmpeg/ffprobe (list arguments, never a shell).

```
python3 skills/demo-reel/scripts/reel.py lint     reel-output/reel-plan.json
python3 skills/demo-reel/scripts/reel.py finish   work/A-vertical.mp4 --format vertical --poster-t 1.4 --out reel-output/reel-A-vertical.mp4
python3 skills/demo-reel/scripts/reel.py captions reel-output/reel-plan.json --variant A --out reel-output/reel-A-vertical.srt
python3 skills/demo-reel/scripts/reel.py check    reel-output/reel-plan.json --renders reel-output
python3 skills/demo-reel/scripts/reel.py hotspots recording.mov --window 20
python3 skills/demo-reel/scripts/reel.py compare  brag-output/brag.mp4 reel-output/reel-A-vertical.mp4
python3 skills/demo-reel/scripts/reel.py learn    reel-output/metrics.csv --objective hook_rate
python3 skills/demo-reel/scripts/reel.py gates
```

| Command | Does |
|---|---|
| `lint` | Runs the 29 plan gates on `reel-plan.json` and prints the hook leaderboard |
| `finish` | Frames the video to the exact format, normalizes to −14 LUFS with a true-peak limiter, outputs limited-range yuv420p, bakes the poster into frame 0, and sets faststart |
| `captions` | Writes the SRT for one variant from the plan |
| `check` | Runs the full gate pass (plan + every variant × format) and writes `qa-report.md` and `qa-report.json` |
| `hotspots` | Ranks the strongest windows of a long recording (motion, cuts, loudness, hook motion) |
| `compare` | Scores any videos side by side on the media gates, such as a /brag render against a reel |
| `learn` | Reads post-launch `metrics.csv` and reports P(best) per variant plus the next traffic split |
| `gates` | Lists every gate with its category, severity, and description (`--count` for the total) |

The skill is exposed at `.claude/skills/`, `.agents/skills/`, and `.github/skills/` via symlinks to `skills/demo-reel/`.

## Tests

```sh
cd skills/demo-reel/scripts && python3 -m unittest discover -s tests -v
```

The media tests render synthetic videos with FFmpeg and take about a minute.
