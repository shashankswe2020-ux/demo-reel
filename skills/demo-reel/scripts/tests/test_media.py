import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reelkit import captions, experiment  # noqa: E402
from reelkit.cli import main  # noqa: E402
from reelkit.ffmpeg import run, tool  # noqa: E402
from reelkit.finish import finish  # noqa: E402
from reelkit.hotspots import hotspots  # noqa: E402
from reelkit.media_qa import analyze  # noqa: E402
from reelkit.plan_lint import variant_cues  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def ffmpeg(*args):
    run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", *args])


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg not installed")
class MediaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="demo-reel-test-"))
        cls.master = cls.tmp / "master.mp4"
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=1920x1080:r=30:d=20",
               "-f", "lavfi", "-i", "sine=f=220:d=20:sample_rate=48000",
               "-vf", "hue=h='floor(t/2.5)*70'", "-c:v", "libx264", "-preset", "ultrafast",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(cls.master))
        cls.good = finish(cls.master, cls.tmp / "renders" / "reel-A-vertical.mp4", "vertical",
                          poster_t=3.0, duration=20.0)
        cls.plan = json.loads((FIXTURES / "reel-plan.json").read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_finished_render_passes_technical_gates(self):
        srt = self.good.with_suffix(".srt")
        srt.write_text(captions.render_srt(variant_cues(self.plan, "A")))
        checks, measured = analyze(self.good, "vertical", 20.0, srt, None)
        by_id = {c.id: c for c in checks}
        for cid in ("media.container", "media.resolution", "media.fps", "media.duration", "media.faststart",
                    "media.audio_stream", "audio.loudness", "audio.true_peak", "audio.lra",
                    "audio.leading_silence", "audio.dead_air", "visual.poster", "visual.first_motion",
                    "visual.black_frames", "visual.static_stretch", "visual.ui_clutter",
                    "captions.present", "captions.timing", "captions.readability"):
            self.assertTrue(by_id[cid].passed, f"{cid}: {by_id[cid].message}")
        self.assertTrue(self.good.with_suffix(".jpg").is_file())
        self.assertAlmostEqual(measured["duration"], 20.0, delta=0.1)

    def test_full_range_peaky_master_is_normalized(self):
        hot = self.tmp / "hot.mp4"
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=16",
               "-f", "lavfi", "-i", "aevalsrc='0.97*sin(2*PI*440*t)*lt(mod(t,0.5),0.03)':s=48000:d=16",
               "-vf", "scale=out_range=pc,format=yuvj420p", "-c:v", "libx264", "-preset", "ultrafast",
               "-c:a", "aac", "-shortest", str(hot))
        out = finish(hot, self.tmp / "hot-out.mp4", "vertical", poster_t=1.0)
        by_id = {c.id: c for c in analyze(out, "vertical", 16.0, None, None)[0]}
        for cid in ("media.container", "audio.true_peak"):
            self.assertTrue(by_id[cid].passed, f"{cid}: {by_id[cid].message}")

    def test_dead_open_fails_hook_gates(self):
        bad = self.tmp / "bad.mp4"
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=20",
               "-f", "lavfi", "-i", "sine=f=440:d=20:sample_rate=48000",
               "-vf", "fade=in:st=2.5:d=0.04", "-af", "volume='if(lt(t,2.5),0,1)':eval=frame",
               "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
               "-shortest", str(bad))
        checks, _ = analyze(bad, "vertical", 20.0, None, None)
        by_id = {c.id: c for c in checks}
        for cid in ("media.faststart", "visual.poster", "visual.first_motion", "visual.black_frames",
                    "audio.leading_silence", "audio.dead_air", "audio.loudness", "captions.present"):
            self.assertFalse(by_id[cid].passed, f"{cid} should fail: {by_id[cid].message}")

    def test_check_command_scores_every_variant(self):
        plan = dict(self.plan, formats=["vertical"])
        plan["project"] = dict(plan["project"], root=str(FIXTURES / "project"))
        plan_path = self.tmp / "reel-plan.json"
        plan_path.write_text(json.dumps(plan))
        renders = self.good.parent
        for v in ("A", "B", "C"):
            target = renders / f"reel-{v}-vertical.mp4"
            if target != self.good:
                shutil.copy(self.good, target)
            target.with_suffix(".srt").write_text(captions.render_srt(variant_cues(plan, v)))
        code = main(["check", str(plan_path), "--renders", str(renders)])
        report = json.loads((renders / "qa-report.json").read_text())
        self.assertEqual(len(report["renders"]), 3)
        self.assertGreaterEqual(report["min_vrs"], 85.0, json.dumps(report["renders"][0]["score"]))
        self.assertEqual(code, 0 if report["shippable"] else 2)

    def test_hotspots_find_the_busy_window(self):
        rec = self.tmp / "recording.mp4"
        ffmpeg("-f", "lavfi", "-i", "sine=f=330:d=60:sample_rate=48000",
               "-filter_complex", "color=c=gray:s=320x180:r=30:d=30[a];testsrc2=s=320x180:r=30:d=20[b];"
                                  "color=c=gray:s=320x180:r=30:d=10[c];[a][b][c]concat=n=3:v=1:a=0[v]",
               "-map", "[v]", "-map", "0:a", "-af", "volume='if(between(t,30,50),1,0.02)':eval=frame",
               "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", str(rec))
        spots = hotspots(rec, window=20.0, top=2, min_gap=2.0)
        self.assertTrue(26.0 <= spots[0]["start"] <= 34.0, spots)


class ExperimentTest(unittest.TestCase):
    def test_clear_winner_and_thin_data(self):
        totals = {
            "A": {"impressions": 4000, "views_3s": 2200, "completions": 700, "shares": 40, "saves": 0, "follows": 0},
            "B": {"impressions": 4000, "views_3s": 1500, "completions": 400, "shares": 12, "saves": 0, "follows": 0},
        }
        result = experiment.evaluate(totals, "hook_rate")
        self.assertEqual(result["leader"], "A")
        self.assertTrue(result["decision"].startswith("ship A"))
        totals["B"]["impressions"] = 100
        totals["B"]["views_3s"] = 30
        self.assertTrue(experiment.evaluate(totals)["decision"].startswith("keep testing"))


if __name__ == "__main__":
    unittest.main()
