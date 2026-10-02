import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reelkit import captions, experiment  # noqa: E402
from reelkit.beats import analyze_audio  # noqa: E402
from reelkit.cli import main  # noqa: E402
from reelkit.ffmpeg import probe, run, tool  # noqa: E402
from reelkit.finish import finish  # noqa: E402
from reelkit.hotspots import hotspots  # noqa: E402
from reelkit.media_qa import analyze  # noqa: E402
from reelkit.plan_lint import variant_cues  # noqa: E402
from reelkit.sheet import contact_sheet  # noqa: E402

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

    def test_brand_color_survives_bt709_playback(self):
        # Untagged BT.601 output shifted #FF5A1F to #FF6419 in players that assume BT.709 for HD.
        png, master = self.tmp / "brand.png", self.tmp / "brand.mp4"
        ffmpeg("-f", "lavfi", "-i", "color=c=0xFF5A1F:s=1080x1920", "-frames:v", "1", str(png))
        ffmpeg("-loop", "1", "-framerate", "30", "-i", str(png), "-f", "lavfi", "-i", "sine=f=220:sample_rate=48000",
               "-t", "16", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
               str(master))
        out = finish(master, self.tmp / "brand-out.mp4", "vertical", poster_t=1.0)
        v = next(s for s in probe(out)["streams"] if s["codec_type"] == "video")
        self.assertEqual([v.get(k) for k in ("color_range", "color_space", "color_primaries", "color_transfer")],
                         ["tv", "bt709", "bt709", "bt709"])
        for t in (0.0, 2.0):  # baked poster frame and an ordinary frame
            rgb = subprocess.run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", str(out),
                                  "-frames:v", "1", "-vf", "crop=4:4:500:900,scale=1:1:in_color_matrix=bt709:"
                                  "in_range=tv,format=rgb24", "-f", "rawvideo", "-"],
                                 capture_output=True, check=True).stdout
            for got, want in zip(rgb[:3], (0xFF, 0x5A, 0x1F)):
                self.assertLessEqual(abs(got - want), 3, f"t={t}: {rgb[:3].hex()} vs ff5a1f")

    def test_contact_sheet_tiles_both_sides_of_every_cut(self):
        cutty = self.tmp / "cutty.mp4"
        colors = ("red", "blue", "yellow", "green", "white")
        ffmpeg("-filter_complex", ";".join(f"color=c={c}:s=320x180:r=30:d=2[c{i}]" for i, c in enumerate(colors))
               + ";" + "".join(f"[c{i}]" for i in range(len(colors))) + f"concat=n={len(colors)}:v=1:a=0[v]",
               "-map", "[v]", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(cutty))
        sheet = contact_sheet(cutty, self.tmp / "cuts.png", cuts=True, cols=4, width=120)
        self.assertEqual(sheet["times"], [1.967, 2.0, 3.967, 4.0, 5.967, 6.0, 7.967, 8.0])
        img = next(s for s in probe(sheet["out"])["streams"] if s["codec_type"] == "video")
        self.assertEqual((img["width"], img["height"]), (4 * 120 + 5 * 6, 2 * 68 + 3 * 6))
        even = contact_sheet(cutty, self.tmp / "even.png", n=6, cols=3, width=120)
        self.assertEqual(len(even["times"]), 6)

    def test_beats_recover_tempo_phase_and_downbeat(self):
        track = self.tmp / "click.wav"
        # 120 BPM from 0.25 s, accented kick on every bar's first beat, noise snare on the backbeat.
        ffmpeg("-f", "lavfi", "-i", "aevalsrc='gte(t,0.25)*(sin(2*PI*55*t)*exp(-25*mod(t-0.25,0.5))"
               "*(1+0.6*lt(mod(t-0.25,2),0.1))+0.5*(random(0)*2-1)*exp(-40*mod(t-0.75,1))*gte(t,0.75))'"
               ":s=48000:d=20", str(track))
        ev = analyze_audio(track)
        self.assertAlmostEqual(ev["bpm"], 120.0, delta=0.5)
        self.assertAlmostEqual(ev["offset_s"], 0.25, delta=0.02)
        self.assertAlmostEqual(ev["downbeats"][0], 0.25, delta=0.02)
        self.assertAlmostEqual(ev["downbeats"][1] - ev["downbeats"][0], 2.0, delta=0.02)
        self.assertEqual(len(ev["onsets"]["low"]), 40)
        self.assertAlmostEqual(analyze_audio(track, bpm=120)["offset_s"], 0.25, delta=0.02)

    def test_sub_bass_master_stays_under_true_peak_ceiling(self):
        deep = self.tmp / "deep.mp4"
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=16",
               "-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*24*t)+0.2*sin(2*PI*330*t)*exp(-6*mod(t,0.5))':s=48000:d=16",
               "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
               "-shortest", str(deep))
        out = finish(deep, self.tmp / "deep-out.mp4", "vertical")
        by_id = {c.id: c for c in analyze(out, "vertical", 16.0, None, None)[0]}
        self.assertTrue(by_id["audio.true_peak"].passed, by_id["audio.true_peak"].message)

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


SCRIPTS = Path(__file__).resolve().parents[1]
NODE_DIR = os.environ.get("DEMO_REEL_NODE_DIR", "")


def _have_playwright() -> bool:
    if not (shutil.which("node") and NODE_DIR):
        return False
    probe_js = "require(require('module').createRequire(process.argv[1] + '/x.js').resolve('playwright'))"
    return subprocess.run(["node", "-e", probe_js, NODE_DIR], capture_output=True).returncode == 0


@unittest.skipUnless(HAVE_FFMPEG and _have_playwright(), "set DEMO_REEL_NODE_DIR to a dir with playwright installed")
class RendererTest(unittest.TestCase):
    def test_template_renders_stills_and_motion_blurred_segment(self):
        tmp = Path(tempfile.mkdtemp(prefix="demo-reel-render-"))
        try:
            comp = tmp / "composition"
            comp.mkdir()
            shutil.copy(SCRIPTS / "runtime" / "reel-runtime.js", comp)
            shutil.copy(SCRIPTS / "runtime" / "template.html", comp / "index.html")
            base = ["node", str(SCRIPTS / "render.mjs"), "--composition", str(comp / "index.html"),
                    "--plan", str(FIXTURES / "reel-plan.json"), "--out", str(tmp), "--only", "A-vertical"]
            for extra in (["--stills", "auto"], ["--samples", "4", "--from", "0", "--to", "1"]):
                proc = subprocess.run(base + extra, cwd=NODE_DIR, capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertNotIn("page errors", proc.stderr + proc.stdout)
            self.assertGreaterEqual(len(list((tmp / "stills").glob("A-vertical-*.png"))), 5)
            v = next(s for s in probe(tmp / "A-vertical.0-30.mp4")["streams"] if s["codec_type"] == "video")
            self.assertEqual((v["width"], v["height"], v["nb_frames"]), (1080, 1920, "30"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


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
