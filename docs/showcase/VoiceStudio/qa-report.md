# demo-reel QA report: debpalash/VoiceStudio

- Hook (variant A): "646 languages. Fully local."
- Headline feature: **Clone a voice, then speak**

## square

- Viral Readiness Score: **100.0** · blockers: none · shippable: **True** · 49 passed, 0 failed, 2 n/a

| Gate | Result | Detail |
|---|---|---|
| `plan.schema` | PASS | schema=demo-reel/plan@1 |
| `plan.claims_evidence` | PASS | 3 claims verified |
| `plan.lexicon_grounded` | PASS | 9 terms |
| `plan.hook_candidates` | PASS | 10 candidates |
| `plan.hook_type_diversity` | PASS | types=['before_after', 'bold_claim', 'challenge', 'contrarian', 'demo_first', 'negative', 'pain_point', 'question', 'statistic', 'teaser'] |
| `plan.variant_count` | PASS | 3 variants |
| `plan.variant_diversity` | PASS | variant hook types=['before_after', 'bold_claim', 'statistic'] |
| `plan.hook_brevity` | PASS | ok |
| `plan.hook_selection` | PASS | cutoff 82.6 |
| `plan.hook_grounded` | PASS | ok |
| `plan.duration_sum` | PASS | sum=22.00s vs duration_s=22.00s |
| `plan.duration_band` | PASS | 22.0s |
| `plan.hook_scene_length` | PASS | scene 1 role=hook duration=2.8 |
| `plan.first_event` | PASS | first event after t=0 at 0.15s |
| `plan.pattern_interrupts` | PASS | longest gap 0.80s |
| `plan.reading_time` | PASS | ok |
| `plan.text_density` | PASS | 1.64 words/s |
| `plan.numbers_backed` | PASS | ok |
| `plan.safe_zone` | PASS | ok |
| `plan.loop` | PASS | strategy=callback |
| `plan.show_the_thing` | PASS | 100% of runtime sourced from product |
| `plan.product_in_use` | PASS | feature: Clone a voice, then speak |
| `plan.banned_phrases` | PASS | ok |
| `plan.one_liner` | PASS | 9 words |
| `plan.cta` | PASS | last role=cta, target='https://voicestudio.sh/install' |
| `plan.formats` | PASS | ['vertical', 'square', 'landscape'] |
| `plan.share_limits` | PASS | ok |
| `plan.share_fold` | PASS | ok |
| `plan.hashtags` | PASS | ['#voicecloning', '#videodubbing', '#contentcreation', '#opensource', '#voiceai'] |
| `media.container` | PASS | mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac |
| `media.resolution` | PASS | 1080x1080 for square |
| `media.fps` | PASS | avg=30.000 r=30.000 |
| `media.duration` | PASS | 22.00s (plan 22.0) |
| `media.faststart` | PASS | atoms=['ftyp', 'moov', 'free', 'mdat'] |
| `media.file_size` | PASS | 4.0 MB |
| `media.audio_stream` | PASS | 2ch @ 48000 Hz |
| `audio.loudness` | PASS | -14.0 LUFS |
| `audio.true_peak` | PASS | -2.2 dBTP |
| `audio.lra` | PASS | 3.7 LU |
| `audio.leading_silence` | PASS | 0.00s |
| `audio.dead_air` | PASS | longest silence 0.00s |
| `visual.poster` | PASS | frame0 YAVG=69 contrast=130 |
| `visual.first_motion` | PASS | first motion at 0.0666667s |
| `visual.black_frames` | PASS | 0 black frames (0.0%), 0 in hook |
| `visual.static_stretch` | PASS | 2.17s frozen |
| `visual.shot_length` | PASS | 4 cuts, avg shot 4.40s |
| `visual.ui_clutter` | n/a | not vertical |
| `visual.loop_seam` | n/a | loop strategy callback |
| `captions.present` | PASS | 8 cues |
| `captions.timing` | PASS | ok |
| `captions.readability` | PASS | ok |

## landscape

- Viral Readiness Score: **100.0** · blockers: none · shippable: **True** · 49 passed, 0 failed, 2 n/a

| Gate | Result | Detail |
|---|---|---|
| `plan.schema` | PASS | schema=demo-reel/plan@1 |
| `plan.claims_evidence` | PASS | 3 claims verified |
| `plan.lexicon_grounded` | PASS | 9 terms |
| `plan.hook_candidates` | PASS | 10 candidates |
| `plan.hook_type_diversity` | PASS | types=['before_after', 'bold_claim', 'challenge', 'contrarian', 'demo_first', 'negative', 'pain_point', 'question', 'statistic', 'teaser'] |
| `plan.variant_count` | PASS | 3 variants |
| `plan.variant_diversity` | PASS | variant hook types=['before_after', 'bold_claim', 'statistic'] |
| `plan.hook_brevity` | PASS | ok |
| `plan.hook_selection` | PASS | cutoff 82.6 |
| `plan.hook_grounded` | PASS | ok |
| `plan.duration_sum` | PASS | sum=22.00s vs duration_s=22.00s |
| `plan.duration_band` | PASS | 22.0s |
| `plan.hook_scene_length` | PASS | scene 1 role=hook duration=2.8 |
| `plan.first_event` | PASS | first event after t=0 at 0.15s |
| `plan.pattern_interrupts` | PASS | longest gap 0.80s |
| `plan.reading_time` | PASS | ok |
| `plan.text_density` | PASS | 1.64 words/s |
| `plan.numbers_backed` | PASS | ok |
| `plan.safe_zone` | PASS | ok |
| `plan.loop` | PASS | strategy=callback |
| `plan.show_the_thing` | PASS | 100% of runtime sourced from product |
| `plan.product_in_use` | PASS | feature: Clone a voice, then speak |
| `plan.banned_phrases` | PASS | ok |
| `plan.one_liner` | PASS | 9 words |
| `plan.cta` | PASS | last role=cta, target='https://voicestudio.sh/install' |
| `plan.formats` | PASS | ['vertical', 'square', 'landscape'] |
| `plan.share_limits` | PASS | ok |
| `plan.share_fold` | PASS | ok |
| `plan.hashtags` | PASS | ['#voicecloning', '#videodubbing', '#contentcreation', '#opensource', '#voiceai'] |
| `media.container` | PASS | mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac |
| `media.resolution` | PASS | 1920x1080 for landscape |
| `media.fps` | PASS | avg=30.000 r=30.000 |
| `media.duration` | PASS | 22.00s (plan 22.0) |
| `media.faststart` | PASS | atoms=['ftyp', 'moov', 'free', 'mdat'] |
| `media.file_size` | PASS | 5.0 MB |
| `media.audio_stream` | PASS | 2ch @ 48000 Hz |
| `audio.loudness` | PASS | -14.0 LUFS |
| `audio.true_peak` | PASS | -2.2 dBTP |
| `audio.lra` | PASS | 3.7 LU |
| `audio.leading_silence` | PASS | 0.00s |
| `audio.dead_air` | PASS | longest silence 0.00s |
| `visual.poster` | PASS | frame0 YAVG=70 contrast=130 |
| `visual.first_motion` | PASS | first motion at 0.0666667s |
| `visual.black_frames` | PASS | 0 black frames (0.0%), 0 in hook |
| `visual.static_stretch` | PASS | 2.20s frozen |
| `visual.shot_length` | PASS | 4 cuts, avg shot 4.40s |
| `visual.ui_clutter` | n/a | not vertical |
| `visual.loop_seam` | n/a | loop strategy callback |
| `captions.present` | PASS | 8 cues |
| `captions.timing` | PASS | ok |
| `captions.readability` | PASS | ok |

## vertical

- Viral Readiness Score: **100.0** · blockers: none · shippable: **True** · 50 passed, 0 failed, 1 n/a

| Gate | Result | Detail |
|---|---|---|
| `plan.schema` | PASS | schema=demo-reel/plan@1 |
| `plan.claims_evidence` | PASS | 3 claims verified |
| `plan.lexicon_grounded` | PASS | 9 terms |
| `plan.hook_candidates` | PASS | 10 candidates |
| `plan.hook_type_diversity` | PASS | types=['before_after', 'bold_claim', 'challenge', 'contrarian', 'demo_first', 'negative', 'pain_point', 'question', 'statistic', 'teaser'] |
| `plan.variant_count` | PASS | 3 variants |
| `plan.variant_diversity` | PASS | variant hook types=['before_after', 'bold_claim', 'statistic'] |
| `plan.hook_brevity` | PASS | ok |
| `plan.hook_selection` | PASS | cutoff 82.6 |
| `plan.hook_grounded` | PASS | ok |
| `plan.duration_sum` | PASS | sum=22.00s vs duration_s=22.00s |
| `plan.duration_band` | PASS | 22.0s |
| `plan.hook_scene_length` | PASS | scene 1 role=hook duration=2.8 |
| `plan.first_event` | PASS | first event after t=0 at 0.15s |
| `plan.pattern_interrupts` | PASS | longest gap 0.80s |
| `plan.reading_time` | PASS | ok |
| `plan.text_density` | PASS | 1.64 words/s |
| `plan.numbers_backed` | PASS | ok |
| `plan.safe_zone` | PASS | ok |
| `plan.loop` | PASS | strategy=callback |
| `plan.show_the_thing` | PASS | 100% of runtime sourced from product |
| `plan.product_in_use` | PASS | feature: Clone a voice, then speak |
| `plan.banned_phrases` | PASS | ok |
| `plan.one_liner` | PASS | 9 words |
| `plan.cta` | PASS | last role=cta, target='https://voicestudio.sh/install' |
| `plan.formats` | PASS | ['vertical', 'square', 'landscape'] |
| `plan.share_limits` | PASS | ok |
| `plan.share_fold` | PASS | ok |
| `plan.hashtags` | PASS | ['#voicecloning', '#videodubbing', '#contentcreation', '#opensource', '#voiceai'] |
| `media.container` | PASS | mov,mp4,m4a,3gp,3g2,mj2 / h264 yuv420p / aac |
| `media.resolution` | PASS | 1080x1920 for vertical |
| `media.fps` | PASS | avg=30.000 r=30.000 |
| `media.duration` | PASS | 22.00s (plan 22.0) |
| `media.faststart` | PASS | atoms=['ftyp', 'moov', 'free', 'mdat'] |
| `media.file_size` | PASS | 5.3 MB |
| `media.audio_stream` | PASS | 2ch @ 48000 Hz |
| `audio.loudness` | PASS | -14.0 LUFS |
| `audio.true_peak` | PASS | -2.2 dBTP |
| `audio.lra` | PASS | 3.7 LU |
| `audio.leading_silence` | PASS | 0.00s |
| `audio.dead_air` | PASS | longest silence 0.00s |
| `visual.poster` | PASS | frame0 YAVG=61 contrast=130 |
| `visual.first_motion` | PASS | first motion at 0.0666667s |
| `visual.black_frames` | PASS | 0 black frames (0.0%), 0 in hook |
| `visual.static_stretch` | PASS | 2.17s frozen |
| `visual.shot_length` | PASS | 4 cuts, avg shot 4.40s |
| `visual.ui_clutter` | PASS | ratio 0.00 |
| `visual.loop_seam` | n/a | loop strategy callback |
| `captions.present` | PASS | 8 cues |
| `captions.timing` | PASS | ok |
| `captions.readability` | PASS | ok |

