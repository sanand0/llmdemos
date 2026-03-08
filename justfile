build:
  npx -y mustache config.json template.html > index.html
  uv run scripts/generate_demos_csv.py
