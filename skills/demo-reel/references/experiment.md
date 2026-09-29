# Step 6: Deliver, post, learn

## Deliverables in `reel-output/`

```
reel-plan.json            the contract
reel-<V>-<fmt>.mp4        one per variant × format, poster baked as frame 0, faststart
reel-<V>-<fmt>.jpg        poster (upload as custom thumbnail where supported)
reel-<V>-<fmt>.srt        captions sidecar (upload as native captions)
qa-report.md / .json      gate results and VRS per render
share-copy.md             per-platform copy from plan.share
posting-plan.md           variant → platform → slot
metrics.csv               header only; the user fills it in after posting
work/                     masters, stills, stems
```

## Share copy rules

- Open with the hook, not with "we". The first line must fit in 125 characters (above the fold on IG, TikTok, and LinkedIn).
- Put the exact CTA (command or URL) in every platform's copy. X counts every URL as 23 characters.
- 3–5 specific hashtags. Don't use generic tags like `#tech` or `#innovation`.
- No clichés (`plan.banned_phrases`).

## Posting plan (A/B the hooks for real)

- **Same slot, different variant.** Post variants at the same weekday and hour on consecutive days, or use platform-native tests: Instagram trial reels, YouTube Shorts on the same channel at the same time slot, TikTok on the same account.
- Use vertical for TikTok, Reels, and Shorts. Square is for LinkedIn and X feeds, landscape for X, YouTube, and the website hero. Upload the `.srt` wherever captions are accepted.
- To measure lift against /brag, post its render as `variant=brag` under the same conditions.

## metrics.csv

```
variant,platform,impressions,views_3s,completions,shares,saves,follows
A,tiktok,4000,2200,700,40,55,12
B,tiktok,4000,1500,400,12,20,3
```

Rows are summed per variant across platforms. Definitions:

| KPI | Formula | Why it matters |
|---|---|---|
| Hook rate | views_3s / impressions | Did the first 3 s stop the scroll? |
| Completion | completions / views_3s | Did the body hold them? |
| Shares per 1k | 1000 × shares / impressions | The strongest distribution signal |

## Learning loop

```
reel.py learn reel-output/metrics.csv --objective hook_rate|completion|share_rate
```

- Each variant gets a Beta(1 + hits, 1 + misses) posterior. 20,000 Monte Carlo draws estimate **P(best)**.
- Decision rules (from yt-clipper's evaluator): keep testing until every variant has ≥ 500 impressions (about a 72 h window). Ship the leader when P(best) ≥ 95%.
- `next_traffic_split` equals P(best) per variant (Thompson sampling). Use it to decide how often to repost each hook.
- When a hook type wins, note it in the project so the next hook lab starts with that type weighted up.
