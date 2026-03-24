#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.28.1",
#   "python-dotenv>=1.1.1",
#   "typer>=0.16.1",
# ]
# ///

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import time
from typing import Any
from urllib.parse import quote_plus

import httpx
from dotenv import load_dotenv
import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)

BRAND_SEARCH_VERSION = 1
SEARCH_PER_PAGE = 100
DEFAULT_CACHE = Path(".cache/github-repo-helper.json")
DEFAULT_CONFIG = Path("config.json")
BRAND_QUERY_BATCH_SIZE = 10


@dataclass(frozen=True)
class BrandQuery:
    label: str
    query: str


@dataclass
class BrandResult:
    branded: bool
    matched_terms: list[str]
    evidence: list[dict[str, str]]
    checked_at: str


BRAND_QUERIES = [
    BrandQuery("Straive", "Straive"),
    BrandQuery("Gramener", "Gramener"),
    BrandQuery("Learning Mate", '"Learning Mate"'),
    BrandQuery("Learning Mate", "LearningMate"),
    BrandQuery("Double Line", '"Double Line"'),
    BrandQuery("Double Line", "DoubleLine"),
    BrandQuery("SG Analytics", '"SG Analytics"'),
    BrandQuery("SG Analytics", "SGAnalytics"),
]


def utc_now() -> str:
    return datetime.now(tz=UTC).isoformat(timespec="seconds")


def normalize_repo_slug(value: str) -> str:
    """Return a lower-cased owner/repo slug from a GitHub URL or slug."""
    text = value.strip()
    text = re.sub(r"^https?://github\.com/", "", text, flags=re.IGNORECASE)
    return text.strip("/").lower()


def repo_url(slug: str) -> str:
    return f"https://github.com/{normalize_repo_slug(slug)}/"


def exact_brand_text(query: str) -> str:
    query = query.strip()
    if len(query) >= 2 and query[0] == query[-1] == '"':
        return query[1:-1]
    return query


def format_brands_field(repo: str, brand_result: BrandResult | None) -> str | None:
    if not brand_result or not brand_result.branded:
        return None

    slug = normalize_repo_slug(repo)
    entries: list[str] = []
    seen: set[str] = set()
    for evidence in brand_result.evidence:
        brand = exact_brand_text(evidence["query"])
        if brand in seen:
            continue
        seen.add(brand)
        url = f"https://github.com/{slug}/search?q={quote_plus(brand)}&type=code"
        entries.append(f"{brand} | {url}")
        if len(entries) == 3:
            break
    return " ; ".join(entries) if entries else None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "version": BRAND_SEARCH_VERSION,
            "brand_results": {},
            "repo_details": {},
            "pages_first_build": {},
        }
    payload = load_json(path)
    if payload.get("version") != BRAND_SEARCH_VERSION:
        return {
            "version": BRAND_SEARCH_VERSION,
            "brand_results": {},
            "repo_details": {},
            "pages_first_build": {},
        }
    payload.setdefault("brand_results", {})
    payload.setdefault("repo_details", {})
    payload.setdefault("pages_first_build", {})
    return payload


def github_client(token: str) -> httpx.Client:
    return httpx.Client(
        base_url="https://api.github.com",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "llmdemos-sync",
        },
        follow_redirects=True,
        timeout=30.0,
    )


def github_request(client: httpx.Client, method: str, url: str, **kwargs: Any) -> httpx.Response:
    response = client.request(method, url, **kwargs)
    response.raise_for_status()
    return response


def rate_limit_sleep_seconds(response: httpx.Response) -> int | None:
    retry_after = response.headers.get("retry-after")
    if retry_after and retry_after.isdigit():
        return max(1, int(retry_after))

    remaining = response.headers.get("x-ratelimit-remaining")
    reset_at = response.headers.get("x-ratelimit-reset")
    if remaining == "0" and reset_at and reset_at.isdigit():
        return max(1, int(reset_at) - int(time.time()) + 1)

    message = response.text.lower()
    if response.status_code == 403 and "secondary rate limit" in message:
        return 60
    return None


def get_token(token_env: str) -> str:
    load_dotenv()
    token = os.getenv(token_env, "").strip()
    if not token:
        raise typer.BadParameter(f"Missing {token_env}. Set it in the environment or .env.")
    return token


def iter_config_repo_slugs(config_path: Path) -> list[str]:
    payload = load_json(config_path)
    demos = payload.get("demos", [])
    if not isinstance(demos, list):
        raise typer.BadParameter(f"{config_path} is missing a list at .demos")
    slugs = {
        normalize_repo_slug(repo)
        for repo in (demo.get("repo") for demo in demos if isinstance(demo, dict))
        if repo
    }
    return sorted(slugs)


def batched(items: list[str], size: int) -> list[list[str]]:
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


def repo_search_query(repos: list[str], search_term: str) -> str:
    qualifiers = " ".join(f"repo:{repo}" for repo in repos)
    return f"{qualifiers} {search_term}".strip()


def search_code_page(
    client: httpx.Client,
    repos: list[str],
    search_term: str,
    page: int,
) -> dict[str, Any]:
    params = {
        "q": repo_search_query(repos, search_term),
        "per_page": SEARCH_PER_PAGE,
        "page": page,
    }
    while True:
        response = client.get("/search/code", params=params)
        if response.is_success:
            return response.json()
        wait_seconds = rate_limit_sleep_seconds(response)
        if wait_seconds is None:
            response.raise_for_status()
        typer.echo(
            f"GitHub search rate limit hit. Waiting {wait_seconds}s before retrying...",
            err=True,
        )
        time.sleep(wait_seconds)


def detect_branded_repos(
    client: httpx.Client,
    repos: list[str],
    cache: dict[str, Any],
    *,
    cache_path: Path | None = None,
    refresh: bool = False,
) -> dict[str, BrandResult]:
    brand_cache = cache["brand_results"]
    results: dict[str, BrandResult] = {}
    unresolved = []

    for repo in repos:
        cached = None if refresh else brand_cache.get(repo)
        if cached:
            results[repo] = BrandResult(**cached)
            continue
        unresolved.append(repo)
        results[repo] = BrandResult(branded=False, matched_terms=[], evidence=[], checked_at="")

    for brand_query in BRAND_QUERIES:
        pending = [repo for repo in unresolved if not results[repo].branded]
        for batch in batched(pending, BRAND_QUERY_BATCH_SIZE):
            page = 1
            while True:
                payload = search_code_page(client, batch, brand_query.query, page)
                items = payload.get("items", [])
                for item in items:
                    repo_name = normalize_repo_slug(item["repository"]["full_name"])
                    result = results[repo_name]
                    if brand_query.label not in result.matched_terms:
                        result.matched_terms.append(brand_query.label)
                    result.branded = True
                    if len(result.evidence) < 3:
                        result.evidence.append(
                            {
                                "query": brand_query.query,
                                "path": item["path"],
                            }
                        )
                    result.checked_at = utc_now()
                    brand_cache[repo_name] = asdict(result)
                if len(items) < SEARCH_PER_PAGE:
                    break
                page += 1
            if cache_path:
                dump_json(cache_path, cache)

    checked_at = utc_now()
    for repo, result in results.items():
        result.checked_at = checked_at
        brand_cache[repo] = asdict(result)
    return results


def ordered_with_field(
    demo: dict[str, Any],
    *,
    key: str,
    value: Any | None,
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    existing = dict(demo)
    if key in existing:
        existing.pop(key)
    if value is None:
        return existing

    items: list[tuple[str, Any]] = []
    inserted = False
    for current_key, current_value in existing.items():
        if before and current_key == before and not inserted:
            items.append((key, value))
            inserted = True
        items.append((current_key, current_value))
        if after and current_key == after and not inserted:
            items.append((key, value))
            inserted = True
    if not inserted:
        items.append((key, value))
    return dict(items)


def apply_brand_flags(payload: dict[str, Any], brand_results: dict[str, BrandResult]) -> int:
    demos = payload.get("demos", [])
    if not isinstance(demos, list):
        raise typer.BadParameter("config.json is missing a list at .demos")

    changed = 0
    for idx, demo in enumerate(demos):
        if not isinstance(demo, dict):
            continue
        repo = demo.get("repo")
        if not repo:
            updated = ordered_with_field(demo, key="branded", value=None)
        else:
            slug = normalize_repo_slug(repo)
            brand_result = brand_results.get(slug)
            branded = bool(brand_result and brand_result.branded)
            brands = format_brands_field(slug, brand_result)
            updated = ordered_with_field(
                demo,
                key="branded",
                value=True if branded else None,
                after="reviewed" if "reviewed" in demo else None,
                before="created" if "created" in demo else None,
            )
            updated = ordered_with_field(
                updated,
                key="brands",
                value=brands,
                after="branded" if "branded" in updated else "repo",
            )
        if updated != demo:
            demos[idx] = updated
            changed += 1
    return changed


def latest_created_from_config(config_path: Path) -> str | None:
    payload = load_json(config_path)
    demos = payload.get("demos", [])
    dates = [demo.get("created") for demo in demos if isinstance(demo, dict) and demo.get("created")]
    return max(dates) if dates else None


def list_user_repos(client: httpx.Client, user: str) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        response = github_request(
            client,
            "GET",
            f"/users/{user}/repos",
            params={"per_page": 100, "page": page, "type": "public", "sort": "created", "direction": "desc"},
        )
        page_items = response.json()
        repos.extend(page_items)
        if len(page_items) < 100:
            return repos
        page += 1


def get_repo_details(client: httpx.Client, repo: str, cache: dict[str, Any], *, refresh: bool = False) -> dict[str, Any]:
    repo = normalize_repo_slug(repo)
    cached = None if refresh else cache["repo_details"].get(repo)
    if cached:
        return cached

    response = github_request(client, "GET", f"/repos/{repo}")
    payload = response.json()
    details = {
        "full_name": normalize_repo_slug(payload["full_name"]),
        "name": payload["name"],
        "description": payload.get("description") or "",
        "license": (payload.get("license") or {}).get("spdx_id") or "",
        "html_url": payload["html_url"],
        "homepage": payload.get("homepage") or "",
        "created_at": payload.get("created_at") or "",
        "default_branch": payload.get("default_branch") or "",
    }
    cache["repo_details"][repo] = details
    return details


def get_first_pages_build(
    client: httpx.Client,
    repo: str,
    cache: dict[str, Any],
    *,
    refresh: bool = False,
) -> str | None:
    repo = normalize_repo_slug(repo)
    cached = None if refresh else cache["pages_first_build"].get(repo)
    if cached is not None:
        return cached or None

    page = 1
    earliest: str | None = None
    while True:
        response = client.get(f"/repos/{repo}/pages/builds", params={"per_page": 100, "page": page})
        if response.status_code == 404:
            cache["pages_first_build"][repo] = ""
            return None
        response.raise_for_status()
        builds = response.json()
        if not builds:
            break
        earliest = builds[-1]["created_at"][:10]
        if len(builds) < 100:
            break
        page += 1
    cache["pages_first_build"][repo] = earliest or ""
    return earliest


@app.command("brand-config")
def brand_config(
    config: Path = typer.Option(DEFAULT_CONFIG, exists=True, dir_okay=False),
    cache_path: Path = typer.Option(DEFAULT_CACHE, "--cache"),
    token_env: str = typer.Option("GITHUB_TOKEN", "--token-env"),
    refresh: bool = typer.Option(False, help="Ignore cached branding results."),
    write: bool = typer.Option(True, "--write/--dry-run", help="Write config.json in place."),
) -> None:
    """Mark demos with branded=true when repo contents match the configured brand terms."""
    repos = iter_config_repo_slugs(config)
    cache = load_cache(cache_path)
    token = get_token(token_env)

    with github_client(token) as client:
        brand_results = detect_branded_repos(
            client,
            repos,
            cache,
            cache_path=cache_path,
            refresh=refresh,
        )

    payload = load_json(config)
    changed = apply_brand_flags(payload, brand_results)
    branded_repos = sorted(repo for repo, result in brand_results.items() if result.branded)

    if write:
        dump_json(config, payload)
    dump_json(cache_path, cache)

    typer.echo(f"Checked {len(repos)} unique repos")
    typer.echo(f"Branded repos: {len(branded_repos)}")
    typer.echo(f"Config entries changed: {changed}")
    for repo in branded_repos:
        matched_terms = ", ".join(brand_results[repo].matched_terms)
        typer.echo(f"{repo}\t{matched_terms}")


@app.command("repo-info")
def repo_info(
    repos: list[str] = typer.Argument(..., help="owner/repo slugs or GitHub repo URLs"),
    cache_path: Path = typer.Option(DEFAULT_CACHE, "--cache"),
    token_env: str = typer.Option("GITHUB_TOKEN", "--token-env"),
    refresh: bool = typer.Option(False, help="Ignore cached repo details."),
) -> None:
    """Fetch and print normalized repo metadata for specific repos."""
    cache = load_cache(cache_path)
    token = get_token(token_env)

    with github_client(token) as client:
        for repo in repos:
            details = get_repo_details(client, repo, cache, refresh=refresh)
            first_build = get_first_pages_build(client, repo, cache, refresh=refresh)
            record = {
                **details,
                "pages_first_build": first_build,
            }
            typer.echo(json.dumps(record, ensure_ascii=False))

    dump_json(cache_path, cache)


@app.command("discover-pages")
def discover_pages(
    users: list[str] = typer.Argument(..., help="GitHub usernames to scan"),
    config: Path = typer.Option(DEFAULT_CONFIG, exists=True, dir_okay=False),
    cutoff: str | None = typer.Option(None, help="YYYY-MM-DD cutoff. Defaults to latest created in config."),
    cache_path: Path = typer.Option(DEFAULT_CACHE, "--cache"),
    token_env: str = typer.Option("GITHUB_TOKEN", "--token-env"),
    refresh: bool = typer.Option(False, help="Ignore cached repo details and Pages dates."),
    include_existing: bool = typer.Option(False, help="Include repos already present in config."),
) -> None:
    """List public repos with GitHub Pages whose first build date is on or after the cutoff."""
    config_repos = set(iter_config_repo_slugs(config))
    effective_cutoff = cutoff or latest_created_from_config(config)
    if not effective_cutoff:
        raise typer.BadParameter("Unable to determine cutoff date.")

    cache = load_cache(cache_path)
    token = get_token(token_env)
    rows: list[dict[str, str]] = []

    with github_client(token) as client:
        seen: set[str] = set()
        for user in users:
            for repo in list_user_repos(client, user):
                slug = normalize_repo_slug(repo["full_name"])
                if slug in seen:
                    continue
                seen.add(slug)

                details = get_repo_details(client, slug, cache, refresh=refresh)
                first_build = get_first_pages_build(client, slug, cache, refresh=refresh)
                if not first_build or first_build < effective_cutoff:
                    continue
                if not include_existing and slug in config_repos:
                    continue
                rows.append(
                    {
                        "repo": slug,
                        "created": first_build,
                        "homepage": details["homepage"],
                        "license": details["license"],
                        "description": details["description"],
                    }
                )

    dump_json(cache_path, cache)
    for row in sorted(rows, key=lambda item: (item["created"], item["repo"]), reverse=True):
        typer.echo(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    app()
