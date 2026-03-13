# LLM Demos

A collection of (mostly LLM) demos. Though authors are often from Straive, these are **NOT** official products. They're personal projects shared as public open-source (MIT licensed) demos. They contain no confidential data/IP.

## Setup

To run locally:

```bash
git clone https://github.com/sanand00/llmdemos.git
cd llmdemos
npx -y mustache config.json template.html > index.html  # just build
npx -y http-server .
```

To add a demo, update [`config.json`](config.json) and commit the changes.

```bash
git add .
git commit -m "Add new demo"
git push
```

<!--

# Update demos

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
Use the public access GITHUB_TOKEN in .env if you need.

-->
