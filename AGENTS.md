# Repo Automation

Use [`scripts/sync_github_demos.py`](/home/vscode/code/llmdemos/scripts/sync_github_demos.py) for GitHub-backed updates.

## Requirements

- `GITHUB_TOKEN` must be available in the shell or `.env`
- Run from the repo root: `/home/vscode/code/llmdemos` or `/home/sanand/code/llmdemos`

## Common Commands

Update `config.json` with `branded: true` when repo contents mention any of:
`Straive`, `Gramener`, `Learning Mate`, `Double Line`, `SG Analytics`

```bash
uv run scripts/sync_github_demos.py brand-config --write
```

List repo details for specific repos:

```bash
uv run scripts/sync_github_demos.py repo-info sanand0/tools ritesh17rb/chart-map
```

Discover GitHub Pages repos for one or more users using the latest `created` date in `config.json` as the default cutoff:

```bash
uv run scripts/sync_github_demos.py discover-pages nitin399-maker pavankumart18 ritesh17rb mynkpdr
```

Use a manual cutoff and include repos already present in `config.json`:

```bash
uv run scripts/sync_github_demos.py discover-pages sanand0 --cutoff 2026-03-01 --include-existing
```

## Notes

- The helper dedupes repos from `config.json` before scanning.
- Branding checks are cached in `.cache/github-repo-helper.json` to make reruns cheap.
- `brand-config` adds `branded: true` only for matching repos and removes stale `branded` flags from non-matches.
- After config updates, rebuild generated outputs with:

```bash
npx -y mustache config.json template.html > index.html
uv run scripts/generate_demos_csv.py
```
