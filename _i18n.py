"""Cross-language routing and hreflang mapping for Beraterium DE/EN sites."""
from __future__ import annotations

DE_SITE_URL = "https://www.beraterium.de"
EN_SITE_URL = "https://en.beraterium.de"

# Static page slug mapping: DE path (no leading/trailing slash) -> EN path
STATIC_ROUTE_MAP: dict[str, str] = {
    "": "",
    "ueber-uns": "about",
    "team": "team",
    "mission-vision": "mission-vision",
    "methode": "method",
    "angebote": "services",
    "angebote/startups": "services/startups",
    "angebote/kmu": "services/smb",
    "angebote/solo": "services/solo",
    "risikoradar": "risk-radar",
    "blog": "blog",
    "kontakt": "contact",
    "kontaktformular": "contact-form",
    "impressum": "legal-notice",
    "datenschutz": "privacy",
    "agb": "terms",
    "danke": "thank-you",
    "404": "404",
}

# Blog slug mapping: DE slug -> EN slug
BLOG_SLUG_MAP: dict[str, str] = {
    "auslandsgrundung-risiken-standortwahl-strategie": "international-expansion-risks-location-strategy",
    "emotionale-fuehrung-kmu-eisbergmodell-risiko": "emotional-leadership-smb-iceberg-model-risk",
    "externe-risikofaktoren-fur-kmu-8-einflussfaktoren-die-ihr-unternehmen-bedrohen": "external-risk-factors-smb-8-threats",
    "familiennachfolge-generationskonflikt-risiko-nach-uebergabe": "family-succession-generational-conflict-risk",
    "geistiges-eigentum-patentschutz-praxistipps": "intellectual-property-patent-protection-tips",
    "gesundheit-gruender-risikomanagement-ernaehrung": "founder-health-risk-management-nutrition",
    "iran-konflikt-oelpreis-lieferketten-unternehmen": "iran-conflict-oil-price-supply-chains",
    "ki-und-risikomanagement-mensch-im-mittelpunkt": "ai-and-risk-management-people-first",
    "mensch-vertrauen-risikomanagement": "people-trust-risk-management",
    "mitarbeitersensibilisierung-risikobewusste-kultur": "employee-awareness-risk-conscious-culture",
    "mittelstand-fokus-risikomanagement": "mid-market-focus-risk-management",
    "risiken-bewusst-eingehen": "taking-risks-consciously",
    "risikoradar-community-experten-unternehmer": "risk-radar-community-experts-entrepreneurs",
    "risk-radar-episode-1-who-is-beraterium": "risk-radar-episode-1-who-is-beraterium",
    "sicherheit-unternehmen-risikomanagement-kmu": "business-security-risk-management-smb",
    "startup-fehler-vermeiden-risikomanagement": "startup-mistakes-avoid-risk-management",
    "ubernimm-die-kontrolle-uber-deine-risiken-bevor-sie-dich-kontrollieren": "take-control-of-your-risks-before-they-control-you",
    "warum-mitarbeiter-riskante-entscheidungen-treffen": "why-employees-make-risky-decisions",
    "what-is-risk-management": "what-is-risk-management",
}

EN_STATIC_ROUTE_MAP: dict[str, str] = {v: k for k, v in STATIC_ROUTE_MAP.items()}
EN_BLOG_SLUG_MAP: dict[str, str] = {v: k for k, v in BLOG_SLUG_MAP.items()}


def _normalize_route(route: str) -> str:
    return route.strip("/")


def de_to_en_route(de_route: str) -> str:
    key = _normalize_route(de_route)
    if key.startswith("blog/"):
        slug = key.split("/", 1)[1]
        en_slug = BLOG_SLUG_MAP.get(slug, slug)
        return f"blog/{en_slug}"
    return STATIC_ROUTE_MAP.get(key, key)


def en_to_de_route(en_route: str) -> str:
    key = _normalize_route(en_route)
    if key.startswith("blog/"):
        slug = key.split("/", 1)[1]
        de_slug = EN_BLOG_SLUG_MAP.get(slug, slug)
        return f"blog/{de_slug}"
    return EN_STATIC_ROUTE_MAP.get(key, key)


def alternate_url(canonical: str, *, from_locale: str, to_locale: str) -> str:
    """Return the URL on to_locale for a page identified by canonical on from_locale."""
    route = _normalize_route(canonical)
    if to_locale == "de":
        base = DE_SITE_URL
        if from_locale == "en":
            if route.startswith("blog/"):
                slug = route.split("/", 1)[1]
                path = f"blog/{EN_BLOG_SLUG_MAP.get(slug, slug)}"
            else:
                path = EN_STATIC_ROUTE_MAP.get(route, route)
        else:
            path = route
    else:
        base = EN_SITE_URL
        if from_locale == "de":
            if route.startswith("blog/"):
                slug = route.split("/", 1)[1]
                path = f"blog/{BLOG_SLUG_MAP.get(slug, slug)}"
            else:
                path = STATIC_ROUTE_MAP.get(route, route)
        else:
            path = route
    if not path or path == "404":
        return f"{base}/"
    return f"{base}/{path}/"


def hreflang_links(canonical: str, *, current_locale: str) -> str:
    """Generate reciprocal hreflang link tags."""
    de_url = alternate_url(canonical, from_locale=current_locale, to_locale="de")
    en_url = alternate_url(canonical, from_locale=current_locale, to_locale="en")
    x_default = de_url
    return (
        f'\n  <link rel="alternate" hreflang="de" href="{de_url}">'
        f'\n  <link rel="alternate" hreflang="en" href="{en_url}">'
        f'\n  <link rel="alternate" hreflang="x-default" href="{x_default}">'
    )


def language_switcher_html(*, current_locale: str, canonical: str, depth: int) -> str:
    """Compact DE | EN switcher for header/footer."""
    if current_locale == "en":
        other_locale = "de"
        other_url = f"{DE_SITE_URL}/"
    else:
        other_locale = "en"
        other_url = alternate_url(canonical, from_locale=current_locale, to_locale="en")
    current_label = "DE" if current_locale == "de" else "EN"
    other_label = "EN" if current_locale == "de" else "DE"
    return (
        f'<div class="site-header__lang" role="navigation" aria-label="Language">'
        f'<span class="site-header__lang-current" aria-current="true">{current_label}</span>'
        f'<span class="site-header__lang-sep" aria-hidden="true">|</span>'
        f'<a class="site-header__lang-link" href="{other_url}" hreflang="{other_locale}">{other_label}</a>'
        f"</div>"
    )
