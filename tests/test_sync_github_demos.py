from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "sync_github_demos.py"
    spec = importlib.util.spec_from_file_location("sync_github_demos", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_normalize_repo_slug_accepts_urls_and_slugs():
    module = load_module()

    assert module.normalize_repo_slug("https://github.com/Sanand0/Tools/") == "sanand0/tools"
    assert module.normalize_repo_slug("Ritesh17rb/chart-map") == "ritesh17rb/chart-map"


def test_apply_brand_flags_sets_and_removes_branded_field():
    module = load_module()

    payload = {
        "demos": [
            {
                "title": "A",
                "repo": "https://github.com/Sanand0/tools/",
                "reviewed": False,
                "created": "2026-03-01",
            },
            {
                "title": "B",
                "repo": "https://github.com/example/demo/",
                "branded": True,
                "brands": "Straive | https://github.com/example/demo/search?q=Straive&type=code",
                "created": "2026-03-01",
            },
        ]
    }
    brand_results = {
        "sanand0/tools": module.BrandResult(
            branded=True,
            matched_terms=["Straive"],
            evidence=[{"query": "Straive", "path": "README.md"}],
            checked_at="2026-03-24T00:00:00+00:00",
        ),
        "example/demo": module.BrandResult(
            branded=False,
            matched_terms=[],
            evidence=[],
            checked_at="2026-03-24T00:00:00+00:00",
        ),
    }

    changed = module.apply_brand_flags(payload, brand_results)

    assert changed == 2
    assert payload["demos"][0]["branded"] is True
    assert payload["demos"][0]["brands"] == "Straive | https://github.com/sanand0/tools/search?q=Straive&type=code"
    assert "branded" not in payload["demos"][1]
    assert "brands" not in payload["demos"][1]


def test_repo_search_query_batches_repo_qualifiers():
    module = load_module()

    query = module.repo_search_query(["a/demo", "b/demo"], '"Learning Mate"')

    assert query == 'repo:a/demo repo:b/demo "Learning Mate"'


def test_format_brands_field_uses_exact_brand_text_and_urls():
    module = load_module()

    result = module.BrandResult(
        branded=True,
        matched_terms=["Learning Mate", "SG Analytics"],
        evidence=[
            {"query": '"Learning Mate"', "path": "README.md"},
            {"query": "SGAnalytics", "path": "index.html"},
        ],
        checked_at="2026-03-24T00:00:00+00:00",
    )

    assert module.format_brands_field("example/demo", result) == (
        "Learning Mate | https://github.com/example/demo/search?q=Learning+Mate&type=code"
        " ; SGAnalytics | https://github.com/example/demo/search?q=SGAnalytics&type=code"
    )
