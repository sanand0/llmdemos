# Prompts

## Add new demos, 09 Oct 2026

<!--
cd ~/code/llmdemos/
dev.sh -- codex --yolo --model gpt-6.1-sol --config model_reasoning_effort=medium
-->

Add these demos (dated based on their last modified date):
https://files.s-anand.net/pages/mckinsey-gep-validation/
https://files.s-anand.net/pages/ed-content-pipeline/
https://sanand0.github.io/llmevals/confidence-calibration/
https://sanand0.github.io/llmevals/jev/

<!-- codex resume 01a120e8-b497-7031-b2df-f4d523c93deb --yolo -->

## Add new demos, 08 Oct 2026

<!--
cd ~/code/llmdemos/
dev.sh -- codex --yolo --model gpt-6.1-sol --config model_reasoning_effort=medium
-->

Add or update content from these demos:
- https://eshwarpotturi.github.io/rate-call-tracker/
- https://eshwarpotturi.github.io/ai-whispers/ - A chinese whisper story (think of a business application while describing it)
- https://jivraj-18.github.io/dream-room-blender/dream_rooms/viewer/ - agents can render 3D quite well now
- https://hrmiitm.github.io/llm-counting-benchmark/reasoning.html - Replace the existing llm-counting-benchmark demo with this link - and rewrite, factoring in reasoning levels and deep learning models: the highlight is the cost vs quality curve.

<!-- codex resume 01a11a45-2478-7662-a9ee-51a027a206d5 --yolo -->

## Add new demos, 05 Oct 2026

<!--
cd ~/code/llmdemos/
dev.sh -- codex --yolo --model gpt-6.1-sol --config model_reasoning_effort=medium
-->

Add or update content from these demos:
- ADD: https://eshwarpotturi.github.io/after-delve/
- ADD: https://jivraj-18.github.io/benchmark-finance-pageindex/
- UPDATE: https://hrmiitm.github.io/llm-counting-benchmark/
- UPDATE: https://atharva-729.github.io/bookshelf-benchmark/

<!-- codex resume 01a10ac3-13e1-75d2-98be-f22355446ea5 --yolo -->

## Add new demos, 01 Oct 2026

<!--
cd ~/code/llmdemos/
dev.sh -- codex --yolo --model gpt-6.1-sol --config model_reasoning_effort=medium
-->

Add these demos:
https://eshwarpotturi.github.io/language-drift/
https://atharva-729.github.io/bookshelf-benchmark/
https://hrmiitm.github.io/llm-counting-benchmark/

<!-- codex resume 01a0f7d7-89a8-7c01-afe1-86b32c82f599 --yolo -->

## Add new demos, 30 Sep 2026

<!--
cd ~/code/llmdemos/
dev.sh -- codex --yolo --model gpt-6-luna --config model_reasoning_effort=medium
-->

Add the following demos:
https://eshwarpotturi.github.io/soc-analyst-jev/
https://hrmiitm.github.io/llm-counting-benchmark/

<!-- codex resume 01a0f1a1-92fd-7360-a772-45170a06b405 --yolo -->

## 05 May 2026

Scan the public GitHub repositories of:

mynkpdr
pavankumart18
prudhvi1709
ritesh17rb
pythonicvarun

... and add any new GOOD repos having GitHub Pages created on/after the latest "created" in config.json.

Add a "reviewed": false field to them to indicate that human review is needed.
Use the public access GITHUB_TOKEN in .env if you need.

---

Create an AGENTS.md that includes documentation on how to add new demos.

<!-- codex resume 019df6c0-d0e8-7351-bc0f-2de54ad6cf46 -->

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
