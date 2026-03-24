build:
  uv run scripts/sync_github_demos.py brand-config --write
  npx -y mustache config.json template.html > index.html
  uv run scripts/generate_demos_csv.py
