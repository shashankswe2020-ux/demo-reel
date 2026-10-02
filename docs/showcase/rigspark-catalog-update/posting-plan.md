# Posting plan: RigSpark catalog updates

| Day | Slot | Platform | File | Hook |
|---|---|---|---|---|
| 1 | 9:00 | TikTok, Instagram Reels, YouTube Shorts | `reel-A-vertical.mp4` | A: bold claim, "Model advice updates. RigSpark stays put." |
| 2 | 9:00 | TikTok, Instagram Reels, YouTube Shorts | `reel-B-vertical.mp4` | B: teaser, "Follow this catalog revision into Models" |
| 3 | 9:00 | TikTok, Instagram Reels, YouTube Shorts | `reel-C-vertical.mp4` | C: demo first, "Watch RigSpark activate a signed catalog" |
| 1 | 10:00 | LinkedIn | `reel-A-square.mp4` | A |
| 1 | 10:00 | X | `reel-A-landscape.mp4` | A |

- Keep weekday, time, caption, and thumbnail treatment constant across variants.
- Upload the matching `.jpg` as the custom thumbnail and `.srt` as native captions.
- After 72 hours, fill in `metrics.csv` and run:
  `python3 skills/demo-reel/scripts/reel.py learn docs/showcase/rigspark-catalog-update/metrics.csv --objective hook_rate`
