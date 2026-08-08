#!/usr/bin/env python3
"""Generate Beraterium static pages from briefing content."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from _blindspot import blindspot_config_json
from _blindspot import selfcheck as blindspot_selfcheck
from _i18n import EN_SITE_URL, hreflang_links, language_switcher_html

from _pricing import PRICE_CATEGORIES, format_eur, offer_price_text
from _pricing_geo import (
    PREISE_GEO_FAQ,
    SCHULUNGEN_GEO_FAQ,
    pricing_compare_section,
    schulungen_value_section,
    schulung_geo_note,
)
from _schulungen import SCHULUNG_CONFIGS

from _cms import (
    SITE_URL,
    BlogPost,
    TeamMember,
    about_founder_section_html,
    about_team_section_html,
    article_author_sidebar_html,
    article_faq_section_html,
    faq_section_html,
    author_name_link_html,
    article_sidebar_html,
    article_youtube_embed_html,
    blog_card_html,
    blog_filters_html,
    blog_posting_schema,
    combine_jsonld,
    course_schema,
    faq_page_schema,
    format_date_en,
    local_business_schema,
    offer_catalog_schema,
    service_schema,
    speakable_webpage_schema,
    header_logo_html,
    home_team_section_html,
    img_html,
    load_blog_posts,
    load_team_members,
    person_schema,
    team_by_slug,
    team_contact_icons,
    team_profile_bio_html,
    team_profile_section,
    team_section_id,
    team_teaser_card,
    write_sitemap,
)

SITE = Path(__file__).parent
BRT_ASSET_VERSION = "20260715-blindspot-v5"

IMG_HOME_ANALYSE = "img/home/analyse-situation.webp"
IMG_METHODE_GEFAHRENKATALOG = "img/methode/gefahrenkatalog-3-ebenen.webp"
IMG_UEBER_UNS_RISIKORADAR = "img/ueber-uns/risikoradar.webp"
IMG_ANGEBOT_STARTUPS_HERO = "img/angebote/startups/hero.webp"
IMG_ANGEBOT_KMU_HERO = "img/angebote/kmu/hero.webp"
IMG_ANGEBOT_SOLO_HERO = "img/angebote/solo/hero.webp"
IMG_RELEVANZ_SCHWELLE = "img/garantie/relevanz-schwelle.webp"
IMG_NUTZEN_KRITERIEN = "img/garantie/nutzen-kriterien.webp"
IMG_BLINDSPOT_WARUM = "img/tools/blindspot-warum.webp"

ALT_TILL = "Till Manfred Blania, Managing Director Beraterium"
ALT_PETER = "Peter Münstermann, Beraterium"


def _depth_from_pre(pre: str) -> int:
    return pre.count("/")


def split_media_html(
    src: str,
    alt: str,
    depth: int,
    *,
    contain: bool = False,
    hover_zoom: bool = False,
) -> str:
    css_class = "brt-split__media-img--contain" if contain else ""
    aspect = "3/2" if contain else "4/3"
    media = img_html(src, alt, depth, css_class=css_class, aspect=aspect, high_detail=hover_zoom)
    slot_style = "--fade-delay: 120ms"
    if hover_zoom:
        slot_style += f"; --hover-zoom-aspect: {aspect.replace('/', ' / ')}"
    zoom_class = " brt-split__media--hover-zoom" if hover_zoom else ""
    return f"""        <div class="brt-split__media{zoom_class} brt-fade-up" style="{slot_style}">
          {media}
        </div>"""

COOKIEYES_HEAD = """  <!-- Start cookieyes banner -->
  <script id="cookieyes" type="text/javascript" src="https://cdn-cookieyes.com/client_data/d36bc57a067448f51ec9da2968bc257a/script.js"></script>
  <!-- End cookieyes banner -->"""

GA4_MEASUREMENT_ID = "G-BM435GHE6W"

GA4_ANALYTICS_HEAD = f"""  <!-- Google tag (gtag.js) — loads only after Analytics consent (CookieYes) -->
  <script type="text/plain" data-cookieyes="analytics" async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
  <script type="text/plain" data-cookieyes="analytics">
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA4_MEASUREMENT_ID}');
  </script>"""

NAV = [
    ("services", "Services"),
    ("method", "Method"),
    ("about", "About us"),
    ("risk-radar", "Risk Radar"),
    ("tools", "Tools"),
    ("blog", "Blog"),
]


def pfx(depth: int) -> str:
    return "../" * depth if depth else ""


CARET_SVG = (
    '<svg class="site-header__caret" width="10" height="6" viewBox="0 0 10 6" '
    'aria-hidden="true" focusable="false"><path d="M1 1l4 4 4-4" fill="none" '
    'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
    'stroke-linejoin="round"/></svg>'
)


def nav_html(depth: int, active: str | None) -> str:
    pre = pfx(depth)
    services_active = bool(
        active and (active.startswith("services") or active in ("pricing", "training"))
    )
    services_cur = ' aria-current="page"' if active == "services" else ""
    pricing_cur = ' aria-current="page"' if active == "pricing" else ""
    training_cur = ' aria-current="page"' if active == "training" else ""
    about_active = active in ("about", "team")
    tools_active = bool(active and active.startswith("tools"))
    tools_cur = ' aria-current="page"' if active == "tools" else ""

    def service_sub_cur(slug: str) -> str:
        return ' aria-current="page"' if active == f"services/{slug}" else ""

    def nav_cur(slug: str) -> str:
        return ' aria-current="page"' if active == slug else ""

    items = [
        f"""        <li class="site-header__item site-header__item--has-menu{" is-active" if services_active else ""}">
          <a href="{pre}services/" class="site-header__parent-link"{services_cur} aria-expanded="false">
            Services
            {CARET_SVG}
          </a>
          <ul class="site-header__submenu" aria-label="Services">
            <li><a href="{pre}services/startups/"{service_sub_cur("startups")}>Startups</a></li>
            <li><a href="{pre}services/smb/"{service_sub_cur("smb")}>SME</a></li>
            <li><a href="{pre}services/solo/"{service_sub_cur("solo")}>Solo self-employed</a></li>
            <li><a href="{pre}training/"{training_cur}>Training</a></li>
            <li><a href="{pre}pricing/"{pricing_cur}>Pricing</a></li>
          </ul>
        </li>""",
        f'        <li><a href="{pre}method/"{nav_cur("method")}>Method</a></li>',
        f"""        <li class="site-header__item site-header__item--has-menu{" is-active" if about_active else ""}">
          <a href="{pre}about/" class="site-header__parent-link" aria-expanded="false">
            About us
            {CARET_SVG}
          </a>
          <ul class="site-header__submenu" aria-label="About us">
            <li><a href="{pre}about/"{nav_cur("about")}>About the company</a></li>
            <li><a href="{pre}team/"{nav_cur("team")}>Our team</a></li>
          </ul>
        </li>""",
        f'        <li><a href="{pre}risk-radar/"{nav_cur("risk-radar")}>Risk Radar</a></li>',
        f"""        <li class="site-header__item site-header__item--has-menu{" is-active" if tools_active else ""}">
          <a href="{pre}tools/" class="site-header__parent-link"{tools_cur} aria-expanded="false">
            Tools
            {CARET_SVG}
          </a>
          <ul class="site-header__submenu" aria-label="Tools">
            <li><a href="{pre}tools/blindspot-check/"{nav_cur("tools/blindspot-check")}>Blindspot Check</a></li>
          </ul>
        </li>""",
        f'        <li><a href="{pre}blog/"{nav_cur("blog")}>Blog</a></li>',
    ]
    return "\n".join(items)


def footer_html(depth: int) -> str:
    pre = pfx(depth)
    lp_links = "\n".join(
        f'        <li><a href="{pre}solutions/{cfg["slug"]}/">{cfg["breadcrumb_name"]}</a></li>'
        for cfg in LP_CONFIGS
    )
    standort_items = "\n".join(
        f'        <li><a href="{pre}locations/{cfg["slug"]}/">{cfg["breadcrumb_name"]}</a></li>'
        for cfg in STANDORT_CONFIGS
    )
    standort_section = (
        f"""    <section>
      <h2>Beraterium on location</h2>
      <ul>
{standort_items}
      </ul>
    </section>
"""
        if STANDORT_CONFIGS
        else ""
    )
    return f"""<footer class="site-footer" aria-label="Footer">
  <div class="site-footer__inner">
    <section>
      <h2>Beraterium</h2>
      <p>Enterprise risk management, translated for mid-market businesses.</p>
      <a href="https://www.linkedin.com/company/beraterium">LinkedIn</a>
      <a href="https://www.youtube.com/@Beraterium">YouTube</a>
    </section>
    <section>
      <h2>Services</h2>
      <ul>
        <li><a href="{pre}services/startups/">Startups</a></li>
        <li><a href="{pre}services/smb/">SME</a></li>
        <li><a href="{pre}services/solo/">Solo self-employed</a></li>
        <li><a href="{pre}services/">Overview</a></li>
        <li><a href="{pre}pricing/">Pricing &amp; services</a></li>
        <li><a href="{pre}training/">Training</a></li>
      </ul>
    </section>
    <section>
      <h2>Solutions</h2>
      <ul>
{lp_links}
      </ul>
    </section>
{standort_section}    <section>
      <h2>Company</h2>
      <ul>
        <li><a href="{pre}about/">About us</a></li>
        <li><a href="{pre}team/">Team</a></li>
        <li><a href="{pre}mission-vision/">Mission &amp; Vision</a></li>
        <li><a href="{pre}method/">Method</a></li>
        <li><a href="{pre}benefit-guarantee/">Value guarantee</a></li>
        <li><a href="{pre}relevance-guarantee/">Relevance guarantee</a></li>
      </ul>
    </section>
    <section>
      <h2>Contact</h2>
      <ul>
        <li><a href="{pre}contact/">Book a free intro call</a></li>
        <li><a href="{pre}contact-form/">Contact form</a></li>
        <li><a href="{pre}accessibility/">Accessibility statement</a></li>
        <li><a href="{pre}legal-notice/">Legal notice</a></li>
        <li><a href="{pre}privacy/">Privacy</a></li>
        <li><a href="{pre}terms/">Terms</a></li>
      </ul>
    </section>
  </div>
  <p class="site-footer__legal">© Beraterium 2026</p>
</footer>"""


def shell(
    *,
    depth: int,
    title: str,
    description: str,
    canonical: str,
    active_nav: str | None,
    main: str,
    json_ld: str = "",
    noindex: bool = False,
    og_type: str = "website",
    og_image: str = "",
    extra_css: str = "",
    extra_scripts: str = "",
) -> str:
    pre = pfx(depth)
    home = pre or "./"
    robots = '\n  <meta name="robots" content="noindex">' if noindex else ""
    ld = f"\n  <script type=\"application/ld+json\">\n{json_ld}\n  </script>" if json_ld else ""
    hreflang = hreflang_links(canonical, current_locale="en")
    og_image_tag = f'\n  <meta property="og:image" content="{og_image}">' if og_image else ""
    lang_switch = language_switcher_html(current_locale="en", canonical=canonical, depth=depth)
    return f"""<!doctype html>
<html lang="en-GB">

<head>
{COOKIEYES_HEAD}
{GA4_ANALYTICS_HEAD}
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{EN_SITE_URL}{canonical}">{robots}{hreflang}

  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{EN_SITE_URL}{canonical}">
  <meta property="og:locale" content="en_GB">{og_image_tag}

  <link rel="icon" href="{pre}favicon.ico" sizes="any">
  <link rel="icon" href="{pre}favicon-dark.ico" sizes="any" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="{pre}icon.png" type="image/png" sizes="192x192">
  <link rel="icon" href="{pre}icon-dark.png" type="image/png" sizes="192x192" media="(prefers-color-scheme: dark)">
  <link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">
  <meta name="theme-color" content="#0E1116">
  <link rel="manifest" href="{pre}site.webmanifest">
  <meta name="referrer" content="strict-origin-when-cross-origin">

  <link rel="stylesheet" href="{pre}css/brt.css?v={BRT_ASSET_VERSION}" data-brt-css>
  <link rel="stylesheet" href="{pre}css/brt-fallback.css?v={BRT_ASSET_VERSION}">
  <link rel="stylesheet" href="{pre}css/brt-layout-fix.css?v={BRT_ASSET_VERSION}">{extra_css}
  <script src="{pre}js/brt-init.js"></script>{ld}
</head>

<body class="brt-page brt-page--inner">

<a class="brt-skip-link" href="#main-content">Skip to content</a>

<header class="site-header site-header--solid" aria-label="Main navigation">
  <div class="site-header__inner">
{header_logo_html(home, pre)}
    <button class="site-header__toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav id="site-nav" class="site-header__nav" aria-label="Primary navigation">
      <ul>
{nav_html(depth, active_nav)}
      </ul>
{lang_switch}
      <a class="brt-btn brt-btn--outline site-header__cta" href="{pre}contact/">Book a free intro call</a>
    </nav>
  </div>
</header>

<div class="brt">
  <main id="main-content">
{main}
  </main>
</div>

{footer_html(depth)}

<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>{extra_scripts}

</body>
</html>
"""


def hero(
    pre: str,
    tag: str,
    h1: str,
    lead: str,
    *,
    compact: bool = False,
    split: bool = False,
    media_label: str = "",
    media_src: str = "",
    actions: str = "",
) -> str:
    cls = "brt-page-hero brt-page-hero--dark"
    if compact:
        cls += " brt-page-hero--compact"
    if split:
        cls += " brt-page-hero--split"
    media = ""
    if split:
        depth = _depth_from_pre(pre)
        if media_src:
            media_inner = img_html(
                media_src,
                media_label,
                depth,
                css_class="brt-page-hero__img",
                aspect="4/3",
            )
        else:
            media_inner = f"""        <div class="brt-image-placeholder" role="img" aria-label="{media_label}">
          <span class="brt-image-placeholder__label">Image coming soon</span>
        </div>"""
        media = f"""
      <div class="brt-page-hero__media brt-fade-up" style="--fade-delay: 120ms">
        {media_inner}
      </div>"""
    act = f'\n        <div class="brt-page-hero__actions">{actions}</div>' if actions else ""
    return f"""
    <section class="{cls}" aria-labelledby="page-hero-title">
      <div class="brt-container">
        <div class="brt-fade-up">
          <p class="brt-tag">{tag}</p>
          <h1 id="page-hero-title" class="brt-h1">{h1}</h1>
          <p class="brt-lead brt-lead--on-dark">{lead}</p>{act}
        </div>{media}
      </div>
    </section>"""


def cta_band(pre: str, h2: str, body: str, btn: str = "Book a free intro call", *, note: str = "") -> str:
    note_html = f'\n        <p class="brt-meta brt-body--on-dark">{note}</p>' if note else ""
    return f"""
    <section class="brt-cta-band brt-cta-band--dark brt-section" aria-labelledby="final-cta">
      <div class="brt-container brt-cta-band__inner brt-fade-up">
        <h2 id="final-cta" class="brt-h2 brt-h2--on-dark">{h2}</h2>
        <p class="brt-body brt-body--on-dark">{body}</p>
        <a class="brt-btn brt-btn--on-dark brt-btn--lg" href="{pre}contact/">{btn}</a>{note_html}
      </div>
    </section>"""



ICON_GUARANTEE_SHIELD = (
    '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>'
)
ICON_GUARANTEE_TARGET = (
    '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">'
    '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
)


def guarantee_stat_row(items: list[tuple[str, str]], *, aria: str) -> str:
    lis = []
    for i, (num, label) in enumerate(items):
        delay = f' style="--fade-delay: {i * 80}ms"' if i else ""
        lis.append(
            f'<li class="brt-stat brt-fade-up"{delay}>'
            f'<span class="brt-stat__number">{num}</span>'
            f'<span class="brt-stat__label">{label}</span></li>'
        )
    return f"""
    <section class="brt-stat-row brt-section brt-section--compact" aria-label="{aria}">
      <div class="brt-container">
        <ul class="brt-stat-row__list">{"".join(lis)}</ul>
      </div>
    </section>"""


def guarantee_rule_band(quote: str, *, aria: str) -> str:
    return f"""
    <section class="brt-quote-band brt-quote-band--accent brt-section--compact" aria-label="{aria}">
      <div class="brt-container brt-fade-up">
        <p class="brt-quote-band__text">{quote}</p>
      </div>
    </section>"""



def guarantee_contrast_duo(
    *,
    left_tag: str,
    left_title: str,
    left_id: str,
    left_paras: list[str],
    left_note_label: str,
    left_note: str,
    right_tag: str,
    right_title: str,
    right_id: str,
    right_paras: list[str],
    right_note_label: str,
    right_note: str,
    section_id: str,
) -> str:
    """Balanced two-card contrast (relevance guarantee: not vs. seek)."""

    def paras_html(items: list[str]) -> str:
        return "".join(f'<p class="brt-body">{p}</p>' for p in items)

    def card(tag: str, title: str, cid: str, paras: list[str], note_label: str, note: str) -> str:
        return f"""
          <li id="{cid}" class="brt-contrast-card brt-fade-up">
            <p class="brt-tag">{tag}</p>
            <h2 class="brt-h2">{title}</h2>
            {paras_html(paras)}
            <div class="brt-contrast-card__footer">
              <div class="brt-contrast-card__note">
                <p class="brt-contrast-card__note-label">{note_label}</p>
                <p class="brt-body">{note}</p>
              </div>
            </div>
          </li>"""

    return f"""
    <section id="{section_id}" class="brt-section brt-section--alt brt-section--compact" aria-labelledby="{left_id}-title">
      <div class="brt-container">
        <ul class="brt-contrast-duo brt-stagger">
          {card(left_tag, left_title, left_id, left_paras, left_note_label, left_note)}
          {card(right_tag, right_title, right_id, right_paras, right_note_label, right_note)}
        </ul>
      </div>
    </section>"""


def guarantee_pair_section(pre: str, *, current: str) -> str:
    """Both guarantees side-by-side (homepage pattern). current: relevanz | nutzen."""
    cards = {
        "relevanz": {
            "slug": "relevance-guarantee",
            "num": "01",
            "icon": ICON_GUARANTEE_SHIELD,
            "title": "Relevance guarantee",
            "quote": "“We don’t find a relevant risk? Money back.”",
            "body": "If the analysis doesn’t identify a single risk above the agreed damage threshold, we refund the full amount.",
            "link": "Learn more →",
        },
        "nutzen": {
            "slug": "benefit-guarantee",
            "num": "02",
            "icon": ICON_GUARANTEE_TARGET,
            "title": "Value guarantee",
            "quote": "“No measurable value? Money back.”",
            "body": "If even one of the three agreed criteria isn’t met at the end, we refund 100% of the project price.",
            "link": "Learn more →",
        },
    }

    def card_html(key: str) -> str:
        c = cards[key]
        is_current = key == current
        cls = "brt-card brt-card--guarantee"
        if is_current:
            cls += " brt-card--guarantee-current"
        else:
            cls += " brt-hover-lift"
        foot = (
            f'<div class="brt-guarantee-card__foot"><span class="brt-guarantee-here"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>You are here</span></div>'
            if is_current
            else f'<div class="brt-guarantee-card__foot"><a href="{pre}{c["slug"]}/">{c["link"]}</a></div>'
        )
        aria = ' aria-current="page"' if is_current else ""
        return f"""
          <li class="{cls}"{aria}>
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">{c["icon"]}</div>
              <span class="brt-guarantee__num" aria-hidden="true">{c["num"]}</span>
            </div>
            <h3 class="brt-h3">{c["title"]}</h3>
            <p class="brt-quote">{c["quote"]}</p>
            <p class="brt-body">{c["body"]}</p>
            {foot}
          </li>"""

    return f"""
    <section class="brt-section brt-section--alt brt-section--compact" aria-labelledby="guarantee-pair">
      <div class="brt-container">
        <header class="brt-section__header brt-section__header--center brt-fade-up">
          <p class="brt-tag">DOUBLE GUARANTEE</p>
          <h2 id="guarantee-pair" class="brt-h2">Both pillars of our safety promise</h2>
          <p class="brt-body brt-section__lede">Two clear promises – if we don’t deliver, we refund the full amount.</p>
        </header>
        <ul class="brt-guarantee-duo brt-stagger">
          {card_html("relevanz")}
          {card_html("nutzen")}
        </ul>
      </div>
    </section>"""




def guarantee_rich_cta(
    pre: str,
    lead: str,
    sub: str,
    btn: str,
    *,
    contact_slug: str = "contact",
    team_name: str = "Your Beraterium team",
    team_note: str = "We’re here for you.",
    aria: str = "Book intro call",
) -> str:
    img = f"{pre}img/team/"
    return f"""
    <section class="brt-section brt-section--guarantee brt-section--compact" aria-labelledby="final-cta">
      <div class="brt-container">
        <aside class="brt-guarantee-cta brt-fade-up" aria-label="{aria}">
          <div class="brt-guarantee-cta__icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
          </div>
          <div class="brt-guarantee-cta__copy">
            <p class="brt-guarantee-cta__lead">{lead}</p>
            <p class="brt-guarantee-cta__sub">{sub}</p>
          </div>
          <a class="brt-btn brt-btn--white" href="{pre}{contact_slug}/">{btn}</a>
          <div class="brt-guarantee-cta__team">
            <div class="brt-guarantee-cta__avatars">
              <img src="{img}till-blania.webp" alt="" width="80" height="80" loading="lazy" decoding="async">
              <img src="{img}peter-muenstermann.webp" alt="" width="80" height="80" loading="lazy" decoding="async">
            </div>
            <div>
              <p class="brt-guarantee-cta__team-name">{team_name}</p>
              <p class="brt-guarantee-cta__team-note">{team_note}</p>
            </div>
          </div>
        </aside>
      </div>
    </section>"""


def steps_flow_section(*, en: bool = False) -> str:
    if en:
        tag = "THREE STEPS"
        h2 = "From risk picture to guided implementation"
        lede = "Three levels that build on each other – you choose the depth, we deliver clarity in euros."
        section_id = "steps-explainer"
        steps = (
            ("Step 1", "Analysis", "You get clarity: the prioritised risk picture, valued in euros."),
            ("Step 2", "Roadmap", "Plus concrete measures, prioritised, with timeline and owners."),
            ("Step 3", "Guidance", "Plus implementation support and access to the Risk Radar expert network."),
        )
    else:
        tag = "IMMER DREI STUFEN"
        h2 = "Vom Lagebild bis zur begleiteten Umsetzung"
        lede = "Drei Stufen, die aufeinander aufbauen – Sie wählen die Tiefe, wir liefern Klarheit in Euro."
        section_id = "options-explainer"
        steps = (
            ("Stufe 1", "Analyse", "Sie bekommen Klarheit: das priorisierte, in Euro bewertete Risiko-Lagebild."),
            ("Stufe 2", "Fahrplan", "Plus konkrete Maßnahmen, priorisiert, mit Timeline und Verantwortlichkeiten."),
            ("Stufe 3", "Begleitung", "Plus Umsetzungsbegleitung und Zugang zum RisikoRadar-Expertennetzwerk."),
        )
    icons = (
        """<svg class="brt-steps-flow__icon" viewBox="0 0 32 32" focusable="false" aria-hidden="true">
                    <rect x="5" y="19" width="5" height="9" rx="1"></rect>
                    <rect x="13.5" y="13" width="5" height="15" rx="1"></rect>
                    <rect x="22" y="7" width="5" height="21" rx="1"></rect>
                  </svg>""",
        """<svg class="brt-steps-flow__icon" viewBox="0 0 32 32" focusable="false" aria-hidden="true">
                    <circle cx="8" cy="24" r="3"></circle>
                    <circle cx="24" cy="8" r="3"></circle>
                    <path d="M8 24 L16 16 L24 8" fill="none" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"></path>
                  </svg>""",
        """<svg class="brt-steps-flow__icon" viewBox="0 0 32 32" focusable="false" aria-hidden="true">
                    <circle cx="16" cy="16" r="3.5"></circle>
                    <circle cx="8" cy="8" r="2.5"></circle>
                    <circle cx="24" cy="8" r="2.5"></circle>
                    <circle cx="8" cy="24" r="2.5"></circle>
                    <path d="M16 16 L8 8 M16 16 L24 8 M16 16 L8 24" fill="none" stroke-width="2" stroke-linecap="round"></path>
                  </svg>""",
    )
    items = []
    for i, ((label, title, body), icon) in enumerate(zip(steps, icons), 1):
        items.append(
            f"""              <li class="brt-steps-flow__item brt-steps-flow__item--{i}">
                <div class="brt-steps-flow__platform" aria-hidden="true">
                  {icon}
                </div>
                <div class="brt-steps-flow__copy">
                  <span class="brt-steps-flow__label">{label}</span>
                  <h3 class="brt-h3">{title}</h3>
                  <p class="brt-body">{body}</p>
                </div>
              </li>"""
        )
    return f"""
    <section class="brt-section brt-section--steps-flow" aria-labelledby="{section_id}">
      <div class="brt-container">
        <div class="brt-steps-flow">
          <header class="brt-steps-flow__intro brt-fade-up">
            <p class="brt-tag">{tag}</p>
            <h2 id="{section_id}" class="brt-h2">{h2}</h2>
            <p class="brt-steps-flow__lede">{lede}</p>
          </header>
          <div class="brt-steps-flow__diagram brt-fade-up">
            <svg class="brt-steps-flow__path" viewBox="0 0 640 400" aria-hidden="true" focusable="false">
              <path class="brt-steps-flow__path-soft" d="M48 318 C120 296, 188 276, 248 254"></path>
              <path class="brt-steps-flow__path-base" d="M48 318 C48 155, 170 48, 318 40 S505 32, 592 72"></path>
              <path class="brt-steps-flow__path-progress" d="M48 318 C48 155, 170 48, 318 40 S505 32, 592 72"></path>
            </svg>
            <ol class="brt-steps-flow__list brt-stagger">
{chr(10).join(items)}
            </ol>
          </div>
        </div>
      </div>
    </section>"""



def _render_case_study_panel(study: dict, index: int, labels: dict) -> str:
    active = " is-active" if index == 0 else ""
    hidden = "" if index == 0 else " hidden"
    meta_items = "".join(
        f'<li><span>{labels[key]}</span> {value}</li>'
        for key, value in study["meta"]
    )
    stats = "".join(
        f'<li class="brt-case-study__stat"><strong>{num}</strong><span>{text}</span></li>'
        for num, text in study["stats"]
    )
    return f"""            <article class="brt-case-study{active}" id="case-panel-{index}" role="tabpanel" aria-labelledby="case-tab-{index}" data-case-study-panel{hidden}>
              <div class="brt-case-study__grid">
                <div class="brt-case-study__challenge">
                  <p class="brt-case-study__label">{labels["challenge"]}</p>
                  <h3 class="brt-case-study__title">{study["title"]}</h3>
                  <ul class="brt-case-study__meta">
                    {meta_items}
                  </ul>
                  <p class="brt-case-study__text">{study["text"]}</p>
                </div>
                <div class="brt-case-study__body">
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">{labels["approach"]}</p>
                    <h4 class="brt-case-study__headline">{study["approach_headline"]}</h4>
                    <p class="brt-body">{study["approach_body"]}</p>
                  </div>
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">{labels["outcome"]}</p>
                    <ul class="brt-case-study__stats">
                      {stats}
                    </ul>
                  </div>
                  <blockquote class="brt-case-study__quote"><p>{study["quote"]}</p></blockquote>
                </div>
              </div>
            </article>"""


def case_studies_section(pre: str, *, en: bool = False) -> str:
    stufe1_link = f'<a href="{pre}angebote/">Risikoanalyse Stufe&nbsp;1</a>'
    if en:
        stufe1_headline = f'<a href="{pre}services/">Stage&nbsp;1 risk analysis</a>'
        cfg = {
            "tag": "FROM THE FIELD",
            "title": "Case studies from the field",
            "lede": "Five anonymised examples – how Stage&nbsp;1 risk analysis works in different phases, and where Stage&nbsp;2 turns insight into action.",
            "tablist_label": "Case studies",
            "prev_label": "Previous case study",
            "next_label": "Next case study",
            "note": "All details anonymised – no conclusions about individuals possible.",
            "labels": {
                "challenge": "Starting point",
                "approach": "Approach",
                "outcome": "Outcome",
                "industry": "Industry",
                "phase": "Phase",
                "team": "Team",
            },
        }
        studies = [
            {
                "tab": "Financial services",
                "title": "Startup founder, pre-launch",
                "meta": [("industry", "Financial services"), ("phase", "Pre-launch / structuring"), ("team", "1 founder + external partners")],
                "text": "Financing and regulation were on his radar – but there was no shared framework to compare all risk fields and no portfolio with clear priorities. Topics were discussed in isolation, not as one picture.",
                "approach_headline": stufe1_headline,
                "approach_body": "We worked through the core hazard matrix systematically: guiding question, damage scenario, euro bands, likelihood and inventory – what already mitigates the risk.",
                "stats": [("1", "Top priority: analysis &amp; decision models"), ("4", "Second tier: cyber, capital, market, reputation"), ("1", "Key partner exit made explicit"), ("✓", "Roadmap after launch")],
                "quote": "&ldquo;I knew there were risks. I just didn&rsquo;t know which came first – and which I&rsquo;d need to reassess after launch.&rdquo;",
            },
            {
                "tab": "Creative crafts",
                "title": "Solo self-employed, growing studio",
                "meta": [("industry", "Creative crafts"), ("phase", "Running business, scaling offer"), ("team", "1 person, project support")],
                "text": "Many open fronts, little time – but no shared priority. What to tackle first without spinning in circles was unclear. She carries every risk alone: customers, IT, premises, contracts, social media.",
                "approach_headline": "Stage&nbsp;1 + Stage&nbsp;2",
                "approach_body": "Stage&nbsp;1 revealed four equally weighted top risks. In Stage&nbsp;2 we turned each into action logic – cyber, reputation, physical total loss and organisation – with effort vs. impact trade-offs.",
                "stats": [("4", "Top risks: IT/cyber, reputation, total loss, processes"), ("A–D", "Stage&nbsp;2 blocks with next steps"), ("3", "Phases: now, 1–3 months, follow-ups"), ("↓", "Capacity freed for top risks")],
                "quote": "&ldquo;Stage&nbsp;1 showed which risks really carry the building – Stage&nbsp;2 how to tackle them without burning out.&rdquo;",
            },
            {
                "tab": "Health tech",
                "title": "MedTech founder in scaling phase",
                "meta": [("industry", "Health tech / MedTech"), ("phase", "Launch &amp; corporate health pilots"), ("team", "1 founder, bootstrapped")],
                "text": "Product on the market, strategic focus on corporate health programmes rather than pure e-commerce – but no shared framework to compare all 16 hazard fields. Individual topics were discussed, not as one portfolio.",
                "approach_headline": stufe1_headline,
                "approach_body": "Industry-specific MedTech questionnaire: health impact evidence, regulation, supply chain and copyable advantage – assessed separately for BGM and e-commerce channels.",
                "stats": [("4", "Stage&nbsp;1 priorities: impact, regulation, supply chain, copyability"), ("2", "BGM vs. e-commerce rated separately"), ("1", "Patent/trademark China flagged"), ("✓", "Roadmap after corporate health pilot")],
                "quote": "&ldquo;I assumed regulation would be top of the list. In the end there were four equal fields – and two of them I hadn&rsquo;t even considered for e-commerce.&rdquo;",
            },
            {
                "tab": "Recruiting",
                "title": "Recruitment firm, medical focus",
                "meta": [("industry", "Recruiting / staffing"), ("phase", "Established business, growth"), ("team", "4 shareholders, equity-funded")],
                "text": "Strong market demand, broad industry diversification – but no shared view of which risks carry the business. Many fields already covered by existing processes; three blind spots surfaced.",
                "approach_headline": stufe1_headline,
                "approach_body": "Recruiting-specific questionnaire with 15 hazard fields: recession, reputation, customer concentration and a follow-up question on phishing/ransomware – not in the standard catalogue.",
                "stats": [("4", "Stage&nbsp;1: recession, reputation, concentration, cyber"), ("7", "Inventory fields already covered"), ("25", "Industries diversified"), ("✓", "Phishing/ransomware as blind spot")],
                "quote": "&ldquo;We thought we had the basics covered. Then came the ransomware question – and we had no answer.&rdquo;",
            },
            {
                "tab": "Additive manufacturing",
                "title": "Wood 3D printing startup, R&amp;D phase",
                "meta": [("industry", "Additive manufacturing / wood 3D printing"), ("phase", "Research &amp; founding, project business"), ("team", "Founder team, university setting")],
                "text": "Development bureau rather than series production; anchor client in rail infrastructure – but unclear who owns which risk. Scalability depends on process reproducibility, not the printer alone.",
                "approach_headline": stufe1_headline,
                "approach_body": "Wood 3D printing questionnaire: product liability, sustainability claims, roles, fire risk, client concentration and funding – with team alignment on damage scenarios.",
                "stats": [("6", "Stage&nbsp;1: liability, sustainability, roles, fire, DB, liquidity"), ("1", "Reproducibility as bottleneck"), ("3", "Fields N/A – revisit when scaling"), ("✓", "English report planned")],
                "quote": "&ldquo;We thought the printer was the risk. What actually carries the building: liability, circularity claims and who is responsible for what.&rdquo;",
            },
        ]
    else:
        cfg = {
            "tag": "AUS DER PRAXIS",
            "title": "Case Studies aus der Praxis",
            "lede": "Fünf anonymisierte Einblicke – wie Risikoanalyse Stufe&nbsp;1 in unterschiedlichen Phasen wirkt und wo Stufe&nbsp;2 aus Erkenntnis konkrete Bearbeitung macht.",
            "tablist_label": "Case Studies",
            "prev_label": "Vorherige Case Study",
            "next_label": "Nächste Case Study",
            "note": "Alle Angaben anonymisiert – ohne Rückschlüsse auf Personen möglich.",
            "labels": {
                "challenge": "Ausgangssituation",
                "approach": "Ansatz",
                "outcome": "Ergebnis",
                "industry": "Branche",
                "phase": "Phase",
                "team": "Team",
            },
        }
        studies = [
            {
                "tab": "Finanzdienstleistungen",
                "title": "Startup-Gründer vor der Auflage",
                "meta": [("industry", "Finanzdienstleistungen"), ("phase", "Vorgründung / Strukturierung"), ("team", "1 Gründer, externe Partner")],
                "text": "Finanzierung und Regulatorik waren im Blick – aber kein gemeinsames Raster, um alle Felder zu vergleichen, und kein Portfolio mit Prioritäten. Einzelthemen waren besprochen, nicht als ein Gesamtbild.",
                "approach_headline": stufe1_link,
                "approach_body": "Systematische Kerngefahren-Matrix: Leitfrage, Schadenszenario, Euro-Stufen, Eintrittswahrscheinlichkeit und Inventar – was das Risiko bereits mindert.",
                "stats": [("1", "Top-Priorität: Analyse- & Entscheidungsmodelle"), ("4", "Zweite Ebene: Cyber, Kapitalgeber, Markt, Reputation"), ("1", "Schlüsselpartner-Ausstieg explizit"), ("✓", "Roadmap nach Unternehmensstart")],
                "quote": "&bdquo;Ich wusste, dass es Risiken gibt. Ich wusste nur nicht, welche zuerst – und welche ich nach dem Start neu bewerten muss.&ldquo;",
            },
            {
                "tab": "Kreativhandwerk",
                "title": "Solo-Selbstständige im laufenden Betrieb",
                "meta": [("industry", "Kreativhandwerk"), ("phase", "Laufender Betrieb, Wachstum"), ("team", "1 Person, projektweise Unterstützung")],
                "text": "Viele Baustellen, wenig Zeit – aber keine gemeinsame Priorität. Was zuerst angehen, ohne sich im Hamsterrad zu verlieren, war unklar. Alle Risiken trägt sie allein: Kunden, IT, Räume, Verträge, Social Media.",
                "approach_headline": "Stufe&nbsp;1 + Stufe&nbsp;2",
                "approach_body": "Stufe&nbsp;1 machte vier gleich gewichtete Top-Risiken sichtbar. In Stufe&nbsp;2 wurden daraus Bearbeitungslogiken – IT/Cyber, Reputation, physischer Totalausfall und Organisation – mit Aufwand-Wirkungs-Abwägung.",
                "stats": [("4", "Top-Risiken: IT/Cyber, Reputation, Totalausfall, Prozesse"), ("A–D", "Stufe-2-Blöcke mit nächsten Schritten"), ("3", "Phasen: Sofort, 1–3 Monate, Folgetermine"), ("↓", "Kapazität für Top-Risiken frei")],
                "quote": "&bdquo;Stufe&nbsp;1 hat gezeigt, welche wirklich das Gebäude tragen – Stufe&nbsp;2, wie ich sie ohne Selbstzerstörung angehen kann.&ldquo;",
            },
            {
                "tab": "Health-Tech",
                "title": "MedTech-Gründer in der Skalierungsphase",
                "meta": [("industry", "Health-Tech / MedTech"), ("phase", "Markteintritt &amp; BGM-Pilotprojekte"), ("team", "1 Gründer, bootstrap-finanziert")],
                "text": "Produkt am Markt, strategischer Fokus auf betriebliches Gesundheitsmanagement statt reinem E-Commerce – aber kein gemeinsames Raster für alle 16 Gefahrenfelder. Einzelthemen waren besprochen, nicht als Portfolio.",
                "approach_headline": stufe1_link,
                "approach_body": "Branchenspezifischer MedTech-Fragenkatalog: Wirkungsnachweis, Regulatorik, Lieferkette und kopierbarer Vorteil – getrennt bewertet für BGM- und E-Commerce-Kanal.",
                "stats": [("4", "Stufe-1-Prioritäten: Wirkung, Regulatorik, Lieferkette, Kopierbarkeit"), ("2", "BGM vs. E-Commerce getrennt"), ("1", "Patent/Marke China als Prüfpunkt"), ("✓", "Fortschreibung nach BGM-Pilotphase")],
                "quote": "&bdquo;Ich dachte, Regulatorik steht ganz oben. Am Ende waren es vier gleichrangige Felder – und zwei kannte ich aus dem E-Commerce gar nicht.&ldquo;",
            },
            {
                "tab": "Recruiting",
                "title": "Personalvermittler mit Medizin-Fokus",
                "meta": [("industry", "Recruiting / Personalvermittlung"), ("phase", "Etabliertes Geschäft, Wachstum"), ("team", "4 Gesellschafter, Eigenkapital")],
                "text": "Starke Marktnachfrage, breite Branchenstreuung – aber kein gemeinsames Bild, welche Risiken das Unternehmen tragen. Viele Felder durch bestehende Prozesse abgedeckt; drei blinde Flecken sichtbar gemacht.",
                "approach_headline": stufe1_link,
                "approach_body": "Recruiting-Fragenkatalog mit 15 Gefahrenfeldern: Rezession, Reputation, Klumpenrisiko und ergänzend Phishing/Ransomware als Zusatzfrage – nicht im Standard-Katalog.",
                "stats": [("4", "Stufe 1: Rezession, Reputation, Klumpenrisiko, Cyber"), ("7", "Inventar-Felder bereits abgedeckt"), ("25", "Branchen diversifiziert"), ("✓", "Phishing/Ransomware als blinder Fleck")],
                "quote": "&bdquo;Wir dachten, die Basics sitzen. Dann kam die Frage nach Ransomware – und wir hatten keine Antwort.&ldquo;",
            },
            {
                "tab": "Additive Fertigung",
                "title": "Holz-3D-Druck-Startup in der Entwicklungsphase",
                "meta": [("industry", "Additive Fertigung / Holz-3D-Druck"), ("phase", "Forschung &amp; Gründung, Projektgeschäft"), ("team", "Gründerteam, universitäres Umfeld")],
                "text": "Entwicklungsbüro statt Serienfertigung; zentraler Auftraggeber aus dem Bahnsektor – aber unklar, wer welches Risiko trägt. Skalierung hängt an Reproduzierbarkeit des Prozesses, nicht am Drucker allein.",
                "approach_headline": stufe1_link,
                "approach_body": "Holz-3D-Druck-Fragenkatalog: Produkthaftung, Nachhaltigkeitsversprechen, Rollen, Brandrisiko, Kundenkonzentration und Förderung – mit Teamabstimmung zu Schadensszenarien.",
                "stats": [("6", "Stufe 1: Haftung, Nachhaltigkeit, Rollen, Brand, DB, Liquidität"), ("1", "Reproduzierbarkeit als Engpass"), ("3", "Felder N.R. – bei Skalierung nachziehen"), ("✓", "Englische Auswertung geplant")],
                "quote": "&bdquo;Wir dachten, der Drucker ist das Risiko. Tatsächlich trägt das Gebäude: Haftung, Zirkularitätsversprechen und wer wofür zuständig ist.&ldquo;",
            },
        ]

    tabs = []
    for i, study in enumerate(studies):
        active = " is-active" if i == 0 else ""
        selected = "true" if i == 0 else "false"
        tab_index = "" if i == 0 else ' tabindex="-1"'
        tabs.append(
            f'<button type="button" class="brt-case-studies__tab{active}" role="tab" id="case-tab-{i}" aria-selected="{selected}" aria-controls="case-panel-{i}" data-case-study-tab{tab_index}>{study["tab"]}</button>'
        )
    panels = "\n".join(_render_case_study_panel(study, i, cfg["labels"]) for i, study in enumerate(studies))

    return f"""
    <section class="brt-section brt-case-studies" aria-labelledby="case-studies-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{cfg["tag"]}</p>
          <h2 id="case-studies-title" class="brt-h2">{cfg["title"]}</h2>
          <p class="brt-body">{cfg["lede"]}</p>
        </header>
        <div class="brt-case-studies__widget brt-fade-up" data-case-studies>
          <div class="brt-case-studies__tabs" role="tablist" aria-label="{cfg["tablist_label"]}">
            {"".join(tabs)}
          </div>
          <div class="brt-case-studies__panels">
{panels}
          </div>
          <div class="brt-case-studies__nav">
            <button type="button" class="brt-testimonials__btn brt-testimonials__btn--prev" data-case-study-prev aria-label="{cfg["prev_label"]}">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <button type="button" class="brt-testimonials__btn brt-testimonials__btn--next" data-case-study-next aria-label="{cfg["next_label"]}">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>
        </div>
        <p class="brt-meta brt-case-studies__note brt-fade-up">{cfg["note"]}</p>
      </div>
    </section>"""


def guarantee(
    pre: str,
    h2: str = "Double guarantee",
    *,
    tag: str | None = None,
    subtitle: str = "Two clear promises &mdash; if we don&rsquo;t deliver, you get a full refund.",
    du: bool = False,
) -> str:
    img = f"{pre}img/team/"
    if tag is None:
        tag = "Your risk is on us" if du else "Your risk is on us"
    nutzen_body = (
        "Before we start, we agree 3&ndash;5 value criteria together. If none are met at the end, you receive a full refund. No questions asked."
        if du
        else "Before we start, we agree 3&ndash;5 value criteria together. If none are met at the end, you receive a full refund. No questions asked."
    )
    cta_lead = "Let&rsquo;s turn your risk into clarity." if du else "Let&rsquo;s turn your risk into clarity."
    cta_sub = "Book a free, no-obligation intro call today."
    team_name = "Your Beraterium team"
    team_note = "We&rsquo;re here for you."
    return f"""
    <section class="brt-section brt-section--guarantee" aria-labelledby="garantie-title">
      <div class="brt-container">
        <header class="brt-section__header brt-section__header--center brt-fade-up">
          <p class="brt-tag">{tag}</p>
          <h2 id="garantie-title" class="brt-h2">{h2}</h2>
          <p class="brt-body brt-section__lede">{subtitle}</p>
        </header>
        <ul class="brt-guarantee-duo brt-stagger">
          <li class="brt-card brt-card--guarantee brt-hover-lift">
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
              </div>
              <span class="brt-guarantee__num" aria-hidden="true">01</span>
            </div>
            <h3 class="brt-h3">Relevance guarantee</h3>
            <p class="brt-quote">&ldquo;No relevant risk found? Money back.&rdquo;</p>
            <p class="brt-body">If the analysis does not identify a single risk with relevant financial impact (threshold agreed jointly in advance), we refund the full amount.</p>
            <a href="{pre}relevance-guarantee/">Learn more &rarr;</a>
          </li>
          <li class="brt-card brt-card--guarantee brt-hover-lift">
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              </div>
              <span class="brt-guarantee__num" aria-hidden="true">02</span>
            </div>
            <h3 class="brt-h3">Value guarantee</h3>
            <p class="brt-quote">&ldquo;No measurable value? Money back.&rdquo;</p>
            <p class="brt-body">{nutzen_body}</p>
            <a href="{pre}benefit-guarantee/">Learn more &rarr;</a>
          </li>
        </ul>
        <aside class="brt-guarantee-cta brt-fade-up" aria-label="Book an intro call">
          <div class="brt-guarantee-cta__icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
          </div>
          <div class="brt-guarantee-cta__copy">
            <p class="brt-guarantee-cta__lead">{cta_lead}</p>
            <p class="brt-guarantee-cta__sub">{cta_sub}</p>
          </div>
          <a class="brt-btn brt-btn--white" href="{pre}contact/">Book an appointment now &rarr;</a>
          <div class="brt-guarantee-cta__team">
            <div class="brt-guarantee-cta__avatars" aria-hidden="true">
              <img src="{img}till-blania.webp" alt="" width="80" height="80" loading="lazy" decoding="async">
              <img src="{img}peter-muenstermann.webp" alt="" width="80" height="80" loading="lazy" decoding="async">
            </div>
            <div>
              <p class="brt-guarantee-cta__team-name">{team_name}</p>
              <p class="brt-guarantee-cta__team-note">{team_note}</p>
            </div>
          </div>
        </aside>
      </div>
    </section>"""


def faq_section(items: list[tuple[str, str]], *, alt: bool = False, title: str = "Frequently asked questions") -> str:
    return faq_section_html(items, title=title, alt=alt)


def page_schema(*blocks: str) -> str:
    return combine_jsonld(*[b for b in blocks if b and b.strip()])


def write(rel: str, html: str) -> None:
    path = SITE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print(f"  wrote {rel}")


def gen_ueber_uns() -> None:
    pre = "../"
    radar_media = split_media_html(
        IMG_UEBER_UNS_RISIKORADAR,
        "Network and collaboration at Risk Radar",
        1,
    )
    main = (
        hero(
            pre,
            "ABOUT BERATERIUM",
            "Why Beraterium exists",
            "Understanding risk should not be a privilege of large corporations. We bring professional risk management to where it has been missing: mid-market businesses, startups, and solo self-employed professionals.",
        )
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="story-title">
      <div class="brt-container brt-fade-up">
        <h2 id="story-title" class="brt-h2">A method that fits how businesses actually work</h2>
        <p class="brt-body">Many business owners know risks exist. But few know which risks matter most for their business.</p>
        <p class="brt-body">Classic risk management methods are often built for corporations: complex, theoretical, and time-consuming. For mid-market businesses, startups, or smaller companies, they rarely match reality.</p>
        <p class="brt-body">Beraterium was born from exactly this gap. We developed a method that helps businesses, together with their people, build a clear picture of their most important risks in a short time – understandable, practical, and without bureaucracy.</p>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="values-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">WHAT WE STAND FOR</p>
          <h2 id="values-title" class="brt-h2">Enterprise-grade substance, without the corporate coldness</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Corporate experience for everyone</h3>
            <p class="brt-body">What was once only available to large corporations, we make understandable, affordable, and ready to use for startups, SMEs, and smaller businesses.</p>
          </li>
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">People before systems</h3>
            <p class="brt-body">The focus is on your people, not the tool. We run analyses with the people involved – not over their heads. That produces realistic results and genuine buy-in.</p>
          </li>
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Impact before perfection</h3>
            <p class="brt-body">A good estimate beats a perfect calculation that never gets done. We look for not the most measures – but the right ones.</p>
          </li>
        </ul>
      </div>
    </section>
"""
        + about_founder_section_html(1)
        + """
    <section class="brt-section" aria-labelledby="radar-teaser">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <p class="brt-tag">MORE THAN CONSULTING</p>
          <h2 id="radar-teaser" class="brt-h2">From insight to action</h2>
          <p class="brt-body">Risk Radar grew out of our work: a community where business owners and experts talk openly about risk, share experience, and learn from each other. Risks are easier to understand when you are not thinking about them alone. And when insight becomes concrete action, teams build workspaces where they develop and implement solutions together.</p>
          <a class="brt-btn brt-btn--ghost" href="../risk-radar/">Discover Risk Radar →</a>
        </div>
{radar_media}
      </div>
    </section>
    <section class="brt-quote-band brt-quote-band--accent" aria-label="Quote">
      <div class="brt-container brt-fade-up">
        <p class="brt-quote-band__text">&ldquo;Beraterium is a thinking space for business owners, where risks become visible and better decisions follow.&rdquo;</p>
      </div>
    </section>
"""
        + about_team_section_html(1)
    )
    main = main.replace("{radar_media}", radar_media)
    about_faq = [
        ("What is Beraterium?", "Beraterium makes professional risk management accessible to SMEs, startups, and solo self-employed professionals — understandable, practical, and without corporate bureaucracy."),
        ("Who is Beraterium for?", "For managing directors, founders, and solo self-employed professionals who want to know which risks could really hit their business — before they become expensive."),
        ("What sets Beraterium apart from classic consulting?", "We do not deliver PowerPoint to file away: structured risk analysis in euros, facilitated with your team, with clear implementation — yourself, with partners, or via Risk Radar."),
    ]
    main += faq_section_html(about_faq, title="Frequently asked questions about Beraterium", section_id="faq", alt=True)
    main += cta_band(
        pre,
        "Let's get to know each other.",
        "In a free intro call, we will show you how to make your biggest risks visible – 30 minutes, no obligation.",
    )
    write(
        "about/index.html",
        shell(
            depth=1,
            title="About Beraterium – Why we exist | Beraterium",
            description="Beraterium was born from a gap: corporate risk management does not fit SMEs, startups, or solo self-employed professionals. We make it understandable, practical, and bureaucracy-free.",
            canonical="/about/",
            active_nav="about",
            main=main,
            json_ld=page_schema(faq_page_schema(about_faq)),
        ),
    )


def gen_team() -> None:
    pre = "../"
    members = [m for m in load_team_members() if m.active and m.profile_type == "full"]
    profiles = "".join(
        team_profile_section(m, 1, alt_bg=(i % 2 == 1))
        for i, m in enumerate(members)
    )
    person_graph = [person_schema(m) for m in members]
    main = (
        hero(
            pre,
            "OUR TEAM",
            "One team, many perspectives, one goal: your peace of mind",
            "Behind Beraterium are people with decades of industry expertise and fresh entrepreneurial spirit – practical, solution-focused, and always on equal footing with you.",
            compact=True,
        )
        + profiles
        + """
    <section class="brt-section" aria-labelledby="shared-values">
      <div class="brt-container brt-fade-up">
        <ul class="brt-values-inline">
          <li>On equal footing</li>
          <li>Practice over theory</li>
          <li>People before systems</li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--dark" aria-labelledby="network-title">
      <div class="brt-container brt-split brt-split--text-only">
        <div class="brt-split__text brt-fade-up">
          <h2 id="network-title" class="brt-h2 brt-h2--on-dark">And a whole network behind you</h2>
          <p class="brt-body brt-body--on-dark">For implementation, we draw on Risk Radar – a protected network of vetted experts, accessible only by referral or application. When you need them, you get exactly the specialists who fit your topic.</p>
          <a class="brt-btn brt-btn--on-dark" href="../risk-radar/">Risk Radar →</a>
        </div>
      </div>
    </section>"""
        + cta_band(
            pre,
            "Speak with us directly",
            "Every analysis is personally led by Till and Peter. Book your free intro call.",
        )
    )
    json_ld = json.dumps(
        {"@context": "https://schema.org", "@graph": person_graph},
        ensure_ascii=False,
        indent=2,
    )
    write(
        "team/index.html",
        shell(
            depth=1,
            title="Our team – Beraterium",
            description="Meet the team behind Beraterium: founders, risk management, marketing, financial advice, and industry expertise – united for SMEs, startups, and solo self-employed professionals.",
            canonical="/team/",
            active_nav="team",
            main=main,
            json_ld=json_ld,
        ),
    )


def gen_mission_vision() -> None:
    pre = "../"
    main = (
        hero(
            pre,
            "MISSION & VISION",
            "Understand risk. Secure your future. Together.",
            "We believe every business – regardless of size – has the right to know its biggest risks and face them with confidence.",
            compact=True,
        )
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="mission-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">OUR MISSION</p>
        <h2 id="mission-title" class="brt-h2">Making corporate-grade tools accessible to mid-market businesses</h2>
        <p class="brt-lead">We support startups, SMEs, and solo self-employed professionals with risk and HR management solutions that are usually reserved for large organisations. Understandable, affordable, and ready to implement. We combine 20 years of German industry expertise with start-up spirit – from gut feeling to clarity – from clarity to decisive action.</p>
      </div>
    </section>
    <section class="brt-section brt-section--dark" aria-labelledby="vision-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">OUR VISION</p>
        <h2 id="vision-title" class="brt-h2 brt-h2--on-dark">Businesses where people enjoy working</h2>
        <p class="brt-body brt-body--on-dark">We want risk management to be understood not as a source of fear, but as a chance for lasting success. Our vision is businesses that spot risks early, share responsibility, and grow together – places where security, trust, and collaboration are simply how things work.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="principles-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">WHAT GUIDES US</p>
          <h2 id="principles-title" class="brt-h2">Six principles that shape our work</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">On equal footing</h3><p class="brt-body">Fair, honest, and always on your side. We will not blow your budget – we help you build lasting success.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">People before systems</h3><p class="brt-body">Your people often know processes and weak spots better than any manual. We work with the people involved, not over their heads.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Clarity over complexity</h3><p class="brt-body">We make complex topics simple, understandable, and immediately applicable. So you see results quickly.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Impact before perfection</h3><p class="brt-body">Direction over absolute precision. A good estimate beats a perfect calculation that never gets done.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Tailored, not off-the-shelf</h3><p class="brt-body">We combine theory and practice: together with you and your team, we develop solutions that fit your business.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Responsibility &amp; partnership</h3><p class="brt-body">We stay your single point of contact – whichever implementation path you choose.</p></li>
        </ul>
      </div>
    </section>"""
        + faq_section_html([
            ("What is Beraterium's mission?", "To make corporate risk management accessible to SMEs, startups, and solo self-employed professionals — understandable, affordable, and ready to implement."),
            ("What is Beraterium's vision?", "Businesses where people enjoy working, spot risks early, and grow together."),
        ], title="Frequently asked questions about mission & vision", section_id="faq", alt=True)
        + cta_band(
            pre,
            "Share our approach?",
            "Then let&rsquo;s talk. 30 minutes, free, no obligation.",
        )
    )
    mission_faq = [
        ("What is Beraterium's mission?", "To make corporate risk management accessible to SMEs, startups, and solo self-employed professionals — understandable, affordable, and ready to implement."),
        ("What is Beraterium's vision?", "Businesses where people enjoy working, spot risks early, and grow together."),
    ]
    write(
        "mission-vision/index.html",
        shell(
            depth=1,
            title="Mission & Vision – Risk management for everyone | Beraterium",
            description="Our mission: make corporate risk management accessible to SMEs, startups, and solo self-employed professionals. Our vision: businesses where people enjoy working and grow together.",
            canonical="/mission-vision/",
            active_nav=None,
            main=main,
            json_ld=page_schema(faq_page_schema(mission_faq)),
        ),
    )


def pricing_cards(pre: str, options: list[dict]) -> str:
    cards = []
    for opt in options:
        feat = "".join(f"<li>{f}</li>" for f in opt.get("features", []))
        extra = f'<p class="brt-meta brt-meta--accent">{opt["extra"]}</p>' if opt.get("extra") else ""
        badge = f'<span class="brt-pricing__badge">{opt["badge"]}</span>' if opt.get("badge") else ""
        featured = " brt-pricing__card--featured" if opt.get("featured") else ""
        cards.append(
            f"""          <li class="brt-pricing__card{featured} brt-hover-lift">
            {badge}
            <h3 class="brt-h3">{opt["title"]}</h3>
            <p class="brt-pricing__claim">{opt["claim"]}</p>
            {extra}
            <ul>{feat}</ul>
            <a class="brt-btn brt-btn--outline" href="{pre}contact/">Book a free intro call</a>
          </li>"""
        )
    return f"""
    <section id="optionen" class="brt-section brt-section--alt" aria-labelledby="options-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">THREE PATHS</p>
          <h2 id="options-title" class="brt-h2">Choose how far we go together</h2>
        </header>
        <ul class="brt-pricing brt-stagger">
{chr(10).join(cards)}
        </ul>
        <p class="brt-meta brt-centered-cta brt-fade-up" style="margin-top: var(--space-8);">We discuss pricing individually in the intro call – matched to your phase and scope.</p>
      </div>
    </section>"""


def gen_methode() -> None:
    pre = "../"
    faq = [
        ("What is a hazard catalog in risk management?", "A hazard catalog is a structured, judgment-free list of everything that could harm a business. Beraterium's 3-level hazard catalog keeps the number manageable. Only when the catalog is complete does assessment begin."),
        ("What is the difference between a hazard and a risk?", "A hazard is anything that can cause harm – collected neutrally. It becomes a risk only when we assess how likely it is and what financial damage it would cause in euros."),
        ("Why does Beraterium assess risks in euros instead of traffic-light colours?", "Traffic-light colours are subjective. Damage in euros is concrete, negotiable, and enables objective prioritisation — biggest damage first, regardless of gut feeling or hierarchy."),
        ("What is a risk management process and how does Beraterium's work?", "Three phases: (1) collect hazards in the 3-level catalog, (2) assess risks — damage in euros × likelihood, minus existing measures, (3) implement the few measures with the greatest impact."),
        ("How long does a risk analysis take?", "Depending on audience, typically 2 weeks (solo) to 6 weeks (SME). We agree the exact timeline at kick-off."),
        ("Do I need prior knowledge or preparation?", "No. You bring your knowledge of your business – we bring the structure and the method."),
        ("What if I work alone?", "Two facilitators and an AI sparring partner replace the missing team so the assessment stays balanced."),
        ("Do you implement the measures too?", "You choose the path: yourself, with your own suppliers, or through our coordination via the Risk Radar network. Beraterium stays your single point of contact."),
    ]
    method_title = "Risk management method: 3-level catalog | Beraterium"
    method_desc = "How does risk management work without corporate bureaucracy? 3-level hazard catalog, assessment in euros, measure prioritisation. Learn more for free."
    method_ld = page_schema(
        service_schema(
            name="Beraterium risk management method",
            description=method_desc,
            url="/method/",
            audience="SMEs, startups and solo self-employed professionals",
        ),
        faq_page_schema(faq),
        speakable_webpage_schema("/method/"),
    )
    main = (
        hero(
            pre,
            "HOW WE WORK",
            "From gut feeling to clarity – in clear steps",
            "Our method deliberately separates three questions: What happens in the worst case? How often does that happen? And what have you already done about it today? Step by step, a clear picture emerges.",
            actions=f'<a class="brt-btn" href="{pre}contact/">Book a free intro call</a>',
        )
        + f"""
    <nav class="brt-anchor-nav" aria-label="On this page" data-anchor-nav>
      <div class="brt-container brt-anchor-nav__inner">
        <p class="brt-anchor-nav__label">On this page</p>
        <div class="brt-anchor-nav__track">
          <ul class="brt-anchor-nav__list">
            <li><a class="brt-anchor-nav__link" href="#hazard-catalog">Hazard catalog</a></li>
            <li><a class="brt-anchor-nav__link" href="#assessment">Assessment</a></li>
            <li><a class="brt-anchor-nav__link" href="#inventory">Inventory</a></li>
            <li><a class="brt-anchor-nav__link" href="#implementation">Implementation</a></li>
            <li><a class="brt-anchor-nav__link" href="#faq">FAQ</a></li>
          </ul>
        </div>
      </div>
    </nav>
    <section id="hazard-catalog" class="brt-section" aria-labelledby="s3-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="s3-title" class="brt-h2">What is the hazard catalog – and why 3 levels?</h2>
          <p class="brt-body">The hazard catalog first collects neutrally and completely what can harm a business – without judging how likely or severe something is. To keep the number of possible hazards manageable, the catalog is limited to three clear levels.</p>
          <p class="brt-body">We deliberately work with hazards because they form a neutral starting point. Only in the second step do they become risks – when we assess how relevant a hazard is for your business.</p>
        </div>
        {split_media_html(IMG_METHODE_GEFAHRENKATALOG, "Beraterium hazard catalog with three levels", 1, contain=True, hover_zoom=True)}
      </div>
    </section>
    <section id="assessment" class="brt-section brt-section--alt" aria-labelledby="s4-title">
      <div class="brt-container brt-fade-up">
        <h2 id="s4-title" class="brt-h2">How do we assess how big a risk really is?</h2>
        <p class="brt-body">We move from gut feeling to a concrete scenario. Instead of asking &lsquo;How likely is that?&rsquo;, we say: &lsquo;Imagine it has already happened.&rsquo; Then we estimate what that event means for your business – and translate the damage into euros.</p>
        <div class="brt-highlight-box" style="margin-top: var(--space-8);">
          <h3 class="brt-h3">Example</h3>
          <p class="brt-body"><strong>Hazard:</strong> Loss of the business owner (key person). <strong>Guiding question:</strong> What happens if you cannot work tomorrow? <strong>Scenario:</strong> Absence for 4 weeks. → On that basis, the extent of damage is estimated in euros.</p>
        </div>
        <p class="brt-quote" style="margin-top: var(--space-8);">&ldquo;Direction over absolute precision.&rdquo;</p>
        <p class="brt-body">A good estimate beats a perfect calculation that never gets done.</p>
      </div>
    </section>
    <section id="inventory" class="brt-section" aria-labelledby="s5-title">
      <div class="brt-container brt-two-col brt-fade-up">
        <div>
          <h2 id="s5-title" class="brt-h2">Do we count what you already do?</h2>
          <p class="brt-body">Yes. Alongside damage, we assess likelihood – in understandable timeframes such as weeks, months or years. And we factor in your &lsquo;inventory&rsquo;: existing measures that already reduce the risk today.</p>
        </div>
        <div>
          <p class="brt-body">For example, cover that can take on around 50&nbsp;% at short notice. The damage would be higher in principle – but measures like this reduce it significantly.</p>
        </div>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="s6-title">
      <div class="brt-container brt-fade-up">
        <h2 id="s6-title" class="brt-h2">Why do several people assess instead of one?</h2>
        <p class="brt-body">Because multiple perspectives lead to a more realistic assessment than a single opinion. In a business, that ideally happens with different managers and team members – with people at the centre, not the system.</p>
        <div class="brt-highlight-box" style="margin-top: var(--space-8);">
          <h3 class="brt-h3">What if I work alone?</h3>
          <p class="brt-body">For solo self-employed people and micro-businesses, we deliberately replace the missing team: two facilitators who structure and challenge, plus an AI sparring partner for statistical estimates and experience-based input.</p>
        </div>
      </div>
    </section>
    <section id="implementation" class="brt-section brt-section--dark" aria-labelledby="s7-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 id="s7-title" class="brt-h2 brt-h2--on-dark">What happens after the analysis?</h2>
          <p class="brt-body brt-body--on-dark">The analysis creates clarity – the real value comes in implementation. Three paths are open. You choose which one. Beraterium stays your single point of contact.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Implement yourself</h3><p class="brt-body">With your own team. Suited to organisational or simple measures and existing capability.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">With your suppliers</h3><p class="brt-body">Continue with trusted partners. Suited to established relationships and structures.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">We coordinate</h3><p class="brt-body">One fixed contact, one face to the customer. We bring the right people together and make sure measures fit together.</p></li>
        </ul>
        <p class="brt-quote" style="margin-top: var(--space-8); color: #fff; text-align: center;">&ldquo;Not analysis to file away – solutions to act on.&rdquo;</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="s8-title">
      <div class="brt-container brt-fade-up">
        <h2 id="s8-title" class="brt-h2">How do we choose which measures actually help?</h2>
        <p class="brt-body">We tackle the biggest risks first. Each measure has one purpose: reduce damage and/or reduce likelihood.</p>
        <div class="brt-criteria-inline">
          <span>effective</span><span>cost-effective</span><span>feasible</span><span>sustainable</span>
        </div>
        <p class="brt-quote" style="margin-top: var(--space-8);">&ldquo;We look for not the most measures – but the right ones.&rdquo;</p>
      </div>
    </section>"""
        + f"""
    <section class="brt-section brt-section--alt" aria-labelledby="methoden-title">
      <div class="brt-container brt-fade-up">
        <h2 id="methoden-title" class="brt-h2">Which methods and processes does Beraterium use?</h2>
        <p class="brt-body">Our risk management process follows three clear phases: collect hazards, assess risks in euros, prioritise measures. No corporate framework — but a repeatable flow that SMEs, startups, and solo operators complete in 2–6 weeks.</p>
        <p class="brt-body">The methods are deliberately lean: structured workshops, guiding questions instead of spreadsheet monsters, assessment through multiple perspectives. The result is a risk picture you can act on — not a folder for the drawer.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="iso-title">
      <div class="brt-container brt-fade-up">
        <h2 id="iso-title" class="brt-h2">ISO 31000 and the Beraterium method</h2>
        <p class="brt-body">ISO 31000 describes the framework for risk management — context, identification, analysis, treatment. Beraterium is not an ISO certifier, but follows the same principles: collect systematically, assess transparently, prioritise measures by impact.</p>
        <p class="brt-body">The difference: we translate the standard into euros, timeframes, and concrete steps for businesses without their own risk office — understandable, practical, without bureaucracy.</p>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="matrix-title">
      <div class="brt-container brt-fade-up">
        <h2 id="matrix-title" class="brt-h2">Risks and opportunities in the matrix</h2>
        <p class="brt-body">Classic risk-opportunity matrices sort by likelihood and impact — often as traffic lights. Beraterium replaces colours with euros: damage × likelihood, minus existing measures. You immediately see which three risks would really become expensive.</p>
        <p class="brt-body">We do not treat opportunities as the opposite pole, but as measures with a positive effect — for example diversification that reduces concentration risk. Prioritisation stays the same: biggest lever first.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="services-link-title">
      <div class="brt-container brt-fade-up">
        <h2 id="services-link-title" class="brt-h2">Matching services by audience</h2>
        <p class="brt-body">The method is the same everywhere — scope adapts to your situation:</p>
        <ul class="brt-list-check">
          <li><a href="{pre}services/smb/">Risk management for SMEs →</a> — 6-week roadmap for mid-market businesses</li>
          <li><a href="{pre}services/startups/">Risk management for startups →</a> — 4-week check, investor-ready</li>
          <li><a href="{pre}services/solo/">Risk management for solo self-employed →</a> — 2-week compass with AI sparring partner</li>
        </ul>
      </div>
    </section>"""
        + faq_section_html(faq, title="Frequently asked questions about the method", section_id="faq", alt=True)
        + cta_band(pre, "Make your risks visible now", "In a free intro call, we show you what the method looks like for your business.", "Book a free intro call")
    )
    write(
        "method/index.html",
        shell(depth=1, title=method_title, description=method_desc,
              canonical="/method/", active_nav="method", main=main, json_ld=method_ld),
    )



def gen_nutzen_garantie() -> None:
    pre = "../"
    faq = [
        ("Ist das nicht sehr streng für euch?", "Ja, bewusst. Wir tragen das unternehmerische Risiko, nicht Sie. Deshalb gilt die Garantie nur für unsere Kernleistungen (Risikoanalyse-Pakete), nicht automatisch für jede Einzelleistung."),
        ("Wer legt die drei Kriterien fest?", "Sie und wir gemeinsam, im Kick-off vor Projektstart. Nicht wir allein und nicht Sie allein."),
        ("Sind weiche Kriterien nicht zu subjektiv?", "Deshalb formulieren wir das weiche Kriterium vorab genauso konkret wie die beiden harten: schriftlich, nachvollziehbar, nicht erst am Ende interpretiert."),
        ("Was zählt konkret als „erfüllt“?", "Genau das, was im Kick-off schriftlich festgehalten wurde. Keine nachträgliche Auslegung, keine Grauzonen."),
        ("Gilt die Garantie auch für Workshops oder Einzelberatung?", "Nur, wenn das ausdrücklich vereinbart wurde. Standardmäßig gilt sie für unsere Risikoanalyse-Pakete."),
        ("Was passiert, wenn ich als Kunde nicht mitwirke?", "Dann kann die Garantie entfallen. Sie setzt voraus, dass Sie Informationen liefern und an vereinbarten Terminen teilnehmen."),
    ]
    title = "Value guarantee: no value, no fee | Beraterium"
    desc = "Unsere Nutzen-Garantie: Drei vorab vereinbarte Kriterien entscheiden. Erfüllen wir auch nur eines nicht, erhalten Sie 100 % zurück."
    json_ld = page_schema(
        faq_page_schema(faq),
        speakable_webpage_schema("/benefit-guarantee/"),
    )
    main = (
        hero(pre, "IHR RISIKO LIEGT BEI UNS", "Kein Nutzen aus unserer Arbeit? Sie zahlen nichts.",
             "Bevor wir starten, legen wir gemeinsam fest, woran Sie den Erfolg unserer Arbeit erkennen. Erfüllen wir das am Ende nicht, erhalten Sie den vollen Betrag zurück, ohne Diskussion.",
             compact=True,
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a>')
        + guarantee_stat_row(
            [
                ("3 Kriterien", "Zwei harte, ein weiches – vorab gemeinsam festgelegt"),
                ("100 %", "Volle Erstattung, wenn auch nur eines fehlt"),
                ("14 Tage", "Rückerstattung ohne weitere Diskussion"),
            ],
            aria="Kernpunkte der Nutzen-Garantie",
        )
        + f"""
    <nav class="brt-anchor-nav" aria-label="Sprungnavigation auf dieser Seite" data-anchor-nav>
      <div class="brt-container brt-anchor-nav__inner">
        <p class="brt-anchor-nav__label">Auf dieser Seite</p>
        <div class="brt-anchor-nav__track">
          <ul class="brt-anchor-nav__list">
            <li><a class="brt-anchor-nav__link" href="#bedeutung">Bedeutung</a></li>
            <li><a class="brt-anchor-nav__link" href="#kriterien">Die 3 Kriterien</a></li>
            <li><a class="brt-anchor-nav__link" href="#vertrag">Vertraglich fixiert</a></li>
            <li><a class="brt-anchor-nav__link" href="#ablauf">Ablauf am Ende</a></li>
            <li><a class="brt-anchor-nav__link" href="#faq">FAQ</a></li>
          </ul>
        </div>
      </div>
    </nav>
    <section id="bedeutung" class="brt-section" aria-labelledby="bedeutung-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="bedeutung-title" class="brt-h2">Was bedeutet die Nutzen-Garantie?</h2>
          <p class="brt-body">Wenn Sie keinen Nutzen aus unserer Arbeit ziehen, zahlen Sie nichts. Im Vorgespräch legen wir gemeinsam mit Ihnen Zielgrößen fest, an denen wir klar messen können, ob unsere Arbeit etwas gebracht hat oder nicht.</p>
          <p class="brt-body">Das ist kein pauschales Versprechen, sondern eine Prüfung anhand konkreter, vorher vereinbarter Punkte. Diese Kriterien werden bereits vor Beginn der Arbeit vertraglich festgehalten, damit für beide Seiten transparent ist, welche Ergebnisse erzielt werden sollen.</p>
        </div>
        {split_media_html(IMG_NUTZEN_KRITERIEN, "Consultant and business owner agreeing the three success criteria for the value guarantee in a kick-off workshop", 1, contain=True)}
      </div>
    </section>"""
        + guarantee_rule_band(
            "„Kein messbarer Nutzen? Geld zurück.“",
            aria="Kernaussage Nutzen-Garantie",
        )
        + f"""
    <section id="kriterien" class="brt-section brt-section--alt" aria-labelledby="kriterien-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">KEIN PAUSCHAL-ERFOLG</p>
          <h2 id="kriterien-title" class="brt-h2">Drei Kriterien, gemeinsam festgelegt: zwei harte, ein weiches</h2>
          <p class="brt-body">Damit die Garantie eine echte Balance hat, arbeiten wir bewusst mit einer Mischung: zwei Kriterien, die sich zählen oder belegen lassen, und ein Kriterium, das beschreibt, wie Sie sich nach der Zusammenarbeit fühlen.</p>
        </header>
        <ul class="brt-guarantee-duo brt-stagger" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));">
          <li class="brt-card brt-card--guarantee brt-hover-lift">
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">{ICON_GUARANTEE_TARGET}</div>
              <span class="brt-guarantee__num" aria-hidden="true">01</span>
            </div>
            <p class="brt-tag">Hart</p>
            <h3 class="brt-h3">Relevante Risiken identifiziert</h3>
            <p class="brt-body">Mindestens 3 Risiken mit Schadenpotenzial über der vereinbarten Schwelle. Zählbar im Ergebnis-Report.</p>
          </li>
          <li class="brt-card brt-card--guarantee brt-hover-lift">
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">{ICON_GUARANTEE_TARGET}</div>
              <span class="brt-guarantee__num" aria-hidden="true">02</span>
            </div>
            <p class="brt-tag">Hart</p>
            <h3 class="brt-h3">Klare Priorisierung mit nächsten Schritten</h3>
            <p class="brt-body">Eine dokumentierte Top-Rangliste mit einem konkreten nächsten Schritt pro Risiko. Nachprüfbar im Dokument.</p>
          </li>
          <li class="brt-card brt-card--guarantee brt-hover-lift">
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">{ICON_GUARANTEE_SHIELD}</div>
              <span class="brt-guarantee__num" aria-hidden="true">03</span>
            </div>
            <p class="brt-tag">Weich</p>
            <h3 class="brt-h3">Spürbare Handlungsklarheit</h3>
            <p class="brt-body">Sie fühlen sich nach der Analyse sicherer und weniger im Blindflug. Vorab konkret formuliert, gemeinsam im Abschlussgespräch geprüft.</p>
          </li>
        </ul>
      </div>
    </section>
    <section id="vertrag" class="brt-section" aria-labelledby="vertrag-title">
      <div class="brt-container brt-fade-up">
        <h2 id="vertrag-title" class="brt-h2">Vertraglich transparent, bevor wir beginnen</h2>
        <p class="brt-body">Alle drei Kriterien stehen schwarz auf weiß im Angebot bzw. Vertrag, bevor das Projekt startet. Es gibt keine nachträgliche Verschiebung der Zielgrößen ohne Ihre Zustimmung, und keine Interpretation im Nachhinein.</p>
        <div class="brt-highlight-box" style="margin-top: var(--space-8);">
          <h3 class="brt-h3">Die Regel ist einfach</h3>
          <p class="brt-body">Sind am Ende alle drei Kriterien erfüllt, war die Zusammenarbeit erfolgreich. Fehlt auch nur eines, erstatten wir 100 % des vereinbarten Projektpreises. Sie tragen kein finanzielles Risiko bei der Beauftragung.</p>
        </div>
      </div>
    </section>
    <section id="ablauf" class="brt-section brt-section--alt" aria-labelledby="ablauf-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 id="ablauf-title" class="brt-h2">So läuft es am Projektende ab</h2>
        </header>
        <ul class="brt-step-cards brt-stagger">
          <li class="brt-step-card"><span class="brt-step-card__num">Schritt 1</span><h3 class="brt-h3">Gemeinsame Abschluss-Reflexion</h3><p class="brt-body">Zum vereinbarten Endergebnis prüfen wir mit Ihnen alle drei Kriterien anhand der schriftlich festgehaltenen Formulierung.</p></li>
          <li class="brt-step-card"><span class="brt-step-card__num">Schritt 2</span><h3 class="brt-h3">Klare Bewertung</h3><p class="brt-body">Ist auch nur eines nicht erfüllt, greift die Garantie. Keine Grauzonen, keine nachträgliche Auslegung.</p></li>
          <li class="brt-step-card"><span class="brt-step-card__num">Schritt 3</span><h3 class="brt-h3">Volle Erstattung</h3><p class="brt-body">Sie erhalten den vollen Betrag innerhalb von 14 Tagen zurück. Die rechtlichen Details stehen in unseren <a href="{pre}agb/">AGB, Abschnitt 7</a>.</p></li>
        </ul>
      </div>
    </section>"""
        + guarantee_pair_section(pre, current="nutzen")
        + guarantee_rich_cta(
            pre,
            "Let’s define your criteria together",
            "In the free intro call, we discuss how you’ll recognise whether our collaboration succeeded.",
            "Book your intro call →",
        )
        + faq_section_html(faq, title="Frequently asked questions about the value guarantee", section_id="faq", alt=True)
    )
    write(
        "benefit-guarantee/index.html",
        shell(depth=1, title=title, description=desc,
              canonical="/benefit-guarantee/", active_nav=None, main=main, json_ld=json_ld),
    )




def gen_relevanz_garantie() -> None:
    pre = "../"
    faq = [
        ("Sucht ihr nicht einfach, bis ihr etwas findet?", "Nein. Nur Risiken über der vorher gemeinsam festgelegten Schadensschwelle zählen als relevant im Sinne der Garantie. Alles darunter ändert an der Erstattung nichts."),
        ("Was, wenn wir unsere Risiken schon alle kennen?", "Dann ist das ein valides Ergebnis. Bestätigen wir nur bereits Bekanntes, ohne eine neue relevante Erkenntnis über der Schwelle, greift die Garantie: Sie zahlen nichts."),
        ("Wie hoch muss die Schadensschwelle sein?", "Das legen wir individuell im Kick-off fest, passend zu Ihrer Unternehmensgröße. Es gibt keine pauschale Zahl für alle."),
        ("Was, wenn ihr nur kleine Risiken findet?", "Liegt der Schaden unter der vereinbarten Schwelle, zählt das nicht als relevantes Risiko im Sinne der Garantie."),
        ("Kostet mich das Erstgespräch etwas?", "Nein. Das Erstgespräch ist immer kostenlos und unverbindlich, unabhängig von dieser Garantie."),
        ("Wie unterscheidet sich das von der Nutzen-Garantie?", "Die Relevanz-Garantie prüft, ob wir überhaupt ein relevantes Risiko finden. Die Nutzen-Garantie prüft, ob die gesamte Zusammenarbeit den vorab vereinbarten Mehrwert bringt."),
    ]
    title = "Relevanz-Garantie: Kein Risiko, kein Geld | Beraterium"
    desc = "Finden wir kein relevantes Risiko über der vereinbarten Schwelle, zahlen Sie nichts. Transparent vertraglich vereinbart, bevor wir starten."
    json_ld = page_schema(
        faq_page_schema(faq),
        speakable_webpage_schema("/relevanz-garantie/"),
    )
    main = (
        hero(pre, "IHR RISIKO LIEGT BEI UNS", "Kein relevantes Risiko gefunden? Sie zahlen nichts.",
             "Wir suchen nicht, um etwas abzurechnen. Finden wir kein Risiko über der gemeinsam vereinbarten Schwelle, erstatten wir den vollen Betrag, ohne Wenn und Aber.",
             compact=True,
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a>')
        + guarantee_stat_row(
            [
                ("Individuell", "Schadensschwelle im Kick-off gemeinsam festgelegt"),
                ("Risiko bei uns", "Kein relevanter Befund — wir tragen das Kostenrisiko"),
                ("100 %", "Volle Erstattung, wenn nichts Relevantes gefunden wird"),
            ],
            aria="Kernpunkte der Relevanz-Garantie",
        )
        + f"""
    <nav class="brt-anchor-nav" aria-label="Sprungnavigation auf dieser Seite" data-anchor-nav>
      <div class="brt-container brt-anchor-nav__inner">
        <p class="brt-anchor-nav__label">Auf dieser Seite</p>
        <div class="brt-anchor-nav__track">
          <ul class="brt-anchor-nav__list">
            <li><a class="brt-anchor-nav__link" href="#bedeutet">Was „relevant“ bedeutet</a></li>
            <li><a class="brt-anchor-nav__link" href="#suchen">Was wir gezielt suchen</a></li>
            <li><a class="brt-anchor-nav__link" href="#vertrag">Vertraglich fixiert</a></li>
            <li><a class="brt-anchor-nav__link" href="#faq">FAQ</a></li>
          </ul>
        </div>
      </div>
    </nav>
    <section id="bedeutet" class="brt-section" aria-labelledby="bedeutet-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="bedeutet-title" class="brt-h2">What &ldquo;relevant&rdquo; means</h2>
          <p class="brt-body">A risk is relevant if its potential damage reaches or exceeds the threshold we agree on together in the kick-off, for example a damage potential of more than EUR 10,000.</p>
          <p class="brt-body">We set this threshold individually with you, not as a blanket figure for every company. If the agreed analysis doesn&rsquo;t identify a single risk that meets this threshold, we refund you the full agreed project price.</p>
        </div>
        {split_media_html(IMG_RELEVANZ_SCHWELLE, "Consultant and business owner agreeing the damage threshold for relevant risks in a kick-off workshop", 1, contain=True)}
      </div>
    </section>"""
        + guarantee_rule_band(
            "„Wir finden kein relevantes Risiko? Geld zurück.“",
            aria="Kernaussage Relevanz-Garantie",
        )
        + guarantee_contrast_duo(
            left_tag="NO SMALL CHANGE",
            left_title="What we don’t do",
            left_id="not",
            left_paras=[
                "We’re not looking for any random, irrelevant risk just so our work gets paid. Findings below the agreed threshold don’t count as relevant under this guarantee.",
                "That matters so you lose the fear that we only search in order to bill you.",
            ],
            left_note_label="Outcome",
            left_note="If we find nothing relevant, the entire analysis costs you nothing.",
            right_tag="BLIND SPOTS",
            right_title="What we specifically look for",
            right_id="search",
            right_paras=[
                "We focus on risks that weren’t on your radar before, or that were internally dismissed as insignificant but turn out to be highly relevant.",
            ],
            right_note_label="Example",
            right_note="A risk internally treated as “long known and under control” turns out in the assessment to have damage potential well above the agreed threshold.",
            section_id="not",
        )
        + f"""
    <section id="vertrag" class="brt-section" aria-labelledby="vertrag-title">
      <div class="brt-container brt-fade-up">
        <h2 id="vertrag-title" class="brt-h2">Vertraglich festgehalten, bevor wir beginnen</h2>
        <p class="brt-body">Die Schadensschwelle und die Garantie selbst werden im Kick-off vereinbart und im Angebot bzw. Vertrag schriftlich festgehalten. Sie haben damit von Anfang an die Sicherheit, dass Sie nichts zahlen müssen, wenn wir kein relevantes Risiko finden.</p>
        <div class="brt-highlight-box" style="margin-top: var(--space-8);">
          <h3 class="brt-h3">Das Risiko liegt bei uns</h3>
          <p class="brt-body">Wir suchen nicht, um abzurechnen. Finden wir nichts Relevantes, tragen wir das finanzielle Risiko, nicht Sie. Die vollständigen Bedingungen stehen in unseren <a href="{pre}agb/">AGB, Abschnitt 7</a>.</p>
        </div>
      </div>
    </section>"""
        + guarantee_pair_section(pre, current="relevanz")
        + guarantee_rich_cta(
            pre,
            "Find out which risks you may be overlooking",
            "In the free intro call, you’ll learn how we set the damage threshold together with you.",
            "Book your intro call →",
        )
        + faq_section_html(faq, title="Frequently asked questions about the relevance guarantee", section_id="faq", alt=True)
    )
    write(
        "relevance-guarantee/index.html",
        shell(depth=1, title=title, description=desc,
              canonical="/relevance-guarantee/", active_nav=None, main=main, json_ld=json_ld),
    )




def gen_angebote() -> None:
    pre = "../"
    services_faq = [
        ("Which service fits me – startup, SME or solo?", "Startups (4 weeks) for founding teams, SMEs (6 weeks) for a full picture from around 10 employees, solo (2 weeks) for sole traders. We clarify what fits in the intro call."),
        ("What does risk management consulting cost at Beraterium?", "Scope depends on business size and chosen option. We discuss pricing transparently in the free intro call — before any proposal."),
        ("Is there a guarantee?", "Yes: double guarantee — relevance and value. No relevant risk found or no measurable value? Money back."),
        ("Do I need ISO certification or corporate methodology?", "No. Beraterium translates corporate methodology into practical steps for SMEs, startups, and solo operators — without bureaucracy overhead."),
    ]
    main = (
        hero(pre, "OUR SERVICES", "The right risk check for your situation",
             "Whether you are a founding team, mid-market business or solo self-employed: you get enterprise methodology, translated to your reality – with a clear outcome and double guarantee.",
             compact=True,
             actions=f'<a class="brt-btn" href="{pre}contact/">Book a free intro call</a>')
        + """
    <section class="brt-section" aria-labelledby="paths-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">WHO IT&rsquo;S FOR</p>
          <h2 id="paths-title" class="brt-h2">Choose your starting point</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-card--target brt-hover-lift">
            <h3 class="brt-h3">Startups</h3>
            <p class="brt-meta brt-meta--accent">The 4-week risk check</p>
            <p class="brt-body">For founding teams up to 10 people. Spot early which risks could slow your growth – before they get expensive.</p>
            <a class="brt-btn brt-btn--ghost" href="../services/startups/">View startup service →</a>
          </li>
          <li class="brt-card brt-card--target brt-card--featured brt-hover-lift">
            <h3 class="brt-h3">SME &amp; mid-market</h3>
            <p class="brt-meta brt-meta--accent">The 6-week clarity roadmap</p>
            <p class="brt-body">For businesses with 10–100+ employees. A complete risk picture, prioritised and valued in euros – plus HR analysis for culture and leadership.</p>
            <a class="brt-btn brt-btn--ghost" href="../services/smb/">View SME service →</a>
          </li>
          <li class="brt-card brt-card--target brt-hover-lift">
            <h3 class="brt-h3">Solo self-employed</h3>
            <p class="brt-meta brt-meta--accent">The 2-week risk compass</p>
            <p class="brt-body">For freelancers and sole traders. In two weeks you know where you are truly vulnerable – facilitated, with an AI sparring partner.</p>
            <a class="brt-btn brt-btn--ghost" href="../services/solo/">View solo service →</a>
          </li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="compare-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">AT A GLANCE</p>
          <h2 id="compare-title" class="brt-h2">What fits you?</h2>
          <p class="brt-body">Three audiences, one method — different scope and pace.</p>
        </header>
        <div class="brt-compare brt-fade-up">
          <div class="brt-compare__scroll">
            <table class="brt-compare__table">
              <caption class="brt-sr-only">Comparison of risk checks for startups, SMEs and solo self-employed</caption>
              <thead>
                <tr>
                  <th class="brt-compare__corner" scope="col"></th>
                  <th class="brt-compare__head" scope="col"><span class="brt-compare__head-icon" aria-hidden="true"><svg class="brt-compare__svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg></span><span class="brt-compare__head-title">Startups</span><span class="brt-compare__head-meta">4-week check</span></th>
                  <th class="brt-compare__head" scope="col"><span class="brt-compare__head-icon" aria-hidden="true"><svg class="brt-compare__svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg></span><span class="brt-compare__head-title">SME</span><span class="brt-compare__head-meta">6-week roadmap</span></th>
                  <th class="brt-compare__head" scope="col"><span class="brt-compare__head-icon" aria-hidden="true"><svg class="brt-compare__svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span><span class="brt-compare__head-title">Solo</span><span class="brt-compare__head-meta">2-week compass</span></th>
                </tr>
              </thead>
              <tbody>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span><span class="brt-compare__row-text">For whom</span></span></th><td>Founding teams up to 10</td><td>10–100+ employees</td><td>Solo entrepreneur</td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></span><span class="brt-compare__row-text">Duration</span></span></th><td><strong>approx. 4</strong> weeks</td><td><strong>approx. 6</strong> weeks</td><td><strong>approx. 2</strong> weeks</td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg></span><span class="brt-compare__row-text">Sessions</span></span></th><td>1–2 <span class="brt-compare__muted">(2h each)</span></td><td>2–3 <span class="brt-compare__muted">(2–3h each)</span></td><td>1 <span class="brt-compare__muted">(2–3h)</span></td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></span><span class="brt-compare__row-text">Outcome</span></span></th><td>prioritised risk picture</td><td>full risk portfolio + roadmap</td><td>personal risk picture</td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.65-8.58 3.91a2 2 0 0 1-1.66 0L3.18 12.65"/><path d="m22 17.65-8.58 3.91a2 2 0 0 1-1.66 0L3.18 17.65"/></svg></span><span class="brt-compare__row-text">Steps</span></span></th><td><span class="brt-compare__pill">1 / 2 / 3</span></td><td><span class="brt-compare__pill">1 / 2 / 3</span></td><td><span class="brt-compare__pill">1 / 2 / 3</span></td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg></span><span class="brt-compare__row-text">Guarantee</span></span></th><td><span class="brt-compare__check">Double</span></td><td><span class="brt-compare__check">Double</span></td><td><span class="brt-compare__check">Double</span></td></tr>
              </tbody>
              <tfoot>
                <tr>
                  <td class="brt-compare__corner"></td>
                  <td><a class="brt-btn brt-btn--ghost" href="../services/startups/">View service →</a></td>
                  <td><a class="brt-btn brt-btn--ghost" href="../services/smb/">View service →</a></td>
                  <td><a class="brt-btn brt-btn--ghost" href="../services/solo/">View service →</a></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </section>"""
        + steps_flow_section(en=True)
        + """
    <section class="brt-section brt-section--alt" aria-labelledby="hr-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">ADD-ON</p>
          <h2 id="hr-title" class="brt-h2">HR, culture &amp; leadership</h2>
          <p class="brt-body">Risks often sit in the team. Our HR modules make morale, leadership quality and culture visible – data-led, not gut feel.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">HR analysis via questionnaire</h3><p class="brt-body">Anonymous culture health check: satisfaction, communication, leadership, workload.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Leadership interviews</h3><p class="brt-body">In-depth 1:1 conversations with your leaders, transcribed and analysed for patterns.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Analysis &amp; recommendations</h3><p class="brt-body">From the data, concrete measures with priorities, sequence and timeline.</p></li>
        </ul>
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Pricing and scope depend on team size – we clarify what fits in the intro call.</p>
      </div>
    </section>"""
        + case_studies_section(pre, en=True)
        + guarantee(pre)
        + faq_section_html(services_faq, title="Frequently asked questions about our services", section_id="faq", alt=True)
        + cta_band(pre, "Not sure what fits?", "We clarify that in a free intro call – including a DIY guide you can use without us.")
    )
    write("services/index.html", shell(depth=1, title="Services – risk analysis for startups, SMEs & solo | Beraterium",
          description="Choose the right risk check: 4 weeks for startups, 6 weeks for SMEs, 2 weeks for solo self-employed. Plus HR analysis. With double guarantee.",
          canonical="/services/", active_nav="services", main=main,
          json_ld=page_schema(faq_page_schema(services_faq))))


def lp_shell(depth: int, slug: str, title: str, desc: str, du: bool, main: str) -> None:
    write(f"services/{slug}/index.html", shell(depth=depth, title=title, description=desc,
          canonical=f"/services/{slug}/", active_nav=f"services/{slug}", main=main))


def gen_lp_startups() -> None:
    pre = "../../"
    opts = [
        {"title": "Option A — Risk snapshot", "claim": "In 4 weeks you know where you stand.", "features": [
            "Kick-off (scope, value criteria)", "Facilitated risk analysis with team (1–2 sessions, 2h each)",
            "Hazard catalog startup edition (3 levels)", "Assessment: damage in euros + likelihood",
            "Inventory check + risk report (one-pager)"]},
        {"title": "Option B — Snapshot + measures sprint", "claim": "You know what&rsquo;s going on – and what to do.", "badge": "Popular", "featured": True,
         "extra": "Everything in A, plus:", "features": [
            "Measures sprint: top risks → concrete actions", "Assessment: impact, effort, feasibility per measure",
            "Quick-win list for this week", "Roadmap with owners &amp; timeline", "Founder wrap-up call"]},
        {"title": "Option C — Snapshot + measures + founder sparring", "claim": "We stay with you until the first measures take hold.",
         "extra": "Everything in B, plus:", "features": [
            "2 months founder sparring (2× monthly, 30 min.)", "Access to the Risk Radar community",
            "Expert introductions when needed", "Risk update after 2 months"]},
    ]
    main = (
        hero(pre, "RISK CHECK FOR STARTUPS", "In 4 weeks you know which risks slow your growth",
             "For founders and startup CEOs with 2–10 people. You build, you run – we make sure no blind spot holds you back.",
             split=True, media_label="Founding team during a risk check with Beraterium",
             media_src=IMG_ANGEBOT_STARTUPS_HERO,
             actions=f'<a class="brt-btn" href="{pre}contact/">Book a free intro call</a><a class="brt-btn brt-btn--outline" href="#optionen">See the 3 options →</a>')
        + """
    <section class="brt-section" aria-labelledby="problem-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">SOUND FAMILIAR?</p>
          <h2 id="problem-title" class="brt-h2">Risks? &ldquo;Yeah, sure – someday.&rdquo; But someday is usually too late.</h2>
          <p class="brt-body">You have a thousand things in your head at once: product, customers, hiring, cash. Risk analysis sounds like enterprise, like spreadsheet monsters, like bureaucracy – so you put it off.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The external problem</h3><p class="brt-body">You have no structured picture of your risks. What could cost you €30,000 tomorrow, you do not know today.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The internal problem</h3><p class="brt-body">Deep down you know: there are things you overlook. Key-person risk, cashflow gaps, legal pitfalls, technical debt.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The belief</h3><p class="brt-body">A founder who carries responsibility for their team should not guess where the biggest hazards lie. They should know.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="erstgespraech-title">
      <div class="brt-container brt-fade-up">
        <p class="brt-tag">GIVE FIRST, THEN OFFER</p>
        <h2 id="erstgespraech-title" class="brt-h2">Your free intro call: the method to do it yourself</h2>
        <p class="brt-body">In the intro call (approx. 30–45 min.) we show you how to run a risk analysis for your startup yourself. No sales pitch – real knowledge:</p>
        <ul class="brt-list-check">
          <li>The 3-level method: collect hazards → assess risks → prioritise measures</li>
          <li>Assessment logic for startups: estimate damage, even without history</li>
          <li>The 5 typical startup hazard areas: key person, cash, legal, tech debt, market</li>
          <li>Concrete guiding questions to bring in your co-founder team</li>
        </ul>
        <p class="brt-meta brt-meta--italic" style="margin-top: var(--space-6);">What you do not get: our full hazard catalog and facilitated delivery with analysis.</p>
      </div>
    </section>"""
        + pricing_cards(pre, opts)
        + guarantee(pre, "Your risk is on us")
        + faq_section([
            ("How much time does it cost me?", "About 2 hours per session, 1–2 sessions plus kick-off in total. We handle the rest."),
            ("Is it worth it this early?", "Especially early: a key-person or cash risk can stop a young startup completely."),
            ("What if there are only two of us?", "No problem. We facilitate so even a small founding team reaches a realistic assessment."),
            ("Do I get something to show investors?", "You get a prioritised risk report as a one-pager. Honest, not polished."),
        ], alt=True)
        + cta_band(pre, "Ready to know your biggest risks?",
                   "Book an intro call – free, no sales pitch. You leave with a DIY guide, however you decide.")
    )
    lp_shell(2, "startups", "Risk management for startups – 4-week risk check | Beraterium",
             "Key-person, cash, legal and tech risks under control: in 4 weeks you know your biggest risks as a founder – facilitated, valued in euros, with guarantee.", True, main)


def gen_lp_kmu() -> None:
    pre = "../../"
    opts = [
        {"title": "Option A — Analysis only", "claim": "You get clarity. We deliver the picture.", "features": [
            "Kick-off with leadership (goals, scope, value criteria)", "Facilitated risk analysis with team (2–3 sessions, 2–3h each)",
            "Full hazard catalog (3 levels, industry-tailored)", "Assessment: damage in euros + likelihood",
            "Inventory capture + risk portfolio report (prioritised)"]},
        {"title": "Option B — Analysis + roadmap", "claim": "Clarity AND a concrete plan.", "badge": "Popular", "featured": True,
         "extra": "Everything in A, plus:", "features": [
            "Measures workshop for top risks", "Assessment per measure: impact, cost-effectiveness, feasibility",
            "Implementation roadmap with timeline &amp; owners", "Leadership wrap-up session"]},
        {"title": "Option C — Analysis + roadmap + implementation support", "claim": "We stay involved until measures take hold.",
         "extra": "Everything in B, plus:", "features": [
            "3 months implementation support (monthly check-ins)", "Access to the Risk Radar community (vetted experts)",
            "Coordination of specialists for complex measures", "Quarterly review (risk update + progress)"]},
    ]
    main = (
        hero(pre, "RISK ANALYSIS FOR SME", "Which risks actually cost your business money?",
             "For managing directors and owners of SMEs with 10 to 100+ employees. In around 6 weeks you receive a complete risk picture, valued in euros – plus a concrete roadmap.",
             split=True, media_label="Leadership of a mid-market business during risk analysis",
             media_src=IMG_ANGEBOT_KMU_HERO,
             actions=f'<a class="brt-btn" href="{pre}contact/">Book a free intro call</a><a class="brt-btn brt-btn--outline" href="#optionen">See the 3 options →</a>')
        + """
    <section class="brt-section" aria-labelledby="problem-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">THE COSTLY UNCERTAINTY</p>
          <h2 id="problem-title" class="brt-h2">You know risks are lurking somewhere. But which ones are expensive?</h2>
          <p class="brt-body">Which risk could cost you €50,000, €200,000 or more next year? You run a business with employees, customers, processes and responsibility – and you sense: there is something you are overlooking.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The external problem</h3><p class="brt-body">You do not have a complete picture of your risks. Classic methods are built for enterprises – complex, theoretical, bureaucratic.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The internal problem</h3><p class="brt-body">Gut feel says &lsquo;something is there&rsquo; – but you cannot name it, prioritise it or put a number on it.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The belief</h3><p class="brt-body">Anyone who carries responsibility for employees and customers should know where the biggest risks lie. Not someday. Now.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="erstgespraech-title">
      <div class="brt-container brt-fade-up">
        <p class="brt-tag">GIVE FIRST, THEN OFFER</p>
        <h2 id="erstgespraech-title" class="brt-h2">Your free intro call: the full method, explained openly</h2>
        <p class="brt-body">In approx. 45–60 minutes we show you how to run a structured risk analysis yourself. You receive:</p>
        <ul class="brt-list-check">
          <li>The 3-level approach explained (hazards → risks → measures)</li>
          <li>The assessment logic (scenario, damage in euros, likelihood, inventory)</li>
          <li>The questioning technique to bring in your team</li>
          <li>A concrete starting point: the 5 hazard areas to work through first</li>
        </ul>
      </div>
    </section>"""
        + pricing_cards(pre, opts)
        + guarantee(pre, "Your risk is zero")
        + faq_section([
            ("How much time does it tie up in the team?", "2–3 hours per session, 2–3 sessions plus kick-off in total. We facilitate efficiently."),
            ("Is this suitable for family businesses too?", "Especially so. Topics such as succession or key people become visible in a structured way."),
            ("How are you different from an audit?", "We do not check past numbers – we make your future risks tangible."),
            ("Do we get a document we can present?", "Yes, a risk portfolio report you can share with your board, bank or team."),
        ], alt=True)
        + cta_band(pre, "Get clarity – before a risk hits",
                   "Book an intro call – free, no obligation. You leave with a DIY guide, however you decide.")
    )
    lp_shell(2, "smb", "Risk management for SME – 6-week clarity roadmap | Beraterium",
             "A complete risk picture for your SME: prioritised, valued in euros, with a measures roadmap. Practical, not enterprise bureaucracy. With double guarantee.", False, main)


def gen_lp_solo() -> None:
    pre = "../../"
    opts = [
        {"title": "Option A — Solo risk check", "claim": "In 2 weeks you know where you are vulnerable.", "features": [
            "Kick-off (situation, scope, value criteria)", "Facilitated risk analysis (1 session, 2–3h) with 2 facilitators + AI sparring partner",
            "Hazard catalog solo edition (3 levels)", "Assessment: damage in euros + likelihood",
            "Inventory check + risk report (1–2 pages)"]},
        {"title": "Option B — Risk check + action plan", "claim": "You know what&rsquo;s going on – and what you can do.", "badge": "Popular", "featured": True,
         "extra": "Everything in A, plus:", "features": [
            "Measures session (top risks → concrete steps)", "Quick-win list for this week",
            "Prioritised roadmap: what first, what can wait?", "Resource check: what can you handle alone, where do you need help?"]},
        {"title": "Option C — Risk check + measures + implementation sparring", "claim": "We stay with you until you are set up securely.",
         "extra": "Everything in B, plus:", "features": [
            "6 weeks sparring (3× 30 min., every 2 weeks)", "Access to the Risk Radar community",
            "Expert introductions for specific needs", "Risk update after 6 weeks"]},
    ]
    main = (
        hero(pre, "RISK COMPASS FOR SOLO SELF-EMPLOYED", "You are your business. Do you know where you are vulnerable?",
             "For freelancers, sole traders and solo self-employed. In 2 weeks you know which risks would hit you hardest – not to create fear, but so you can decide freely.",
             split=True, media_label="Solo self-employed person during a risk compass with Beraterium",
             media_src=IMG_ANGEBOT_SOLO_HERO,
             actions=f'<a class="brt-btn" href="{pre}contact/">Book a free intro call</a><a class="brt-btn brt-btn--outline" href="#optionen">See the 3 options →</a>')
        + """
    <section class="brt-section" aria-labelledby="problem-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">KNOW THAT FEELING?</p>
          <h2 id="problem-title" class="brt-h2">If you go down, everything stops. If a client leaves, your livelihood wobbles.</h2>
          <p class="brt-body">There is no colleague to catch you. And &lsquo;risk management&rsquo; has been on your &lsquo;should really do that&rsquo; list forever.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The external problem</h3><p class="brt-body">You have no overview of which risks truly threaten your business. Classic risk analysis feels like it is for enterprises with 500 people.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The internal problem</h3><p class="brt-body">You worry – about absence, dependencies, things you overlook. But as a solo, you are alone with those thoughts.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">The belief</h3><p class="brt-body">Anyone who carries their own business has the right to know where the biggest hazards lie. So they can decide freely.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="moderatoren-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <h3 id="moderatoren-title" class="brt-h3">Why two facilitators and an AI sparring partner?</h3>
        <p class="brt-body">As a solo you have no team bringing different perspectives. We replace that: two facilitators who structure and challenge, plus an AI sparring partner for statistical experience-based input.</p>
      </div>
    </section>"""
        + pricing_cards(pre, opts)
        + guarantee(pre, "Zero risk for you")
        + faq_section([
            ("Is it worth it when it is just me?", "Especially then. If you go down, there is no buffer."),
            ("How much time does it cost me?", "One session of 2–3 hours plus a short kick-off. That is it."),
            ("I find risk topics uncomfortable – will this be a fear session?", "No. It is about clarity and decisive action, not fear."),
            ("What does the AI sparring partner do for me?", "It provides statistical estimates and experience-based input so your assessment does not rely only on gut feel."),
        ], alt=True)
        + cta_band(pre, "Get clarity on your risks",
                   "Book an intro call – 30 minutes, free, no pressure. We explain our DIY method and you decide afterwards in your own time.")
    )
    lp_shell(2, "solo", "Risk management for self-employed – 2-week risk compass | Beraterium",
             "You are your business. In 2 weeks you know which risks would hit you hardest – facilitated, with AI sparring partner and double guarantee.", True, main)


def gen_risikoradar() -> None:
    pre = "../"
    main = (
        hero(pre, "OUR NETWORK", "Risk Radar – solutions are not built in isolation",
             "A protected space of vetted, trusted experts. Not a loose contact pool, but a working network where disciplines work together – so your analysis turns into real implementation.")
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="umsetzung-title">
      <div class="brt-container brt-fade-up">
        <h2 id="umsetzung-title" class="brt-h2">Not analysis to file away – solutions to act on</h2>
        <p class="brt-body">The analysis creates clarity. The real value comes in implementation. That is exactly where Risk Radar comes in: we bring the right people together and make sure measures work together sensibly. Beraterium remains your single point of contact throughout.</p>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="ways-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">YOU DECIDE</p>
          <h2 id="ways-title" class="brt-h2">How should implementation work?</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Implement yourself</h3><p class="brt-body">With your own team – for organisational or straightforward measures.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">With your service providers</h3><p class="brt-body">Continue with trusted partners – for established business relationships.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">We coordinate</h3><p class="brt-body">One dedicated contact, one face to the customer. We bring the right experts together.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="special-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">NOT A LOOSE CONTACT POOL</p>
          <h2 id="special-title" class="brt-h2">Trust, quality, collaboration</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Access by referral or application only</h3><p class="brt-body">Not everyone gets in. That protects the quality.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Vetted experts</h3><p class="brt-body">Trusted specialists in organisation, processes, technology &amp; security, IT &amp; systems, and people &amp; behaviour.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">One point of contact</h3><p class="brt-body">No coordination overhead, no debates about responsibilities – results instead of administration.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="dual-cta">
      <div class="brt-container brt-two-col brt-two-col--cta brt-fade-up">
        <div>
          <h3 class="brt-h3">Looking for implementation support?</h3>
          <p class="brt-body">After your risk analysis, we can assemble exactly the experts that fit your top risks – already vetted, no Google roulette.</p>
          <p class="brt-section__cta">
            <a class="brt-btn brt-btn--outline" href="../contact/">Book a free intro call →</a>
          </p>
        </div>
        <div>
          <h3 class="brt-h3">Are you an expert and want to contribute?</h3>
          <p class="brt-body">Risk Radar grows through referral and application. If you value quality, trust and genuine collaboration, we would love to hear from you.</p>
          <p class="brt-section__cta">
            <a class="brt-btn brt-btn--outline" href="../contact/">Apply as an expert →</a>
          </p>
        </div>
      </div>
    </section>"""
        + faq_section_html([
            ("What is Risk Radar?", "Risk Radar is the protected expert network behind Beraterium — vetted specialists who implement measures from your risk analysis."),
            ("How do I get access to Risk Radar?", "As a Beraterium client, you receive access. Experts join through referral or application — not an open forum."),
        ], title="Frequently asked questions about Risk Radar", section_id="faq", alt=True)
        + cta_band(pre, "From clarity to decisive action", "You decide how implementation runs – we make sure it works.")
    )
    risk_radar_faq = [
        ("What is Risk Radar?", "Risk Radar is the protected expert network behind Beraterium — vetted specialists who implement measures from your risk analysis."),
        ("How do I get access to Risk Radar?", "As a Beraterium client, you receive access. Experts join through referral or application — not an open forum."),
    ]
    write("risk-radar/index.html", shell(depth=1, title="Risk Radar – The expert network behind Beraterium | Beraterium",
          description="Risk Radar is a protected network of vetted experts. Implement measures with one point of contact instead of coordination chaos.",
          canonical="/risk-radar/", active_nav="risk-radar", main=main,
          json_ld=page_schema(faq_page_schema(risk_radar_faq))))


BLINDSPOT_FAQ = [
    ("What is the Blindspot Quick Check?",
     "The Blindspot Quick Check is a free online self-assessment by Beraterium. In 10 to 15 questions you check where your business is vulnerable — around key people, technology and day-to-day operations. You get your results immediately, no sign-up required."),
    ("What is the difference from Stage 1 of the risk analysis?",
     "The Quick Check on this page is a simplified self-assessment: 15 selected hazard areas, traffic-light rating, no conversation. Stage 1 of the risk analysis is a moderated process with an industry-specific questionnaire, damage scenarios in euros, likelihood, inventory and a prioritised risk portfolio — typically in a joint session."),
    ("How long does the Blindspot Quick Check take?",
     "About 10 minutes. Depending on your audience choice you answer 10 to 15 short 'What happens if …' questions and see your results right afterwards."),
    ("Is the Blindspot Quick Check free?",
     "Yes, the check is completely free and can be used without registration. Optionally, you can have the results sent to you as a PDF report by email."),
    ("Does the Quick Check replace a full risk analysis?",
     "No. The Quick Check covers a selection from more than 100 hazard areas of our 3-level hazard catalog. A good result does not mean all risks are ruled out — that is what Beraterium's Stage 1 and Stage 2 risk analysis is for."),
    ("Who is the Blindspot Quick Check for?",
     "For solo self-employed professionals, founders and startups, and small and medium-sized enterprises (SMEs). The questions adapt to your choice: solo self-employed answer 10 questions, founders and SMEs 15 each."),
    ("What happens to my answers?",
     "The evaluation runs directly in your browser. You only provide personal data if you request the optional PDF report — in that case our privacy policy applies. We do not store IP addresses."),
]


def gen_tools_index() -> None:
    pre = "../"
    main = (
        hero(
            pre,
            "FREE TOOLS",
            "Tools: check your risks yourself — in minutes, not weeks",
            "Compact self-assessments drawn from the Beraterium method. No substitute for a full risk analysis, but an honest first look at your blind spots.",
            compact=True,
        )
        + f"""
    <section class="brt-section" aria-labelledby="tools-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">TEST YOURSELF</p>
          <h2 id="tools-title" class="brt-h2">Which tools are available?</h2>
          <p class="brt-body">One tool right now — more are in the works. All tools are based on our 3-level hazard catalog with more than 100 hazard areas.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Blindspot Check</h3>
            <p class="brt-body">The free quick check: 10–15 'What happens if …' questions about key people, technology and day-to-day operations. Immediate results with traffic-light status and concrete first steps.</p>
            <p class="brt-section__cta"><a class="brt-btn" href="{pre}tools/blindspot-check/">Start the Blindspot Check →</a></p>
          </li>
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Risk Radar</h3>
            <p class="brt-body">Not a self-assessment, but the next step: our protected expert network for implementing the measures from your risk analysis.</p>
            <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}risk-radar/">Discover Risk Radar →</a></p>
          </li>
        </ul>
      </div>
    </section>"""
        + cta_band(pre, "Prefer to talk to an expert directly?", "In a free intro call we clarify which risks really matter for your business.")
    )
    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Tools", "item": f"{SITE_URL}/tools/"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    write("tools/index.html", shell(
        depth=1,
        title="Tools – Free risk checks | Beraterium",
        description="Free tools by Beraterium: use the Blindspot Check to spot blind spots and business risks in 10 minutes – no sign-up, immediate results.",
        canonical="/tools/",
        active_nav="tools",
        main=main,
        json_ld=page_schema(breadcrumb_ld),
    ))


def gen_blindspot_check() -> None:
    pre = "../../"
    canonical = "/tools/blindspot-check/"
    config_json = blindspot_config_json(
        locale="en",
        submit_url="https://script.google.com/macros/s/AKfycbxOVMHI01byul3j0QqJ-MGgDdnw9l_HMKwgoyZlHteAftWo7rnGN7I-R9r77XJvCqmSDQ/exec",
        report_url="https://script.google.com/macros/s/AKfycbxOVMHI01byul3j0QqJ-MGgDdnw9l_HMKwgoyZlHteAftWo7rnGN7I-R9r77XJvCqmSDQ/exec",
        booking_url=f"{pre}contact/",
        privacy_url=f"{pre}privacy/",
    )
    main = (
        hero(
            pre,
            "FREE SELF-ASSESSMENT",
            "Blindspot Quick Check: where is your business vulnerable?",
            "Answer 10–15 short 'What happens if …' questions and get immediate results: traffic-light status, a risk profile by category and concrete first steps for your most critical points. The Quick Check is the simplified online version — Stage 1 of the risk analysis goes much deeper.",
            compact=True,
            actions='<a class="brt-btn brt-btn--on-dark brt-btn--lg" href="#brt-blindspot">Start the check now</a>',
        )
        + f"""
    <section class="brt-section" aria-labelledby="why-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="why-title" class="brt-h2">Why a Blindspot Quick Check?</h2>
          <p class="brt-body">Most businesses don't fail because of the risks they know — they fail because of the ones they never looked at. The Blindspot Quick Check makes these blind spots visible: it examines 15 of the more than 100 hazard areas from our 3-level hazard catalog, spread across <strong>People</strong>, <strong>Technology</strong> and <strong>Operations</strong>.</p>
          <p class="brt-body">Each question describes a concrete scenario. You rate how critical it would be for you — and whether you have already prepared measures. The result is your personal risk profile with a traffic-light status per question.</p>
        </div>
        {split_media_html(IMG_BLINDSPOT_WARUM, "Blindspot Check reveals overlooked business risks in people, technology and operations", 2, contain=True)}
      </div>
    </section>
    <section id="check" class="brt-section brt-section--alt" aria-labelledby="check-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">INTERACTIVE CHECK</p>
          <h2 id="check-title" class="brt-h2">The Blindspot Quick Check</h2>
          <p class="brt-body brt-section__lede">Start the simplified self-test here — online, in about 10 minutes, no appointment. It does not replace Stage 1 of the risk analysis, but gives you an honest first look at typical blind spots.</p>
        </header>
        <div id="brt-blindspot" class="bqc-widget brt-fade-up" aria-live="polite"></div>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="compare-title">
      <div class="brt-container brt-fade-up">
        <header class="brt-section__header">
          <p class="brt-tag">TWO FORMATS</p>
          <h2 id="compare-title" class="brt-h2">Quick Check vs. Stage&nbsp;1 risk analysis</h2>
        </header>
        <ul class="brt-guarantee-duo brt-stagger">
          <li class="brt-card">
            <h3 class="brt-h3">Blindspot Quick Check (this page)</h3>
            <ul class="brt-list">
              <li>Online self-test, start immediately</li>
              <li>10–15 selected questions from the hazard catalog</li>
              <li>Traffic-light rating and category profile</li>
              <li>No conversation, no detailed industry tailoring</li>
              <li>Free and no sign-up</li>
            </ul>
          </li>
          <li class="brt-card">
            <h3 class="brt-h3">Stage&nbsp;1 risk analysis (moderated process)</h3>
            <ul class="brt-list">
              <li>Joint session with Beraterium</li>
              <li>Industry-specific questionnaire (15–16 hazard fields)</li>
              <li>Damage scenarios in euros, likelihood, inventory</li>
              <li>Prioritised risk portfolio instead of isolated topics</li>
              <li>Foundation for Stage&nbsp;2 with action plan</li>
            </ul>
            <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}services/">Services &amp; stages →</a></p>
          </li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="method-title">
      <div class="brt-container brt-fade-up">
        <header class="brt-section__header">
          <p class="brt-tag">CORE IDEA</p>
          <h2 id="method-title" class="brt-h2">How the risk analysis works — and what the Quick Check takes from it</h2>
        </header>
        <p class="brt-body">The Beraterium method uses a structured hazard catalog: for each relevant field we clarify the guiding question, damage scenario, possible damage in euros, likelihood and <em>inventory</em> — what you already have to mitigate the risk. The result is not a collection of isolated topics, but a comparable risk portfolio with clear priorities.</p>
        <p class="brt-body">The Blindspot Quick Check uses the same logic in a strongly simplified form: concrete 'What happens if …' scenarios, your assessment of criticality and whether preparation exists. It shows direction and blind spots — Stages 1 and 2 of the risk analysis deepen and prioritise systematically across the full catalog. More on the method: <a href="{pre}method/">Beraterium method</a>.</p>
      </div>
    </section>
    <section class="brt-section brt-section--narrow" aria-labelledby="limits-title">
      <div class="brt-container brt-fade-up">
        <h2 id="limits-title" class="brt-h2">What the Quick Check does — and what it doesn't</h2>
        <p class="brt-body">The Blindspot Quick Check is a quick test, not a full risk analysis. It looks at selected, particularly common blind spots. An unremarkable result does not mean the remaining hazard areas hold no risks. If you want certainty, take the next step: <a href="{pre}services/">Stage 1 of the risk analysis</a> examines all relevant fields of the hazard catalog — including prioritisation; Stage 2 delivers the action plan.</p>
      </div>
    </section>""".replace("{pre}", pre)
        + faq_section_html(
            BLINDSPOT_FAQ,
            title="Frequently asked questions about the Blindspot Quick Check",
            section_id="faq",
            alt=True,
        )
        + cta_band(pre, "Red points in your results?", "In a free intro call we discuss your most critical blind spots and what to tackle first.")
    )
    webapp_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Blindspot Check",
            "url": f"{SITE_URL}{canonical}",
            "description": "Free online self-assessment: in 10–15 questions, solo self-employed professionals, founders and SMEs check where their business is vulnerable. Immediate results with traffic-light status and first steps.",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "browserRequirements": "Requires JavaScript",
            "inLanguage": "en",
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "provider": {"@id": f"{SITE_URL}/#organization"},
        },
        ensure_ascii=False,
        indent=2,
    )
    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Tools", "item": f"{SITE_URL}/tools/"},
                {"@type": "ListItem", "position": 3, "name": "Blindspot Check", "item": f"{SITE_URL}{canonical}"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    extra_css = f'\n  <link rel="stylesheet" href="{pre}css/brt-blindspot.css?v={BRT_ASSET_VERSION}">'
    extra_scripts = (
        f'\n<script type="application/json" id="brt-blindspot-config">{config_json}</script>'
        f'\n<script src="{pre}js/brt-blindspot.js?v={BRT_ASSET_VERSION}"></script>'
    )
    write("tools/blindspot-check/index.html", shell(
        depth=2,
        title="Blindspot Check – Free business risk self-test | Beraterium",
        description="Blindspot Check: find out in 10 minutes, for free, where your business is vulnerable. 10–15 questions, immediate results, concrete first steps.",
        canonical=canonical,
        active_nav="tools/blindspot-check",
        main=main,
        json_ld=page_schema(faq_page_schema(BLINDSPOT_FAQ), webapp_ld, breadcrumb_ld),
        extra_css=extra_css,
        extra_scripts=extra_scripts,
    ))


def gen_blog() -> None:
    pre = "../"
    posts = load_blog_posts()
    cards = []
    for i, p in enumerate(posts):
        card = blog_card_html(p, 1, featured=(i == 0))
        cards.append(card)
    if not cards:
        cards = [
            """        <li class="brt-card brt-card--blog">
          <div class="brt-card__body">
            <p class="brt-body">No published articles yet. Please check back soon.</p>
          </div>
        </li>"""
        ]
    main = (
        hero(
            pre,
            "BERATERIUM BLOG",
            "Risk, made understandable",
            "Practical insights on risk management, business risks, HR and leadership – without consultant jargon. For people who want to lead their business safely into the future.",
            compact=True,
        )
        + f"""
    <section class="brt-section" aria-labelledby="blog-grid">
      <div class="brt-container">
        <header class="brt-section__header brt-section__header--row brt-fade-up">
          <div>
            <h2 id="blog-grid" class="brt-h2">All articles</h2>
            <p class="brt-body">{len(posts)} articles on risk management, leadership and business practice.</p>
          </div>
        </header>
        <nav class="brt-blog-filters" aria-label="Categories">
          {blog_filters_html()}
        </nav>
        <ul class="brt-blog-grid brt-stagger" id="blog-grid-list">
{chr(10).join(cards)}
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="newsletter-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <h2 id="newsletter-title" class="brt-h3">Don't miss risk insights</h2>
        <p class="brt-body">One concise update per month – practical, free, unsubscribe any time.</p>
        <form class="brt-form" action="#" method="post" style="max-width: 28rem; margin-inline: auto;">
          <label>Email
            <input type="email" name="email" required placeholder="you@email.com" autocomplete="email">
          </label>
          <button class="brt-btn" type="submit">Subscribe</button>
          <p class="brt-meta">By subscribing, you agree to processing in accordance with our <a href="{pre}privacy/">privacy policy</a>.</p>
        </form>
      </div>
    </section>"""
    )
    write(
        "blog/index.html",
        shell(
            depth=1,
            title="Blog – Risk management, HR & mid-market explained clearly | Beraterium",
            description="Practical insights on risk management, business risks, HR and leadership – for startups, SMEs and solo self-employed. Clear, honest, immediately applicable.",
            canonical="/blog/",
            active_nav="blog",
            main=main,
        ),
    )


def gen_blog_singles() -> None:
    posts = load_blog_posts()
    all_by_slug = {p.slug: p for p in posts}
    team = team_by_slug(load_team_members())
    for post in posts:
        pre = "../../"
        author = team.get(post.author)
        author_name = author.name if author else "Beraterium"
        author_img = ""
        if author:
            img = img_html(author.image, author.image_alt, 2, css_class="brt-article__author-img", aspect="1/1")
            if "brt-image-placeholder" not in img:
                author_img = img
        hero_img = img_html(post.hero_image, post.hero_alt, 2, hero=True, css_class="brt-article__hero-img", aspect="16/9")
        hero_media = (
            f'<figure class="brt-article__hero-media">{hero_img}</figure>'
            if "brt-image-placeholder" not in hero_img
            else f'<div class="brt-article__hero-media">{hero_img}</div>'
        )
        sticky_title = post.title if len(post.title) <= 72 else post.title[:69].rsplit(" ", 1)[0] + "…"
        progress_block = """
        <div class="brt-article__progress" aria-hidden="true" data-article-progress>
          <span class="brt-article__progress-bar"></span>
        </div>"""
        sticky_bar_block = f"""
      <div class="brt-article__sticky-bar" data-article-sticky-bar hidden>
        <div class="brt-container brt-article__sticky-inner">
          <span class="brt-tag brt-tag--small">{escape(post.category)}</span>
          <p class="brt-article__sticky-title">{escape(sticky_title)}</p>
        </div>
{progress_block}
      </div>"""
        youtube_block = article_youtube_embed_html(
            post.youtube_id,
            post.title,
            f"https://en.beraterium.de/blog/{post.slug}/",
        )
        author_col = article_author_sidebar_html(author, author_name, post.author, 2, pre)
        author_meta = author_name_link_html(post.author, author_name, pre)
        aside_block = article_sidebar_html(post.toc, post.category, 2, pre)
        lead_block = (
            f'          <p class="brt-lead brt-article__lead">{escape(post.lead)}</p>\n'
            if post.lead
            else ""
        )
        back_top_block = """
    <button type="button" class="brt-article__back-top" aria-label="Scroll back to top" data-article-back-top hidden>
      <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M10 4l-6 6h4v6h4v-6h4L10 4z" fill="currentColor"/></svg>
    </button>"""
        faq_block = article_faq_section_html(post.faq)
        related_cards = []
        for slug in post.related_slugs:
            rel_post = all_by_slug.get(slug)
            if rel_post:
                related_cards.append(blog_card_html(rel_post, 2))
        if not related_cards:
            for rel_post in posts:
                if rel_post.slug != post.slug and rel_post.category == post.category:
                    related_cards.append(blog_card_html(rel_post, 2))
                if len(related_cards) >= 3:
                    break
        related_block = ""
        if related_cards:
            related_block = f"""
    <section class="brt-section" aria-labelledby="related-posts">
      <div class="brt-container">
        <h2 id="related-posts" class="brt-h2">More articles</h2>
        <ul class="brt-blog-grid brt-stagger">
{chr(10).join(related_cards[:3])}
        </ul>
      </div>
    </section>"""
        author_box = f"""
    <section class="brt-section brt-section--alt" aria-labelledby="author-box">
      <div class="brt-container brt-article__author brt-fade-up">
        {author_img}
        <div>
          <h2 id="author-box" class="brt-h3">{author_name_link_html(post.author, author_name, pre, css_class="brt-article__author-link brt-article__author-link--heading")}</h2>
          <p class="brt-body">{escape(author.teaser_bio if author else "")}</p>
          <a class="brt-btn brt-btn--ghost" href="{pre}team/">Our team →</a>
        </div>
      </div>
    </section>"""
        main = f"""
    <article class="brt-article" data-article>
{sticky_bar_block}
      <div class="brt-container brt-article__hero-split brt-fade-up" data-article-hero>
        <div class="brt-article__hero-copy">
          <a class="brt-skip-link brt-skip-link--article" href="#article-body">Skip to article text</a>
          <h1 class="brt-h1 brt-article__title">{escape(post.title)}</h1>
          <p class="brt-article__meta brt-meta">
            <span class="brt-article__category">{escape(post.category)}</span> · {author_meta} · <time datetime="{post.date.isoformat()}">{format_date_en(post.date)}</time> · approx. {post.reading_time_min} min read
          </p>
        </div>
        {hero_media}
      </div>
      <div class="brt-container brt-article__layout brt-fade-up">
{author_col}
        <div class="brt-article__main">
{lead_block}          <div class="brt-article__body" id="article-body" tabindex="-1">
{post.body_html}
          </div>
        </div>
{aside_block}
      </div>
{youtube_block}
    </article>
{back_top_block}
{faq_block}
{author_box}
    <section class="brt-cta-band brt-cta-band--dark brt-section" aria-labelledby="article-cta">
      <div class="brt-container brt-cta-band__inner brt-fade-up">
        <h2 id="article-cta" class="brt-h2 brt-h2--on-dark">Clarify risks in your business?</h2>
        <p class="brt-body brt-body--on-dark">Book a free intro call – 30 minutes, no obligation.</p>
        <a class="brt-btn brt-btn--on-dark" href="{pre}contact/">Book a free intro call</a>
      </div>
    </section>
{related_block}"""
        json_ld = blog_posting_schema(post, author)
        write(
            f"blog/{post.slug}/index.html",
            shell(
                depth=2,
                title=f"{post.title} | Beraterium Blog",
                description=post.excerpt,
                canonical=f"/blog/{post.slug}/",
                active_nav="blog",
                main=main,
                json_ld=json_ld,
            ),
        )


def gen_home_analyse() -> None:
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    media = img_html(
        IMG_HOME_ANALYSE,
        "Unternehmer verschafft sich Klarheit über die größten Risiken",
        0,
        aspect="4/3",
    )
    old = """      <div class="brt-split__media brt-fade-up" style="--fade-delay: 120ms">
        <div
          class="brt-image-placeholder"
          role="img"
          aria-label="Unternehmer verschafft sich Klarheit über die größten Risiken">
          <span class="brt-image-placeholder__label">Analyse-Situation</span>
        </div>
      </div>"""
    new = f"""      <div class="brt-split__media brt-fade-up" style="--fade-delay: 120ms">
        {media}
      </div>"""
    if old not in html:
        print("  skip index.html home analyse (pattern not found)")
        return
    path.write_text(html.replace(old, new), encoding="utf-8")
    print("  updated index.html home analyse")


def gen_home_team() -> None:
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    start = "  <!-- HOME_TEAM_START -->"
    end = "  <!-- HOME_TEAM_END -->"
    section = home_team_section_html(0)
    if start in html and end in html:
        before = html.split(start)[0]
        after = html.split(end)[1]
        path.write_text(before + section + after, encoding="utf-8")
    else:
        legacy_start = "  <!-- S7 — Die Köpfe -->"
        legacy_end = '        <a class="brt-btn brt-btn--outline" href="team/">More about the team →</a>\n      </p>\n    </div>\n  </section>'
        if legacy_start not in html or legacy_end not in html:
            return
        before = html.split(legacy_start)[0]
        rest = html.split(legacy_start)[1]
        after = rest.split(legacy_end, 1)[1]
        path.write_text(before + section + after, encoding="utf-8")
    print("  updated index.html home team")


def gen_home_blog_teaser() -> None:
    path = SITE / "index.html"
    if not path.exists():
        return
    posts = load_blog_posts()[:3]
    if not posts:
        return
    cards = "\n".join(blog_card_html(p, 0) for p in posts)
    html = path.read_text(encoding="utf-8")
    start = "  <!-- BLOG_TEASER_START -->"
    end = "  <!-- BLOG_TEASER_END -->"
    if start not in html or end not in html:
        return
    section = f"""  <!-- BLOG_TEASER_START -->
  <section class="brt-section" aria-labelledby="blog-title">
    <div class="brt-container">
      <header class="brt-section__header brt-section__header--row brt-fade-up">
        <div>
          <p class="brt-tag">Insights</p>
          <h2 id="blog-title" class="brt-h2">Expert insights from Beraterium</h2>
          <p class="brt-body">Short, practical articles on risk, leadership, and decisions — from our team, for founders, SMEs, and solo operators.</p>
        </div>
        <a class="brt-btn brt-btn--outline" href="blog/">All articles →</a>
      </header>
      <ul class="brt-blog-grid brt-stagger">
{cards}
      </ul>
    </div>
  </section>
  <!-- BLOG_TEASER_END -->"""
    before = html.split(start)[0]
    after = html.split(end)[1]
    path.write_text(before + section + after, encoding="utf-8")
    print("  updated index.html blog teaser")


def gen_home_analytics() -> None:
    """Home index.html: sync GA4 snippet after CookieYes."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    start = "  <!-- GA4_START -->"
    end = "  <!-- GA4_END -->\n"
    block = f"{start}\n{GA4_ANALYTICS_HEAD}\n{end}"
    if start in html:
        i = html.find(start)
        j = html.find(end, i)
        if j < 0:
            print("  skip index.html home analytics (end marker not found)")
            return
        path.write_text(html[:i] + block + html[j + len(end) :], encoding="utf-8")
    else:
        anchor = "  <!-- End cookieyes banner -->\n"
        pos = html.find(anchor)
        if pos < 0:
            print("  skip index.html home analytics (cookieyes anchor not found)")
            return
        pos += len(anchor)
        path.write_text(html[:pos] + block + html[pos:], encoding="utf-8")
    print("  updated index.html home analytics")


def gen_home_nav() -> None:
    """Home index.html: sync the main navigation from nav_html()."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    start = '<nav id="site-nav" class="site-header__nav" aria-label="Primary navigation">\n      <ul>\n'
    end = "\n      </ul>"
    i = html.find(start)
    j = html.find(end, i)
    if i < 0 or j < 0:
        print("  skip index.html home nav (pattern not found)")
        return
    i += len(start)
    path.write_text(html[:i] + nav_html(0, None) + html[j:], encoding="utf-8")
    print("  updated index.html home nav")


def gen_home_tools_teaser() -> None:
    """Home index.html: teaser for the Blindspot Check before the blog teaser."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    start = "  <!-- TOOLS_TEASER_START -->"
    end = "  <!-- TOOLS_TEASER_END -->\n"
    section = f"""{start}
  <section class="brt-section brt-section--alt" aria-labelledby="tools-teaser-title">
    <div class="brt-container brt-split brt-split--text-only">
      <div class="brt-split__text brt-fade-up">
        <p class="brt-tag">Free self-assessment</p>
        <h2 id="tools-teaser-title" class="brt-h2">Where is your business vulnerable? The Blindspot Check shows you in 10 minutes.</h2>
        <p class="brt-body">10 to 15 short 'What happens if …' questions about key people, technology and day-to-day operations. Immediate results with traffic-light status and first steps, no sign-up required.</p>
        <a class="brt-btn" href="tools/blindspot-check/">Start the Blindspot Check →</a>
      </div>
    </div>
  </section>
{end}"""
    if start in html and end in html:
        before = html.split(start)[0]
        after = html.split(end)[1]
        path.write_text(before + section + after, encoding="utf-8")
    else:
        anchor = "  <!-- BLOG_TEASER_START -->"
        if anchor not in html:
            print("  skip index.html tools teaser (pattern not found)")
            return
        path.write_text(html.replace(anchor, section + "\n" + anchor, 1), encoding="utf-8")
    print("  updated index.html tools teaser")


def gen_kontakt() -> None:
    pre = "../"
    main = (
        hero(pre, "CONTACT", "Let's talk about your risks",
             "30 minutes, free, no obligation. You leave with genuine insight – however you decide to proceed.",
             compact=True)
        + f"""
    <section class="brt-section brt-section--booking" aria-labelledby="contact-title">
      <div class="brt-container brt-contact-booking brt-fade-up">
        <div class="brt-contact-booking__head">
          <div class="brt-contact-booking__intro">
            <div class="brt-contact-booking__lead">
              <p class="brt-tag">30 minutes · free · no obligation</p>
              <h2 id="contact-title" class="brt-h2">Your free intro call</h2>
              <p class="brt-body">Choose a slot directly – we take time for your situation, not for sales pitches.</p>
            </div>
            <div class="brt-contact-expect">
              <h3 class="brt-contact-expect__title">What to expect</h3>
              <ul class="brt-contact-expect__points">
                <li class="brt-contact-expect__point">
                  <strong>No sales pitch</strong>
                  <span>No hard sell – we explain what we do and how our method works.</span>
                </li>
                <li class="brt-contact-expect__point">
                  <strong>Practical tips included</strong>
                  <span>Concrete pointers so you can start with your own research and groundwork straight away.</span>
                </li>
                <li class="brt-contact-expect__point">
                  <strong>Do it yourself</strong>
                  <span>You leave with enough clarity to take first steps on your own.</span>
                </li>
                <li class="brt-contact-expect__point">
                  <strong>Support optional</strong>
                  <span>If you want guidance, we discuss next steps together – as outlined below.</span>
                </li>
              </ul>
            </div>
          </div>
          <aside class="brt-contact-aside">
            <p class="brt-contact-aside__label">Alternatively</p>
            <h3 class="brt-h3">Direct contact</h3>
            <p class="brt-body">Prefer to write? Use our contact form – we usually reply within one working day.</p>
            <a class="brt-btn brt-btn--outline" href="{pre}contact-form/">Go to contact form</a>
            <ul class="brt-contact-aside__links">
              <li><a href="mailto:info@beraterium.de">info@beraterium.de</a></li>
              <li><a href="https://www.linkedin.com/company/beraterium">LinkedIn</a></li>
            </ul>
          </aside>
        </div>
        <div class="brt-calendly" data-calendly-embed>
          <div id="beraterium-calendly" class="calendly-inline-widget" data-url="https://calendly.com/beraterium/30min"></div>
        </div>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="steps-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">HOW IT WORKS</p>
          <h2 id="steps-title" class="brt-h2">Three steps to clarity</h2>
        </header>
        <ul class="brt-step-cards brt-stagger">
          <li class="brt-step-card"><span class="brt-step-card__num">Step 1</span><h3 class="brt-h3">Choose a slot</h3><p class="brt-body">Book a 30-minute slot that suits you.</p></li>
          <li class="brt-step-card"><span class="brt-step-card__num">Step 2</span><h3 class="brt-h3">The conversation</h3><p class="brt-body">We show you the method and discuss your situation. No sales pressure.</p></li>
          <li class="brt-step-card"><span class="brt-step-card__num">Step 3</span><h3 class="brt-h3">You decide</h3><p class="brt-body">With a DIY guide in hand, you decide in your own time whether and how we work together.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section" aria-label="Trust">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-body">No sales pitch. Free. And if we work together later: with our double guarantee – relevance and value, or your money back.</p>
      </div>
    </section>"""
        + faq_section_html([
            ("What does the intro call cost?", "Nothing. 30 minutes, free and no obligation — not a sales pitch."),
            ("How long is the intro call?", "About 30 minutes. You get the method explained and leave with concrete first steps."),
            ("Do I have to decide afterwards?", "No. You decide in your own time — with a DIY guide in hand, however you choose to proceed."),
        ], title="Frequently asked questions about the intro call", section_id="faq", alt=True)
    )
    contact_faq = [
        ("What does the intro call cost?", "Nothing. 30 minutes, free and no obligation — not a sales pitch."),
        ("How long is the intro call?", "About 30 minutes. You get the method explained and leave with concrete first steps."),
        ("Do I have to decide afterwards?", "No. You decide in your own time — with a DIY guide in hand, however you choose to proceed."),
    ]
    write(
        "contact/index.html",
        shell(
            depth=1,
            title="Book a free intro call | Beraterium",
            description="30 minutes, free, no sales pitch: book your intro call with Till and Peter and make your biggest risks visible.",
            canonical="/contact/",
            active_nav=None,
            main=main,
            json_ld=page_schema(faq_page_schema(contact_faq)),
        ).replace(
            f'<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
            f'<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript" async></script>\n<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
        ),
    )


def gen_kontaktformular() -> None:
    pre = "../"
    main = f"""
    <section class="brt-page-hero brt-page-hero--dark brt-page-hero--compact" aria-labelledby="page-hero-title">
      <div class="brt-container">
        <div class="brt-fade-up">
          <p class="brt-tag">CONTACT</p>
          <h1 id="page-hero-title" class="brt-h1">Contact form</h1>
          <p class="brt-lead brt-lead--on-dark">Write to us – we usually reply within one working day.</p>
        </div>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="form-title">
      <div class="brt-container brt-contact-form-wrap brt-fade-up">
        <header class="brt-section__header">
          <h2 id="form-title" class="brt-h2">Contact us directly</h2>
          <p class="brt-body">Use our contact form below. For a free intro call, you can also book a slot directly.</p>
          <p class="brt-meta"><a href="{pre}contact/">Book a slot →</a></p>
        </header>
        <form class="brt-form brt-form--contact" action="https://formsubmit.co/till.blania@beraterium.de" method="POST" novalidate>
          <input type="hidden" name="_subject" value="New contact request – Beraterium">
          <input type="hidden" name="_next" value="https://en.beraterium.de/thank-you/">
          <input type="hidden" name="_template" value="table">
          <input type="text" name="_honey" class="brt-form__honey" tabindex="-1" autocomplete="off" aria-hidden="true">
          <label>Name *
            <input type="text" name="name" required autocomplete="name">
          </label>
          <label>Email *
            <input type="email" name="email" required autocomplete="email">
          </label>
          <label>Company
            <input type="text" name="company" autocomplete="organization">
          </label>
          <label>I am …
            <select name="type">
              <option value="">Please select</option>
              <option>Startup</option>
              <option>SME</option>
              <option>Solo self-employed</option>
              <option>Other</option>
            </select>
          </label>
          <label>Your message *
            <textarea name="message" required placeholder="What is this about?"></textarea>
          </label>
          <fieldset class="brt-form__legal">
            <legend class="brt-form__legal-legend">Confirmations</legend>
            <div class="brt-form__check-group">
              <label class="brt-form__check" for="agb_accepted">
                <input type="checkbox" id="agb_accepted" name="agb_accepted" value="Yes">
                <span>I have read and accept the <a href="{pre}terms/">terms and conditions</a>.</span>
              </label>
              <p class="brt-form__error" id="agb-error" role="alert" hidden>Please confirm the terms and conditions.</p>
            </div>
            <div class="brt-form__check-group">
              <label class="brt-form__check" for="privacy_accepted">
                <input type="checkbox" id="privacy_accepted" name="privacy_accepted" value="Yes">
                <span>I have read the <a href="{pre}privacy/">privacy policy</a> and agree to the processing of my data.</span>
              </label>
              <p class="brt-form__error" id="privacy-error" role="alert" hidden>Please confirm the privacy policy.</p>
            </div>
          </fieldset>
          <button class="brt-btn" type="submit">Send message</button>
          <p class="brt-meta">We usually reply within one working day.</p>
        </form>
      </div>
    </section>"""
    write(
        "contact-form/index.html",
        shell(
            depth=1,
            title="Contact form | Beraterium",
            description="Contact Beraterium directly via our contact form. We usually reply within one working day.",
            canonical="/contact-form/",
            active_nav=None,
            main=main,
        ),
    )


def gen_impressum() -> None:
    sections = (SITE / "_content" / "impressum_sections.html").read_text()
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">Legal notice</h1>
{sections}
      </div>
    </section>"""
    write(
        "legal-notice/index.html",
        shell(
            depth=1,
            title="Legal notice | Beraterium",
            description="Legal notice and provider information for Beraterium GbR — contact, VAT ID and legal details.",
            canonical="/legal-notice/",
            active_nav=None,
            main=main,
        ),
    )


def gen_datenschutz() -> None:
    sections = (SITE / "_content" / "datenschutz_sections.html").read_text()
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">Privacy policy</h1>
{sections}
      </div>
    </section>"""
    write(
        "privacy/index.html",
        shell(
            depth=1,
            title="Privacy policy | Beraterium",
            description="Information on the processing of personal data on en.beraterium.de — GDPR-compliant, updated 2026.",
            canonical="/privacy/",
            active_nav=None,
            main=main,
        ),
    )


def gen_agb() -> None:
    sections = (SITE / "_content" / "agb_sections.html").read_text()
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">Terms and conditions</h1>
{sections}
      </div>
    </section>"""
    write(
        "terms/index.html",
        shell(
            depth=1,
            title="Terms and conditions | Beraterium",
            description="Terms and conditions of Beraterium GbR for consulting services in risk management, HR, management and process optimisation.",
            canonical="/terms/",
            active_nav=None,
            main=main,
        ),
    )


def gen_accessibility() -> None:
    main = """
    <section class="brt-section" aria-labelledby="a11y-title">
      <div class="brt-container brt-legal">
        <h1 id="a11y-title" class="brt-h2">Accessibility statement</h1>
        <p>We continuously work to make content and features on en.beraterium.de accessible and align implementation with WCAG 2.1 Level AA requirements.</p>
        <h2 class="brt-h3">Compliance status</h2>
        <p>This website is partially compliant with WCAG 2.1 AA. Some barriers still exist and are being resolved step by step.</p>
        <h2 class="brt-h3">Assessment approach</h2>
        <p>Our assessment combines automated checks (own Playwright + axe-core audit pipeline) with manual keyboard, focus-order and semantic-structure reviews across representative page types.</p>
        <h2 class="brt-h3">Known limitations</h2>
        <ul>
          <li>Some legacy content blocks may still contain incomplete semantics or contrast-sensitive details.</li>
          <li>Embedded third-party content (for example external widgets) is only partly under our direct control.</li>
        </ul>
        <h2 class="brt-h3">Feedback and contact</h2>
        <p>If you encounter accessibility barriers or have improvement suggestions, contact us at <a href="mailto:info@beraterium.de">info@beraterium.de</a> or use our <a href="../contact-form/">contact form</a>.</p>
        <p>We review your message and respond as quickly as possible.</p>
        <h2 class="brt-h3">Statement date</h2>
        <p>This statement was created on 2026-06-26 and is reviewed regularly.</p>
      </div>
    </section>"""
    write(
        "accessibility/index.html",
        shell(
            depth=1,
            title="Accessibility statement | Beraterium",
            description="Information about digital accessibility on en.beraterium.de, our audit approach and contact options for accessibility feedback.",
            canonical="/accessibility/",
            active_nav=None,
            main=main,
        ),
    )


def gen_legal(slug: str, title: str, h1: str, sections: str, noindex: bool = False) -> None:
    pre = "../"
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">{h1}</h1>
{sections}
      </div>
    </section>"""
    write(f"{slug}/index.html", shell(depth=1, title=title, description=title,
          canonical=f"/{slug}/", active_nav=None, main=main, noindex=noindex))


def gen_404() -> None:
    pre = ""
    main = """
    <section class="brt-page-hero brt-page-hero--dark brt-page-hero--compact" aria-labelledby="not-found-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">404</p>
        <h1 id="not-found-title" class="brt-h1">This page doesn't exist</h1>
        <p class="brt-lead brt-lead--on-dark">The address may have changed or there might be a typo. Here are some useful links:</p>
        <div class="brt-page-hero__actions" style="justify-content: center;">
          <a class="brt-btn brt-btn--on-dark" href="./">Home</a>
          <a class="brt-btn brt-btn--outline" href="services/" style="color:#fff;border-color:rgba(255,255,255,.5);">Services</a>
          <a class="brt-btn brt-btn--outline" href="method/" style="color:#fff;border-color:rgba(255,255,255,.5);">Method</a>
          <a class="brt-btn brt-btn--outline" href="contact/" style="color:#fff;border-color:rgba(255,255,255,.5);">Contact</a>
        </div>
      </div>
    </section>"""
    write("404.html", shell(depth=0, title="Page not found | Beraterium", description="The requested page does not exist.",
          canonical="/404", active_nav=None, main=main, noindex=True))


def gen_danke() -> None:
    pre = "../"
    main = f"""
    <section class="brt-section" aria-labelledby="danke-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">THANK YOU</p>
        <h1 id="danke-title" class="brt-h2">Thank you – we look forward to speaking with you!</h1>
        <p class="brt-body">Your message has been received. Till or Peter will usually get back to you within one working day.</p>
        <ul class="brt-step-cards" style="margin-top: var(--space-8); text-align: left;">
          <li class="brt-step-card"><p class="brt-body">In the meantime, take a look at our <a href="{pre}method/">method</a>.</p></li>
        </ul>
        <p class="brt-section__cta">
          <a class="brt-btn brt-btn--outline" href="{pre}">Back to homepage</a>
        </p>
      </div>
    </section>"""
    write("thank-you/index.html", shell(depth=1, title="Thank you – we'll be in touch | Beraterium",
          description="Thank you for your enquiry. We will get back to you shortly.", canonical="/thank-you/",
          active_nav=None, main=main, noindex=True))

# --- EN parity generators (from DE site) ---
def _offer_details_block(o: dict) -> str:
    """Ausklappbarer Detail-Teaser fuer jedes Angebot; verlinkt zusaetzlich auf die
    Schulungsseite, falls vorhanden (Schulungen SCH-*)."""
    if not o.get("details_html"):
        return ""
    link = (
        f'<p class="brt-meta"><a href="../training/{o["slug"]}/">Zur Schulungsseite mit allen Details \u2192</a></p>'
        if o.get("slug")
        else ""
    )
    return (
        '<details class="brt-faq__item brt-price-details">'
        '<summary class="brt-faq__summary">'
        '<span class="brt-faq__toggle" aria-hidden="true"></span>'
        '<span class="brt-faq__question">Mehr zu diesem Angebot anzeigen</span>'
        '<span class="brt-faq__chevron" aria-hidden="true"></span>'
        "</summary>"
        f'<div class="brt-faq__answer">{o["details_html"]}{link}</div>'
        "</details>"
    )


def price_table_html(cat: dict) -> str:
    """Preistabelle einer Kategorie aus _pricing.py (sichtbar == Schema-Quelle)."""
    rows = "\n".join(
        f'              <tr id="{o["nr"].lower()}">'
        f'<th scope="row">{o["name"]}<br><span class="brt-compare__muted">{o["desc"]}</span>'
        + _offer_details_block(o)
        + "</th>"
        f'<td><strong>{offer_price_text(o)}</strong>'
        + (f'<br><span class="brt-compare__muted">{o["price_detail"]}</span>' if o.get("price_detail") else "")
        + f'</td><td>{o["duration"]}</td></tr>'
        for o in cat["offers"]
    )
    return f"""
    <section class="brt-section" id="{cat["id"]}" aria-labelledby="preise-{cat["id"]}-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{cat["tag"]}</p>
          <h2 id="preise-{cat["id"]}-title" class="brt-h2">{cat["title"]}</h2>
          <p class="brt-body">{cat["lede"]}</p>
        </header>
        <div class="brt-table-wrap brt-fade-up">
          <table class="brt-table">
            <caption class="brt-sr-only">Preise: {cat["title"]}</caption>
            <thead>
              <tr><th scope="col">Angebot</th><th scope="col">Preis (netto)</th><th scope="col">Dauer &amp; Umfang</th></tr>
            </thead>
            <tbody>
{rows}
            </tbody>
          </table>
        </div>
      </div>
    </section>"""


def gen_pricing() -> None:
    pre = "../"
    preise_faq = [
        ("Was kostet eine Risikoanalyse bei Beraterium?", "Die Risiko-Analyse 360° ist das Komplettpaket für 3.475 € (Analyse + Strategie + Budgetplanung). Einzeln kosten die drei Module 1.725 €, 2.175 € und 1.250 € — zusammen 5.150 €. Das Gesamtpaket XL mit kompletter Begleitung kostet 9.675 €."),
        ("Was kosten die Workshops?", "Workshops werden pro Person berechnet, mit Mengenstaffel: der Einstiegs-Workshop „Risiken allgemein“ kostet einzeln 127 €, ab 8 Personen 57 € pro Person. Spezial-Workshops wie „Globale Risiken“ liegen bei bis zu 347 € pro Person."),
        ("Was kosten die Schulungen?", "Die Ausbildung zum Risikoexperten (Kombi aus drei Modulen) kostet 9.875 € für eine Person, 14.315 € für zwei. Die drei Einzelschulungen im Intensivformat (1:1 oder Kleinstgruppe) liegen bei 3.475–4.975 € — deutlich tiefer und persönlicher als in der Kombi. Innovations- und Feedback-Schulungen ab 2.875 €, interkulturelles Management ab 3.475 € — Risiko-Schulungen im Intensivformat ab 3.475 € (Materialien, Tools, Gefahrenkatalog). Alle Preise netto zzgl. USt."),
        ("Gibt es einen kostenlosen Einstieg?", "Ja. Der Risiko-Check für Startups (1 Stunde) ist für Neugründer bis 10.000 € Umsatz kostenlos. Kompakte Kurz-Checks gibt es ab 47 €."),
        ("Sind das Festpreise oder Stundensätze?", "Die Analysepakete sind Festpreise — Sie wissen vorher genau, was es kostet. Workshops und HR-Module werden pro Person bzw. pro Interview berechnet, mit Mengenstaffel. Alle Preise verstehen sich netto zuzüglich Umsatzsteuer."),
        ("Warum veröffentlicht Beraterium seine Preise?", "Transparenz gehört zu unserer Haltung: Sie sollen Angebote vergleichen können, bevor Sie mit uns sprechen. Im kostenlosen Erstgespräch klären wir dann, welches Paket zu Ihrer Situation passt."),
        ("Gilt die doppelte Garantie auch für diese Angebote?", "Ja. Für die Analysepakete gelten Relevanz- und Nutzen-Garantie: Finden wir kein relevantes Risiko oder erfüllen wir die vereinbarten Nutzen-Kriterien nicht, erstatten wir den vollen Betrag."),
    ] + list(PREISE_GEO_FAQ)
    tables = "".join(price_table_html(cat) for cat in PRICE_CATEGORIES)
    main = (
        hero(pre, "PREISE & LEISTUNGEN", "Was kostet Risikomanagement-Beratung bei Beraterium?",
             "Alle Preise transparent: vom kostenlosen Startup-Erst-Check über Team-Workshops ab 57 € pro Person und Ausbildung zum Risikoexperten ab 9.875 €, Einzelschulungen Intensivformat ab 3.475 € bis zum Kernpaket Risiko-Analyse 360° für 3.475 € (Einzelmodule ab 1.250 €) und Gesamtpaket XL für 9.675 €. Alle Preise netto zzgl. USt.",
             compact=True,
             actions=f'<a class="brt-btn" href="{pre}contact/">Book a free intro call</a>')
        + pricing_compare_section(pre=pre)
        + tables
        + f"""
    <section class="brt-section brt-section--alt" aria-labelledby="preise-erklaert-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">SO SETZEN SICH DIE PREISE ZUSAMMEN</p>
          <h2 id="preise-erklaert-title" class="brt-h2">Preismodelle erklärt</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Festpreis-Pakete</h3><p class="brt-body">Analyse- und Strategiepakete haben einen Festpreis (1.250–9.675 €). Das Kernpaket Risiko-Analyse 360° bündelt Analyse, Strategie und Budgetplanung für 3.475 € — abgesichert durch die doppelte Garantie.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Pro-Kopf-Staffeln</h3><p class="brt-body">Workshops und HR-Module werden pro Person bzw. pro Interview berechnet — je größer die Gruppe, desto günstiger pro Kopf. Schulungen kombinieren Basispreis, Aufpreis je weiterem Teilnehmer und eine gedeckelte Team-Pauschale: ab der Deckel-Gruppengröße kostet das ganze Team nicht mehr.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Doppelte Garantie</h3><p class="brt-body">Analysepakete sind durch Relevanz- und Nutzen-Garantie abgesichert: kein relevantes Risiko oder kein vereinbarter Nutzen — volle Erstattung. Details auf den <a href="{pre}benefit-guarantee/">Garantie-Seiten</a>.</p></li>
        </ul>
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Welches Paket zu Ihrer Situation passt, klären wir im <a href="{pre}contact/">kostenlosen Erstgespräch</a> — Übersicht nach Zielgruppe: <a href="{pre}services/">Angebote für Startups, KMU &amp; Solo</a>.</p>
      </div>
    </section>"""
        + guarantee(pre)
        + faq_section_html(preise_faq, title="Frequently asked questions zu Preisen", section_id="faq", alt=True)
        + cta_band(pre, "Unsicher, welches Paket passt?", "Im kostenlosen Erstgespräch klären wir Umfang, Förderung und den besten Einstieg für Ihre Situation.")
    )
    preise_title = "Preise – Risikomanagement-Beratung | Beraterium"
    preise_desc = "Preise transparent: Risiko-Analyse 360° 3.475 € (Festpreis), Workshops ab 57 €/Person, Schulungen ab 3.475 €. Marktvergleich: unter Konzernberatern, mit doppelter Garantie."
    write("pricing/index.html", shell(depth=1, title=preise_title, description=preise_desc,
          canonical="/pricing/", active_nav="pricing", main=main,
          json_ld=page_schema(
              offer_catalog_schema(
                  name="Preise & Leistungen — Risikomanagement-Beratung",
                  description=preise_desc,
                  url="/pricing/",
                  categories=PRICE_CATEGORIES,
              ),
              faq_page_schema(preise_faq),
              speakable_webpage_schema(
                  "/pricing/",
                  selectors=[".brt-highlight-box", ".brt-faq__answer", "#preisvergleich .brt-body"],
              ),
              json.dumps(
                  {
                      "@context": "https://schema.org",
                      "@type": "BreadcrumbList",
                      "itemListElement": [
                          {"@type": "ListItem", "position": 1, "name": "Start", "item": f"{EN_SITE_URL}/"},
                          {"@type": "ListItem", "position": 2, "name": "Preise & Leistungen", "item": f"{EN_SITE_URL}/pricing/"},
                      ],
                  },
                  ensure_ascii=False,
                  indent=2,
              ),
          )))

_SCH_PRICING: dict[str, dict] = {
    o["nr"]: o
    for cat in PRICE_CATEGORIES
    for o in cat["offers"]
    if o["nr"].startswith("SCH-")
}


def schulung_price_section(offer: dict, *, pre: str) -> str:
    """Preisblock einer Schulung: Basis + Aufpreis + gedeckelte Team-Pauschale."""
    team_max = offer.get("team_max")
    if team_max:
        intro = (
            f"Buchbar f\u00fcr einzelne Mitarbeitende oder Kleingruppen "
            f"\u2014 pauschal bis max. {team_max} Teilnehmer."
        )
        team_card = (
            f"<strong>{format_eur(offer['price_team'])} pauschal</strong><br>"
            f"Max. {team_max} Teilnehmer."
        )
    else:
        intro = (
            f"Buchbar f\u00fcr einzelne Mitarbeitende, Kleingruppen oder das ganze Team "
            f"\u2014 ab {offer['team_from']} Personen greift die gedeckelte Team-Pauschale."
        )
        team_card = (
            f"<strong>{format_eur(offer['price_team'])} pauschal</strong> ab {offer['team_from']} Personen<br>"
            f"Gedeckelt \u2014 mehr Teilnehmer kosten nicht mehr."
        )
    return f"""
    <section class="brt-section brt-section--alt" id="preis" aria-labelledby="preis-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">PREIS (NETTO ZZGL. UST.)</p>
          <h2 id="preis-title" class="brt-h2">Was kostet die Schulung?</h2>
          <p class="brt-body">{intro}</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Einzeln</h3><p class="brt-body"><strong>{format_eur(offer["price_base"])}</strong><br>Basispreis f\u00fcr die erste Person.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Kleingruppe</h3><p class="brt-body"><strong>+{format_eur(offer["price_add"])}</strong> je weiterem Teilnehmer<br>Sie zahlen nur, wer wirklich teilnimmt.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Ganzes Team</h3><p class="brt-body">{team_card}</p></li>
        </ul>
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Alle Preise und Angebote im \u00dcberblick: <a href="{pre}pricing/">Preise &amp; Leistungen</a>.</p>
      </div>
    </section>"""

def gen_schulung(cfg: dict) -> None:
    """Datengetriebene Schulungs-Unterseite /training/<slug>/.

    Inhalt aus _schulungen.py (SCHULUNG_CONFIGS), Preis-Staffel aus
    _pricing.py (Join ueber "nr"). Struktur: Hero -> Fuer-wen-Checkliste ->
    Ablauf/Sessions -> Ergebnis -> Preisblock -> FAQ -> CTA.
    """
    slug = cfg["slug"]
    pre = "../../"
    canonical = f"/training/{slug}/"
    offer = _SCH_PRICING[cfg["nr"]]

    fuer_wen_items = "".join(f"<li>{item}</li>" for item in cfg["fuer_wen"])
    session_cards = "".join(
        f'<li class="brt-card brt-hover-lift"><h3 class="brt-h3">{title}</h3>'
        '<ul class="brt-list-check">'
        + "".join(f"<li>{b}</li>" for b in bullets)
        + "</ul></li>"
        for title, bullets in cfg["sessions"]
    )
    ergebnis_items = "".join(f"<li>{item}</li>" for item in cfg["ergebnis"])

    if len(cfg["sessions"]) > 3:
        # Slider: zeigt 3 Karten, Pfeile blaettern (initCardsSlider in brt-site.js)
        sessions_block = (
            '<div class="brt-cards-slider brt-fade-up" data-cards-slider>'
            '<div class="brt-cards-slider__viewport" tabindex="0" role="group" aria-label="Sessions der Schulung">'
            f'<ul class="brt-cards-slider__track">{session_cards}</ul>'
            "</div>"
            '<div class="brt-cards-slider__nav">'
            '<button type="button" class="brt-cards-slider__btn brt-cards-slider__btn--prev" aria-label="Vorherige Session">'
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>'
            "</button>"
            '<button type="button" class="brt-cards-slider__btn brt-cards-slider__btn--next" aria-label="N\u00e4chste Session">'
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>'
            "</button></div></div>"
        )
    else:
        sessions_block = f'<ul class="brt-cards-3col brt-stagger">{session_cards}</ul>'

    main = (
        hero(
            pre, cfg["tag"], cfg["h1"], cfg["lead"],
            actions=(
                f'<a class="brt-btn" href="{pre}contact/">Kostenloses Erstgespr\u00e4ch buchen</a>'
                f'<a class="brt-btn brt-btn--outline" href="#preis">Zum Preis \u2192</a>'
            ),
        )
        + f"""
    <section class="brt-section" id="fuer-wen" aria-labelledby="fuer-wen-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">F\u00dcR WEN?</p>
        <h2 id="fuer-wen-title" class="brt-h2">F\u00fcr wen ist diese Schulung gedacht?</h2>
        <p class="brt-body">{cfg["fuer_wen_intro"]}</p>
        <ul class="brt-list-check">{fuer_wen_items}</ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" id="ablauf" aria-labelledby="ablauf-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">INHALTE &amp; ABLAUF</p>
          <h2 id="ablauf-title" class="brt-h2">Wie l\u00e4uft die Schulung ab?</h2>
          <p class="brt-body">Dauer: {offer["duration"]} \u2014 inhouse bei Ihnen vor Ort oder online. Zielgruppe: {cfg["audience"]}.</p>
        </header>
        {sessions_block}
      </div>
    </section>
    <section class="brt-section" id="ergebnis" aria-labelledby="ergebnis-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">ERGEBNIS</p>
        <h2 id="ergebnis-title" class="brt-h2">Was nehmen Sie mit?</h2>
        <ul class="brt-list-check">{ergebnis_items}</ul>
      </div>
    </section>"""
        + schulung_price_section(offer, pre=pre)
        + schulung_geo_note(cfg["nr"], pre=pre)
        + faq_section(cfg["faq"])
        + cta_band(pre, cfg["cta_h2"], cfg["cta_body"], "Kostenloses Erstgespr\u00e4ch buchen")
    )

    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{EN_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Schulungen", "item": f"{EN_SITE_URL}/training/"},
                {"@type": "ListItem", "position": 3, "name": cfg["h1"], "item": f"{EN_SITE_URL}{canonical}"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    ld = page_schema(
        course_schema(
            name=cfg["h1"],
            description=cfg["description"],
            url=canonical,
            price=offer["price_base"],
            price_detail=offer["price_detail"],
            workload_iso=cfg["workload_iso"],
        ),
        faq_page_schema(cfg["faq"]),
        speakable_webpage_schema(canonical),
        breadcrumb_ld,
    )
    write(
        f"training/{slug}/index.html",
        shell(
            depth=2,
            title=cfg["title"],
            description=cfg["description"],
            canonical=canonical,
            active_nav="training",
            main=main,
            json_ld=ld,
        ),
    )


def gen_schulungen_index() -> None:
    """Index-Seite /training/ mit Karten zu allen Schulungen."""
    pre = "../"
    cards = "".join(
        f'<li class="brt-card brt-card--catalog brt-hover-lift"><a class="brt-card__link" href="{cfg["slug"]}/">'
        f'<h3 class="brt-h3">{cfg["h1"]}</h3>'
        f'<p class="brt-body">{_SCH_PRICING[cfg["nr"]]["desc"]}</p>'
        f'<p class="brt-meta">{_SCH_PRICING[cfg["nr"]]["duration"]} \u00b7 {offer_price_text(_SCH_PRICING[cfg["nr"]])}</p>'
        f'<span class="brt-meta" aria-hidden="true">Zur Schulung \u2192</span></a></li>'
        for cfg in SCHULUNG_CONFIGS
    )
    schulungen_faq = [
        ("Wie funktioniert das Preismodell der Schulungen?", "Jede Schulung hat einen Basispreis f\u00fcr die erste Person und einen festen Aufpreis je weiterem Teilnehmer. Ab einer definierten Gruppengr\u00f6\u00dfe greift eine gedeckelte Team-Pauschale \u2014 mehr Teilnehmer kosten dann nicht mehr. Alle Preise netto zzgl. USt."),
        ("Kann ich eine Schulung f\u00fcr einen einzelnen Mitarbeiter buchen?", "Ja. Jede Schulung ist sowohl f\u00fcr einzelne Mitarbeitende (Basispreis) als auch f\u00fcr Kleingruppen oder das ganze Team buchbar \u2014 die Inhalte werden auf die Gruppengr\u00f6\u00dfe zugeschnitten."),
        ("Finden die Schulungen bei uns im Haus statt?", "Ja, wahlweise inhouse bei Ihnen vor Ort oder online. Bei Team-Buchungen empfehlen wir inhouse \u2014 die Praxisteile arbeiten direkt an Ihren realen Prozessen und F\u00e4llen."),
        ("Wie liegen die Preise im Marktvergleich?", "Team-Schulungen (SCH-04–06): ab 2.875 €, Team-Pauschalen 9.395–9.875 € — unter üblichen Inhouse-Preisen (2.500–4.000 €). Intensivformat (SCH-01–03): 3.475–4.975 € für 1:1/Kleinstgruppe — mehr als offene Seminare (250–500 €/Tag), weil Coaching-Tiefe und Transfer inklusive sind. Risikoexperte (SCH-07): 9.875 € (1 Pers.) statt 12.425 € als Einzelbuchungen."),
    ] + list(SCHULUNGEN_GEO_FAQ)
    main = (
        hero(pre, "SCHULUNGEN", "Schulungen f\u00fcr Risikokultur, Innovation &amp; F\u00fchrung",
             "Sieben vertiefende Schulungen \u2014 von der kompletten Ausbildung zum Risikoexperten \u00fcber die Risk-Awareness-Kultur nach Luftfahrt-Vorbild \u00fcber praktisches Risikomanagement bis zu Innovations-, Feedback- und interkulturellem Management. Buchbar f\u00fcr einzelne Mitarbeitende oder das ganze Team, inhouse oder online. Ausbildung zum Risikoexperten ab 9.875 \u20ac (2 Personen 14.315 \u20ac); Einzelschulungen Intensivformat ab 3.475 \u20ac (netto zzgl. USt.).",
             compact=True,
             actions=f'<a class="brt-btn" href="{pre}contact/">Kostenloses Erstgespr\u00e4ch buchen</a>')
        + f"""
    <section class="brt-section" id="katalog" aria-labelledby="katalog-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">SECHS SCHULUNGEN</p>
          <h2 id="katalog-title" class="brt-h2">Welche Schulungen bietet Beraterium an?</h2>
          <p class="brt-body">Alle Schulungen kommen aus der Praxis unserer Risikoanalysen \u2014 und geben Ihrem Team Methoden an die Hand, die es danach selbst anwenden kann.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">{cards}</ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" id="preismodell" aria-labelledby="preismodell-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">DAS PREISMODELL</p>
          <h2 id="preismodell-title" class="brt-h2">Ein Preismodell, drei Stufen</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Einzeln</h3><p class="brt-body">Intensivformat ab 3.475 \u20ac oder Kombi-Ausbildung Risikoexperte ab 9.875 \u20ac \u2014 ideal, um eine Schulung erst einmal zu testen.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Kleingruppe</h3><p class="brt-body">Fester Aufpreis je weiterem Teilnehmer (725\u2013995 \u20ac je nach Schulung) \u2014 transparent und planbar, Sie zahlen nur, wer teilnimmt.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Ganzes Team</h3><p class="brt-body">Gedeckelte Team-Pauschale ab Gruppengr\u00f6\u00dfe (9.395\u20139.875 \u20ac) \u2014 mehr Teilnehmer kosten nicht mehr. Bewusst unter den \u00fcblichen Inhouse-Seminarpreisen (2.500\u20134.000 \u20ac).</p></li>
        </ul>
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Alle Staffeln im Detail: <a href="{pre}pricing/#schulungen">Preise &amp; Leistungen</a>.</p>
      </div>
    </section>"""
        + schulungen_value_section(pre=pre)
        + faq_section_html(schulungen_faq, title="H\u00e4ufige Fragen zu den Schulungen")
        + cta_band(pre, "Welche Schulung passt zu Ihrem Team?", "Im kostenlosen Erstgespr\u00e4ch kl\u00e4ren wir Ziel, Teamgr\u00f6\u00dfe und den besten Einstieg \u2014 unverbindlich, in 30 Minuten.")
    )
    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{EN_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Schulungen", "item": f"{EN_SITE_URL}/training/"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    schulungen_title = "Schulungen Risikomanagement & F\u00fchrung | Beraterium"
    schulungen_desc = "Sieben Inhouse-Schulungen: Ausbildung zum Risikoexperten ab 9.875 \u20ac, Einzelschulungen Intensivformat ab 3.475 \u20ac, Innovation, Feedback, interkulturelles Management."
    write("training/index.html", shell(depth=1, title=schulungen_title, description=schulungen_desc,
          canonical="/training/", active_nav="training", main=main,
          json_ld=page_schema(faq_page_schema(schulungen_faq), speakable_webpage_schema("/training/", selectors=[".brt-highlight-box", ".brt-faq__answer", "#schulungen-vergleich .brt-body"]), breadcrumb_ld)))

def lp_deep_sections_html(sections: list[dict], start: int = 0, end: int | None = None) -> str:
    """Vertiefungs-Bloecke einer Landingpage (Prosa + optionale Checkliste)."""
    out = []
    for i, sec in enumerate(sections[start:end], start=start + 1):
        paragraphs = "".join(f'<p class="brt-body">{p}</p>' for p in sec.get("paragraphs", []))
        items = ""
        if sec.get("items"):
            items = '<ul class="brt-list-check">' + "".join(f"<li>{it}</li>" for it in sec["items"]) + "</ul>"
        out.append(f"""
    <section class="brt-section" id="vertiefung-{i}" aria-labelledby="vertiefung-{i}-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">{sec["tag"]}</p>
        <h2 id="vertiefung-{i}-title" class="brt-h2">{sec["h2"]}</h2>
        <p class="brt-body">{sec["intro"]}</p>
        {paragraphs}
        {items}
      </div>
    </section>""")
    return "".join(out)


def lp_steps_section_html(cfg: dict) -> str:
    """Nummerierte Schritt-Karten (z. B. Sofortmassnahmen, Uebergabe-Checkliste)."""
    sec = cfg.get("steps_section")
    if not sec:
        return ""
    step_cards = "".join(
        f'<li class="brt-card brt-hover-lift">'
        f'<span class="brt-method-step__num" aria-hidden="true">{i:02d}</span>'
        f'<h3 class="brt-h3">{title}</h3><p class="brt-body">{body}</p></li>'
        for i, (title, body) in enumerate(sec["steps"], start=1)
    )
    return f"""
    <section class="brt-section" id="schritte" aria-labelledby="schritte-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{sec["tag"]}</p>
          <h2 id="schritte-title" class="brt-h2">{sec["h2"]}</h2>
          <p class="brt-body">{sec["intro"]}</p>
        </header>
        <ol class="brt-cards-3col brt-stagger">{step_cards}</ol>
      </div>
    </section>"""


def lp_facts_table_html(table: dict | None) -> str:
    """Zitierbare Fakten-Tabelle (GEO-Block, z. B. Meldefristen oder Personas)."""
    if not table:
        return ""
    head = "".join(f'<th scope="col">{h}</th>' for h in table["headers"])
    rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        for row in table["rows"]
    )
    return f"""
    <section class="brt-section brt-section--alt" id="fakten" aria-labelledby="fakten-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{table["tag"]}</p>
          <h2 id="fakten-title" class="brt-h2">{table["h2"]}</h2>
          <p class="brt-body">{table["intro"]}</p>
        </header>
        <div class="brt-table-wrap brt-fade-up">
          <table class="brt-table">
            <caption class="brt-sr-only">{table["caption"]}</caption>
            <thead><tr>{head}</tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </div>
    </section>"""


def lp_related_blog_section(slugs: list[str]) -> str:
    """Kuratierte Blog-Karten am Ende einer Landingpage (Crosslinking LP -> Blog)."""
    if not slugs:
        return ""
    by_slug = {p.slug: p for p in load_blog_posts()}
    cards = []
    for s in slugs:
        post = by_slug.get(s)
        if post:
            cards.append(blog_card_html(post, 2))
        else:
            print(f"  warn: lp blog_slug nicht gefunden: {s}")
    if not cards:
        return ""
    return f"""
    <section class="brt-section" aria-labelledby="lp-related-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">WEITERFÜHRENDE ARTIKEL</p>
          <h2 id="lp-related-title" class="brt-h2">Vertiefung im Beraterium-Blog</h2>
        </header>
        <ul class="brt-blog-grid brt-stagger">
{chr(10).join(cards)}
        </ul>
      </div>
    </section>"""

def gen_landingpage(cfg: dict) -> None:
    """Datengetriebenes SEO+GEO-One-Pager-Template unter /solutions/<slug>/.

    Eine neue Landingpage = ein neuer Eintrag in LP_CONFIGS (siehe NIS2 als
    Referenz). Struktur: Hero (answer-first) -> Kriterien-Checkliste (GEO-
    Zitat-Block) -> Stats -> Schmerz-Karten -> Beraterium-Ueberblick mit Links
    zur Hauptseite -> FAQ (sichtbar + Schema aus derselben Quelle) -> CTA.
    """
    slug = cfg["slug"]
    pre = "../../"
    canonical = f"/solutions/{slug}/"

    criteria_items = "".join(f"<li>{item}</li>" for item in cfg["criteria"])
    pain_cards = "".join(
        f'<li class="brt-card brt-hover-lift"><h3 class="brt-h3">{title}</h3>'
        f'<p class="brt-body">{body}</p></li>'
        for title, body in cfg["pain_cards"]
    )
    overview_cards = "".join(
        f'<li class="brt-card brt-hover-lift"><a class="brt-card__link" href="{pre}{href}">'
        f'<h3 class="brt-h3">{title}</h3><p class="brt-body">{body}</p>'
        f'<span class="brt-meta" aria-hidden="true">{link_label} \u2192</span></a></li>'
        for title, body, href, link_label in cfg["overview_cards"]
    )

    hero_cta2 = cfg.get("hero_cta2")
    hero_cta2_html = (
        f'<a class="brt-btn brt-btn--outline" href="{pre}{hero_cta2["href"]}">{hero_cta2["label"]}</a>'
        if hero_cta2
        else '<a class="brt-btn brt-btn--outline" href="#faq">Frequently asked questions \u2192</a>'
    )
    main = (
        hero(
            pre, cfg["tag"], cfg["h1"], cfg["lead"],
            actions=(
                f'<a class="brt-btn" href="{pre}contact/">{cfg["hero_cta"]}</a>'
                f'{hero_cta2_html}'
            ),
        )
        + f"""
    <section class="brt-section" id="kriterien" aria-labelledby="kriterien-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">{cfg["criteria_tag"]}</p>
        <h2 id="kriterien-title" class="brt-h2">{cfg["criteria_h2"]}</h2>
        <p class="brt-body">{cfg["criteria_intro"]}</p>
        <ul class="brt-list-check">{criteria_items}</ul>
      </div>
    </section>"""
        + guarantee_stat_row(cfg["stats"], aria=cfg["stats_aria"])
        + lp_deep_sections_html(cfg.get("deep_sections", []), end=1)
        + f"""
    <section class="brt-section brt-section--alt" aria-labelledby="pain-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{cfg["pain_tag"]}</p>
          <h2 id="pain-title" class="brt-h2">{cfg["pain_h2"]}</h2>
          <p class="brt-body">{cfg["pain_intro"]}</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">{pain_cards}</ul>
      </div>
    </section>"""
        + lp_steps_section_html(cfg)
        + lp_facts_table_html(cfg.get("facts_table"))
        + lp_deep_sections_html(cfg.get("deep_sections", []), start=1)
        + (guarantee(pre, du=cfg.get("du", False)) if cfg.get("guarantee_section") else "")
        + f"""
    <section class="brt-section" aria-labelledby="overview-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{cfg["overview_tag"]}</p>
          <h2 id="overview-title" class="brt-h2">{cfg["overview_h2"]}</h2>
          <p class="brt-body">{cfg["overview_intro"]}</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">{overview_cards}</ul>
      </div>
    </section>"""
        + lp_related_blog_section(cfg.get("blog_slugs", []))
        + faq_section(cfg["faq"], alt=True)
        + cta_band(pre, cfg["cta_h2"], cfg["cta_body"], cfg["hero_cta"], note=cfg.get("cta_note", ""))
    )

    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{EN_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": cfg["breadcrumb_name"], "item": f"{EN_SITE_URL}{canonical}"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    ld = page_schema(
        service_schema(
            name=cfg["service_name"],
            description=cfg["description"],
            url=canonical,
            audience=cfg["audience"],
        ),
        faq_page_schema(cfg["faq"]),
        speakable_webpage_schema(canonical),
        breadcrumb_ld,
    )
    write(
        f"solutions/{slug}/index.html",
        shell(
            depth=2,
            title=cfg["title"],
            description=cfg["description"],
            canonical=canonical,
            active_nav=None,
            main=main,
            json_ld=ld,
        ),
    )

LP_CONFIGS: list[dict] = [
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): "nis2 betroffen prüfen" / "nis2 wer ist betroffen" (P1, hoch)
        "slug": "nis2",
        "du": False,
        "audience": "KMU und Mittelstand",
        "tag": "NIS2",
        "h1": "NIS2: Ist Ihr Unternehmen betroffen?",
        "lead": (
            "NIS2 verpflichtet deutlich mehr Unternehmen als bisher zur IT-Sicherheit – vor allem "
            "mittelständische Betriebe aus Sektoren wie Energie, Gesundheit, Transport, digitale "
            "Infrastruktur oder verarbeitendes Gewerbe ab bestimmten Mitarbeiter- und Umsatzgrößen. "
            "Wer betroffen ist, muss Risikomanagement-Maßnahmen nachweisen – die Geschäftsführung "
            "haftet dabei persönlich. Beraterium hilft Ihnen, Ihre Betroffenheit zu prüfen und die "
            "wichtigsten Risiken mit dem 3-Ebenen-Gefahrenkatalog in Euro bewertet sichtbar zu machen."
        ),
        "hero_cta": "Book a free intro call",
        "criteria_tag": "DIREKT-CHECK",
        "criteria_h2": "Welche Unternehmen müssen NIS2 umsetzen?",
        "criteria_intro": "Sie sind wahrscheinlich betroffen, wenn Ihr Unternehmen mindestens eines der folgenden Kriterien erfüllt:",
        "criteria": [
            "Mindestens 50 Mitarbeitende oder mehr als 10 Mio. € Jahresumsatz",
            "Tätigkeit in einem NIS2-Sektor (z. B. Energie, Gesundheit, Transport, digitale Infrastruktur, verarbeitendes Gewerbe, Abfallwirtschaft)",
            "Wichtiger Zulieferer eines bereits NIS2-pflichtigen Unternehmens",
            "Verarbeitung kritischer Daten oder Betrieb kritischer IT-Systeme",
        ],
        "stats_aria": "NIS2 in Zahlen",
        "stats": [
            ("Seit 12/2025", "ist NIS2 in Deutschland Pflicht"),
            ("Bis 10 Mio. €", "mögliches Bußgeld bei Verstößen"),
            ("Persönlich", "haftet die Geschäftsführung bei Pflichtverletzung"),
            ("Unter 2 %", "der KMU sind optimal gegen Cyberrisiken geschützt"),
        ],
        "pain_tag": "DIE FOLGEN VON NIS2",
        "pain_h2": "Was passiert, wenn Sie NIS2 ignorieren?",
        "pain_intro": "NIS2 ist kein Papiertiger. Wer die Anforderungen nicht erfüllt, riskiert mehr als ein Bußgeld.",
        "pain_cards": [
            ("Unklare Betroffenheit", "Ohne Prüfung wissen Sie nicht, ob Sie zur Sektorenliste gehören oder die Schwellenwerte erreichen – und verpassen Fristen unbemerkt."),
            ("Persönliche Haftung", "Bei Pflichtverletzung haftet nicht nur das Unternehmen, sondern die Geschäftsführung persönlich – zivil- und teils strafrechtlich."),
            ("Aktionismus statt Plan", "Ohne Priorisierung wird NIS2 zum teuren Compliance-Blindflug statt zu echtem Schutz vor den Risiken, die wirklich zählen."),
        ],
        "overview_tag": "SO HILFT BERATERIUM",
        "overview_h2": "Wie führt Beraterium Sie von der NIS2-Pflicht zur echten Sicherheit?",
        "overview_intro": (
            "NIS2-Konformität beginnt mit einem klaren Risikobild. Der 3-Ebenen-Gefahrenkatalog von "
            "Beraterium macht sichtbar, wo Ihr Unternehmen wirklich verwundbar ist – in Euro bewertet, "
            "nicht mit Ampelfarben."
        ),
        "overview_cards": [
            ("Die Methode", "Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.", "method/", "Zur Methode"),
            ("Risikoanalyse für KMU", "In rund 6 Wochen zu einem vollständigen, bankfähigen Risiko-Lagebild – inklusive NIS2-relevanter Cyberrisiken.", "services/smb/", "Zum Angebot für KMU"),
            ("Doppelte Garantie", "Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.", "benefit-guarantee/", "Zur Garantie"),
        ],
        "faq": [
            ("Welche Unternehmen müssen NIS2 umsetzen?", "Betroffen sind vor allem mittelständische und größere Unternehmen aus definierten Sektoren wie Energie, Gesundheit, Transport, digitaler Infrastruktur oder verarbeitendem Gewerbe – meist ab 50 Mitarbeitenden oder 10 Mio. € Jahresumsatz. Auch wichtige Zulieferer betroffener Unternehmen können erfasst sein."),
            ("Was passiert, wenn ein Unternehmen NIS2 ignoriert?", "Es drohen Bußgelder von bis zu 10 Mio. € oder einem Prozentsatz des Jahresumsatzes, je nach Einrichtungskategorie. Zusätzlich haftet die Geschäftsführung bei nachgewiesenen Pflichtverletzungen persönlich."),
            ("Was sind die Geschäftsführer-Pflichten nach NIS2?", "NIS2 macht Geschäftsführer persönlich haftbar für die Implementierung von Cybersicherheitsmaßnahmen. Zu den Pflichten gehören: technische und organisatorische Schutzmaßnahmen, BSI-Registrierung, Meldepflichten bei Vorfällen (24 Stunden Erstmeldung, 72 Stunden vollständige Meldung) und Schulung der Mitarbeitenden. Bei Verstößen drohen Bußgelder von bis zu 10 Mio. € oder 2 % des weltweiten Jahresumsatzes."),
            ("Was kostet die NIS2-Umsetzung ungefähr?", "Die Kosten hängen stark von der IT-Ausgangslage und der Unternehmensgröße ab. Der günstigste erste Schritt ist eine strukturierte Risikoanalyse, die zeigt, welche Maßnahmen wirklich notwendig sind – statt pauschal in alles zu investieren."),
            ("Wie prüfe ich, ob mein Unternehmen betroffen ist?", "Prüfen Sie Branche, Mitarbeiterzahl und Jahresumsatz gegen die NIS2-Sektorenliste und die Schwellenwerte. Im kostenlosen Erstgespräch bei Beraterium klären wir Ihre konkrete Betroffenheit in rund 30 Minuten."),
            ("Wer hilft KMU bei der NIS2-Betroffenheitsprüfung?", "Beraterium unterstützt mittelständische Unternehmen dabei, ihre NIS2-Betroffenheit zu klären und die zugrunde liegenden Cyberrisiken mit dem 3-Ebenen-Gefahrenkatalog in Euro zu bewerten – praxisnah statt bürokratisch."),
            ("Was ist der Unterschied zwischen NIS2-Compliance und klassischem Risikomanagement?", "NIS2 fordert konkrete Cybersicherheits- und Meldemaßnahmen, ersetzt aber kein umfassendes Risikomanagement. Beraterium ordnet NIS2-Anforderungen in ein vollständiges, priorisiertes Risikobild ein, statt sie isoliert abzuarbeiten."),
        ],
        "deep_sections": [
            {
                "tag": "PFLICHTEN IM ÜBERBLICK",
                "h2": "Was verlangt NIS2 konkret von betroffenen Unternehmen?",
                "intro": (
                    "NIS2 ist seit Dezember 2025 in Deutschland verbindlich und schreibt betroffenen Unternehmen einen "
                    "Katalog an Cybersicherheits-Pflichten vor. Im Kern geht es nicht um ein Zertifikat, sondern um "
                    "nachweisbares Risikomanagement: Sie müssen zeigen, dass Sie Ihre IT-Risiken kennen, bewerten und "
                    "mit angemessenen Maßnahmen behandeln."
                ),
                "paragraphs": [
                    "Die Geschäftsführung trägt dabei die persönliche Verantwortung – sie muss die Maßnahmen freigeben, ihre Umsetzung überwachen und sich selbst schulen lassen. Diese Pflicht lässt sich nicht vollständig an die IT-Abteilung oder externe Dienstleister delegieren.",
                ],
                "items": [
                    "Technische und organisatorische Schutzmaßnahmen: Risikoanalyse, Zugriffskontrollen, Verschlüsselung, Backup-Konzepte und Notfallpläne",
                    "Registrierung beim Bundesamt für Sicherheit in der Informationstechnik (BSI)",
                    "Meldepflichten bei erheblichen Sicherheitsvorfällen – mit festen Fristen ab 24 Stunden",
                    "Schulung von Geschäftsführung und Mitarbeitenden zu Cyberrisiken",
                    "Absicherung der Lieferkette: Sicherheitsanforderungen auch an kritische Zulieferer und Dienstleister",
                ],
            },
        ],
        "steps_section": {
            "tag": "IN 5 SCHRITTEN",
            "h2": "Wie prüfen Sie Ihre NIS2-Betroffenheit?",
            "intro": "Die Betroffenheitsprüfung folgt einer klaren Logik – Sektor, Größe, Lieferkette. In den meisten Fällen lässt sie sich in wenigen Tagen abschließen.",
            "steps": [
                ("Sektor prüfen", "Gleichen Sie Ihre Tätigkeit mit den NIS2-Sektorenlisten ab: Energie, Transport, Gesundheit, Wasser, digitale Infrastruktur, verarbeitendes Gewerbe, Abfallwirtschaft, Chemie, Ernährung und weitere."),
                ("Schwellenwerte prüfen", "Ab 50 Mitarbeitenden oder mehr als 10 Mio. € Jahresumsatz bzw. Bilanzsumme fallen Unternehmen aus den gelisteten Sektoren in der Regel unter NIS2."),
                ("Lieferkette prüfen", "Auch unterhalb der Schwellen können Sie betroffen sein – wenn Sie kritischer Zulieferer oder Dienstleister eines NIS2-pflichtigen Unternehmens sind, verlangt dieses Sicherheitsnachweise von Ihnen."),
                ("Einstufung klären", "NIS2 unterscheidet wesentliche und wichtige Einrichtungen – mit unterschiedlich strenger Aufsicht und Bußgeldrahmen (bis 10 Mio. € bzw. bis 7 Mio. €)."),
                ("Risikoanalyse starten", "Leiten Sie Maßnahmen aus Ihrem tatsächlichen Risikobild ab, statt Checklisten abzuarbeiten – so erfüllen Sie die Pflicht und gewinnen echte Sicherheit."),
            ],
        },
        "facts_table": {
            "tag": "MELDEFRISTEN",
            "h2": "Welche Meldefristen gelten bei Sicherheitsvorfällen?",
            "intro": "Bei einem erheblichen Sicherheitsvorfall läuft für NIS2-regulierte Unternehmen eine dreistufige Meldekette an das BSI. Parallel kann bei Verlust personenbezogener Daten die DSGVO-Meldung an die Datenschutzaufsicht (72 Stunden) fällig werden.",
            "caption": "NIS2-Meldefristen bei erheblichen Sicherheitsvorfällen",
            "headers": ["Frist", "Meldung", "Inhalt"],
            "rows": [
                ("<strong>24 Stunden</strong>", "Erstmeldung ans BSI", "Frühwarnung: Verdacht auf erheblichen Sicherheitsvorfall, erste Einschätzung ob Angriff oder Störung"),
                ("<strong>72 Stunden</strong>", "Bewertungsmeldung", "Erste Bewertung von Schweregrad und Auswirkungen, Indikatoren der Kompromittierung"),
                ("<strong>1 Monat</strong>", "Abschlussbericht", "Detaillierte Beschreibung des Vorfalls, Ursachen, ergriffene und laufende Gegenmaßnahmen"),
            ],
        },
        "blog_slugs": [
            "cyber-attack-what-to-do-smb",
            "business-security-risk-management-smb",
            "risk-management-consulting-smb-providers",
        ],
        "cta_h2": "Klären Sie Ihre NIS2-Betroffenheit – kostenlos und unverbindlich",
        "cta_body": "Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Sie erhalten unsere Methode erklärt und wissen danach, wo Sie stehen.",
        "title": "NIS2-Betroffenheit prüfen für KMU | Beraterium",
        "description": "Prüfen Sie, ob Ihr Unternehmen von der NIS2-Richtlinie betroffen ist – inklusive Pflichten, Fristen und Bußgeldern. Book a free intro call.",
        "service_name": "NIS2-Risikocheck für KMU",
        "breadcrumb_name": "NIS2-Betroffenheit",
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): unternehmensnachfolge planen / nachfolge mittelstand risiken
        "slug": "succession",
        "du": False,
        "audience": 'KMU und Mittelstand',
        "tag": 'NACHFOLGE',
        "h1": 'Welche Risiken entstehen bei der Unternehmensnachfolge?',
        "lead": (
            'Bis 2030 stehen in Deutschland rund 186.000 Unternehmensübergaben an – viele davon im '
            'Familienunternehmen des Mittelstands. Neben Steuer und Vertrag entscheidet ein drittes '
            'Risikofeld über Erfolg oder Scheitern: Wissenstransfer, Führungsakzeptanz und '
            'Finanzierungsstruktur. Beraterium hilft Ihnen, diese Risiken vor der Übergabe mit dem '
            '3-Ebenen-Gefahrenkatalog in Euro bewertet sichtbar zu machen.'
        ),
        "hero_cta": 'Book a free intro call',
        "criteria_tag": 'DIREKT-CHECK',
        "criteria_h2": 'Wann sollten Sie mit der Nachfolge-Risikoanalyse beginnen?',
        "criteria_intro": 'Sie sollten Ihre Nachfolge-Risiken jetzt strukturiert prüfen, wenn mindestens eines dieser Kriterien zutrifft:',
        "criteria": [
            'Übergabe ist in den nächsten 1–5 Jahren geplant oder bereits in Vorbereitung',
            'Operatives Wissen liegt bei einer Person – meist dem aktuellen Inhaber',
            'Kundenbeziehungen hängen stark am persönlichen Kontakt des Seniors',
            'Finanzierung, Haftung oder stille Reserven sind noch nicht transparent geklärt',
        ],
        "stats_aria": 'Unternehmensnachfolge in Zahlen',
        "stats": [
            ('186.000', 'anstehende Übergaben bis 2030 in Deutschland'),
            ('3 Felder', 'Wissen, Führung und Finanzierung gleichzeitig'),
            ('Jahre', 'können Nachfolge-Risiken unbemerkt schwelen'),
            ('Vor der Übergabe', 'ist der günstigste Zeitpunkt für einen Risiko-Check'),
        ],
        "pain_tag": 'DIE ÜBERSEHENEN RISIKEN',
        "pain_h2": 'Was passiert, wenn Sie nur Steuer und Vertrag planen?',
        "pain_intro": 'Die meisten Nachfolgeprojekte scheitern nicht am Kaufvertrag, sondern an Risiken, die erst nach der Übergabe sichtbar werden.',
        "pain_cards": [
            ('Wissen geht verloren', 'Implizites Führungswissen, Lieferantenbeziehungen und Entscheidungslogik sind selten dokumentiert – und verschwinden mit dem Senior.'),
            ('Vertrauen bricht ein', 'Mitarbeitende und Kunden müssen der neuen Führung vertrauen. Ohne aktive Übergabe wirkt der Wechsel wie ein Kontaktwechsel, nicht wie Kontinuität.'),
            ('Haftung überrascht', 'Ungeklärte Altlasten, stille Reserven oder Finanzierungslücken werden oft erst sichtbar, wenn Bank, Beirat oder Nachfolger nachfragen.'),
        ],
        "overview_tag": 'SO HILFT BERATERIUM',
        "overview_h2": 'Wie bereitet Beraterium Ihre Nachfolge bank- und beiratsfähig vor?',
        "overview_intro": (
            'Eine erfolgreiche Übergabe braucht ein klares Risikobild – nicht nur einen Vertrag. Der '
            '3-Ebenen-Gefahrenkatalog von Beraterium macht sichtbar, welche Risiken Ihre Nachfolge '
            'wirklich gefährden, in Euro bewertet und priorisiert.'
        ),
        "overview_cards": [
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'method/', 'Zur Methode'),
            ('Risikoanalyse für KMU', 'In rund 6 Wochen zu einem vollständigen, bankfähigen Risiko-Lagebild – inklusive Nachfolge-Risiken.', 'services/smb/', 'Zum Angebot für KMU'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.', 'benefit-guarantee/', 'Zur Garantie'),
        ],
        "faq": [
            ('Welche Risiken entstehen bei der Unternehmensnachfolge im Mittelstand?', 'Bei der Unternehmensnachfolge treten drei Risikofelder gleichzeitig auf: Wissenstransfer (implizites Führungswissen des Seniors geht verloren), Führungsakzeptanz (Mitarbeitende und Kunden müssen Vertrauen zur Nachfolge aufbauen) und Finanzierungsstruktur (oft ungeklärte Haftungsfragen oder stille Reserven). Eine strukturierte Risikoanalyse vor der Übergabe identifiziert diese Felder und priorisiert Maßnahmen.'),
            ('Welche Risiken hat ein KMU bei der Unternehmensnachfolge?', 'Bei der Unternehmensnachfolge entstehen drei Risikofelder gleichzeitig: Wissenstransfer (was geht mit dem Senior?), Führungskultur (wer hat wirklich die Autorität?) und Kundenbeziehungen (halten diese den Inhaberwechsel?). Ohne eine strukturierte Risikoanalyse vor der Übergabe werden diese Risiken oft erst sichtbar, wenn sie bereits wirtschaftlichen Schaden angerichtet haben.'),
            ('Was muss ich bei einer Betriebsübergabe beachten, um Risiken zu minimieren?', 'Eine Betriebsübergabe gelingt dann, wenn drei Bedingungen erfüllt sind: (1) Das operative Wissen des Übergebers ist dokumentiert und übertragbar. (2) Die Kundenbeziehungen werden aktiv übergeben — nicht einfach der Ansprechpartner getauscht. (3) Die Haftungsrisiken aus der Vergangenheit sind transparent gemacht. Beraterium erstellt einen strukturierten Übergabe-Risiko-Check.'),
            ('Was ist ein Generationenwechsel im Unternehmen und welche Risiken bringt er?', 'Ein Generationenwechsel im Unternehmen beschreibt den Übergang der Führung von einer Generation zur nächsten — oft innerhalb der Familie. Die größten Risiken sind nicht finanzieller Natur, sondern kultureller: Wenn Senior und Junior unterschiedliche Vorstellungen von Autorität, Tempo und Richtung haben, entstehen Lähmungseffekte, die Mitarbeitende und Kunden verunsichern. Beraterium analysiert diese Dynamiken als Teil des Nachfolge-Risiko-Checks.'),
            ('Wann sollte ich mit der Nachfolgeplanung aus Risikosicht beginnen?', 'Idealerweise 3–5 Jahre vor der geplanten Übergabe – spätestens aber, sobald ein Nachfolger feststeht oder die Übergabe konkret wird. Je früher Wissenslücken, Kundenabhängigkeiten und Finanzierungsfragen sichtbar werden, desto günstiger sind die Gegenmaßnahmen.'),
            ('Wer begleitet Unternehmensnachfolge aus Risiko-Sicht?', 'Beraterium unterstützt mittelständische Unternehmen dabei, Nachfolge-Risiken vor der Übergabe strukturiert zu erfassen und mit dem 3-Ebenen-Gefahrenkatalog in Euro zu bewerten – praxisnah statt nur steuerlich oder rechtlich.'),
            ('Was ist ein Generationenwechsel im Unternehmen und welche Risiken bringt er?', 'Ein Generationenwechsel beschreibt den Übergang der Führung von einer Generation zur nächsten – oft innerhalb der Familie. Die größten Risiken sind dabei nicht finanzieller, sondern kultureller Natur: Wenn Senior und Junior unterschiedliche Vorstellungen von Autorität, Tempo und Richtung haben, entstehen Lähmungseffekte, die Mitarbeitende und Kunden verunsichern. Beraterium analysiert diese Dynamiken als Teil des Nachfolge-Risiko-Checks.'),
        ],
        "deep_sections": [
            {
                "tag": "DIE DREI RISIKOFELDER",
                "h2": "Welche drei Risikofelder entstehen bei jeder Nachfolge?",
                "intro": (
                    "Jede Nachfolge – ob an ein Familienmitglied, das Management oder einen externen Käufer – trifft "
                    "dieselben drei Felder gleichzeitig. Steuer und Vertrag regeln keines davon."
                ),
                "items": [
                    "<strong>Wissenstransfer:</strong> Implizites Führungswissen, Lieferantenbeziehungen und Entscheidungslogik des Seniors sind selten dokumentiert – und verschwinden mit ihm, wenn sie nicht aktiv übertragen werden",
                    "<strong>Führungsakzeptanz:</strong> Mitarbeitende und Schlüsselkunden entscheiden selbst, ob sie dem Nachfolger folgen – ein Wechsel der Visitenkarte reicht nicht, Vertrauen muss aktiv übergeben werden",
                    "<strong>Finanzierungsstruktur:</strong> Stille Reserven, Altlasten und Haftungsfragen werden oft erst sichtbar, wenn Bank, Beirat oder Nachfolger nachfragen – dann unter Zeitdruck",
                ],
                "paragraphs": [
                    "Diese Felder betreffen die Phase vor und während der Übergabe. Was nach der formalen Übergabe schiefgehen kann – Rollenkonflikte, Generationsdynamik, gefühlte gegen formale Macht – ist ein eigenes Risikofeld, das im Beraterium-Blog vertieft wird.",
                ],
            },
            {
                "tag": "BANK & BEIRAT",
                "h2": "Wie wird Ihre Nachfolge bank- und beiratsfähig?",
                "intro": (
                    "Banken und Beiräte wollen vor einer Nachfolgefinanzierung drei Dinge wissen: Was kann schiefgehen, "
                    "was kostet es, und was wird dagegen getan? Ein Risiko-Portfolio-Report aus der Beraterium-Methode "
                    "liefert genau das – priorisierte Risiken in Euro, mit Maßnahmen und Verantwortlichkeiten."
                ),
                "items": [
                    "Ausfall des Übergebers während der Übergangsphase – bewertet als Schlüsselpersonrisiko in Euro",
                    "Abwanderung von Schlüsselkunden oder Leistungsträgern beim Führungswechsel",
                    "Ungeklärte Gewährleistungen, laufende Verfahren und steuerliche Altlasten",
                    "Finanzierungslücken durch stille Reserven oder zu optimistische Kaufpreisannahmen",
                ],
                "paragraphs": [
                    "Das Ergebnis ist kein Gutachten für die Schublade, sondern ein Arbeitsdokument für die 12–18 Monate vor der Übergabe – vorzeigbar gegenüber Bank, Beirat und Nachfolger.",
                ],
            },
        ],
        "steps_section": {
            "tag": "ÜBERGABE-CHECKLISTE",
            "h2": "Wie bereiten Sie die Übergabe strukturiert vor?",
            "intro": "Diese sechs Schritte decken die häufigsten Nachfolge-Risiken ab – idealerweise beginnen Sie 3–5 Jahre vor der geplanten Übergabe.",
            "steps": [
                ("Wissen dokumentieren", "Erfassen Sie das operative Wissen des Übergebers systematisch: Entscheidungslogik, Lieferantenkonditionen, Preisfindung, ungeschriebene Regeln. Was nur im Kopf existiert, geht verloren."),
                ("Kundenbeziehungen übergeben", "Führen Sie den Nachfolger persönlich bei den wichtigsten Kunden ein – gemeinsame Termine statt einer E-Mail. Kunden folgen Menschen, nicht Firmennamen."),
                ("Haftung transparent machen", "Klären Sie vor dem Vertragsabschluss, was aus der Vergangenheit den Nachfolger treffen kann: Gewährleistungen, laufende Verfahren, steuerliche Altlasten."),
                ("Finanzierung realistisch planen", "Lassen Sie stille Reserven und Kaufpreis von unabhängiger Seite prüfen – zu optimistische Annahmen sind eine der häufigsten Ursachen für spätere Finanzierungslücken."),
                ("Führung schrittweise abgeben", "Definieren Sie, welche Entscheidungen ab wann beim Nachfolger liegen – und halten Sie sich daran. Parallele Machtstrukturen lähmen Mitarbeitende und verunsichern Kunden."),
                ("Risikobild erstellen", "Erfassen Sie alle Nachfolge-Risiken in einem priorisierten Portfolio in Euro – als Arbeitsgrundlage für die Übergabe und als Nachweis für Bank und Beirat."),
            ],
        },
        "blog_slugs": [
            "business-succession-overlooked-risks",
            "family-succession-generational-conflict-risk",
            "key-person-risk-identify-mitigate",
        ],
        "cta_h2": 'Klären Sie Ihre Nachfolge-Risiken – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Sie erhalten unsere Methode erklärt und wissen danach, wo Sie stehen.',
        "title": 'Nachfolge-Risiken im Mittelstand | Beraterium',
        "description": 'Unternehmensnachfolge: übersehene Risiken erkennen und in Euro bewerten. 186.000 Übergaben bis 2030. Kostenloses Erstgespräch bei Beraterium buchen.',
        "service_name": 'Nachfolge-Risikoanalyse für KMU',
        "breadcrumb_name": 'Unternehmensnachfolge',
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): cyberangriff unternehmen was tun / cyberangriff mittelstand schutz
        "slug": "cyber-attack",
        "du": False,
        "audience": 'KMU und Mittelstand',
        "tag": 'CYBERANGRIFF',
        "h1": 'Was tun nach einem Cyberangriff auf Ihr Unternehmen?',
        "lead": (
            'Cyberangriffe sind das häufigste existenzielle Risiko für mittelständische Unternehmen – '
            'und weniger als 2 % der KMU sind optimal geschützt. Im Ernstfall zählen die ersten zwei '
            'Stunden: isolieren, nicht selbst löschen, Experten hinzuziehen, melden. Beraterium hilft '
            'Ihnen, Cyberrisiken vorab zu bewerten und eine Reaktionskette zu planen – in Euro '
            'bewertet, nicht mit Ampelfarben.'
        ),
        "hero_cta": 'Book a free intro call',
        "criteria_tag": 'DIREKT-CHECK',
        "criteria_h2": 'Wann ist Ihr Unternehmen besonders angreifbar?',
        "criteria_intro": 'Ihr Cyberrisiko ist besonders hoch, wenn mindestens eines dieser Kriterien zutrifft:',
        "criteria": [
            'Keine eigene IT-Abteilung oder kein dedizierter IT-Sicherheitsverantwortlicher',
            'Kritische Daten, Kundeninformationen oder Produktionssysteme sind digital vernetzt',
            'Mitarbeitende arbeiten remote oder nutzen private Geräte für Firmendaten',
            'Es gibt keinen getesteten Notfallplan für IT-Sicherheitsvorfälle',
        ],
        "stats_aria": 'Cyberrisiko im Mittelstand',
        "stats": [
            ('#1 Risiko', 'Cyberangriffe sind das häufigste existenzielle KMU-Risiko'),
            ('Unter 2 %', 'der KMU sind optimal gegen Cyberrisiken geschützt'),
            ('2 Stunden', 'entscheiden im Ernstfall über Schadensumfang'),
            ('24/72 h', 'Meldefristen bei NIS2-pflichtigen Unternehmen'),
        ],
        "pain_tag": 'DIE FOLGEN EINES ANGRIFFS',
        "pain_h2": 'Was passiert, wenn Sie unvorbereitet sind?',
        "pain_intro": 'Ohne Vorbereitung verlieren Unternehmen im Ernstfall wertvolle Zeit – und oft mehr Geld als der Angriff selbst kostet.',
        "pain_cards": [
            ('Panik statt Plan', 'Ohne vorbereitete Reaktionskette wird im Ernstfall improvisiert – Systeme werden falsch heruntergefahren oder Beweise vernichtet.'),
            ('Stillstand kostet', 'Produktionsausfall, gesperrte Systeme und Datenverlust treffen KMU härter als Konzerne – jeder Ausfalltag kostet direkt Umsatz.'),
            ('Meldepflicht überrascht', 'NIS2-pflichtige Unternehmen müssen Vorfälle innerhalb von 24 Stunden melden. Ohne Vorbereitung verpassen Sie Fristen und riskieren Bußgelder.'),
        ],
        "overview_tag": 'SO HILFT BERATERIUM',
        "overview_h2": 'Wie macht Beraterium Cyberrisiken handlungsfähig?',
        "overview_intro": (
            'Cybersicherheit beginnt mit einem klaren Risikobild. Der 3-Ebenen-Gefahrenkatalog von '
            'Beraterium bewertet Ihre Cyberrisiken in Euro – und priorisiert Maßnahmen, die wirklich '
            'Schaden verhindern, statt Compliance-Blindflug.'
        ),
        "overview_cards": [
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'method/', 'Zur Methode'),
            ('Risikoanalyse für KMU', 'In rund 6 Wochen zu einem vollständigen, bankfähigen Risiko-Lagebild – inklusive Cyber- und NIS2-Risiken.', 'services/smb/', 'Zum Angebot für KMU'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.', 'benefit-guarantee/', 'Zur Garantie'),
        ],
        "faq": [
            ('Was tun, wenn mein Unternehmen von einem Cyberangriff betroffen ist?', 'Im Ernstfall zählen die ersten 2 Stunden: betroffene Systeme isolieren (Netzwerk trennen), nicht selbst versuchen zu löschen oder zu entschlüsseln, IT-Sicherheitsexperten hinzuziehen und bei schweren Angriffen das BSI sowie die Polizei informieren. Danach folgt die Schadenserfassung. Beraterium unterstützt KMU dabei, diese Reaktionskette vorab zu planen — damit im Ernstfall niemand raten muss.'),
            ('Was sind die ersten Sofortmaßnahmen bei einem Cyberangriff?', 'Isolieren Sie betroffene Systeme vom Netzwerk, dokumentieren Sie den Zeitpunkt und Umfang, ziehen Sie IT-Sicherheitsexperten hinzu und informieren Sie bei schweren Vorfällen BSI und Polizei. Löschen oder entschlüsseln Sie nichts selbst – das kann Beweise vernichten.'),
            ('Wie schütze ich mein KMU präventiv ohne eigene IT-Abteilung?', 'Beginnen Sie mit einer strukturierten Risikoanalyse: Welche Systeme sind kritisch, welcher Schaden entsteht bei Ausfall, welche Maßnahmen bringen den größten Nutzen? Beraterium priorisiert diese Schritte in Euro bewertet – statt pauschal in teure Tools zu investieren.'),
            ('Wie hängen Cyberangriffe und NIS2 zusammen?', 'NIS2 verpflichtet betroffene Unternehmen zu Cybersicherheitsmaßnahmen und Meldepflichten bei Vorfällen. Ein Cyberangriff kann gleichzeitig NIS2-Meldepflichten auslösen. Beraterium ordnet Cyberrisiken in ein vollständiges Risikobild ein – inklusive NIS2-Anforderungen.'),
            ('Was kostet ein Cyberangriff für ein mittelständisches Unternehmen?', 'Die Kosten variieren stark – von einigen tausend Euro bei kleineren Vorfällen bis zu existenzbedrohenden Beträgen bei Ransomware mit Produktionsausfall. Eine Euro-Bewertung vorab zeigt, welche Szenarien für Ihr Unternehmen wirklich kritisch sind.'),
            ('Wer hilft KMU bei der Cyberrisiko-Bewertung?', 'Beraterium unterstützt mittelständische Unternehmen dabei, Cyberrisiken mit dem 3-Ebenen-Gefahrenkatalog in Euro zu bewerten und eine handlungsfähige Reaktionskette zu planen – praxisnah statt bürokratisch.'),
        ],
        "deep_sections": [
            {
                "tag": "WARUM DER MITTELSTAND?",
                "h2": "Warum trifft es besonders kleine und mittlere Unternehmen?",
                "intro": (
                    "Rund 82 % aller Ransomware-Angriffe treffen kleine Unternehmen – nicht, weil sie lukrativer wären, "
                    "sondern weil sie schlechter geschützt sind. Angreifer automatisieren ihre Attacken und nehmen den "
                    "Weg des geringsten Widerstands: Betriebe ohne IT-Abteilung, ohne getestete Backups und ohne "
                    "sensibilisierte Mitarbeitende."
                ),
                "paragraphs": [
                    "Dazu kommt der Faktor Mensch: 40–50 % aller erfolgreichen Cyberangriffe beginnen mit menschlichem Fehlverhalten – ein geöffneter Anhang, ein gescannter QR-Code (Quishing), ein zu einfaches Passwort. Neue Angriffsformen wie QR-Code-Phishing umgehen dabei klassische Sicherheitsfilter komplett, weil Virenscanner den Code nur als Bild sehen.",
                    "Für KMU ist der Schaden dabei überproportional: Während Konzerne einen mehrtägigen Ausfall abfedern, kostet jeder Stillstandstag ein mittelständisches Unternehmen direkt Umsatz – und die Wiederherstellung ist oft teurer als der eigentliche Angriff.",
                ],
            },
            {
                "tag": "PRÄVENTION",
                "h2": "Wie schützen Sie sich präventiv – ohne eigene IT-Abteilung?",
                "intro": (
                    "Wirksame Prävention beginnt nicht mit teuren Tools, sondern mit einem klaren Risikobild: Welche "
                    "Systeme sind kritisch, welcher Schaden entsteht bei Ausfall, welche Maßnahme senkt das Risiko am "
                    "stärksten? Vier Grundmaßnahmen decken die häufigsten Angriffswege ab:"
                ),
                "items": [
                    "3-2-1-Backup-Regel: drei Kopien Ihrer Daten, auf zwei verschiedenen Medien, eine davon offline – für Ransomware unerreichbar",
                    "Mitarbeitersensibilisierung: Phishing, Quishing und Passwortsicherheit regelmäßig schulen – erklären statt kontrollieren schafft Akzeptanz",
                    "Zugriffe limitieren: jede Person erhält nur die Rechte, die sie wirklich braucht – das begrenzt den Schaden kompromittierter Konten",
                    "Getesteter Notfallplan: wer im Ernstfall was tut, muss vorher feststehen – inklusive Erreichbarkeiten, Dienstleistern und Meldewegen",
                ],
            },
        ],
        "steps_section": {
            "tag": "DIE ERSTEN 2 STUNDEN",
            "h2": "Was tun Sie unmittelbar nach einem Cyberangriff?",
            "intro": "Im Ernstfall entscheiden die ersten zwei Stunden über den Schadensumfang. Diese Reaktionskette sollte jede Führungskraft kennen – bevor sie gebraucht wird.",
            "steps": [
                ("Systeme isolieren", "Trennen Sie betroffene Rechner und Server sofort vom Netzwerk – Kabel ziehen, WLAN deaktivieren. So stoppen Sie die Ausbreitung, ohne Beweise zu vernichten."),
                ("Zeitpunkt dokumentieren", "Halten Sie fest, wann was aufgefallen ist, welche Systeme betroffen sind und welche Meldungen auf den Bildschirmen stehen – Fotos genügen."),
                ("Nichts selbst löschen", "Versuchen Sie nicht, Schadsoftware zu entfernen oder Daten zu entschlüsseln – das vernichtet forensische Beweise und kann den Schaden vergrößern."),
                ("Experten hinzuziehen", "Kontaktieren Sie IT-Sicherheitsexperten – über Ihre Cyber-Versicherung, Ihren IT-Dienstleister oder die Zentrale Ansprechstelle Cybercrime (ZAC) der Landespolizei."),
                ("Meldungen absetzen", "Prüfen Sie die Meldepflichten: Datenschutzaufsicht bei Personendaten, BSI bei NIS2-Pflicht, Cyber-Versicherung immer sofort – sonst riskieren Sie den Versicherungsschutz."),
            ],
        },
        "facts_table": {
            "tag": "MELDEPFLICHTEN",
            "h2": "Wen müssen Sie informieren – und bis wann?",
            "intro": "Nach einem Angriff laufen mehrere Meldefristen parallel. Diese Übersicht zeigt, welche Stelle wann informiert werden muss.",
            "caption": "Meldepflichten nach einem Cyberangriff",
            "headers": ["Stelle", "Frist", "Wann relevant"],
            "rows": [
                ("Datenschutzaufsicht (DSGVO Art. 33)", "<strong>72 Stunden</strong>", "Bei Verlust oder Kompromittierung personenbezogener Daten"),
                ("BSI (NIS2)", "<strong>24 h</strong> Erstmeldung, <strong>72 h</strong> Bewertung, <strong>1 Monat</strong> Abschlussbericht", "Nur für NIS2-regulierte Unternehmen bei erheblichen Vorfällen"),
                ("Polizei / ZAC", "Keine Frist – sofort empfohlen", "Bei jedem Angriff mit Schaden; die ZAC arbeitet diskret und auf Unternehmen spezialisiert"),
                ("Cyber-Versicherung", "<strong>Sofort</strong>", "Immer – verspätete Meldung gefährdet den Versicherungsschutz; viele Policen stellen eigene Incident-Response-Teams"),
            ],
        },
        "blog_slugs": [
            "cyber-attack-what-to-do-smb",
            "business-security-risk-management-smb",
            "key-person-risk-identify-mitigate",
        ],
        "cta_h2": 'Bewerten Sie Ihr Cyberrisiko – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Sie erhalten unsere Methode erklärt und wissen danach, wo Sie stehen.',
        "title": 'Cyberangriff Mittelstand: Was tun? | Beraterium',
        "description": 'Cyberangriff im Mittelstand: Was droht und was Sie tun können? Risiken in Euro bewertet. Jetzt kostenloses Erstgespräch bei Beraterium buchen.',
        "service_name": 'Cyberrisiko-Analyse für KMU',
        "breadcrumb_name": 'Cyberangriff',
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): selbstständig absichern / risiken selbstständigkeit
        "slug": "self-employed-protection",
        "du": True,
        "audience": 'Solo-Selbstständige und Freelancer',
        "tag": 'SELBSTSTÄNDIGKEIT',
        "h1": 'Wie sicherst du dich als Selbstständiger ab?',
        "lead": (
            'Als Selbstständiger bist du dein Unternehmen – fällst du aus, fällt der Umsatz aus. Die '
            'drei größten Risiken: eigene Arbeitskraft (Krankheit, Burnout, Unfall), '
            'Kundenkonzentration und Scheinselbstständigkeit. Beraterium hilft dir, diese Risiken mit '
            'dem 2-Wochen-Risiko-Kompass in Euro bewertet sichtbar zu machen – bevor der Ernstfall '
            'eintritt.'
        ),
        "hero_cta": 'Book a free intro call',
        "criteria_tag": 'DIREKT-CHECK',
        "criteria_h2": 'Wann solltest du deine Absicherung prüfen?',
        "criteria_intro": 'Du solltest deine Risiken jetzt strukturiert prüfen, wenn mindestens eines dieser Kriterien zutrifft:',
        "criteria": [
            'Ein Hauptkunde macht mehr als 40 % deines Umsatzes aus',
            'Du hast keine Vertretung für Krankheit oder Urlaub',
            'Du arbeitest überwiegend für einen Auftraggeber',
            'Deine Rücklagen reichen nicht für 3–6 Monate Ausfall',
        ],
        "stats_aria": 'Selbstständigkeit in Zahlen',
        "stats": [
            ('0 Tage', 'Lohnfortzahlung – Ausfall = Einkommensausfall'),
            ('83 %', 'Umsatz von einem Kunden = Scheinselbstständigkeits-Risiko'),
            ('4–6 Wochen', 'Krankheit können existenzbedrohend werden'),
            ('2 Wochen', 'Risiko-Kompass von Beraterium für Solo'),
        ],
        "pain_tag": 'DIE DREI HAUPTRISIKEN',
        "pain_h2": 'Was passiert, wenn du nichts vorbereitest?',
        "pain_intro": 'Als Solo-Selbstständiger trägst du jedes Risiko allein – ohne Betriebsrat, ohne IT-Abteilung, ohne Vertretung.',
        "pain_cards": [
            ('Du fällst aus', 'Krankheit, Burnout oder Unfall stoppen sofort dein Einkommen – während Miete, Versicherungen und Software weiterlaufen.'),
            ('Ein Kunde fällt weg', 'Wenn ein Hauptkunde kündigt, bricht der Umsatz ein. Ohne Diversifikation reicht ein Vertrag, um deine Existenz zu gefährden.'),
            ('Scheinselbstständigkeit droht', 'Die Deutsche Rentenversicherung kann rückwirkend Sozialversicherungsbeiträge über Jahre nachfordern – oft erst Jahre später.'),
        ],
        "overview_tag": 'SO HILFT BERATERIUM',
        "overview_h2": 'Wie hilft dir Beraterium, handlungsfähig abgesichert zu sein?',
        "overview_intro": (
            'Absicherung beginnt mit einem klaren Bild deiner Risiken. Der 2-Wochen-Risiko-Kompass '
            'von Beraterium deckt Ausfall, Kundenkonzentration und Scheinselbstständigkeit auf – in '
            'Euro bewertet, mit konkreten nächsten Schritten. Du willst erst einmal selbst testen, '
            'wo du stehst? Der kostenlose <a href="../../tools/blindspot-check/">Blindspot Check</a> '
            'zeigt dir in 10 Minuten deine größten blinden Flecken.'
        ),
        "overview_cards": [
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'method/', 'Zur Methode'),
            ('2-Wochen-Risiko-Kompass', 'In zwei Wochen zu einem vollständigen Risiko-Lagebild – speziell für Solo-Selbstständige und Freelancer.', 'services/solo/', 'Zum Solo-Angebot'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Du erhältst den vollen Betrag zurück.', 'benefit-guarantee/', 'Zur Garantie'),
        ],
        "faq": [
            ('Was sind die größten Risiken für Selbstständige und Freelancer?', 'Die drei größten Risiken für Solo-Selbstständige sind: (1) Ausfall der eigenen Arbeitskraft — durch Krankheit, Burnout oder Unfall — ohne Vertretung und ohne Gehaltsfortzahlung; (2) Kundenkonzentration — wenn ein Hauptkunde wegbricht, bricht der Umsatz weg; (3) Scheinselbstständigkeit — eine rückwirkende Feststellung kostet Sozialversicherungsbeiträge über mehrere Jahre. Der 2-Wochen-Risiko-Kompass von Beraterium deckt alle drei auf.'),
            ('Was passiert, wenn ich als Selbstständiger krank werde?', 'Als Selbstständiger gibt es keine Lohnfortzahlung — fällt die Arbeit aus, fällt auch das Einkommen aus. Gleichzeitig laufen fixe Kosten (Miete, Versicherungen, Software) weiter. Ohne Notfallplan und ausreichende Rücklagen kann schon ein 4–6-wöchiger Ausfall existenzbedrohend werden. Beraterium hilft, dieses Szenario konkret zu bewerten und einen Notfallplan zu entwickeln — bevor der Ernstfall eintritt.'),
            ('Was ist Scheinselbstständigkeit und wie prüfe ich, ob ich betroffen bin?', 'Scheinselbstständigkeit liegt vor, wenn jemand formal als Freelancer arbeitet, aber tatsächlich wie ein Angestellter in ein Unternehmen eingebunden ist — erkennbar an Kriterien wie ausschließlich einem Auftraggeber, festen Arbeitszeiten und weisungsgebundener Arbeit. Die Deutsche Rentenversicherung kann rückwirkend Sozialversicherungsbeiträge über Jahre nachfordern. Beraterium bewertet das Scheinselbstständigkeitsrisiko als Teil des Solo-Risiko-Kompasses.'),
            ('Wie viele Auftraggeber brauche ich, um Scheinselbstständigkeit zu vermeiden?', 'Es gibt keine gesetzliche Mindestanzahl, aber die Praxis der Deutschen Rentenversicherung zeigt: Wer mehr als 83 % seines Umsatzes von einem Auftraggeber erzielt, gerät schnell unter Verdacht. Wichtiger als die reine Zahl ist die Art der Zusammenarbeit — Weisungsbindung, feste Arbeitszeiten und fehlende unternehmerische Eigenständigkeit sind stärkere Indizien als die Auftraggeberanzahl allein.'),
            ('Wie viele Rücklagen sollte ich als Selbstständiger aufbauen?', 'Als Faustregel: mindestens 3–6 Monatsausgaben als Notreserve. Die genaue Höhe hängt von deinen Fixkosten, Krankenversicherung und Kundenkonzentration ab. Beraterium bewertet dein persönliches Ausfallszenario in Euro – statt mit pauschalen Prozentregeln.'),
            ('Wer hilft Selbstständigen bei der Risiko-Absicherung?', 'Beraterium unterstützt Solo-Selbstständige und Freelancer mit dem 2-Wochen-Risiko-Kompass – Ausfall, Kundenkonzentration und Scheinselbstständigkeit in Euro bewertet, mit konkreten nächsten Schritten.'),
        ],
        "deep_sections": [
            {
                "tag": "DIE DREI KERNRISIKEN",
                "h2": "Warum sind genau diese drei Risiken existenziell?",
                "intro": (
                    "Als Solo-Selbstständiger bist du dein Unternehmen – Person und Betrieb sind identisch. Deshalb "
                    "wirken drei Risiken bei dir anders als in jedem anderen Unternehmen: Sie treffen nicht eine "
                    "Abteilung, sondern sofort dein gesamtes Einkommen."
                ),
                "items": [
                    "<strong>Ausfall der Arbeitskraft:</strong> Es gibt keine Lohnfortzahlung und keine Vertretung – schon 4–6 Wochen Krankheit oder Burnout können existenzbedrohend werden, während Miete, Versicherungen und Software weiterlaufen",
                    "<strong>Kundenkonzentration:</strong> Macht ein Hauptkunde mehr als 40 % deines Umsatzes aus, entscheidet dessen Budgetplanung über deine Existenz – ein einziger gekündigter Vertrag reicht",
                    "<strong>Scheinselbstständigkeit:</strong> Die Deutsche Rentenversicherung kann rückwirkend Sozialversicherungsbeiträge über Jahre nachfordern – oft fünfstellige Beträge, die ohne Rücklagen nicht zu stemmen sind",
                ],
            },
            {
                "tag": "SCHEINSELBSTSTÄNDIGKEIT",
                "h2": "Woran erkennst du ein Scheinselbstständigkeits-Risiko?",
                "intro": (
                    "Scheinselbstständigkeit liegt vor, wenn du formal als Freelancer arbeitest, aber tatsächlich wie "
                    "ein Angestellter in ein Unternehmen eingebunden bist. Die Praxis der Deutschen Rentenversicherung "
                    "zeigt: Wer mehr als 83 % seines Umsatzes von einem Auftraggeber erzielt, gerät schnell unter "
                    "Verdacht. Diese Kriterien sind die stärksten Indizien:"
                ),
                "items": [
                    "Du arbeitest überwiegend oder ausschließlich für einen Auftraggeber",
                    "Du bist an feste Arbeitszeiten oder Anwesenheitspflichten gebunden",
                    "Du arbeitest weisungsgebunden – der Auftraggeber bestimmt, wie du arbeitest, nicht nur was",
                    "Du bist in Teams, Tools und Prozesse des Auftraggebers eingebunden wie Festangestellte",
                    "Du trägst kein unternehmerisches Risiko und trittst nicht am Markt auf (keine eigene Website, keine weiteren Kunden-Akquise)",
                ],
                "paragraphs": [
                    "Wichtiger als die reine Auftraggeberzahl ist die Art der Zusammenarbeit. Bei Unsicherheit schafft eine Statusfeststellung bei der Deutschen Rentenversicherung Klarheit – besser proaktiv als in einer Betriebsprüfung.",
                ],
            },
        ],
        "steps_section": {
            "tag": "DIESE WOCHE MACHBAR",
            "h2": "Was kannst du sofort für deine Absicherung tun?",
            "intro": "Absicherung muss nicht mit einem großen Projekt beginnen. Diese fünf Schritte kannst du diese Woche anstoßen – jeder einzelne senkt dein Risiko messbar.",
            "steps": [
                ("Kundenanteile ausrechnen", "Rechne aus, wie viel Prozent deines Umsatzes jeder Kunde ausmacht. Liegt einer über 40 %, ist Diversifikation deine wichtigste Baustelle – plane aktiv Akquise-Zeit ein."),
                ("Rücklagen-Reichweite prüfen", "Teile deine Rücklagen durch deine monatlichen Fixkosten. Weniger als 3 Monate Reichweite heißt: Sparrate erhöhen, bevor du in andere Absicherung investierst."),
                ("Verträge prüfen", "Prüfe deine Rahmenverträge auf Scheinselbstständigkeits-Indizien: Weisungsbindung, feste Zeiten, Exklusivität. Formulierungen lassen sich oft nachverhandeln."),
                ("Notfallkontakte klären", "Wer informiert deine Kunden, wenn du morgen ausfällst? Ein Kollege, Partner oder Netzwerk-Kontakt mit Zugriff auf eine simple Notfall-Liste genügt für den Anfang."),
                ("Risikobild erstellen", "Bewerte deine drei Kernrisiken in Euro – selbst mit dem kostenlosen Blindspot Check oder strukturiert mit dem 2-Wochen-Risiko-Kompass von Beraterium."),
            ],
        },
        "blog_slugs": [
            "risks-self-employed-freelancers",
            "false-self-employment-check",
            "key-person-risk-identify-mitigate",
        ],
        "cta_h2": 'Prüfe deine Absicherung – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Du erhältst unsere Methode erklärt und weißt danach, wo du stehst.',
        "title": 'Selbstständig absichern: Ausfallrisiko | Beraterium',
        "description": 'Selbstständig absichern: Ausfallrisiko und Kundenkonzentration in Euro bewertet. Der 2-Wochen-Risiko-Kompass. Book a free intro call.',
        "service_name": '2-Wochen-Risiko-Kompass für Solo',
        "breadcrumb_name": 'Selbstständig absichern',
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): schlüsselperson absichern unternehmen / key person risiko
        "slug": "key-person-risk",
        "du": False,
        "audience": 'KMU, Startups und Solo-Selbstständige',
        "tag": 'SCHLÜSSELPERSON',
        "h1": 'Was passiert, wenn eine Schlüsselperson ausfällt?',
        "lead": (
            'Das Schlüsselpersonrisiko beschreibt den wirtschaftlichen Schaden, der entsteht, wenn '
            'eine für das Unternehmen unverzichtbare Person langfristig ausfällt – durch Krankheit, '
            'Kündigung oder Tod. In KMU ist das oft die Geschäftsführung, in Startups der Gründer, '
            'bei Solo-Selbstständigen sind Sie die Schlüsselperson selbst. Beraterium erfasst diese '
            'Abhängigkeiten mit dem 3-Ebenen-Gefahrenkatalog in Euro.'
        ),
        "hero_cta": 'Book a free intro call',
        "criteria_tag": 'DIREKT-CHECK',
        "criteria_h2": 'Wann ist Ihr Unternehmen von Schlüsselpersonen abhängig?',
        "criteria_intro": 'Sie haben ein relevantes Schlüsselpersonrisiko, wenn mindestens eines dieser Kriterien zutrifft:',
        "criteria": [
            'Eine Person trägt Wissen, das nirgends dokumentiert ist',
            'Kundenbeziehungen hängen an einer einzelnen Ansprechperson',
            'Entscheidungen stocken, wenn eine bestimmte Person fehlt',
            'Es gibt keine dokumentierte Vertretungsregelung',
        ],
        "stats_aria": 'Schlüsselpersonrisiko in Zahlen',
        "stats": [
            ('1 Person', 'kann in KMU das gesamte Unternehmen lahmlegen'),
            ('40–50 %', 'der Startup-Teams erleben Co-Founder-Trennung'),
            ('Solo', 'bist du selbst die Schlüsselperson'),
            ('Euro', 'bewertet Beraterium den Schaden – nicht mit Ampeln'),
        ],
        "pain_tag": 'DIE FOLGEN DES AUSFALLS',
        "pain_h2": 'Was passiert, wenn die Schlüsselperson wegbricht?',
        "pain_intro": 'Der Ausfall einer Schlüsselperson trifft Unternehmen härter als viele andere Risiken – weil Wissen, Beziehungen und Entscheidungsfähigkeit gleichzeitig wegfallen.',
        "pain_cards": [
            ('Wissen verschwindet', 'Implizites Know-how, Lieferantenbeziehungen und Entscheidungslogik sind selten dokumentiert – und gehen mit der Person verloren.'),
            ('Kunden verunsichern', 'Wenn die persönliche Ansprechperson fehlt, verlieren Kunden Vertrauen – besonders in KMU und bei Startups mit wenigen Großkunden.'),
            ('Entscheidungen stocken', 'Ohne Vertretungsregelung warten Projekte, Lieferungen und strategische Entscheidungen – jeder Tag kostet Umsatz.'),
        ],
        "overview_tag": 'SO HILFT BERATERIUM',
        "overview_h2": 'Wie macht Beraterium Schlüsselpersonrisiken sichtbar?',
        "overview_intro": (
            'Schlüsselpersonrisiken lassen sich systematisch erfassen. Der 3-Ebenen-Gefahrenkatalog '
            'von Beraterium identifiziert, welche Personen welche einzigartigen Funktionen tragen – '
            'in Euro bewertet, mit Maßnahmen zur Wissensverteilung und Vertretung.'
        ),
        "overview_cards": [
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'method/', 'Zur Methode'),
            ('Angebote für jede Zielgruppe', 'Ob KMU, Startup oder Solo – Beraterium hat ein passendes Risiko-Angebot für Ihre Situation.', 'services/', 'Zu den Angeboten'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.', 'benefit-guarantee/', 'Zur Garantie'),
        ],
        "faq": [
            ('Was ist das Schlüsselpersonrisiko und wie schützt mein KMU sich dagegen?', 'Das Schlüsselpersonrisiko beschreibt den wirtschaftlichen Schaden, der entsteht, wenn eine für das Unternehmen unverzichtbare Person langfristig ausfällt — durch Krankheit, Kündigung oder Tod. In vielen KMU ist das die Geschäftsführung selbst. Beraterium erfasst im 3-Ebenen-Gefahrenkatalog systematisch, welche Personen welche einzigartigen Funktionen tragen, und entwickelt Maßnahmen zur Wissensverteilung oder -dokumentation.'),
            ('Wie zeigt sich Schlüsselpersonrisiko bei Startups?', 'Bei Startups konzentriert sich das Risiko oft auf Gründer und Co-Founder: Technisches Know-how, Kundenbeziehungen und strategische Entscheidungen hängen an wenigen Personen. Co-Founder-Konflikte treffen 40–50 % aller Teams. Beraterium erfasst Team-Risiken als eigene Kategorie im Gefahrenkatalog.'),
            ('Wie zeigt sich Schlüsselpersonrisiko bei Solo-Selbstständigen?', 'Bei Solo-Selbstständigen sind Sie selbst die Schlüsselperson – jeder Ausfall durch Krankheit, Burnout oder Unfall stoppt sofort Umsatz und Einkommen. Es gibt keine Vertretung und keine Lohnfortzahlung. Der 2-Wochen-Risiko-Kompass von Beraterium bewertet dieses Szenario konkret in Euro.'),
            ('Welche Sofortmaßnahmen reduzieren Schlüsselpersonrisiken?', 'Dokumentieren Sie kritisches Wissen, benennen Sie Vertretungen für jeden Kernprozess und verteilen Sie Kundenbeziehungen auf mindestens zwei Ansprechpersonen. Beraterium priorisiert diese Maßnahmen nach Euro-Schaden – nicht nach Bauchgefühl.'),
            ('Was kostet der Ausfall einer Schlüsselperson?', 'Der Schaden hängt von Branche, Unternehmensgröße und der Rolle der Person ab – von einigen tausend Euro bei kurzem Ausfall bis zu existenzbedrohenden Beträgen bei langfristigem Wegfall der Geschäftsführung. Eine Euro-Bewertung vorab macht das Szenario greifbar.'),
            ('Wer hilft bei der Schlüsselperson-Absicherung?', 'Beraterium unterstützt KMU, Startups und Solo-Selbstständige dabei, Schlüsselpersonrisiken mit dem 3-Ebenen-Gefahrenkatalog systematisch zu erfassen und in Euro zu bewerten – für jede Zielgruppe mit dem passenden Angebot.'),
        ],
        "deep_sections": [
            {
                "tag": "DEFINITION",
                "h2": "Was genau ist ein Schlüsselpersonrisiko?",
                "intro": (
                    "Das Schlüsselpersonrisiko beschreibt den wirtschaftlichen Schaden, der entsteht, wenn eine für das "
                    "Unternehmen unverzichtbare Person langfristig ausfällt – durch Krankheit, Kündigung, Unfall oder Tod. "
                    "Entscheidend ist nicht die Position auf dem Organigramm, sondern die Frage: Welche Funktion kann "
                    "niemand anderes kurzfristig übernehmen?"
                ),
                "paragraphs": [
                    "Typische Schlüsselpersonen sind die Geschäftsführung mit exklusiven Kundenbeziehungen, der Meister mit undokumentiertem Produktionswissen, die eine Person, die das ERP-System versteht – oder der Gründer, auf den Produktvision und Investorenvertrauen zugeschnitten sind.",
                    "Das Risiko bleibt oft jahrelang unsichtbar, weil im Alltag alles funktioniert. Sichtbar wird es erst im Ausfall – dann aber mit voller Wucht: Wissen, Beziehungen und Entscheidungsfähigkeit brechen gleichzeitig weg.",
                ],
            },
        ],
        "steps_section": {
            "tag": "IN 3 SCHRITTEN",
            "h2": "Wie erfasst der 3-Ebenen-Gefahrenkatalog Schlüsselpersonen?",
            "intro": "Im 3-Ebenen-Gefahrenkatalog von Beraterium ist der Ausfall von Schlüsselpersonen eine eigene Gefahrenklasse – neben externen Gefahren und internen Prozessrisiken. Die Analyse läuft in drei Schritten:",
            "steps": [
                ("Sammeln", "Welche Personen tragen welche einzigartigen Funktionen? Erfasst werden Wissen, Kundenbeziehungen, Entscheidungsbefugnisse und technische Abhängigkeiten – neutral, ohne vorschnelle Bewertung."),
                ("Bewerten", "„Stell dir vor, die Person fällt morgen aus“ – der mögliche Schaden wird in Euro geschätzt: Umsatzausfall, Wiederbeschaffungskosten, Vertrauensverlust bei Kunden, Projektverzögerungen."),
                ("Priorisieren", "Das Ergebnis fließt in die Risikomatrix ein und wird gegen alle anderen Risiken gestellt – etwa einen Cyberangriff oder Liquiditätsengpass. So landet das Budget bei dem Risiko, das wirklich am meisten kostet."),
            ],
        },
        "facts_table": {
            "tag": "DREI ZIELGRUPPEN",
            "h2": "Wie zeigt sich das Risiko bei KMU, Startup und Solo?",
            "intro": "Das Schlüsselpersonrisiko trifft jede Unternehmensform – aber in unterschiedlicher Ausprägung und mit unterschiedlichen Gegenmaßnahmen.",
            "caption": "Schlüsselpersonrisiko im Vergleich: KMU, Startup, Solo-Selbstständige",
            "headers": ["Zielgruppe", "Typische Ausprägung", "Wirksamste Maßnahme"],
            "rows": [
                ("<strong>KMU</strong>", "Geschäftsführung oder Meister mit exklusivem Wissen und persönlichen Kundenbeziehungen – ein Single Point of Failure im Tagesgeschäft", "Wissen dokumentieren, Vertretungsregelungen definieren, Kundenbeziehungen auf zwei Ansprechpersonen verteilen"),
                ("<strong>Startup</strong>", "Produktwissen und Investorenvertrauen konzentrieren sich auf die Gründer – verschärft durch Burnout-Risiko und Co-Founder-Konflikte (40–50 % der Teams)", "Rollen und Entscheidungsregeln schriftlich klären, technisches Wissen im Team verteilen, Key-Person-Frage vor der Due Diligence beantworten"),
                ("<strong>Solo</strong>", "Du bist selbst die Schlüsselperson – jeder Ausfalltag kostet direkt Umsatz, ohne Vertretung und ohne Lohnfortzahlung", "Rücklagen für 3–6 Monate, Notfallplan mit Vertretungsnetzwerk, Absicherung der Arbeitskraft prüfen"),
            ],
        },
        "blog_slugs": [
            "key-person-risk-identify-mitigate",
            "business-succession-overlooked-risks",
            "risks-self-employed-freelancers",
        ],
        "cta_h2": 'Bewerten Sie Ihr Schlüsselpersonrisiko – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Sie erhalten unsere Methode erklärt und wissen danach, wo Sie stehen.',
        "title": 'Schlüsselperson-Risiko erkennen | Beraterium',
        "description": 'Schlüsselperson-Risiko: Was passiert, wenn eine Person ausfällt? Schaden in Euro bewertet. Jetzt kostenloses Erstgespräch bei Beraterium buchen.',
        "service_name": 'Schlüsselperson-Risikoanalyse',
        "breadcrumb_name": 'Schlüsselperson-Risiko',
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): due diligence vorbereiten startup / startup due diligence checklist
        "slug": 'investor-due-diligence',
        "du": True,
        "audience": 'Startups und Gründer',
        "tag": 'DUE DILIGENCE',
        "h1": 'Wie bereitest du dein Startup auf Due Diligence vor?',
        "lead": (
            'Wenn ein Investor nach deinem Risk Assessment fragt, will er wissen: Kennst du deine '
            'eigenen Risiken – und kannst du sie managen? Due Diligence prüft nicht nur Zahlen, '
            'sondern auch Key-Person-, Cash-, Legal- und Tech-Risiken. Beraterium erstellt in 4 '
            'Wochen ein strukturiertes Risiko-Portfolio in Euro bewertet – investor-ready statt '
            'improvisiert.'
        ),
        "hero_cta": 'Book a free intro call',
        "criteria_tag": 'DIREKT-CHECK',
        "criteria_h2": 'Wann solltest du dein Startup investor-ready machen?',
        "criteria_intro": 'Du solltest deine Due-Diligence-Vorbereitung starten, wenn mindestens eines dieser Kriterien zutrifft:',
        "criteria": [
            'Ein Investor oder Business Angel hat Interesse signalisiert',
            'Du wirst nach Risk Assessment oder Risiko-Portfolio gefragt',
            'Co-Founder-Rollen oder Entscheidungsregeln sind ungeklärt',
            'Ein Großkunde macht mehr als 40 % deines Umsatzes aus',
        ],
        "stats_aria": 'Due Diligence in Zahlen',
        "stats": [
            ('4 Wochen', 'Risiko-Check von Beraterium für Startups'),
            ('40–50 %', 'der Founding-Teams erleben Co-Founder-Trennung'),
            ('~32 %', 'der scheiternden Startups scheitern wegen Cash'),
            ('Investor-ready', 'mit strukturiertem Risiko-Portfolio'),
        ],
        "pain_tag": 'DIE INVESTOR-FRAGEN',
        "pain_h2": 'Was passiert, wenn du unvorbereitet bist?',
        "pain_intro": 'Investoren erwarten kein perfektes Unternehmen – aber sie erwarten, dass du deine Risiken kennst und einen Plan hast.',
        "pain_cards": [
            ('Vertrauen sinkt', 'Wenn du bei der Risk-Assessment-Frage zögerst oder Risiken herunterspielst, verlierst du Glaubwürdigkeit – oft schneller als durch schlechte Zahlen.'),
            ('Deal verzögert sich', 'Fehlende Dokumentation zu Team, IP, Legal oder Cash-Runway verlängert Due Diligence um Wochen – und manchmal bricht der Deal ab.'),
            ('Bewertung sinkt', 'Unerkannte Risiken tauchen in der Due Diligence auf und drücken die Bewertung – oder führen zu härteren Investorenbedingungen.'),
        ],
        "overview_tag": 'SO HILFT BERATERIUM',
        "overview_h2": 'Wie macht Beraterium dein Startup investor-ready?',
        "overview_intro": (
            'Investor-Readiness beginnt mit einem ehrlichen Risikobild. Der 4-Wochen-Risiko-Check von '
            'Beraterium deckt Key-Person-, Cash-, Legal- und Tech-Risiken auf – in Euro bewertet, '
            'priorisiert und als Portfolio dokumentiert.'
        ),
        "overview_cards": [
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'method/', 'Zur Methode'),
            ('4-Wochen-Risiko-Check', 'In vier Wochen zu einem investor-ready Risiko-Portfolio – Key-Person, Cash, Legal und Tech.', 'services/startups/', 'Zum Startup-Angebot'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Du erhältst den vollen Betrag zurück.', 'benefit-guarantee/', 'Zur Garantie'),
        ],
        "faq": [
            ('Wie bereite ich mein Startup auf Due Diligence vor?', 'Due Diligence durch Investoren prüft nicht nur die Zahlen — sie prüft auch, ob Gründer ihre eigenen Risiken kennen und managen. Ein strukturiertes Risiko-Portfolio, in dem Key-Person-, Cash-, Legal- und Tech-Risiken bewertet und priorisiert sind, ist ein starkes Signal für Investor-Readiness. Beraterium erstellt dieses Portfolio in 4 Wochen.'),
            ('Was fragt ein Investor bei Due Diligence über Risiken?', 'Investoren prüfen typischerweise: Team-Risiken (Co-Founder, Key-Person-Abhängigkeit), Cash-Runway und Burn-Rate, Kundenkonzentration, IP- und Legal-Risiken sowie technische Abhängigkeiten. Ein strukturiertes Risk Assessment zeigt, dass du diese Felder kennst und priorisiert hast.'),
            ('Welche Risiken haben Startups, die oft übersehen werden?', 'Die häufig übersehenen Startup-Risiken liegen nicht im Produkt, sondern in den Strukturen: Co-Founder-Konflikte (in 40–50 % aller Founding-Teams kommt es zur Trennung), Klumpenrisiko bei Kunden (ein Großkunde = 60 % Umsatz), Key-Person-Abhängigkeit und Cash-Runway-Unterschätzung. Beraterium deckt diese Risiken im 4-Wochen-Risiko-Check systematisch auf.'),
            ('Was ist ein Co-Founder-Konflikt und wie manage ich das Risiko?', 'Ein Co-Founder-Konflikt entsteht häufig nicht durch schlechte Persönlichkeiten, sondern durch ungeklärte Rollenverteilung und fehlende Entscheidungsregeln für Krisen. Beraterium erfasst Team-Risiken als eigene Kategorie im Gefahrenkatalog: Wer hat welche Funktion, was passiert bei Ausfall, und welche Vereinbarungen fehlen? Das Ergebnis ist eine konkrete To-do-Liste.'),
            ('Wie lange dauert die Due-Diligence-Vorbereitung?', 'Der 4-Wochen-Risiko-Check von Beraterium liefert ein vollständiges, investor-ready Risiko-Portfolio – inklusive Key-Person-, Cash-, Legal- und Tech-Risiken in Euro bewertet. Für dringende Investor-Gespräche kann ein fokussiertes Erstgespräch die größten Lücken in 30 Minuten identifizieren.'),
            ('Wer hilft Startups bei der Due-Diligence-Vorbereitung?', 'Beraterium unterstützt Startups und Gründer mit dem 4-Wochen-Risiko-Check – ein strukturiertes Risiko-Portfolio in Euro bewertet, das Investoren zeigt, dass du deine Risiken kennst und managst.'),
        ],
        "deep_sections": [
            {
                "tag": "WAS INVESTOREN PRÜFEN",
                "h2": "Was prüft ein Investor beim Risk Assessment wirklich?",
                "intro": (
                    "Due Diligence prüft nicht nur, ob deine Zahlen stimmen – sie prüft, ob du dein eigenes Unternehmen "
                    "verstehst. Ein Investor will sehen, dass du deine Risiken kennst, ehrlich benennst und einen Plan "
                    "dafür hast. Vier Risikofelder stehen dabei fast immer im Fokus:"
                ),
                "items": [
                    "<strong>Key-Person-Risiken:</strong> Hängt das Produkt an einer Person? Was passiert bei Co-Founder-Trennung – in 40–50 % aller Founding-Teams kommt es dazu",
                    "<strong>Cash-Risiken:</strong> Runway, Burn-Rate und Kundenkonzentration – rund 32 % der scheiternden Startups scheitern an Cash, nicht am Produkt",
                    "<strong>Legal- und IP-Risiken:</strong> Gehört dem Startup wirklich der Code? Sind Verträge, Marken und Datenschutz sauber dokumentiert?",
                    "<strong>Tech-Risiken:</strong> Abhängigkeiten von einzelnen Plattformen, Dienstleistern oder Legacy-Entscheidungen, die eine Skalierung bremsen",
                ],
                "paragraphs": [
                    "Ein Startup, das diese Felder in einem strukturierten Risiko-Portfolio beantwortet – bewertet in Euro, mit Maßnahmen und Prioritäten – signalisiert Reife. Das alte Notion-Dokument mit einer Brainstorming-Liste tut das Gegenteil.",
                ],
            },
            {
                "tag": "TYPISCHE FEHLER",
                "h2": "Welche Fehler kosten Startups die Investor-Glaubwürdigkeit?",
                "intro": (
                    "Die meisten Startups scheitern in der Due Diligence nicht an ihren Risiken – sondern daran, wie sie "
                    "damit umgehen. Drei Muster tauchen immer wieder auf:"
                ),
                "items": [
                    "<strong>Risiken herunterspielen:</strong> „Das ist bei uns kein Thema“ wirkt auf erfahrene Investoren wie ein Warnsignal – sie kennen die Basisraten für Co-Founder-Konflikte und Cash-Probleme",
                    "<strong>Struktur improvisieren:</strong> Unklare Rollen, fehlende Entscheidungsregeln und Mikromanagement des Gründers zeigen sich in der Due Diligence als Organisations-Risiko – lange bevor sie im Alltag eskalieren",
                    "<strong>Dokumentation aufschieben:</strong> Wer IP-Zuordnung, Verträge und Runway-Berechnung erst zusammensucht, wenn der Investor fragt, verlängert die Due Diligence um Wochen – und manchmal stirbt der Deal an der Verzögerung",
                ],
            },
        ],
        "steps_section": {
            "tag": "DD-CHECKLISTE",
            "h2": "Wie machst du dein Startup in 6 Schritten investor-ready?",
            "intro": "Diese Checkliste deckt die Risiko-Seite der Due-Diligence-Vorbereitung ab – das, wonach Investoren beim Stichwort Risk Assessment wirklich fragen.",
            "steps": [
                ("Risiko-Portfolio aufbauen", "Erfasse alle Risiken strukturiert nach Kategorien: Team, Cash, Kunden, Legal/IP, Tech. Ein priorisiertes Portfolio in Euro schlägt jede unsortierte Liste."),
                ("Runway ehrlich berechnen", "Verfügbares Kapital geteilt durch monatlichen Netto-Cash-Burn – mit realistischen Annahmen. Investoren rechnen nach."),
                ("Key-Person-Frage beantworten", "Dokumentiere, welches Wissen an welchen Köpfen hängt und was bei Ausfall passiert. Co-Founder-Rollen und Entscheidungsregeln gehören schriftlich fixiert."),
                ("Kundenkonzentration ausweisen", "Zeige den Umsatzanteil deiner Top-Kunden offen. Ein Klumpenrisiko, das du selbst benennst und managst, ist glaubwürdiger als eines, das der Investor findet."),
                ("Legal & IP dokumentieren", "IP-Übertragungen, Arbeitsverträge, Datenschutz und Markenrechte sauber ablegen – die häufigsten Verzögerer in der Due Diligence."),
                ("Maßnahmen priorisieren", "Zu jedem Top-Risiko eine konkrete Maßnahme mit Verantwortlichem und Zeitrahmen – das unterscheidet ein Risk Assessment von einer Risiko-Liste."),
            ],
        },
        "blog_slugs": [
            "startup-mistakes-avoid-risk-management",
            "key-person-risk-identify-mitigate",
            "what-is-risk-management",
        ],
        "cta_h2": 'Mach dein Startup investor-ready – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Du erhältst unsere Methode erklärt und weißt danach, wo du stehst.',
        "title": 'Startup Due Diligence vorbereiten | Beraterium',
        "description": 'Due Diligence für Startups: Risiken erkennen, in Euro bewerten und investor-ready werden. Der 4-Wochen-Check. Book a free intro call.',
        "service_name": '4-Wochen-Risiko-Check für Startups',
        "breadcrumb_name": 'Investor Due Diligence',
    },
    {
        # Offer one-pager (2026-08-08). Keyword intent: risk analysis startup cost / process / pricing
        "slug": "risk-analysis-startup",
        "du": True,
        "audience": "Startups and founders",
        "tag": "STARTUP RISK ANALYSIS",
        "h1": "Risk analysis for your startup: process and pricing",
        "lead": (
            "The 360° Risk Analysis shows your startup&rsquo;s top 5&ndash;10 risks, assessed in euros "
            "and prioritised &mdash; from key-person dependency to runway. You get analysis, strategy "
            "session and budget planning as a fixed-price bundle for &euro;3,475, completed in "
            "2&ndash;4 weeks. Not there yet? The free Blindspot Quick Check reveals your biggest "
            "blind spots in 10 minutes."
        ),
        "hero_cta": "Book a free intro call",
        "hero_cta2": {"label": "Blindspot Quick Check (10 min)", "href": "tools/blindspot-check/"},
        "guarantee_section": True,
        "criteria_tag": "FIT CHECK",
        "criteria_h2": "Is a risk analysis right for your startup?",
        "criteria_intro": "A structured risk analysis is worth it if at least one of these applies:",
        "criteria": [
            "You have reached product&ndash;market fit or are close",
            "Your team has 3&ndash;20 people",
            "An investor conversation or due diligence review is coming up or on the horizon",
            "At least one risk (key person, runway, major customer) would seriously hurt the business",
        ],
        "stats_aria": "Startup risk analysis at a glance",
        "stats": [
            ("2&ndash;4 weeks", "from analysis to final report"),
            ("Top 5&ndash;10", "risks assessed in euros and prioritised"),
            ("&euro;3,475", "fixed price for analysis, strategy and budget"),
            ("2&times; money back", "relevance and value guarantee"),
        ],
        "pain_tag": "THREE RISKS INVESTORS SPOT",
        "pain_h2": "What happens if these three risks stay hidden?",
        "pain_intro": "As a founder you carry risks that stay invisible day to day &mdash; until an investor or an outage makes them obvious.",
        "pain_cards": [
            ("Key-person risk", 'Does product or sales depend on one person &mdash; often you? If you drop out, the startup stalls. More: <a href="../../solutions/key-person-risk/">Identify key-person risk</a>.'),
            ("Runway and burn rate", "Roughly 32% of failed startups run out of cash, not product. Without a clear picture, runway only becomes a topic when it is too late."),
            ("Due diligence", 'Investors ask for your risk assessment. Without a structured risk picture it reads as uncertainty &mdash; not control. More: <a href="../../solutions/investor-due-diligence/">Prepare for investor due diligence</a>.'),
        ],
        "overview_tag": "NEXT STEPS",
        "overview_h2": "How does the risk analysis connect to our other services?",
        "overview_intro": "The risk analysis is the entry point &mdash; depending on the outcome, further focused steps follow.",
        "overview_cards": [
            ("The method", "The 3-level hazard catalogue: collect hazards, assess risks in euros, prioritise measures.", "method/", "View method"),
            ("Services for startups", "All startup packages &mdash; from a short analysis to the full 360° risk analysis.", "services/startups/", "Startup services"),
            ("Full pricing", "Complete price list for all 32 services &mdash; analysis, workshops and training.", "pricing/", "View pricing"),
            ("Blindspot Quick Check", "Free self-assessment: 10 minutes to surface your biggest blind spots.", "tools/blindspot-check/", "Start quick check"),
        ],
        "faq": [
            ("What does a risk analysis for startups cost?", "The 360° Risk Analysis (RA-01) costs &euro;3,475 as a fixed price for analysis, strategy session and budget planning &mdash; bought separately the three parts would cost &euro;5,150. For a smaller entry there is analysis only (RA-02) at &euro;1,725 or startup risk-analysis preparation (ZUS-05) at &euro;295."),
            ("How long does the risk analysis take?", "The 360° Risk Analysis includes three workshops, each with its own report and follow-up call &mdash; from booking to final deliverable the process usually takes 2&ndash;4 weeks, depending on your team&rsquo;s availability."),
            ("What happens in the free intro call?", "In a 30-minute intro call we clarify where your startup stands, which risks are already visible and which package fits your stage &mdash; no obligation and no sales pressure."),
            ("What do I receive in writing?", "After each workshop you get a report: the prioritised risk list in euros, the strategy and implementation plan, and the budget plan with cost&ndash;benefit view &mdash; together a complete, investor-ready document."),
            ("What if I am not sure my startup needs this yet?", "If product&ndash;market fit, investor interest or a tangible risk are not there yet, the free Blindspot Quick Check is often enough as a first step &mdash; it shows where you stand in 10 minutes."),
            ("What if the analysis finds no relevant risk?", "Then the relevance guarantee applies: if the analysis finds no risk above the agreed threshold, Beraterium refunds the full fee. The value guarantee additionally ensures the agreed criteria are actually met."),
        ],
        "deep_sections": [
            {
                "tag": "SCOPE (RA-01)",
                "h2": "What is included in fixed price RA-01 (&euro;3,475)?",
                "intro": (
                    "All three analysis building blocks &mdash; analysis, strategy and budget &mdash; in one "
                    "continuous process with your team. The bundle costs less than booking separately "
                    "(&euro;5,150 individually) and is the recommended entry for startups under investor or growth pressure."
                ),
                "items": [
                    "Analysis workshop: identify top 5&ndash;10 risks, assess in euros and by likelihood",
                    "Strategy workshop: develop concrete, actionable measures for the top risks &mdash; with implementation plan",
                    "Budget workshop: weigh internal resources vs external providers, guided by damage figures from the analysis",
                    "Each phase ends with a report and a follow-up call with leadership",
                ],
            },
        ],
        "steps_section": {
            "tag": "HOW IT WORKS",
            "h2": "How does the risk analysis for your startup work?",
            "intro": "Five clear steps &mdash; no guesswork about effort.",
            "steps": [
                ("Intro call (30 min)", "We clarify your starting point, goal and whether RA-01, RA-02 or ZUS-05 fits your stage."),
                ("Analysis workshop", "Together we identify your startup&rsquo;s top 5&ndash;10 risks and assess them in euros."),
                ("Report with prioritised risks", "You receive the prioritised risk list in writing &mdash; basis for investor or bank conversations."),
                ("Strategy session", "For the top risks we develop concrete, actionable measures with an implementation plan."),
                ("Budget planning", "You decide how much budget goes into which measure &mdash; guided by actual damage from the analysis."),
            ],
        },
        "facts_table": {
            "tag": "PACKAGE COMPARISON",
            "h2": "Which package fits your stage?",
            "intro": "Three entry points by startup stage and budget &mdash; from a compact check to the full 360° risk analysis.",
            "caption": "Package comparison ZUS-05, RA-02 and RA-01 for startups",
            "headers": ["Package", "Duration", "Outcome", "Price"],
            "rows": [
                ("ZUS-05 Risk analysis preparation", "Session + review", "Typical risk fields for your sector mapped &mdash; basis for investor talks", "&euro;295"),
                ("RA-02 Risk consulting (analysis)", "1 workshop (2&ndash;3 h) + report", "Top 5&ndash;10 risks identified, assessed in euros and prioritised", "&euro;1,725"),
                ("RA-01 360° Risk Analysis", "3 workshops + 3 reports", "Analysis, strategy and budget planning in one fixed-price bundle", "&euro;3,475"),
            ],
        },
        "blog_slugs": [
            "startup-mistakes-avoid-risk-management",
            "key-person-risk-identify-mitigate",
            "what-is-risk-management",
        ],
        "cta_h2": "Clarify your top risks &mdash; free and no obligation",
        "cta_body": "Book an intro call &mdash; 30 minutes, no sales pressure. We explain our method and you will know where you stand.",
        "cta_note": 'Not there yet? <a href="../../tools/blindspot-check/">Blindspot Quick Check</a> &mdash; 10 minutes, free.',
        "title": "Startup risk analysis: pricing & process | Beraterium",
        "description": "Startup risk analysis: process, duration and pricing from &euro;295. Top 5&ndash;10 risks in euros, &euro;3,475 bundle. Book a free intro call.",
        "service_name": "360° Risk Analysis for startups",
        "breadcrumb_name": "Startup risk analysis",
    },
    {
        # Offer one-pager (2026-08-08). Keyword intent: risk analysis SME cost / process / pricing
        "slug": "risk-analysis-smb",
        "du": False,
        "audience": "SMEs and mid-market businesses",
        "tag": "SME RISK ANALYSIS",
        "h1": "Risk analysis for your SME: process and pricing",
        "lead": (
            "The 360° Risk Analysis delivers your company&rsquo;s top 5&ndash;10 risks, assessed in euros "
            "and prioritised &mdash; from director liability to dependencies in grown processes. "
            "Analysis, strategy session and budget planning come as a fixed-price bundle for "
            "&euro;3,475, completed in around 6 weeks. Still unsure? The free Blindspot Quick Check "
            "shows your biggest blind spots in 10 minutes."
        ),
        "hero_cta": "Book a free intro call",
        "hero_cta2": {"label": "Blindspot Quick Check (10 min)", "href": "tools/blindspot-check/"},
        "guarantee_section": True,
        "criteria_tag": "FIT CHECK",
        "criteria_h2": "Is a risk analysis right for your company?",
        "criteria_intro": "A structured risk analysis is worth it if at least one of these applies:",
        "criteria": [
            "Your company has 10&ndash;80 employees",
            "Processes and responsibilities grew over years but were never systematically reviewed",
            "As management you carry personal liability, e.g. under NIS2 or other regulation",
            "Succession, a bank or advisory board conversation is coming up or on the horizon",
        ],
        "stats_aria": "SME risk analysis at a glance",
        "stats": [
            ("Around 6 weeks", "from analysis to complete risk picture"),
            ("Top 5&ndash;10", "risks assessed in euros and prioritised"),
            ("&euro;3,475", "fixed price for analysis, strategy and budget"),
            ("2&times; money back", "relevance and value guarantee"),
        ],
        "pain_tag": "THREE MID-MARKET RISKS",
        "pain_h2": "What happens if these three risks stay hidden?",
        "pain_intro": "In a grown mid-market business, risks often hide in processes nobody questions any more.",
        "pain_cards": [
            ("Director liability and NIS2", 'NIS2 and other regulation make risk management a management duty &mdash; without documented analysis you are personally liable. More: <a href="../../solutions/nis2/">Check NIS2 applicability</a>.'),
            ("Succession", 'Around 186,000 business handovers are due in Germany by 2030. Without a solid risk picture, transition is hard for bank, board or successor to assess. More: <a href="../../solutions/succession/">Succession risks</a>.'),
            ("Dependencies in grown processes", 'Key people, single suppliers or undocumented knowledge build up unnoticed over years &mdash; and only surface in a crisis. More: <a href="../../solutions/key-person-risk/">Identify key-person risk</a>.'),
        ],
        "overview_tag": "NEXT STEPS",
        "overview_h2": "How does the risk analysis connect to our other services?",
        "overview_intro": "The risk analysis is the entry point &mdash; depending on the outcome, further focused steps follow.",
        "overview_cards": [
            ("The method", "The 3-level hazard catalogue: collect hazards, assess risks in euros, prioritise measures.", "method/", "View method"),
            ("Services for SMEs", "All mid-market packages &mdash; from a short analysis to the full 360° risk analysis.", "services/smb/", "SME services"),
            ("Full pricing", "Complete price list for all 32 services &mdash; analysis, workshops and training.", "pricing/", "View pricing"),
            ("Blindspot Quick Check", "Free self-assessment: 10 minutes to surface your biggest blind spots.", "tools/blindspot-check/", "Start quick check"),
        ],
        "faq": [
            ("What does a risk analysis for SMEs cost?", "The 360° Risk Analysis (RA-01) costs &euro;3,475 as a fixed price for analysis, strategy session and budget planning &mdash; bought separately the three parts would cost &euro;5,150. For a smaller entry there is analysis only (RA-02) at &euro;1,725."),
            ("How long does the risk analysis take for an SME?", "The 360° Risk Analysis includes three workshops, each with its own report and follow-up with leadership &mdash; the full process usually takes around 6 weeks, depending on your team&rsquo;s availability."),
            ("What happens in the free intro call?", "In a 30-minute intro call we clarify your starting point, possible risk fields and which package fits your company &mdash; no obligation and no sales pressure."),
            ("What do we receive in writing?", "After each workshop you get a report: the prioritised risk list in euros, the strategy and implementation plan, and the budget plan with cost&ndash;benefit view &mdash; together a complete, bank-ready risk picture."),
            ("What if we are not sure we need this yet?", "If it is still unclear whether structured risk management is needed, the free Blindspot Quick Check is often enough as a first step &mdash; it shows where your company stands in 10 minutes."),
            ("What if the analysis finds no relevant risk?", "Then the relevance guarantee applies: if the analysis finds no risk above the agreed threshold, Beraterium refunds the full fee. The value guarantee additionally ensures the agreed criteria are actually met."),
        ],
        "deep_sections": [
            {
                "tag": "SCOPE (RA-01)",
                "h2": "What is included in fixed price RA-01 (&euro;3,475)?",
                "intro": (
                    "All three analysis building blocks &mdash; analysis, strategy and budget &mdash; in one "
                    "continuous process with your team. The bundle costs less than booking separately "
                    "(&euro;5,150 individually) and is the recommended entry for SMEs."
                ),
                "items": [
                    "Analysis workshop: identify top 5&ndash;10 risks, assess in euros and by likelihood",
                    "Strategy workshop: develop concrete, actionable measures for the top risks &mdash; with implementation plan",
                    "Budget workshop: weigh internal resources vs external providers, guided by damage figures from the analysis",
                    "Each phase ends with a report and a follow-up call with leadership",
                ],
            },
        ],
        "steps_section": {
            "tag": "HOW IT WORKS",
            "h2": "How does the risk analysis for your company work?",
            "intro": "Five clear steps &mdash; no guesswork about effort.",
            "steps": [
                ("Intro call (30 min)", "We clarify your starting point and which package fits your company."),
                ("Analysis workshop", "Together we identify your top 5&ndash;10 risks and assess them in euros."),
                ("Report with prioritised risks", "You receive the prioritised risk list in writing &mdash; basis for bank or board conversations."),
                ("Strategy session", "For the top risks we develop concrete, actionable measures with an implementation plan."),
                ("Budget planning", "You decide how much budget goes into which measure &mdash; guided by actual damage from the analysis."),
            ],
        },
        "facts_table": {
            "tag": "PACKAGE COMPARISON",
            "h2": "Which package fits your company?",
            "intro": "Two main entry points for mid-market businesses &mdash; from analysis only to the full 360° bundle.",
            "caption": "Package comparison RA-02 and RA-01 for SMEs",
            "headers": ["Package", "Duration", "Outcome", "Price"],
            "rows": [
                ("RA-02 Risk consulting (analysis)", "1 workshop (2&ndash;3 h) + report", "Top 5&ndash;10 risks identified, assessed in euros and prioritised", "&euro;1,725"),
                ("RA-01 360° Risk Analysis", "3 workshops + 3 reports", "Analysis, strategy and budget planning in one fixed-price bundle", "&euro;3,475"),
            ],
        },
        "blog_slugs": [
            "cyber-attack-what-to-do-smb",
            "business-succession-overlooked-risks",
            "risk-management-consulting-smb-providers",
        ],
        "cta_h2": "Clarify your top risks &mdash; free and no obligation",
        "cta_body": "Book an intro call &mdash; 30 minutes, no sales pressure. We explain our method and you will know where you stand.",
        "cta_note": 'Still unsure? <a href="../../tools/blindspot-check/">Blindspot Quick Check</a> &mdash; 10 minutes, free.',
        "title": "SME risk analysis: pricing & process | Beraterium",
        "description": "Risk analysis for your SME: process, duration and &euro;3,475 fixed price. Top 5&ndash;10 risks in euros, double guarantee. Book a free intro call.",
        "service_name": "360° Risk Analysis for SMEs",
        "breadcrumb_name": "SME risk analysis",
    },
    {
        # Offer one-pager (2026-08-08). Keyword intent: risk analysis self-employed cost / freelancer
        "slug": "risk-analysis-solo",
        "du": True,
        "audience": "Solo self-employed professionals and freelancers",
        "tag": "SOLO RISK ANALYSIS",
        "h1": "Risk analysis for self-employed professionals: process and pricing",
        "lead": (
            "Risk consulting shows your top 5&ndash;10 self-employment risks, assessed in euros "
            "&mdash; from incapacity to client concentration. You get a workshop with report and "
            "follow-up from &euro;1,725; for a first overview the compact risk check from &euro;97 "
            "is enough. Not there yet? The free Blindspot Quick Check reveals your biggest blind "
            "spots in 10 minutes."
        ),
        "hero_cta": "Book a free intro call",
        "hero_cta2": {"label": "Blindspot Quick Check (10 min)", "href": "tools/blindspot-check/"},
        "guarantee_section": True,
        "criteria_tag": "FIT CHECK",
        "criteria_h2": "Is a risk analysis right for your self-employment?",
        "criteria_intro": "A structured risk analysis is worth it if at least one of these applies:",
        "criteria": [
            "Your revenue depends entirely on you as a person &mdash; if you stop, revenue stops",
            "You employ 1&ndash;5 people or work with a fixed network of collaborators",
            "One main client accounts for a large share of your revenue",
            "You have no clear picture of what an outage would actually cost you",
        ],
        "stats_aria": "Solo risk analysis at a glance",
        "stats": [
            ("From &euro;97", "for the compact risk check (30 min)"),
            ("Top 5&ndash;10", "risks assessed in euros and prioritised"),
            ("From &euro;1,725", "for full risk consulting with report"),
            ("2&times; money back", "relevance and value guarantee"),
        ],
        "pain_tag": "THREE RISKS WITH NO BACKUP",
        "pain_h2": "What happens if these three risks stay hidden?",
        "pain_intro": "As a solo professional you carry every risk alone &mdash; no works council, no cover, no IT department.",
        "pain_cards": [
            ("Incapacity", 'There is no employer sick pay &mdash; 4&ndash;6 weeks off or burnout can threaten your livelihood while fixed costs continue. More: <a href="../../solutions/self-employed-protection/">Protect yourself as self-employed</a>.'),
            ("Client concentration", 'If one main client drives most of your revenue, their budget cycle decides your survival. More: <a href="../../blog/risks-self-employed-freelancers/">Risks for self-employed professionals</a>.'),
            ("No cover", 'Without colleagues or a network contact with access to your projects, everything stops when you do &mdash; including towards clients. More: <a href="../../solutions/key-person-risk/">Identify key-person risk</a>.'),
        ],
        "overview_tag": "NEXT STEPS",
        "overview_h2": "How does the risk analysis connect to our other services?",
        "overview_intro": "The risk analysis is the entry point &mdash; depending on the outcome, further focused steps follow.",
        "overview_cards": [
            ("The method", "The 3-level hazard catalogue: collect hazards, assess risks in euros, prioritise measures.", "method/", "View method"),
            ("Services for solo professionals", "All solo packages &mdash; from compact check to full risk consulting.", "services/solo/", "Solo services"),
            ("Full pricing", "Complete price list for all 32 services &mdash; analysis, workshops and training.", "pricing/", "View pricing"),
            ("Blindspot Quick Check", "Free self-assessment: 10 minutes to surface your biggest blind spots.", "tools/blindspot-check/", "Start quick check"),
        ],
        "faq": [
            ("What does a risk analysis for self-employed professionals cost?", "The compact risk check costs &euro;97 (30 minutes) for a first assessment. Full risk consulting with workshop, report and follow-up costs &euro;1,725."),
            ("How long does the risk analysis take?", "The compact risk check takes 30 minutes. Full risk consulting includes a 2&ndash;3 hour workshop plus report and follow-up &mdash; completed within a few days."),
            ("What happens in the free intro call?", "In a 30-minute intro call we clarify where you stand, which risks are already visible and whether the compact check or full consulting fits you."),
            ("What do I receive in writing?", "You get a report with your top 5&ndash;10 risks, assessed by damage in euros and likelihood &mdash; a basis for insurance or bank conversations."),
            ("What if I am not sure I need this yet?", "If you cannot yet estimate your biggest risks, the free Blindspot Quick Check is often enough as a first step &mdash; it shows where you stand in 10 minutes."),
            ("What if the outcome is not useful?", "Then the relevance guarantee applies: if the analysis finds no risk above the agreed threshold, Beraterium refunds the full fee. The value guarantee additionally ensures the agreed criteria are actually met."),
        ],
        "deep_sections": [
            {
                "tag": "SCOPE (RA-02)",
                "h2": "What do you get with risk consulting (RA-02)?",
                "intro": (
                    "One workshop (2&ndash;3 hours), facilitated by us. Goal: turn gut feeling into a "
                    "prioritised list assessed in euros &mdash; without jumping straight into implementation planning."
                ),
                "items": [
                    "Each risk assessed by damage in euros and likelihood",
                    "Top 5&ndash;10 risks named and prioritised &mdash; basis for insurance or bank talks",
                    "Outcome documented as a report, including follow-up call to interpret results",
                    "Ideal if you want clarity on your risk picture first, without immediate measure planning",
                ],
            },
        ],
        "steps_section": {
            "tag": "HOW IT WORKS",
            "h2": "How does the risk analysis work for you?",
            "intro": "Five clear steps &mdash; no guesswork about effort.",
            "steps": [
                ("Intro call (30 min)", "We clarify your starting point and whether the compact check or full consulting fits you."),
                ("Analysis workshop", "Together we identify your top 5&ndash;10 risks and assess them in euros."),
                ("Report with prioritised risks", "You receive the prioritised risk list in writing &mdash; basis for insurance or bank conversations."),
                ("Follow-up call", "We interpret the results together and answer open questions on prioritisation."),
                ("Next steps", "You decide which measures to tackle first &mdash; alone or with implementation support."),
            ],
        },
        "facts_table": {
            "tag": "PACKAGE COMPARISON",
            "h2": "Which package fits you?",
            "intro": "Three entry points &mdash; from compact check to full 360° analysis if your business grows.",
            "caption": "Package comparison ZUS-02, RA-02 and RA-01 for solo professionals",
            "headers": ["Package", "Duration", "Outcome", "Price"],
            "rows": [
                ("ZUS-02 Short risk check", "30 minutes", "Rough read on your risk status, top 3 risks plus immediate pointers", "&euro;97"),
                ("RA-02 Risk consulting (analysis)", "1 workshop (2&ndash;3 h) + report", "Top 5&ndash;10 risks identified, assessed in euros and prioritised", "&euro;1,725"),
                ("RA-01 360° Risk Analysis", "3 workshops + 3 reports", "Analysis, strategy and budget planning in one bundle &mdash; e.g. when your team grows", "&euro;3,475"),
            ],
        },
        "blog_slugs": [
            "risks-self-employed-freelancers",
            "false-self-employment-check",
            "key-person-risk-identify-mitigate",
        ],
        "cta_h2": "Clarify your top risks &mdash; free and no obligation",
        "cta_body": "Book an intro call &mdash; 30 minutes, no sales pressure. We explain our method and you will know where you stand.",
        "cta_note": 'Not there yet? <a href="../../tools/blindspot-check/">Blindspot Quick Check</a> &mdash; 10 minutes, free.',
        "title": "Self-employed risk analysis: pricing | Beraterium",
        "description": "Risk analysis for self-employed professionals: process, duration and pricing from &euro;97. Top 5&ndash;10 risks in euros. Book a free intro call.",
        "service_name": "Risk consulting for solo self-employed professionals",
        "breadcrumb_name": "Solo risk analysis",
    },
]




def standort_cities_section(cfg: dict) -> str:
    """Sichtbare Städte-Abdeckung für Local SEO/GEO (optional pro STANDORT_CONFIG)."""
    cities = cfg.get("city_coverage", [])
    if not cities:
        return ""
    cards = "".join(
        f'<li class="brt-card brt-hover-lift"><h3 class="brt-h3">Risikomanagement {c["name"]}</h3>'
        f'<p class="brt-body">{c["text"]}</p></li>'
        for c in cities
    )
    region = cfg.get("region", cfg["city"])
    h2 = cfg.get("cities_h2", f"Beraterium als lokaler Partner in {region}")
    intro = cfg.get(
        "cities_intro",
        f"Beraterium ist mit fester Lokalvertretung in {region} für KMU, Startups und Solo-Selbstständige vor Ort erreichbar.",
    )
    return f"""
    <section class="brt-section brt-section--alt" id="staedte" aria-labelledby="staedte-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">REGIONALE PRÄSENZ</p>
          <h2 id="staedte-title" class="brt-h2">{h2}</h2>
          <p class="brt-body">{intro}</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">{cards}</ul>
      </div>
    </section>"""

def gen_standort(cfg: dict) -> None:
    """Lokale Vertretungs-One-Pager unter /locations/<slug>/ (Local SEO + GEO).

    Neue Stadt = neuer Eintrag in STANDORT_CONFIGS (Muenchen als Referenz).
    Struktur: Hero (answer-first) -> Lokalvertretung (Person + Region) ->
    Methode kompakt (GEO-Zitat-Block) -> Angebote-Ueberblick -> Doppelte
    Garantie -> Google Maps (Klick-to-load, DSGVO) -> Blog-Teaser ->
    Termin buchen (Calendly) -> FAQ (sichtbar + Schema) -> CTA.
    """
    slug = cfg["slug"]
    city = cfg["city"]
    pre = "../../"
    canonical = f"/locations/{slug}/"

    member = team_by_slug(load_team_members()).get(cfg["member_slug"])
    rep_bio = (
        team_profile_bio_html(member, team_section_id(member.slug))
        if member
        else ""
    )
    rep_media = (
        img_html(member.image, member.image_alt, 2, css_class="brt-team-portrait", aspect="4/5")
        if member
        else ""
    )
    rep_contacts = team_contact_icons(member) if member else ""
    geo_facts = "".join(f"<li>{item}</li>" for item in cfg.get("geo_facts", []))
    geo_section = ""
    if cfg.get("geo_h2"):
        geo_section = f"""
    <section class="brt-section" id="geo-local" aria-labelledby="geo-local-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">{cfg.get('geo_tag', 'KURZ & KLAR')}</p>
        <h2 id="geo-local-title" class="brt-h2">{cfg['geo_h2']}</h2>
        <p class="brt-body">{cfg.get('geo_intro', '')}</p>
        <ul class="brt-list-check">{geo_facts}</ul>
      </div>
    </section>"""

    offer_cards = "".join(
        f'<li class="brt-card brt-hover-lift"><a class="brt-card__link" href="{pre}{href}">'
        f'<h3 class="brt-h3">{title}</h3><p class="brt-body">{body}</p>'
        f'<span class="brt-meta" aria-hidden="true">{label} \u2192</span></a></li>'
        for title, body, href, label in [
            (
                "Risikoanalyse für KMU",
                f"In rund 6 Wochen zum vollständigen, in Euro bewerteten Risiko-Lagebild – moderiert vor Ort in {city} oder remote.",
                "services/smb/",
                "Zum Angebot für KMU",
            ),
            (
                "Risiko-Check für Startups",
                "In 4 Wochen wissen Gründerteams, welche Risiken ihr Wachstum bremsen – investor-ready aufbereitet.",
                "services/startups/",
                "Zum Angebot für Startups",
            ),
            (
                "Risiko-Kompass für Solo-Selbstständige",
                "In 2 Wochen weißt du, wo du verletzlich bist – Ausfall, Kundenabhängigkeit, Rücklagen.",
                "services/solo/",
                "Zum Angebot für Solo-Selbstständige",
            ),
        ]
    )
    blog_cards = "\n".join(blog_card_html(p, 2) for p in load_blog_posts()[:3])

    main = (
        hero(
            pre,
            cfg["tag"],
            cfg["h1"],
            cfg["lead"],
            actions=(
                f'<a class="brt-btn" href="#termin">{cfg["hero_cta"]}</a>'
                f'<a class="brt-btn brt-btn--outline" href="#faq">Frequently asked questions \u2192</a>'
            ),
        )
        + geo_section
        + standort_cities_section(cfg)
        + f"""
    <section class="brt-section brt-standort-rep" id="{cfg.get('member_slug', 'lokalvertretung')}" aria-labelledby="vertretung-title">
      <div class="brt-container brt-split">
        <div class="brt-split__media brt-fade-up" style="--fade-delay: 120ms">
          {rep_media}
        </div>
        <div class="brt-split__text brt-fade-up">
          <p class="brt-tag">IHRE LOKALVERTRETUNG</p>
          <h2 id="vertretung-title" class="brt-h2">{cfg["rep_h2"]}</h2>
          {rep_contacts}
          {rep_bio}
          <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}team/">Mehr über das Team \u2192</a></p>
        </div>
      </div>
    </section>
    <section class="brt-section brt-section--alt" id="methode" aria-labelledby="methode-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">DIE METHODE</p>
        <h2 id="methode-title" class="brt-h2">Was macht Beraterium?</h2>
        <p class="brt-body">Beraterium ist eine Risikomanagement-Beratung für KMU, Startups und Solo-Selbstständige. Der 3-Ebenen-Gefahrenkatalog macht sichtbar, wo Ihr Unternehmen wirklich verwundbar ist – praxisnah statt bürokratisch:</p>
        <ul class="brt-list-check">
          <li>Gefahren strukturiert sammeln – mit dem 3-Ebenen-Gefahrenkatalog, branchenangepasst</li>
          <li>Risiken in Euro bewerten – Schadenshöhe und Eintrittswahrscheinlichkeit statt Ampelfarben</li>
          <li>Die wenigen wirksamsten Maßnahmen priorisieren – mit Fahrplan und Verantwortlichkeiten</li>
          <li>Doppelte Garantie: Relevanz und Nutzen – sonst erstatten wir den vollen Betrag</li>
        </ul>
        <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}method/">Zur Methode \u2192</a> <a class="brt-btn brt-btn--outline" href="{pre}pricing/">Preise &amp; Leistungen \u2192</a></p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="angebote-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">UNSERE ANGEBOTE</p>
          <h2 id="angebote-title" class="brt-h2">Risikoanalyse in {city} – für jede Unternehmensgröße</h2>
          <p class="brt-body">Dieselbe Methode, angepasst auf Ihre Größe und Branche – vor Ort in {city} und Umgebung oder remote.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">{offer_cards}</ul>
      </div>
    </section>"""
        + guarantee(pre)
        + f"""
    <section class="brt-section brt-section--alt" id="karte" aria-labelledby="karte-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">VOR ORT IN {city.upper()}</p>
          <h2 id="karte-title" class="brt-h2">{cfg["map_h2"]}</h2>
          <p class="brt-body">{cfg["map_body"]}</p>
        </header>
        <div class="brt-map-embed brt-fade-up" data-map-embed data-map-query="{cfg["map_query"]}" data-map-title="Karte: Beraterium vor Ort in {city}">
          <button type="button" class="brt-map-embed__poster">
            <span class="brt-map-embed__label">Karte anzeigen</span>
            <span class="brt-map-embed__hint">Beim Klick wird eine Google-Maps-Karte geladen; dabei werden Daten an Google übertragen.</span>
          </button>
        </div>
        <p class="brt-meta brt-fade-up">Details zur Datenverarbeitung durch Google finden Sie in unserer <a href="{pre}privacy/">Datenschutzerklärung</a>.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="blog-title">
      <div class="brt-container">
        <header class="brt-section__header brt-section__header--row brt-fade-up">
          <div>
            <p class="brt-tag">EINBLICKE</p>
            <h2 id="blog-title" class="brt-h2">Experten-Einblicke von Beraterium</h2>
            <p class="brt-body">Kurze, praxisnahe Artikel zu Risiko, Führung und Entscheidungen – geschrieben vom Beraterium-Team.</p>
          </div>
          <a class="brt-btn brt-btn--outline" href="{pre}blog/">Alle Artikel \u2192</a>
        </header>
        <ul class="brt-blog-grid brt-stagger">
{blog_cards}
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--booking" id="termin" aria-labelledby="termin-title">
      <div class="brt-container brt-fade-up">
        <header class="brt-section__header">
          <p class="brt-tag">30 Minuten · kostenlos · unverbindlich</p>
          <h2 id="termin-title" class="brt-h2">Ihr kostenloses Erstgespräch – vor Ort in {city} oder online</h2>
          <p class="brt-body">Wählen Sie direkt einen Termin – wir nehmen uns Zeit für Ihre Situation, nicht für Verkaufsargumente.</p>
        </header>
        <div class="brt-calendly" data-calendly-embed>
          <div id="beraterium-calendly" class="calendly-inline-widget" data-url="https://calendly.com/beraterium/30min"></div>
        </div>
      </div>
    </section>"""
        + faq_section(cfg["faq"], alt=True)
        + cta_band(pre, cfg["cta_h2"], cfg["cta_body"], "Book a free intro call")
    )

    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{EN_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": f"Beraterium vor Ort {city}", "item": f"{EN_SITE_URL}{canonical}"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    person_ld = ""
    member_section_id = team_section_id(member.slug) if member else ""
    if member:
        person_data = person_schema(member)
        person_data["@id"] = f"{EN_SITE_URL}/team/#{member_section_id}"
        person_ld = json.dumps(
            {"@context": "https://schema.org", **person_data},
            ensure_ascii=False,
            indent=2,
        )
    ld = page_schema(
        local_business_schema(
            name=f"Beraterium vor Ort {city}",
            description=cfg["description"],
            url=canonical,
            locality=city,
            region=cfg["region"],
            latitude=cfg["lat"],
            longitude=cfg["lng"],
            email=member.email if member else "",
            telephone=member.phone if member else "",
            employee_name=member.name if member else "",
            employee_id=f"{EN_SITE_URL}/team/#{member_section_id}" if member else "",
            schema_locality=cfg.get("schema_locality", ""),
            street_address=cfg.get("street_address", ""),
            postal_code=cfg.get("postal_code", ""),
            cities_served=cfg.get("cities_served"),
        ),
        service_schema(
            name=f"Risikomanagement-Beratung {city}",
            description=cfg["description"],
            url=canonical,
            audience=cfg.get("service_audience", f"KMU, Startups und Solo-Selbstständige in {city} und {cfg['region']}"),
            service_type="Risikomanagement-Beratung",
            area_served=cfg["region"],
            cities_served=cfg.get("cities_served"),
        ),
        person_ld,
        faq_page_schema(cfg["faq"]),
        speakable_webpage_schema(
            canonical,
            selectors=[
                ".brt-page-hero__text .brt-lead",
                "#geo-local .brt-highlight-box",
                "#staedte .brt-card",
                ".brt-faq__answer",
            ],
        ),
        breadcrumb_ld,
    )
    write(
        f"locations/{slug}/index.html",
        shell(
            depth=2,
            title=cfg["title"],
            description=cfg["description"],
            canonical=canonical,
            active_nav=None,
            main=main,
            json_ld=ld,
            og_image=(f"https://www.beraterium.com/{member.image}" if member and member.image else ""),
        ).replace(
            f'<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
            f'<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript" async></script>\n<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
        ),
    )

STANDORT_CONFIGS: list[dict] = [
    {
        # Keyword (lokal, Muster wie "risikomanagement bautzen" in Webseite/Keywords/keyword-liste-master.csv):
        # "risikomanagement münchen" / "risikoberatung münchen" — anbieter-suchend, Local SEO/GEO.
        # Adresse bewusst nur Region-Level (Umzug steht an); exakte Anschrift + Map-Pin nachrüsten, sobald final.
        "slug": "munich",
        "city": "München",
        "region": "Bayern",
        "lat": 48.1372,
        "lng": 11.5756,
        "map_query": "München, Deutschland",
        "member_slug": "peter-muenstermann",
        "tag": "BERATERIUM VOR ORT · MÜNCHEN",
        "h1": "Risikomanagement in München: Beraterium vor Ort",
        "lead": (
            "Beraterium ist mit einer eigenen Lokalvertretung im Großraum München für Sie da: "
            "Peter Münstermann, Mitgründer und Entwickler des Beraterium-Risikomanagement-Ansatzes, "
            "betreut Unternehmen in München und Bayern persönlich. Ob KMU, Startup oder "
            "Solo-Selbstständige – wir machen Ihre größten Risiken sichtbar, bewerten sie in Euro "
            "und priorisieren die Maßnahmen, die wirklich zählen. Vor Ort bei Ihnen oder remote."
        ),
        "hero_cta": "Book a free intro call",
        "rep_h2": "Peter Münstermann – Ihre Beraterium-Lokalvertretung in München",
        "rep_paragraphs": [
            "Peter Münstermann bringt über 20 Jahre Erfahrung als Risikomanager in großen Unternehmen mit – und übersetzt Konzern-Risikomanagement in eine Form, die für Mittelstand, Familienunternehmen und Startups im Raum München praktisch funktioniert.",
            "Er bringt Führungskräfte und Mitarbeitende an einen Tisch und moderiert offene Diskussionen über Risiken, Chancen und Lösungen – strukturiert, aber menschlich. Das Ergebnis: Klarheit, Prioritäten und Maßnahmen, die im Alltag funktionieren.",
            "Als Lokalvertretung im Großraum München ist er für Kick-offs, Analyse-Sessions und Workshops direkt bei Ihnen im Unternehmen – von der Münchner Innenstadt über das Umland bis nach ganz Bayern.",
        ],
        "map_h2": "So erreichen Sie uns in München",
        "map_body": "Unsere Lokalvertretung ist im Großraum München ansässig und für Termine in der ganzen Region unterwegs – von München-Stadt über das Umland bis nach ganz Bayern. Die genaue Anschrift erhalten Sie mit Ihrer Terminbestätigung.",
        "faq": [
            ("Bietet Beraterium Risikomanagement-Beratung in München an?", "Ja. Beraterium ist mit Peter Münstermann als Lokalvertretung im Großraum München vertreten. Analyse-Sessions und Workshops finden direkt bei Ihnen im Unternehmen in München und Bayern statt – oder remote, wenn Sie das bevorzugen."),
            ("Wer ist die Beraterium-Lokalvertretung in München?", "Peter Münstermann, Mitgründer von Beraterium und Entwickler des Risikomanagement-Ansatzes. Er bringt über 20 Jahre Erfahrung als Risikomanager in großen Unternehmen mit und macht Risikomanagement für KMU, Familienunternehmen und Startups greifbar und praktisch umsetzbar."),
            ("Finden die Risikoanalyse-Sessions vor Ort in München statt?", "Ja. Im Großraum München kommen wir für Kick-off, Analyse-Sessions und Workshops direkt zu Ihnen ins Unternehmen. Alle Formate funktionieren genauso remote – viele Kunden kombinieren beides."),
            ("Für welche Unternehmen in München eignet sich die Risikoanalyse?", "Für KMU und Familienunternehmen, für Startups und Gründerteams sowie für Solo-Selbstständige. Die Methode ist dieselbe – der 3-Ebenen-Gefahrenkatalog wird auf Größe und Branche angepasst."),
            ("Was kostet eine Risikoanalyse in München?", "Kompakte Checks starten ab 47 €, vollständige Analysepakete ab 3.475 € Festpreis. Alle Preise stehen transparent auf der Preisseite; der Standort ändert nichts am Preis."),
            ("Arbeitet Beraterium nur in München?", "Nein. Beraterium arbeitet deutschlandweit und im DACH-Raum. München ist einer unserer Standorte – neben Sachsen und NRW. Die Lokalvertretung sorgt dafür, dass Unternehmen in München und Bayern einen persönlichen Ansprechpartner vor Ort haben."),
            ("Gibt es Risikomanagement-Berater in München?", "Ja. Beraterium ist mit Peter Münstermann als Lokalvertretung im Großraum München vertreten. Er moderiert Risikoanalysen für KMU, Startups und Solo-Selbstständige – vor Ort in München und Bayern oder remote."),
            ("Wie finde ich eine Risikoberatung für mein KMU in München?", "Achten Sie auf eine strukturierte Methode (nicht nur Checklisten), Euro-Bewertung statt Ampeln und einen festen Ansprechpartner. Beraterium kombiniert Konzern-Erfahrung mit Mittelstands-Praxis – transparente Festpreise auf der Preisseite, abgesichert durch die doppelte Garantie."),
        ],
        "geo_tag": "RISIKOMANAGEMENT IN MÜNCHEN",
        "geo_h2": "Risikomanagement in München – kurz erklärt",
        "geo_intro": (
            "Beraterium ist eine unabhängige Risikomanagement-Beratung für KMU, Startups und Solo-Selbstständige – "
            "mit fester Lokalvertretung in München. Wir bewerten Risiken in Euro, priorisieren die wirksamsten Maßnahmen "
            "und liefern ein umsetzbares Lagebild statt theoretischer Checklisten."
        ),
        "geo_facts": [
            "Ansprechpartner vor Ort: Peter Münstermann im Großraum München – von der Innenstadt über das Umland bis ganz Bayern.",
            "Formate: Kick-off, Analyse-Sessions und Workshops bei Ihnen im Unternehmen oder remote – je nachdem, was schneller Klarheit schafft.",
            "Zielgruppen: KMU und Familienunternehmen, Startups und Gründerteams, Solo-Selbstständige und Freelancer.",
            "Ergebnis: vollständiges Risiko-Lagebild in Euro plus Fahrplan mit Verantwortlichkeiten – abgesichert durch die doppelte Garantie.",
            "Preise: transparent auf der Preisseite; München ist kein Aufschlag, sondern persönlicher Ansprechpartner vor Ort.",
        ],
        "service_audience": "KMU, Startups und Solo-Selbstständige in München und Bayern",
        "cta_h2": "Bereit für Klarheit über Ihre Risiken – vor Ort in München?",
        "cta_body": "Buchen Sie Ihr kostenloses Erstgespräch mit Peter Münstermann – 30 Minuten, kein Sales-Pitch. Sie gehen mit einer DIY-Anleitung raus, egal wie Sie sich entscheiden.",
        "title": "Risikomanagement München – vor Ort | Beraterium",
        "description": "Risikomanagement & Risikoberatung in München und Bayern: Peter Münstermann als Lokalvertretung vor Ort. Risiken in Euro bewertet, doppelte Garantie. Erstgespräch kostenlos.",
        "breadcrumb_name": "München",
    },
    {
        # Keywords (lokal): risikomanagement bautzen/dresden/leipzig/chemnitz/goerlitz, risikoberatung sachsen
        # GEO: Städte-Abdeckung + FAQ je Kernstadt; Schema areaServed + Firmensitz Bautzen (NAP).
        "slug": "saxony",
        "city": "Sachsen",
        "region": "Sachsen",
        "lat": 51.1814,
        "lng": 14.4279,
        "map_query": "Bautzen, Sachsen, Deutschland",
        "schema_locality": "Bautzen",
        "street_address": "Dr.-Maria-Grollmuß-Str. 14",
        "postal_code": "02625",
        "member_slug": "till-blania",
        "cities_served": [
            "Bautzen", "Dresden", "Görlitz", "Leipzig", "Chemnitz", "Zwickau", "Plauen",
            "Freiberg", "Meißen", "Pirna", "Riesa", "Hoyerswerda", "Bischofswerda", "Döbeln", "Delitzsch", "Torgau", "Annaberg-Buchholz",
        ],
        "tag": "BERATERIUM VOR ORT · SACHSEN",
        "h1": "Risikomanagement in Sachsen: Beraterium – Ihr lokaler Partner vor Ort",
        "lead": (
            "Beraterium hat seinen Firmensitz in Bautzen und betreut Unternehmen im gesamten Freistaat Sachsen "
            "als lokaler Partner für Risikomanagement: Till Manfred Blania, Geschäftsführer und Mitgründer, "
            "ist persönlich in Bautzen, Dresden, Görlitz, Leipzig, Chemnitz und der gesamten Region für Sie da. "
            "Risiken werden in Euro bewertet, Maßnahmen priorisiert – vor Ort bei Ihnen oder remote."
        ),
        "hero_cta": "Book a free intro call",
        "rep_h2": "Till Manfred Blania – Ihre Beraterium-Lokalvertretung in Sachsen",
        "map_h2": "So erreichen Sie uns in Sachsen",
        "map_body": (
            "Unser Firmensitz liegt in Bautzen (Dr.-Maria-Grollmuß-Str. 14) – Till Blania ist für Termine "
            "im gesamten Freistaat unterwegs: Oberlausitz, Dresden, Leipzig, Chemnitz, Vogtland, Erzgebirge "
            "und sächsische Schweiz."
        ),
        "cities_h2": "Beraterium als lokaler Risikomanagement-Partner in Sachsen",
        "cities_intro": (
            "Beraterium ist in den wichtigsten Wirtschaftsregionen Sachsens als fester Ansprechpartner vor Ort "
            "präsent – mit derselben Methode, transparenten Festpreisen und doppelter Garantie in jeder Stadt."
        ),
        "city_coverage": [
            {
                "name": "Bautzen",
                "text": "Firmensitz der Beraterium GbR: Till Blania ist hier ansässig und betreut KMU, Familienunternehmen und Startups in der Oberlausitz persönlich – Kick-offs und Workshops direkt bei Ihnen.",
            },
            {
                "name": "Dresden",
                "text": "Als lokaler Partner in der Landeshauptstadt moderiert Beraterium Risikoanalysen für Unternehmen in Dresden und dem Umland – von Tech- und Kultur-Startups bis zu etablierten Dienstleistern und Industrie.",
            },
            {
                "name": "Görlitz",
                "text": "Beraterium ist Ihr Ansprechpartner für Risikomanagement in Görlitz und der Lausitz: strukturierte Analyse-Sessions bei Ihnen im Unternehmen, Risiken in Euro bewertet, mit Umsetzungsfahrplan.",
            },
            {
                "name": "Leipzig",
                "text": "In Leipzigs dynamischem Gründer- und Mittelstandsumfeld begleitet Beraterium Teams von der ersten Risikoanalyse bis zum investor-ready Lagebild – vor Ort oder remote.",
            },
            {
                "name": "Chemnitz",
                "text": "KMU und Industrieunternehmen in Chemnitz und Westsachsen erhalten mit Beraterium einen festen Lokalpartner: Konzern-Methodik, Mittelstands-Praxis, persönliche Moderation durch Till Blania.",
            },
            {
                "name": "Zwickau",
                "text": "Beraterium betreut Unternehmen in Zwickau und Südwestsachsen – vom Familienbetrieb bis zum wachsenden Mittelständler. Sessions vor Ort im Unternehmen.",
            },
            {
                "name": "Plauen",
                "text": "Im Vogtland und rund um Plauen bringt Beraterium strukturiertes Risikomanagement für KMU und Solo-Selbstständige – ohne bürokratische Checklisten, mit Euro-Bewertung.",
            },
            {
                "name": "Freiberg",
                "text": "Beraterium ist lokaler Risikomanagement-Partner für Unternehmen in Freiberg und Mittelsachsen – Analyse, Priorisierung und Maßnahmenplan mit festem Ansprechpartner.",
            },
            {
                "name": "Meißen",
                "text": "Unternehmen im Elbtal und rund um Meißen werden von Beraterium persönlich betreut: Risiko-Lagebild in Euro, Team-Einbindung, doppelte Garantie.",
            },
            {
                "name": "Pirna",
                "text": "In der Sächsischen Schweiz und Pirna begleitet Beraterium Firmen bei der strukturierten Risikoanalyse – vor Ort bei Ihnen oder online.",
            },
            {
                "name": "Riesa",
                "text": "KMU in Riesa und Nordwestsachsen erhalten mit Beraterium einen regionalen Partner für Risikoberatung – praxisnah und in Festpreisen kalkuliert.",
            },
            {
                "name": "Hoyerswerda",
                "text": "Beraterium unterstützt Unternehmen in Hoyerswerda und der Lausitz bei der systematischen Risikoanalyse – mit Till Blania als Lokalvertretung.",
            },
        ],
        "faq": [
            (
                "Wer ist der lokale Risikomanagement-Partner von Beraterium in Sachsen?",
                "Beraterium mit Firmensitz in Bautzen und Till Manfred Blania als Lokalvertretung. Er betreut KMU, Startups und Solo-Selbstständige in ganz Sachsen persönlich – Risiken in Euro bewertet, mit doppelter Garantie und transparenten Festpreisen.",
            ),
            (
                "Bietet Beraterium Risikomanagement in Bautzen an?",
                "Ja. Bautzen ist der Firmensitz der Beraterium GbR (Dr.-Maria-Grollmuß-Str. 14). Till Blania betreut Unternehmen in Bautzen und der Oberlausitz vor Ort – Kick-offs, Analyse-Sessions und Workshops direkt bei Ihnen im Unternehmen.",
            ),
            (
                "Gibt es Risikomanagement-Beratung in Dresden?",
                "Ja. Beraterium ist als lokaler Partner in Dresden und dem Dresdner Umland vertreten. Till Blania moderiert Risikoanalysen für KMU, Startups und Solo-Selbstständige – vor Ort in Dresden oder remote.",
            ),
            (
                "Wer hilft bei Risikomanagement in Görlitz und der Lausitz?",
                "Beraterium mit Lokalvertretung Till Blania. Analyse-Sessions finden in Görlitz, Bautzen, Hoyerswerda und der gesamten Lausitz bei Ihnen im Unternehmen statt – strukturiert mit dem 3-Ebenen-Gefahrenkatalog.",
            ),
            (
                "Bietet Beraterium Risikoberatung in Leipzig an?",
                "Ja. Für Leipzigs Gründer- und Mittelstandsszene bietet Beraterium vollständige Risikoanalysen ab 3.475 € Festpreis – investor-ready aufbereitet, mit persönlichem Ansprechpartner vor Ort.",
            ),
            (
                "Gibt es einen Risikomanagement-Berater in Chemnitz?",
                "Ja. Beraterium betreut Unternehmen in Chemnitz und Westsachsen als lokaler Partner – Industrie, Dienstleister und Gründerteams. Termine vor Ort oder online.",
            ),
            (
                "Deckt Beraterium auch Zwickau, Plauen und Freiberg ab?",
                "Ja. Beraterium ist im gesamten Freistaat Sachsen unterwegs – u. a. Zwickau, Plauen, Freiberg, Meißen, Pirna und Riesa. Der Standort ändert nichts am Preis; Sachsen bedeutet persönlichen Ansprechpartner vor Ort.",
            ),
            (
                "Was kostet eine Risikoanalyse in Sachsen?",
                "Kompakte Checks ab 47 €, vollständige Analysepakete ab 3.475 € Festpreis. Alle Preise stehen transparent auf beraterium.de/pricing/ – unabhängig davon, ob Sie in Dresden, Leipzig oder Bautzen sitzen.",
            ),
            (
                "Finden Risikoanalyse-Sessions vor Ort in Sachsen statt?",
                "Ja. Im Raum Bautzen, Dresden, Görlitz, Leipzig, Chemnitz und der gesamten Region kommen wir für Kick-off, Analyse-Sessions und Workshops zu Ihnen. Remote ist ebenfalls möglich – viele Kunden kombinieren beides.",
            ),
            (
                "Arbeitet Beraterium nur in Sachsen?",
                "Nein. Beraterium arbeitet deutschlandweit und im DACH-Raum – mit weiteren Lokalvertretungen in München und NRW. Sachsen ist der Heimatstandort mit Firmensitz in Bautzen.",
            ),
        ],
        "geo_tag": "RISIKOMANAGEMENT IN SACHSEN",
        "geo_h2": "Was ist Risikomanagement in Sachsen mit Beraterium?",
        "geo_intro": (
            "Beraterium ist eine unabhängige Risikomanagement-Beratung mit Firmensitz in Bautzen und fester "
            "Lokalvertretung im Freistaat Sachsen. Als lokaler Partner bewerten wir Risiken in Euro, priorisieren "
            "die wirksamsten Maßnahmen und liefern ein umsetzbares Lagebild – in Dresden, Leipzig, Görlitz, "
            "Chemnitz und der gesamten Region."
        ),
        "geo_facts": [
            "Lokaler Partner: Till Blania – persönlich in Bautzen, Dresden, Görlitz, Leipzig, Chemnitz, Zwickau, Plauen und ganz Sachsen.",
            "Firmensitz: Beraterium GbR, Dr.-Maria-Grollmuß-Str. 14, 02625 Bautzen – Termine im gesamten Freistaat.",
            "Formate: Kick-off, Analyse-Sessions und Workshops bei Ihnen im Unternehmen oder remote.",
            "Zielgruppen: KMU, Familienunternehmen, Startups, Gründerteams, Solo-Selbstständige und Freelancer.",
            "Ergebnis: Risiko-Lagebild in Euro plus Fahrplan – abgesichert durch die doppelte Garantie (Relevanz + Nutzen).",
            "Preise: transparent auf beraterium.de/pricing/; kein Aufschlag für Sachsen.",
        ],
        "service_audience": "KMU, Startups und Solo-Selbstständige in Sachsen",
        "cta_h2": "Bereit für Klarheit über Ihre Risiken – vor Ort in Sachsen?",
        "cta_body": (
            "Buchen Sie Ihr kostenloses Erstgespräch mit Till Blania – 30 Minuten, kein Sales-Pitch. "
            "Sie gehen mit einer DIY-Anleitung raus, egal wie Sie sich entscheiden."
        ),
        "title": "Risikomanagement Sachsen: Bautzen–Dresden | Beraterium",
        "description": (
            "Lokaler Partner Sachsen: Beraterium Bautzen, Till Blania – Dresden, Leipzig, Görlitz, Chemnitz. "
            "Risiken in Euro. Erstgespräch kostenlos."
        ),
        "breadcrumb_name": "Sachsen",
    },
    {
        # Keywords (lokal): risikomanagement köln/düsseldorf/dortmund/essen, risikoberatung nrw
        # GEO: Städte-Abdeckung + FAQ je Kernstadt; Schema areaServed + Hub Düsseldorf (Region-Level).
        "slug": "nrw",
        "city": "NRW",
        "region": "Nordrhein-Westfalen",
        "lat": 51.2277,
        "lng": 6.7735,
        "map_query": "Düsseldorf, Nordrhein-Westfalen, Deutschland",
        "schema_locality": "Düsseldorf",
        "member_slug": "joachim-lau",
        "cities_served": [
            "Köln", "Düsseldorf", "Dortmund", "Essen", "Duisburg", "Bochum", "Wuppertal",
            "Bielefeld", "Bonn", "Münster", "Aachen", "Gelsenkirchen", "Mönchengladbach",
            "Krefeld", "Oberhausen", "Hagen", "Hamm", "Herne", "Solingen", "Leverkusen",
            "Neuss", "Paderborn", "Recklinghausen", "Bottrop", "Remscheid", "Siegen",
        ],
        "tag": "BERATERIUM VOR ORT · NRW",
        "h1": "Risikomanagement in NRW: Beraterium – Ihr lokaler Partner vor Ort",
        "lead": (
            "Beraterium betreut Unternehmen in Nordrhein-Westfalen als lokaler Partner für "
            "Risikomanagement und Risikoberatung: Joachim Lau, Experte für Textil- und "
            "produzierende Betriebe, ist persönlich in Köln, Düsseldorf, Dortmund, Essen und "
            "dem gesamten Ruhrgebiet für Sie da. Risiken werden in Euro bewertet, Maßnahmen "
            "priorisiert – vor Ort bei Ihnen oder remote."
        ),
        "hero_cta": "Book a free intro call",
        "rep_h2": "Joachim Lau – Ihre Beraterium-Lokalvertretung in NRW",
        "map_h2": "So erreichen Sie uns in NRW",
        "map_body": (
            "Joachim Lau ist im gesamten Nordrhein-Westfalen unterwegs – von Köln und Düsseldorf "
            "über das Ruhrgebiet (Dortmund, Essen, Duisburg) bis nach Bonn, Münster, Aachen und "
            "Ostwestfalen. Die genaue Anschrift erhalten Sie mit Ihrer Terminbestätigung."
        ),
        "cities_h2": "Beraterium als lokaler Risikomanagement-Partner in NRW",
        "cities_intro": (
            "Beraterium ist in den wichtigsten Wirtschaftsregionen Nordrhein-Westfalens als fester "
            "Ansprechpartner vor Ort präsent – mit derselben Methode, transparenten Festpreisen "
            "und doppelter Garantie in jeder Stadt."
        ),
        "city_coverage": [
            {
                "name": "Köln",
                "text": "Als lokaler Partner am Rhein moderiert Beraterium Risikoanalysen für KMU, Startups und produzierende Betriebe in Köln und dem Umland – strukturiert mit dem 3-Ebenen-Gefahrenkatalog, in Euro bewertet.",
            },
            {
                "name": "Düsseldorf",
                "text": "Beraterium betreut Unternehmen in Düsseldorf und der Landeshauptstadt-Region persönlich – von Dienstleistern und Mittelständlern bis zu wachsenden Gründerteams. Sessions vor Ort oder remote.",
            },
            {
                "name": "Dortmund",
                "text": "Im Ruhrgebiet begleitet Joachim Lau Firmen in Dortmund bei der systematischen Risikoanalyse – besonders Textil- und produzierende Betriebe mit über 20 Jahren Branchenerfahrung.",
            },
            {
                "name": "Essen",
                "text": "KMU und Industrieunternehmen in Essen erhalten mit Beraterium einen festen Lokalpartner: Konzern-Methodik, Mittelstands-Praxis, persönliche Moderation durch Joachim Lau.",
            },
            {
                "name": "Duisburg",
                "text": "Beraterium ist Ihr Ansprechpartner für Risikomanagement in Duisburg und am unteren Rhein – Kick-offs, Analyse-Sessions und Workshops direkt bei Ihnen im Unternehmen.",
            },
            {
                "name": "Bochum",
                "text": "Beraterium begleitet Unternehmen in Bochum und dem mittleren Ruhrgebiet – vom Familienbetrieb bis zum wachsenden Mittelständler, mit Umsetzungsfahrplan statt Checklisten.",
            },
            {
                "name": "Gelsenkirchen",
                "text": "KMU in Gelsenkirchen und dem nördlichen Ruhrgebiet erhalten mit Beraterium einen regionalen Partner für Risikoberatung – praxisnah und in Festpreisen kalkuliert.",
            },
            {
                "name": "Bonn",
                "text": "Unternehmen in Bonn und der Region werden von Beraterium persönlich betreut: Risiko-Lagebild in Euro, Team-Einbindung, doppelte Garantie.",
            },
            {
                "name": "Münster",
                "text": "In Münster und Westfalen begleitet Beraterium Teams von der ersten Risikoanalyse bis zum priorisierten Maßnahmenplan – vor Ort oder remote.",
            },
            {
                "name": "Aachen",
                "text": "Beraterium unterstützt Unternehmen in Aachen und der Städteregion bei strukturiertem Risikomanagement – mit Joachim Lau als Lokalvertretung.",
            },
            {
                "name": "Wuppertal",
                "text": "KMU in Wuppertal und Bergischem Land erhalten mit Beraterium einen regionalen Partner für Risikoberatung – Risiken in Euro bewertet, nicht mit Ampelfarben.",
            },
            {
                "name": "Bielefeld",
                "text": "Beraterium betreut Unternehmen in Bielefeld und Ostwestfalen – vom Familienbetrieb bis zum wachsenden Mittelständler, Sessions vor Ort im Unternehmen.",
            },
            {
                "name": "Mönchengladbach",
                "text": "Im Textil- und Produktionsumfeld von Mönchengladbach bringt Joachim Lau Branchen-Know-how und strukturiertes Risikomanagement zusammen – ohne bürokratische Checklisten.",
            },
            {
                "name": "Leverkusen",
                "text": "Unternehmen in Leverkusen und der Region Rheinland profitieren von Berateriums lokaler Präsenz – Analyse, Priorisierung und Maßnahmenplan mit festem Ansprechpartner.",
            },
            {
                "name": "Krefeld",
                "text": "Beraterium betreut Textil- und produzierende Betriebe in Krefeld und am Niederrhein – Joachim Lau verbindet über 20 Jahre Branchenpraxis mit der Beraterium-Methode.",
            },
            {
                "name": "Oberhausen",
                "text": "KMU in Oberhausen und dem westlichen Ruhrgebiet erhalten strukturierte Risikoanalysen ab 3.475 € Festpreis – mit persönlichem Ansprechpartner vor Ort.",
            },
        ],
        "faq": [
            (
                "Wer ist der lokale Risikomanagement-Partner von Beraterium in NRW?",
                "Beraterium mit Joachim Lau als Lokalvertretung in Nordrhein-Westfalen. Er betreut KMU, Startups und Solo-Selbstständige in ganz NRW persönlich – Risiken in Euro bewertet, mit doppelter Garantie und transparenten Festpreisen auf beraterium.de/pricing/.",
            ),
            (
                "Bietet Beraterium Risikomanagement in Köln an?",
                "Ja. Beraterium ist als lokaler Partner in Köln und dem Kölner Umland vertreten. Joachim Lau moderiert Risikoanalysen für KMU, Startups und produzierende Betriebe – vor Ort in Köln oder remote.",
            ),
            (
                "Gibt es Risikomanagement-Beratung in Düsseldorf?",
                "Ja. Beraterium betreut Unternehmen in Düsseldorf und der Landeshauptstadt-Region als lokaler Partner – Analyse-Sessions bei Ihnen im Unternehmen, strukturiert mit dem 3-Ebenen-Gefahrenkatalog.",
            ),
            (
                "Wer hilft bei Risikomanagement im Ruhrgebiet (Dortmund, Essen, Duisburg)?",
                "Beraterium mit Lokalvertretung Joachim Lau. Kick-offs und Workshops finden in Dortmund, Essen, Duisburg, Bochum, Gelsenkirchen und dem gesamten Ruhrgebiet bei Ihnen im Unternehmen statt – besonders für Textil- und produzierende Betriebe.",
            ),
            (
                "Gibt es Risikoberatung für Textil- und produzierende Betriebe in NRW?",
                "Ja. Joachim Lau bringt über 20 Jahre Textilbranchen-Erfahrung (Key Account, IT-Modernisierung) mit und passt den 3-Ebenen-Gefahrenkatalog auf produzierende KMU in NRW an – von Mönchengladbach über Krefeld bis ins Ruhrgebiet.",
            ),
            (
                "Bietet Beraterium Risikoberatung in Bonn oder Münster an?",
                "Ja. Für Unternehmen in Bonn, Münster und Westfalen bietet Beraterium vollständige Risikoanalysen ab 3.475 € Festpreis – mit persönlichem Ansprechpartner vor Ort.",
            ),
            (
                "Deckt Beraterium auch Aachen, Bielefeld und Leverkusen ab?",
                "Ja. Beraterium ist im gesamten Nordrhein-Westfalen unterwegs – u. a. Aachen, Bielefeld, Wuppertal, Leverkusen, Krefeld und Oberhausen. Der Standort ändert nichts am Preis; NRW bedeutet persönlichen Ansprechpartner vor Ort.",
            ),
            (
                "Was kostet eine Risikoanalyse in NRW?",
                "Kompakte Checks ab 47 €, vollständige Analysepakete ab 3.475 € Festpreis. Alle Preise stehen transparent auf beraterium.de/pricing/ – unabhängig davon, ob Sie in Köln, Düsseldorf oder Dortmund sitzen.",
            ),
            (
                "Finden Risikoanalyse-Sessions vor Ort in NRW statt?",
                "Ja. Im Raum Köln, Düsseldorf, Ruhrgebiet und der gesamten Region kommen wir für Kick-off, Analyse-Sessions und Workshops zu Ihnen. Remote ist ebenfalls möglich – viele Kunden kombinieren beides.",
            ),
            (
                "Wie finde ich eine Risikoberatung für mein KMU in Köln oder NRW?",
                "Achten Sie auf eine strukturierte Methode (nicht nur Checklisten), Euro-Bewertung statt Ampeln und einen festen Ansprechpartner. Beraterium kombiniert Branchen- und Konzern-Erfahrung mit Mittelstands-Praxis – transparente Festpreise, abgesichert durch die doppelte Garantie.",
            ),
            (
                "Arbeitet Beraterium nur in NRW?",
                "Nein. Beraterium arbeitet deutschlandweit und im DACH-Raum – mit weiteren Lokalvertretungen in München und Sachsen. NRW ist einer unserer Standorte mit persönlichem Ansprechpartner vor Ort.",
            ),
        ],
        "geo_tag": "RISIKOMANAGEMENT IN NRW",
        "geo_h2": "Was ist Risikomanagement in NRW mit Beraterium?",
        "geo_intro": (
            "Beraterium ist eine unabhängige Risikomanagement-Beratung mit fester Lokalvertretung "
            "in Nordrhein-Westfalen. Als lokaler Partner bewerten wir Risiken in Euro, priorisieren "
            "die wirksamsten Maßnahmen und liefern ein umsetzbares Lagebild – in Köln, Düsseldorf, "
            "Dortmund, dem Ruhrgebiet und der gesamten Region."
        ),
        "geo_facts": [
            "Lokaler Partner: Joachim Lau – persönlich in Köln, Düsseldorf, Dortmund, Essen, Duisburg, Bonn, Münster, Aachen und ganz NRW.",
            "Branchen-Schwerpunkt: Textil- und produzierende Betriebe (Mönchengladbach, Krefeld, Ruhrgebiet) – die Methode gilt für alle KMU.",
            "Formate: Kick-off, Analyse-Sessions und Workshops bei Ihnen im Unternehmen oder remote.",
            "Zielgruppen: KMU, Familienunternehmen, Startups, Gründerteams, Solo-Selbstständige und Freelancer.",
            "Ergebnis: Risiko-Lagebild in Euro plus Fahrplan – abgesichert durch die doppelte Garantie (Relevanz + Nutzen).",
            "Preise: transparent auf beraterium.de/pricing/; kein Aufschlag für NRW.",
        ],
        "service_audience": "KMU, Startups und Solo-Selbstständige in NRW (Köln, Düsseldorf, Ruhrgebiet)",
        "cta_h2": "Bereit für Klarheit über Ihre Risiken – vor Ort in NRW?",
        "cta_body": (
            "Buchen Sie Ihr kostenloses Erstgespräch mit Joachim Lau – 30 Minuten, kein Sales-Pitch. "
            "Sie gehen mit einer DIY-Anleitung raus, egal wie Sie sich entscheiden."
        ),
        "title": "Risikomanagement NRW: Köln–Düsseldorf | Beraterium",
        "description": (
            "Lokaler Partner NRW: Joachim Lau – Köln, Düsseldorf, Dortmund, Ruhrgebiet. "
            "Risiken in Euro. Erstgespräch kostenlos."
        ),
        "breadcrumb_name": "NRW",
    },
]

def gen_home_guarantee_avatars() -> None:
    """Home index.html: Garantie-Avatare mit Alt-Text (hand-maintained section)."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    html = html.replace(
        '<div class="brt-guarantee-cta__avatars" aria-hidden="true">\n            <img src="img/team/till-blania.webp" alt=""',
        f'<div class="brt-guarantee-cta__avatars">\n            <img src="img/team/till-blania.webp" alt="{ALT_TILL}"',
        1,
    )
    html = html.replace(
        '<img src="img/team/peter-muenstermann.webp" alt="" width="80" height="80" loading="lazy" decoding="async">',
        f'<img src="img/team/peter-muenstermann.webp" alt="{ALT_PETER}" width="80" height="80" loading="lazy" decoding="async">',
        1,
    )
    path.write_text(html, encoding="utf-8")

def gen_home_footer() -> None:
    """Home index.html: Footer aus footer_html() synchronisieren."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    start = '<footer class="site-footer"'
    end = "</footer>"
    i = html.find(start)
    j = html.find(end, i)
    if i < 0 or j < 0:
        print("  skip index.html home footer (pattern not found)")
        return
    j += len(end)
    path.write_text(html[:i] + footer_html(0) + html[j:], encoding="utf-8")
    print("  updated index.html home footer")


if __name__ == "__main__":
    print("Generating pages...")
    blindspot_selfcheck()
    gen_ueber_uns()
    gen_team()
    gen_mission_vision()
    gen_methode()
    gen_nutzen_garantie()
    gen_relevanz_garantie()
    gen_angebote()
    gen_pricing()
    gen_schulungen_index()
    for _sch_cfg in SCHULUNG_CONFIGS:
        gen_schulung(_sch_cfg)
    gen_lp_startups()
    gen_lp_kmu()
    gen_lp_solo()
    for _lp_cfg in LP_CONFIGS:
        gen_landingpage(_lp_cfg)
    for _st_cfg in STANDORT_CONFIGS:
        gen_standort(_st_cfg)
    gen_risikoradar()
    gen_tools_index()
    gen_blindspot_check()
    gen_blog()
    gen_blog_singles()
    gen_home_analyse()
    gen_home_team()
    gen_home_guarantee_avatars()
    gen_home_blog_teaser()
    gen_home_nav()
    gen_home_analytics()
    gen_home_tools_teaser()
    gen_home_footer()
    gen_kontakt()
    gen_kontaktformular()
    gen_impressum()
    gen_datenschutz()
    gen_agb()
    gen_accessibility()
    gen_danke()
    gen_404()
    write_sitemap()
    print("Done.")
