/* demo-reel runtime: a deterministic, beat-aware timeline for HTML compositions.
 *
 * A composition loads this file with <script src>, then calls Reel.define({ setup, render }).
 * The renderer (scripts/render.mjs) drives it with window.setup(cfg) and window.seek(t).
 * Opened in a browser without ?render=1, it becomes a scrubbable preview (serve over http):
 *   space play/pause · ←/→ ±1 s (shift ±5) · ,/. ±1 frame · [/] prev/next scene · l loop scene
 *   v next variant · f next format · h hide HUD · URL: ?t=4.2&variant=B&format=square
 */
(function () {
  "use strict";
  const DIMS = { vertical: [1080, 1920], square: [1080, 1080], landscape: [1920, 1080], portrait: [1080, 1350] };

  // ---------- math, easing, keyframes ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ease = {
    linear: x => x,
    inCubic: x => x * x * x,
    outCubic: x => 1 - Math.pow(1 - x, 3),
    inOutCubic: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    inExpo: x => (x <= 0 ? 0 : Math.pow(2, 10 * x - 10)),
    outExpo: x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
    inOutExpo: x => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2),
    outBack: x => { const c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
  };
  /** Progress of t through [a, a+d], eased. */
  const prog = (t, a, d, e = ease.linear) => e(clamp(d > 0 ? (t - a) / d : t >= a ? 1 : 0));
  /** Damped spring from 0 to 1 starting at t0 (overshoots, then settles). */
  const spring = (t, t0, { freq = 4.5, damp = 0.35 } = {}) => {
    if (t <= t0) return 0;
    const x = t - t0, w = 2 * Math.PI * freq;
    return 1 - Math.exp(-damp * w * x) * Math.cos(w * Math.sqrt(1 - damp * damp) * x);
  };
  /** Piecewise keyframes: keys(t, [[0, 0], [0.4, 1, ease.outExpo], [1.2, 0.8]]) → value at t. */
  const keys = (t, ks) => {
    if (t <= ks[0][0]) return ks[0][1];
    for (let i = 1; i < ks.length; i++) {
      const [t1, v1, e = ease.inOutCubic] = ks[i], [t0, v0] = ks[i - 1];
      if (t <= t1) return lerp(v0, v1, e(clamp((t - t0) / (t1 - t0 || 1))));
    }
    return ks[ks.length - 1][1];
  };
  /** Seeded RNG; never use Math.random() for visuals. */
  const mulberry32 = seed => () => {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let r = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
  const hash = n => mulberry32(Math.floor(n) * 2654435761)();
  /** Map output progress onto a measured cumulative-progress curve, enforcing monotonicity. */
  const remapProgress = (u, values) => {
    if (!Array.isArray(values) || values.length < 2) return clamp(u);
    const curve = [];
    let running = -Infinity;
    for (const value of values) {
      running = Math.max(running, Number.isFinite(+value) ? +value : running);
      curve.push(running);
    }
    const start = curve[0], span = curve[curve.length - 1] - start;
    if (!(span > 0)) return clamp(u);
    const target = start + clamp(u) * span;
    let lo = 0, hi = curve.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (curve[mid] < target) lo = mid + 1; else hi = mid;
    }
    if (lo === 0) return 0;
    const a = curve[lo - 1], b = curve[lo];
    const fraction = b > a ? (target - a) / (b - a) : 1;
    return ((lo - 1) + fraction) / (curve.length - 1);
  };

  // ---------- audio events (from `reel.py beats --out audio-events.json`) ----------
  const KIND = { kick: "low", snare: "mid", hat: "high", low: "low", mid: "mid", high: "high" };
  function makeAudio(ev) {
    const beats = (ev && ev.beats) || [];
    const period = beats.length > 1 ? (beats[beats.length - 1] - beats[0]) / (beats.length - 1) : 0.5;
    const first = beats.length ? beats[0] : 0;
    const downbeats = (ev && ev.downbeats) || [];
    const barPhase0 = downbeats.length && beats.length ? Math.round((downbeats[0] - first) / period) : 0;
    const lastBefore = (arr, t) => {
      let lo = 0, hi = arr.length - 1, best = -1;
      while (lo <= hi) { const m = (lo + hi) >> 1; if (arr[m] <= t) { best = m; lo = m + 1; } else hi = m - 1; }
      return best;
    };
    const A = {
      bpm: (ev && ev.bpm) || 60 / period, period, beats, downbeats,
      /** Continuous beat index: 3.0 exactly on beat 3, 3.5 halfway to beat 4. */
      beatAt: t => {
        const i = lastBefore(beats, t);
        if (i < 0 || i >= beats.length - 1) return (t - first) / period;
        return i + (t - beats[i]) / (beats[i + 1] - beats[i]);
      },
      timeOfBeat: i => (beats[i] !== undefined ? beats[i] : first + i * period),
      nearestBeat: t => A.timeOfBeat(Math.round(A.beatAt(t))),
      beatBefore: t => A.timeOfBeat(Math.floor(A.beatAt(t) + 1e-6)),
      /** Decaying pulse after the last onset of a band: 1 on the hit, 0.5 after halfLife seconds. */
      hit: (kind, t, halfLife = 0.12) => {
        const arr = ((ev && ev.onsets) || {})[KIND[kind] || kind] || [];
        const i = lastBefore(arr, t);
        return i < 0 ? 0 : Math.pow(2, -(t - arr[i]) / halfLife);
      },
      /** Loudness envelope 0..1 for rms | low | mid | high. */
      env: (name, t) => {
        const e = ev && ev.env, arr = e && e[name];
        if (!arr || !arr.length) return 0;
        const x = clamp(t / e.hop_s, 0, arr.length - 1), i = Math.floor(x);
        return lerp(arr[i], arr[Math.min(i + 1, arr.length - 1)], x - i);
      },
    };
    A.barPhase0 = barPhase0;
    return A;
  }

  // ---------- timeline ----------
  let def = null, cfg = null, scenes = [], audio = makeAudio(null), fps = 30, duration = 20;
  const frameIdx = t => Math.floor(t * fps + 1e-6);

  function frameAt(t) {
    const t0 = frameIdx(t) / fps;
    let si = scenes.findIndex((s, i) => t >= s.start && (t < s.end || (i === scenes.length - 1 && t <= s.end)));
    if (si < 0) si = t < 0 ? 0 : scenes.length - 1;
    const s = scenes[si] || { id: "", start: 0, end: duration };
    const beat = audio.beatAt(t), bar = (beat - audio.barPhase0) / 4;
    return {
      t, frame: frameIdx(t), frameT: t0, scene: s.id, sceneIndex: si, lt: t - s.start,
      p: clamp((t - s.start) / ((s.end - s.start) || 1)), sceneStart: s.start, sceneEnd: s.end,
      beat, beatPhase: beat - Math.floor(beat), bar, barPhase: bar - Math.floor(bar),
      a: {
        kick: audio.hit("low", t), snare: audio.hit("mid", t), hat: audio.hit("high", t, 0.06),
        rms: audio.env("rms", t), low: audio.env("low", t), mid: audio.env("mid", t), high: audio.env("high", t),
      },
      cfg,
    };
  }

  function applyFormat(format, w, h) {
    document.documentElement.style.setProperty("--w", w + "px");
    document.documentElement.style.setProperty("--h", h + "px");
    document.documentElement.style.setProperty("--u", Math.min(w, h) / 100 + "px");
    document.body.classList.remove(...Object.keys(DIMS));
    document.body.classList.add(format);
  }

  async function setup(c) {
    if (!def) throw new Error("composition never called Reel.define()");
    cfg = c;
    fps = c.fps || 30;
    const plan = c.plan || {};
    duration = +plan.duration_s || def.duration || 20;
    scenes = (plan.scenes || def.scenes || []).map(s => ({ id: s.id, start: +s.start, end: +s.start + +s.duration }));
    audio = makeAudio(c.events);
    Reel.audio = audio;
    const [w, h] = [c.width || DIMS[c.format][0], c.height || DIMS[c.format][1]];
    applyFormat(c.format, w, h);
    await Promise.all((def.fonts || []).map(f => document.fonts.load(f)));
    await document.fonts.ready;
    if (def.setup) await def.setup(c, Reel);
    await document.fonts.ready;
  }

  function seek(t) {
    return def.render(frameAt(t), Reel);
  }

  // ---------- preview ----------
  async function preview() {
    const q = new URLSearchParams(location.search);
    const load = async (url, kind) => {
      try { const r = await fetch(url); return r.ok ? (kind === "json" ? r.json() : r) : null; } catch { return null; }
    };
    const plan = await load(q.get("plan") || "../../reel-plan.json", "json");
    const events = await load(q.get("events") || "../audio-events.json", "json");
    if (!plan) {
      document.body.insertAdjacentHTML("beforeend", "<pre style='position:fixed;inset:0;z-index:99;color:#fff;background:#000;padding:2em'>" +
        "Preview needs http: run `python3 -m http.server` in reel-output/ and open work/composition/index.html.\n" +
        "Override paths with ?plan=…&events=…&audio=…</pre>");
      return;
    }
    const variants = plan.variants || [], hooks = Object.fromEntries((plan.hooks || []).map(h => [h.id, h.text]));
    const formats = plan.formats || ["vertical"];
    const variant = q.get("variant") || (variants[0] || {}).id, format = q.get("format") || formats[0];
    const v = variants.find(x => x.id === variant) || variants[0] || {};
    const [w, h] = DIMS[format];
    Object.assign(document.documentElement.style, { width: w + "px", height: h + "px", overflow: "hidden" });
    Object.assign(document.body.style, { width: w + "px", height: h + "px", transformOrigin: "0 0" });
    const fit = () => { document.body.style.transform = `scale(${Math.min(innerWidth / w, innerHeight / h)})`; };
    addEventListener("resize", fit); fit();
    await setup({ variant: v.id, hook: hooks[v.hook] || "", hooks: variants.map(x => hooks[x.hook]), format,
                  width: w, height: h, fps: 30, plan, events });

    const audioEl = new Audio(q.get("audio") || "../audio.wav");
    const hud = document.createElement("div");
    hud.style.cssText = "position:fixed;left:8px;top:8px;z-index:99;font:12px/1.4 Menlo,monospace;color:#fff;" +
      "background:rgba(0,0,0,.6);padding:4px 8px;border-radius:4px;pointer-events:none;transform-origin:0 0";
    document.documentElement.appendChild(hud);
    let t = clamp(+q.get("t") || 0, 0, duration), playing = false, loop = null, wall = 0, hudOn = true;
    const draw = () => {
      seek(t);
      const f = frameAt(t);
      hud.style.display = hudOn ? "block" : "none";
      hud.textContent = `${t.toFixed(3)}s  f${f.frame}  ${f.scene}  beat ${f.beat.toFixed(2)}  ` +
        `${v.id}/${format}${loop ? "  LOOP" : ""}${playing ? "" : "  ❚❚"}`;
    };
    const tick = now => {
      if (!playing) return;
      t = audioEl.duration ? audioEl.currentTime : t + (now - wall) / 1000;
      wall = now;
      if (loop && t >= loop[1]) { t = loop[0]; audioEl.currentTime = t; }
      if (t >= duration) { t = 0; audioEl.currentTime = 0; }
      draw();
      requestAnimationFrame(tick);
    };
    const go = nt => { t = clamp(nt, 0, duration); audioEl.currentTime = t; draw(); };
    const reload = (k, val) => { q.set(k, val); q.set("t", t.toFixed(3)); location.search = q.toString(); };
    addEventListener("keydown", e => {
      const k = e.key;
      if (k === " ") { playing = !playing; if (playing) { audioEl.currentTime = t; audioEl.play().catch(() => {}); wall = performance.now(); requestAnimationFrame(tick); } else audioEl.pause(); }
      else if (k === "ArrowRight") go(t + (e.shiftKey ? 5 : 1));
      else if (k === "ArrowLeft") go(t - (e.shiftKey ? 5 : 1));
      else if (k === ".") go((frameIdx(t) + 1) / fps);
      else if (k === ",") go((frameIdx(t) - 1) / fps);
      else if (k === "]") { const s = scenes.find(s => s.start > t + 1e-3); if (s) go(s.start); }
      else if (k === "[") { const prev = scenes.filter(s => s.start < t - 0.05); if (prev.length) go(prev[prev.length - 1].start); }
      else if (k === "l") { const s = scenes[frameAt(t).sceneIndex]; loop = loop ? null : [s.start, s.end]; draw(); }
      else if (k === "h") { hudOn = !hudOn; draw(); }
      else if (k === "v" && variants.length) reload("variant", variants[(variants.indexOf(v) + 1) % variants.length].id);
      else if (k === "f") reload("format", formats[(formats.indexOf(format) + 1) % formats.length]);
      else return;
      e.preventDefault();
    });
    draw();
  }

  const Reel = {
    define(d) {
      def = d;
      if (!new URLSearchParams(location.search).has("render")) {
        if (document.readyState === "loading") addEventListener("DOMContentLoaded", preview); else preview();
      }
    },
    clamp, lerp, ease, prog, spring, keys, mulberry32, hash, remapProgress, DIMS,
    frameIdx, frameAt, audio,
    /** Shrink an element's font size until it fits its own box (call in setup, after fonts load). */
    fit(el, { max = 200, min = 12 } = {}) {
      let size = max;
      el.style.fontSize = size + "px";
      while (size > min && (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)) {
        size -= 1;
        el.style.fontSize = size + "px";
      }
      return size;
    },
  };
  window.Reel = Reel;
  window.setup = setup;
  window.seek = seek;
})();
