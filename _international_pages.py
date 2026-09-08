"""Generators for /internationale-angebote/ (DE), /ru/internationale-angebote/ (RU)."""
from __future__ import annotations

import json
from pathlib import Path

from _cms import (
    faq_page_schema,
    load_team_members,
    service_schema,
    speakable_webpage_schema,
    team_by_slug,
    img_html,
)
from _i18n import DE_SITE_URL
from _internationale_angebote import (
    INT_INDEX_DE,
    INT_OFFER_CONFIGS_DE,
    LEGAL_NOTICE_DE,
    LEGAL_NOTICE_RU,
    RU_SLUG_MAP,
)
from _internationale_stufen import INT_JOURNEY, INT_STAGES, package_savings, stage_price_label
from _pricing import PRICE_CATEGORIES, format_eur, offer_price_text

_INT_PRICING = {
    o["nr"]: o
    for cat in PRICE_CATEGORIES
    for o in cat["offers"]
    if o["nr"].startswith("INT-")
}

INT_INDEX_RU = {
    "tag": "МЕЖДУНАРОДНЫЕ УСЛУГИ",
    "h1": "Консалтинг для русскоязычных предпринимателей в Германии",
    "lead": (
        "Локальные знания, русско-немецкая команда и анализ рисков с первого дня — "
        "для предпринимателей из постсоветского пространства."
    ),
    "title": "Международные услуги | Beraterium",
    "description": "Консалтинг: открытие бизнеса, интеграция, turnaround, экспансия — от 50 €.",
    "why_h2": "Почему Beraterium?",
    "why_intro": "Немецкое регулирование + родной язык + анализ рисков.",
    "why_cards": INT_INDEX_DE["why_cards"],
    "faq": [
        ("Для кого?", "Предприниматели из постсоветского пространства."),
        ("Говорите по-русски?", "Да — Veronika, Aleksandra и Till."),
        ("Юридические услуги?", "Нет — консалтинг и координация."),
    ],
    "cta_h2": "Какое предложение подходит?",
    "cta_body": "Консультация 50 € — 30 мин.",
}

RU_OFFER_OVERRIDES: dict[str, dict] = {
    "INT-01": {"h1": "Открыть бизнес в Германии", "lead": "Сопровождение от формы до регистрации и рисков.", "card_teaser": "Бизнес-план, ведомства, риски."},
    "INT-02": {"h1": "Жизнь и работа в Германии", "lead": "Культура, ведомства, ELSTER — модульно.", "card_teaser": "Культура и ведомства."},
    "INT-03": {"h1": "Business Health Check", "lead": "Анализ рисков для действующего бизнеса.", "card_teaser": "Turnaround и приоритеты."},
    "INT-04": {"h1": "Экспансия в Германию", "lead": "Дочерняя компания и продажи на месте.", "card_teaser": "EU-экспансия без переезда."},
}


def ru_offer_configs() -> list[dict]:
    out: list[dict] = []
    for cfg in INT_OFFER_CONFIGS_DE:
        ru = dict(cfg)
        ru["slug"] = RU_SLUG_MAP[cfg["nr"]]
        ru.update(RU_OFFER_OVERRIDES.get(cfg["nr"], {}))
        ru["title"] = f"{ru['h1']} | Beraterium"
        out.append(ru)
    return out


def locale_paths(locale: str, slug: str, *, is_index: bool = False) -> tuple[str, int, str]:
    if locale == "ru":
        base = "ru/internationale-angebote"
        depth = 2 if is_index else 3
        canonical = f"/{base}/" if is_index else f"/{base}/{slug}/"
        return canonical, depth, "../" * depth
    if locale == "en":
        base = "international-services"
        depth = 1 if is_index else 2
        canonical = f"/{base}/" if is_index else f"/{base}/{slug}/"
        return canonical, depth, "../" * depth
    base = "internationale-angebote"
    depth = 1 if is_index else 2
    canonical = f"/{base}/" if is_index else f"/{base}/{slug}/"
    return canonical, depth, "../" * depth


def international_team_section(*, pre: str, team_slugs: list[str], title: str, locale: str = "de") -> str:
    by_slug = team_by_slug(load_team_members())
    members = [by_slug[s] for s in team_slugs if s in by_slug]
    depth = len(pre) // 3 if pre else 0
    lang_label = {"de": "Sprachen", "ru": "Языки", "en": "Languages"}[locale]
    default_lang = {"de": "Deutsch", "ru": "Немецкий", "en": "German"}[locale]
    cards = []
    for m in members:
        langs = ", ".join(m.languages) if m.languages else default_lang
        cards.append(
            f'<li class="brt-card brt-hover-lift">'
            f'{img_html(m.image, m.image_alt, depth, css_class="brt-team-card__img", aspect="1/1")}'
            f'<h3 class="brt-h3">{m.name}</h3><p class="brt-meta">{m.role_tag}</p>'
            f'<p class="brt-body">{m.teaser_bio}</p>'
            f'<p class="brt-meta"><strong>{lang_label}:</strong> {langs}</p></li>'
        )
    return f"""<section class="brt-section brt-section--alt" id="team"><div class="brt-container">
      <h2 class="brt-h2">{title}</h2>
      <ul class="brt-cards-3col brt-stagger">{"".join(cards)}</ul>
    </div></section>"""


def international_price_section(offer: dict, *, pre: str, locale: str) -> str:
    price = offer_price_text(offer)
    price_page = {"de": "preise", "en": "pricing", "ru": "preise"}[locale]
    link = {"de": "Alle Preise", "ru": "Все цены", "en": "All prices"}[locale]
    price_h2 = {"de": "Preis", "ru": "Цена", "en": "Price"}[locale]
    return f"""<section class="brt-section" id="preis"><div class="brt-container brt-highlight-box">
      <h2 class="brt-h2">{price_h2}</h2>
      <p class="brt-body"><strong>{price}</strong> · {offer["duration"]}</p>
      <p class="brt-body">{offer.get("price_detail", "")}</p>
      <p class="brt-meta"><a href="{pre}{price_page}/#international">{link}</a></p>
    </div></section>"""


def international_legal_section(notice: str) -> str:
    return f'<section class="brt-section brt-section--alt"><div class="brt-container"><p class="brt-meta">{notice}</p></div></section>'


_L = dict  # locale string map shorthand


def _t(m: _L | str, locale: str) -> str:
    if isinstance(m, str):
        return m
    return m.get(locale, m.get("de", ""))


def international_journey_section(*, locale: str, pre: str, contact_href: str) -> str:
    steps = INT_JOURNEY.get(locale, INT_JOURNEY["de"])
    h2 = {"de": "Ihr Weg — von der Idee bis zum Wachstum", "en": "Your path — from idea to growth", "ru": "Ваш путь — от идеи до роста"}[locale]
    intro = {
        "de": "Fünf Stufen, die aufeinander aufbauen — Sie starten dort, wo Sie stehen. Jede Stufe einzeln buchbar.",
        "en": "Five stages that build on each other — start where you are. Each stage bookable individually.",
        "ru": "Пять этапов — начните там, где вы сейчас. Каждый этап можно заказать отдельно.",
    }[locale]
    cta = {"de": "Erstberatung 50 €", "en": "Intro call €50", "ru": "Консультация 50 €"}[locale]
    items = []
    for i, step in enumerate(steps, 1):
        price = format_eur(step["price"])
        items.append(
            f'<li class="brt-int-journey__step brt-fade-up" style="--int-step:{i}">'
            f'<span class="brt-int-journey__num" aria-hidden="true">{i}</span>'
            f'<p class="brt-int-journey__label">{step["label"]}</p>'
            f'<p class="brt-int-journey__q">{step["question"]}</p>'
            f'<p class="brt-int-journey__price"><strong>{price}</strong></p>'
            f"</li>"
        )
    return f"""
    <section class="brt-section brt-section--alt brt-int-journey-wrap" id="journey" aria-labelledby="int-journey-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{"CUSTOMER JOURNEY" if locale == "en" else "IHR WEG" if locale == "de" else "ПУТЬ"}</p>
          <h2 id="int-journey-title" class="brt-h2">{h2}</h2>
          <p class="brt-body">{intro}</p>
        </header>
        <ol class="brt-int-journey brt-stagger">{"".join(items)}</ol>
        <p class="brt-int-journey__cta brt-fade-up"><a class="brt-btn" href="{contact_href}">{cta}</a></p>
      </div>
    </section>"""


def international_stages_section(*, parent_nr: str, locale: str, contact_href: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or not block.get("stages"):
        return ""
    cta_stage = {"de": "Anfragen", "en": "Inquire", "ru": "Запрос"}[locale]
    cards = []
    for st in block["stages"]:
        nr = st["nr"].lower()
        hl = "".join(f"<li>{x}</li>" for x in _t(st["highlights"], locale))
        cards.append(
            f'<li class="brt-int-stage brt-card brt-hover-lift" id="{nr}">'
            f'<p class="brt-int-stage__nr">{st["nr"]}</p>'
            f'<h3 class="brt-h3">{_t(st["name"], locale)}</h3>'
            f'<p class="brt-int-stage__price">{stage_price_label(st, locale)}</p>'
            f'<p class="brt-meta">{_t(st["duration"], locale)}</p>'
            f'<p class="brt-body">{_t(st["teaser"], locale)}</p>'
            f'<ul class="brt-list-check brt-int-stage__hl">{hl}</ul>'
            f'<p class="brt-int-stage__cta"><a class="brt-btn brt-btn--ghost" href="{contact_href}">{cta_stage}</a></p>'
            f"</li>"
        )
    h2 = _t(block["stages_h2"], locale)
    intro = _t(block.get("stages_intro", ""), locale)
    return f"""
    <section class="brt-section" id="stufen" aria-labelledby="int-stufen-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 id="int-stufen-title" class="brt-h2">{h2}</h2>
          <p class="brt-body">{intro}</p>
        </header>
        <ul class="brt-int-stages brt-stagger">{"".join(cards)}</ul>
      </div>
    </section>"""


def international_packages_section(*, parent_nr: str, locale: str, contact_href: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or not block.get("packages"):
        return ""
    pkgs = block["packages"]
    h2 = _t(block.get("packages_h2", {"de": "Pakete", "en": "Bundles", "ru": "Пакеты"}), locale)
    save_l = {"de": "Sie sparen", "en": "You save", "ru": "Экономия"}[locale]
    incl_l = {"de": "Enthalten", "en": "Includes", "ru": "Включено"}[locale]
    btn_pkg = {"de": "Paket besprechen", "en": "Discuss bundle", "ru": "Обсудить"}[locale]
    cards = []
    for pkg in pkgs:
        feat = ' brt-int-pack--featured' if pkg.get("featured") else ""
        sav = package_savings(pkg)
        sav_html = f'<p class="brt-int-pack__save">{save_l} {format_eur(sav)}</p>' if sav else ""
        inc = ", ".join(pkg["includes"])
        cards.append(
            f'<li class="brt-int-pack brt-card brt-hover-lift{feat}">'
            f'<p class="brt-int-pack__nr">{pkg["nr"]}</p>'
            f'<h3 class="brt-h3">{_t(pkg["name"], locale)}</h3>'
            f'<p class="brt-int-pack__price">{format_eur(pkg["price"])}</p>'
            f'{sav_html}'
            f'<p class="brt-meta"><strong>{incl_l}:</strong> {inc}</p>'
            f'<p class="brt-int-pack__cta"><a class="brt-btn" href="{contact_href}">{btn_pkg}</a></p>'
            f"</li>"
        )
    matrix = ""
    cols = block.get("package_cols") or []
    if cols and parent_nr == "INT-01":
        stage_nrs = [s["nr"] for s in block["stages"]]
        hdr = "".join(f'<th scope="col">{p["nr"].replace("INT-01-", "P")}</th>' for p in pkgs)
        rows = []
        for snr in stage_nrs:
            cells = []
            for pkg in pkgs:
                mark = "✓" if snr in pkg["includes"] else "—"
                cells.append(f"<td>{mark}</td>")
            rows.append(
                f'<tr><th scope="row">{snr.replace("INT-01-", "")}</th>'
                f'<td>{format_eur(next(s["price"] for s in block["stages"] if s["nr"] == snr))}</td>'
                f'{"".join(cells)}</tr>'
            )
        price_row = "".join(f'<td><strong>{format_eur(p["price"])}</strong></td>' for p in pkgs)
        matrix = f"""
        <div class="brt-table-wrap brt-int-pack-table brt-fade-up">
          <table class="brt-table">
            <caption class="brt-sr-only">{h2}</caption>
            <thead><tr><th scope="col">Stufe</th><th scope="col">Einzeln</th>{hdr}</tr></thead>
            <tbody>{"".join(rows)}
              <tr class="brt-int-pack-table__total"><th scope="row">Paketpreis</th><td></td>{price_row}</tr>
            </tbody>
          </table>
        </div>"""
    return f"""
    <section class="brt-section brt-section--alt" id="pakete" aria-labelledby="int-pakete-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 id="int-pakete-title" class="brt-h2">{h2}</h2>
        </header>
        <ul class="brt-int-packs brt-stagger">{"".join(cards)}</ul>
        {matrix}
      </div>
    </section>"""


def international_excluded_section(*, parent_nr: str, locale: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or not block.get("excluded"):
        return ""
    h2 = {"de": "Nicht enthalten", "en": "Not included", "ru": "Не входит"}[locale]
    items = "".join(f"<li>{x}</li>" for x in _t(block["excluded"], locale))
    return f"""
    <section class="brt-section" id="ausgeschlossen"><div class="brt-container brt-highlight-box brt-fade-up">
      <h2 class="brt-h2">{h2}</h2>
      <ul class="brt-list-check">{items}</ul>
    </div></section>"""


def international_stages_price_banner(*, offer: dict, parent_nr: str, locale: str, pre: str) -> str:
    block = INT_STAGES.get(parent_nr)
    price_h2 = {"de": "Preise", "ru": "Цены", "en": "Pricing"}[locale]
    price_page = {"de": "preise", "en": "pricing", "ru": "preise"}[locale]
    link = {"de": "Alle Preise auf der Preisseite", "ru": "Все цены", "en": "All prices on pricing page"}[locale]
    anchor = {"de": "Einzelstufen & Pakete unten", "en": "Individual stages & bundles below", "ru": "Этапы и пакеты ниже"}[locale]
    detail = offer.get("price_detail", "")
    return f"""<section class="brt-section" id="preis"><div class="brt-container brt-int-price-banner brt-fade-up">
      <h2 class="brt-h2">{price_h2}</h2>
      <p class="brt-int-price-banner__main"><strong>{offer_price_text(offer)}</strong></p>
      <p class="brt-body">{detail}</p>
      <p class="brt-meta">{anchor} · <a href="{pre}{price_page}/#international">{link}</a></p>
    </div></section>"""
