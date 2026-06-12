#!/usr/bin/env python3
"""Patch team/index.html profile bios from content/team/*.yaml (stdlib only)."""
from __future__ import annotations

import re
from html import escape
from pathlib import Path

SITE = Path(__file__).parent
TEAM_HTML = SITE / "team" / "index.html"
TEAM_DIR = SITE / "content" / "team"


def parse_simple_yaml(path: Path) -> dict:
    data: dict = {}
    extended: list[dict[str, str]] = []
    current_block: dict[str, str] | None = None
    key: str | None = None
    buf: list[str] = []

    def flush_scalar() -> None:
        nonlocal key, buf
        if key is None:
            return
        val = "\n".join(buf).strip()
        if key == "extended":
            return
        data[key] = val.strip('"')
        key = None
        buf = []

    def flush_block() -> None:
        nonlocal current_block, buf
        if current_block is None:
            return
        if buf:
            current_block["text"] = "\n".join(buf).strip().strip('"')
        extended.append(current_block)
        current_block = None
        buf = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            flush_scalar()
            flush_block()
            item = line[4:].strip()
            if item == "text:":
                current_block = {}
                buf = []
            elif item.startswith("label:"):
                current_block = {"label": item.split(":", 1)[1].strip().strip('"')}
                buf = []
            elif item.startswith("text:"):
                if current_block is None:
                    current_block = {}
                buf = [item.split(":", 1)[1].strip().strip('"')]
            continue
        if line.startswith("    "):
            if current_block is not None:
                buf.append(line.strip().strip('"'))
            elif key is not None:
                buf.append(line.strip().strip('"'))
            continue
        if ":" in line:
            flush_scalar()
            flush_block()
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k == "extended":
                data["extended"] = extended
                key = k
                buf = []
            elif v:
                data[k] = v.strip('"')
            else:
                key = k
                buf = []
    flush_scalar()
    flush_block()
    if extended:
        data["extended"] = extended
    return data


def section_id(slug: str) -> str:
    return slug.replace("-", "")


def extended_html(blocks: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for block in blocks:
        text = (block.get("text") or "").strip()
        if not text:
            continue
        label = (block.get("label") or "").strip()
        if label:
            parts.append(
                f'            <p class="brt-body"><strong>{escape(label)}:</strong> {escape(text)}</p>'
            )
        else:
            parts.append(f'            <p class="brt-body">{escape(text)}</p>')
    return "\n".join(parts)


def bio_html(member: dict) -> str:
    sid = section_id(member["slug"])
    approach = escape(member.get("approach", ""))
    goal = escape(member.get("goal", ""))
    blocks = member.get("extended") or []
    more = extended_html(blocks)
    toggle = ""
    if more:
        toggle = f"""
          <div class="brt-team-bio__more" id="{sid}-more" hidden>
{more}
          </div>
          <button type="button" class="brt-team-bio__toggle brt-btn brt-btn--ghost" aria-expanded="false" aria-controls="{sid}-more" data-more-label="Mehr anzeigen" data-less-label="Weniger anzeigen">Mehr anzeigen</button>"""
    return f"""          <div class="brt-team-bio">
            <div class="brt-team-bio__preview">
              <p class="brt-body"><strong>Mein Ansatz:</strong> {approach}</p>
              <p class="brt-body"><strong>Mein Ziel:</strong> {goal}</p>
            </div>{toggle}
          </div>"""


def main() -> None:
    html = TEAM_HTML.read_text(encoding="utf-8")
    for path in sorted(TEAM_DIR.glob("*.yaml")):
        member = parse_simple_yaml(path)
        member["slug"] = member.get("slug", path.stem)
        sid = section_id(member["slug"])
        new_bio = bio_html(member)
        pattern = (
            rf'(<section class="brt-section[^"]*" id="{sid}"[\s\S]*?<ul class="brt-team-contact">[\s\S]*?</ul>\n)'
            rf'          <p class="brt-body"><strong>Mein Ansatz:</strong>[\s\S]*?'
            rf'(<\s*/div>\s*</div>\s*</section>)'
        )
        repl = rf"\1{new_bio}\n        \2"
        updated, n = re.subn(pattern, repl, html, count=1)
        if n != 1:
            raise SystemExit(f"Could not patch section {sid} ({n} matches)")
        html = updated
    TEAM_HTML.write_text(html, encoding="utf-8")
    print("patched", TEAM_HTML)


if __name__ == "__main__":
    main()
