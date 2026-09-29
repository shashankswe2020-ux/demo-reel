<h1 align="center">demo-reel</h1>

<p align="center">
  <strong>AI launch video and viral reel generator for coding agents.</strong><br>
  Turn any repo, website, or screen recording into launch videos for TikTok, Instagram Reels, YouTube Shorts, LinkedIn, and X.
  Every render has to pass 51 automated quality gates before it ships.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License: Apache 2.0"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/requires-FFmpeg-007808" alt="Requires FFmpeg">
  <img src="https://img.shields.io/badge/Agent%20Skill-Claude%20Code%20%7C%20Codex%20%7C%20Copilot%20%7C%20Cursor-C6F432" alt="Agent Skill for Claude Code, Codex, Copilot, and Cursor">
</p>

<p align="center">
  <a href="docs/assets/demo-reel-launch-video.mp4">
    <img src="docs/assets/demo-reel-hero.gif" width="720" alt="demo-reel launch video: 51 checks before your launch video ships, a hook lab leaderboard, 3 hooks × 3 formats, and a QA report scoring VRS 100">
  </a>
</p>
<p align="center">
  <sub>demo-reel made this video of its own repo.
  <a href="docs/assets/demo-reel-launch-video.mp4">Watch with sound (16:9 MP4)</a> ·
  <a href="docs/case-studies/demo-reel/reel-A-vertical.mp4">9:16 version</a> ·
  <a href="docs/case-studies/demo-reel/qa-report.md">QA report: VRS 100 on 9/9 renders</a></sub>
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#use">Use</a> ·
  <a href="skills/demo-reel/references/case-studies.md">Case studies</a> ·
  <a href="skills/demo-reel/references/metrics.md">51 gates</a> ·
  <a href="skills/demo-reel/references/faq.md">FAQ</a>
</p>

## What is demo-reel?

An open-source **Agent Skill** that makes **launch videos and short-form reels** for software projects. Run `/demo-reel`
in Claude Code, Codex CLI, GitHub Copilot, Cursor, or any agent that supports skills. The agent:

1. Writes 10+ hooks from your code.
2. Renders the best 3 in 9:16, 1:1, and 16:9.
3. Ships only renders that pass **51 machine-verified gates**.

After launch, `reel.py learn` picks the winning hook from your real analytics.

## Install

```sh
npx skills add https://github.com/shashankswe2020-ux/demo-reel --skill demo-reel
```

Requires Python 3.10+, FFmpeg, and a frame renderer (Playwright, Remotion, Hyperframes, or Pillow).

## Use

```
/demo-reel                                   # current project
/demo-reel https://example.com --tone cinematic
/demo-reel demo-recording.mov --duration 25
```

You get `reel-output/` with 9 videos, posters, captions, share copy, a posting plan, and a QA report.

## Learn more

| Topic | Reference |
|---|---|
| Workflow and creative laws | [SKILL.md](skills/demo-reel/SKILL.md) |
| All 51 gates and scoring | [metrics.md](skills/demo-reel/references/metrics.md) |
| CLI commands and tests | [toolkit.md](skills/demo-reel/references/toolkit.md) |
| Case studies: demo-reel and local-llmup | [case-studies.md](skills/demo-reel/references/case-studies.md) |
| FAQ | [faq.md](skills/demo-reel/references/faq.md) |

Licensed under [Apache 2.0](LICENSE).
