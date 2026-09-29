# demo-reel

An agent skill that turns a project, a website, or a long screen recording into **gated, A/B-ready launch reels**:
3 hook variants × 3 native formats (9:16, 1:1, 16:9). Each render comes with a baked poster, captions, per-platform
share copy, and a QA report scored against **51 machine-verified gates**. After launch, a Bayesian loop reads real
analytics and picks the winning hook.

It builds on [/brag](https://github.com/latent-spaces/brag) (story-first launch videos, creative laws, poster-as-frame-0)
and on yt-clipper-server (weighted hot-zone detection, hook-type A/B testing, Thompson sampling, shell-free FFmpeg).
It adds measurement at every step.

## Install

```sh
npx skills add <this-repo> --skill demo-reel      # or copy skills/demo-reel/ into your agent's skills dir
```

The skill is exposed at `.claude/skills/`, `.agents/skills/`, and `.github/skills/` via symlinks to `skills/demo-reel/`.

**Requirements:** Python 3.10+ (stdlib only), FFmpeg/ffprobe on `PATH`, and any frame renderer (Hyperframes, Remotion, Playwright, or Pillow).

## Use

```
/demo-reel                                   # current project
/demo-reel https://example.com --tone cinematic
/demo-reel demo-recording.mov --duration 25
```

## Toolkit

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

## Verifiable scorecard against /brag

| Metric | /brag | demo-reel |
|---|---|---|
| Machine-verified gate types (`reel.py gates --count`) | ~5 | **51** |
| Gate evaluations per run (`qa-report.json`) | ~5 | **227** |
| Hooks generated and scored | 1 | **≥ 10** |
| Shipped renders per run | 1 | **9** |
| Claims checked verbatim against source | 0 | **all** |
| Post-launch winner selection | none | **P(best) ≥ 95%** |

Pre-launch gates show a reel is *ready*. Whether it's *more viral* is decided by audience data: post the /brag render
as a control variant and run `reel.py learn`. See
[skills/demo-reel/references/metrics.md](skills/demo-reel/references/metrics.md).

## Tests

```sh
cd skills/demo-reel/scripts && python3 -m unittest discover -s tests -v
```
