#!/usr/bin/env node
// demo-reel renderer: drives an HTML composition (window.setup / window.seek, see runtime/reel-runtime.js)
// with Playwright and pipes frames to FFmpeg. Install Playwright in your work dir first:
//   cd reel-output/work && npm i -D playwright && npx playwright install chromium
//
// node render.mjs --composition work/composition/index.html --plan reel-plan.json \
//   [--events work/audio-events.json] [--audio work/audio.wav] [--out work] [--only A-vertical,B-square]
//   [--formats vertical] [--samples 1] [--shutter 0.35] [--png] [--jobs 2] [--from 0 --to 20]
//   [--stills auto|0,1.4,6.2]
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const DIMS = { vertical: [1080, 1920], square: [1080, 1080], landscape: [1920, 1080], portrait: [1080, 1350] };
const here = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const o = { fps: 30, samples: 1, shutter: 0.35, jobs: 2, png: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i].replace(/^--/, "");
    if (k === "png") o.png = true;
    else o[k] = argv[++i];
  }
  for (const k of ["fps", "samples", "shutter", "jobs", "from", "to"]) if (o[k] !== undefined) o[k] = Number(o[k]);
  if (!o.composition || !o.plan) {
    console.error("usage: render.mjs --composition <index.html> --plan <reel-plan.json> [options]");
    process.exit(2);
  }
  return o;
}

async function loadPlaywright() {
  for (const base of [process.cwd(), path.dirname(path.resolve(process.argv[1])), here]) {
    try {
      const req = createRequire(path.join(base, "noop.js"));
      return req("playwright");
    } catch { /* try next */ }
  }
  console.error("playwright not found: run `npm i -D playwright && npx playwright install chromium` in your work dir");
  process.exit(2);
}

/** Sub-frame times for frame i: spread over the shutter, centred on the frame, never crossing a cut. */
function subTimes(i, o, cuts, duration) {
  const t0 = i / o.fps;
  if (o.samples <= 1) return [t0];
  const lo = Math.max(0, ...cuts.filter(c => c <= t0 + 1e-6));
  const hi = Math.min(duration, ...cuts.filter(c => c > t0 + 1e-6)) - 1e-4;
  return Array.from({ length: o.samples }, (_, k) =>
    Math.min(hi, Math.max(lo, t0 + (k / (o.samples - 1) - 0.5) * o.shutter / o.fps)));
}

function autoStills(plan) {
  const ts = [0];
  for (const s of plan.scenes) {
    ts.push(+s.start + Math.min(1.2, +s.duration * 0.6));
    if (+s.start > 0) ts.push(+s.start + 0.1);
  }
  return [...new Set(ts.map(t => +t.toFixed(2)))].sort((a, b) => a - b);
}

const o = parseArgs(process.argv.slice(2));
const plan = JSON.parse(readFileSync(o.plan, "utf8"));
const events = o.events && existsSync(o.events) ? JSON.parse(readFileSync(o.events, "utf8")) : null;
const outDir = path.resolve(o.out || process.cwd());
const duration = +plan.duration_s;
const cuts = plan.scenes.map(s => +s.start).filter(t => t > 0);
const hookText = Object.fromEntries(plan.hooks.map(h => [h.id, h.text]));
const hooks = plan.variants.map(v => hookText[v.hook]);
const formats = o.formats ? o.formats.split(",") : plan.formats;
const only = o.only ? o.only.split(",") : null;
const jobs = plan.variants.flatMap(v => formats.map(f => ({ v: v.id, hook: hookText[v.hook], f })))
  .filter(j => !only || only.includes(`${j.v}-${j.f}`));
const stills = o.stills === "auto" ? autoStills(plan) : o.stills ? o.stills.split(",").map(Number) : null;
const url = pathToFileURL(path.resolve(o.composition)).href + "?render=1";

const { chromium } = await loadPlaywright();
const browser = await chromium.launch();

async function renderJob(job) {
  const [w, h] = DIMS[job.f];
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", e => errors.push(String(e)));
  page.on("console", m => m.type() === "error" && errors.push(m.text()));
  await page.goto(url);
  await page.evaluate(cfg => window.setup(cfg),
    { variant: job.v, hook: job.hook, hooks, format: job.f, width: w, height: h, fps: o.fps, plan, events });
  const shot = async t => {
    await page.evaluate(t => window.seek(t), t);
    return page.screenshot(o.png ? { type: "png" } : { type: "jpeg", quality: 95 });
  };

  if (stills) {
    const dir = path.join(outDir, "stills");
    mkdirSync(dir, { recursive: true });
    for (const t of stills) {
      await page.evaluate(t => window.seek(t), t);
      await page.screenshot({ path: path.join(dir, `${job.v}-${job.f}-${t.toFixed(2)}.png`) });
    }
  } else {
    const first = Math.round((o.from ?? 0) * o.fps), last = Math.round((o.to ?? duration) * o.fps);
    const seg = o.from !== undefined || o.to !== undefined ? `.${first}-${last}` : "";
    const out = path.join(outDir, `${job.v}-${job.f}${seg}.mp4`);
    const n = Math.max(1, o.samples);
    const args = ["-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", o.png ? "png" : "mjpeg",
      "-framerate", String(o.fps * n), "-i", "-"];
    if (o.audio) args.push("-ss", String(first / o.fps), "-t", String((last - first) / o.fps), "-i", path.resolve(o.audio));
    // Average every n sub-frames into one output frame.
    if (n > 1) args.push("-vf", `tmix=frames=${n},select='eq(mod(n\\,${n})\\,${n - 1})',setpts=N/(${o.fps}*TB)`);
    args.push("-r", String(o.fps), "-map", "0:v");
    if (o.audio) args.push("-map", "1:a", "-c:a", "aac", "-b:a", "256k", "-shortest");
    args.push("-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", out);
    const ff = spawn("ffmpeg", args, { stdio: ["pipe", "inherit", "inherit"] });
    const done = new Promise((res, rej) => ff.on("close", c => (c === 0 ? res() : rej(new Error(`ffmpeg ${c} for ${out}`)))));
    const write = async buf => { if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r)); };
    let blurred = 0;
    for (let i = first; i < last; i++) {
      const ts = subTimes(i, o, cuts, duration);
      if (ts.length === 1) { await write(await shot(ts[0])); continue; }
      // Adaptive: a frame whose shutter edges match is still; reuse one capture instead of rendering n.
      const a = await shot(ts[0]), b = await shot(ts[ts.length - 1]);
      if (a.equals(b)) { for (let k = 0; k < n; k++) await write(a); continue; }
      blurred++;
      await write(a);
      for (const t of ts.slice(1, -1)) await write(await shot(t));
      await write(b);
    }
    ff.stdin.end();
    await done;
    console.log(`rendered ${out}` + (n > 1 ? ` (${blurred}/${last - first} frames motion-blurred)` : ""));
  }
  if (errors.length) console.warn(`${job.v}-${job.f}: page errors:\n  ` + errors.slice(0, 5).join("\n  "));
  await page.close();
}

const queue = [...jobs];
await Promise.all(Array.from({ length: Math.max(1, o.jobs) }, async () => {
  while (queue.length) await renderJob(queue.shift());
}));
await browser.close();
