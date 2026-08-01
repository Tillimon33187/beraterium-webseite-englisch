#!/usr/bin/env python3
"""Generate Beraterium static pages from briefing content."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from _blindspot import blindspot_config_json
from _blindspot import selfcheck as blindspot_selfcheck
from _i18n import hreflang_links, language_switcher_html

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
    faq_page_schema,
    format_date_en,
    service_schema,
    speakable_webpage_schema,
    header_logo_html,
    home_team_section_html,
    img_html,
    load_blog_posts,
    load_team_members,
    person_schema,
    team_by_slug,
    team_profile_section,
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
    services_active = bool(active and active.startswith("services"))
    services_cur = ' aria-current="page"' if active == "services" else ""
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
      </ul>
    </section>
    <section>
      <h2>Company</h2>
      <ul>
        <li><a href="{pre}about/">About us</a></li>
        <li><a href="{pre}team/">Team</a></li>
        <li><a href="{pre}mission-vision/">Mission &amp; Vision</a></li>
        <li><a href="{pre}method/">Method</a></li>
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
    extra_css: str = "",
    extra_scripts: str = "",
) -> str:
    pre = pfx(depth)
    home = pre or "./"
    robots = '\n  <meta name="robots" content="noindex">' if noindex else ""
    ld = f"\n  <script type=\"application/ld+json\">\n{json_ld}\n  </script>" if json_ld else ""
    hreflang = hreflang_links(canonical, current_locale="en")
    lang_switch = language_switcher_html(current_locale="en", canonical=canonical, depth=depth)
    return f"""<!doctype html>
<html lang="en">

<head>
{COOKIEYES_HEAD}
{GA4_ANALYTICS_HEAD}
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://en.beraterium.de{canonical}">{robots}{hreflang}

  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://en.beraterium.de{canonical}">
  <meta property="og:locale" content="en_GB">

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


def cta_band(pre: str, h2: str, body: str, btn: str = "Book a free intro call") -> str:
    return f"""
    <section class="brt-cta-band brt-cta-band--dark brt-section" aria-labelledby="final-cta">
      <div class="brt-container brt-cta-band__inner brt-fade-up">
        <h2 id="final-cta" class="brt-h2 brt-h2--on-dark">{h2}</h2>
        <p class="brt-body brt-body--on-dark">{body}</p>
        <a class="brt-btn brt-btn--on-dark brt-btn--lg" href="{pre}contact/">{btn}</a>
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



def case_studies_section(pre: str, *, en: bool = False) -> str:
    if en:
        return """
    <section class="brt-section brt-case-studies" aria-labelledby="case-studies-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">FROM THE FIELD</p>
          <h2 id="case-studies-title" class="brt-h2">Case studies from the field</h2>
          <p class="brt-body">Two anonymised examples – how the BlindSpot Check works in different phases, and where Stage&nbsp;2 turns insight into action.</p>
        </header>
        <div class="brt-case-studies__widget brt-fade-up" data-case-studies>
          <div class="brt-case-studies__tabs" role="tablist" aria-label="Case studies">
            <button type="button" class="brt-case-studies__tab is-active" role="tab" id="case-tab-0" aria-selected="true" aria-controls="case-panel-0" data-case-study-tab>Financial services</button>
            <button type="button" class="brt-case-studies__tab" role="tab" id="case-tab-1" aria-selected="false" aria-controls="case-panel-1" data-case-study-tab tabindex="-1">Creative crafts</button>
          </div>
          <div class="brt-case-studies__panels">
            <article class="brt-case-study is-active" id="case-panel-0" role="tabpanel" aria-labelledby="case-tab-0" data-case-study-panel>
              <div class="brt-case-study__grid">
                <div class="brt-case-study__challenge">
                  <p class="brt-case-study__label">Starting point</p>
                  <h3 class="brt-case-study__title">Startup founder, pre-launch</h3>
                  <ul class="brt-case-study__meta">
                    <li><span>Industry</span> Financial services</li>
                    <li><span>Phase</span> Pre-launch / structuring</li>
                    <li><span>Team</span> 1 founder + external partners</li>
                  </ul>
                  <p class="brt-case-study__text">Financing and regulation were on his radar – but there was no shared framework to compare all risk fields and no portfolio with clear priorities. Topics were discussed in isolation, not as one picture.</p>
                </div>
                <div class="brt-case-study__body">
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Approach</p>
                    <h4 class="brt-case-study__headline">BlindSpot Check (Stage&nbsp;1)</h4>
                    <p class="brt-body">We worked through the core hazard matrix systematically: guiding question, damage scenario, euro bands, likelihood and inventory – what already mitigates the risk.</p>
                  </div>
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Outcome</p>
                    <ul class="brt-case-study__stats">
                      <li class="brt-case-study__stat"><strong>1</strong><span>Top priority: quality of analysis &amp; decision models – not financing</span></li>
                      <li class="brt-case-study__stat"><strong>4</strong><span>Equal second tier: cyber, capital providers, market, reputation</span></li>
                      <li class="brt-case-study__stat"><strong>1</strong><span>Key partner exit scenario made explicit – redundancy question opened</span></li>
                      <li class="brt-case-study__stat"><strong>✓</strong><span>Roadmap to revisit phase-dependent risks after launch</span></li>
                    </ul>
                  </div>
                  <blockquote class="brt-case-study__quote"><p>&ldquo;I knew there were risks. I just didn&rsquo;t know which came first – and which I&rsquo;d need to reassess after launch.&rdquo;</p></blockquote>
                </div>
              </div>
            </article>
            <article class="brt-case-study" id="case-panel-1" role="tabpanel" aria-labelledby="case-tab-1" data-case-study-panel hidden>
              <div class="brt-case-study__grid">
                <div class="brt-case-study__challenge">
                  <p class="brt-case-study__label">Starting point</p>
                  <h3 class="brt-case-study__title">Solo self-employed, growing studio</h3>
                  <ul class="brt-case-study__meta">
                    <li><span>Industry</span> Creative crafts</li>
                    <li><span>Phase</span> Running business, scaling offer</li>
                    <li><span>Team</span> 1 person, project support</li>
                  </ul>
                  <p class="brt-case-study__text">Many open fronts, little time – but no shared priority. What to tackle first without spinning in circles was unclear. She carries every risk alone: customers, IT, premises, contracts, social media.</p>
                </div>
                <div class="brt-case-study__body">
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Approach</p>
                    <h4 class="brt-case-study__headline">Stage&nbsp;1 + Stage&nbsp;2</h4>
                    <p class="brt-body">Stage&nbsp;1 revealed four equally weighted top risks. In Stage&nbsp;2 we turned each into action logic – cyber, reputation, physical total loss and organisation – with effort vs. impact trade-offs.</p>
                  </div>
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Outcome</p>
                    <ul class="brt-case-study__stats">
                      <li class="brt-case-study__stat"><strong>4</strong><span>Top risks: IT/cyber, reputation, physical total loss, missing processes</span></li>
                      <li class="brt-case-study__stat"><strong>A–D</strong><span>Stage&nbsp;2 blocks with concrete next steps per area</span></li>
                      <li class="brt-case-study__stat"><strong>3</strong><span>Phases: now, 1–3 months, follow-up sessions</span></li>
                      <li class="brt-case-study__stat"><strong>↓</strong><span>Non-core work made measurable – capacity freed for top risks</span></li>
                    </ul>
                  </div>
                  <blockquote class="brt-case-study__quote"><p>&ldquo;Stage&nbsp;1 showed which risks really carry the building – Stage&nbsp;2 how to tackle them without burning out.&rdquo;</p></blockquote>
                </div>
              </div>
            </article>
          </div>
          <div class="brt-case-studies__nav">
            <button type="button" class="brt-testimonials__btn brt-testimonials__btn--prev" data-case-study-prev aria-label="Previous case study">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <button type="button" class="brt-testimonials__btn brt-testimonials__btn--next" data-case-study-next aria-label="Next case study">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>
        </div>
        <p class="brt-meta brt-case-studies__note brt-fade-up">All details anonymised – no conclusions about individuals possible.</p>
      </div>
    </section>"""
    return """
    <section class="brt-section brt-case-studies" aria-labelledby="case-studies-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">AUS DER PRAXIS</p>
          <h2 id="case-studies-title" class="brt-h2">Case Studies aus der Praxis</h2>
          <p class="brt-body">Zwei anonymisierte Einblicke – wie der Blindspot Check in unterschiedlichen Phasen wirkt und wo Stufe&nbsp;2 aus Erkenntnis konkrete Bearbeitung macht.</p>
        </header>
        <div class="brt-case-studies__widget brt-fade-up" data-case-studies>
          <div class="brt-case-studies__tabs" role="tablist" aria-label="Case Studies">
            <button type="button" class="brt-case-studies__tab is-active" role="tab" id="case-tab-0" aria-selected="true" aria-controls="case-panel-0" data-case-study-tab>Finanzdienstleistungen</button>
            <button type="button" class="brt-case-studies__tab" role="tab" id="case-tab-1" aria-selected="false" aria-controls="case-panel-1" data-case-study-tab tabindex="-1">Kreativhandwerk</button>
          </div>
          <div class="brt-case-studies__panels">
            <article class="brt-case-study is-active" id="case-panel-0" role="tabpanel" aria-labelledby="case-tab-0" data-case-study-panel>
              <div class="brt-case-study__grid">
                <div class="brt-case-study__challenge">
                  <p class="brt-case-study__label">Ausgangssituation</p>
                  <h3 class="brt-case-study__title">Startup-Gründer vor der Auflage</h3>
                  <ul class="brt-case-study__meta">
                    <li><span>Branche</span> Finanzdienstleistungen</li>
                    <li><span>Phase</span> Vorgründung / Strukturierung</li>
                    <li><span>Team</span> 1 Gründer, externe Partner</li>
                  </ul>
                  <p class="brt-case-study__text">Finanzierung und Regulatorik waren im Blick – aber kein gemeinsames Raster, um alle Felder zu vergleichen, und kein Portfolio mit Prioritäten. Einzelthemen waren besprochen, nicht als ein Gesamtbild.</p>
                </div>
                <div class="brt-case-study__body">
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Ansatz</p>
                    <h4 class="brt-case-study__headline">Blindspot Check (Stufe&nbsp;1)</h4>
                    <p class="brt-body">Systematische Kerngefahren-Matrix: Leitfrage, Schadenszenario, Euro-Stufen, Eintrittswahrscheinlichkeit und Inventar – was das Risiko bereits mindert.</p>
                  </div>
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Ergebnis</p>
                    <ul class="brt-case-study__stats">
                      <li class="brt-case-study__stat"><strong>1</strong><span>Top-Priorität: Qualität von Analyse- &amp; Entscheidungsmodellen – nicht Finanzierung</span></li>
                      <li class="brt-case-study__stat"><strong>4</strong><span>Gleichrangige zweite Ebene: Cyber, Kapitalgeber, Markt, Reputation</span></li>
                      <li class="brt-case-study__stat"><strong>1</strong><span>Schlüsselpartner-Ausstieg explizit – Redundanz-Frage eröffnet</span></li>
                      <li class="brt-case-study__stat"><strong>✓</strong><span>Roadmap zur Fortschreibung phasenabhängiger Risiken nach Auflage</span></li>
                    </ul>
                  </div>
                  <blockquote class="brt-case-study__quote"><p>&bdquo;Ich wusste, dass es Risiken gibt. Ich wusste nur nicht, welche zuerst – und welche ich nach dem Start neu bewerten muss.&ldquo;</p></blockquote>
                </div>
              </div>
            </article>
            <article class="brt-case-study" id="case-panel-1" role="tabpanel" aria-labelledby="case-tab-1" data-case-study-panel hidden>
              <div class="brt-case-study__grid">
                <div class="brt-case-study__challenge">
                  <p class="brt-case-study__label">Ausgangssituation</p>
                  <h3 class="brt-case-study__title">Solo-Selbstständige im laufenden Betrieb</h3>
                  <ul class="brt-case-study__meta">
                    <li><span>Branche</span> Kreativhandwerk</li>
                    <li><span>Phase</span> Laufender Betrieb, Wachstum</li>
                    <li><span>Team</span> 1 Person, projektweise Unterstützung</li>
                  </ul>
                  <p class="brt-case-study__text">Viele Baustellen, wenig Zeit – aber keine gemeinsame Priorität. Was zuerst angehen, ohne sich im Hamsterrad zu verlieren, war unklar. Alle Risiken trägt sie allein: Kunden, IT, Räume, Verträge, Social Media.</p>
                </div>
                <div class="brt-case-study__body">
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Ansatz</p>
                    <h4 class="brt-case-study__headline">Stufe&nbsp;1 + Stufe&nbsp;2</h4>
                    <p class="brt-body">Stufe&nbsp;1 machte vier gleich gewichtete Top-Risiken sichtbar. In Stufe&nbsp;2 wurden daraus Bearbeitungslogiken – IT/Cyber, Reputation, physischer Totalausfall und Organisation – mit Aufwand-Wirkungs-Abwägung.</p>
                  </div>
                  <div class="brt-case-study__block">
                    <p class="brt-case-study__label">Ergebnis</p>
                    <ul class="brt-case-study__stats">
                      <li class="brt-case-study__stat"><strong>4</strong><span>Top-Risiken: IT/Cyber, Reputation, physischer Totalausfall, fehlende Prozesse</span></li>
                      <li class="brt-case-study__stat"><strong>A–D</strong><span>Stufe-2-Blöcke mit konkreten nächsten Schritten pro Bereich</span></li>
                      <li class="brt-case-study__stat"><strong>3</strong><span>Phasen: Sofort, 1–3 Monate, Folgetermine</span></li>
                      <li class="brt-case-study__stat"><strong>↓</strong><span>Nicht-Kerngeschäft messbar reduzierbar – Kapazität für Top-Risiken</span></li>
                    </ul>
                  </div>
                  <blockquote class="brt-case-study__quote"><p>&bdquo;Stufe&nbsp;1 hat gezeigt, welche wirklich das Gebäude tragen – Stufe&nbsp;2, wie ich sie ohne Selbstzerstörung angehen kann.&ldquo;</p></blockquote>
                </div>
              </div>
            </article>
          </div>
          <div class="brt-case-studies__nav">
            <button type="button" class="brt-testimonials__btn brt-testimonials__btn--prev" data-case-study-prev aria-label="Vorherige Case Study">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
            </button>
            <button type="button" class="brt-testimonials__btn brt-testimonials__btn--next" data-case-study-next aria-label="Nächste Case Study">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>
        </div>
        <p class="brt-meta brt-case-studies__note brt-fade-up">Alle Angaben anonymisiert – ohne Rückschlüsse auf Personen möglich.</p>
      </div>
    </section>"""


def guarantee(
    pre: str,
    h2: str = "Double guarantee",
    *,
    tag: str = "The risk is on us",
    subtitle: str = "Two clear promises &mdash; if we don&rsquo;t deliver, you get a full refund.",
) -> str:
    img = f"{pre}img/team/"
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
            <p class="brt-body">Before we start, we agree 3&ndash;5 value criteria together. If none are met at the end, you receive a full refund. No questions asked.</p>
          </li>
        </ul>
        <aside class="brt-guarantee-cta brt-fade-up" aria-label="Book an intro call">
          <div class="brt-guarantee-cta__icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
          </div>
          <div class="brt-guarantee-cta__copy">
            <p class="brt-guarantee-cta__lead">Let&rsquo;s turn your risk into clarity.</p>
            <p class="brt-guarantee-cta__sub">Book a free, no-obligation intro call today.</p>
          </div>
          <a class="brt-btn brt-btn--white" href="{pre}contact/">Book an appointment now →</a>
          <div class="brt-guarantee-cta__team">
            <div class="brt-guarantee-cta__avatars" aria-hidden="true">
              <img src="{img}till-blania.webp" alt="" width="80" height="80" loading="lazy" decoding="async">
              <img src="{img}peter-muenstermann.webp" alt="" width="80" height="80" loading="lazy" decoding="async">
            </div>
            <div>
              <p class="brt-guarantee-cta__team-name">Your Beraterium team</p>
              <p class="brt-guarantee-cta__team-note">We&rsquo;re here for you.</p>
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
    ("What is the Blindspot Check?",
     "The Blindspot Check is a free online self-assessment by Beraterium. In 10 to 15 questions you check where your business is vulnerable — around key people, technology and day-to-day operations. You get your results immediately, no sign-up required."),
    ("How long does the Blindspot Check take?",
     "About 10 minutes. Depending on your audience choice you answer 10 to 15 short 'What happens if …' questions and see your results right afterwards."),
    ("Is the Blindspot Check free?",
     "Yes, the check is completely free and can be used without registration. Optionally, you can have the results sent to you as a PDF report by email."),
    ("Does the check replace a full risk analysis?",
     "No. The Blindspot Check covers a selection from more than 100 hazard areas of our 3-level hazard catalog. A good result does not mean all risks are ruled out — that is what Beraterium's systematic risk analysis is for."),
    ("Who is the Blindspot Check for?",
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
            "Blindspot Check: where is your business vulnerable?",
            "Answer 10–15 short 'What happens if …' questions and get immediate results: traffic-light status, a risk profile by category and concrete first steps for your most critical points.",
            compact=True,
            actions='<a class="brt-btn brt-btn--on-dark brt-btn--lg" href="#brt-blindspot">Start the check now</a>',
        )
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="why-title">
      <div class="brt-container brt-fade-up">
        <h2 id="why-title" class="brt-h2">Why a Blindspot Check?</h2>
        <p class="brt-body">Most businesses don't fail because of the risks they know — they fail because of the ones they never looked at. The Blindspot Check makes these blind spots visible: it examines 15 of the more than 100 hazard areas from our 3-level hazard catalog, spread across <strong>People</strong>, <strong>Technology</strong> and <strong>Operations</strong>.</p>
        <p class="brt-body">Each question describes a concrete scenario. You rate how critical it would be for you — and whether you have already prepared measures. The result is your personal risk profile with a traffic-light status per question.</p>
      </div>
    </section>
    <section id="check" class="brt-section brt-section--alt" aria-labelledby="check-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">INTERACTIVE CHECK</p>
          <h2 id="check-title" class="brt-h2">The Blindspot Quick Check</h2>
        </header>
        <div id="brt-blindspot" class="bqc-widget brt-fade-up" aria-live="polite"></div>
      </div>
    </section>
    <section class="brt-section brt-section--narrow" aria-labelledby="limits-title">
      <div class="brt-container brt-fade-up">
        <h2 id="limits-title" class="brt-h2">What the check does — and what it doesn't</h2>
        <p class="brt-body">The Blindspot Check is a quick test, not a full risk analysis. It looks at selected, particularly common blind spots. An unremarkable result does not mean the remaining hazard areas hold no risks. If you want certainty, take the next step: the systematic <a href="{pre}method/">Beraterium method</a> examines all three levels of the hazard catalog — including prioritisation and an action plan through our <a href="{pre}services/">services</a>.</p>
      </div>
    </section>""".replace("{pre}", pre)
        + faq_section_html(
            BLINDSPOT_FAQ,
            title="Frequently asked questions about the Blindspot Check",
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


if __name__ == "__main__":
    print("Generating pages...")
    blindspot_selfcheck()
    gen_ueber_uns()
    gen_team()
    gen_mission_vision()
    gen_methode()
    gen_angebote()
    gen_lp_startups()
    gen_lp_kmu()
    gen_lp_solo()
    gen_risikoradar()
    gen_tools_index()
    gen_blindspot_check()
    gen_blog()
    gen_blog_singles()
    gen_home_analyse()
    gen_home_team()
    gen_home_nav()
    gen_home_analytics()
    gen_home_tools_teaser()
    gen_home_blog_teaser()
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
