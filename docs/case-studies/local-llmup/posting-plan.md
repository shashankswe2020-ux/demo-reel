# Posting plan — local-llmup reels

Variants: **A** "yes / slow / no, before the download" (demo_first) · **B** "Stop downloading weights your RAM can't fit" (negative) · **C** "Which local LLMs can your laptop run?" (question)

| Day | Slot (IST) | TikTok / Reels / Shorts (vertical) | X (landscape) | LinkedIn (square) |
|---|---|---|---|---|
| Tue | 19:30 | A | A | A |
| Wed | 19:30 | B | B | — |
| Thu | 19:30 | C | C | B |
| Fri | 19:30 | — | — | C |

- Same weekday slot, one variant per day, same account per platform. Use Instagram trial reels where available.
- Upload the matching `.jpg` as custom thumbnail and the `.srt` as native captions.
- Optional control: post the repo's existing `assets/local-llmup.mp4` as `variant=brag` in the same slot the following week.
- After ~72 h (≥ 500 impressions per variant), fill in `metrics.csv` and run:
  `python3 skills/demo-reel/scripts/reel.py learn reel-output/metrics.csv --objective hook_rate`
