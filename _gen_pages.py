#!/usr/bin/env python3
"""Generate Beraterium static pages from briefing content."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from _i18n import DE_SITE_URL, EN_SITE_URL, hreflang_links, language_switcher_html

from _pricing import PRICE_CATEGORIES, format_eur, offer_price_text
from _pricing_geo import (
    PREISE_GEO_FAQ,
    SCHULUNGEN_GEO_FAQ,
    pricing_compare_section,
    schulungen_value_section,
    schulung_geo_note,
)

from _schulungen import SCHULUNG_CONFIGS

from _international_pages import (
    INT_INDEX_RU,
    cards_slider_block,
    int_faq_title,
    int_is_project_offer,
    int_team_member_intros,
    international_audience_section,
    international_excluded_section,
    international_journey_section,
    international_stage_scope_section,
    international_legal_section,
    international_next_stages_section,
    international_outcome_section,
    international_packages_section,
    international_price_section,
    international_process_section,
    international_project_price_banner,
    international_project_section,
    international_single_stage_price_banner,
    international_stage_scope_section,
    international_stages_price_banner,
    international_stages_section,
    international_team_section,
    locale_paths,
    ru_offer_configs,
)
from _internationale_stufen import INT_STAGES
from _internationale_stufen_detail import (
    iter_stage_pages,
    merged_stage,
    parent_slug,
    stage_rel_path,
    stage_slug,
)
from _internationale_stufen_detail_ru import apply_stage_locale
from _internationale_angebote import INT_INDEX_DE, INT_INDEX_EN, INT_OFFER_CONFIGS_DE, LEGAL_NOTICE_DE, LEGAL_NOTICE_RU, LEGAL_NOTICE_EN, en_offer_configs

from _blindspot import blindspot_config_json
from _blindspot import selfcheck as blindspot_selfcheck
from _ra_prep import ra_prep_config_json
from _ra_prep import selfcheck as ra_prep_selfcheck

from _cms import (
    BlogPost,
    TeamMember,
    article_author_sidebar_html,
    article_faq_section_html,
    faq_section_html,
    author_name_link_html,
    article_sidebar_html,
    article_youtube_embed_html,
    blog_card_html,
    blog_filters_html,
    blog_meta_description,
    blog_posting_schema,
    blog_hero_public_url,
    blog_shell_title,
    combine_jsonld,
    faq_page_schema,
    offer_catalog_schema,
    course_schema,
    service_schema,
    speakable_webpage_schema,
    local_business_schema,
    format_date_de,
    header_logo_html,
    home_team_section_html,
    img_html,
    ki_image_label_html,
    load_blog_posts,
    load_team_members,
    person_schema,
    team_by_slug,
    team_contact_icons,
    team_profile_bio_html,
    team_profile_section,
    team_section_id,
    about_founder_section_html,
    about_team_section_html,
    write_sitemap,
)

SITE = Path(__file__).parent
BRT_ASSET_VERSION = "20260911-price-details-bg-v1"

ALT_TILL = "Till Manfred Blania, Geschäftsführer Beraterium"
ALT_PETER = "Peter Münstermann, Beraterium"

IMG_HOME_ANALYSE = "img/home/analyse-situation.webp"
IMG_METHODE_GEFAHRENKATALOG = "img/methode/gefahrenkatalog-3-ebenen.webp"
IMG_UEBER_UNS_RISIKORADAR = "img/ueber-uns/risikoradar.webp"
IMG_ANGEBOT_STARTUPS_HERO = "img/angebote/startups/hero.webp"
IMG_ANGEBOT_KMU_HERO = "img/angebote/kmu/hero.webp"
IMG_ANGEBOT_SOLO_HERO = "img/angebote/solo/hero.webp"
IMG_RELEVANZ_SCHWELLE = "img/garantie/relevanz-schwelle.webp"
IMG_NUTZEN_KRITERIEN = "img/garantie/nutzen-kriterien.webp"
IMG_BLINDSPOT_WARUM = "img/tools/blindspot-warum.webp"
IMG_RA_PREP_VORBEREITUNG = "img/tools/ra-prep-vorbereitung.webp"


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

GA4_ANALYTICS_HEAD = f"""  <!-- Google Consent Mode v2 + GA4 (CookieYes setzt analytics_storage) -->
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('consent', 'default', {{
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied',
      functionality_storage: 'denied',
      personalization_storage: 'denied',
      security_storage: 'granted',
      wait_for_update: 500
    }});
  </script>
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
  <script>
    gtag('js', new Date());
    gtag('config', '{GA4_MEASUREMENT_ID}', {{
      linker: {{ domains: ['beraterium.de', 'beraterium.com'] }}
    }});
    function brtGrantAnalyticsConsent() {{
      gtag('consent', 'update', {{ analytics_storage: 'granted' }});
    }}
    document.addEventListener('cookieyes_consent_update', function (event) {{
      var accepted = (event.detail && event.detail.accepted) || [];
      if (accepted.indexOf('analytics') !== -1) brtGrantAnalyticsConsent();
    }});
    document.addEventListener('DOMContentLoaded', function () {{
      setTimeout(function () {{
        try {{
          if (typeof getCkyConsent === 'function' && getCkyConsent().categories.analytics) {{
            brtGrantAnalyticsConsent();
          }}
        }} catch (e) {{}}
      }}, 800);
    }});
  </script>"""

NAV = [
    ("angebote", "Angebote"),
    ("methode", "Methode"),
    ("ueber-uns", "Über uns"),
    ("risikoradar", "RisikoRadar"),
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
    angebote_active = bool(
        active and (active.startswith("angebote") or active in ("preise", "schulungen", "internationale-angebote"))
    )
    angebote_cur = ' aria-current="page"' if active == "angebote" else ""
    preise_cur = ' aria-current="page"' if active == "preise" else ""
    schulungen_cur = ' aria-current="page"' if active == "schulungen" else ""
    internationale_cur = ' aria-current="page"' if active == "internationale-angebote" else ""
    ueber_active = active in ("ueber-uns", "team")
    tools_active = bool(active and active.startswith("tools"))
    tools_cur = ' aria-current="page"' if active == "tools" else ""

    def angebot_sub_cur(slug: str) -> str:
        return ' aria-current="page"' if active == f"angebote/{slug}" else ""

    def nav_cur(slug: str) -> str:
        return ' aria-current="page"' if active == slug else ""

    items = [
        f"""        <li class="site-header__item site-header__item--has-menu{" is-active" if angebote_active else ""}">
          <a href="{pre}angebote/" class="site-header__parent-link"{angebote_cur} aria-expanded="false">
            Angebote
            {CARET_SVG}
          </a>
          <ul class="site-header__submenu" aria-label="Angebote">
            <li><a href="{pre}angebote/startups/"{angebot_sub_cur("startups")}>Startups</a></li>
            <li><a href="{pre}angebote/kmu/"{angebot_sub_cur("kmu")}>KMU</a></li>
            <li><a href="{pre}angebote/solo/"{angebot_sub_cur("solo")}>Solo-Selbstständige</a></li>
            <li><a href="{pre}schulungen/"{schulungen_cur}>Schulungen</a></li>
            <li><a href="{pre}internationale-angebote/"{internationale_cur}>Internationale Angebote</a></li>
            <li><a href="{pre}preise/"{preise_cur}>Preise</a></li>
          </ul>
        </li>""",
        f'        <li><a href="{pre}methode/"{nav_cur("methode")}>Methode</a></li>',
        f"""        <li class="site-header__item site-header__item--has-menu{" is-active" if ueber_active else ""}">
          <a href="{pre}ueber-uns/" class="site-header__parent-link" aria-expanded="false">
            Über uns
            {CARET_SVG}
          </a>
          <ul class="site-header__submenu" aria-label="Über uns">
            <li><a href="{pre}ueber-uns/"{nav_cur("ueber-uns")}>Über das Unternehmen</a></li>
            <li><a href="{pre}team/"{nav_cur("team")}>Unser Team</a></li>
          </ul>
        </li>""",
        f'        <li><a href="{pre}risikoradar/"{nav_cur("risikoradar")}>RisikoRadar</a></li>',
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
        f'        <li><a href="{pre}loesungen/{cfg["slug"]}/">{cfg["breadcrumb_name"]}</a></li>'
        for cfg in LP_CONFIGS
    )
    standort_items = "\n".join(
        f'        <li><a href="{pre}standort/{cfg["slug"]}/">{cfg["breadcrumb_name"]}</a></li>'
        for cfg in STANDORT_CONFIGS
    )
    standort_section = (
        f"""    <section>
      <h2>Beraterium vor Ort</h2>
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
      <p>Konzern-Risikomanagement, übersetzt für den Mittelstand.</p>
      <a href="https://www.linkedin.com/company/beraterium">LinkedIn</a>
      <a href="https://www.youtube.com/@Beraterium">YouTube</a>
    </section>
    <section>
      <h2>Angebote</h2>
      <ul>
        <li><a href="{pre}angebote/startups/">Startups</a></li>
        <li><a href="{pre}angebote/kmu/">KMU</a></li>
        <li><a href="{pre}angebote/solo/">Solo-Selbstständige</a></li>
        <li><a href="{pre}angebote/">Übersicht</a></li>
        <li><a href="{pre}preise/">Preise &amp; Leistungen</a></li>
        <li><a href="{pre}schulungen/">Schulungen</a></li>
        <li><a href="{pre}internationale-angebote/">Internationale Angebote</a></li>
      </ul>
    </section>
    <section>
      <h2>Lösungen</h2>
      <ul>
{lp_links}
      </ul>
    </section>
{standort_section}    <section>
      <h2>Unternehmen</h2>
      <ul>
        <li><a href="{pre}ueber-uns/">Über uns</a></li>
        <li><a href="{pre}team/">Team</a></li>
        <li><a href="{pre}mission-vision/">Mission &amp; Vision</a></li>
        <li><a href="{pre}methode/">Methode</a></li>
        <li><a href="{pre}nutzen-garantie/">Nutzen-Garantie</a></li>
        <li><a href="{pre}relevanz-garantie/">Relevanz-Garantie</a></li>
      </ul>
    </section>
    <section>
      <h2>Kontakt</h2>
      <ul>
        <li><a href="{pre}kontakt/">Erstgespräch buchen</a></li>
        <li><a href="{pre}kontaktformular/">Kontaktformular</a></li>
        <li><a href="{pre}barrierefreiheit/">Barrierefreiheit</a></li>
        <li><a href="{pre}impressum/">Impressum</a></li>
        <li><a href="{pre}datenschutz/">Datenschutz</a></li>
        <li><a href="{pre}agb/">AGB</a></li>
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
    html_lang: str = "de",
    current_locale: str = "de",
) -> str:
    pre = pfx(depth)
    home = pre or "./"
    robots = '\n  <meta name="robots" content="noindex">' if noindex else ""
    ld = f"\n  <script type=\"application/ld+json\">\n{json_ld}\n  </script>" if json_ld else ""
    hreflang = hreflang_links(canonical, current_locale=current_locale)
    og_image_tag = f'\n  <meta property="og:image" content="{og_image}">' if og_image else ""
    lang_switch = language_switcher_html(current_locale=current_locale, canonical=canonical, depth=depth)
    og_locale = {"de": "de_DE", "en": "en_GB", "ru": "ru_RU"}.get(current_locale, "de_DE")
    site_base = EN_SITE_URL
    return f"""<!doctype html>
<html lang="{html_lang}">

<head>
{COOKIEYES_HEAD}
{GA4_ANALYTICS_HEAD}
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{site_base}{canonical}">{robots}{hreflang}

  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{site_base}{canonical}">
  <meta property="og:locale" content="{og_locale}">{og_image_tag}

  <link rel="icon" href="{pre}favicon.ico" sizes="any">
  <link rel="icon" href="{pre}icon.svg" type="image/svg+xml">
  <meta name="theme-color" content="#0E1116">
  <meta name="referrer" content="strict-origin-when-cross-origin">

  <link rel="stylesheet" href="{pre}css/brt.css?v={BRT_ASSET_VERSION}" data-brt-css>
  <link rel="stylesheet" href="{pre}css/brt-fallback.css?v={BRT_ASSET_VERSION}">
  <link rel="stylesheet" href="{pre}css/brt-layout-fix.css?v={BRT_ASSET_VERSION}">
  <link rel="stylesheet" href="{pre}css/brt-print.css?v={BRT_ASSET_VERSION}" media="print">{extra_css}
  <script src="{pre}js/brt-init.js"></script>{ld}
</head>

<body class="brt-page brt-page--inner">

<a class="brt-skip-link" href="#main-content">Zum Inhalt springen</a>

<header class="site-header site-header--solid" aria-label="Hauptnavigation">
  <div class="site-header__inner">
{header_logo_html(home, pre)}
    <button class="site-header__toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menü</button>
    <nav id="site-nav" class="site-header__nav" aria-label="Primäre Navigation">
      <ul>
{nav_html(depth, active_nav)}
      </ul>
{lang_switch}
      <a class="brt-btn brt-btn--outline site-header__cta" href="{pre}kontakt/">Erstgespräch buchen</a>
    </nav>
  </div>
</header>

<div class="brt">
  <main id="main-content">
{main}
  </main>
</div>

{footer_html(depth)}

<script src="{pre}js/brt-analytics.js?v={BRT_ASSET_VERSION}"></script>
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
          <span class="brt-image-placeholder__label">Bild folgt</span>
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


_CARDS_SLIDER_SVG_PREV = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>'
)
_CARDS_SLIDER_SVG_NEXT = (
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>'
)


def cards_slider_block(
    cards_html: str,
    *,
    aria_label: str,
    prev_label: str = "Zurück",
    next_label: str = "Weiter",
    autoplay_ms: int = 10000,
) -> str:
    """Horizontal card slider — 3 visible on desktop; optional autoplay (initCardsSlider)."""
    autoplay_attr = f' data-cards-slider-autoplay="{autoplay_ms}"' if autoplay_ms else ""
    return (
        f'<div class="brt-cards-slider brt-fade-up" data-cards-slider{autoplay_attr}>'
        f'<div class="brt-cards-slider__viewport" tabindex="0" role="group" aria-label="{aria_label}">'
        f'<ul class="brt-cards-slider__track">{cards_html}</ul>'
        "</div>"
        '<div class="brt-cards-slider__nav">'
        f'<button type="button" class="brt-cards-slider__btn brt-cards-slider__btn--prev" '
        f'aria-label="{prev_label}">{_CARDS_SLIDER_SVG_PREV}</button>'
        f'<button type="button" class="brt-cards-slider__btn brt-cards-slider__btn--next" '
        f'aria-label="{next_label}">{_CARDS_SLIDER_SVG_NEXT}</button>'
        "</div></div>"
    )


def cta_band(pre: str, h2: str, body: str, btn: str = "Erstgespräch buchen", *, note: str = "") -> str:
    note_html = f'\n        <p class="brt-meta brt-body--on-dark">{note}</p>' if note else ""
    return f"""
    <section class="brt-cta-band brt-cta-band--dark brt-section" aria-labelledby="final-cta">
      <div class="brt-container brt-cta-band__inner brt-fade-up">
        <h2 id="final-cta" class="brt-h2 brt-h2--on-dark">{h2}</h2>
        <p class="brt-body brt-body--on-dark">{body}</p>
        <a class="brt-btn brt-btn--on-dark brt-btn--lg" href="{pre}kontakt/" data-print-url="{DE_SITE_URL}/kontakt/">{btn}</a>{note_html}
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
            "slug": "relevanz-garantie",
            "num": "01",
            "icon": ICON_GUARANTEE_SHIELD,
            "title": "Relevanz-Garantie",
            "quote": "\u201eWir finden kein relevantes Risiko? Geld zur\u00fcck.\u201c",
            "body": "Identifiziert die Analyse kein einziges Risiko mit relevanter Schadensh\u00f6he, erstatten wir den vollen Betrag.",
            "link": "Mehr erfahren \u2192",
        },
        "nutzen": {
            "slug": "nutzen-garantie",
            "num": "02",
            "icon": ICON_GUARANTEE_TARGET,
            "title": "Nutzen-Garantie",
            "quote": "\u201eKein messbarer Nutzen? Geld zur\u00fcck.\u201c",
            "body": "Wird am Ende auch nur eines der drei vereinbarten Kriterien nicht erf\u00fcllt, erstatten wir 100 % des Projektpreises.",
            "link": "Mehr erfahren \u2192",
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
            f'<div class="brt-guarantee-card__foot"><span class="brt-guarantee-here"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>Sie sind hier</span></div>'
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
          <p class="brt-tag">DOPPELTE GARANTIE</p>
          <h2 id="guarantee-pair" class="brt-h2">Beide S\u00e4ulen unseres Sicherheitsversprechens</h2>
          <p class="brt-body brt-section__lede">Zwei klare Versprechen \u2013 wenn wir nicht liefern, erstatten wir den vollen Betrag.</p>
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
    contact_slug: str = "kontakt",
    team_name: str = "Ihr Beraterium-Team",
    team_note: str = "Wir sind für Sie da.",
    aria: str = "Erstgespräch vereinbaren",
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
              <img src="{img}till-blania.webp" alt="{ALT_TILL}" width="80" height="80" loading="lazy" decoding="async">
              <img src="{img}peter-muenstermann.webp" alt="{ALT_PETER}" width="80" height="80" loading="lazy" decoding="async">
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
        tag = "IMMER DREI STUFEN"
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
                "approach_headline": "Stufe&nbsp;1 + Stufe&nbsp;2 + Folgemodule",
                "approach_body": "Stufe&nbsp;1: vier gleich gewichtete Top-Risiken. Stufe&nbsp;2: Bearbeitungslogiken für IT/Cyber, Reputation, Totalausfall und Organisation. Folgemodule: Finanztransparenz (Umsatzmix, Hebel) und fokussierter 3-Monats-Akquise-Test.",
                "stats": [("4", "Top-Risiken: IT/Cyber, Reputation, Totalausfall, Prozesse"), ("A–D", "Stufe-2-Blöcke mit nächsten Schritten"), ("3", "Phasen: Sofort, 1–3 Monate, Folgetermine"), ("↗", "Umsatzmix + 1 Kanal-Test")],
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
    h2: str = "Doppelte Garantie",
    *,
    tag: str | None = None,
    subtitle: str = "Zwei klare Versprechen – wenn wir nicht liefern, erstatten wir den vollen Betrag.",
    du: bool = False,
) -> str:
    img = f"{pre}img/team/"
    if tag is None:
        tag = "Dein Risiko liegt bei uns" if du else "Ihr Risiko liegt bei uns"
    nutzen_body = (
        "Wir legen vor dem Start gemeinsam drei Nutzen-Kriterien fest – zwei messbare, eines emotional. Erfüllst du am Ende auch nur eines nicht, bekommst du den vollen Betrag zurück. Ohne Diskussion."
        if du
        else "Wir legen vor dem Start gemeinsam drei Nutzen-Kriterien fest – zwei messbare, eines emotional. Wird am Ende auch nur eines nicht erfüllt, bekommen Sie den vollen Betrag zurück. Ohne Diskussion."
    )
    cta_lead = (
        "Lass uns dein Risiko in Klarheit verwandeln."
        if du
        else "Lassen Sie uns Ihr Risiko in Klarheit verwandeln."
    )
    cta_sub = (
        "Vereinbare jetzt ein unverbindliches Erstgespräch."
        if du
        else "Vereinbaren Sie jetzt ein unverbindliches Erstgespräch."
    )
    team_name = "Dein Beraterium-Team" if du else "Ihr Beraterium-Team"
    team_note = "Wir sind für dich da." if du else "Wir sind für Sie da."
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
            <h3 class="brt-h3">Relevanz-Garantie</h3>
            <p class="brt-quote">„Wir finden kein relevantes Risiko? Geld zurück."</p>
            <p class="brt-body">Identifiziert die Analyse kein einziges Risiko mit relevanter Schadenshöhe (Schwelle vorab gemeinsam definiert), erstatten wir den vollen Betrag.</p>
            <a href="{pre}relevanz-garantie/">Mehr erfahren →</a>
          </li>
          <li class="brt-card brt-card--guarantee brt-hover-lift">
            <div class="brt-guarantee__visual">
              <div class="brt-guarantee__icon" aria-hidden="true">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              </div>
              <span class="brt-guarantee__num" aria-hidden="true">02</span>
            </div>
            <h3 class="brt-h3">Nutzen-Garantie</h3>
            <p class="brt-quote">„Kein messbarer Nutzen? Geld zurück."</p>
            <p class="brt-body">{nutzen_body}</p>
            <a href="{pre}nutzen-garantie/">Mehr erfahren →</a>
          </li>
        </ul>
        <aside class="brt-guarantee-cta brt-fade-up" aria-label="Erstgespräch vereinbaren">
          <div class="brt-guarantee-cta__icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
          </div>
          <div class="brt-guarantee-cta__copy">
            <p class="brt-guarantee-cta__lead">{cta_lead}</p>
            <p class="brt-guarantee-cta__sub">{cta_sub}</p>
          </div>
          <a class="brt-btn brt-btn--white" href="{pre}kontakt/">Jetzt Termin vereinbaren →</a>
          <div class="brt-guarantee-cta__team">
            <div class="brt-guarantee-cta__avatars">
              <img src="{img}till-blania.webp" alt="{ALT_TILL}" width="80" height="80" loading="lazy" decoding="async">
              <img src="{img}peter-muenstermann.webp" alt="{ALT_PETER}" width="80" height="80" loading="lazy" decoding="async">
            </div>
            <div>
              <p class="brt-guarantee-cta__team-name">{team_name}</p>
              <p class="brt-guarantee-cta__team-note">{team_note}</p>
            </div>
          </div>
        </aside>
      </div>
    </section>"""


def faq_section(items: list[tuple[str, str]], *, alt: bool = False, title: str = "Häufige Fragen") -> str:
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
        "Netzwerk und Zusammenarbeit bei RisikoRadar",
        1,
    )
    main = (
        hero(
            pre,
            "ÜBER BERATERIUM",
            "Warum es Beraterium gibt",
            "Risiken verstehen sollte kein Privileg großer Konzerne sein. Wir bringen professionelles Risikomanagement dorthin, wo es bisher gefehlt hat: in den Mittelstand, zu Startups und Solo-Selbstständigen.",
        )
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="story-title">
      <div class="brt-container brt-fade-up">
        <h2 id="story-title" class="brt-h2">Eine Methode, die zur Realität von Unternehmern passt</h2>
        <p class="brt-body">Viele Unternehmer wissen, dass Risiken existieren. Aber nur wenige wissen wirklich, welche Risiken für ihr Unternehmen die größten sind.</p>
        <p class="brt-body">Klassische Risikomanagement-Methoden sind oft für Konzerne gemacht: komplex, theoretisch und aufwendig. Für mittelständische Unternehmen, Startups oder Kleinunternehmen passen sie selten zur Realität.</p>
        <p class="brt-body">Beraterium ist aus genau dieser Lücke entstanden. Wir haben eine Methode entwickelt, mit der Unternehmen gemeinsam mit ihren Mitarbeitenden in kurzer Zeit ein klares Bild ihrer wichtigsten Risiken erhalten – verständlich, praxisnah und ohne Bürokratie.</p>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="values-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">WOFÜR WIR STEHEN</p>
          <h2 id="values-title" class="brt-h2">Konzern-Erfahrung, Start-up-Spirit, echte Augenhöhe</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Konzern-Erfahrung für alle</h3>
            <p class="brt-body">Was bisher nur großen Unternehmen zur Verfügung stand, machen wir für Startups, KMU und kleine Unternehmen verständlich, erschwinglich und einsatzbereit.</p>
          </li>
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Mensch vor System</h3>
            <p class="brt-body">Im Mittelpunkt steht der Mitarbeiter, nicht das Tool. Wir führen Analysen mit den Menschen durch – nicht über ihre Köpfe hinweg. So entstehen realistische Ergebnisse und echte Akzeptanz.</p>
          </li>
          <li class="brt-card brt-hover-lift">
            <h3 class="brt-h3">Wirkung vor Perfektion</h3>
            <p class="brt-body">Lieber eine gute Schätzung als eine perfekte Rechnung, die nie gemacht wird. Wir suchen nicht die meisten Maßnahmen – sondern die richtigen.</p>
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
          <p class="brt-tag">MEHR ALS BERATUNG</p>
          <h2 id="radar-teaser" class="brt-h2">Aus Erkenntnissen werden Schritte</h2>
          <p class="brt-body">Im Gegensatz zu Facebook-Gruppen, offenen Foren oder LinkedIn ist RisikoRadar ein geschlossener Club: Zugang nur über Empfehlung oder Bewerbung. Kein stilles Mitlesen, kein Network-Marketing — sondern geprüfte Experten, die wirklich beitragen. Ein einzelner Berater deckt vielleicht 80&nbsp;% ab; Risiken hängen aber zusammen — IT, Arbeitsschutz, Führung, DSGVO. In RisikoRadar arbeiten mehrere Experten an einer Lösung. Kunden erhalten einen kostenfreien Jahreszugang.</p>
          <a class="brt-btn brt-btn--ghost" href="../risikoradar/">RisikoRadar entdecken →</a>
        </div>
{radar_media}
      </div>
    </section>
    <section class="brt-quote-band brt-quote-band--accent" aria-label="Zitat">
      <div class="brt-container brt-fade-up">
        <p class="brt-quote-band__text">„Beraterium ist ein Denkraum für Unternehmer, in dem Risiken sichtbar werden und bessere Entscheidungen entstehen."</p>
      </div>
    </section>
"""
        + about_team_section_html(1)
    )
    main = main.replace("{radar_media}", radar_media)
    ueber_uns_faq = [
        ("Was ist Beraterium?", "Beraterium macht professionelles Risikomanagement für KMU, Startups und Solo-Selbstständige zugänglich — verständlich, praxisnah und ohne Konzern-Bürokratie."),
        ("Für wen ist Beraterium gedacht?", "Für Geschäftsführer, Gründer und Solo-Selbstständige, die wissen wollen, welche Risiken ihr Unternehmen wirklich treffen könnten — bevor sie teuer werden."),
        ("Was unterscheidet Beraterium von klassischer Beratung?", "Wir liefern kein PowerPoint zum Ablegen: strukturierte Risikoanalyse in Euro, moderiert mit Ihrem Team, mit klarer Umsetzung — selbst, mit Partnern oder über RisikoRadar."),
    ]
    main += faq_section_html(ueber_uns_faq, title="Häufige Fragen zu Beraterium", section_id="faq", alt=True)
    main += cta_band(
        pre,
        "Lernen wir uns kennen.",
        "Im kostenlosen Erstgespräch zeigen wir Ihnen, wie Sie Ihre größten Risiken sichtbar machen – in 30 Minuten, ohne Verpflichtung.",
    )
    write(
        "ueber-uns/index.html",
        shell(
            depth=1,
            title="Über Beraterium – Warum es uns gibt | Beraterium",
            description="Beraterium macht Konzern-Risikomanagement für KMU, Startups und Solo zugänglich — verständlich, praxisnah, ohne Bürokratie.",
            canonical="/ueber-uns/",
            active_nav="ueber-uns",
            main=main,
            json_ld=page_schema(faq_page_schema(ueber_uns_faq)),
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
            "UNSER TEAM",
            "Ein Team mit vielen Perspektiven, ein Ziel: Ihre Sicherheit",
            "Hinter Beraterium stehen Menschen mit jahrzehntelanger Industriekompetenz und frischem Unternehmergeist – praxisorientiert, lösungsorientiert und immer auf Augenhöhe.",
            compact=True,
        )
        + profiles
        + """
    <section class="brt-section" aria-labelledby="shared-values">
      <div class="brt-container brt-fade-up">
        <ul class="brt-values-inline">
          <li>Auf Augenhöhe</li>
          <li>Praxis statt Theorie</li>
          <li>Mensch vor System</li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--dark" aria-labelledby="network-title">
      <div class="brt-container brt-split brt-split--text-only">
        <div class="brt-split__text brt-fade-up">
          <h2 id="network-title" class="brt-h2 brt-h2--on-dark">Und ein ganzes Netzwerk im Rücken</h2>
          <p class="brt-body brt-body--on-dark">Für die Umsetzung greifen wir auf RisikoRadar zurück – ein geschütztes Netzwerk geprüfter Experten, deren Zugang nur über Empfehlung oder Bewerbung möglich ist. So bekommen Sie bei Bedarf genau die Spezialisten, die zu Ihrem Thema passen.</p>
          <a class="brt-btn brt-btn--on-dark" href="../risikoradar/">RisikoRadar →</a>
        </div>
      </div>
    </section>"""
        + cta_band(
            pre,
            "Sprechen Sie direkt mit uns",
            "Jede Analyse wird von Till und Peter persönlich begleitet. Buchen Sie Ihr kostenloses Erstgespräch.",
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
            title="Unser Team – Beraterium",
            description="Team hinter Beraterium: Gründer, Risikomanagement und Branchenexpertise für KMU, Startups und Solo-Selbstständige.",
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
            "Risiken verstehen. Zukunft sichern. Gemeinsam.",
            "Wir glauben, dass jedes Unternehmen – unabhängig von seiner Größe – das Recht hat, seine größten Risiken zu kennen und ihnen souverän zu begegnen.",
            compact=True,
        )
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="mission-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">UNSERE MISSION</p>
        <h2 id="mission-title" class="brt-h2">Konzern-Werkzeuge für den Mittelstand zugänglich machen</h2>
        <p class="brt-lead">Wir unterstützen Startups, KMU und Solo-Selbstständige mit Risiko- und HR-Management-Lösungen, die sonst nur großen Organisationen zur Verfügung stehen. Verständlich, erschwinglich und sofort umsetzbar. Wir verbinden 20 Jahre deutsche Industriekompetenz mit Start-up-Spirit – damit aus Bauchgefühl Klarheit wird und aus Klarheit Handlungsfähigkeit.</p>
      </div>
    </section>
    <section class="brt-section brt-section--dark" aria-labelledby="vision-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">UNSERE VISION</p>
        <h2 id="vision-title" class="brt-h2 brt-h2--on-dark">Unternehmen, in denen Menschen gerne arbeiten</h2>
        <p class="brt-body brt-body--on-dark">Wir wollen, dass Risikomanagement nicht als Quelle der Angst, sondern als Chance für nachhaltigen Erfolg verstanden wird. Unsere Vision sind Unternehmen, die Risiken früh erkennen, Verantwortung teilen und gemeinsam wachsen – Orte, an denen Sicherheit, Vertrauen und Zusammenarbeit selbstverständlich sind.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="principles-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">WAS UNS LEITET</p>
          <h2 id="principles-title" class="brt-h2">Sechs Prinzipien, die unsere Arbeit prägen</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Auf Augenhöhe</h3><p class="brt-body">Fair, ehrlich und immer an Ihrer Seite. Wir sprengen nicht Ihr Budget – wir verhelfen Ihnen zu nachhaltigem Erfolg.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Mensch vor System</h3><p class="brt-body">Der Mitarbeiter kennt die Abläufe und Schwachstellen oft besser als jedes Handbuch. Wir arbeiten mit den Menschen, nicht über ihre Köpfe hinweg.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Klarheit statt Komplexität</h3><p class="brt-body">Komplexe Themen machen wir einfach, verständlich und sofort anwendbar. So erzielen Sie schnell Ergebnisse.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Wirkung vor Perfektion</h3><p class="brt-body">Tendenz vor absoluter Genauigkeit. Lieber eine gute Schätzung als eine perfekte Rechnung, die nie gemacht wird.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Individuell statt Standard</h3><p class="brt-body">Theorie und Praxis verbinden: gemeinsam mit Ihnen und Ihrem Team entwickeln wir Lösungen, die zu Ihrem Unternehmen passen.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Verantwortung &amp; Partnerschaft</h3><p class="brt-body">Wir bleiben die Klammer – unabhängig davon, welchen Weg der Umsetzung Sie wählen.</p></li>
        </ul>
      </div>
    </section>"""
        + faq_section_html([
            ("Was ist die Mission von Beraterium?", "Konzern-Risikomanagement für KMU, Startups und Solo zugänglich machen — verständlich, erschwinglich und sofort umsetzbar."),
            ("Was ist die Vision von Beraterium?", "Unternehmen, in denen Menschen gerne arbeiten, Risiken früh erkennen und gemeinsam wachsen."),
        ], title="Häufige Fragen zu Mission & Vision", section_id="faq", alt=True)
        + cta_band(
            pre,
            "Teilen Sie unsere Haltung?",
            "Dann lassen Sie uns sprechen. 30 Minuten, kostenlos, unverbindlich.",
        )
    )
    mission_faq = [
        ("Was ist die Mission von Beraterium?", "Konzern-Risikomanagement für KMU, Startups und Solo zugänglich machen — verständlich, erschwinglich und sofort umsetzbar."),
        ("Was ist die Vision von Beraterium?", "Unternehmen, in denen Menschen gerne arbeiten, Risiken früh erkennen und gemeinsam wachsen."),
    ]
    write(
        "mission-vision/index.html",
        shell(
            depth=1,
            title="Mission & Vision – Risikomanagement für alle | Beraterium",
            description="Mission: Risikomanagement für alle zugänglich. Vision: Unternehmen, in denen Menschen gerne arbeiten und Risiken früh erkannt werden.",
            canonical="/mission-vision/",
            active_nav=None,
            main=main,
            json_ld=page_schema(faq_page_schema(mission_faq)),
        ),
    )


def pricing_cards(pre: str, options: list[dict], *, du: bool = False, price_note: str | None = None) -> str:
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
            <a class="brt-btn brt-btn--outline" href="{pre}kontakt/">Erstgespräch buchen</a>
          </li>"""
        )
    return f"""
    <section id="optionen" class="brt-section brt-section--alt" aria-labelledby="options-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">DREI WEGE</p>
          <h2 id="options-title" class="brt-h2">{"Wähle, wie weit wir gemeinsam gehen" if du else "Wählen Sie, wie weit wir gemeinsam gehen"}</h2>
        </header>
        <ul class="brt-pricing brt-stagger">
{chr(10).join(cards)}
        </ul>
        <p class="brt-meta brt-centered-cta brt-fade-up" style="margin-top: var(--space-8);">{price_note if price_note else ("Preise besprechen wir individuell im Erstgespräch – passend zu deiner Phase und deinem Umfang." if du else "Preise besprechen wir individuell im Erstgespräch – passend zu Phase und Umfang.")}</p>
      </div>
    </section>"""


def gen_methode() -> None:
    pre = "../"
    faq = [
        ("Was ist ein Gefahrenkatalog im Risikomanagement?", "Ein Gefahrenkatalog ist eine strukturierte, bewertungsfreie Liste aller Ereignisse, die einem Unternehmen schaden könnten. Der 3-Ebenen-Gefahrenkatalog von Beraterium hält die Anzahl handhabbar. Erst wenn der Katalog vollständig ist, beginnt die Bewertung."),
        ("Was ist der Unterschied zwischen Gefahr und Risiko?", "Eine Gefahr ist alles, was schaden kann – neutral gesammelt. Zum Risiko wird sie erst, wenn wir einschätzen, wie wahrscheinlich das Eintreten ist und welchen Schaden es in Euro verursachen würde."),
        ("Warum bewertet Beraterium Risiken in Euro statt mit Ampelfarben?", "Ampelfarben sind subjektiv. Ein Schaden in Euro ist konkret verhandelbar und ermöglicht objektive Priorisierung — größter Schaden zuerst, unabhängig von Bauchgefühl oder Hierarchie."),
        ("Was ist ein Risikomanagement-Prozess und wie sieht er bei Beraterium aus?", "Drei Phasen: (1) Gefahren sammeln im 3-Ebenen-Gefahrenkatalog, (2) Risiken bewerten — Schaden in Euro × Eintrittswahrscheinlichkeit, abzüglich vorhandener Maßnahmen, (3) die wenigen Maßnahmen mit dem größten Wirkungsgrad umsetzen."),
        ("Wie lange dauert eine Risikoanalyse?", "Je nach Zielgruppe typischerweise 2 Wochen (Solo) bis 6 Wochen (KMU). Den genauen Rahmen legen wir im Kick-off fest."),
        ("Brauche ich Vorwissen oder Vorbereitung?", "Nein. Sie bringen Ihr Wissen über Ihr Unternehmen mit – die Struktur und die Methode bringen wir mit."),
        ("Was, wenn ich allein arbeite?", "Dann ersetzen zwei Moderatoren und ein KI-Impulsgeber das fehlende Team, damit die Bewertung trotzdem ausgewogen ist."),
        ("Setzt ihr die Maßnahmen auch um?", "Sie entscheiden über den Weg: selbst, mit Ihren Dienstleistern oder durch unsere Koordination über das RisikoRadar-Netzwerk. Beraterium bleibt die Klammer."),
    ]
    methode_title = "Risikomanagement-Methode: 3-Ebenen-Katalog | Beraterium"
    methode_desc = "Wie funktioniert Risikomanagement ohne Konzern-Bürokratie? 3-Ebenen-Gefahrenkatalog, Bewertung in Euro, Maßnahmen-Priorisierung. Kostenlos kennenlernen."
    methode_ld = page_schema(
        service_schema(
            name="Beraterium Risikomanagement-Methode",
            description=methode_desc,
            url="/methode/",
            audience="KMU, Startups und Solo-Selbstständige",
        ),
        faq_page_schema(faq),
        speakable_webpage_schema("/methode/"),
    )
    main = (
        hero(
            pre,
            "WIE WIR ARBEITEN",
            "Von Bauchgefühl zu Klarheit – in nachvollziehbaren Schritten",
            "Unsere Methode trennt bewusst drei Fragen: Was passiert im schlimmsten Fall? Wie oft passiert das? Und was haben Sie heute schon dagegen getan? So entsteht Schritt für Schritt ein klares Bild.",
            actions=f'<a class="brt-btn" href="{pre}kontakt/">Erstgespräch buchen</a>',
        )
        + f"""
    <nav class="brt-anchor-nav" aria-label="Sprungnavigation auf dieser Seite" data-anchor-nav>
      <div class="brt-container brt-anchor-nav__inner">
        <p class="brt-anchor-nav__label">Auf dieser Seite</p>
        <div class="brt-anchor-nav__track">
          <ul class="brt-anchor-nav__list">
            <li><a class="brt-anchor-nav__link" href="#gefahrenkatalog">Gefahrenkatalog</a></li>
            <li><a class="brt-anchor-nav__link" href="#bewertung">Bewertung</a></li>
            <li><a class="brt-anchor-nav__link" href="#inventar">Inventar</a></li>
            <li><a class="brt-anchor-nav__link" href="#umsetzung">Umsetzung</a></li>
            <li><a class="brt-anchor-nav__link" href="#faq">FAQ</a></li>
          </ul>
        </div>
      </div>
    </nav>
    <section id="gefahrenkatalog" class="brt-section" aria-labelledby="s3-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="s3-title" class="brt-h2">Was ist der Gefahrenkatalog – und warum 3 Ebenen?</h2>
          <p class="brt-body">Der Gefahrenkatalog sammelt zunächst neutral und vollständig, was einem Unternehmen schaden kann – ohne zu bewerten, wie wahrscheinlich oder schlimm etwas ist. Damit die Zahl möglicher Gefahren handhabbar bleibt, ist der Katalog auf drei klare Ebenen begrenzt.</p>
          <p class="brt-body">Wir arbeiten bewusst mit Gefahren, weil sie eine neutrale Ausgangsbasis bilden. Erst im zweiten Schritt werden daraus Risiken – wenn wir bewerten, wie relevant eine Gefahr konkret für Ihr Unternehmen ist.</p>
        </div>
        {split_media_html(IMG_METHODE_GEFAHRENKATALOG, "Der Gefahrenkatalog von Beraterium mit drei Ebenen", 1, contain=True, hover_zoom=True)}
      </div>
    </section>
    <section id="bewertung" class="brt-section brt-section--alt" aria-labelledby="s4-title">
      <div class="brt-container brt-fade-up">
        <h2 id="s4-title" class="brt-h2">Wie bewerten wir, wie groß ein Risiko wirklich ist?</h2>
        <p class="brt-body">Wir gehen vom Gefühl zum konkreten Szenario. Statt zu fragen ‚Wie wahrscheinlich ist das?', sagen wir: ‚Stell dir vor, es ist bereits passiert.' Dann schätzen wir, was dieses Ereignis konkret für Ihr Unternehmen bedeutet – und übersetzen den Schaden in Euro.</p>
        <div class="brt-highlight-box" style="margin-top: var(--space-8);">
          <h3 class="brt-h3">Beispiel</h3>
          <p class="brt-body"><strong>Gefahr:</strong> Ausfall der Unternehmerperson (Schlüsselperson). <strong>Leitfrage:</strong> Was passiert, wenn Sie morgen nicht arbeiten können? <strong>Szenario:</strong> Ausfall für 4 Wochen. → Auf dieser Basis wird das Schadensausmaß in Euro eingeschätzt.</p>
        </div>
        <p class="brt-quote" style="margin-top: var(--space-8);">„Tendenz vor absoluter Genauigkeit."</p>
        <p class="brt-body">Lieber eine gute Schätzung als eine perfekte Rechnung, die nie gemacht wird.</p>
      </div>
    </section>
    <section id="inventar" class="brt-section" aria-labelledby="s5-title">
      <div class="brt-container brt-two-col brt-fade-up">
        <div>
          <h2 id="s5-title" class="brt-h2">Wird angerechnet, was wir schon tun?</h2>
          <p class="brt-body">Ja. Parallel zur Schadenshöhe bewerten wir die Eintrittswahrscheinlichkeit – in verständlichen Zeiträumen wie Wochen, Monaten oder Jahren. Und wir berücksichtigen Ihr ‚Inventar': vorhandene Maßnahmen, die das Risiko heute schon reduzieren.</p>
        </div>
        <div>
          <p class="brt-body">Etwa eine Vertretung, die kurzfristig rund 50&nbsp;% übernehmen kann. Der Schaden wäre grundsätzlich höher – wird durch solche Maßnahmen aber deutlich gemindert.</p>
        </div>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="s6-title">
      <div class="brt-container brt-fade-up">
        <h2 id="s6-title" class="brt-h2">Warum bewerten mehrere Personen statt einer?</h2>
        <p class="brt-body">Weil mehrere Blickwinkel zu einer realistischeren Einschätzung führen als eine Einzelmeinung. Im Unternehmen geschieht das idealerweise mit verschiedenen Verantwortlichen und Mitarbeitenden – im Mittelpunkt steht dabei immer der Mitarbeiter, nicht das System.</p>
        <div class="brt-highlight-box" style="margin-top: var(--space-8);">
          <h3 class="brt-h3">Und wenn ich allein bin?</h3>
          <p class="brt-body">Bei Solo-Selbstständigen und Kleinstunternehmen ersetzen wir das fehlende Team gezielt: zwei Moderatoren, die strukturieren und hinterfragen, plus einen KI-gestützten Impulsgeber für statistische Einschätzungen und Erfahrungswerte.</p>
        </div>
      </div>
    </section>
    <section id="umsetzung" class="brt-section brt-section--dark" aria-labelledby="s7-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 id="s7-title" class="brt-h2 brt-h2--on-dark">Was passiert nach der Analyse?</h2>
          <p class="brt-body brt-body--on-dark">Die Analyse schafft Klarheit – der eigentliche Mehrwert entsteht in der Umsetzung. Dafür stehen drei Wege offen. Welchen Sie wählen, entscheiden Sie. Beraterium bleibt die Klammer.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Selbst umsetzen</h3><p class="brt-body">Mit Ihrer eigenen Mannschaft. Geeignet für organisatorische oder einfache Maßnahmen und vorhandene Kompetenzen.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Mit Ihren Dienstleistern</h3><p class="brt-body">Mit vertrauten Partnern weiterarbeiten. Geeignet für gewachsene Geschäftsbeziehungen und etablierte Strukturen.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Wir koordinieren</h3><p class="brt-body">Ein fester Ansprechpartner, ‚one face to the customer'. Wir bringen die richtigen Menschen zusammen und sorgen, dass Maßnahmen ineinandergreifen.</p></li>
        </ul>
        <p class="brt-quote" style="margin-top: var(--space-8); color: #fff; text-align: center;">„Wir liefern keine Analyse zum Ablegen – sondern Lösungen zum Umsetzen."</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="s8-title">
      <div class="brt-container brt-fade-up">
        <h2 id="s8-title" class="brt-h2">Wie wählen wir aus, welche Maßnahmen wirklich helfen?</h2>
        <p class="brt-body">Wir kümmern uns zuerst um die größten Risiken. Jede Maßnahme verfolgt genau einen Zweck: die Schadenshöhe senken und/oder die Eintrittswahrscheinlichkeit reduzieren.</p>
        <div class="brt-criteria-inline">
          <span>wirksam</span><span>wirtschaftlich</span><span>umsetzbar</span><span>nachhaltig</span>
        </div>
        <p class="brt-quote" style="margin-top: var(--space-8);">„Wir suchen nicht die meisten Maßnahmen – sondern die richtigen."</p>
      </div>
    </section>"""
        + f"""
    <section class="brt-section brt-section--alt" aria-labelledby="methoden-title">
      <div class="brt-container brt-fade-up">
        <h2 id="methoden-title" class="brt-h2">Welche Methoden und Prozesse nutzt Beraterium?</h2>
        <p class="brt-body">Unser Risikomanagement-Prozess folgt drei klaren Phasen: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren. Kein Konzern-Framework — sondern ein wiederholbarer Ablauf, den KMU, Startups und Solo in 2–6 Wochen durchlaufen.</p>
        <p class="brt-body">Die Methoden sind bewusst schlank: strukturierte Workshops, Leitfragen statt Excel-Monster, Bewertung durch mehrere Blickwinkel. So entsteht ein Risiko-Lagebild, das Sie umsetzen können — nicht eine Mappe für die Schublade.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="iso-title">
      <div class="brt-container brt-fade-up">
        <h2 id="iso-title" class="brt-h2">ISO 31000 und die Beraterium-Methode</h2>
        <p class="brt-body">ISO 31000 beschreibt den Rahmen für Risikomanagement — Kontext, Identifikation, Analyse, Behandlung. Beraterium ist kein ISO-Zertifizierer, orientiert sich aber an denselben Prinzipien: systematisch sammeln, transparent bewerten, Maßnahmen nach Wirkung priorisieren.</p>
        <p class="brt-body">Der Unterschied: Wir übersetzen den Standard in Euro, Zeiträume und konkrete Schritte für Unternehmen ohne eigenes Risk-Office — verständlich, praxisnah, ohne Bürokratie.</p>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="matrix-title">
      <div class="brt-container brt-fade-up">
        <h2 id="matrix-title" class="brt-h2">Risiken und Chancen in der Matrix</h2>
        <p class="brt-body">Klassische Risiko-Chancen-Matrizen sortieren nach Wahrscheinlichkeit und Auswirkung — oft als Ampel. Beraterium ersetzt die Farben durch Euro: Schadenshöhe × Eintrittswahrscheinlichkeit, abzüglich vorhandener Maßnahmen. So sehen Sie sofort, welche drei Risiken wirklich teuer werden.</p>
        <p class="brt-body">Chancen behandeln wir nicht als Gegenpol, sondern als Maßnahmen mit positivem Effekt — etwa Diversifikation, die ein Klumpenrisiko senkt. Die Priorisierung bleibt dieselbe: größter Hebel zuerst.</p>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="angebote-link-title">
      <div class="brt-container brt-fade-up">
        <h2 id="angebote-link-title" class="brt-h2">Passende Angebote nach Zielgruppe</h2>
        <p class="brt-body">Die Methode ist überall dieselbe — der Umfang passt sich Ihrer Situation an:</p>
        <ul class="brt-list-check">
          <li><a href="{pre}angebote/kmu/">Risikomanagement Mittelstand →</a> — 6-Wochen-Fahrplan für KMU</li>
          <li><a href="{pre}angebote/startups/">Risikomanagement für Startups →</a> — 4-Wochen-Check, investor-ready</li>
          <li><a href="{pre}angebote/solo/">Risikomanagement für Selbstständige →</a> — 2-Wochen-Kompass mit KI-Impulsgeber</li>
        </ul>
      </div>
    </section>"""
        + faq_section_html(faq, title="Häufige Fragen zur Methode", section_id="faq", alt=True)
        + cta_band(pre, "Machen Sie Ihre Risiken sichtbar", "Im kostenlosen Erstgespräch zeigen wir Ihnen, wie die Methode konkret für Ihr Unternehmen aussieht.", "Kostenloses Erstgespräch buchen")
    )
    write(
        "methode/index.html",
        shell(depth=1, title=methode_title, description=methode_desc,
              canonical="/methode/", active_nav="methode", main=main, json_ld=methode_ld),
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
    title = "Nutzen-Garantie: Kein Nutzen, kein Geld | Beraterium"
    desc = "Unsere Nutzen-Garantie: Drei vorab vereinbarte Kriterien entscheiden. Erfüllen wir auch nur eines nicht, erhalten Sie 100 % zurück."
    json_ld = page_schema(
        faq_page_schema(faq),
        speakable_webpage_schema("/nutzen-garantie/"),
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
        {split_media_html(IMG_NUTZEN_KRITERIEN, "Berater und Unternehmer legen im Kick-off die drei Erfolgskriterien der Nutzen-Garantie fest", 1, contain=True)}
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
            "Lassen Sie uns gemeinsam Ihre Kriterien festlegen",
            "Im kostenlosen Erstgespräch besprechen wir, woran Sie den Erfolg unserer Zusammenarbeit erkennen.",
            "Jetzt Termin vereinbaren →",
        )
        + faq_section_html(faq, title="Häufige Fragen zur Nutzen-Garantie", section_id="faq", alt=True)
    )
    write(
        "nutzen-garantie/index.html",
        shell(depth=1, title=title, description=desc,
              canonical="/nutzen-garantie/", active_nav=None, main=main, json_ld=json_ld),
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
          <h2 id="bedeutet-title" class="brt-h2">Was „relevant“ bedeutet</h2>
          <p class="brt-body">Ein Risiko ist relevant, wenn sein möglicher Schaden die im Kick-off gemeinsam festgelegte Schwelle erreicht oder überschreitet, zum Beispiel ein Schadenspotenzial von mehr als 10.000 Euro.</p>
          <p class="brt-body">Diese Schwelle legen wir individuell mit Ihnen fest, nicht pauschal für alle Unternehmen gleich. Finden wir im Ergebnis der vereinbarten Analyse kein einziges Risiko, das diese Schwelle erfüllt, erstatten wir Ihnen den vollen vereinbarten Projektpreis zurück.</p>
        </div>
        {split_media_html(IMG_RELEVANZ_SCHWELLE, "Berater und Unternehmer legen im Kick-off die Schadensschwelle für relevante Risiken fest", 1, contain=True)}
      </div>
    </section>"""
        + guarantee_rule_band(
            "„Wir finden kein relevantes Risiko? Geld zurück.“",
            aria="Kernaussage Relevanz-Garantie",
        )
        + guarantee_contrast_duo(
            left_tag="KEIN KLEINKLEIN",
            left_title="Was wir nicht tun",
            left_id="nicht",
            left_paras=[
                "Es geht uns nicht darum, irgendein x-beliebiges, unrelevantes Risiko zu finden, nur damit unsere Arbeit bezahlt wird. Kleinigkeiten unterhalb der vereinbarten Schwelle z\u00e4hlen nicht als relevantes Risiko im Sinne dieser Garantie.",
                "Das ist uns wichtig, damit Sie die Sorge verlieren, wir w\u00fcrden nur suchen, um etwas abzurechnen.",
            ],
            left_note_label="Ergebnis",
            left_note="Finden wir nichts Relevantes, kostet Sie die gesamte Analyse nichts.",
            right_tag="BLINDE FLECKEN",
            right_title="Was wir gezielt suchen",
            right_id="suchen",
            right_paras=[
                "Im Fokus stehen Risiken, die vorher nicht in Ihrem Blick waren oder die intern bereits als nicht relevant abgestempelt wurden, sich am Ende aber doch als sehr relevant herausstellen.",
            ],
            right_note_label="Beispiel",
            right_note="Ein Risiko, das intern als \u201eschon lange bekannt und unter Kontrolle\u201c galt, entpuppt sich in der Bewertung als Risiko mit einem Schadenpotenzial deutlich \u00fcber der vereinbarten Schwelle.",
            section_id="nicht",
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
            "Finden Sie heraus, welche Risiken Sie übersehen",
            "Im kostenlosen Erstgespräch erfahren Sie, wie wir die Schadensschwelle gemeinsam mit Ihnen festlegen.",
            "Jetzt Termin vereinbaren →",
        )
        + faq_section_html(faq, title="Häufige Fragen zur Relevanz-Garantie", section_id="faq", alt=True)
    )
    write(
        "relevanz-garantie/index.html",
        shell(depth=1, title=title, description=desc,
              canonical="/relevanz-garantie/", active_nav=None, main=main, json_ld=json_ld),
    )




def gen_angebote() -> None:
    pre = "../"
    angebote_faq = [
        ("Welches Angebot passt zu mir – Startup, KMU oder Solo?", "Startups (4 Wochen) für Gründerteams, KMU (6 Wochen) für vollständiges Lagebild ab ca. 10 Mitarbeitenden, Solo (2 Wochen) für Einzelunternehmer. Im Erstgespräch klären wir, was passt."),
        ("Was ist der Unterschied zwischen Risikobewertung und Risikomanagement-Beratung?", "Risikobewertung bewertet Schadenshöhe und Eintrittswahrscheinlichkeit in Euro — die Grundlage für Prioritäten. Risikomanagement-Beratung umfasst Analyse, Maßnahmen und Umsetzung mit unserem 3-Ebenen-Gefahrenkatalog. Details zur Methode finden Sie auf der Methode-Seite."),
        ("Was kostet Risikomanagement-Beratung bei Beraterium?", "Das Kernpaket Risiko-Analyse 360° kostet 3.475 € (Bundle aus Analyse, Strategie und Budgetplanung). Einzelmodule: Analyse 1.725 €, Strategie-Sitzung 2.175 €, Budgetplanung 1.250 €. Workshops ab 57 € pro Person, der Erst-Check für Startups ist kostenlos. Alle Preise transparent auf der Preisseite."),
        ("Gibt es eine Garantie?", "Ja: Doppelte Garantie — Relevanz und Nutzen. Kein relevantes Risiko gefunden oder kein Mehrwert? Geld zurück."),
        ("Brauche ich ISO-Zertifizierung oder Konzern-Methodik?", "Nein. Beraterium übersetzt Konzern-Methodik in praxisnahe Schritte für KMU, Startups und Solo — ohne Bürokratie-Overhead."),
    ]
    main = (
        hero(pre, "UNSERE ANGEBOTE", "Risikomanagement-Beratung: Der passende Check für Ihre Situation",
             "Ob Gründerteam, Mittelständler oder Solo-Selbstständige: strukturierte Risikobewertung in Euro und Risikomanagement-Beratung mit Konzern-Methodik — übersetzt auf Ihre Realität, mit doppelter Garantie.",
             compact=True,
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a>')
        + """
    <section class="brt-section" aria-labelledby="paths-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">FÜR WEN</p>
          <h2 id="paths-title" class="brt-h2">Wählen Sie Ihren Einstieg</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-card--target brt-hover-lift">
            <h3 class="brt-h3">Startups</h3>
            <p class="brt-meta brt-meta--accent">Der 4-Wochen Risiko-Check</p>
            <p class="brt-body">Für Gründerteams bis 10 Mitarbeitende. Sie erkennen früh, welche Risiken Ihr Wachstum bremsen könnten – bevor sie teuer werden.</p>
            <a class="brt-btn brt-btn--ghost" href="../angebote/startups/">Zum Startup-Angebot →</a>
          </li>
          <li class="brt-card brt-card--target brt-card--featured brt-hover-lift">
            <h3 class="brt-h3">KMU &amp; Mittelstand</h3>
            <p class="brt-meta brt-meta--accent">Der 6-Wochen Klarheits-Fahrplan</p>
            <p class="brt-body">Für Unternehmen mit 10–100+ Mitarbeitenden. Vollständiges Risiko-Lagebild, priorisiert und in Euro bewertet – plus HR-Analyse für Kultur und Führung.</p>
            <a class="brt-btn brt-btn--ghost" href="../angebote/kmu/">Zum KMU-Angebot →</a>
          </li>
          <li class="brt-card brt-card--target brt-hover-lift">
            <h3 class="brt-h3">Solo-Selbstständige</h3>
            <p class="brt-meta brt-meta--accent">Der 2-Wochen Risiko-Kompass</p>
            <p class="brt-body">Für Freiberufler und Einzelunternehmer. In zwei Wochen wissen Sie, wo Sie wirklich verletzlich sind – moderiert, mit KI-Impulsgeber.</p>
            <a class="brt-btn brt-btn--ghost" href="../angebote/solo/">Zum Solo-Angebot →</a>
          </li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="compare-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">AUF EINEN BLICK</p>
          <h2 id="compare-title" class="brt-h2">Was passt zu Ihnen?</h2>
          <p class="brt-body">Drei Zielgruppen, eine Methode — unterschiedlicher Umfang und Tempo.</p>
        </header>
        <div class="brt-compare brt-fade-up">
          <div class="brt-compare__scroll">
            <table class="brt-compare__table">
              <caption class="brt-sr-only">Vergleich der Risiko-Checks für Startups, KMU und Solo-Selbstständige</caption>
              <thead>
                <tr>
                  <th class="brt-compare__corner" scope="col"></th>
                  <th class="brt-compare__head" scope="col"><span class="brt-compare__head-icon" aria-hidden="true"><svg class="brt-compare__svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg></span><span class="brt-compare__head-title">Startups</span><span class="brt-compare__head-meta">4-Wochen-Check</span></th>
                  <th class="brt-compare__head" scope="col"><span class="brt-compare__head-icon" aria-hidden="true"><svg class="brt-compare__svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg></span><span class="brt-compare__head-title">KMU</span><span class="brt-compare__head-meta">6-Wochen-Fahrplan</span></th>
                  <th class="brt-compare__head" scope="col"><span class="brt-compare__head-icon" aria-hidden="true"><svg class="brt-compare__svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span><span class="brt-compare__head-title">Solo</span><span class="brt-compare__head-meta">2-Wochen-Kompass</span></th>
                </tr>
              </thead>
              <tbody>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span><span class="brt-compare__row-text">Für wen</span></span></th><td>Gründerteams bis 10 MA</td><td>10–100+ MA</td><td>Einzelunternehmer</td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></span><span class="brt-compare__row-text">Dauer</span></span></th><td><strong>ca. 4</strong> Wochen</td><td><strong>ca. 6</strong> Wochen</td><td><strong>ca. 2</strong> Wochen</td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg></span><span class="brt-compare__row-text">Sessions</span></span></th><td>1–2 <span class="brt-compare__muted">(je 2h)</span></td><td>2–3 <span class="brt-compare__muted">(je 2–3h)</span></td><td>1 <span class="brt-compare__muted">(2–3h)</span></td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></span><span class="brt-compare__row-text">Ergebnis</span></span></th><td>priorisiertes Risiko-Lagebild</td><td>vollständiges Risiko-Portfolio + Fahrplan</td><td>persönliches Risiko-Lagebild</td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.65-8.58 3.91a2 2 0 0 1-1.66 0L3.18 12.65"/><path d="m22 17.65-8.58 3.91a2 2 0 0 1-1.66 0L3.18 17.65"/></svg></span><span class="brt-compare__row-text">Schritte</span></span></th><td><span class="brt-compare__pill">1 / 2 / 3</span></td><td><span class="brt-compare__pill">1 / 2 / 3</span></td><td><span class="brt-compare__pill">1 / 2 / 3</span></td></tr>
                <tr><th class="brt-compare__row-label" scope="row"><span class="brt-compare__row-label-inner"><span class="brt-compare__row-icon" aria-hidden="true"><svg class="brt-compare__svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg></span><span class="brt-compare__row-text">Garantie</span></span></th><td><span class="brt-compare__check">Doppelt</span></td><td><span class="brt-compare__check">Doppelt</span></td><td><span class="brt-compare__check">Doppelt</span></td></tr>
              </tbody>
              <tfoot>
                <tr>
                  <td class="brt-compare__corner"></td>
                  <td><a class="brt-btn brt-btn--ghost" href="../angebote/startups/">Zum Angebot →</a></td>
                  <td><a class="brt-btn brt-btn--ghost" href="../angebote/kmu/">Zum Angebot →</a></td>
                  <td><a class="brt-btn brt-btn--ghost" href="../angebote/solo/">Zum Angebot →</a></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </section>"""
        + steps_flow_section()
        + """
    <section class="brt-section brt-section--alt" aria-labelledby="hr-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">ERGÄNZEND</p>
          <h2 id="hr-title" class="brt-h2">HR, Kultur &amp; Führung</h2>
          <p class="brt-body">Risiken stecken oft im Team. Mit unseren HR-Modulen machen Sie Stimmung, Führungsqualität und Kultur sichtbar – datenbasiert statt aus dem Bauch.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">HR-Analyse per Fragebogen</h3><p class="brt-body">Anonymer Kultur-Health-Check: Zufriedenheit, Kommunikation, Führung, Belastung.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Führungskräfte-Interviews</h3><p class="brt-body">Tiefe 1:1-Gespräche mit Ihren Führungskräften, transkribiert und in Mustern ausgewertet.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Auswertung &amp; Handlungsempfehlungen</h3><p class="brt-body">Aus den Daten werden konkrete Maßnahmen mit Prioritäten, Reihenfolge und Timeline.</p></li>
        </ul>
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Preise und Umfang je nach Teamgröße – alle Preise transparent auf der <a href="../preise/">Preisseite</a>.</p>
      </div>
    </section>"""
        + case_studies_section(pre)
        + guarantee(pre)
        + faq_section_html(angebote_faq, title="Häufige Fragen zu unseren Angeboten", section_id="faq", alt=True)
        + cta_band(pre, "Unsicher, was zu Ihnen passt?", "Das klären wir im kostenlosen Erstgespräch – inklusive einer DIY-Anleitung, die Sie auch ohne uns nutzen können.")
    )
    angebote_title = "Risikomanagement-Beratung KMU, Startups & Solo | Beraterium"
    angebote_desc = "Risikomanagement-Beratung für KMU, Startups und Solo: 2–6 Wochen zum klaren Risiko-Lagebild in Euro — mit doppelter Garantie."
    write("angebote/index.html", shell(depth=1, title=angebote_title, description=angebote_desc,
          canonical="/angebote/", active_nav="angebote", main=main,
          json_ld=page_schema(faq_page_schema(angebote_faq))))



def _offer_details_block(o: dict) -> str:
    """Ausklappbarer Detail-Teaser; verlinkt auf Schulungs- oder Internationale-Angebote-Seite."""
    if not o.get("details_html"):
        return ""
    link = ""
    if o.get("slug"):
        if o["nr"].startswith("INT-"):
            if o.get("sub") and o.get("parent_slug"):
                path = f'../internationale-angebote/{o["parent_slug"]}/#{o["nr"].lower()}'
            elif o["nr"] == "INT-00":
                path = "../internationale-angebote/"
            else:
                path = f'../internationale-angebote/{o["slug"]}/'
            link = f'<p class="brt-meta"><a href="{path}">Zur Angebotsseite mit allen Details \u2192</a></p>'
        elif o["nr"].startswith("SCH-"):
            link = f'<p class="brt-meta"><a href="../schulungen/{o["slug"]}/">Zur Schulungsseite mit allen Details \u2192</a></p>'
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
        f'              <tr id="{o["nr"].lower()}"{" class=\"brt-table__subrow\"" if o.get("sub") else ""}>'
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


def gen_preise() -> None:
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
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a>')
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
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Doppelte Garantie</h3><p class="brt-body">Analysepakete sind durch Relevanz- und Nutzen-Garantie abgesichert: kein relevantes Risiko oder kein vereinbarter Nutzen — volle Erstattung. Details auf den <a href="{pre}nutzen-garantie/">Garantie-Seiten</a>.</p></li>
        </ul>
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Welches Paket zu Ihrer Situation passt, klären wir im <a href="{pre}kontakt/">kostenlosen Erstgespräch</a> — Übersicht nach Zielgruppe: <a href="{pre}angebote/">Angebote für Startups, KMU &amp; Solo</a>.</p>
      </div>
    </section>"""
        + guarantee(pre)
        + faq_section_html(preise_faq, title="Häufige Fragen zu Preisen", section_id="faq", alt=True)
        + cta_band(pre, "Unsicher, welches Paket passt?", "Im kostenlosen Erstgespräch klären wir Umfang, Förderung und den besten Einstieg für Ihre Situation.")
    )
    preise_title = "Preise – Risikomanagement-Beratung | Beraterium"
    preise_desc = "Preise transparent: Risiko-Analyse 360° 3.475 € (Festpreis), Workshops ab 57 €/Person, Schulungen ab 3.475 €. Marktvergleich: unter Konzernberatern, mit doppelter Garantie."
    write("preise/index.html", shell(depth=1, title=preise_title, description=preise_desc,
          canonical="/preise/", active_nav="preise", main=main,
          json_ld=page_schema(
              offer_catalog_schema(
                  name="Preise & Leistungen — Risikomanagement-Beratung",
                  description=preise_desc,
                  url="/preise/",
                  categories=PRICE_CATEGORIES,
              ),
              faq_page_schema(preise_faq),
              speakable_webpage_schema(
                  "/preise/",
                  selectors=[".brt-highlight-box", ".brt-faq__answer", "#preisvergleich .brt-body"],
              ),
              json.dumps(
                  {
                      "@context": "https://schema.org",
                      "@type": "BreadcrumbList",
                      "itemListElement": [
                          {"@type": "ListItem", "position": 1, "name": "Start", "item": f"{DE_SITE_URL}/"},
                          {"@type": "ListItem", "position": 2, "name": "Preise & Leistungen", "item": f"{DE_SITE_URL}/preise/"},
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


_INT_PRICING: dict[str, dict] = {
    o["nr"]: o
    for cat in PRICE_CATEGORIES
    for o in cat["offers"]
    if o["nr"].startswith("INT-")
}


def _international_offer_main(cfg: dict, *, locale: str, pre: str) -> str:
    offer = _INT_PRICING[cfg["nr"]]
    team_title = {"de": "Ihr deutsch-russisches Beratungsteam", "ru": "Ваша команда", "en": "Your German-Russian advisory team"}[locale]
    cta_btn = {"de": "Erstgespräch buchen", "ru": "Записаться", "en": "Book intro call"}[locale]
    legal = {"de": LEGAL_NOTICE_DE, "ru": LEGAL_NOTICE_RU, "en": LEGAL_NOTICE_EN}[locale]
    contact_href = f"{pre}{'kontakt' if locale != 'en' else 'contact'}/"
    nr = cfg["nr"]
    is_project = int_is_project_offer(nr)
    has_stages = nr in INT_STAGES and not is_project
    if is_project:
        middle = international_project_section(
            parent_nr=nr, locale=locale, contact_href=contact_href
        ) + international_process_section(cfg["steps"], locale=locale)
        price_block = international_project_price_banner(
            parent_nr=nr, locale=locale, pre=pre, contact_href=contact_href
        )
    elif has_stages:
        middle = (
            international_stages_section(parent_nr=nr, locale=locale, contact_href=contact_href)
            + international_packages_section(parent_nr=nr, locale=locale, contact_href=contact_href, pre=pre)
            + international_excluded_section(parent_nr=nr, locale=locale)
            + international_process_section(cfg["steps"], locale=locale)
        )
        price_block = international_stages_price_banner(
            offer=offer, parent_nr=nr, locale=locale, pre=pre
        )
    else:
        leistungen = "".join(f"<li>{x}</li>" for x in cfg["leistungen"])
        middle = f"""
    <section class="brt-section brt-section--alt" id="leistungen"><div class="brt-container">
      <ul class="brt-list-check brt-fade-up">{leistungen}</ul>
    </div></section>"""
        middle += international_process_section(cfg["steps"], locale=locale)
        price_block = international_price_section(offer, pre=pre, locale=locale)

    return (
        hero(
            pre, cfg["tag"], cfg["h1"], cfg["lead"],
            actions=f'<a class="brt-btn" href="{contact_href}">{cta_btn}</a>',
        )
        + international_audience_section(
            intro=cfg["fuer_wen_intro"],
            items=cfg["fuer_wen"],
            locale=locale,
            depth=len(pre) // 3 if pre else 0,
            offer_nr=nr,
            lead=cfg.get("fuer_wen_lead", ""),
        )
        + middle
        + international_outcome_section(items=cfg["ergebnis"], locale=locale)
        + international_team_section(
            pre=pre,
            team_slugs=cfg["team_slugs"],
            title=team_title,
            locale=locale,
            member_intros=int_team_member_intros(locale),
        )
        + price_block
        + international_legal_section(legal)
        + faq_section(cfg["faq"], title=int_faq_title(locale))
        + cta_band(pre, cfg["cta_h2"], cfg["cta_body"], cta_btn)
    )


def _international_stage_main(
    stage: dict,
    *,
    parent_cfg: dict | None,
    locale: str,
    pre: str,
) -> str:
    def _t(m, loc: str) -> str:
        if isinstance(m, str):
            return m
        return m.get(loc, m.get("de", ""))

    contact_href = f"{pre}{'kontakt' if locale != 'en' else 'contact'}/"
    cta_btn = {"de": "Erstgespräch buchen", "ru": "Записаться", "en": "Book intro call"}[locale]
    legal = {"de": LEGAL_NOTICE_DE, "ru": LEGAL_NOTICE_RU, "en": LEGAL_NOTICE_EN}[locale]
    team_title = {"de": "Ihr deutsch-russisches Beratungsteam", "ru": "Ваша команда", "en": "Your German-Russian advisory team"}[locale]
    index_href = {
        "de": f"{pre}internationale-angebote/",
        "en": f"{pre}international-services/",
        "ru": f"{pre}ru/internationale-angebote/",
    }[locale]
    if parent_cfg:
        tag = parent_cfg.get("tag", "")
        team_slugs = parent_cfg["team_slugs"]
        cta_h2 = parent_cfg.get("cta_h2", "")
        cta_body = parent_cfg.get("cta_body", "")
        pslug = parent_slug(stage["nr"], locale)
        base = {"de": "internationale-angebote", "en": "international-services", "ru": "ru/internationale-angebote"}[locale]
        parent_href = f"{pre}{base}/{pslug}/"
        back_l = {"de": "Zur Rubrik", "en": "Back to offer", "ru": "К разделу"}[locale]
        breadcrumb = f'<p class="brt-meta brt-fade-up"><a href="{parent_href}">{back_l}</a></p>'
        offer_nr = parent_cfg["nr"]
    else:
        tag = _t(stage.get("tag", ""), locale)
        team_slugs = stage.get("team_slugs", ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"])
        cta_h2 = {"de": "Passende Stufe finden?", "en": "Find the right stage?", "ru": "Найти подходящий этап?"}[locale]
        cta_body = {"de": "Erstberatung buchen — 50 €, 30 Min.", "en": "Book intro call — €50, 30 min.", "ru": "Консультация 50 €, 30 мин."}[locale]
        index_l = {"de": "Internationale Angebote", "en": "International services", "ru": "Международные услуги"}[locale]
        breadcrumb = f'<p class="brt-meta brt-fade-up"><a href="{index_href}">{index_l}</a></p>'
        offer_nr = "INT-00"
    return (
        breadcrumb
        + hero(
            pre,
            tag,
            _t(stage["name"], locale),
            _t(stage.get("teaser", ""), locale),
            actions=f'<a class="brt-btn" href="{contact_href}">{cta_btn}</a>',
        )
        + international_audience_section(
            intro=stage["fuer_wen_intro"],
            items=stage["fuer_wen"],
            locale=locale,
            depth=len(pre) // 3 if pre else 0,
            offer_nr=offer_nr,
            lead=stage.get("fuer_wen_lead", ""),
        )
        + international_stage_scope_section(
            leistungen=stage["leistungen"],
            excluded=stage.get("excluded", []),
            locale=locale,
        )
        + international_process_section(stage["steps"], locale=locale)
        + international_outcome_section(items=stage["ergebnis"], locale=locale)
        + international_next_stages_section(stage=stage, locale=locale, pre=pre)
        + international_team_section(
            pre=pre,
            team_slugs=team_slugs,
            title=team_title,
            locale=locale,
            section_alt=True,
            member_intros=int_team_member_intros(locale),
        )
        + international_single_stage_price_banner(
            stage=stage, locale=locale, pre=pre, contact_href=contact_href
        )
        + international_legal_section(legal)
        + faq_section(stage["faq"], title=int_faq_title(locale))
        + cta_band(pre, cta_h2, cta_body, cta_btn)
    )


def gen_international_stage(stage: dict, *, parent_cfg: dict | None, locale: str = "de") -> None:
    stage_nr = stage["nr"]
    pslug = parent_slug(stage_nr, locale) if parent_cfg else stage_slug(stage_nr, locale)
    sslug = stage_slug(stage_nr, locale)
    canonical, depth, pre = locale_paths(
        locale,
        pslug if parent_cfg else sslug,
        stage_slug_key=sslug if parent_cfg else None,
    )
    stage = apply_stage_locale(stage, locale)
    main = _international_stage_main(stage, parent_cfg=parent_cfg, locale=locale, pre=pre)
    name = stage["name"].get(locale, stage["name"].get("de", "")) if isinstance(stage["name"], dict) else stage["name"]
    teaser = stage.get("teaser", {})
    desc = teaser.get(locale, teaser.get("de", "")) if isinstance(teaser, dict) else str(teaser)
    title = f"{name} | Beraterium"
    audience = parent_cfg["audience"] if parent_cfg else "Internationale Gründer und Unternehmer"
    ld = page_schema(
        service_schema(name=name, description=desc, url=canonical, audience=audience),
        faq_page_schema(stage["faq"]),
        speakable_webpage_schema(canonical),
    )
    rel = stage_rel_path(stage_nr, locale)
    active_nav = "international-services" if locale == "en" else "internationale-angebote"
    write(
        rel,
        shell(
            depth=depth,
            title=title,
            description=desc,
            canonical=canonical,
            active_nav=active_nav,
            main=main,
            json_ld=ld,
            html_lang={"de": "de", "ru": "ru", "en": "en"}[locale],
            current_locale=locale,
        ),
    )


def gen_all_international_stages(*, locale: str) -> None:
    parent_by_nr = {c["nr"]: c for c in INT_OFFER_CONFIGS_DE}
    if locale == "en":
        parent_by_nr = {c["nr"]: c for c in en_offer_configs()}
    elif locale == "ru":
        parent_by_nr = {c["nr"]: c for c in ru_offer_configs()}
    for parent_nr, stage in iter_stage_pages():
        if parent_nr and int_is_project_offer(parent_nr):
            continue
        parent_cfg = parent_by_nr.get(parent_nr) if parent_nr else None
        gen_international_stage(stage, parent_cfg=parent_cfg, locale=locale)


def gen_international_offer(cfg: dict, *, locale: str = "de") -> None:
    slug = cfg["slug"]
    canonical, depth, pre = locale_paths(locale, slug)
    main = _international_offer_main(cfg, locale=locale, pre=pre)
    ld = page_schema(
        service_schema(name=cfg["h1"], description=cfg["description"], url=canonical, audience=cfg["audience"]),
        faq_page_schema(cfg["faq"]),
        speakable_webpage_schema(canonical),
    )
    rel = {
        "ru": f"ru/internationale-angebote/{slug}/index.html",
        "en": f"international-services/{slug}/index.html",
    }.get(locale, f"internationale-angebote/{slug}/index.html")
    write(
        rel,
        shell(
            depth=depth,
            title=cfg["title"],
            description=cfg["description"],
            canonical=canonical,
            active_nav="international-services" if locale == "en" else "internationale-angebote",
            main=main,
            json_ld=ld,
            html_lang={"de": "de", "ru": "ru", "en": "en"}[locale],
            current_locale=locale,
        ),
    )


def gen_international_index(*, locale: str = "de") -> None:
    index_cfg = {"ru": INT_INDEX_RU, "en": INT_INDEX_EN}.get(locale, INT_INDEX_DE)
    configs = {"ru": ru_offer_configs(), "en": en_offer_configs()}.get(locale, INT_OFFER_CONFIGS_DE)
    canonical, depth, pre = locale_paths(locale, "", is_index=True)
    cards = []
    for cfg in configs:
        offer = _INT_PRICING[cfg["nr"]]
        cards.append(
            f'<li class="brt-card brt-card--catalog brt-hover-lift"><a class="brt-card__link" href="{cfg["slug"]}/">'
            f'<h3 class="brt-h3">{cfg["h1"]}</h3>'
            f'<p class="brt-body">{cfg.get("card_teaser", offer["desc"])}</p>'
            f'<p class="brt-meta">{offer_price_text(offer)}</p></a></li>'
        )
    why = "".join(
        f'<li class="brt-card brt-hover-lift"><h3 class="brt-h3">{t}</h3><p class="brt-body">{b}</p></li>'
        for t, b in index_cfg["why_cards"]
    )
    cta_btn = {"de": "Erstgespräch buchen", "ru": "Записаться", "en": "Book intro call"}[locale]
    contact_href = f"{pre}{'kontakt' if locale != 'en' else 'contact'}/"
    slider_i18n = {
        "de": ("Internationale Angebote", "Vorheriges Angebot", "Nächstes Angebot"),
        "en": ("International services", "Previous offer", "Next offer"),
        "ru": ("Международные услуги", "Предыдущее предложение", "Следующее предложение"),
    }[locale]
    offers_slider = cards_slider_block(
        "".join(cards),
        aria_label=slider_i18n[0],
        prev_label=slider_i18n[1],
        next_label=slider_i18n[2],
    )
    why_slider_i18n = {
        "de": ("Warum Beraterium", "Vorheriger Punkt", "Nächster Punkt"),
        "en": ("Why Beraterium", "Previous point", "Next point"),
        "ru": ("Почему Beraterium", "Предыдущий пункт", "Следующий пункт"),
    }[locale]
    why_slider = cards_slider_block(
        why,
        aria_label=why_slider_i18n[0],
        prev_label=why_slider_i18n[1],
        next_label=why_slider_i18n[2],
        autoplay_ms=0,
    )
    team_block = international_team_section(
        pre=pre,
        team_slugs=index_cfg.get("team_slugs", ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"]),
        title=index_cfg.get("team_h2", "Ihr deutsch-russisches Beratungsteam"),
        locale=locale,
        intro=index_cfg.get("team_intro", ""),
        tag=index_cfg.get("team_tag", ""),
        member_intros=index_cfg.get("team_member_intros"),
    )
    main = (
        hero(pre, index_cfg["tag"], index_cfg["h1"], index_cfg["lead"], compact=True,
             actions=f'<a class="brt-btn" href="{contact_href}">{cta_btn}</a>')
        + international_journey_section(locale=locale, pre=pre, contact_href=contact_href)
        + f"""
    <section class="brt-section" id="angebote"><div class="brt-container">
      {offers_slider}
    </div></section>
    <section class="brt-section brt-section--alt" id="warum"><div class="brt-container">
      <h2 class="brt-h2">{index_cfg["why_h2"]}</h2>
      <p class="brt-body">{index_cfg["why_intro"]}</p>
      {why_slider}
    </div></section>"""
        + team_block
        + faq_section(index_cfg["faq"], title=int_faq_title(locale))
        + cta_band(pre, index_cfg["cta_h2"], index_cfg["cta_body"], cta_btn)
    )
    ld = page_schema(faq_page_schema(index_cfg["faq"]), speakable_webpage_schema(canonical))
    rel = {
        "ru": "ru/internationale-angebote/index.html",
        "en": "international-services/index.html",
    }.get(locale, "internationale-angebote/index.html")
    write(
        rel,
        shell(
            depth=depth,
            title=index_cfg["title"],
            description=index_cfg["description"],
            canonical=canonical,
            active_nav="internationale-angebote",
            main=main,
            json_ld=ld,
            html_lang={"de": "de", "ru": "ru", "en": "en"}[locale],
            current_locale=locale,
        ),
    )


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
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Alle Preise und Angebote im \u00dcberblick: <a href="{pre}preise/">Preise &amp; Leistungen</a>.</p>
      </div>
    </section>"""


def gen_schulung(cfg: dict) -> None:
    """Datengetriebene Schulungs-Unterseite /schulungen/<slug>/.

    Inhalt aus _schulungen.py (SCHULUNG_CONFIGS), Preis-Staffel aus
    _pricing.py (Join ueber "nr"). Struktur: Hero -> Fuer-wen-Checkliste ->
    Ablauf/Sessions -> Ergebnis -> Preisblock -> FAQ -> CTA.
    """
    slug = cfg["slug"]
    pre = "../../"
    canonical = f"/schulungen/{slug}/"
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
                f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespr\u00e4ch buchen</a>'
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
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DE_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Schulungen", "item": f"{DE_SITE_URL}/schulungen/"},
                {"@type": "ListItem", "position": 3, "name": cfg["h1"], "item": f"{DE_SITE_URL}{canonical}"},
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
        f"schulungen/{slug}/index.html",
        shell(
            depth=2,
            title=cfg["title"],
            description=cfg["description"],
            canonical=canonical,
            active_nav="schulungen",
            main=main,
            json_ld=ld,
        ),
    )


def gen_schulungen_index() -> None:
    """Index-Seite /schulungen/ mit Karten zu allen Schulungen."""
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
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespr\u00e4ch buchen</a>')
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
        <p class="brt-meta brt-fade-up" style="margin-top: var(--space-6); text-align: center;">Alle Staffeln im Detail: <a href="{pre}preise/#schulungen">Preise &amp; Leistungen</a>.</p>
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
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DE_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Schulungen", "item": f"{DE_SITE_URL}/schulungen/"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    schulungen_title = "Schulungen Risikomanagement & F\u00fchrung | Beraterium"
    schulungen_desc = "Sieben Inhouse-Schulungen: Ausbildung zum Risikoexperten ab 9.875 \u20ac, Einzelschulungen Intensivformat ab 3.475 \u20ac, Innovation, Feedback, interkulturelles Management."
    write("schulungen/index.html", shell(depth=1, title=schulungen_title, description=schulungen_desc,
          canonical="/schulungen/", active_nav="schulungen", main=main,
          json_ld=page_schema(faq_page_schema(schulungen_faq), speakable_webpage_schema("/schulungen/", selectors=[".brt-highlight-box", ".brt-faq__answer", "#schulungen-vergleich .brt-body"]), breadcrumb_ld)))


def lp_shell(depth: int, slug: str, title: str, desc: str, du: bool, main: str, *, json_ld: str = "") -> None:
    write(
        f"angebote/{slug}/index.html",
        shell(
            depth=depth,
            title=title,
            description=desc,
            canonical=f"/angebote/{slug}/",
            active_nav=f"angebote/{slug}",
            main=main,
            json_ld=json_ld,
        ),
    )


def gen_lp_startups() -> None:
    pre = "../../"
    startups_faq = [
        ("Wie viel Zeit kostet mich das?", "Pro Session rund 2 Stunden, insgesamt 1–2 Sessions plus Kick-off. Den Rest übernehmen wir."),
        ("Lohnt sich das so früh überhaupt?", "Gerade früh: Ein Key-Person- oder Cash-Risiko kann ein junges Startup komplett stoppen."),
        ("Was, wenn wir nur zu zweit sind?", "Kein Problem. Wir moderieren so, dass auch ein kleines Gründerteam zu einer realistischen Bewertung kommt."),
        ("Bekomme ich etwas Vorzeigbares für Investoren?", "Du bekommst einen priorisierten Risiko-Report als One-Pager. Ehrlich, nicht geschönt."),
        ("Welche Risiken haben Startups, die oft übersehen werden?", "Co-Founder-Konflikte, Klumpenrisiko bei Kunden, Key-Person-Abhängigkeit und Cash-Runway-Unterschätzung — nicht das Produkt allein."),
        ("Wie bereite ich mein Startup auf Due Diligence vor?", "Investoren prüfen auch, ob Gründer ihre Risiken kennen. Ein strukturiertes, priorisiertes Risiko-Portfolio ist ein starkes Signal."),
    ]
    opts = [
        {"title": "Option A — Risiko-Snapshot", "claim": "In 4 Wochen weißt du, wo du dran bist.", "features": [
            "Kick-off (Scope, Nutzen-Kriterien)", "Moderierte Risikoanalyse mit Team (1–2 Sessions, je 2h)",
            "Gefahrenkatalog Startup-Edition (3 Ebenen)", "Bewertung: Schadenshöhe in Euro + Wahrscheinlichkeit",
            "Inventar-Check + Risiko-Report (One-Pager)"]},
        {"title": "Option B — Snapshot + Maßnahmen-Sprint", "claim": "Du weißt, was los ist – und was zu tun ist.", "badge": "Beliebt", "featured": True,
         "extra": "Alles aus A, plus:", "features": [
            "Maßnahmen-Sprint: Top-Risiken → konkrete Maßnahmen", "Bewertung: Wirkung, Aufwand, Umsetzbarkeit je Maßnahme",
            "Quick-Win-Liste für diese Woche", "Fahrplan mit Verantwortlichkeiten & Timeline", "Gründer-Abschluss-Call"]},
        {"title": "Option C — Snapshot + Maßnahmen + Gründer-Sparring", "claim": "Wir begleiten dich, bis die ersten Maßnahmen greifen.",
         "extra": "Alles aus B, plus:", "features": [
            "2 Monate Gründer-Sparring (2× monatlich 30 Min.)", "Zugang zur RisikoRadar-Community",
            "Experten-Vermittlung bei Bedarf", "Risiko-Update nach 2 Monaten"]},
    ]
    main = (
        hero(pre, "RISIKO-CHECK FÜR STARTUPS", "In 4 Wochen weißt du, welche Risiken dein Wachstum bremsen",
             "Für Gründer und Startup-CEOs mit 2–10 Mitarbeitenden. Du baust, du rennst – wir sorgen dafür, dass dich kein blinder Fleck ausbremst.",
             split=True, media_label="Gründerteam beim Risiko-Check mit Beraterium",
             media_src=IMG_ANGEBOT_STARTUPS_HERO,
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a><a class="brt-btn brt-btn--outline" href="#optionen">Die 3 Optionen ansehen →</a>')
        + """
    <section class="brt-section" aria-labelledby="problem-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">KENNST DU DAS?</p>
          <h2 id="problem-title" class="brt-h2">Risiken? „Ja, klar – irgendwann." Aber irgendwann ist meistens zu spät.</h2>
          <p class="brt-body">Du hast tausend Dinge gleichzeitig im Kopf: Produkt, Kunden, Hiring, Cash. Risikoanalyse klingt nach Konzern, nach Excel-Monster, nach Bürokratie – also schiebst du es.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Das externe Problem</h3><p class="brt-body">Du hast kein strukturiertes Bild deiner Risiken. Was dich morgen 30.000 € kosten könnte, weißt du heute nicht.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Das interne Problem</h3><p class="brt-body">Tief drinnen weißt du: Es gibt Dinge, die du übersiehst. Key-Person-Risk, Cashflow-Lücken, rechtliche Stolperfallen, technische Schulden.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Die Überzeugung</h3><p class="brt-body">Ein Gründer, der Verantwortung für sein Team trägt, sollte nicht raten, wo die größten Gefahren liegen. Er sollte es wissen.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="erstgespraech-title">
      <div class="brt-container brt-fade-up">
        <p class="brt-tag">ERST GEBEN, DANN ANBIETEN</p>
        <h2 id="erstgespraech-title" class="brt-h2">Dein kostenloses Erstgespräch: die Methode zum Selbermachen</h2>
        <p class="brt-body">Im Erstgespräch (ca. 30–45 Min.) zeigen wir dir, wie du selbst eine Risikoanalyse für dein Startup machst. Kein Verkaufsgespräch – echtes Wissen:</p>
        <ul class="brt-list-check">
          <li>Die 3-Ebenen-Methode: Gefahren sammeln → Risiken bewerten → Maßnahmen priorisieren</li>
          <li>Bewertungslogik für Startups: Schadenshöhe schätzen, auch ohne Historie</li>
          <li>Die 5 typischen Startup-Gefahrenfelder: Key Person, Cash, Legal, Tech Debt, Markt</li>
          <li>Konkrete Leitfragen, mit denen du dein Co-Founder-Team einbindest</li>
        </ul>
        <p class="brt-meta brt-meta--italic" style="margin-top: var(--space-6);">Was du nicht bekommst: unseren vollständigen Gefahrenkatalog und die moderierte Durchführung mit Auswertung.</p>
      </div>
    </section>"""
        + pricing_cards(pre, opts, du=True, price_note=f'Der Einstieg ist kostenlos: 1-Stunden-Risiko-Check für Startups (0 €). Alle Preise findest du transparent auf der <a href="{pre}preise/">Preisseite</a>.')
        + guarantee(pre, du=True, tag="Dein Risiko liegt bei uns")
        + faq_section(startups_faq, alt=True)
        + f"""
    <section class="brt-section" aria-label="Ratgeber-Empfehlung">
      <div class="brt-container brt-fade-up">
        <p class="brt-body">Gründerwissen, Investorenvertrauen, Burnout-Gefahr: Warum Key-Person-Risk Startups besonders hart trifft, liest du im Ratgeber <a href="{pre}blog/schluesselpersonrisiko-erkennen-absichern/">Schlüsselpersonrisiko erkennen, bewerten und absichern &rarr;</a></p>
      </div>
    </section>"""
        + cta_band(pre, "Bereit, deine größten Risiken zu kennen?",
                   "Erstgespräch buchen – gratis, kein Sales-Pitch. Du gehst mit einer DIY-Anleitung raus, egal wie du dich entscheidest.",
                   "Kostenloses Erstgespräch buchen")
    )
    startups_title = "Risikomanagement für Startups – 4-Wochen-Check | Beraterium"
    startups_desc = "Risikomanagement für Startups: Key-Person, Cash, Legal, Tech — in 4 Wochen kennst du deine größten Risiken. Investor-ready, in Euro bewertet."
    startups_ld = page_schema(
        service_schema(name="4-Wochen Risiko-Check für Startups", description=startups_desc, url="/angebote/startups/", audience="Startups und Gründerteams"),
        faq_page_schema(startups_faq),
    )
    lp_shell(2, "startups", startups_title, startups_desc, True, main, json_ld=startups_ld)


def gen_lp_kmu() -> None:
    pre = "../../"
    kmu_faq = [
        ("Wie viel Zeit bindet das im Team?", "Pro Session 2–3 Stunden, insgesamt 2–3 Sessions plus Kick-off. Wir moderieren effizient."),
        ("Ist das auch für Familienunternehmen geeignet?", "Besonders. Themen wie Generationenwechsel oder Schlüsselpersonen werden strukturiert sichtbar."),
        ("Was unterscheidet Sie von einer Wirtschaftsprüfung?", "Wir prüfen nicht Zahlen der Vergangenheit, sondern machen Ihre Zukunftsrisiken greifbar."),
        ("Bekommen wir ein vorzeigbares Dokument?", "Ja, ein Risiko-Portfolio-Report, den Sie Beirat, Bank oder Team vorlegen können."),
        ("Was ist das Schlüsselpersonrisiko und wie schützt mein KMU sich dagegen?", "Der wirtschaftliche Schaden, wenn eine unverzichtbare Person ausfällt. Beraterium erfasst das systematisch und entwickelt Maßnahmen zur Wissensverteilung."),
        ("Wie unterscheidet sich Risikomanagement für KMU von Konzern-Methodik?", "KMU brauchen ein klares Lagebild — welche 3–5 Risiken wirklich teuer werden — nicht ISO-Bürokratie. In 6 Wochen, mit Ihrem Team."),
        (
            "Welche Dienstleister bieten professionelle Risikoanalysen für mittelständische Unternehmen an?",
            "Vier Typen: Big-4/ISO-Beratung, spezialisierte Mittelstandsberater, Versicherungsmakler und Eigenregie. "
            "Für ein handlungsfähiges Ergebnis ohne Zertifizierungszwang eignet sich ein spezialisierter Berater mit Euro-Bewertung und Umsetzungsbegleitung. "
            "Vergleich der Anbietertypen im Blog-Artikel Risikomanagement-Beratung KMU; das Beraterium-Angebot finden Sie unter /angebote/kmu/.",
        ),
        (
            "Welche Beratungsansätze für Risikomanagement sind für den Mittelstand am effektivsten?",
            "Am effektivsten ist ein pragmatischer Ansatz: vollständiger Gefahrenkatalog, Bewertung in Euro, Priorisierung auf wenige wirksame Maßnahmen — ohne ISO-Bürokratie. "
            "Genau so arbeitet die Beraterium-Methode in rund 6 Wochen mit Ihrem Team.",
        ),
    ]
    opts = [
        {"title": "Option A — Analyse Pur", "claim": "Sie bekommen Klarheit. Wir liefern das Lagebild.", "features": [
            "Kick-off mit Geschäftsführung (Ziele, Scope, Nutzen-Kriterien)", "Moderierte Risikoanalyse mit Team (2–3 Sessions, je 2–3h)",
            "Vollständiger Gefahrenkatalog (3 Ebenen, branchenangepasst)", "Bewertung: Schadenshöhe in Euro + Eintrittswahrscheinlichkeit",
            "Inventar-Erfassung + Risiko-Portfolio-Report (priorisiert)"]},
        {"title": "Option B — Analyse + Fahrplan", "claim": "Klarheit UND einen konkreten Plan.", "badge": "Beliebt", "featured": True,
         "extra": "Alles aus A, plus:", "features": [
            "Maßnahmen-Workshop für die Top-Risiken", "Bewertung je Maßnahme: Wirkung, Wirtschaftlichkeit, Umsetzbarkeit",
            "Umsetzungsfahrplan mit Timeline & Verantwortlichkeiten", "GF-Abschluss-Session"]},
        {"title": "Option C — Analyse + Fahrplan + Umsetzungsbegleitung", "claim": "Wir bleiben dran, bis die Maßnahmen greifen.",
         "extra": "Alles aus B, plus:", "features": [
            "3 Monate Umsetzungsbegleitung (monatliche Check-ins)", "Zugang zur RisikoRadar-Community (geprüfte Experten)",
            "Koordination von Fachexperten bei komplexen Maßnahmen", "Quartals-Review (Risiko-Update + Fortschritt)"]},
    ]
    main = (
        hero(pre, "RISIKOANALYSE FÜR KMU", "Risikomanagement für den Mittelstand — welche Risiken kosten Sie wirklich Geld?",
             "Für Geschäftsführer und Inhaber von KMU mit 10 bis über 100 Mitarbeitenden. In rund 6 Wochen bekommen Sie ein vollständiges, in Euro bewertetes Risiko-Lagebild – plus konkreten Fahrplan.",
             split=True, media_label="Geschäftsführung eines Mittelständlers bei der Risikoanalyse",
             media_src=IMG_ANGEBOT_KMU_HERO,
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a><a class="brt-btn brt-btn--outline" href="#optionen">Die 3 Optionen ansehen →</a>')
        + """
    <section class="brt-section" aria-labelledby="problem-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">DIE TEURE UNSICHERHEIT</p>
          <h2 id="problem-title" class="brt-h2">Sie wissen, dass irgendwo Risiken lauern. Aber welche sind die teuren?</h2>
          <p class="brt-body">Welches Risiko könnte Sie im nächsten Jahr 50.000 €, 200.000 € oder mehr kosten? Sie führen ein Unternehmen mit Mitarbeitenden, Kunden, Prozessen und Verantwortung – und spüren: Da ist etwas, das Sie übersehen.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Das externe Problem</h3><p class="brt-body">Sie haben kein vollständiges Bild Ihrer Risiken. Klassische Methoden sind für Konzerne gebaut – komplex, theoretisch, bürokratisch.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Das interne Problem</h3><p class="brt-body">Das Bauchgefühl sagt ‚da ist was' – aber Sie können es nicht benennen, nicht priorisieren, nicht beziffern.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Die Überzeugung</h3><p class="brt-body">Wer Verantwortung für Mitarbeitende und Kunden trägt, sollte wissen, wo die größten Risiken liegen. Nicht irgendwann. Jetzt.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="erstgespraech-title">
      <div class="brt-container brt-fade-up">
        <p class="brt-tag">ERST GEBEN, DANN ANBIETEN</p>
        <h2 id="erstgespraech-title" class="brt-h2">Ihr kostenloses Erstgespräch: die komplette Methode, offen erklärt</h2>
        <p class="brt-body">In ca. 45–60 Minuten zeigen wir Ihnen, wie Sie selbst eine strukturierte Risikoanalyse durchführen. Sie bekommen:</p>
        <ul class="brt-list-check">
          <li>Den 3-Ebenen-Ansatz erklärt (Gefahren → Risiken → Maßnahmen)</li>
          <li>Die Bewertungslogik (Szenario, Schaden in Euro, Eintrittswahrscheinlichkeit, Inventar)</li>
          <li>Die Fragetechnik, mit der Sie Ihr Team einbinden</li>
          <li>Einen konkreten Startpunkt: die 5 Gefahrenfelder, die Sie zuerst durchgehen sollten</li>
        </ul>
      </div>
    </section>"""
        + pricing_cards(pre, opts, price_note=f'Analysepakete ab 3.475 € Festpreis. Alle Preise transparent auf der <a href="{pre}preise/">Preisseite</a>.')
        + guarantee(pre, "Ihr Risiko ist null")
        + faq_section(kmu_faq, alt=True)
        + f"""
    <section class="brt-section" aria-label="Ratgeber-Empfehlung">
      <div class="brt-container brt-fade-up">
        <p class="brt-body">Geschäftsführung, Meister, Vertrieb: Wie Sie Schlüsselpersonen im Mittelstand erkennen und absichern, lesen Sie im Ratgeber <a href="{pre}blog/schluesselpersonrisiko-erkennen-absichern/">Schlüsselpersonrisiko erkennen, bewerten und absichern &rarr;</a></p>
      </div>
    </section>"""
        + cta_band(pre, "Verschaffen Sie sich Klarheit – bevor ein Risiko zuschlägt",
                   "Erstgespräch buchen – kostenlos, unverbindlich. Sie gehen mit einer DIY-Anleitung raus, egal wie Sie sich entscheiden.",
                   "Kostenloses Erstgespräch buchen")
    )
    kmu_title = "Risikomanagement Beratung KMU & Mittelstand | Beraterium"
    kmu_desc = "Risikomanagement-Beratung für den Mittelstand: Risiko-Lagebild in Euro, ab 3.475 € Festpreis. Kostenloses Erstgespräch. Doppelte Garantie."
    kmu_ld = page_schema(
        service_schema(name="6-Wochen Klarheits-Fahrplan für KMU", description=kmu_desc, url="/angebote/kmu/", audience="KMU und Mittelstand"),
        faq_page_schema(kmu_faq),
    )
    lp_shell(2, "kmu", kmu_title, kmu_desc, False, main, json_ld=kmu_ld)


def gen_lp_solo() -> None:
    pre = "../../"
    solo_faq = [
        ("Lohnt sich das, wenn ich nur ich bin?", "Gerade dann. Fällst du aus, gibt es keinen Puffer."),
        ("Wie viel Zeit kostet es mich?", "Eine Session von 2–3 Stunden plus ein kurzes Kick-off. Mehr nicht."),
        ("Ich finde Risiko-Themen unangenehm – wird das ein Angst-Termin?", "Nein. Es geht um Klarheit und Handlungsfähigkeit, nicht um Angst."),
        ("Was bringt mir der KI-Impulsgeber konkret?", "Er liefert statistische Einschätzungen und Erfahrungswerte, damit deine Bewertung nicht nur auf deinem Bauchgefühl beruht."),
        ("Was passiert, wenn ich als Selbstständiger krank werde?", "Keine Lohnfortzahlung — fixe Kosten laufen weiter. Beraterium bewertet das Szenario konkret und hilft beim Notfallplan."),
        ("Was ist Scheinselbstständigkeit und wie prüfe ich, ob ich betroffen bin?", "Formal Freelancer, faktisch wie Angestellter — die Rentenversicherung kann rückwirkend Beiträge nachfordern. Wir bewerten das Risiko im Solo-Kompass."),
        ("Wie viele Rücklagen sollte ich als Selbstständiger aufbauen?", "Faustregel: 3–6 Monate laufende Kosten. Im Risiko-Kompass rechnen wir das für dein konkretes Profil durch."),
    ]
    opts = [
        {"title": "Option A — Risiko-Check Solo", "claim": "In 2 Wochen weißt du, wo du verletzlich bist.", "features": [
            "Kick-off (Situation, Scope, Nutzen-Kriterien)", "Moderierte Risikoanalyse (1 Session, 2–3h) mit 2 Moderatoren + KI-Impulsgeber",
            "Gefahrenkatalog Solo-Edition (3 Ebenen)", "Bewertung: Schadenshöhe in Euro + Wahrscheinlichkeit",
            "Inventar-Check + Risiko-Report (1–2 Seiten)"]},
        {"title": "Option B — Risiko-Check + Maßnahmen-Plan", "claim": "Du weißt, was los ist – und was du tun kannst.", "badge": "Beliebt", "featured": True,
         "extra": "Alles aus A, plus:", "features": [
            "Maßnahmen-Session (Top-Risiken → konkrete Schritte)", "Quick-Win-Liste für diese Woche",
            "Priorisierter Fahrplan: Was zuerst, was kann warten?", "Ressourcen-Check: Was schaffst du allein, wo brauchst du Hilfe?"]},
        {"title": "Option C — Risiko-Check + Maßnahmen + Umsetzungs-Sparring", "claim": "Wir bleiben dran, bis du sicher aufgestellt bist.",
         "extra": "Alles aus B, plus:", "features": [
            "6 Wochen Sparring (3× 30 Min., alle 2 Wochen)", "Zugang zur RisikoRadar-Community",
            "Experten-Vermittlung bei konkretem Bedarf", "Risiko-Update nach 6 Wochen"]},
    ]
    main = (
        hero(pre, "RISIKO-KOMPASS FÜR SOLO-SELBSTSTÄNDIGE", "Du bist dein Unternehmen. Weißt du, wo du verletzlich bist?",
             "Für Freiberufler, Einzelunternehmer und Solo-Selbstständige. In 2 Wochen weißt du, welche Risiken dich am härtesten treffen würden – nicht um Angst zu haben, sondern um frei entscheiden zu können.",
             split=True, media_label="Solo-Selbstständige beim Risiko-Kompass mit Beraterium",
             media_src=IMG_ANGEBOT_SOLO_HERO,
             actions=f'<a class="brt-btn" href="{pre}kontakt/">Kostenloses Erstgespräch buchen</a><a class="brt-btn brt-btn--outline" href="#optionen">Die 3 Optionen ansehen →</a>')
        + """
    <section class="brt-section" aria-labelledby="problem-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">KENNST DU DAS GEFÜHL?</p>
          <h2 id="problem-title" class="brt-h2">Wenn du ausfällst, steht alles. Wenn ein Kunde wegbricht, wackelt die Existenz.</h2>
          <p class="brt-body">Es gibt keinen Kollegen, der auffängt. Und ‚Risikomanagement' steht seit Ewigkeiten auf deiner ‚Müsste-ich-mal'-Liste.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Das externe Problem</h3><p class="brt-body">Du hast keinen Überblick, welche Risiken dein Business wirklich bedrohen. Klassische Risikoanalyse fühlt sich an wie für Konzerne mit 500 Leuten.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Das interne Problem</h3><p class="brt-body">Du machst dir Sorgen – über Ausfall, Abhängigkeiten, Dinge, die du übersiehst. Aber als Solo bist du allein mit diesen Gedanken.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Die Überzeugung</h3><p class="brt-body">Wer sein eigenes Unternehmen trägt, hat das Recht zu wissen, wo die größten Gefahren liegen. Um frei entscheiden zu können.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="moderatoren-title">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <h3 id="moderatoren-title" class="brt-h3">Warum zwei Moderatoren und ein KI-Impulsgeber?</h3>
        <p class="brt-body">Als Solo hast du kein Team, das verschiedene Perspektiven einbringt. Das ersetzen wir: zwei Moderatoren, die strukturieren und hinterfragen, plus ein KI-gestützter Impulsgeber für statistische Erfahrungswerte.</p>
      </div>
    </section>"""
        + pricing_cards(pre, opts, du=True, price_note=f'Kompakte Checks ab 47 € — alle Preise findest du transparent auf der <a href="{pre}preise/">Preisseite</a>.')
        + guarantee(pre, du=True, h2="Null Risiko für dich", tag="Dein Risiko liegt bei uns")
        + faq_section(solo_faq, alt=True)
        + f"""
    <section class="brt-section" aria-label="Ratgeber-Empfehlung">
      <div class="brt-container brt-fade-up">
        <p class="brt-body">Als Solo bist du selbst die Schlüsselperson. Was das konkret bedeutet und welche Sofortmaßnahmen helfen, liest du im Ratgeber <a href="{pre}blog/schluesselpersonrisiko-erkennen-absichern/">Schlüsselpersonrisiko erkennen, bewerten und absichern &rarr;</a></p>
      </div>
    </section>"""
        + cta_band(pre, "Hol dir Klarheit über deine Risiken",
                   "Erstgespräch buchen – 30 Minuten, gratis, kein Druck. Du bekommst unsere DIY-Methode erklärt und entscheidest danach in Ruhe.",
                   "Kostenloses Erstgespräch buchen")
    )
    solo_title = "Risikomanagement Selbstständige – 2 Wochen | Beraterium"
    solo_desc = "Risikomanagement für Selbstständige: In 2 Wochen weißt du, wo du verletzlich bist — Ausfall, Kundenabhängigkeit, Scheinselbstständigkeit. Mit Garantie."
    solo_ld = page_schema(
        service_schema(name="2-Wochen Risiko-Kompass für Solo-Selbstständige", description=solo_desc, url="/angebote/solo/", audience="Solo-Selbstständige und Freelancer"),
        faq_page_schema(solo_faq),
    )
    lp_shell(2, "solo", solo_title, solo_desc, True, main, json_ld=solo_ld)


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
    """Datengetriebenes SEO+GEO-One-Pager-Template unter /loesungen/<slug>/.

    Eine neue Landingpage = ein neuer Eintrag in LP_CONFIGS (siehe NIS2 als
    Referenz). Struktur: Hero (answer-first) -> Kriterien-Checkliste (GEO-
    Zitat-Block) -> Stats -> Schmerz-Karten -> Beraterium-Ueberblick mit Links
    zur Hauptseite -> FAQ (sichtbar + Schema aus derselben Quelle) -> CTA.
    """
    slug = cfg["slug"]
    pre = "../../"
    canonical = f"/loesungen/{slug}/"

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
        f'<a class="brt-btn brt-btn--outline" href="{pre}{hero_cta2["href"]}" '
        f'data-print-url="{DE_SITE_URL}/{hero_cta2["href"]}">{hero_cta2["label"]}</a>'
        if hero_cta2
        else '<a class="brt-btn brt-btn--outline" href="#faq">Häufige Fragen \u2192</a>'
    )
    pdf_button_html = (
        '<button type="button" class="brt-btn brt-btn--ghost" data-brt-print>Als PDF speichern</button>'
        if cfg.get("pdf_button")
        else ""
    )
    main = (
        hero(
            pre, cfg["tag"], cfg["h1"], cfg["lead"],
            actions=(
                f'<a class="brt-btn" href="{pre}kontakt/" data-print-url="{DE_SITE_URL}/kontakt/">{cfg["hero_cta"]}</a>'
                f'{hero_cta2_html}{pdf_button_html}'
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
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DE_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": cfg["breadcrumb_name"], "item": f"{DE_SITE_URL}{canonical}"},
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
        f"loesungen/{slug}/index.html",
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
        "hero_cta": "Kostenloses Erstgespräch buchen",
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
            ("Die Methode", "Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.", "methode/", "Zur Methode"),
            ("Risikoanalyse für KMU", "In rund 6 Wochen zu einem vollständigen, bankfähigen Risiko-Lagebild – inklusive NIS2-relevanter Cyberrisiken.", "angebote/kmu/", "Zum Angebot für KMU"),
            ("Doppelte Garantie", "Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.", "nutzen-garantie/", "Zur Garantie"),
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
            "cyberangriff-was-tun-kmu",
            "sicherheit-unternehmen-risikomanagement-kmu",
            "risikomanagement-beratung-kmu-anbieter",
        ],
        "cta_h2": "Klären Sie Ihre NIS2-Betroffenheit – kostenlos und unverbindlich",
        "cta_body": "Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Sie erhalten unsere Methode erklärt und wissen danach, wo Sie stehen.",
        "title": "NIS2-Betroffenheit prüfen für KMU | Beraterium",
        "description": "Prüfen Sie, ob Ihr Unternehmen von der NIS2-Richtlinie betroffen ist – inklusive Pflichten, Fristen und Bußgeldern. Kostenloses Erstgespräch buchen.",
        "service_name": "NIS2-Risikocheck für KMU",
        "breadcrumb_name": "NIS2-Betroffenheit",
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): unternehmensnachfolge planen / nachfolge mittelstand risiken
        "slug": 'nachfolge',
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
        "hero_cta": 'Kostenloses Erstgespräch buchen',
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
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'methode/', 'Zur Methode'),
            ('Risikoanalyse für KMU', 'In rund 6 Wochen zu einem vollständigen, bankfähigen Risiko-Lagebild – inklusive Nachfolge-Risiken.', 'angebote/kmu/', 'Zum Angebot für KMU'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.', 'nutzen-garantie/', 'Zur Garantie'),
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
            "unternehmensnachfolge-uebersehene-risiken",
            "familiennachfolge-generationskonflikt-risiko-nach-uebergabe",
            "schluesselpersonrisiko-erkennen-absichern",
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
        "slug": 'cyberangriff',
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
        "hero_cta": 'Kostenloses Erstgespräch buchen',
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
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'methode/', 'Zur Methode'),
            ('Risikoanalyse für KMU', 'In rund 6 Wochen zu einem vollständigen, bankfähigen Risiko-Lagebild – inklusive Cyber- und NIS2-Risiken.', 'angebote/kmu/', 'Zum Angebot für KMU'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.', 'nutzen-garantie/', 'Zur Garantie'),
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
            "cyberangriff-was-tun-kmu",
            "sicherheit-unternehmen-risikomanagement-kmu",
            "schluesselpersonrisiko-erkennen-absichern",
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
        "slug": 'selbststaendig-absichern',
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
        "hero_cta": 'Kostenloses Erstgespräch buchen',
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
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'methode/', 'Zur Methode'),
            ('2-Wochen-Risiko-Kompass', 'In zwei Wochen zu einem vollständigen Risiko-Lagebild – speziell für Solo-Selbstständige und Freelancer.', 'angebote/solo/', 'Zum Solo-Angebot'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Du erhältst den vollen Betrag zurück.', 'nutzen-garantie/', 'Zur Garantie'),
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
            "risiken-selbststaendige-freelancer",
            "scheinselbststaendigkeit-pruefen",
            "schluesselpersonrisiko-erkennen-absichern",
        ],
        "cta_h2": 'Prüfe deine Absicherung – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Du erhältst unsere Methode erklärt und weißt danach, wo du stehst.',
        "title": 'Selbstständig absichern: Ausfallrisiko | Beraterium',
        "description": 'Selbstständig absichern: Ausfallrisiko und Kundenkonzentration in Euro bewertet. Der 2-Wochen-Risiko-Kompass. Kostenloses Erstgespräch buchen.',
        "service_name": '2-Wochen-Risiko-Kompass für Solo',
        "breadcrumb_name": 'Selbstständig absichern',
    },
    {
        # Keyword (Webseite/Keywords/keyword-liste-master.csv): schlüsselperson absichern unternehmen / key person risiko
        "slug": 'schluesselperson-risiko',
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
        "hero_cta": 'Kostenloses Erstgespräch buchen',
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
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'methode/', 'Zur Methode'),
            ('Angebote für jede Zielgruppe', 'Ob KMU, Startup oder Solo – Beraterium hat ein passendes Risiko-Angebot für Ihre Situation.', 'angebote/', 'Zu den Angeboten'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Sie erhalten den vollen Betrag zurück.', 'nutzen-garantie/', 'Zur Garantie'),
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
            "schluesselpersonrisiko-erkennen-absichern",
            "unternehmensnachfolge-uebersehene-risiken",
            "risiken-selbststaendige-freelancer",
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
        "hero_cta": 'Kostenloses Erstgespräch buchen',
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
            ('Die Methode', 'Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.', 'methode/', 'Zur Methode'),
            ('4-Wochen-Risiko-Check', 'In vier Wochen zu einem investor-ready Risiko-Portfolio – Key-Person, Cash, Legal und Tech.', 'angebote/startups/', 'Zum Startup-Angebot'),
            ('Doppelte Garantie', 'Kein relevantes Risiko gefunden oder kein Nutzen? Du erhältst den vollen Betrag zurück.', 'nutzen-garantie/', 'Zur Garantie'),
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
            "startup-fehler-vermeiden-risikomanagement",
            "schluesselpersonrisiko-erkennen-absichern",
            "what-is-risk-management",
        ],
        "cta_h2": 'Mach dein Startup investor-ready – kostenlos und unverbindlich',
        "cta_body": 'Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Du erhältst unsere Methode erklärt und weißt danach, wo du stehst.',
        "title": 'Startup Due Diligence vorbereiten | Beraterium',
        "description": 'Due Diligence für Startups: Risiken erkennen, in Euro bewerten und investor-ready werden. Der 4-Wochen-Check. Kostenloses Erstgespräch buchen.',
        "service_name": '4-Wochen-Risiko-Check für Startups',
        "breadcrumb_name": 'Investor Due Diligence',
    },
    {
        # Angebots-One-Pager ohne BAFA (2026-08-07). Keyword (Webseite/Keywords/keyword-themen-map.md): "risikoanalyse startup kosten"
        "slug": "risikoanalyse-startup",
        "du": True,
        "audience": "Startups und Gründer",
        "tag": "RISIKOANALYSE STARTUP",
        "h1": "Risikoanalyse für dein Startup: Ablauf und Kosten",
        "lead": (
            "Die Risiko-Analyse 360° zeigt dir die Top 5–10 Risiken deines Startups, in Euro bewertet "
            "und priorisiert – von Schlüsselperson-Abhängigkeit bis Runway. Du bekommst Analyse, "
            "Strategie-Sitzung und Budgetplanung als Festpreis-Bundle für 3.475 €, abgeschlossen in "
            "2–4 Wochen. Noch nicht so weit? Der kostenlose Blindspot Quick Check zeigt dir in 10 "
            "Minuten deine größten blinden Flecken."
        ),
        "hero_cta": "Kostenloses Erstgespräch buchen",
        "hero_cta2": {"label": "Blindspot Quick Check (10 Min)", "href": "tools/blindspot-check/"},
        "guarantee_section": True,
        "criteria_tag": "DIREKT-CHECK",
        "criteria_h2": "Passt eine Risikoanalyse zu deinem Startup?",
        "criteria_intro": "Eine strukturierte Risikoanalyse lohnt sich für dich, wenn mindestens eines dieser Kriterien zutrifft:",
        "criteria": [
            "Du hast Product-Market-Fit erreicht oder stehst kurz davor",
            "Dein Team hat 3–20 Mitarbeitende",
            "Ein Investoren-Gespräch oder eine Due-Diligence-Prüfung steht an oder ist absehbar",
            "Mindestens ein Risiko (Schlüsselperson, Runway, Kunde) würde dein Startup ernsthaft treffen",
        ],
        "stats_aria": "Risikoanalyse Startup in Zahlen",
        "stats": [
            ("2–4 Wochen", "von der Analyse bis zum fertigen Report"),
            ("Top 5–10", "Risiken einzeln in Euro bewertet und priorisiert"),
            ("3.475 €", "Festpreis für Analyse, Strategie und Budget"),
            ("2× Geld zurück", "Relevanz- und Nutzen-Garantie"),
        ],
        "pain_tag": "DIE DREI RISIKEN, DIE INVESTOREN SEHEN",
        "pain_h2": "Was passiert, wenn diese drei Risiken unentdeckt bleiben?",
        "pain_intro": "Als Gründer trägst du Risiken, die im Alltag unsichtbar bleiben – bis ein Investor oder ein Ausfall sie sichtbar macht.",
        "pain_cards": [
            ("Schlüsselperson-Risiko", 'Hängt Produkt oder Vertrieb an einer Person – meist dir selbst? Fällst du aus, steht das Startup still. Mehr dazu: <a href="../../loesungen/schluesselperson-risiko/">Schlüsselperson-Risiko erkennen</a>.'),
            ("Runway und Burn-Rate", "Rund 32 % der scheiternden Startups scheitern an Cash, nicht am Produkt. Ohne klares Bild wird Runway erst zum Thema, wenn es zu spät ist."),
            ("Due Diligence", 'Investoren fragen nach deinem Risk Assessment. Ohne strukturiertes Risikobild wirkt das wie Unsicherheit – nicht wie Kontrolle. Mehr dazu: <a href="../../loesungen/investor-due-diligence/">Investor Due Diligence vorbereiten</a>.'),
        ],
        "overview_tag": "WEITERFÜHREND",
        "overview_h2": "Wie hängt die Risikoanalyse mit dem restlichen Angebot zusammen?",
        "overview_intro": "Die Risikoanalyse ist der Einstieg – je nach Ergebnis ergeben sich daraus weitere, gezielte Schritte.",
        "overview_cards": [
            ("Die Methode", "Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.", "methode/", "Zur Methode"),
            ("Angebot für Startups", "Alle Pakete für Startups im Überblick – von der Kurzanalyse bis zur vollen Risiko-Analyse 360°.", "angebote/startups/", "Zum Startup-Angebot"),
            ("Alle Preise", "Die komplette Preisübersicht aller 32 Angebote – Analyse, Workshops, Schulungen.", "preise/", "Zur Preisübersicht"),
            ("Blindspot Quick Check", "Kostenloser Selbsttest: 10 Minuten, deine größten blinden Flecken sofort sichtbar.", "tools/blindspot-check/", "Zum Quick Check"),
        ],
        "faq": [
            ("Was kostet eine Risikoanalyse für Startups?", "Die Risiko-Analyse 360° (RA-01) kostet 3.475 € als Festpreis für Analyse, Strategie-Sitzung und Budgetplanung – einzeln würden die drei Bausteine 5.150 € kosten. Für einen kleineren Einstieg gibt es die reine Analyse (RA-02) für 1.725 € oder die Risikoanalyse-Vorbereitung für Startups (ZUS-05) für 295 €."),
            ("Wie lange dauert die Risikoanalyse?", "Die Risiko-Analyse 360° umfasst drei Workshops mit jeweils eigenem Report und Nachbereitungsgespräch – von der Terminvereinbarung bis zum fertigen Ergebnis dauert der gesamte Prozess in der Regel 2–4 Wochen, abhängig von der Terminverfügbarkeit deines Teams."),
            ("Was passiert im kostenlosen Erstgespräch?", "Im 30-minütigen Erstgespräch klären wir, wo dein Startup steht, welche Risiken bereits absehbar sind und welches Paket zu deiner Phase passt – unverbindlich und ohne Verkaufsdruck."),
            ("Was bekomme ich am Ende schriftlich?", "Nach jedem Workshop erhältst du einen Report: die priorisierte Risikoliste in Euro bewertet, den Strategie- und Umsetzungsplan sowie den Budgetplan mit Kosten-Nutzen-Einordnung – zusammen ein vollständiges, investorentaugliches Dokument."),
            ("Was ist, wenn ich unsicher bin, ob mein Startup das schon braucht?", "Wenn Product-Market-Fit, Investoren-Interesse oder ein spürbares Risiko noch nicht da sind, reicht oft der kostenlose Blindspot Quick Check als erster Schritt – er zeigt in 10 Minuten, wo du stehst."),
            ("Was passiert, wenn die Analyse kein relevantes Risiko findet?", "Dann greift die Relevanz-Garantie: Findet die Analyse kein einziges Risiko mit relevanter Schadenshöhe, erstattet Beraterium den vollen Betrag. Zusätzlich sichert die Nutzen-Garantie ab, dass die vereinbarten Kriterien auch tatsächlich erfüllt werden."),
        ],
        "deep_sections": [
            {
                "tag": "LEISTUNGSUMFANG (RA-01)",
                "h2": "Was ist im Festpreis RA-01 (3.475 €) enthalten?",
                "intro": (
                    "Die Kombination aller drei Analyse-Bausteine — Analyse, Strategie und Budget — in einem "
                    "durchgehenden Prozess mit deinem Team. Das Bundle ist günstiger als die Einzelbuchung "
                    "(einzeln 5.150 €) und der empfohlene Einstieg für Startups mit Investoren- oder Wachstumsdruck."
                ),
                "items": [
                    "Analyse-Workshop: die Top 5–10 Risiken identifizieren, in Euro bewerten und nach Eintrittswahrscheinlichkeit einordnen",
                    "Strategie-Workshop: für die wichtigsten Risiken konkrete, umsetzbare Maßnahmen entwickeln – mit Umsetzungsplan",
                    "Budget-Workshop: eigene Ressourcen vs. externe Dienstleister abwägen, orientiert am Schaden aus der Analyse",
                    "Jede Phase endet mit einem Report und einem Nachbereitungsgespräch mit der Geschäftsführung",
                ],
            },
        ],
        "steps_section": {
            "tag": "SO LÄUFT ES AB",
            "h2": "Wie läuft die Risikoanalyse für dein Startup ab?",
            "intro": "Fünf klare Schritte – kein Rätselraten über den Aufwand.",
            "steps": [
                ("Erstgespräch (30 Min)", "Wir klären deine Ausgangslage, dein Ziel und ob RA-01, RA-02 oder ZUS-05 zu deiner Phase passt."),
                ("Analyse-Workshop", "Gemeinsam mit dir identifizieren wir die Top 5–10 Risiken deines Startups und bewerten sie in Euro."),
                ("Report mit priorisierten Risiken", "Du erhältst die priorisierte Risikoliste schriftlich – Basis für Investoren- oder Bankgespräche."),
                ("Strategie-Sitzung", "Für die wichtigsten Risiken entwickeln wir konkrete, umsetzbare Maßnahmen mit Umsetzungsplan."),
                ("Budgetplanung", "Du entscheidest, wie viel Budget in welche Maßnahme fließt – orientiert am tatsächlichen Schaden aus der Analyse."),
            ],
        },
        "facts_table": {
            "tag": "PAKETVERGLEICH",
            "h2": "Welches Paket passt zu deiner Phase?",
            "intro": "Drei Einstiegspunkte, je nach Startup-Phase und Budget – vom kompakten Check bis zur vollen Risiko-Analyse 360°.",
            "caption": "Paketvergleich ZUS-05, RA-02 und RA-01 für Startups",
            "headers": ["Paket", "Dauer", "Ergebnis", "Preis"],
            "rows": [
                ("ZUS-05 Risikoanalyse-Vorbereitung", "Session + Auswertung", "Typische Risikofelder deiner Branche eingeordnet, Basis für Investorengespräche", "295 €"),
                ("RA-02 Risiko-Beratung (Analyse)", "1 Workshop (2–3 h) + Report", "Top 5–10 Risiken identifiziert, in Euro bewertet und priorisiert", "1.725 €"),
                ("RA-01 Risiko-Analyse 360°", "3 Workshops + 3 Reports", "Analyse, Strategie und Budgetplanung im Festpreis-Bundle", "3.475 €"),
            ],
        },
        "blog_slugs": [
            "startup-fehler-vermeiden-risikomanagement",
            "schluesselpersonrisiko-erkennen-absichern",
            "what-is-risk-management",
        ],
        "cta_h2": "Kläre deine Top-Risiken – kostenlos und unverbindlich",
        "cta_body": "Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Du erhältst unsere Methode erklärt und weißt danach, wo du stehst.",
        "cta_note": 'Noch nicht so weit? <a href="../../tools/blindspot-check/">Blindspot Quick Check</a> – 10 Minuten, kostenlos.',
        "title": "Risikoanalyse Startup: Kosten & Ablauf | Beraterium",
        "description": "Risikoanalyse für dein Startup: Ablauf, Dauer und Preis ab 295 €. Top 5–10 Risiken in Euro bewertet, Festpreis 3.475 €. Kostenloses Erstgespräch buchen.",
        "service_name": "Risiko-Analyse 360° für Startups",
        "breadcrumb_name": "Risikoanalyse Startup",
    },
    {
        # Angebots-One-Pager ohne BAFA (2026-08-07). Keyword (Webseite/Keywords/keyword-themen-map.md): "risikoanalyse kmu kosten"
        "slug": "risikoanalyse-kmu",
        "du": False,
        "audience": "KMU und Mittelstand",
        "tag": "RISIKOANALYSE KMU",
        "h1": "Risikoanalyse für Ihr KMU: Ablauf und Kosten",
        "lead": (
            "Die Risiko-Analyse 360° liefert Ihnen die Top 5–10 Risiken Ihres Unternehmens, in Euro "
            "bewertet und priorisiert – von Geschäftsführerhaftung bis Abhängigkeiten in gewachsenen "
            "Prozessen. Analyse, Strategie-Sitzung und Budgetplanung erhalten Sie als Festpreis-Bundle "
            "für 3.475 €, abgeschlossen in rund 6 Wochen. Noch unsicher? Der kostenlose Blindspot Quick "
            "Check zeigt in 10 Minuten Ihre größten blinden Flecken."
        ),
        "hero_cta": "Kostenloses Erstgespräch buchen",
        "hero_cta2": {"label": "Blindspot Quick Check (10 Min)", "href": "tools/blindspot-check/"},
        "guarantee_section": True,
        "criteria_tag": "DIREKT-CHECK",
        "criteria_h2": "Passt eine Risikoanalyse zu Ihrem Unternehmen?",
        "criteria_intro": "Eine strukturierte Risikoanalyse lohnt sich für Sie, wenn mindestens eines dieser Kriterien zutrifft:",
        "criteria": [
            "Ihr Unternehmen hat 10–80 Mitarbeitende",
            "Prozesse und Verantwortlichkeiten sind über Jahre gewachsen, aber nie systematisch geprüft worden",
            "Sie tragen als Geschäftsführung persönliche Haftung, z. B. durch NIS2 oder andere Regulatorik",
            "Eine Nachfolge, ein Bank- oder Beiratsgespräch steht an oder ist absehbar",
        ],
        "stats_aria": "Risikoanalyse KMU in Zahlen",
        "stats": [
            ("Rund 6 Wochen", "von der Analyse bis zum vollständigen Lagebild"),
            ("Top 5–10", "Risiken einzeln in Euro bewertet und priorisiert"),
            ("3.475 €", "Festpreis für Analyse, Strategie und Budget"),
            ("2× Geld zurück", "Relevanz- und Nutzen-Garantie"),
        ],
        "pain_tag": "DIE DREI RISIKEN IM MITTELSTAND",
        "pain_h2": "Was passiert, wenn diese drei Risiken unentdeckt bleiben?",
        "pain_intro": "Im gewachsenen Mittelstand verstecken sich Risiken oft in Prozessen, die niemand mehr hinterfragt.",
        "pain_cards": [
            ("GF-Haftung und NIS2", 'NIS2 und weitere Regulatorik machen Risikomanagement zur Geschäftsführerpflicht – ohne dokumentierte Analyse haften Sie persönlich. Mehr dazu: <a href="../../loesungen/nis2/">NIS2-Betroffenheit prüfen</a>.'),
            ("Nachfolge", 'Bis 2030 stehen rund 186.000 Unternehmensübergaben an. Ohne belastbares Risikobild wird die Übergabe für Bank, Beirat oder Nachfolger schwer einschätzbar. Mehr dazu: <a href="../../loesungen/nachfolge/">Risiken bei der Unternehmensnachfolge</a>.'),
            ("Abhängigkeiten in gewachsenen Prozessen", 'Schlüsselpersonen, Einzel-Lieferanten oder undokumentiertes Wissen entstehen unbemerkt über Jahre – und werden erst im Ernstfall sichtbar. Mehr dazu: <a href="../../loesungen/schluesselperson-risiko/">Schlüsselperson-Risiko erkennen</a>.'),
        ],
        "overview_tag": "WEITERFÜHREND",
        "overview_h2": "Wie hängt die Risikoanalyse mit dem restlichen Angebot zusammen?",
        "overview_intro": "Die Risikoanalyse ist der Einstieg – je nach Ergebnis ergeben sich daraus weitere, gezielte Schritte.",
        "overview_cards": [
            ("Die Methode", "Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.", "methode/", "Zur Methode"),
            ("Angebot für KMU", "Alle Pakete für den Mittelstand im Überblick – von der Kurzanalyse bis zur vollen Risiko-Analyse 360°.", "angebote/kmu/", "Zum KMU-Angebot"),
            ("Alle Preise", "Die komplette Preisübersicht aller 32 Angebote – Analyse, Workshops, Schulungen.", "preise/", "Zur Preisübersicht"),
            ("Blindspot Quick Check", "Kostenloser Selbsttest: 10 Minuten, Ihre größten blinden Flecken sofort sichtbar.", "tools/blindspot-check/", "Zum Quick Check"),
        ],
        "faq": [
            ("Was kostet eine Risikoanalyse für KMU?", "Die Risiko-Analyse 360° (RA-01) kostet 3.475 € als Festpreis für Analyse, Strategie-Sitzung und Budgetplanung – einzeln würden die drei Bausteine 5.150 € kosten. Für einen kleineren Einstieg gibt es die reine Analyse (RA-02) für 1.725 €."),
            ("Wie lange dauert die Risikoanalyse für ein KMU?", "Die Risiko-Analyse 360° umfasst drei Workshops mit jeweils eigenem Report und Nachbereitungsgespräch mit der Geschäftsführung – der gesamte Prozess dauert in der Regel rund 6 Wochen, abhängig von der Terminverfügbarkeit Ihres Teams."),
            ("Was passiert im kostenlosen Erstgespräch?", "Im 30-minütigen Erstgespräch klären wir Ihre Ausgangslage, mögliche Risikofelder und welches Paket zu Ihrem Unternehmen passt – unverbindlich und ohne Verkaufsdruck."),
            ("Was erhalten wir am Ende schriftlich?", "Nach jedem Workshop erhalten Sie einen Report: die priorisierte Risikoliste in Euro bewertet, den Strategie- und Umsetzungsplan sowie den Budgetplan mit Kosten-Nutzen-Einordnung – zusammen ein vollständiges, bankfähiges Lagebild."),
            ("Was ist, wenn wir unsicher sind, ob wir das brauchen?", "Wenn noch unklar ist, ob strukturiertes Risikomanagement nötig ist, reicht oft der kostenlose Blindspot Quick Check als erster Schritt – er zeigt in 10 Minuten, wo Ihr Unternehmen steht."),
            ("Was passiert, wenn die Analyse kein relevantes Risiko findet?", "Dann greift die Relevanz-Garantie: Findet die Analyse kein einziges Risiko mit relevanter Schadenshöhe, erstattet Beraterium den vollen Betrag. Zusätzlich sichert die Nutzen-Garantie ab, dass die vereinbarten Kriterien auch tatsächlich erfüllt werden."),
        ],
        "deep_sections": [
            {
                "tag": "LEISTUNGSUMFANG (RA-01)",
                "h2": "Was ist im Festpreis RA-01 (3.475 €) enthalten?",
                "intro": (
                    "Die Kombination aller drei Analyse-Bausteine — Analyse, Strategie und Budget — in einem "
                    "durchgehenden Prozess mit Ihrem Team. Das Bundle ist günstiger als die Einzelbuchung "
                    "(einzeln 5.150 €) und der empfohlene Einstieg für KMU."
                ),
                "items": [
                    "Analyse-Workshop: die Top 5–10 Risiken identifizieren, in Euro bewerten und nach Eintrittswahrscheinlichkeit einordnen",
                    "Strategie-Workshop: für die wichtigsten Risiken konkrete, umsetzbare Maßnahmen entwickeln – mit Umsetzungsplan",
                    "Budget-Workshop: eigene Ressourcen vs. externe Dienstleister abwägen, orientiert am Schaden aus der Analyse",
                    "Jede Phase endet mit einem Report und einem Nachbereitungsgespräch mit der Geschäftsführung",
                ],
            },
        ],
        "steps_section": {
            "tag": "SO LÄUFT ES AB",
            "h2": "Wie läuft die Risikoanalyse für Ihr Unternehmen ab?",
            "intro": "Fünf klare Schritte – kein Rätselraten über den Aufwand.",
            "steps": [
                ("Erstgespräch (30 Min)", "Wir klären Ihre Ausgangslage, Ihr Ziel und ob RA-01 oder RA-02 zu Ihrem Unternehmen passt."),
                ("Analyse-Workshop", "Gemeinsam mit Ihrem Team identifizieren wir die Top 5–10 Risiken und bewerten sie in Euro."),
                ("Report mit priorisierten Risiken", "Sie erhalten die priorisierte Risikoliste schriftlich – Basis für Bank-, Beirats- oder Nachfolgegespräche."),
                ("Strategie-Sitzung", "Für die wichtigsten Risiken entwickeln wir konkrete, umsetzbare Maßnahmen mit Umsetzungsplan."),
                ("Budgetplanung", "Sie entscheiden, wie viel Budget in welche Maßnahme fließt – orientiert am tatsächlichen Schaden aus der Analyse."),
            ],
        },
        "facts_table": {
            "tag": "PAKETVERGLEICH",
            "h2": "Welches Paket passt zu Ihrem Unternehmen?",
            "intro": "Drei Stufen, je nach Bedarf – von der reinen Analyse bis zur begleiteten Umsetzung.",
            "caption": "Paketvergleich RA-02, RA-01 und RA-07 für KMU",
            "headers": ["Paket", "Dauer", "Ergebnis", "Preis"],
            "rows": [
                ("RA-02 Risiko-Beratung (Analyse)", "1 Workshop (2–3 h) + Report", "Top 5–10 Risiken identifiziert, in Euro bewertet und priorisiert", "1.725 €"),
                ("RA-01 Risiko-Analyse 360°", "3 Workshops + 3 Reports", "Analyse, Strategie und Budgetplanung im Festpreis-Bundle", "3.475 €"),
                ("RA-07 Gesamtpaket L", "24–32 Wochen Begleitung", "Risiko-Analyse 360° plus Maßnahmen-Integration bis zur gelebten Umsetzung", "7.825 €"),
            ],
        },
        "blog_slugs": [
            "cyberangriff-was-tun-kmu",
            "unternehmensnachfolge-uebersehene-risiken",
            "risikomanagement-beratung-kmu-anbieter",
        ],
        "cta_h2": "Klären Sie Ihre Top-Risiken – kostenlos und unverbindlich",
        "cta_body": "Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Sie erhalten unsere Methode erklärt und wissen danach, wo Sie stehen.",
        "cta_note": 'Noch unsicher? <a href="../../tools/blindspot-check/">Blindspot Quick Check</a> – 10 Minuten, kostenlos.',
        "title": "Risikoanalyse KMU: Kosten & Ablauf | Beraterium",
        "description": "Risikoanalyse für Ihr KMU: Ablauf, Dauer und Festpreis 3.475 €. Top 5–10 Risiken in Euro bewertet, doppelte Garantie. Kostenloses Erstgespräch buchen.",
        "service_name": "Risiko-Analyse 360° für KMU",
        "breadcrumb_name": "Risikoanalyse KMU",
    },
    {
        # Angebots-One-Pager ohne BAFA (2026-08-07). Keyword (Webseite/Keywords/keyword-themen-map.md): "risikoanalyse selbstständige kosten"
        "slug": "risikoanalyse-solo",
        "du": True,
        "audience": "Solo-Selbstständige und Freelancer",
        "tag": "RISIKOANALYSE SELBSTSTÄNDIGE",
        "h1": "Risikoanalyse für Selbstständige: Ablauf und Kosten",
        "lead": (
            "Die Risiko-Beratung zeigt dir die Top 5–10 Risiken deiner Selbstständigkeit, in Euro "
            "bewertet – von Ausfall durch Krankheit bis Kundenabhängigkeit. Du bekommst einen Workshop "
            "mit Report und Nachbereitungsgespräch ab 1.725 €, für den ersten Überblick reicht auch der "
            "kompakte Risiko-Check ab 97 €. Noch nicht so weit? Der kostenlose Blindspot Quick Check "
            "zeigt dir in 10 Minuten deine größten blinden Flecken."
        ),
        "hero_cta": "Kostenloses Erstgespräch buchen",
        "hero_cta2": {"label": "Blindspot Quick Check (10 Min)", "href": "tools/blindspot-check/"},
        "guarantee_section": True,
        "criteria_tag": "DIREKT-CHECK",
        "criteria_h2": "Passt eine Risikoanalyse zu deiner Selbstständigkeit?",
        "criteria_intro": "Eine strukturierte Risikoanalyse lohnt sich für dich, wenn mindestens eines dieser Kriterien zutrifft:",
        "criteria": [
            "Dein Umsatz hängt vollständig an dir als Person – fällst du aus, fällt der Umsatz aus",
            "Du beschäftigst 1–5 Mitarbeitende oder arbeitest mit einem festen Netzwerk aus Kolleg:innen",
            "Ein Hauptkunde macht einen großen Teil deines Umsatzes aus",
            "Du hast noch keinen Überblick, wie viel dich ein Ausfall wirklich kosten würde",
        ],
        "stats_aria": "Risikoanalyse Selbstständige in Zahlen",
        "stats": [
            ("Ab 97 €", "für den kompakten Risiko-Check (30 Min)"),
            ("Top 5–10", "Risiken einzeln in Euro bewertet und priorisiert"),
            ("Ab 1.725 €", "für die vollständige Risiko-Beratung mit Report"),
            ("2× Geld zurück", "Relevanz- und Nutzen-Garantie"),
        ],
        "pain_tag": "DIE DREI RISIKEN OHNE VERTRETUNG",
        "pain_h2": "Was passiert, wenn diese drei Risiken unentdeckt bleiben?",
        "pain_intro": "Als Selbstständiger trägst du jedes Risiko allein – ohne Betriebsrat, ohne Vertretung, ohne IT-Abteilung.",
        "pain_cards": [
            ("Ausfall durch Krankheit", 'Es gibt keine Lohnfortzahlung – schon 4–6 Wochen Krankheit oder Burnout können existenzbedrohend werden, während Fixkosten weiterlaufen. Mehr dazu: <a href="../../loesungen/selbststaendig-absichern/">Als Selbstständiger absichern</a>.'),
            ("Kundenabhängigkeit", 'Macht ein Hauptkunde einen Großteil deines Umsatzes aus, entscheidet dessen Budgetplanung über deine Existenz. Mehr dazu: <a href="../../blog/risiken-selbststaendige-freelancer/">Risiken für Selbstständige</a>.'),
            ("Keine Vertretung", 'Ohne Kollegen oder Netzwerk-Kontakt mit Zugriff auf deine laufenden Projekte steht bei Ausfall alles still – auch gegenüber deinen Kunden. Mehr dazu: <a href="../../loesungen/schluesselperson-risiko/">Schlüsselperson-Risiko erkennen</a>.'),
        ],
        "overview_tag": "WEITERFÜHREND",
        "overview_h2": "Wie hängt die Risikoanalyse mit dem restlichen Angebot zusammen?",
        "overview_intro": "Die Risikoanalyse ist der Einstieg – je nach Ergebnis ergeben sich daraus weitere, gezielte Schritte.",
        "overview_cards": [
            ("Die Methode", "Der 3-Ebenen-Gefahrenkatalog: Gefahren sammeln, Risiken in Euro bewerten, Maßnahmen priorisieren.", "methode/", "Zur Methode"),
            ("Angebot für Solo", "Alle Pakete für Solo-Selbstständige im Überblick – vom kompakten Check bis zur vollen Risiko-Beratung.", "angebote/solo/", "Zum Solo-Angebot"),
            ("Alle Preise", "Die komplette Preisübersicht aller 32 Angebote – Analyse, Workshops, Schulungen.", "preise/", "Zur Preisübersicht"),
            ("Blindspot Quick Check", "Kostenloser Selbsttest: 10 Minuten, deine größten blinden Flecken sofort sichtbar.", "tools/blindspot-check/", "Zum Quick Check"),
        ],
        "faq": [
            ("Was kostet eine Risikoanalyse für Selbstständige?", "Der kompakte Risiko-Check kostet 97 € (30 Minuten) für eine erste Einschätzung. Die vollständige Risiko-Beratung mit Workshop, Report und Nachbereitungsgespräch kostet 1.725 €."),
            ("Wie lange dauert die Risikoanalyse?", "Der kompakte Risiko-Check dauert 30 Minuten. Die vollständige Risiko-Beratung umfasst einen Workshop von 2–3 Stunden plus Report und Nachbereitungsgespräch – abgeschlossen innerhalb weniger Tage."),
            ("Was passiert im kostenlosen Erstgespräch?", "Im 30-minütigen Erstgespräch klären wir, wo du stehst, welche Risiken bereits spürbar sind und ob der kompakte Check oder die vollständige Risiko-Beratung zu dir passt."),
            ("Was bekomme ich am Ende schriftlich?", "Du erhältst einen Report mit deinen Top 5–10 Risiken, bewertet nach Schadenshöhe in Euro und Eintrittswahrscheinlichkeit – Basis für Versicherungs- oder Bankgespräche."),
            ("Was ist, wenn ich unsicher bin, ob ich das brauche?", "Wenn du noch nicht einschätzen kannst, wo deine größten Risiken liegen, reicht oft der kostenlose Blindspot Quick Check als erster Schritt – er zeigt in 10 Minuten, wo du stehst."),
            ("Was passiert, wenn das Ergebnis nichts bringt?", "Dann greift die Relevanz-Garantie: Findet die Analyse kein einziges Risiko mit relevanter Schadenshöhe, erstattet Beraterium den vollen Betrag. Zusätzlich sichert die Nutzen-Garantie ab, dass die vereinbarten Kriterien auch tatsächlich erfüllt werden."),
        ],
        "deep_sections": [
            {
                "tag": "LEISTUNGSUMFANG (RA-02)",
                "h2": "Was bekommst du mit der Risiko-Beratung (RA-02)?",
                "intro": (
                    "Ein Workshop (2–3 Stunden), moderiert von uns. Ziel: aus Bauchgefühl wird eine "
                    "priorisierte, in Euro bewertete Liste – ohne dass du bereits in die Maßnahmenplanung "
                    "einsteigen musst."
                ),
                "items": [
                    "Bewertung jedes Risikos nach Schadenshöhe in Euro und Eintrittswahrscheinlichkeit",
                    "Top 5–10 Risiken benannt und priorisiert – Basis für Versicherungs- oder Bankgespräche",
                    "Ergebnis als Report dokumentiert, inklusive Nachbereitungsgespräch zur Einordnung",
                    "Ideal, wenn du zunächst nur Klarheit über die Risikolage willst, ohne direkt in die Maßnahmenplanung zu gehen",
                ],
            },
        ],
        "steps_section": {
            "tag": "SO LÄUFT ES AB",
            "h2": "Wie läuft die Risikoanalyse für dich ab?",
            "intro": "Fünf klare Schritte – kein Rätselraten über den Aufwand.",
            "steps": [
                ("Erstgespräch (30 Min)", "Wir klären deine Ausgangslage und ob der kompakte Check oder die vollständige Risiko-Beratung zu dir passt."),
                ("Analyse-Workshop", "Im Workshop identifizieren wir gemeinsam deine Top 5–10 Risiken und bewerten sie in Euro."),
                ("Report mit priorisierten Risiken", "Du erhältst die priorisierte Risikoliste schriftlich – Basis für Versicherungs- oder Bankgespräche."),
                ("Nachbereitungsgespräch", "Wir ordnen die Ergebnisse gemeinsam ein und klären offene Fragen zur Priorisierung."),
                ("Nächste Schritte festlegen", "Du entscheidest, welche Maßnahmen du zuerst angehst – allein oder mit begleitender Umsetzung."),
            ],
        },
        "facts_table": {
            "tag": "PAKETVERGLEICH",
            "h2": "Welches Paket passt zu dir?",
            "intro": "Drei Einstiegspunkte – vom kompakten Check bis zur vollständigen Risiko-Analyse 360°, falls dein Unternehmen wächst.",
            "caption": "Paketvergleich ZUS-02, RA-02 und RA-01 für Solo-Selbstständige",
            "headers": ["Paket", "Dauer", "Ergebnis", "Preis"],
            "rows": [
                ("ZUS-02 Kurzer Risiko-Check", "30 Minuten", "Grobe Einordnung deines Risiko-Status, Top-3-Risiken plus Sofort-Impulse", "97 €"),
                ("RA-02 Risiko-Beratung (Analyse)", "1 Workshop (2–3 h) + Report", "Top 5–10 Risiken identifiziert, in Euro bewertet und priorisiert", "1.725 €"),
                ("RA-01 Risiko-Analyse 360°", "3 Workshops + 3 Reports", "Analyse, Strategie und Budgetplanung im Festpreis-Bundle – z. B. bei wachsendem Team", "3.475 €"),
            ],
        },
        "blog_slugs": [
            "risiken-selbststaendige-freelancer",
            "scheinselbststaendigkeit-pruefen",
            "schluesselpersonrisiko-erkennen-absichern",
        ],
        "cta_h2": "Kläre deine Top-Risiken – kostenlos und unverbindlich",
        "cta_body": "Erstgespräch buchen – 30 Minuten, ohne Verkaufsdruck. Du erhältst unsere Methode erklärt und weißt danach, wo du stehst.",
        "cta_note": 'Noch nicht so weit? <a href="../../tools/blindspot-check/">Blindspot Quick Check</a> – 10 Minuten, kostenlos.',
        "title": "Risikoanalyse Selbstständige: Kosten | Beraterium",
        "description": "Risikoanalyse für Selbstständige: Ablauf, Dauer und Preis ab 97 €. Top 5–10 Risiken in Euro bewertet, doppelte Garantie. Kostenloses Erstgespräch buchen.",
        "service_name": "Risiko-Beratung für Solo-Selbstständige",
        "breadcrumb_name": "Risikoanalyse Selbstständige",
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
    """Lokale Vertretungs-One-Pager unter /standort/<slug>/ (Local SEO + GEO).

    Neue Stadt = neuer Eintrag in STANDORT_CONFIGS (Muenchen als Referenz).
    Struktur: Hero (answer-first) -> Lokalvertretung (Person + Region) ->
    Methode kompakt (GEO-Zitat-Block) -> Angebote-Ueberblick -> Doppelte
    Garantie -> Google Maps (Klick-to-load, DSGVO) -> Blog-Teaser ->
    Termin buchen (Calendly) -> FAQ (sichtbar + Schema) -> CTA.
    """
    slug = cfg["slug"]
    city = cfg["city"]
    pre = "../../"
    canonical = f"/standort/{slug}/"

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
                "angebote/kmu/",
                "Zum Angebot für KMU",
            ),
            (
                "Risiko-Check für Startups",
                "In 4 Wochen wissen Gründerteams, welche Risiken ihr Wachstum bremsen – investor-ready aufbereitet.",
                "angebote/startups/",
                "Zum Angebot für Startups",
            ),
            (
                "Risiko-Kompass für Solo-Selbstständige",
                "In 2 Wochen weißt du, wo du verletzlich bist – Ausfall, Kundenabhängigkeit, Rücklagen.",
                "angebote/solo/",
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
                f'<a class="brt-btn brt-btn--outline" href="#faq">Häufige Fragen \u2192</a>'
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
        <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}methode/">Zur Methode \u2192</a> <a class="brt-btn brt-btn--outline" href="{pre}preise/">Preise &amp; Leistungen \u2192</a></p>
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
        <p class="brt-meta brt-fade-up">Details zur Datenverarbeitung durch Google finden Sie in unserer <a href="{pre}datenschutz/">Datenschutzerklärung</a>.</p>
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
        + cta_band(pre, cfg["cta_h2"], cfg["cta_body"], "Kostenloses Erstgespräch buchen")
    )

    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DE_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": f"Beraterium vor Ort {city}", "item": f"{DE_SITE_URL}{canonical}"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    person_ld = ""
    member_section_id = team_section_id(member.slug) if member else ""
    if member:
        person_data = person_schema(member)
        person_data["@id"] = f"{DE_SITE_URL}/team/#{member_section_id}"
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
            employee_id=f"{DE_SITE_URL}/team/#{member_section_id}" if member else "",
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
        f"standort/{slug}/index.html",
        shell(
            depth=2,
            title=cfg["title"],
            description=cfg["description"],
            canonical=canonical,
            active_nav=None,
            main=main,
            json_ld=ld,
            og_image=(f"https://www.beraterium.de/{member.image}" if member and member.image else ""),
        ).replace(
            f'<script src="{pre}js/brt-analytics.js?v={BRT_ASSET_VERSION}"></script>\n<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
            f'<script src="{pre}js/brt-analytics.js?v={BRT_ASSET_VERSION}"></script>\n<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript" async></script>\n<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
        ),
    )


STANDORT_CONFIGS: list[dict] = [
    {
        # Keyword (lokal, Muster wie "risikomanagement bautzen" in Webseite/Keywords/keyword-liste-master.csv):
        # "risikomanagement münchen" / "risikoberatung münchen" — anbieter-suchend, Local SEO/GEO.
        # Adresse bewusst nur Region-Level (Umzug steht an); exakte Anschrift + Map-Pin nachrüsten, sobald final.
        "slug": "muenchen",
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
        "hero_cta": "Kostenloses Erstgespräch buchen",
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
        "slug": "sachsen",
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
        "hero_cta": "Kostenloses Erstgespräch buchen",
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
                "Kompakte Checks ab 47 €, vollständige Analysepakete ab 3.475 € Festpreis. Alle Preise stehen transparent auf beraterium.de/preise/ – unabhängig davon, ob Sie in Dresden, Leipzig oder Bautzen sitzen.",
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
            "Preise: transparent auf beraterium.de/preise/; kein Aufschlag für Sachsen.",
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
        "hero_cta": "Kostenloses Erstgespräch buchen",
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
                "Beraterium mit Joachim Lau als Lokalvertretung in Nordrhein-Westfalen. Er betreut KMU, Startups und Solo-Selbstständige in ganz NRW persönlich – Risiken in Euro bewertet, mit doppelter Garantie und transparenten Festpreisen auf beraterium.de/preise/.",
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
                "Kompakte Checks ab 47 €, vollständige Analysepakete ab 3.475 € Festpreis. Alle Preise stehen transparent auf beraterium.de/preise/ – unabhängig davon, ob Sie in Köln, Düsseldorf oder Dortmund sitzen.",
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
            "Preise: transparent auf beraterium.de/preise/; kein Aufschlag für NRW.",
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


def gen_risikoradar() -> None:
    pre = "../"
    main = (
        hero(pre, "UNSER NETZWERK", "RisikoRadar – Lösungen entstehen nicht isoliert",
             "Ein geschützter Raum aus geprüften, vertrauten Experten. Kein loser Kontaktpool, sondern ein funktionierendes Netzwerk, in dem Disziplinen zusammenspielen – damit aus Ihrer Analyse echte Umsetzung wird.")
        + """
    <section class="brt-section brt-section--narrow" aria-labelledby="umsetzung-title">
      <div class="brt-container brt-fade-up">
        <h2 id="umsetzung-title" class="brt-h2">Wir liefern keine Analyse zum Ablegen – sondern Lösungen zum Umsetzen</h2>
        <p class="brt-body">Die Analyse schafft Klarheit. Der eigentliche Mehrwert entsteht in der Umsetzung. Genau hier setzt RisikoRadar an: Wir bringen die richtigen Menschen zusammen und sorgen dafür, dass Maßnahmen sinnvoll ineinandergreifen. Beraterium bleibt dabei die Klammer.</p>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="ways-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">SIE ENTSCHEIDEN</p>
          <h2 id="ways-title" class="brt-h2">Wie soll die Umsetzung laufen?</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Selbst umsetzen</h3><p class="brt-body">Mit Ihrer eigenen Mannschaft – für organisatorische oder einfache Maßnahmen.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Mit Ihren Dienstleistern</h3><p class="brt-body">Mit vertrauten Partnern weiterarbeiten – für gewachsene Geschäftsbeziehungen.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Wir koordinieren</h3><p class="brt-body">Ein fester Ansprechpartner, ‚one face to the customer'. Wir bringen die richtigen Experten zusammen.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="special-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">KEIN LOSER KONTAKTPOOL</p>
          <h2 id="special-title" class="brt-h2">Vertrauen, Qualität, Zusammenarbeit</h2>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Zugang nur über Empfehlung oder Bewerbung</h3><p class="brt-body">Nicht jeder kommt rein. Das schützt die Qualität.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Geprüfte Experten</h3><p class="brt-body">Vertraute Spezialisten aus Organisation, Prozesse, Technik &amp; Sicherheit, IT &amp; Systeme, Mitarbeitende &amp; Verhalten.</p></li>
          <li class="brt-card brt-hover-lift"><h3 class="brt-h3">Ein Ansprechpartner</h3><p class="brt-body">Kein Koordinationsaufwand, keine Diskussionen über Zuständigkeiten – Ergebnisse statt Organisation.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="dual-cta">
      <div class="brt-container brt-two-col brt-two-col--cta brt-fade-up">
        <div>
          <h3 class="brt-h3">Sie suchen Umsetzung?</h3>
          <p class="brt-body">Nach Ihrer Risikoanalyse stellen wir Ihnen bei Bedarf genau die Experten zusammen, die zu Ihren Top-Risiken passen – schon geprüft, kein Google-Roulette.</p>
          <p class="brt-section__cta">
            <a class="brt-btn brt-btn--outline" href="../kontakt/">Erstgespräch buchen →</a>
          </p>
        </div>
        <div>
          <h3 class="brt-h3">Sie sind Experte und möchten mitwirken?</h3>
          <p class="brt-body">RisikoRadar wächst über Empfehlung und Bewerbung. Wenn Sie Qualität, Vertrauen und echte Zusammenarbeit schätzen, freuen wir uns über Ihre Nachricht.</p>
          <p class="brt-section__cta">
            <a class="brt-btn brt-btn--outline" href="../kontakt/">Als Experte bewerben →</a>
          </p>
        </div>
      </div>
    </section>"""
        + faq_section_html([
            ("Was ist RisikoRadar?", "RisikoRadar ist das geschützte Expertennetzwerk hinter Beraterium — geprüfte Fachleute, die Maßnahmen aus Ihrer Risikoanalyse umsetzen."),
            ("Wie komme ich in RisikoRadar?", "Als Beraterium-Kunde erhalten Sie Zugang. Experten kommen über Empfehlung oder Bewerbung — kein offenes Forum."),
        ], title="Häufige Fragen zu RisikoRadar", section_id="faq", alt=True)
        + cta_band(pre, "Aus Klarheit wird Handlungsfähigkeit", "Sie entscheiden, wie die Umsetzung läuft – wir sorgen dafür, dass sie funktioniert.")
    )
    risikoradar_faq = [
        ("Was ist RisikoRadar?", "RisikoRadar ist das geschützte Expertennetzwerk hinter Beraterium — geprüfte Fachleute, die Maßnahmen aus Ihrer Risikoanalyse umsetzen."),
        ("Wie komme ich in RisikoRadar?", "Als Beraterium-Kunde erhalten Sie Zugang. Experten kommen über Empfehlung oder Bewerbung — kein offenes Forum."),
    ]
    write("risikoradar/index.html", shell(depth=1, title="RisikoRadar – Expertennetzwerk | Beraterium",
          description="RisikoRadar ist ein geschütztes Netzwerk geprüfter Experten. So setzen Sie Maßnahmen um – mit einem Ansprechpartner statt Koordinationschaos.",
          canonical="/risikoradar/", active_nav="risikoradar", main=main,
          json_ld=page_schema(faq_page_schema(risikoradar_faq))))


BLINDSPOT_FAQ = [
    ("Was ist der Blindspot Quick Check?",
     "Der Blindspot Quick Check ist ein kostenloser Online-Selbsttest von Beraterium. In 10 bis 15 Fragen prüfen Sie, wo Ihr Unternehmen verwundbar ist — bei Schlüsselpersonen, Technik und operativen Abläufen. Die Auswertung erhalten Sie sofort, ohne Anmeldung."),
    ("Was ist der Unterschied zum Blindspot Check in Stufe 1 der Risikoanalyse?",
     "Der Quick Check hier auf der Seite ist eine vereinfachte Selbstprüfung: 15 ausgewählte Gefahrenbereiche, Ampelbewertung, ohne Gespräch. Stufe 1 der Risikoanalyse ist ein moderierter Prozess mit branchenspezifischem Fragenkatalog, Schadensszenarien in Euro, Eintrittswahrscheinlichkeit, Inventar und einem priorisierten Risikoportfolio — typischerweise in einem gemeinsamen Termin."),
    ("Wie lange dauert der Blindspot Quick Check?",
     "Etwa 10 Minuten. Sie beantworten je nach Zielgruppe 10 bis 15 kurze „Was passiert, wenn …“-Fragen und sehen die Auswertung direkt im Anschluss."),
    ("Ist der Blindspot Quick Check kostenlos?",
     "Ja, der Check ist vollständig kostenlos und ohne Registrierung nutzbar. Optional können Sie sich die Auswertung als PDF-Report per E-Mail zusenden lassen."),
    ("Ersetzt der Quick Check eine vollständige Risikoanalyse?",
     "Nein. Der Quick Check bildet einen Ausschnitt aus über 100 Gefahrenbereichen unseres 3-Ebenen-Gefahrenkatalogs ab. Ein gutes Ergebnis bedeutet nicht, dass alle Risiken ausgeschlossen sind — dafür gibt es die systematische Risikoanalyse Stufe 1 und 2 von Beraterium."),
    ("Für wen ist der Blindspot Quick Check gedacht?",
     "Für Solo-Selbstständige, Gründer und Startups sowie kleine und mittlere Unternehmen (KMU). Die Fragen passen sich Ihrer Auswahl an: Solo-Selbstständige beantworten 10 Fragen, Gründer und KMU je 15."),
    ("Was passiert mit meinen Antworten?",
     "Die Auswertung läuft direkt in Ihrem Browser. Persönliche Daten geben Sie nur an, wenn Sie den optionalen PDF-Report anfordern — dann gelten die Hinweise in unserer Datenschutzerklärung. IP-Adressen speichern wir nicht."),
]


def gen_tools_index() -> None:
    pre = "../"
    main = (
        hero(
            pre,
            "KOSTENLOSE TOOLS",
            "Tools: Risiken selbst prüfen — in Minuten statt Wochen",
            "Kompakte Selbsttests aus der Beraterium-Methode. Kein Ersatz für eine vollständige Risikoanalyse, aber ein ehrlicher erster Blick auf Ihre blinden Flecken.",
            compact=True,
        )
        + f"""
    <section class="brt-section" aria-labelledby="tools-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">SELBST TESTEN</p>
          <h2 id="tools-title" class="brt-h2">Welche Tools stehen zur Verfügung?</h2>
          <p class="brt-body">Aktuell ein Tool — weitere sind in Arbeit. Alle Tools basieren auf unserem 3-Ebenen-Gefahrenkatalog mit über 100 Gefahrenbereichen.</p>
        </header>
        <ul class="brt-cards-3col brt-stagger">
          <li class="brt-card brt-card--target brt-hover-lift">
            <h3 class="brt-h3">Blindspot Check</h3>
            <p class="brt-body">Der kostenlose Quick Check: 10–15 „Was passiert, wenn …“-Fragen zu Schlüsselpersonen, Technik und operativen Abläufen. Sofortige Auswertung mit Ampelstatus und konkreten ersten Schritten.</p>
            <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}tools/blindspot-check/">Blindspot Check starten →</a></p>
          </li>
          <li class="brt-card brt-card--target brt-hover-lift">
            <h3 class="brt-h3">RisikoRadar</h3>
            <p class="brt-body">Kein Selbsttest, aber der nächste Schritt: unser geschütztes Expertennetzwerk für die Umsetzung der Maßnahmen aus Ihrer Risikoanalyse.</p>
            <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}risikoradar/">RisikoRadar kennenlernen →</a></p>
          </li>
        </ul>
      </div>
    </section>"""
        + cta_band(pre, "Lieber direkt mit Experten sprechen?", "Im kostenlosen Erstgespräch klären wir, welche Risiken für Ihr Unternehmen wirklich relevant sind.")
    )
    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DE_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Tools", "item": f"{DE_SITE_URL}/tools/"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    write("tools/index.html", shell(
        depth=1,
        title="Tools – Kostenlose Risiko-Checks | Beraterium",
        description="Kostenlose Tools von Beraterium: Mit dem Blindspot Check erkennen Sie in 10 Minuten blinde Flecken und Unternehmensrisiken – sofort und ohne Anmeldung.",
        canonical="/tools/",
        active_nav="tools",
        main=main,
        json_ld=page_schema(breadcrumb_ld),
    ))


def gen_blindspot_check() -> None:
    pre = "../../"
    canonical = "/tools/blindspot-check/"
    config_json = blindspot_config_json(
        locale="de",
        submit_url="https://script.google.com/macros/s/AKfycbyPc0XZXUu9ok3-5rkXJNlAYbj5WsmzVq9vyuquKJmtjPKhgSfqXPDQMM63lC2OreIVIQ/exec",
        report_url="https://script.google.com/macros/s/AKfycbyPc0XZXUu9ok3-5rkXJNlAYbj5WsmzVq9vyuquKJmtjPKhgSfqXPDQMM63lC2OreIVIQ/exec",
        booking_url=f"{pre}kontakt/",
        privacy_url=f"{pre}datenschutz/",
    )
    main = (
        hero(
            pre,
            "KOSTENLOSER SELBSTTEST",
            "Blindspot Quick Check: Wo ist Ihr Unternehmen verwundbar?",
            "Beantworten Sie 10–15 kurze „Was passiert, wenn …“-Fragen und erhalten Sie sofort eine Auswertung: Ampelstatus, Risikoprofil nach Kategorien und konkrete erste Schritte für Ihre kritischsten Punkte. Der Quick Check ist die vereinfachte Online-Variante — Stufe 1 der Risikoanalyse geht deutlich tiefer.",
            compact=True,
            actions='<a class="brt-btn brt-btn--on-dark brt-btn--lg" href="#brt-blindspot">Check jetzt starten</a>',
        )
        + f"""
    <section class="brt-section" aria-labelledby="warum-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="warum-title" class="brt-h2">Warum ein Blindspot Quick Check?</h2>
          <p class="brt-body">Die meisten Unternehmen scheitern nicht an den Risiken, die sie kennen — sondern an denen, die sie nie betrachtet haben. Der Blindspot Quick Check macht diese blinden Flecken sichtbar: Er prüft 15 der über 100 Gefahrenbereiche aus unserem 3-Ebenen-Gefahrenkatalog, verteilt auf die Bereiche <strong>Mensch</strong>, <strong>Technik</strong> und <strong>Operatives</strong>.</p>
          <p class="brt-body">Jede Frage beschreibt ein konkretes Szenario. Sie bewerten, wie kritisch es für Sie wäre — und ob Sie bereits Maßnahmen vorbereitet haben. Daraus entsteht Ihr persönliches Risikoprofil mit Ampelstatus je Frage.</p>
        </div>
        {split_media_html(IMG_BLINDSPOT_WARUM, "Blindspot Check macht übersehene Unternehmensrisiken in den Bereichen Mensch, Technik und Operatives sichtbar", 2, contain=True)}
      </div>
    </section>
    <section id="check" class="brt-section brt-section--alt" aria-labelledby="check-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">INTERAKTIVER CHECK</p>
          <h2 id="check-title" class="brt-h2">Der Blindspot Quick Check</h2>
          <p class="brt-body brt-section__lede">Hier starten Sie den vereinfachten Selbsttest — online, in etwa 10 Minuten, ohne Termin. Er ersetzt nicht Stufe 1 der Risikoanalyse, gibt Ihnen aber einen ehrlichen ersten Blick auf typische blinde Flecken.</p>
        </header>
        <div id="brt-blindspot" class="bqc-widget brt-fade-up" aria-live="polite"></div>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="vergleich-title">
      <div class="brt-container brt-fade-up">
        <header class="brt-section__header">
          <p class="brt-tag">ZWEI FORMEN</p>
          <h2 id="vergleich-title" class="brt-h2">Quick Check vs. Risikoanalyse Stufe&nbsp;1</h2>
        </header>
        <ul class="brt-guarantee-duo brt-stagger">
          <li class="brt-card">
            <h3 class="brt-h3">Blindspot Quick Check (diese Seite)</h3>
            <ul class="brt-list">
              <li>Online-Selbsttest, sofort startbar</li>
              <li>10–15 ausgewählte Fragen aus dem Gefahrenkatalog</li>
              <li>Ampelbewertung und Kategorien-Profil</li>
              <li>Kein Gespräch, keine Branchenanpassung im Detail</li>
              <li>Kostenlos und ohne Anmeldung</li>
            </ul>
          </li>
          <li class="brt-card">
            <h3 class="brt-h3">Risikoanalyse Stufe&nbsp;1 (moderierter Prozess)</h3>
            <ul class="brt-list">
              <li>Gemeinsamer Termin mit Beraterium</li>
              <li>Branchenspezifischer Fragenkatalog (15–16 Gefahrenfelder)</li>
              <li>Schadensszenarien in Euro, Eintrittswahrscheinlichkeit, Inventar</li>
              <li>Priorisiertes Risikoportfolio statt Einzelthemen</li>
              <li>Grundlage für Stufe&nbsp;2 mit Maßnahmenplan</li>
            </ul>
            <p class="brt-section__cta"><a class="brt-btn brt-btn--outline" href="{pre}angebote/">Angebote &amp; Stufen →</a></p>
          </li>
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="methode-title">
      <div class="brt-container brt-fade-up">
        <header class="brt-section__header">
          <p class="brt-tag">GRUNDIDEE</p>
          <h2 id="methode-title" class="brt-h2">So funktioniert die Risikoanalyse — und was der Quick Check davon übernimmt</h2>
        </header>
        <p class="brt-body">Die Beraterium-Methode arbeitet mit einem strukturierten Gefahrenkatalog: Für jedes relevante Feld klären wir Leitfrage, Schadensszenario, möglichen Schaden in Euro, Eintrittswahrscheinlichkeit und <em>Inventar</em> — also, was Sie bereits haben, um das Risiko zu mindern. Daraus entsteht kein Sammelsurium einzelner Themen, sondern ein vergleichbares Risikoportfolio mit klaren Prioritäten.</p>
        <p class="brt-body">Der Blindspot Quick Check nutzt dieselbe Logik in stark vereinfachter Form: konkrete „Was passiert, wenn …“-Szenarien, Ihre Einschätzung der Kritikalität und ob Vorsorge existiert. Er zeigt Richtung und blinde Flecken — Stufe 1 und 2 der Risikoanalyse vertiefen und priorisieren systematisch über den gesamten Katalog. Mehr zur Methode: <a href="{pre}methode/">Beraterium-Methode</a>.</p>
      </div>
    </section>
    <section class="brt-section brt-section--narrow" aria-labelledby="grenzen-title">
      <div class="brt-container brt-fade-up">
        <h2 id="grenzen-title" class="brt-h2">Was der Quick Check leistet — und was nicht</h2>
        <p class="brt-body">Der Blindspot Quick Check ist ein Schnelltest, keine vollständige Risikoanalyse. Er betrachtet ausgewählte, besonders häufige Blindspots. Ein unauffälliges Ergebnis heißt nicht, dass in den übrigen Gefahrenbereichen keine Risiken bestehen. Wer es genau wissen will, geht den nächsten Schritt: <a href="{pre}angebote/">Risikoanalyse Stufe&nbsp;1</a> prüft alle relevanten Felder des Gefahrenkatalogs — inklusive Priorisierung; Stufe&nbsp;2 liefert den Maßnahmenplan.</p>
      </div>
    </section>""".replace("{pre}", pre)
        + faq_section_html(
            BLINDSPOT_FAQ,
            title="Häufige Fragen zum Blindspot Quick Check",
            section_id="faq",
            alt=True,
        )
        + cta_band(pre, "Rote Punkte im Ergebnis?", "Im kostenlosen Erstgespräch besprechen wir Ihre kritischsten Blindspots und was Sie zuerst angehen sollten.")
    )
    webapp_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Blindspot Check",
            "url": f"{DE_SITE_URL}{canonical}",
            "description": "Kostenloser Online-Selbsttest: In 10–15 Fragen prüfen Solo-Selbstständige, Gründer und KMU, wo ihr Unternehmen verwundbar ist. Sofortige Auswertung mit Ampelstatus und ersten Schritten.",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "browserRequirements": "Requires JavaScript",
            "inLanguage": "de",
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "provider": {"@id": f"{DE_SITE_URL}/#organization"},
        },
        ensure_ascii=False,
        indent=2,
    )
    breadcrumb_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{DE_SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Tools", "item": f"{DE_SITE_URL}/tools/"},
                {"@type": "ListItem", "position": 3, "name": "Blindspot Check", "item": f"{DE_SITE_URL}{canonical}"},
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
        title="Blindspot Check – Risiko-Selbsttest kostenlos | Beraterium",
        description="Blindspot Check: Prüfen Sie in 10 Minuten kostenlos, wo Ihr Unternehmen verwundbar ist. 10–15 Fragen, sofortige Auswertung, konkrete erste Schritte.",
        canonical=canonical,
        active_nav="tools/blindspot-check",
        main=main,
        json_ld=page_schema(faq_page_schema(BLINDSPOT_FAQ), webapp_ld, breadcrumb_ld),
        extra_css=extra_css,
        extra_scripts=extra_scripts,
    ))


# Nach Apps-Script-Deploy: URL hier eintragen (gleiche Web-App-URL wie EN).
RA_PREP_SUBMIT_URL = "https://script.google.com/macros/s/AKfycbzJDCClA9HKNK99xIjsvt9S9hCYDPtFd9nF4OlV3YPxqqzK9uOXyRz9AdLlXsEfy9gq/exec"


def gen_ra_prep() -> None:
    pre = "../../"
    canonical = "/tools/ra-vorbereitung/"
    config_json = ra_prep_config_json(
        locale="de",
        submit_url=RA_PREP_SUBMIT_URL,
        privacy_url=f"{pre}datenschutz/",
        terms_url=f"{pre}agb/",
    )
    main = (
        hero(
            pre,
            "RISIKOANALYSE",
            "Vorbereitung für Ihre Risikoanalyse",
            "Mit diesem Fragebogen bereiten Sie den Workshop bei Beraterium optimal vor. Ihre Angaben helfen uns, den Termin zielgerichtet zu planen — Dauer etwa 15–20 Minuten.",
            compact=True,
            actions='<a class="brt-btn brt-btn--on-dark brt-btn--lg" href="#brt-ra-prep">Fragebogen starten</a>',
        )
        + f"""
    <section class="brt-section" aria-labelledby="rap-warum-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <h2 id="rap-warum-title" class="brt-h2">Warum dieser Fragebogen?</h2>
          <p class="brt-body">Eine gute Risikoanalyse beginnt nicht im Termin — sondern mit dem richtigen Kontext. Ihre Antworten helfen uns, Schwerpunkte zu setzen, passende Beispiele vorzubereiten und den Workshop an Ihre Branche, Größe und aktuelle Lage anzupassen.</p>
          <p class="brt-body">Je konkreter Ihre Angaben, desto weniger Zeit verbringen wir mit Standardfragen — und desto mehr mit den Themen, die für Ihr Unternehmen wirklich zählen.</p>
          <ul class="rap-intro__meta" aria-label="Hinweise zum Fragebogen">
            <li><span class="rap-intro__meta-label">Dauer</span> 15–20&nbsp;Minuten</li>
            <li><span class="rap-intro__meta-label">Pflicht</span> Kontakt, Datenschutz, AGB</li>
            <li><span class="rap-intro__meta-label">Felder</span> nur ausfüllen, was zutrifft</li>
          </ul>
        </div>
        {split_media_html(IMG_RA_PREP_VORBEREITUNG, "Berater und Unternehmer bereiten gemeinsam eine Risikoanalyse vor — strukturierte Vorbereitung am Workshop-Tisch", 2, contain=True)}
      </div>
    </section>
    <section id="fragebogen" class="brt-section brt-section--alt" aria-labelledby="rap-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">FRAGEBOGEN</p>
          <h2 id="rap-title" class="brt-h2">Online ausfüllen</h2>
          <p class="brt-body brt-section__lede">Der Fragebogen führt Sie Schritt für Schritt durch fünf Themenbereiche. Sie können jederzeit zurückspringen und am Ende alles prüfen, bevor Sie absenden.</p>
        </header>
        <ul class="rap-topics brt-stagger" aria-label="Themenbereiche im Fragebogen">
          <li class="rap-topic brt-card">
            <p class="rap-topic__num" aria-hidden="true">01</p>
            <h3 class="rap-topic__title brt-h3">Unternehmen &amp; Organisation</h3>
            <p class="rap-topic__desc">Angebot, Rechtsform, Mitarbeitende, Standorte</p>
          </li>
          <li class="rap-topic brt-card">
            <p class="rap-topic__num" aria-hidden="true">02</p>
            <h3 class="rap-topic__title brt-h3">Tätigkeit &amp; Außenwirkung</h3>
            <p class="rap-topic__desc">Räumlichkeiten, Reichweite, Website, Social Media</p>
          </li>
          <li class="rap-topic brt-card">
            <p class="rap-topic__num" aria-hidden="true">03</p>
            <h3 class="rap-topic__title brt-h3">Ziele &amp; Schwerpunkte</h3>
            <p class="rap-topic__desc">Erwartungen, aktuelle Sorgen, kritische Bereiche</p>
          </li>
          <li class="rap-topic brt-card">
            <p class="rap-topic__num" aria-hidden="true">04</p>
            <h3 class="rap-topic__title brt-h3">Erfahrung &amp; Vorsorge</h3>
            <p class="rap-topic__desc">Störungen, Schutzmaßnahmen, Szenarien</p>
          </li>
          <li class="rap-topic brt-card">
            <p class="rap-topic__num" aria-hidden="true">05</p>
            <h3 class="rap-topic__title brt-h3">Workshop</h3>
            <p class="rap-topic__desc">Teilnehmende, Ansprechpartner, Besonderheiten</p>
          </li>
        </ul>
        <div id="brt-ra-prep" class="rap-widget brt-fade-up" aria-live="polite"></div>
      </div>
    </section>"""
    )
    extra_css = f'\n  <link rel="stylesheet" href="{pre}css/brt-ra-prep.css?v={BRT_ASSET_VERSION}">'
    extra_scripts = (
        f'\n<script type="application/json" id="brt-ra-prep-config">{config_json}</script>'
        f'\n<script src="{pre}js/brt-ra-prep.js?v={BRT_ASSET_VERSION}"></script>'
    )
    write("tools/ra-vorbereitung/index.html", shell(
        depth=2,
        title="RA-Vorbereitung – Fragebogen | Beraterium",
        description="Vorbereitungsfragebogen für Ihre Risikoanalyse bei Beraterium: Unternehmensdaten, Ziele und Workshop-Vorbereitung in 15–20 Minuten.",
        canonical=canonical,
        active_nav=None,
        main=main,
        noindex=True,
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
            <p class="brt-body">Noch keine veröffentlichten Artikel. Schauen Sie bald wieder vorbei.</p>
          </div>
        </li>"""
        ]
    main = (
        hero(
            pre,
            "BERATERIUM-BLOG",
            "Risiko verständlich gemacht",
            "Praxiswissen zu Risikomanagement, Unternehmensrisiken, HR und Führung – ohne Berater-Kauderwelsch. Für Menschen, die ihr Unternehmen sicher in die Zukunft führen wollen.",
            compact=True,
        )
        + f"""
    <section class="brt-section" aria-labelledby="blog-grid">
      <div class="brt-container">
        <header class="brt-section__header brt-section__header--row brt-fade-up">
          <div>
            <h2 id="blog-grid" class="brt-h2">Alle Artikel</h2>
            <p class="brt-body">{len(posts)} Beiträge zu Risikomanagement, Führung und Unternehmenspraxis.</p>
          </div>
        </header>
        <nav class="brt-blog-filters" aria-label="Kategorien">
          {blog_filters_html()}
        </nav>
        <ul class="brt-blog-grid brt-stagger" id="blog-grid-list">
{chr(10).join(cards)}
        </ul>
      </div>
    </section>
    <section class="brt-section brt-section--alt" aria-labelledby="newsletter-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <h2 id="newsletter-title" class="brt-h3">Kein Risiko-Wissen verpassen</h2>
        <p class="brt-body">Ein kompakter Impuls pro Monat – praxisnah, kostenlos, jederzeit abbestellbar.</p>
        <form class="brt-form" action="#" method="post" style="max-width: 28rem; margin-inline: auto;">
          <label>E-Mail
            <input type="email" name="email" required placeholder="ihre@email.de" autocomplete="email">
          </label>
          <button class="brt-btn" type="submit">Anmelden</button>
          <p class="brt-meta">Mit der Anmeldung stimmen Sie der Verarbeitung gemäß unserer <a href="{pre}datenschutz/">Datenschutzerklärung</a> zu.</p>
        </form>
      </div>
    </section>"""
    )
    write(
        "blog/index.html",
        shell(
            depth=1,
            title="Blog – Risikomanagement & Mittelstand | Beraterium",
            description="Praxiswissen zu Risikomanagement, Unternehmensrisiken, HR und Führung – für Startups, KMU und Solo-Selbstständige. Klar, ehrlich, sofort anwendbar.",
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
            f'<figure class="brt-article__hero-media">{hero_img}{ki_image_label_html()}</figure>'
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
            f"https://www.beraterium.de/blog/{post.slug}/",
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
    <button type="button" class="brt-article__back-top" aria-label="Nach oben scrollen" data-article-back-top hidden>
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
        <h2 id="related-posts" class="brt-h2">Weitere Artikel</h2>
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
          <a class="brt-btn brt-btn--ghost" href="{pre}team/">Unser Team →</a>
        </div>
      </div>
    </section>"""
        main = f"""
    <article class="brt-article" data-article>
{sticky_bar_block}
      <div class="brt-container brt-article__hero-split brt-fade-up" data-article-hero>
        <div class="brt-article__hero-copy">
          <a class="brt-skip-link brt-skip-link--article" href="#article-body">Zum Artikeltext springen</a>
          <h1 class="brt-h1 brt-article__title">{escape(post.title)}</h1>
          <p class="brt-article__meta brt-meta">
            <span class="brt-article__category">{escape(post.category)}</span> · {author_meta} · <time datetime="{post.date.isoformat()}">{format_date_de(post.date)}</time> · ca. {post.reading_time_min} Min. Lesezeit
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
        <h2 id="article-cta" class="brt-h2 brt-h2--on-dark">Risiken im eigenen Unternehmen klären?</h2>
        <p class="brt-body brt-body--on-dark">Buchen Sie ein kostenloses Erstgespräch – 30 Minuten, unverbindlich.</p>
        <a class="brt-btn brt-btn--on-dark" href="{pre}kontakt/">Erstgespräch buchen</a>
      </div>
    </section>
{related_block}"""
        json_ld_blocks = [blog_posting_schema(post, author)]
        if post.faq:
            json_ld_blocks.append(faq_page_schema(post.faq))
        json_ld = page_schema(*json_ld_blocks)
        og_image = blog_hero_public_url(post.hero_image) if post.hero_image else ""
        write(
            f"blog/{post.slug}/index.html",
            shell(
                depth=2,
                title=blog_shell_title(post),
                description=blog_meta_description(post.excerpt),
                canonical=f"/blog/{post.slug}/",
                active_nav="blog",
                main=main,
                json_ld=json_ld,
                og_type="article",
                og_image=og_image,
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
        legacy_end = '        <a class="brt-btn brt-btn--outline" href="team/">Mehr über das Team →</a>\n      </p>\n    </div>\n  </section>'
        if legacy_start not in html or legacy_end not in html:
            return
        before = html.split(legacy_start)[0]
        rest = html.split(legacy_start)[1]
        after = rest.split(legacy_end, 1)[1]
        path.write_text(before + section + after, encoding="utf-8")
    print("  updated index.html home team")




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
    print("  updated index.html guarantee avatars")

def gen_home_analytics() -> None:
    """Home index.html: GA4-Snippet nach CookieYes synchronisieren."""
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


def gen_home_scripts() -> None:
    """Home index.html: Analytics + Site + Hero JS synchronisieren."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    block = (
        f'<script src="js/brt-analytics.js?v={BRT_ASSET_VERSION}"></script>\n'
        f'<script src="js/brt-site.js?v={BRT_ASSET_VERSION}"></script>\n'
        f'<script src="js/brt-hero.js?v={BRT_ASSET_VERSION}"></script>\n'
    )
    start = '<script src="js/brt-site.js?v='
    i = html.find(start)
    if i < 0:
        print("  skip index.html home scripts (anchor not found)")
        return
    body = html.find("</body>", i)
    if body < 0:
        print("  skip index.html home scripts (body end not found)")
        return
    path.write_text(html[:i] + block + html[body:], encoding="utf-8")
    print("  updated index.html home scripts")


def gen_home_nav() -> None:
    """Home index.html: Hauptnavigation aus nav_html() synchronisieren."""
    path = SITE / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    start = '<nav id="site-nav" class="site-header__nav" aria-label="Primäre Navigation">\n      <ul>\n'
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
    """Home index.html: Teaser fuer den Blindspot Check vor dem Blog-Teaser."""
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
        <p class="brt-tag">Kostenloser Selbsttest</p>
        <h2 id="tools-teaser-title" class="brt-h2">Wo ist Ihr Unternehmen verwundbar? Der Blindspot Check zeigt es in 10 Minuten.</h2>
        <p class="brt-body">10 bis 15 kurze „Was passiert, wenn …“-Fragen zu Schlüsselpersonen, Technik und operativen Abläufen. Sofortige Auswertung mit Ampelstatus und ersten Schritten, ohne Anmeldung.</p>
        <a class="brt-btn" href="tools/blindspot-check/">Blindspot Check starten →</a>
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
          <p class="brt-tag">Einblicke</p>
          <h2 id="blog-title" class="brt-h2">Experten-Einblicke von Beraterium</h2>
          <p class="brt-body">Kurze, praxisnahe Artikel zu Risiko, Führung und Entscheidungen — geschrieben vom Beraterium-Team für Gründer, KMU und Selbstständige.</p>
        </div>
        <a class="brt-btn brt-btn--outline" href="blog/">Alle Artikel →</a>
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


def gen_kontakt() -> None:
    pre = "../"
    main = (
        hero(pre, "KONTAKT", "Lassen Sie uns über Ihre Risiken sprechen",
             "30 Minuten, kostenlos, unverbindlich. Sie gehen mit echtem Wissen raus – egal, wie Sie sich danach entscheiden.",
             compact=True)
        + f"""
    <section class="brt-section brt-section--booking" aria-labelledby="contact-title">
      <div class="brt-container brt-contact-booking brt-fade-up">
        <div class="brt-contact-booking__head">
          <div class="brt-contact-booking__intro">
            <div class="brt-contact-booking__lead">
              <p class="brt-tag">30 Minuten · kostenlos · unverbindlich</p>
              <h2 id="contact-title" class="brt-h2">Ihr kostenloses Erstgespräch</h2>
              <p class="brt-body">Wählen Sie direkt einen Termin – wir nehmen uns Zeit für Ihre Situation, nicht für Verkaufsargumente.</p>
            </div>
            <div class="brt-contact-expect">
              <h3 class="brt-contact-expect__title">Was Sie erwartet</h3>
              <ul class="brt-contact-expect__points">
                <li class="brt-contact-expect__point">
                  <strong>Kein Verkaufsgespräch</strong>
                  <span>Kein Pitch – wir erklären, was wir tun und wie unsere Methode funktioniert.</span>
                </li>
                <li class="brt-contact-expect__point">
                  <strong>Praxistipps inklusive</strong>
                  <span>Konkrete Hinweise, mit denen Sie direkt mit Eigenarbeit und Recherche starten können.</span>
                </li>
                <li class="brt-contact-expect__point">
                  <strong>Selbst umsetzen</strong>
                  <span>Sie gehen mit genug Klarheit raus, um erste Schritte eigenständig anzugehen.</span>
                </li>
                <li class="brt-contact-expect__point">
                  <strong>Unterstützung optional</strong>
                  <span>Wenn Sie Begleitung brauchen, besprechen wir die weiteren Schritte gemeinsam – wie unten beschrieben.</span>
                </li>
              </ul>
            </div>
          </div>
          <aside class="brt-contact-aside">
            <p class="brt-contact-aside__label">Alternativ</p>
            <h3 class="brt-h3">Direkter Draht</h3>
            <p class="brt-body">Lieber schriftlich? Nutzen Sie unser Kontaktformular – Antwort i. d. R. innerhalb eines Werktags.</p>
            <a class="brt-btn brt-btn--outline" href="{pre}kontaktformular/">Zum Kontaktformular</a>
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
          <p class="brt-tag">SO LÄUFT ES AB</p>
          <h2 id="steps-title" class="brt-h2">Drei Schritte bis zur Klarheit</h2>
        </header>
        <ul class="brt-step-cards brt-stagger">
          <li class="brt-step-card"><span class="brt-step-card__num">Schritt 1</span><h3 class="brt-h3">Termin wählen</h3><p class="brt-body">Sie buchen einen 30-Minuten-Slot, der Ihnen passt.</p></li>
          <li class="brt-step-card"><span class="brt-step-card__num">Schritt 2</span><h3 class="brt-h3">Gespräch</h3><p class="brt-body">Wir zeigen Ihnen die Methode und gehen auf Ihre Situation ein. Kein Verkaufsdruck.</p></li>
          <li class="brt-step-card"><span class="brt-step-card__num">Schritt 3</span><h3 class="brt-h3">Sie entscheiden</h3><p class="brt-body">Mit DIY-Anleitung im Gepäck entscheiden Sie in Ruhe, ob und wie wir zusammenarbeiten.</p></li>
        </ul>
      </div>
    </section>
    <section class="brt-section" aria-label="Vertrauen">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-body">Kein Sales-Pitch. Kostenlos. Und falls wir später zusammenarbeiten: mit doppelter Garantie – <a href="{pre}relevanz-garantie/">Relevanz</a> und <a href="{pre}nutzen-garantie/">Nutzen</a>, sonst Geld zurück.</p>
      </div>
    </section>"""
        + faq_section_html([
            ("Was kostet das Erstgespräch?", "Nichts. 30 Minuten, kostenlos und unverbindlich — kein Verkaufsgespräch."),
            ("Wie lange dauert das Erstgespräch?", "Ca. 30 Minuten. Sie bekommen die Methode erklärt und gehen mit konkreten ersten Schritten raus."),
            ("Muss ich mich danach entscheiden?", "Nein. Sie entscheiden in Ruhe — mit einer DIY-Anleitung im Gepäck, egal wie Sie sich entscheiden."),
        ], title="Häufige Fragen zum Erstgespräch", section_id="faq", alt=True)
    )
    kontakt_faq = [
        ("Was kostet das Erstgespräch?", "Nichts. 30 Minuten, kostenlos und unverbindlich — kein Verkaufsgespräch."),
        ("Wie lange dauert das Erstgespräch?", "Ca. 30 Minuten. Sie bekommen die Methode erklärt und gehen mit konkreten ersten Schritten raus."),
        ("Muss ich mich danach entscheiden?", "Nein. Sie entscheiden in Ruhe — mit einer DIY-Anleitung im Gepäck, egal wie Sie sich entscheiden."),
    ]
    write(
        "kontakt/index.html",
        shell(
            depth=1,
            title="Kostenloses Erstgespräch buchen | Beraterium",
            description="30 Minuten, kostenlos, kein Sales-Pitch: Buchen Sie Ihr Erstgespräch mit Till und Peter und machen Sie Ihre größten Risiken sichtbar.",
            canonical="/kontakt/",
            active_nav=None,
            main=main,
            json_ld=page_schema(faq_page_schema(kontakt_faq)),
        ).replace(
            f'<script src="{pre}js/brt-analytics.js?v={BRT_ASSET_VERSION}"></script>\n<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
            f'<script src="{pre}js/brt-analytics.js?v={BRT_ASSET_VERSION}"></script>\n<script src="https://assets.calendly.com/assets/external/widget.js" type="text/javascript" async></script>\n<script src="{pre}js/brt-site.js?v={BRT_ASSET_VERSION}"></script>',
        ),
    )


def gen_kontaktformular() -> None:
    pre = "../"
    main = f"""
    <section class="brt-page-hero brt-page-hero--dark brt-page-hero--compact" aria-labelledby="page-hero-title">
      <div class="brt-container">
        <div class="brt-fade-up">
          <p class="brt-tag">KONTAKT</p>
          <h1 id="page-hero-title" class="brt-h1">Kontaktformular</h1>
          <p class="brt-lead brt-lead--on-dark">Schreiben Sie uns – wir melden uns in der Regel innerhalb eines Werktags.</p>
        </div>
      </div>
    </section>
    <section class="brt-section" aria-labelledby="form-title">
      <div class="brt-container brt-contact-form-wrap brt-fade-up">
        <header class="brt-section__header">
          <h2 id="form-title" class="brt-h2">Kontaktieren Sie uns direkt</h2>
          <p class="brt-body">Kontaktieren Sie uns direkt über unser Kontaktformular. Für ein kostenloses Erstgespräch können Sie alternativ direkt einen Termin buchen.</p>
          <p class="brt-meta"><a href="{pre}kontakt/">Zum Termin buchen →</a></p>
        </header>
        <form class="brt-form brt-form--contact" action="https://formsubmit.co/till.blania@beraterium.de" method="POST" novalidate>
          <input type="hidden" name="_subject" value="Neue Kontaktanfrage – Beraterium">
          <input type="hidden" name="_next" value="https://www.beraterium.de/danke/">
          <input type="hidden" name="_template" value="table">
          <input type="text" name="_honey" class="brt-form__honey" tabindex="-1" autocomplete="off" aria-hidden="true">
          <label>Name *
            <input type="text" name="name" required autocomplete="name">
          </label>
          <label>E-Mail *
            <input type="email" name="email" required autocomplete="email">
          </label>
          <label>Unternehmen
            <input type="text" name="company" autocomplete="organization">
          </label>
          <label>Ich bin …
            <select name="type">
              <option value="">Bitte wählen</option>
              <option>Startup</option>
              <option>KMU</option>
              <option>Solo-Selbstständige</option>
              <option>Sonstiges</option>
            </select>
          </label>
          <label>Ihre Nachricht *
            <textarea name="message" required placeholder="Worum geht es?"></textarea>
          </label>
          <fieldset class="brt-form__legal">
            <legend class="brt-form__legal-legend">Bestätigungen</legend>
            <div class="brt-form__check-group">
              <label class="brt-form__check" for="agb_accepted">
                <input type="checkbox" id="agb_accepted" name="agb_accepted" value="Ja">
                <span>Ich habe die <a href="{pre}agb/">AGB</a> gelesen und akzeptiere sie.</span>
              </label>
              <p class="brt-form__error" id="agb-error" role="alert" hidden>Bitte bestätigen Sie die AGB.</p>
            </div>
            <div class="brt-form__check-group">
              <label class="brt-form__check" for="privacy_accepted">
                <input type="checkbox" id="privacy_accepted" name="privacy_accepted" value="Ja">
                <span>Ich habe die <a href="{pre}datenschutz/">Datenschutzerklärung</a> gelesen und stimme der Verarbeitung meiner Daten&nbsp;zu.</span>
              </label>
              <p class="brt-form__error" id="privacy-error" role="alert" hidden>Bitte bestätigen Sie die Datenschutzerklärung.</p>
            </div>
          </fieldset>
          <button class="brt-btn" type="submit">Nachricht senden</button>
          <p class="brt-meta">Antwort i. d. R. innerhalb eines Werktags.</p>
        </form>
      </div>
    </section>"""
    write(
        "kontaktformular/index.html",
        shell(
            depth=1,
            title="Kontaktformular | Beraterium",
            description="Kontaktieren Sie Beraterium direkt über unser Kontaktformular. Wir melden uns in der Regel innerhalb eines Werktags.",
            canonical="/kontaktformular/",
            active_nav=None,
            main=main,
        ),
    )


def gen_impressum() -> None:
    sections = (SITE / "_content" / "impressum_sections.html").read_text()
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">Impressum</h1>
{sections}
      </div>
    </section>"""
    write(
        "impressum/index.html",
        shell(
            depth=1,
            title="Impressum | Beraterium",
            description="Impressum und Anbieterkennzeichnung der Beraterium GbR — Kontakt, Umsatzsteuer-ID und rechtliche Hinweise.",
            canonical="/impressum/",
            active_nav=None,
            main=main,
        ),
    )


def gen_datenschutz() -> None:
    sections = (SITE / "_content" / "datenschutz_sections.html").read_text()
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">Datenschutzerklärung</h1>
{sections}
      </div>
    </section>"""
    write(
        "datenschutz/index.html",
        shell(
            depth=1,
            title="Datenschutzerklärung | Beraterium",
            description="Informationen zur Verarbeitung personenbezogener Daten auf beraterium.de — DSGVO-konform, Stand 2026.",
            canonical="/datenschutz/",
            active_nav=None,
            main=main,
        ),
    )


def gen_agb() -> None:
    sections = (SITE / "_content" / "agb_sections.html").read_text()
    main = f"""
    <section class="brt-section" aria-labelledby="legal-title">
      <div class="brt-container brt-legal">
        <h1 id="legal-title" class="brt-h2">Allgemeine Geschäftsbedingungen (AGB)</h1>
{sections}
      </div>
    </section>"""
    write(
        "agb/index.html",
        shell(
            depth=1,
            title="Allgemeine Geschäftsbedingungen | Beraterium",
            description="Allgemeine Geschäftsbedingungen von Beraterium GbR für Beratungsleistungen in Risikomanagement, HR, Management und Prozessoptimierung.",
            canonical="/agb/",
            active_nav=None,
            main=main,
        ),
    )


def gen_barrierefreiheit() -> None:
    main = """
    <section class="brt-section" aria-labelledby="a11y-title">
      <div class="brt-container brt-legal">
        <h1 id="a11y-title" class="brt-h2">Barrierefreiheitserklärung</h1>
        <p>Wir arbeiten kontinuierlich daran, die Inhalte und Funktionen auf beraterium.de barrierefrei zugänglich zu machen und orientieren uns dabei an den Anforderungen der WCAG 2.1 auf Konformitätsstufe AA.</p>
        <h2 class="brt-h3">Stand der Vereinbarkeit</h2>
        <p>Diese Website ist teilweise mit den Anforderungen der WCAG 2.1 AA vereinbar. Es bestehen aktuell noch einzelne Einschränkungen, die wir sukzessive beheben.</p>
        <h2 class="brt-h3">Erstellungs- und Prüfverfahren</h2>
        <p>Die Bewertung basiert auf einer Kombination aus automatisierten Tests (eigene Prüfstrecke mit Playwright + axe-core) und manuellen Tastatur-, Fokus- und Strukturprüfungen auf repräsentativen Seitentypen.</p>
        <h2 class="brt-h3">Bekannte Einschränkungen</h2>
        <ul>
          <li>Einzelne ältere Inhaltsblöcke können noch unvollständige semantische Struktur oder kontrastkritische Details enthalten.</li>
          <li>Eingebundene Drittanbieter-Inhalte (z. B. externe Widgets) liegen nur teilweise in unserem direkten Einflussbereich.</li>
        </ul>
        <h2 class="brt-h3">Feedback und Kontakt</h2>
        <p>Wenn Sie auf Barrieren stoßen oder Hinweise zur Verbesserung haben, schreiben Sie uns bitte an <a href="mailto:info@beraterium.de">info@beraterium.de</a> oder nutzen Sie das <a href="../kontaktformular/">Kontaktformular</a>.</p>
        <p>Wir prüfen Ihr Anliegen und melden uns so schnell wie möglich zurück.</p>
        <h2 class="brt-h3">Stand dieser Erklärung</h2>
        <p>Diese Erklärung wurde am 26.06.2026 erstellt und wird regelmäßig aktualisiert.</p>
      </div>
    </section>"""
    write(
        "barrierefreiheit/index.html",
        shell(
            depth=1,
            title="Barrierefreiheitserklärung | Beraterium",
            description="Informationen zur digitalen Barrierefreiheit auf beraterium.de, unserem Prüfverfahren sowie Kontaktmöglichkeiten bei Barrieren.",
            canonical="/barrierefreiheit/",
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
        <h1 id="not-found-title" class="brt-h1">Diese Seite gibt es nicht (mehr)</h1>
        <p class="brt-lead brt-lead--on-dark">Vielleicht hat sich die Adresse geändert oder ein Tippfehler eingeschlichen. Hier kommen Sie weiter:</p>
        <div class="brt-page-hero__actions" style="justify-content: center;">
          <a class="brt-btn brt-btn--on-dark" href="./">Zur Startseite</a>
          <a class="brt-btn brt-btn--outline" href="angebote/" style="color:#fff;border-color:rgba(255,255,255,.5);">Angebote</a>
          <a class="brt-btn brt-btn--outline" href="methode/" style="color:#fff;border-color:rgba(255,255,255,.5);">Methode</a>
          <a class="brt-btn brt-btn--outline" href="kontakt/" style="color:#fff;border-color:rgba(255,255,255,.5);">Kontakt</a>
        </div>
      </div>
    </section>"""
    write("404.html", shell(depth=0, title="Seite nicht gefunden | Beraterium", description="Die angeforderte Seite existiert nicht.",
          canonical="/404", active_nav=None, main=main, noindex=True))


def gen_danke() -> None:
    pre = "../"
    main = f"""
    <section class="brt-section" aria-labelledby="danke-title">
      <div class="brt-container brt-centered-cta brt-fade-up">
        <p class="brt-tag">DANKE</p>
        <h1 id="danke-title" class="brt-h2">Danke – wir freuen uns auf das Gespräch!</h1>
        <p class="brt-body">Ihre Nachricht ist angekommen. Till oder Peter meldet sich in der Regel innerhalb eines Werktags bei Ihnen.</p>
        <ul class="brt-step-cards" style="margin-top: var(--space-8); text-align: left;">
          <li class="brt-step-card"><p class="brt-body">Schauen Sie sich in der Zwischenzeit unsere <a href="{pre}methode/">Methode</a> an.</p></li>
        </ul>
        <p class="brt-section__cta">
          <a class="brt-btn brt-btn--outline" href="{pre}">Zurück zur Startseite</a>
        </p>
      </div>
    </section>"""
    write("danke/index.html", shell(depth=1, title="Danke – wir melden uns | Beraterium",
          description="Vielen Dank für Ihre Anfrage. Wir melden uns in Kürze bei Ihnen.", canonical="/danke/",
          active_nav=None, main=main, noindex=True))


if __name__ == "__main__":
    print("Generating pages...")
    gen_ueber_uns()
    gen_team()
    gen_mission_vision()
    gen_methode()
    gen_nutzen_garantie()
    gen_relevanz_garantie()
    gen_angebote()
    gen_preise()
    gen_international_index(locale="en")
    for _int_cfg in en_offer_configs():
        gen_international_offer(_int_cfg, locale="en")
    gen_all_international_stages(locale="en")
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
    blindspot_selfcheck()
    ra_prep_selfcheck()
    gen_tools_index()
    gen_blindspot_check()
    gen_ra_prep()
    gen_blog()
    gen_blog_singles()
    gen_home_analyse()
    gen_home_team()
    gen_home_guarantee_avatars()
    gen_home_blog_teaser()
    gen_home_nav()
    gen_home_analytics()
    gen_home_scripts()
    gen_home_tools_teaser()
    gen_home_footer()
    gen_kontakt()
    gen_kontaktformular()
    gen_impressum()
    gen_datenschutz()
    gen_agb()
    gen_barrierefreiheit()
    gen_danke()
    gen_404()
    write_sitemap()
    from scripts.gen_legacy_redirects import main as gen_legacy_htaccess

    gen_legacy_htaccess()
    print("Done.")
