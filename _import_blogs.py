#!/usr/bin/env python3
"""Import blog articles from Briefing/Seiten/Blogs into content/blog/."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import yaml

SITE = Path(__file__).parent
BRIEFING_DIR = SITE.parent / "Briefing" / "Seiten" / "Blogs"
CONTENT_DIR = SITE / "content" / "blog"
IMG_DIR = SITE / "img" / "blog"

CATEGORY_RULES: list[tuple[list[str], str]] = [
    (["startup", "gründer", "gruender", "founder", "auslandsgründung"], "Startup"),
    (["kmu", "mittelstand", "familienunternehmen", "nachfolge", "generations"], "KMU"),
    (["solo", "selbstständig", "selbststaendig"], "Solo"),
    (
        [
            "mitarbeiter",
            "führung",
            "fuehrung",
            "hr",
            "kultur",
            "team",
            "fehlerkultur",
            "emotionale",
            "vertrauen",
            "gesundheit",
        ],
        "HR & Kultur",
    ),
]


def parse_briefing(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title = text.split("\n", 1)[0].removeprefix("# ").strip()
    meta: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^- \*\*(.+?):\*\* (.+)$", line.strip())
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("`") and val.endswith("`"):
                val = val[1:-1]
            meta[key] = val

    body = text.split("## Inhalt", 1)[-1].strip() if "## Inhalt" in text else ""
    return {"title": title, "meta": meta, "body": body, "slug": path.stem}


def guess_category(title: str, slug: str, body: str) -> str:
    hay = f"{title} {slug} {body[:800]}".lower()
    for keywords, cat in CATEGORY_RULES:
        if any(k in hay for k in keywords):
            return cat
    return "Risikomanagement"


def german_excerpt(body: str, fallback: str) -> str:
    if fallback and not re.search(r"\b(the|and|why|what|how)\b", fallback.lower()[:60]):
        return fallback.strip().strip('"')
    for line in body.splitlines():
        line = line.strip().lstrip("*").strip()
        if line.startswith("**") and len(line) > 40:
            return re.sub(r"\*\*", "", line)
        if line.startswith("* ") and len(line) > 40:
            return line[2:].strip()
    for line in body.splitlines():
        line = line.strip()
        if len(line) > 60 and not line.startswith("#") and not line.startswith("!"):
            return line
    return fallback[:200] if fallback else ""


def download_image(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Beraterium-Import/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp.read())
        return True
    except Exception as exc:
        print(f"    ! image download failed: {exc}")
        return False


def hero_local_path(slug: str, url: str) -> tuple[str, str]:
    ext = Path(urlparse(url).path).suffix.lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".jpg"
    filename = f"{slug}-hero{ext}"
    local = IMG_DIR / filename
    rel = f"img/blog/{filename}"
    if not local.exists():
        print(f"    downloading {url}")
        download_image(url, local)
    return rel, str(local)


def extract_faq(body: str) -> tuple[str, list[dict[str, str]]]:
    lines = body.splitlines()
    faq_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.endswith("?") and 15 < len(stripped) < 200 and not stripped.startswith("#"):
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().endswith("?"):
                faq_start = i
                break
    if faq_start is None:
        return body, []

    content_lines = lines[:faq_start]
    faq_lines = lines[faq_start:]
    faq: list[dict[str, str]] = []
    i = 0
    while i < len(faq_lines):
        q = faq_lines[i].strip()
        if q.endswith("?"):
            answers: list[str] = []
            i += 1
            while i < len(faq_lines):
                a = faq_lines[i].strip()
                if a.endswith("?") and len(a) < 200:
                    break
                if a:
                    answers.append(a)
                i += 1
            if answers:
                faq.append({"question": q, "answer": " ".join(answers)})
        else:
            i += 1
    return "\n".join(content_lines).strip(), faq


def clean_body(body: str, title: str, hero_url: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    skip_until_content = True
    title_norm = title.strip().lower()

    for line in lines:
        stripped = line.strip()
        if skip_until_content:
            if stripped.startswith("## ") and stripped.lower().removeprefix("## ").strip() == title_norm:
                continue
            if stripped.startswith("## ") and "?" not in stripped[3:30]:
                skip_until_content = False
            elif re.match(r"^\*\s+\d+\\?\.\s", stripped):
                continue
            elif stripped.startswith("* ") and len(stripped) < 30:
                continue
            elif not stripped:
                continue
            else:
                skip_until_content = False

        if hero_url and hero_url in stripped and stripped.startswith("!["):
            continue
        if stripped.startswith("#### "):
            line = "## " + stripped[5:]
        elif stripped.startswith("##### "):
            line = "### " + stripped[6:]
        out.append(line)

    body = "\n".join(out)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def build_post(data: dict) -> tuple[dict, str]:
    meta = data["meta"]
    slug = meta.get("Slug", data["slug"])
    title = data["title"]
    body = data["body"]

    hero_url = meta.get("Beitragsbild", "")
    hero_alt = meta.get("Beitragsbild alt", title)
    hero_image = ""
    if hero_url.startswith("http"):
        hero_image, _ = hero_local_path(slug, hero_url)

    body = clean_body(body, title, hero_url)
    body, faq = extract_faq(body)

    excerpt = german_excerpt(body, meta.get("Excerpt", ""))
    category = guess_category(title, slug, body)

    front = {
        "title": title,
        "slug": slug,
        "date": meta.get("Datum", "2026-01-01"),
        "category": category,
        "author": "till-blania",
        "excerpt": excerpt[:300],
        "hero_image": hero_image,
        "hero_alt": hero_alt[:200],
        "draft": False,
        "faq": faq or None,
        "related_slugs": [],
    }
    front = {k: v for k, v in front.items() if v is not None}
    return front, body


def yaml_dump(data: dict) -> str:
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()


def main() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(BRIEFING_DIR.glob("*.md"))
    files = [f for f in files if f.name != "00_BLOGS_README.md"]
    print(f"Importing {len(files)} articles…")
    for path in files:
        data = parse_briefing(path)
        front, body = build_post(data)
        slug = front["slug"]
        out = CONTENT_DIR / f"{slug}.md"
        content = f"---\n{yaml_dump(front)}\n---\n\n{body}\n"
        out.write_text(content, encoding="utf-8")
        print(f"  ✓ {slug}.md")
    print("Done.")


if __name__ == "__main__":
    main()
