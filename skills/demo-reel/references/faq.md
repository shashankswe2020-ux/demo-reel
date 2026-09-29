# FAQ

**How do I make a launch video for my GitHub project?**
Install the skill, open your repo in an agent that supports skills, and run `/demo-reel`. It reads the code, writes the hooks, renders the videos, and checks them.

**Which platforms and formats does it produce?**
Vertical 9:16 (1080×1920) for TikTok, Instagram Reels, and YouTube Shorts. Square 1:1 for LinkedIn and X feeds. Landscape 16:9 for X, YouTube, and your website. Each render comes with an SRT captions file and a poster image.

**Which AI agents does it work with?**
Any agent that loads Agent Skills: Claude Code, OpenAI Codex CLI, GitHub Copilot, Cursor, Gemini CLI, and opencode. For other agents, point them at `skills/demo-reel/SKILL.md`.

**Does it need a paid API or cloud rendering?**
No. The toolkit is stdlib-only Python plus FFmpeg, and rendering runs on your machine with Playwright, Remotion, Hyperframes, or Pillow.

**What makes a reel "viral-ready" here?**
51 measurable gates: sound and motion in the first half-second, a hook of 8 words or fewer, a pattern interrupt at least every 2.5 s, readable text holds, −14 LUFS loudness, platform safe zones, and on-screen claims traced to your source. Whether it *actually* goes viral is measured after posting, with `reel.py learn`.

**How is it different from /brag?**
/brag makes one landscape video behind one lint gate. demo-reel makes 9 renders per run (3 hooks × 3 formats), runs 227 gate evaluations, verifies claims, and picks the winning hook from real analytics. See the scorecard in [metrics.md](metrics.md#scorecard-against-brag-reproducible).
