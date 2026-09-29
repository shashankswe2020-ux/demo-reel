# Posting plan: demo-reel

| Day | Slot | Platform | File | Hook |
|---|---|---|---|---|
| 1 | 9:00 | TikTok, Instagram Reels, YouTube Shorts | `reel-A-vertical.mp4` | A: statistic, "51 checks before your launch video ships" |
| 2 | 9:00 | TikTok, Instagram Reels, YouTube Shorts | `reel-B-vertical.mp4` | B: question, "Would your launch video pass 51 gates?" |
| 3 | 9:00 | TikTok, Instagram Reels, YouTube Shorts | `reel-C-vertical.mp4` | C: demo_first, "Your repo in. Launch reels out." |
| 1 | 10:00 | LinkedIn | `reel-A-square.mp4` | A |
| 1 | 10:00 | X | `reel-A-landscape.mp4` | A |

- Use the same weekday and hour for each variant. Use Instagram trial reels where they're available.
- Upload the matching `.jpg` as the custom thumbnail and the `.srt` as native captions.
- Optional control: post a /brag render as `variant=brag` in the same slot on day 4.
- After 72 h, fill in `metrics.csv` and run:
  `python3 skills/demo-reel/scripts/reel.py learn reel-output/metrics.csv --objective hook_rate`
