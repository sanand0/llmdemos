# LLM Demos

A collection of LLM demos.

This list aggregates interactive projects from [prudhvi1709](https://github.com/prudhvi1709),
[krishna-gramener](https://github.com/krishna-gramener) and
[nitin399-maker](https://github.com/nitin399-maker) that were updated after **June 2025**.

## Setup

To run locally:

```bash
git clone https://github.com/sanand00/llmdemos.git
cd llmdemos
npx -y mustache config.json template.html > index.html
npx -y http-server .
```

To add a demo, update [`config.json`](config.json) and commit the changes.

```bash
git add .
git commit -m "Add new demo"
git push
```

This is deployed at [llmdemos.s-anand.net](https://llmdemos.s-anand.net/) via CloudFlare DNS (root.node@gmail.com) via [Zero Trust auth](https://one.dash.cloudflare.com/2c483e1dd66869c9554c6949a2d17d96/access/apps/self-hosted/23c76465-2ba4-4a39-b742-37bead262a28/edit).
