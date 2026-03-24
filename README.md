# LLM Demos

A collection of (mostly LLM) demos. Though authors are often from Straive, these are **NOT** official products. They're personal projects shared as public open-source (MIT licensed) demos. They contain no confidential data/IP.

## Setup

To run locally:

```bash
git clone https://github.com/sanand00/llmdemos.git
cd llmdemos
just build
npx -y http-server .
```

To add a demo, update [`config.json`](config.json) and commit the changes.

```bash
git add .
git commit -m "Add new demo"
git push
```

See [`AGENTS.md`](AGENTS.md) for the helper workflow and repo discovery commands.

<!--

Prompt to use with Codex when refreshing the demo list (e.g. with Codex - GPT 5.4 medium):

```text
Scan the public GitHub repositories of:
krishna-gramener
prudhvi1709
nitin399-maker
pavankumart18
pythonicvarun
ritesh17rb
yadav-aayansh
mynkpdr

... and add any GOOD repos having GitHub Pages created on/after the latest "created" in config.json.

Add a "reviewed": false field to them to indicate that human review is needed.
Add a "branded": true if any repo's contents include "Straive", "Gramener", "Learning\\s*Mate", "Double\\s*Line", "SG\\s*Analytics" (case-insensitive).
Use the public access GITHUB_TOKEN in .env if you need.
```

codex resume 019d1dbd-de04-7681-9bf5-0479af7fe9ac
-->
