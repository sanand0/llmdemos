build:
  uv run scripts/sync_github_demos.py brand-config --write
  npx -y mustache config.json template.html > index.html
  uv run scripts/generate_demos_csv.py
upload:
  python3 -c "import csv, json, sys; json.dump({'values': list(csv.reader(sys.stdin))}, sys.stdout)" < open-demos.csv > upload.json
  gws sheets spreadsheets values clear --params '{"spreadsheetId": "1_6TRACgbK78BcFclidQAumt5Ves-300jbvG_S-3xPKI", "range": "repos"}'
  gws sheets spreadsheets values update --params '{"spreadsheetId": "1_6TRACgbK78BcFclidQAumt5Ves-300jbvG_S-3xPKI", "range": "repos", "valueInputOption": "USER_ENTERED"}' --json "$(cat upload.json)"
