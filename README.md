# LLM Demos

A collection of LLM demos.

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

This is deployed on CloudFlare (root.node@gmail.com) with Zero Trust auth.
