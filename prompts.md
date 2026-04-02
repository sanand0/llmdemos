# Prompts

## 2 Apr 2026

Scan the public GitHub repositories of:
mynkpdr
pavankumart18
prudhvi1709
ritesh17rb

... and add any new GOOD repos having GitHub Pages created on/after the latest "created" in config.json.

Add a "reviewed": false field to them to indicate that human review is needed.
Use the public access GITHUB_TOKEN in .env if you need.

## 24 Mar 2026

Scan the public GitHub repositories of:
nitin399-maker
pavankumart18
ritesh17rb
mynkpdr

... and add any GOOD repos having GitHub Pages created on/after the latest "created" in config.json.

Add a "reviewed": false field to them to indicate that human review is needed.
Use the public access GITHUB_TOKEN in .env if you need.

---

Add a "branded": true if any repo's contents include "Straive", "Gramener", "Learning\s*Mate", "Double\s*Line", "SG\s*Analytics" (case-insensitive). Update config.json EFFICIENTLY. Also write a helper script that will simplify this and fetching repo details, etc. from other users and document this by creating an AGENTS.md. Run and test it.

---

Update README.md documenting the prompt to use to update config.json.

---

BTW, we don't need reviewed AND unreviewed fields in config.json. Retain only reviewed. Also, modify generate_demos_csv to also create a open-demos.csv that has a subset where it has an MIT license AND reviewed is true.

---

In open-demos.csv, just use these fields in this order: repo, license, created, title, branded. Add a "brands" to config.json and llmdemos.csv (not open-demos.csv) that mentions the specific brands (exact string) present in the repo along with the GitHub URL. If there are many, list any three. Use an easy-to-read easy-to-parse text format for the field.

---

When saving open-demos.csv de-duplicate by repo so that when there are multiple rows for the same repo, the license is MIT if ANY of the rows as MIT, created is the earliest date, title is the date's title, and branded is TRUE if ANY of the rows are TRUE.

<!-- codex resume 019d1dbd-de04-7681-9bf5-0479af7fe9ac -->
