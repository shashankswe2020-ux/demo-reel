# demo-reel QA report

- Gates evaluated: 51
- Minimum Viral Readiness Score: **100.0** (ship at >= 85.0, zero blockers)
- Shippable: **True**

| Variant | Format | VRS | Hook | Retention | Truth | Audio | Platform | Distribution | Blockers |
|---|---|---|---|---|---|---|---|---|---|
| A | vertical | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| A | square | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| A | landscape | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| B | vertical | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| B | square | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| B | landscape | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| C | vertical | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| C | square | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |
| C | landscape | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | - |

## Plan checks

- PASS `plan.schema` (blocker): schema=demo-reel/plan@1
- PASS `plan.claims_evidence` (blocker): 5 claims verified
- PASS `plan.lexicon_grounded` (major): 7 terms
- PASS `plan.hook_candidates` (blocker): 10 candidates
- PASS `plan.hook_type_diversity` (major): types=['before_after', 'bold_claim', 'challenge', 'contrarian', 'demo_first', 'negative', 'pain_point', 'question', 'statistic', 'teaser']
- PASS `plan.variant_count` (major): 3 variants
- PASS `plan.variant_diversity` (minor): variant hook types=['demo_first', 'question', 'statistic']
- PASS `plan.hook_brevity` (major): ok
- PASS `plan.hook_selection` (major): cutoff 80.0
- PASS `plan.hook_grounded` (major): ok
- PASS `plan.duration_sum` (blocker): sum=20.00s vs duration_s=20.00s
- PASS `plan.duration_band` (major): 20.0s
- PASS `plan.hook_scene_length` (major): scene 1 role=hook duration=2.8
- PASS `plan.first_event` (blocker): first event after t=0 at 0.15s
- PASS `plan.pattern_interrupts` (major): longest gap 1.40s
- PASS `plan.reading_time` (major): ok
- PASS `plan.text_density` (minor): 2.20 words/s
- PASS `plan.numbers_backed` (blocker): ok
- PASS `plan.safe_zone` (major): ok
- PASS `plan.loop` (minor): strategy=callback
- PASS `plan.show_the_thing` (major): 100% of runtime sourced from product
- PASS `plan.product_in_use` (major): needs a sourced scene with role=demo
- PASS `plan.banned_phrases` (major): ok
- PASS `plan.one_liner` (minor): 12 words
- PASS `plan.cta` (blocker): last role=cta, target='npx skills add shashankswe2020-ux/demo-reel'
- PASS `plan.formats` (major): ['vertical', 'square', 'landscape']
- PASS `plan.share_limits` (major): ok
- PASS `plan.share_fold` (minor): ok
- PASS `plan.hashtags` (minor): ['#buildinpublic', '#aiagents', '#devtools', '#launchday']

## Hook leaderboard

| Hook | Score |
|---|---|
| h2 | 85.6 |
| h3 | 83.4 |
| h1 | 80.0 |
| h5 | 77.0 |
| h4 | 75.4 |
| h8 | 74.0 |
| h6 | 66.8 |
| h10 | 62.6 |
| h7 | 49.4 |
| h9 | 45.4 |

## A / vertical

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1920 for vertical
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.2 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=69 contrast=154
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.93s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `visual.ui_clutter`: ratio 0.04
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## A / square

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1080 for square
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 2.9 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=84 contrast=156
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 0.60s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## A / landscape

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1920x1080 for landscape
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.7 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=72 contrast=154
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.97s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## B / vertical

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1920 for vertical
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.2 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=70 contrast=154
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.93s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `visual.ui_clutter`: ratio 0.04
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## B / square

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1080 for square
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 2.9 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=84 contrast=156
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 0.60s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## B / landscape

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1920x1080 for landscape
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.7 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=73 contrast=154
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.97s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## C / vertical

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1920 for vertical
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.2 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=66 contrast=90
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.93s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `visual.ui_clutter`: ratio 0.04
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## C / square

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1080 for square
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 2.9 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=77 contrast=155
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 0.60s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## C / landscape

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1920x1080 for landscape
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.00s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.7 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.6 LUFS
- PASS `audio.true_peak`: -1.1 dBTP
- PASS `audio.lra`: 0.5 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=74 contrast=154
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.97s frozen
- PASS `visual.shot_length`: 4 cuts, avg shot 4.00s
- PASS `captions.present`: 9 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok
