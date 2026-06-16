"""Content loading and rendering for Beraterium CMS build."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from html import escape
from pathlib import Path
from typing import Any

import markdown
import yaml

SITE = Path(__file__).parent
CONTENT = SITE / "content"
BLOG_DIR = CONTENT / "blog"
TEAM_DIR = CONTENT / "team"
IMG_DIR = SITE / "img"

BLOG_CATEGORIES = [
    "Risk management",
    "HR & culture",
    "Startup",
    "SME",
    "Solo",
]

CATEGORY_ANGEBOTE: dict[str, list[tuple[str, str]]] = {
    "Startup": [("startups", "Risk check for startups")],
    "SME": [("smb", "Clarity roadmap for SMEs")],
    "Solo": [("solo", "Risk compass for solo")],
    "HR & culture": [("smb", "Clarity roadmap for SMEs")],
    "Risk management": [
        ("startups", "Risk check for startups"),
        ("smb", "Clarity roadmap for SMEs"),
        ("solo", "Risk compass for solo"),
    ],
}

DEFAULT_ANGEBOTE = [
    ("startups", "Risk check for startups"),
    ("smb", "Clarity roadmap for SMEs"),
    ("solo", "Risk compass for solo"),
]

CATEGORY_SLUGS = {
    "Risk management": "risk-management",
    "HR & culture": "hr-culture",
    "Startup": "startup",
    "SME": "smb",
    "Solo": "solo",
}

SITE_URL = "https://en.beraterium.de"

HOME_TEAM_FEATURED_SLUGS = (
    "till-blania",
    "peter-muenstermann",
    "aleksandra-polosukhina",
)

HOME_TEAM_CARD_COPY: dict[str, tuple[str, str]] = {
    "till-blania": (
        "Managing director · HR management approach",
        "Connects business, HR and risk management with experience from his own start-ups. "
        "Brings leaders and employees together so solutions emerge that actually work.",
    ),
    "peter-muenstermann": (
        "Risk management approach · 20 years in corporate",
        "Facilitates open conversations about risks, opportunities and solutions – structured yet human. "
        "Makes risk management tangible, understandable and actionable.",
    ),
    "aleksandra-polosukhina": (
        "Head of marketing and PR",
        "Marketing and PR specialist with over seven years' experience – strengthens teams through smart "
        "communication and targeted employer branding.",
    ),
    "torsten-walter-helbig": (
        "Local representative · Chemnitz",
        "Independent financial adviser for over 31 years – develops robust cashflow architectures "
        "for lasting security and financial freedom.",
    ),
    "joachim-lau": (
        "Textile industry expert · 20 years in the sector",
        "Brings management and staff together to implement improvements that work in day-to-day operations – "
        "from fashion to IT modernisation.",
    ),
}


@dataclass
class TeamMember:
    slug: str
    name: str
    role_tag: str = ""
    order: int = 0
    profile_type: str = "full"
    layout: str = "normal"
    image: str = ""
    image_alt: str = ""
    approach: str = ""
    goal: str = ""
    extended: list[dict[str, str]] = field(default_factory=list)
    teaser_bio: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    active: bool = True
    show_on_home: bool = False
    show_on_ueber_uns: bool = False


@dataclass
class BlogPost:
    title: str
    slug: str
    date: date
    category: str
    author: str
    excerpt: str
    hero_image: str = ""
    hero_alt: str = ""
    draft: bool = True
    reading_time_min: int = 0
    faq: list[dict[str, str]] = field(default_factory=list)
    related_slugs: list[str] = field(default_factory=list)
    body_html: str = ""
    toc: list[dict[str, str]] = field(default_factory=list)
    lead: str = ""
    youtube_id: str = ""
    source_path: Path | None = None


def pfx(depth: int) -> str:
    return "../" * depth if depth else ""


def header_logo_html(home: str, pre: str) -> str:
    return f"""    <a class="site-header__logo" href="{home}" aria-label="Beraterium homepage">
      <img class="site-header__logo-img site-header__logo-img--light" src="{pre}img/logo-en/logo-white.png" alt="Beraterium" width="4444" height="1238" decoding="async">
      <img class="site-header__logo-img site-header__logo-img--dark" src="{pre}img/logo-en/logo-black.png" alt="" aria-hidden="true" width="4444" height="1238" decoding="async">
    </a>"""


def _parse_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def load_team_members() -> list[TeamMember]:
    members: list[TeamMember] = []
    if not TEAM_DIR.exists():
        return members
    for path in sorted(TEAM_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        members.append(
            TeamMember(
                slug=data.get("slug", path.stem),
                name=data.get("name", path.stem),
                role_tag=data.get("role_tag", ""),
                order=int(data.get("order", 99)),
                profile_type=data.get("profile_type", "full"),
                layout=data.get("layout", "normal"),
                image=data.get("image", ""),
                image_alt=data.get("image_alt", data.get("name", "")),
                approach=data.get("approach", ""),
                goal=data.get("goal", ""),
                extended=list(data.get("extended") or []),
                teaser_bio=data.get("teaser_bio", ""),
                email=data.get("email", ""),
                phone=data.get("phone", ""),
                linkedin=data.get("linkedin", ""),
                active=bool(data.get("active", True)),
                show_on_home=bool(data.get("show_on_home", False)),
                show_on_ueber_uns=bool(data.get("show_on_ueber_uns", False)),
            )
        )
    return sorted(members, key=lambda m: m.order)


def team_by_slug(members: list[TeamMember]) -> dict[str, TeamMember]:
    return {m.slug: m for m in members}


def team_section_id(slug: str) -> str:
    return slug.replace("-", "")


def team_anchor_id(slug: str) -> str:
    return team_section_id(slug) + "-title"


def team_member_url(pre: str, slug: str) -> str:
    return f"{pre}team/#{team_section_id(slug)}"


def author_name_link_html(
    author_slug: str,
    author_name: str,
    pre: str,
    *,
    css_class: str = "brt-article__author-link",
) -> str:
    name = escape(author_name)
    if not author_slug:
        return name
    href = team_member_url(pre, author_slug)
    return f'<a class="{css_class}" href="{escape(href)}">{name}</a>'


def _reading_time(text: str, minutes: int) -> int:
    if minutes > 0:
        return minutes
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 200))


def _clean_excerpt(text: str) -> str:
    cleaned = re.sub(r"^[\*\-•]\s+", "", (text or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _render_markdown(body: str) -> str:
    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "nl2br"],
        extension_configs={"toc": {"permalink": False}},
    )
    html = md.convert(body)
    html = re.sub(r"<h2", '<h2 class="brt-article__h2"', html)
    html = re.sub(r"<h3", '<h3 class="brt-article__h3"', html)
    html = re.sub(r"<p>", '<p class="brt-body">', html)
    html = re.sub(r"<blockquote>", '<blockquote class="brt-article__quote">', html)
    html = re.sub(r"<ul>", '<ul class="brt-article__list">', html)
    html = re.sub(r"<ol>", '<ol class="brt-article__list brt-article__list--ordered">', html)
    return html


def _unwrap_list_paragraphs(html: str) -> str:
    return re.sub(
        r"<li>\s*<p class=\"brt-body\">(.*?)</p>\s*</li>",
        r"<li>\1</li>",
        html,
        flags=re.DOTALL,
    )


_KEYPOINT_LINK_SKIP = re.compile(r"^(Sources|References|Conclusion|Summary)\b", re.IGNORECASE)
_KEYPOINT_STOP_WORDS = frozenset(
    {
        "about", "after", "also", "and", "are", "because", "been", "before", "being",
        "both", "but", "can", "could", "does", "each", "for", "from", "have", "has",
        "here", "how", "into", "its", "just", "more", "most", "not", "only", "other",
        "our", "out", "over", "should", "some", "such", "than", "that", "the", "their",
        "them", "then", "there", "these", "they", "this", "through", "under", "very",
        "was", "were", "what", "when", "where", "which", "while", "who", "will", "with",
        "would", "your",
    }
)


def _keypoint_match_words(text: str) -> set[str]:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    cleaned = cleaned.lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return {word for word in cleaned.split() if len(word) > 3 and word not in _KEYPOINT_STOP_WORDS}


def _keypoint_heading_score(keypoint_html: str, title: str) -> int:
    kp_words = _keypoint_match_words(keypoint_html)
    title_words = _keypoint_match_words(title)
    strong_words = set()
    for strong in re.findall(r"<strong>(.*?)</strong>", keypoint_html, flags=re.DOTALL):
        strong_words |= _keypoint_match_words(strong)

    title_norm = title.lower()

    score = len(kp_words & title_words) + (2 * len(strong_words & title_words))
    for word in kp_words | strong_words:
        for title_word in title_words:
            if word == title_word:
                score += 4 if word in strong_words else 2
            elif len(word) >= 6 and (word in title_word or title_word in word):
                score += 3 if word in strong_words else 1

    if ("family" in strong_words or "families" in strong_words) and "business" in title_norm:
        score += 4
    if ("organization" in strong_words or "organisation" in strong_words) and "business" in title_norm:
        score += 4
    if ("staff" in strong_words or "employee" in strong_words or "employees" in strong_words) and (
        "staff" in title_norm or "employee" in title_norm
    ):
        score += 5
    if "worst" in strong_words and "cases" in strong_words and "worst" in title_norm:
        score += 5
    if ("practical" in strong_words or "practice" in strong_words) and "practical" in title_norm:
        score += 5
    if "psychological" in title_norm and ("ownership" in kp_words or "emotional" in kp_words):
        score += 4
    if "radical" in strong_words and "radical" in title_norm:
        score += 5
    if ("risks" in strong_words or "risk" in strong_words) and "risk" in title_norm:
        score += 3
    if "growth" in strong_words and "paradox" in title_norm:
        score += 4
    if "framework" in strong_words and "framework" in title_norm:
        score += 5
    if ("people" in strong_words or "human" in strong_words) and (
        "people" in title_norm or "human" in title_norm
    ):
        score += 4
    if ("tool" in strong_words or "instrument" in strong_words) and (
        "instrument" in title_norm or "tool" in title_norm
    ):
        score += 4
    if "threat" in strong_words and "threat" in title_norm:
        score += 5
    if "paradox" in strong_words and "paradox" in title_norm:
        score += 5
    if "overregulation" in strong_words and "paradox" in title_norm:
        score += 4
    if any(word.startswith("conflict") for word in strong_words) and "conflict" in title_norm:
        score += 6
    if "succession" in strong_words and "succession" in title_norm and "conflict" not in strong_words:
        score += 4

    return score


def _link_keypoints_items(keypoints_html: str, body_html: str) -> str:
    headings = [
        item
        for item in _extract_toc(body_html)
        if not _KEYPOINT_LINK_SKIP.search(item["title"])
    ]
    if not headings:
        return keypoints_html

    def replacer(match: re.Match[str]) -> str:
        inner = match.group(1)
        if inner.strip().startswith('<a class="brt-article__keypoints-link"'):
            return match.group(0)

        best_id = None
        best_score = -1
        best_index = len(headings)
        for index, heading in enumerate(headings):
            score = _keypoint_heading_score(inner, heading["title"])
            if score > best_score or (score == best_score and index < best_index):
                best_score = score
                best_id = heading["id"]
                best_index = index

        if best_score < 1 or not best_id:
            return match.group(0)

        return (
            f'<li><a class="brt-article__keypoints-link" href="#{best_id}">'
            f"{inner}</a></li>"
        )

    return re.sub(r"<li>(.*?)</li>", replacer, keypoints_html, flags=re.DOTALL)


def _promote_keypoints(html: str) -> str:
    if re.search(r"<h2 class=\"brt-article__h2\"", html):
        before, _, after = html.partition('<h2 class="brt-article__h2"')
    else:
        before, after = html, ""
    match = re.match(
        r"\s*(<ul class=\"brt-article__list\">.*?</ul>)\s*",
        before,
        flags=re.DOTALL,
    )
    if not match or len(re.findall(r"<li>", match.group(1))) < 2:
        return html
    keypoints = match.group(1).replace(
        '<ul class="brt-article__list">',
        '<ul class="brt-article__list brt-article__keypoints-list">',
        1,
    )
    rest = before[match.end():] + ('<h2 class="brt-article__h2"' + after if after else "")
    keypoints = _link_keypoints_items(keypoints, rest)
    return (
        '<aside class="brt-article__keypoints" aria-label="Key takeaways">'
        '<div class="brt-article__keypoints-head">'
        '<div class="brt-article__keypoints-head-copy">'
        '<p class="brt-article__keypoints-label">Key takeaways</p>'
        '<p class="brt-article__keypoints-deck">The essentials at a glance</p>'
        "</div></div>"
        f"{keypoints}"
        "</aside>"
        + rest
    )


def _youtube_id_from_url(url: str) -> str:
    if not url:
        return ""
    for pattern in (
        r"youtu\.be/([\w-]{11})",
        r"youtube\.com/watch\?v=([\w-]{11})",
        r"youtube\.com/embed/([\w-]{11})",
        r"youtube\.com/shorts/([\w-]{11})",
    ):
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def _extract_podcast_youtube(html: str) -> tuple[str, str]:
    pattern = (
        r'<h3 class="brt-article__h3"[^>]*>.*?(?:Podcast|🎧).*?</h3>\s*'
        r'<p class="brt-body"><a href="(https?://[^"]+)">([^<]*)</a></p>'
    )
    match = re.search(pattern, html, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return html, ""
    video_id = _youtube_id_from_url(match.group(1))
    cleaned = re.sub(pattern, "", html, count=1, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip(), video_id


def _extract_toc(html: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for match in re.finditer(
        r'<h2 class="brt-article__h2" id="([^"]+)">([^<]+)</h2>',
        html,
    ):
        title = re.sub(r"\s+", " ", match.group(2)).strip()
        if title:
            items.append({"id": match.group(1), "title": title})
    return items


def _truncate_faq_answer(text: str, limit: int = 320) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rsplit(" ", 1)[0] + "…"


def _faq_from_body_html(html: str, *, limit: int = 6) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for match in re.finditer(
        r'<h2 class="brt-article__h2" id="[^"]+">([^<]+)</h2>\s*'
        r'(?:<p class="brt-body">(.*?)</p>)?',
        html,
        flags=re.DOTALL,
    ):
        question = re.sub(r"\s+", " ", match.group(1)).strip()
        answer = _truncate_faq_answer(re.sub(r"<[^>]+>", "", match.group(2) or ""))
        if not question or not answer:
            continue
        if not question.endswith("?"):
            question = question.rstrip(".") + "?"
        items.append({"question": question, "answer": answer})
        if len(items) >= limit:
            break
    return items


def _faq_from_keypoints(html: str, *, limit: int = 5) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for match in re.finditer(r"<li>(.*?)</li>", html, flags=re.DOTALL):
        text = _truncate_faq_answer(re.sub(r"<[^>]+>", "", match.group(1)), 280)
        if len(text) < 40:
            continue
        question = text.split(".", 1)[0].strip()
        if len(question) < 20:
            question = text[:80].rsplit(" ", 1)[0]
        if not question.endswith("?"):
            question = question.rstrip(".") + "?"
        items.append({"question": question, "answer": text})
        if len(items) >= limit:
            break
    return items


def resolve_article_faq(
    faq: list[dict[str, str]],
    body_html: str,
    excerpt: str,
) -> list[dict[str, str]]:
    if faq:
        return faq
    generated = _faq_from_body_html(body_html)
    if len(generated) < 3:
        keypoint_block = re.search(
            r'<aside class="brt-article__keypoints".*?</aside>',
            body_html,
            flags=re.DOTALL,
        )
        if keypoint_block:
            generated.extend(_faq_from_keypoints(keypoint_block.group(0), limit=6 - len(generated)))
    if generated:
        return generated[:6]
    if excerpt:
        return [
            {
                "question": "What is this article about?",
                "answer": _truncate_faq_answer(excerpt, 400),
            }
        ]
    return []


def _postprocess_article_html(html: str, excerpt: str) -> tuple[str, list[dict[str, str]], str, str]:
    html = _unwrap_list_paragraphs(html)
    html = _promote_keypoints(html)
    html, youtube_id = _extract_podcast_youtube(html)
    toc = _extract_toc(html)
    lead = _clean_excerpt(excerpt)
    if lead:
        first_li = re.search(r'<aside class="brt-article__keypoints".*?<li>(.*?)</li>', html, re.DOTALL)
        if first_li:
            first_text = re.sub(r"<[^>]+>", "", first_li.group(1))
            first_text = re.sub(r"\s+", " ", first_text).strip()
            if first_text[:80] == lead[:80]:
                lead = ""
    return html, toc, lead, youtube_id


def article_toc_html(toc: list[dict[str, str]], depth: int) -> str:
    if not toc:
        return ""
    count = len(toc)
    items = "\n".join(
        f'            <li><a href="#{escape(item["id"])}">{escape(item["title"])}</a></li>'
        for item in toc
    )
    return f"""
        <nav class="brt-article__toc" aria-label="Table of contents" data-article-toc>
          <details class="brt-article__toc-details" open>
            <summary class="brt-article__toc-label">
              <span class="brt-article__toc-label-text">Contents</span>
              <span class="brt-article__toc-label-actions">
                <span class="brt-article__toc-count">{count} sections</span>
                <span class="brt-article__toc-toggle" aria-hidden="true"></span>
              </span>
            </summary>
            <ol class="brt-article__toc-list">
{items}
            </ol>
          </details>
        </nav>"""


def article_youtube_embed_html(youtube_id: str, title: str, page_url: str = "") -> str:
    if not youtube_id:
        return ""
    safe_title = escape(f"Risk Radar Podcast: {title}")
    watch_url = f"https://www.youtube.com/watch?v={youtube_id}"
    page_attr = f'\n          data-youtube-page="{escape(page_url)}"' if page_url else ""
    vid = escape(youtube_id)
    thumb = f"https://i.ytimg.com/vi/{vid}"
    return f"""
    <section class="brt-article__video" aria-labelledby="article-podcast-video">
      <div class="brt-container">
        <div class="brt-article__video-head">
          <p class="brt-article__video-label" id="article-podcast-video">Risk Radar Podcast</p>
          <p class="brt-article__video-deck">🎧 Watch the full podcast episode here:</p>
        </div>
        <div
          class="brt-article__video-wrap"
          data-youtube-embed
          data-youtube-id="{vid}"{page_attr}
          data-youtube-title="{safe_title}"
        >
          <button type="button" class="brt-article__video-poster" aria-label="Play podcast: {safe_title}">
            <img
              src="{thumb}/maxresdefault.jpg"
              srcset="{thumb}/maxresdefault.jpg 1280w, {thumb}/sddefault.jpg 640w"
              sizes="(min-width: 1024px) min(1200px, 100vw), 100vw"
              alt=""
              width="1280"
              height="720"
              loading="lazy"
              decoding="async"
              data-youtube-thumb-base="{thumb}/"
              onerror="if(this.src.includes('maxresdefault')){{this.src='{thumb}/sddefault.jpg';}}else if(this.src.includes('sddefault')){{this.src='{thumb}/hqdefault.jpg';}}"
            >
            <span class="brt-article__video-play" aria-hidden="true"></span>
          </button>
          <a
            class="brt-article__video-yt-badge"
            href="{watch_url}"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Watch on YouTube"
          >
            <span class="brt-article__video-yt-prefix">Watch on</span>
            <span class="brt-article__video-yt-brand" aria-hidden="true">
              <svg class="brt-article__video-yt-icon" width="20" height="14" viewBox="0 0 20 14" focusable="false">
                <path fill="#f03" d="M19.6 2.2A2.5 2.5 0 0 0 17.6.4C16.1 0 10 0 10 0S3.9 0 2.4.4A2.5 2.5 0 0 0 .4 2.2C0 3.7 0 7 0 7s0 3.3.4 4.8A2.5 2.5 0 0 0 2.4 13.6C3.9 14 10 14 10 14s6.1 0 7.6-.4a2.5 2.5 0 0 0 2-2.2C20 10.3 20 7 20 7s0-3.3-.4-4.8z"/>
                <path fill="#fff" d="M8 4.5v5l5-2.5z"/>
              </svg>
              <span class="brt-article__video-yt-name">YouTube</span>
            </span>
          </a>
        </div>
      </div>
    </section>"""


def faq_items_html(items: list[dict[str, str] | tuple[str, str]]) -> str:
    blocks: list[str] = []
    for item in items:
        if isinstance(item, tuple):
            question, answer = item
        else:
            question = item.get("question", "")
            answer = item.get("answer", "")
        blocks.append(
            f"""          <details class="brt-faq__item">
            <summary class="brt-faq__summary">
              <span class="brt-faq__toggle" aria-hidden="true"></span>
              <span class="brt-faq__question">{escape(question)}</span>
              <span class="brt-faq__chevron" aria-hidden="true"></span>
            </summary>
            <div class="brt-faq__answer">
              <p class="brt-body">{escape(answer)}</p>
            </div>
          </details>"""
        )
    return "\n".join(blocks)


def faq_section_html(
    items: list[dict[str, str] | tuple[str, str]],
    *,
    title: str = "Frequently asked questions",
    section_id: str = "",
    heading_id: str = "faq-title",
    alt: bool = False,
    container_class: str = "",
    use_section_header: bool = True,
) -> str:
    if not items:
        return ""
    alt_cls = " brt-section--alt" if alt else ""
    id_attr = f' id="{escape(section_id)}"' if section_id else ""
    container_cls = f"brt-container {container_class}".strip() if container_class else "brt-container"
    if use_section_header:
        heading = f"""        <header class="brt-section__header brt-fade-up">
          <h2 id="{escape(heading_id)}" class="brt-h2">{escape(title)}</h2>
        </header>"""
    else:
        heading = f'        <h2 id="{escape(heading_id)}" class="brt-h2">{escape(title)}</h2>'
    return f"""
    <section{id_attr} class="brt-section{alt_cls}" aria-labelledby="{escape(heading_id)}">
      <div class="{container_cls}">
{heading}
        <div class="brt-faq brt-fade-up">
{faq_items_html(items)}
        </div>
      </div>
    </section>"""


def article_faq_section_html(faq: list[dict[str, str]]) -> str:
    if not faq:
        return ""
    return faq_section_html(
        faq,
        title="Frequently asked questions",
        heading_id="article-faq",
        alt=True,
        container_class="brt-article__faq",
        use_section_header=False,
    )


def article_author_sidebar_html(
    author: TeamMember | None,
    author_name: str,
    author_slug: str,
    depth: int,
    pre: str,
) -> str:
    pre = pre or pfx(depth)
    img_block = ""
    if author and author.image:
        img = img_html(author.image, author.image_alt, depth, css_class="brt-article__author-col-img", aspect="1/1")
        if "brt-image-placeholder" not in img:
            img_block = img
    role = ""
    if author:
        role = author.role_tag or (author.approach[:90] + "…" if len(author.approach) > 90 else author.approach)
    linkedin = ""
    if author and author.linkedin:
        linkedin = (
            f'          <a class="brt-article__author-col-link" href="{escape(author.linkedin)}" '
            f'target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>\n'
        )
    name_link = author_name_link_html(
        author_slug,
        author_name,
        pre,
        css_class="brt-article__author-col-name",
    )
    return f"""
        <aside class="brt-article__author-col" aria-labelledby="article-author-label">
          <p id="article-author-label" class="brt-article__sidebar-label">Author</p>
          {img_block}
          {name_link}
          <p class="brt-body brt-article__author-col-role">{escape(role)}</p>
{linkedin}          <a class="brt-btn brt-btn--outline brt-btn--small" href="{pre}team/">Our team →</a>
        </aside>"""


def article_angebote_sidebar_html(category: str, depth: int, pre: str) -> str:
    pre = pre or pfx(depth)
    links = CATEGORY_ANGEBOTE.get(category, DEFAULT_ANGEBOTE)
    items = "\n".join(
        f'            <li><a href="{pre}services/{slug}/">{escape(label)}</a></li>'
        for slug, label in links
    )
    return f"""
          <nav class="brt-article__angebote" aria-labelledby="article-angebote-label">
            <p id="article-angebote-label" class="brt-article__sidebar-label">Related services</p>
            <ul class="brt-article__angebote-list">
{items}
            </ul>
          </nav>"""


def article_sidebar_html(toc: list[dict[str, str]], category: str, depth: int, pre: str) -> str:
    toc_block = article_toc_html(toc, depth)
    angebote = article_angebote_sidebar_html(category, depth, pre)
    if not toc_block.strip() and not angebote.strip():
        return ""
    return f"""
        <aside class="brt-article__aside" aria-label="Article navigation">
{toc_block}
{angebote}
        </aside>"""


def load_blog_posts(*, include_drafts: bool = False) -> list[BlogPost]:
    posts: list[BlogPost] = []
    if not BLOG_DIR.exists():
        return posts
    for path in sorted(BLOG_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        parts = raw.split("---", 2)
        if len(parts) < 3:
            continue
        meta = yaml.safe_load(parts[1]) or {}
        body = parts[2].strip()
        draft = bool(meta.get("draft", True))
        if draft and not include_drafts:
            continue
        reading = _reading_time(body, int(meta.get("reading_time_min", 0) or 0))
        excerpt = _clean_excerpt(meta.get("excerpt", ""))
        body_html, toc, lead, youtube_id = _postprocess_article_html(_render_markdown(body), excerpt)
        meta_youtube = _youtube_id_from_url(str(meta.get("youtube_url", "") or ""))
        faq = resolve_article_faq(meta.get("faq") or [], body_html, excerpt)
        posts.append(
            BlogPost(
                title=meta.get("title", path.stem),
                slug=meta.get("slug", path.stem),
                date=_parse_date(meta.get("date", "2026-01-01")),
                category=meta.get("category", "Risk management"),
                author=meta.get("author", ""),
                excerpt=excerpt,
                hero_image=meta.get("hero_image", ""),
                hero_alt=meta.get("hero_alt", meta.get("title", "")),
                draft=draft,
                reading_time_min=reading,
                faq=faq,
                related_slugs=meta.get("related_slugs") or [],
                body_html=body_html,
                toc=toc,
                lead=lead,
                youtube_id=meta_youtube or youtube_id,
                source_path=path,
            )
        )
    return sorted(posts, key=lambda p: p.date, reverse=True)


def resolve_image_src(src: str) -> str | None:
    if not src:
        return None
    base = Path(src)
    stem = base.with_suffix("")
    candidates: list[str] = []
    if base.suffix:
        candidates.append(src)
    for ext in (".webp", ".png", ".jpg", ".jpeg"):
        candidate = str(stem.with_suffix(ext)).replace("\\", "/")
        if candidate not in candidates:
            candidates.append(candidate)
    for candidate in candidates:
        if (SITE / candidate).exists():
            return candidate
    return None


def _image_dimensions(src: str) -> tuple[int, int] | None:
    meta_path = SITE / f"{src}.meta.json"
    if meta_path.exists():
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        return int(data["width"]), int(data["height"])
    full = SITE / src
    if not full.exists():
        return None
    try:
        from PIL import Image

        with Image.open(full) as im:
            return im.size
    except Exception:
        return None


def _srcset_variants(src: str) -> list[tuple[str, int]]:
    base = Path(src)
    stem = base.stem
    parent = base.parent
    variants: list[tuple[str, int]] = []
    for suffix, width in (("-480w", 480), ("-960w", 960), ("-1440w", 1440)):
        candidate = parent / f"{stem}{suffix}.webp"
        if (SITE / candidate).exists():
            variants.append((str(candidate).replace("\\", "/"), width))
    full = SITE / src
    if full.exists():
        dims = _image_dimensions(src)
        w = dims[0] if dims else 1920
        variants.append((src, w))
    return variants


def img_html(
    src: str,
    alt: str,
    depth: int,
    *,
    hero: bool = False,
    css_class: str = "",
    aspect: str = "16/9",
    high_detail: bool = False,
) -> str:
    resolved = resolve_image_src(src)
    if not resolved:
        label = escape(alt or "Image coming soon")
        return (
            f'<div class="brt-image-placeholder" role="img" aria-label="{label}" '
            f'style="aspect-ratio:{aspect}">'
            f'<span class="brt-image-placeholder__label">{label}</span></div>'
        )
    src = resolved
    full = SITE / src
    pre = pfx(depth)
    url = f"{pre}{src}"
    dims = _image_dimensions(src)
    w_attr = f' width="{dims[0]}"' if dims else ""
    h_attr = f' height="{dims[1]}"' if dims else ""
    srcset = ""
    if not high_detail:
        variants = _srcset_variants(src)
        if len(variants) > 1:
            parts = [f"{pre}{v} {width}w" for v, width in variants]
            srcset = f' srcset="{", ".join(parts)}" sizes="(max-width: 768px) 100vw, 960px"'
    loading = ' loading="eager" fetchpriority="high"' if hero else ' loading="lazy" decoding="async"'
    cls = f' class="{css_class}"' if css_class else ""
    return (
        f"<img src=\"{url}\" alt=\"{escape(alt)}\"{cls}{w_attr}{h_attr}{srcset}{loading}>"
    )


def format_date_de(d: date) -> str:
    months = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember",
    ]
    return f"{d.day}. {months[d.month - 1]} {d.year}"


def format_date_en(d: date) -> str:
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return f"{d.day} {months[d.month - 1]} {d.year}"


def blog_card_html(post: BlogPost, depth: int, featured: bool = False) -> str:
    pre = pfx(depth)
    href = f"{pre}blog/{post.slug}/"
    thumb = img_html(
        post.hero_image,
        post.hero_alt,
        depth,
        css_class="brt-card__thumb-img",
        aspect="16/9",
    )
    thumb_wrap = (
        thumb
        if "brt-image-placeholder" in thumb
        else f'<div class="brt-card__thumb">{thumb}</div>'
    )
    if "brt-card__thumb-img" in thumb:
        thumb_wrap = f'<div class="brt-card__thumb">{thumb}</div>'
    meta = f"{format_date_en(post.date)} · approx. {post.reading_time_min} min."
    cat_slug = CATEGORY_SLUGS.get(post.category, "all")
    excerpt_html = ""
    if post.excerpt:
        snippet = post.excerpt if len(post.excerpt) <= 150 else post.excerpt[:147].rsplit(" ", 1)[0] + "…"
        excerpt_html = f'\n              <p class="brt-body brt-card__excerpt">{escape(snippet)}</p>'
    featured_cls = " brt-card--featured" if featured else ""
    return f"""        <li class="brt-card brt-card--blog brt-hover-lift{featured_cls}" data-category="{cat_slug}">
          <a class="brt-card__link" href="{href}">
{thumb_wrap}
            <div class="brt-card__body">
              <span class="brt-tag brt-tag--small">{escape(post.category)}</span>
              <h3 class="brt-h3">{escape(post.title)}</h3>
              <p class="brt-meta">{meta}</p>{excerpt_html}
              <span class="brt-btn brt-btn--ghost">Read more →</span>
            </div>
          </a>
        </li>"""


def blog_filters_html(active: str = "all") -> str:
    items = ['<a href="#" class="is-active" data-filter="all">All</a>']
    for cat in BLOG_CATEGORIES:
        slug = CATEGORY_SLUGS[cat]
        cls = "is-active" if active == slug else ""
        items.append(f'<a href="#" data-filter="{slug}" class="{cls}">{escape(cat)}</a>')
    return "\n          ".join(items)


_SVG_LINKEDIN = (
    '<svg width="18" height="18" viewBox="0 0 448 512" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"/>'
    "</svg>"
)
_SVG_EMAIL = (
    '<svg width="18" height="18" viewBox="0 0 576 512" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M160 448c-25.6 0-51.2-22.4-64-32-64-44.8-83.2-60.8-96-70.4V480c0 17.67 14.33 32 32 32h256c17.67 0 32-14.33 32-32V345.6c-12.8 9.6-32 25.6-96 70.4-12.8 9.6-38.4 32-64 32zm128-192H32c-17.67 0-32 14.33-32 32v16c25.6 19.2 22.4 19.2 115.2 86.4 9.6 6.4 28.8 25.6 44.8 25.6s35.2-19.2 44.8-22.4c92.8-67.2 89.6-67.2 115.2-86.4V288c0-17.67-14.33-32-32-32zm256-96H224c-17.67 0-32 14.33-32 32v32h96c33.21 0 60.59 25.42 63.71 57.82l.29-.22V416h192c17.67 0 32-14.33 32-32V192c0-17.67-14.33-32-32-32zm-32 128h-64v-64h64v64zm-352-96c0-35.29 28.71-64 64-64h224V32c0-17.67-14.33-32-32-32H96C78.33 0 64 14.33 64 32v192h96v-32z"/>'
    "</svg>"
)
_SVG_PHONE = (
    '<svg width="18" height="18" viewBox="0 0 448 512" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M400 32H48A48 48 0 0 0 0 80v352a48 48 0 0 0 48 48h352a48 48 0 0 0 48-48V80a48 48 0 0 0-48-48zm-16.39 307.37l-15 65A15 15 0 0 1 354 416C194 416 64 286.29 64 126a15.7 15.7 0 0 1 11.63-14.61l65-15A18.23 18.23 0 0 1 144 96a16.27 16.27 0 0 1 13.79 9.09l30 70A17.9 17.9 0 0 1 189 181a17 17 0 0 1-5.5 11.61l-37.89 31a231.91 231.91 0 0 0 110.78 110.78l31-37.89A17 17 0 0 1 299 291a17.85 17.85 0 0 1 5.91 1.21l70 30A16.25 16.25 0 0 1 384 336a17.41 17.41 0 0 1-.39 3.37z"/>'
    "</svg>"
)


def team_contact_icons(member: TeamMember) -> str:
    items: list[str] = []
    name = escape(member.name)
    if member.linkedin:
        items.append(
            f'<li><a class="brt-team-contact__link" href="{escape(member.linkedin)}" '
            f'target="_blank" rel="noopener noreferrer" '
            f'aria-label="LinkedIn profile of {name}">{_SVG_LINKEDIN}</a></li>'
        )
    if member.email:
        items.append(
            f'<li><a class="brt-team-contact__link" href="mailto:{escape(member.email)}" '
            f'aria-label="Email {name}">{_SVG_EMAIL}</a></li>'
        )
    if member.phone:
        tel = re.sub(r"[^\d+]", "", member.phone)
        items.append(
            f'<li><a class="brt-team-contact__link" href="tel:{escape(tel)}" '
            f'aria-label="Phone {name}">{_SVG_PHONE}</a></li>'
        )
    if not items:
        return ""
    return f'<ul class="brt-team-contact">{"".join(items)}</ul>'


def team_extended_paragraphs_html(member: TeamMember) -> str:
    parts: list[str] = []
    for block in member.extended:
        text = (block.get("text") or "").strip()
        if not text:
            continue
        label = (block.get("label") or "").strip()
        if label:
            parts.append(
                f'<p class="brt-body"><strong>{escape(label)}:</strong> {escape(text)}</p>'
            )
        else:
            parts.append(f'<p class="brt-body">{escape(text)}</p>')
    return "\n            ".join(parts)


def team_profile_bio_html(member: TeamMember, slug_id: str) -> str:
    extended_html = team_extended_paragraphs_html(member)
    toggle = ""
    if extended_html:
        toggle = f"""
          <div class="brt-team-bio__more" id="{slug_id}-more" hidden>
            {extended_html}
          </div>
          <button type="button" class="brt-team-bio__toggle brt-btn brt-btn--ghost" aria-expanded="false" aria-controls="{slug_id}-more" data-more-label="Show more" data-less-label="Show less">Show more</button>"""
    return f"""
          <div class="brt-team-bio">
            <div class="brt-team-bio__preview">
              <p class="brt-body"><strong>My approach:</strong> {escape(member.approach)}</p>
              <p class="brt-body"><strong>My goal:</strong> {escape(member.goal)}</p>
            </div>{toggle}
          </div>"""


def team_profile_section(member: TeamMember, depth: int, *, alt_bg: bool = False) -> str:
    pre = pfx(depth)
    section_cls = "brt-section brt-section--alt" if alt_bg else "brt-section"
    split_cls = "brt-split brt-split--reverse" if member.layout == "reversed" else "brt-split"
    slug_id = team_section_id(member.slug)
    media = img_html(
        member.image,
        member.image_alt,
        depth,
        css_class="brt-team-portrait",
        aspect="4/5",
    )
    if "brt-image-placeholder" in media:
        media_block = f"""
        <div class="brt-split__media brt-fade-up">
          {media}
        </div>"""
    else:
        media_block = f"""
        <div class="brt-split__media brt-fade-up">
          {media}
        </div>"""
    contacts = team_contact_icons(member)
    bio = team_profile_bio_html(member, slug_id)
    return f"""
    <section class="{section_cls}" id="{slug_id}" aria-labelledby="{slug_id}-title">
      <div class="brt-container {split_cls}">
{media_block}
        <div class="brt-split__text brt-fade-up" style="--fade-delay: 120ms">
          <p class="brt-tag">{escape(member.role_tag)}</p>
          <h2 id="{slug_id}-title" class="brt-h2">{escape(member.name)}</h2>
          {contacts}
{bio}
        </div>
      </div>
    </section>"""


def _home_team_card_media(member: TeamMember, depth: int) -> str:
    pre = pfx(depth)
    full = SITE / member.image if member.image else None
    if member.image and full and full.exists():
        img = img_html(
            member.image,
            member.image_alt,
            depth,
            css_class="brt-card__media-img",
            aspect="4/5",
        )
        return f"          <div class=\"brt-card__media\">{img}</div>"
    first = member.name.split()[0]
    return f"""          <div
            class="brt-card__media brt-card__media--placeholder"
            role="img"
            aria-label="{escape(member.image_alt)}">
            <span class="brt-card__media-label">Photo of {escape(first)} coming soon</span>
          </div>"""


def home_team_card(member: TeamMember, depth: int, *, hidden: bool = False) -> str:
    pre = pfx(depth)
    role, bio = HOME_TEAM_CARD_COPY.get(
        member.slug,
        (member.role_tag, member.teaser_bio or member.approach[:160]),
    )
    extra_cls = " brt-home-team__card--more" if hidden else ""
    hidden_attr = " hidden" if hidden else ""
    href = team_member_url(pre, member.slug)
    return f"""        <li class="brt-card brt-card--profile brt-hover-lift{extra_cls}"{hidden_attr}>
          <a class="brt-card__link" href="{escape(href)}">
{_home_team_card_media(member, depth)}
          <div class="brt-card__body">
            <h3 class="brt-h3">{escape(member.name)}</h3>
            <p class="brt-meta brt-meta--accent">{escape(role)}</p>
            <p class="brt-body">{escape(bio)}</p>
          </div>
          </a>
        </li>"""


def home_team_section_html(depth: int = 0) -> str:
    pre = pfx(depth)
    members = [
        m for m in load_team_members() if m.active and m.profile_type == "full"
    ]
    by_slug = {m.slug: m for m in members}
    featured = [by_slug[s] for s in HOME_TEAM_FEATURED_SLUGS if s in by_slug]
    featured_slugs = {m.slug for m in featured}
    more = [m for m in members if m.slug not in featured_slugs]
    cards = "\n".join(home_team_card(m, depth) for m in featured)
    if more:
        cards += "\n" + "\n".join(home_team_card(m, depth, hidden=True) for m in more)
        toggle = """      <p class="brt-home-team__toggle-wrap brt-fade-up">
        <button
          type="button"
          class="brt-home-team__toggle"
          aria-expanded="false"
          aria-controls="home-team-cards"
          data-more-label="Show more"
          data-less-label="Show less">
          Show more
        </button>
      </p>"""
    else:
        toggle = ""
    return f"""  <!-- HOME_TEAM_START -->
  <section class="brt-section" id="home-team" aria-labelledby="team-title">
    <div class="brt-container">
      <header class="brt-section__header brt-fade-up">
        <p class="brt-tag">Who we are</p>
        <h2 id="team-title" class="brt-h2">One team, many perspectives, one goal: your security</h2>
      </header>
      <ul class="brt-cards-3col brt-stagger" id="home-team-cards">
{cards}
      </ul>
{toggle}
      <p class="brt-section__cta brt-fade-up">
        <a class="brt-btn brt-btn--outline" href="{pre}team/">More about the team →</a>
      </p>
    </div>
  </section>
  <!-- HOME_TEAM_END -->"""


FOUNDER_PODCAST_YOUTUBE_ID = "shVbfq7n9LQ"
FOUNDER_PODCAST_TITLE = "Risk Radar Episode 1 – Who is Beraterium?"


def founder_podcast_embed_html(youtube_id: str, title: str, page_url: str) -> str:
    safe_title = escape(title)
    watch_url = f"https://www.youtube.com/watch?v={youtube_id}"
    vid = escape(youtube_id)
    thumb = f"https://i.ytimg.com/vi/{vid}"
    page_attr = f'\n                data-youtube-page="{escape(page_url)}"'
    return f"""              <div
                class="brt-article__video-wrap"
                data-youtube-embed
                data-youtube-id="{vid}"{page_attr}
                data-youtube-title="{safe_title}"
              >
                <button type="button" class="brt-article__video-poster" aria-label="Play podcast: {safe_title}">
                  <img
                    src="{thumb}/maxresdefault.jpg"
                    srcset="{thumb}/maxresdefault.jpg 1280w, {thumb}/sddefault.jpg 640w"
                    sizes="(min-width: 1024px) min(420px, 40vw), 100vw"
                    alt="Video preview: Risk Radar Episode 1 – Who is Beraterium?"
                    width="1280"
                    height="720"
                    loading="lazy"
                    decoding="async"
                    data-youtube-thumb-base="{thumb}/"
                    onerror="if(this.src.includes('maxresdefault')){{this.src='{thumb}/sddefault.jpg';}}else if(this.src.includes('sddefault')){{this.src='{thumb}/hqdefault.jpg';}}"
                  >
                  <span class="brt-article__video-play" aria-hidden="true"></span>
                </button>
                <a
                  class="brt-article__video-yt-badge"
                  href="{watch_url}"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Watch on YouTube"
                >
                  <span class="brt-article__video-yt-prefix">Watch on</span>
                  <span class="brt-article__video-yt-brand" aria-hidden="true">
                    <svg class="brt-article__video-yt-icon" width="20" height="14" viewBox="0 0 20 14" focusable="false">
                      <path fill="#f03" d="M19.6 2.2A2.5 2.5 0 0 0 17.6.4C16.1 0 10 0 10 0S3.9 0 2.4.4A2.5 2.5 0 0 0 .4 2.2C0 3.7 0 7 0 7s0 3.3.4 4.8A2.5 2.5 0 0 0 2.4 13.6C3.9 14 10 14 10 14s6.1 0 7.6-.4a2.5 2.5 0 0 0 2-2.2C20 10.3 20 7 20 7s0-3.3-.4-4.8z"/>
                      <path fill="#fff" d="M8 4.5v5l5-2.5z"/>
                    </svg>
                    <span class="brt-article__video-yt-name">YouTube</span>
                  </span>
                </a>
              </div>"""


def about_founder_section_html(depth: int = 1) -> str:
    pre = pfx(depth)
    page_url = f"{SITE_URL}/about/"
    embed = founder_podcast_embed_html(
        FOUNDER_PODCAST_YOUTUBE_ID,
        FOUNDER_PODCAST_TITLE,
        page_url,
    )
    return f"""    <section class="brt-section brt-founder" aria-labelledby="founder-title">
      <div class="brt-container brt-split brt-split--founder brt-fade-up">
        <div class="brt-split__text brt-founder__story">
          <p class="brt-tag">THE FOUNDERS</p>
          <h2 id="founder-title" class="brt-h2">Two perspectives, one mission</h2>
          <p class="brt-founder__lead">Till and Peter met through social media — different paths, one shared belief: risks are not a threat but a chance to grow. That conversation became Beraterium.</p>
          <ul class="brt-founder-credentials brt-stagger">
            <li class="brt-founder-credential">
              <span class="brt-founder-credential__initial" aria-hidden="true">P</span>
              <div class="brt-founder-credential__body">
                <strong class="brt-founder-credential__name">Peter Münstermann</strong>
                <p class="brt-body">Over 20 years in a DAX-listed corporation — information protection, IT security and risk management up to board level. His insight: it is not technology but people who decide on security.</p>
              </div>
            </li>
            <li class="brt-founder-credential">
              <span class="brt-founder-credential__initial" aria-hidden="true">T</span>
              <div class="brt-founder-credential__body">
                <strong class="brt-founder-credential__name">Till Manfred Blania</strong>
                <p class="brt-body">Startups, research, people development — serial founder and economist. With his own analysis method, he spots early where teams get stuck and culture carries.</p>
              </div>
            </li>
          </ul>
          <p class="brt-body brt-founder__closer">Peter calm, structured, experienced. Till bold, change-oriented, always looking for the opportunity in risk. Together: corporate experience with start-up spirit — on equal footing.</p>
          <p class="brt-section__cta">
            <a class="brt-btn brt-btn--ghost" href="https://www.youtube.com/@Beraterium">All episodes on YouTube →</a>
            <a class="brt-btn brt-btn--outline" href="{pre}team/">Meet the team →</a>
          </p>
        </div>
        <aside class="brt-founder__media brt-fade-up" style="--fade-delay: 120ms" aria-labelledby="founder-podcast">
          <div class="brt-founder-podcast">
            <header class="brt-founder-podcast__head">
              <p class="brt-tag brt-tag--small">Risk Radar · Episode 1</p>
              <h3 id="founder-podcast" class="brt-h3">Who is Beraterium?</h3>
              <p class="brt-meta">Till &amp; Peter in conversation — your entry point into the podcast.</p>
            </header>
            <div class="brt-founder-podcast__video">
{embed}
            </div>
            <footer class="brt-founder-podcast__foot">
              <a class="brt-founder-podcast__link" href="{pre}blog/risk-radar-episode-1-who-is-beraterium/">Read the episode article →</a>
            </footer>
          </div>
        </aside>
      </div>
    </section>"""


def about_team_section_html(depth: int = 1) -> str:
    pre = pfx(depth)
    members = [m for m in load_team_members() if m.active and m.show_on_ueber_uns]
    by_slug = {m.slug: m for m in members}
    featured = [by_slug[s] for s in HOME_TEAM_FEATURED_SLUGS if s in by_slug]
    featured_slugs = {m.slug for m in featured}
    more = [m for m in members if m.slug not in featured_slugs]
    cards = "\n".join(team_teaser_card(m, depth) for m in featured)
    if more:
        cards += "\n" + "\n".join(team_teaser_card(m, depth, hidden=True) for m in more)
        toggle = """        <p class="brt-home-team__toggle-wrap brt-fade-up">
          <button
            type="button"
            class="brt-home-team__toggle"
            aria-expanded="false"
            aria-controls="about-team-cards"
            data-more-label="Show more"
            data-less-label="Show less">
            Show more
          </button>
        </p>"""
    else:
        toggle = ""
    return f"""    <section class="brt-section" id="about-team" aria-labelledby="team-teaser">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 id="team-teaser" class="brt-h2">The people behind Beraterium</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger" id="about-team-cards">
{cards}
        </ul>
{toggle}
        <p class="brt-section__cta brt-fade-up">
          <a class="brt-btn brt-btn--ghost" href="{pre}team/">Our team →</a>
        </p>
      </div>
    </section>"""


def team_teaser_card(member: TeamMember, depth: int, *, hidden: bool = False) -> str:
    pre = pfx(depth)
    media = img_html(
        member.image,
        member.image_alt,
        depth,
        css_class="brt-card__media-img",
        aspect="4/5",
    )
    if "brt-image-placeholder" in media:
        media_block = f"""
            <div class="brt-card__media brt-card__media--placeholder" role="img" aria-label="{escape(member.image_alt)}">
              <span class="brt-card__media-label">{escape(member.name)}</span>
            </div>"""
    else:
        media_block = f'<div class="brt-card__media">{media}</div>'
    bio = member.teaser_bio or member.approach[:120]
    href = f"{pre}team/index.html#{team_section_id(member.slug)}"
    extra_cls = " brt-home-team__card--more" if hidden else ""
    hidden_attr = " hidden" if hidden else ""
    return f"""          <li class="brt-card brt-card--profile brt-hover-lift{extra_cls}"{hidden_attr}>
            <a class="brt-card__link" href="{href}">
{media_block}
              <div class="brt-card__body">
                <h3 class="brt-h3">{escape(member.name)}</h3>
                <p class="brt-body">{escape(bio)}</p>
              </div>
            </a>
          </li>"""


def person_schema(member: TeamMember) -> dict[str, Any]:
    data: dict[str, Any] = {
        "@type": "Person",
        "name": member.name,
        "jobTitle": member.role_tag.split("·")[0].strip() if member.role_tag else "",
        "worksFor": {"@id": f"{SITE_URL}/#organization"},
        "inLanguage": "en-GB",
    }
    if member.image:
        data["image"] = f"{SITE_URL}/{member.image}"
    if member.email:
        data["email"] = f"mailto:{member.email}"
    if member.phone:
        data["telephone"] = member.phone
    if member.linkedin:
        data["sameAs"] = [member.linkedin]
    return data


def blog_posting_schema(post: BlogPost, author: TeamMember | None) -> str:
    author_obj: dict[str, Any] = {"@type": "Person", "name": author.name if author else "Beraterium"}
    if author and author.image:
        author_obj["image"] = f"{SITE_URL}/{author.image}"
    graph = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "datePublished": post.date.isoformat(),
        "dateModified": post.date.isoformat(),
        "author": author_obj,
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "mainEntityOfPage": f"{SITE_URL}/blog/{post.slug}/",
        "inLanguage": "en-GB",
    }
    if post.hero_image:
        graph["image"] = f"{SITE_URL}/{post.hero_image}"
    return json.dumps(graph, ensure_ascii=False, indent=2)


def gen_sitemap_urls() -> list[str]:
    static_routes = [
        "/",
        "/about/",
        "/team/",
        "/mission-vision/",
        "/method/",
        "/services/",
        "/services/startups/",
        "/services/smb/",
        "/services/solo/",
        "/risk-radar/",
        "/blog/",
        "/contact/",
        "/contact-form/",
        "/legal-notice/",
        "/privacy/",
        "/terms/",
    ]
    urls = [f"{SITE_URL}{route}" for route in static_routes]
    for post in load_blog_posts():
        urls.append(f"{SITE_URL}/blog/{post.slug}/")
    return urls


def write_sitemap() -> None:
    urls = gen_sitemap_urls()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  wrote sitemap.xml")
