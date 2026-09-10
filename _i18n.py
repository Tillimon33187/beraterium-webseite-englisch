"""Cross-language routing and hreflang mapping for Beraterium DE/EN/RU sites."""
from __future__ import annotations

from _internationale_stufen_detail import build_i18n_stage_routes

DE_SITE_URL = "https://www.beraterium.de"
EN_SITE_URL = "https://www.beraterium.com"

_STATIC_STAGE_ROUTES, _RU_STAGE_ROUTES, _ = build_i18n_stage_routes()

STATIC_ROUTE_MAP: dict[str, str] = {
    "": "",
    "ueber-uns": "about",
    "team": "team",
    "mission-vision": "mission-vision",
    "methode": "method",
    "nutzen-garantie": "benefit-guarantee",
    "relevanz-garantie": "relevance-guarantee",
    "angebote": "services",
    "angebote/startups": "services/startups",
    "angebote/kmu": "services/smb",
    "angebote/solo": "services/solo",
    "preise": "pricing",
    "schulungen": "training",
    "internationale-angebote": "international-services",
    "internationale-angebote/gruendung-deutschland": "international-services/founding-germany",
    "internationale-angebote/leben-arbeiten-deutschland": "international-services/living-working-germany",
    "internationale-angebote/business-turnaround": "international-services/business-turnaround",
    "internationale-angebote/expansion-tochtergesellschaft": "international-services/expansion-subsidiary",
    "schulungen/risikoexperte": "training/risk-expert",
    "schulungen/risk-awareness-kultur": "training/risk-awareness-culture",
    "schulungen/risikobewusster-manager": "training/risk-aware-manager",
    "schulungen/risikomanagement-praktisch": "training/practical-risk-management",
    "schulungen/innovationsmanagement": "training/innovation-management",
    "schulungen/feedbackkultur": "training/feedback-culture",
    "schulungen/kulturelles-management": "training/cultural-management",
    "risikoradar": "risk-radar",
    "loesungen/nis2": "solutions/nis2",
    "loesungen/nachfolge": "solutions/succession",
    "loesungen/cyberangriff": "solutions/cyber-attack",
    "loesungen/selbststaendig-absichern": "solutions/self-employed-protection",
    "loesungen/schluesselperson-risiko": "solutions/key-person-risk",
    "loesungen/investor-due-diligence": "solutions/investor-due-diligence",
    "loesungen/risikoanalyse-startup": "solutions/risk-analysis-startup",
    "loesungen/risikoanalyse-kmu": "solutions/risk-analysis-smb",
    "loesungen/risikoanalyse-solo": "solutions/risk-analysis-solo",
    "standort/muenchen": "locations/munich",
    "standort/sachsen": "locations/saxony",
    "standort/nrw": "locations/nrw",
    "blog": "blog",
    "kontakt": "contact",
    "kontaktformular": "contact-form",
    "impressum": "legal-notice",
    "datenschutz": "privacy",
    "agb": "terms",
    "danke": "thank-you",
    "404": "404",
    "tools/ra-vorbereitung": "tools/ra-preparation",
    **_STATIC_STAGE_ROUTES,
}

RU_ROUTE_MAP: dict[str, str] = {
    "internationale-angebote": "ru/internationale-angebote",
    "internationale-angebote/gruendung-deutschland": "ru/internationale-angebote/osnovanie-biznesa-germaniya",
    "internationale-angebote/leben-arbeiten-deutschland": "ru/internationale-angebote/zhizn-i-rabota-germaniya",
    "internationale-angebote/business-turnaround": "ru/internationale-angebote/biznes-zdorovye-proverka",
    "internationale-angebote/expansion-tochtergesellschaft": "ru/internationale-angebote/ekspansiya-dochernaya-kompaniya",
    **_RU_STAGE_ROUTES,
}

DE_FROM_RU_ROUTE_MAP: dict[str, str] = {v: k for k, v in RU_ROUTE_MAP.items()}

BLOG_SLUG_MAP: dict[str, str] = {
    "auslandsgrundung-risiken-standortwahl-strategie": "international-expansion-risks-location-strategy",
    "emotionale-fuehrung-kmu-eisbergmodell-risiko": "emotional-leadership-smb-iceberg-model-risk",
    "externe-risikofaktoren-fur-kmu-8-einflussfaktoren-die-ihr-unternehmen-bedrohen": "external-risk-factors-smb-8-threats",
    "familiennachfolge-generationskonflikt-risiko-nach-uebergabe": "family-succession-generational-conflict-risk",
    "geistiges-eigentum-patentschutz-praxistipps": "intellectual-property-patent-protection-tips",
    "gesundheit-gruender-risikomanagement-ernaehrung": "founder-health-risk-management-nutrition",
    "iran-konflikt-oelpreis-lieferketten-unternehmen": "iran-conflict-oil-price-supply-chains",
    "ki-unternehmen-risiken-agenten-marie-ossenkopf": "ai-business-risks-agents-marie-ossenkopf",
    "ki-und-risikomanagement-mensch-im-mittelpunkt": "ai-and-risk-management-people-first",
    "ki-verordnung-deutschland-unternehmen": "eu-ai-act-germany-companies",
    "mensch-vertrauen-risikomanagement": "people-trust-risk-management",
    "mitarbeitersensibilisierung-risikobewusste-kultur": "employee-awareness-risk-conscious-culture",
    "mittelstand-fokus-risikomanagement": "mid-market-focus-risk-management",
    "risiken-bewusst-eingehen": "taking-risks-consciously",
    "risikoanalyse-startup-solo-selbststaendige-methode": "risk-analysis-startup-solo-self-employed-method",
    "risikomanagement-klarheit-gefahrenkatalog": "risk-management-clarity-hazard-catalog",
    "risikoradar-community-experten-unternehmer": "risk-radar-community-experts-entrepreneurs",
    "risk-radar-episode-1-who-is-beraterium": "risk-radar-episode-1-who-is-beraterium",
    "sicherheit-unternehmen-risikomanagement-kmu": "business-security-risk-management-smb",
    "startup-fehler-vermeiden-risikomanagement": "startup-mistakes-avoid-risk-management",
    "theorie-praxis-risikomanagement-standards-kmu": "theory-practice-risk-management-standards-smb",
    "ubernimm-die-kontrolle-uber-deine-risiken-bevor-sie-dich-kontrollieren": "take-control-of-your-risks-before-they-control-you",
    "warum-mitarbeiter-riskante-entscheidungen-treffen": "why-employees-make-risky-decisions",
    "what-is-risk-management": "what-is-risk-management",
    "zeit-als-risikofaktor-unternehmer-risikomanagement": "time-as-risk-factor-entrepreneurs-risk-management",
    "notfallplan-unternehmen-payment-ausfall": "business-emergency-plan-payment-outage-smb",
    "gruender-risikomanagement-medtech-christian-senfleben": "founder-risk-management-medtech-christian-senfleben",
}

EN_STATIC_ROUTE_MAP: dict[str, str] = {v: k for k, v in STATIC_ROUTE_MAP.items()}
EN_BLOG_SLUG_MAP: dict[str, str] = {v: k for k, v in BLOG_SLUG_MAP.items()}


def _normalize_route(route: str) -> str:
    return route.strip("/")


def de_to_en_route(de_route: str) -> str:
    key = _normalize_route(de_route)
    if key.startswith("blog/"):
        slug = key.split("/", 1)[1]
        return f"blog/{BLOG_SLUG_MAP.get(slug, slug)}"
    return STATIC_ROUTE_MAP.get(key, key)


def en_to_de_route(en_route: str) -> str:
    key = _normalize_route(en_route)
    if key.startswith("blog/"):
        slug = key.split("/", 1)[1]
        return f"blog/{EN_BLOG_SLUG_MAP.get(slug, slug)}"
    return EN_STATIC_ROUTE_MAP.get(key, key)


def _de_route_from_canonical(canonical: str, *, from_locale: str) -> str:
    route = _normalize_route(canonical)
    if from_locale == "de":
        return route
    if from_locale == "en":
        return en_to_de_route(route)
    if from_locale == "ru":
        return DE_FROM_RU_ROUTE_MAP.get(route, "")
    return route


def has_ru_version(canonical: str, *, from_locale: str = "de") -> bool:
    de_route = _de_route_from_canonical(canonical, from_locale=from_locale)
    return bool(de_route and de_route in RU_ROUTE_MAP)


def alternate_url(canonical: str, *, from_locale: str, to_locale: str) -> str:
    route = _normalize_route(canonical)
    de_route = _de_route_from_canonical(canonical, from_locale=from_locale)

    if to_locale == "de":
        base = DE_SITE_URL
        path = de_route if de_route else route
    elif to_locale == "en":
        base = EN_SITE_URL
        if de_route:
            if de_route.startswith("blog/"):
                slug = de_route.split("/", 1)[1]
                path = f"blog/{BLOG_SLUG_MAP.get(slug, slug)}"
            else:
                path = STATIC_ROUTE_MAP.get(de_route, de_route)
        elif from_locale == "en":
            path = route
        else:
            path = de_to_en_route(route)
    elif to_locale == "ru":
        base = DE_SITE_URL
        if not de_route or de_route not in RU_ROUTE_MAP:
            return ""
        path = RU_ROUTE_MAP[de_route]
    else:
        base = DE_SITE_URL
        path = route

    if not path or path == "404":
        return f"{base}/"
    return f"{base}/{path}/"


def hreflang_links(canonical: str, *, current_locale: str) -> str:
    de_url = alternate_url(canonical, from_locale=current_locale, to_locale="de")
    en_url = alternate_url(canonical, from_locale=current_locale, to_locale="en")
    ru_url = alternate_url(canonical, from_locale=current_locale, to_locale="ru")
    lines = [
        f'\n  <link rel="alternate" hreflang="de" href="{de_url}">',
        f'\n  <link rel="alternate" hreflang="en" href="{en_url}">',
    ]
    if ru_url:
        lines.append(f'\n  <link rel="alternate" hreflang="ru" href="{ru_url}">')
    lines.append(f'\n  <link rel="alternate" hreflang="x-default" href="{de_url}">')
    return "".join(lines)


def language_switcher_html(*, current_locale: str, canonical: str, depth: int) -> str:
    _ = depth
    parts: list[str] = []
    for loc, label in (("de", "DE"), ("en", "EN"), ("ru", "RU")):
        if loc == current_locale:
            parts.append(f'<span class="site-header__lang-current" aria-current="true">{label}</span>')
        else:
            url = alternate_url(canonical, from_locale=current_locale, to_locale=loc)
            if not url:
                continue
            parts.append(
                f'<a class="site-header__lang-link" href="{url}" hreflang="{loc}">{label}</a>'
            )
    inner = '<span class="site-header__lang-sep" aria-hidden="true">|</span>'.join(parts)
    return (
        f'<div class="site-header__lang" role="navigation" aria-label="Language">'
        f"{inner}</div>"
    )
