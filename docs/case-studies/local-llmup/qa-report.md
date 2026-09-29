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
- PASS `plan.claims_evidence` (blocker): 4 claims verified
- PASS `plan.lexicon_grounded` (major): 10 terms
- PASS `plan.hook_candidates` (blocker): 10 candidates
- PASS `plan.hook_type_diversity` (major): types=['before_after', 'bold_claim', 'challenge', 'contrarian', 'demo_first', 'negative', 'pain_point', 'question', 'statistic', 'teaser']
- PASS `plan.variant_count` (major): 3 variants
- PASS `plan.variant_diversity` (minor): variant hook types=['demo_first', 'negative', 'question']
- PASS `plan.hook_brevity` (major): ok
- PASS `plan.hook_selection` (major): cutoff 77.0
- PASS `plan.hook_grounded` (major): ok
- PASS `plan.duration_sum` (blocker): sum=20.00s vs duration_s=20.00s
- PASS `plan.duration_band` (major): 20.0s
- PASS `plan.hook_scene_length` (major): scene 1 role=hook duration=2.8
- PASS `plan.first_event` (blocker): first event after t=0 at 0.15s
- PASS `plan.pattern_interrupts` (major): longest gap 0.80s
- PASS `plan.reading_time` (major): ok
- PASS `plan.text_density` (minor): 1.75 words/s
- PASS `plan.numbers_backed` (blocker): ok
- PASS `plan.safe_zone` (major): ok
- PASS `plan.loop` (minor): strategy=callback
- PASS `plan.show_the_thing` (major): 100% of runtime sourced from product
- PASS `plan.product_in_use` (major): needs a sourced scene with role=demo
- PASS `plan.banned_phrases` (major): ok
- PASS `plan.one_liner` (minor): 12 words
- PASS `plan.cta` (blocker): last role=cta, target='brew install shashankswe2020-ux/tap/local-llmup'
- PASS `plan.formats` (major): ['vertical', 'square', 'landscape']
- PASS `plan.share_limits` (major): ok
- PASS `plan.share_fold` (minor): ok
- PASS `plan.hashtags` (minor): ['#localllm', '#ollama', '#rustlang', '#selfhosted']

## Hook leaderboard

| Hook | Score |
|---|---|
| h3 | 88.6 |
| h2 | 88.0 |
| h1 | 77.0 |
| h5 | 76.4 |
| h6 | 72.6 |
| h8 | 70.4 |
| h9 | 67.4 |
| h7 | 66.0 |
| h4 | 65.0 |
| h10 | 64.0 |

## A / vertical

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1920 for vertical
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.9 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=158 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.03s frozen
- PASS `visual.shot_length`: 7 cuts, avg shot 2.50s
- PASS `visual.ui_clutter`: ratio 0.09
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## A / square

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1080 for square
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.2 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=119 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 0.73s frozen
- PASS `visual.shot_length`: 8 cuts, avg shot 2.22s
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## A / landscape

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1920x1080 for landscape
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.1 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=141 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.07s frozen
- PASS `visual.shot_length`: 7 cuts, avg shot 2.50s
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## B / vertical

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1920 for vertical
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.0 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=156 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.03s frozen
- PASS `visual.shot_length`: 7 cuts, avg shot 2.50s
- PASS `visual.ui_clutter`: ratio 0.09
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## B / square

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1080 for square
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.2 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=117 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 0.70s frozen
- PASS `visual.shot_length`: 8 cuts, avg shot 2.22s
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## B / landscape

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1920x1080 for landscape
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.1 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=140 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.07s frozen
- PASS `visual.shot_length`: 7 cuts, avg shot 2.50s
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## C / vertical

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1920 for vertical
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.9 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=158 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.03s frozen
- PASS `visual.shot_length`: 7 cuts, avg shot 2.50s
- PASS `visual.ui_clutter`: ratio 0.10
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## C / square

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1080x1080 for square
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 3.2 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=119 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 0.70s frozen
- PASS `visual.shot_length`: 8 cuts, avg shot 2.22s
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok

## C / landscape

- PASS `media.container`: mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac
- PASS `media.resolution`: 1920x1080 for landscape
- PASS `media.fps`: avg=30.000 r=30.000
- PASS `media.duration`: 20.01s (plan 20.0)
- PASS `media.faststart`: atoms=['ftyp', 'moov', 'free', 'mdat']
- PASS `media.file_size`: 4.1 MB
- PASS `media.audio_stream`: 2ch @ 48000 Hz
- PASS `audio.loudness`: -14.0 LUFS
- PASS `audio.true_peak`: -2.4 dBTP
- PASS `audio.lra`: 1.2 LU
- PASS `audio.leading_silence`: 0.00s
- PASS `audio.dead_air`: longest silence 0.00s
- PASS `visual.poster`: frame0 YAVG=142 contrast=181
- PASS `visual.first_motion`: first motion at 0.0666667s
- PASS `visual.black_frames`: 0 black frames (0.0%), 0 in hook
- PASS `visual.static_stretch`: 1.07s frozen
- PASS `visual.shot_length`: 7 cuts, avg shot 2.50s
- PASS `captions.present`: 7 cues
- PASS `captions.timing`: ok
- PASS `captions.readability`: ok
