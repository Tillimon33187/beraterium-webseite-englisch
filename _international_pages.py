"""Generators for /internationale-angebote/ (DE), /ru/internationale-angebote/ (RU)."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from _cms import (
    faq_page_schema,
    load_team_members,
    service_schema,
    speakable_webpage_schema,
    team_by_slug,
    team_member_url,
    img_html,
)
from _i18n import DE_SITE_URL
from _internationale_angebote import (
    EN_SLUG_MAP,
    INT_INDEX_DE,
    INT_INDEX_EN,
    INT_OFFER_CONFIGS_DE,
    LEGAL_NOTICE_DE,
    LEGAL_NOTICE_RU,
    RU_SLUG_MAP,
)
from _internationale_stufen import (
    INT_JOURNEY,
    INT_STAGES,
    package_price_label,
    package_savings,
    stage_price_label,
)
from _internationale_stufen_detail import (
    customer_label,
    humanize_customer_text,
    merged_stage,
    stage_detail_href,
    stage_url,
)
from _pricing import PRICE_CATEGORIES, format_eur, offer_price_text

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


_INT_AUDIENCE_IMAGES: dict[str, str] = {
    "INT-01": "img/international/gruendung-deutschland-fuer-wen.png",
    "INT-02": "img/international/leben-arbeiten-deutschland-fuer-wen.png",
    "INT-03": "img/international/business-turnaround-fuer-wen.png",
    "INT-04": "img/international/expansion-deutschland-fuer-wen.png",
}

_INT_AUDIENCE_ALT: dict[str, dict[str, str]] = {
    "INT-01": {
        "de": "Berater und Gründerin besprechen Unterlagen zur Selbstständigkeit in Deutschland",
        "en": "Advisor and founder reviewing documents for starting a business in Germany",
        "ru": "Консультант и основательница обсуждают документы для бизнеса в Германии",
    },
    "INT-02": {
        "de": "Beraterin erklärt einer Neuankömmlingin Behördenbriefe und Alltag in Deutschland",
        "en": "Advisor explaining authority letters and daily life in Germany to a newcomer",
        "ru": "Консультант объясняет новоприбывшей письма из ведомств и быт в Германии",
    },
    "INT-03": {
        "de": "Berater und Unternehmerin sortieren Unterlagen zu Finanzamt, IHK und Compliance",
        "en": "Advisor and business owner reviewing tax office, chamber, and compliance documents",
        "ru": "Консультант и предпринимательница разбирают документы Finanzamt, IHK и compliance",
    },
    "INT-04": {
        "de": "Berater und Unternehmer besprechen Expansion und Tochtergesellschaft in Deutschland",
        "en": "Advisor and entrepreneur discussing expansion and subsidiary setup in Germany",
        "ru": "Консультант и предприниматель обсуждают экспансию и дочернюю компанию в Германии",
    },
}

INT_INDEX_RU = {
    "tag": "МЕЖДУНАРОДНЫЕ УСЛУГИ",
    "h1": "Консалтинг для русскоязычных предпринимателей в Германии",
    "lead": (
        "Лучшее из двух миров: немецкая экспертиза по регистрации и регулированию плюс "
        "русскоязычные консультанты, у которых вы чувствуете себя как среди своих — "
        "Gründung, ведомства, культура, нормы ЕС и риски. DE · EN · RU."
    ),
    "title": "Международные услуги | Beraterium",
    "description": "Консалтинг: открытие бизнеса, интеграция, turnaround, экспансия — бесплатная консультация.",
    "why_h2": "Почему Beraterium для международных предпринимателей?",
    "why_intro": (
        "Мы соединяем локальную экспертизу и сеть в Германии с культурной связью с Россией — "
        "чтобы вы получали профессиональную и понятную консультацию."
    ),
    "why_cards": [
        (
            "Русский — родной язык, среди своих",
            "Veronika Berdnikova и Aleksandra Polosukhina — носители русского языка. "
            "По запросу консультируем полностью на русском — без потерь при переводе, как среди своих.",
        ),
        (
            "Экспертиза по Германии",
            "Till Blania знает Gründung, ведомства, законы, деловую культуру DE, нормы ЕС "
            "и типичные риски из многолетней практики — от идеи до запуска.",
        ),
        (
            "Два мира в одном",
            "Локальная сеть (нотариусы, юристы, Steuerberater, IHK) плюс понимание "
            "русского мышления — не нужно выбирать между «правильно по-немецки» и «как дома».",
        ),
        (
            "Риски с первого дня",
            "Слепые зоны заранее: Aufenthalt, форма, налоги, банки, санкции, культура — "
            "с оценкой Beraterium в евро, а не только интуицией.",
        ),
        (
            "Три языка DE · EN · RU",
            "Полноценные страницы на beraterium.de/ru/ — вы выбираете язык, мы подстраиваемся.",
        ),
    ],
    "team_tag": "ВАША КОМАНДА",
    "team_h2": "Русско-немецкая команда — вы в надёжных руках",
    "team_intro": (
        "Два носителя русского языка и экспертиза по Gründung и рискам в Германии в одной команде: "
        "Veronika и Aleksandra — доверие и понимание на русском, Till — путь через немецкие "
        "ведомства, законы и правила. Мы объединяем оба мира — профессионально и по-человечески."
    ),
    "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
    "team_member_intros": {
        "veronika-berdnikova": (
            "Русский — родной язык. Ваш контакт для предпринимателей из России и СНГ. "
            "Ясно, тактично, без давления."
        ),
        "aleksandra-polosukhina": (
            "Русский — родной язык. Международные коммуникации, маркетинг и культура команд. "
            "Мост между русским и немецким бизнесом."
        ),
        "till-blania": (
            "Gründung в Германии, ведомства, законы, нормы ЕС и риск-менеджмент — "
            "плюс HSE St. Petersburg и понимание постсоветского пространства."
        ),
    },
    "faq": [
        ("Для кого?", "Предприниматели из постсоветского пространства."),
        (
            "Говорите по-русски?",
            "Да — Veronika и Aleksandra носители русского; Till консультирует на DE, EN "
            "и RU (B1, продолжает учить). По запросу — всё общение на русском.",
        ),
        ("Юридические услуги?", "Нет — консалтинг и координация."),
    ],
    "cta_h2": "Какое предложение подходит?",
    "cta_body": "Бесплатная консультация — 30 мин.",
}

RU_OFFER_OVERRIDES: dict[str, dict] = {
    "INT-01": {
        "tag": "ОСНОВАНИЕ · ГЕРМАНИЯ",
        "h1": "Открыть бизнес в Германии — с планом и защитой от рисков",
        "lead": (
            "Регистрация — лишь часть пути. Нет идеи или уже готовы к старту — "
            "ведём шаг за шагом на DE, EN или RU. Бесплатная консультация, "
            "затем ориентация, планирование с нуля или сразу launch."
        ),
        "card_teaser": "Бесплатная консультация · ориентация 150 € · пакет от 2.390 €.",
        "fuer_wen_intro": "Подходит, если:",
        "fuer_wen": [
            "Вы в Германии или планируете приехать — с идеей или без",
            "Сначала хотите понять, как работает рынок (ориентация)",
            "Старт с нуля — научиться планировать бизнес (пакет P0)",
            "Идея есть — нужна реализация launch (пакет P1)",
        ],
        "leistungen": [
            "Бесплатная консультация и ориентация по Германии (1:1)",
            "Планирование: рынок, модель, SWOT, PESTEL — вы работаете, мы направляем",
            "Launch Roadmap и практическая помощь с ведомствами и банком",
            "Координация нотариуса, юриста, Steuerberater из сети",
            "Поиск субсидий и анализ рисков",
        ],
        "steps": [
            ("Первая консультация", "30 мин. бесплатно: ситуация, цель, путь — без обязательств."),
            ("Ориентация (опц.)", "Ориентация по Германии 1,5 ч — рынок, рамки, ваши вопросы (150 €)."),
            ("Два пути", "Сопровождение с нуля (Check + план) — или Launch (Roadmap + реализация), если идея готова."),
            ("Go-Live", "Задокументированный статус, план рисков, опционально следующий пакет."),
        ],
        "ergebnis": [
            "Ясный путь — ориентация, планирование с нуля или launch",
            "Ваш план Gründung своими словами — не переписанный нами",
            "Сеть нотариус, Steuerberater, IHK подключена",
            "Типичные blind spots выявлены до того, как станут дорогими",
        ],
        "faq": [
            ("Можно ли иностранцу?", "Да — в зависимости от Aufenthaltstitel. Разберём на бесплатной консультации или Business Check."),
            ("Сколько стоит?", "Ориентация 150 € · сопровождение с нуля от 2.390 € · Launch 4.490 € · Gründung 360° 7.490 € netto."),
            ("По отдельности или пакет?", "Два пути: планирование с нуля (P0) или Launch (P1) — полный путь как Gründung 360° (P2)."),
            ("Юридические услуги?", "Нет — координация с партнёрами-юристами и Steuerberater."),
        ],
        "cta_h2": "Планируете Gründung?",
        "cta_body": "Бесплатная консультация — 30 мин., DE/EN/RU.",
    },
    "INT-02": {
        "tag": "ИНТЕГРАЦИЯ · ГЕРМАНИЯ",
        "h1": "Жизнь и работа в Германии",
        "lead": (
            "Ведомства, язык, культура — без ощущения «как дома» в Германии не построить стабильный бизнес. "
            "Мы убираем барьеры: практично, 1:1, на русском или немецком."
        ),
        "card_teaser": "Культура и ведомства.",
        "fuer_wen_lead": (
            "Интеграция в Германии редко ломается из-за нежелания — чаще из-за языка, ведомств, "
            "негласных правил и чувства «я здесь чужой». Сначала быт и язык, потом бизнес. "
            "Мы помогаем: local know-how, русскоязычные консультанты и понимание обоих миров."
        ),
        "fuer_wen": [
            "Немецкая деловая коммуникация, прямота и small talk кажутся чужими",
            "Письма из ведомств перегружают — Finanzamt, Gewerbeamt, Ausländerbehörde: неясно, что делать",
            "ELSTER, налоги, страховки — немецкие правила как лабиринт",
            "Вы сильны профессионально, но не чувствуете, что можете «управлять системой» в DE",
            "Сначала должен сложиться быт (язык, жильё, повседневность) — иначе бизнес не держится",
            "Хотите понимать и действовать сами — не только перевод или тупик",
            "Русскоязычные консультанты + опыт Германии — вас понимают и ведут, вы не одни",
            "Параллельно с Gründung или после — модульно, это не языковой курс",
        ],
        "fuer_wen_intro": "Подходит, если:",
        "leistungen": [
            "Деловая и бытовая культура",
            "Навигация по ведомствам и ELSTER",
            "Типичные ошибки и ловушки",
            "Опционально: поиск объекта",
        ],
        "steps": [
            ("Уточнение потребности", "Модули и сроки."),
            ("Сессии", "1:1, практично."),
            ("Домашние задания", "Конкретные задачи."),
            ("Review", "Корректировка после модуля."),
        ],
        "ergebnis": [
            "Уверенность с ведомствами",
            "Понимание культуры",
            "Индивидуальный план",
        ],
        "faq": [
            ("Языковой курс?", "Нет — soft skills и знание ведомств."),
            ("Модули по отдельности?", "Да — от 180 €/ч, модуль от 490 €, пакет 2.900 €."),
        ],
        "cta_h2": "Понять Германию?",
        "cta_body": "Записаться — подберём модули.",
    },
    "INT-03": {
        "tag": "TURNAROUND · ГЕРМАНИЯ",
        "h1": "Business Health Check",
        "lead": (
            "Открыли бизнес в Германии — работает, но нестабильно? Finanzamt, IHK, охрана труда, "
            "Datenschutz — давление со всех сторон. От быстрой диагностики до сопровождения: "
            "найдём, где застряло, и выстроим стратегию, которую можно реализовать."
        ),
        "card_teaser": "Ведомства, cash flow, рост — структурная диагностика.",
        "fuer_wen_lead": (
            "Многие замечают уже после старта: выручка есть, а cash flow, ведомства и правила "
            "перегружают. Finanzamt, IHK, Arbeitsschutz, проверки Datenschutz с предупреждениями — "
            "накапливаются темы, о которых не думали. Именно тогда подходит Business Health Check: "
            "вместе найти узкие места, расставить приоритеты и выработать план с сопровождением до внедрения."
        ),
        "fuer_wen": [
            "Открыли бизнес в Германии — работает, но нестабильно",
            "Finanzamt, IHK или Gewerbeamt давят — непонятно, с чего начать",
            "Arbeitsschutz, Datenschutz или Abmahnung — неожиданные темы накапливаются",
            "Выручка есть, cash flow нет — не знаете, куда смотреть",
            "Вторая точка (салон, филиал) — без ошибок первой локации",
            "Переход с Einzelunternehmen на GmbH — неясно, выгодно ли и какие есть варианты",
            "Нужна ясность и пошаговый план, который можно выполнить",
        ],
        "fuer_wen_intro": "Подходит, если:",
        "leistungen": [
            "Анализ рисков по методике Beraterium",
            "Диагностика узких мест",
            "Приоритетные меры",
        ],
        "steps": [
            ("Kick-off", "90 мин. — текущая ситуация."),
            ("Диагностика", "Workshops, матрица рисков."),
            ("Стратегия", "Топ-5 мер."),
            ("Передача", "Report, опционально сопровождение."),
        ],
        "ergebnis": [
            "Ясность, где реально застряло — финансы, команда, процессы, ведомства",
            "Приоритетные меры вместо суеты",
            "План внедрения, который мы можем сопровождать вместе",
        ],
        "faq": [
            ("BAFA?", "Да — полный Health Check от 3.500 € подходит для субсидии."),
            ("Quick Check vs. полный?", "Quick Check (790 €) = 90 мин. диагностика. Полный = метод Beraterium с workshops."),
            ("Отдельные риски?", "Нет — только в контексте пакета анализа рисков."),
        ],
        "cta_h2": "Где застряло?",
        "cta_body": "Запросить Health Check.",
    },
    "INT-04": {
        "tag": "ЭКСПАНСИЯ · EU",
        "h1": "Экспансия в Германию",
        "lead": (
            "Успешный бизнес в России — и экспансия в Германию? Часто мешают не продукт, а ограничения, "
            "compliance и отсутствие партнёров на месте. Мы реализуем в DE: анализ рынка, Vertrieb, "
            "регистрация компании, договоры, заявки — по индивидуальному проекту. "
            "Вы — капитал и стратегия, Beraterium — координация на месте."
        ),
        "card_teaser": "Индивидуальный проект экспансии — объём и бюджет по согласованию.",
        "fuer_wen_intro": "Подходит, если:",
        "fuer_wen_lead": (
            "Многие предприниматели с работающим бизнесом в России хотят рынок Германии — но санкции, "
            "регуляторика и отсутствие local partner тормозят. Каждая экспансия — отдельный проект: "
            "объём, команда и бюджет планируем вместе — обычно 30.000–100.000 €."
        ),
        "fuer_wen": [
            "Успешный бизнес в России/СНГ — хотите экспансию в Германию",
            "Санкции, compliance или нет local partner — вход на рынок заблокирован",
            "Анализ рынка, Vertrieb и Gründung в DE — но нет команды на месте",
            "Дочерняя компания, договоры, регистрация — координация из одних рук",
            "Не хотите сами разбираться с ведомствами, нотариусом и setup в DE",
            "Производство может остаться дома — присутствие и продажи в Германии",
            "Индивидуальный проект: вы — капитал, Beraterium координирует реализацию на месте",
        ],
        "ergebnis": [
            "Присутствие в DE без переезда — минимум операционной нагрузки на месте",
            "Compliance-безопасная структура — санкции, KYC, чистое разделение",
            "Рынок, Vertrieb и компания — реализовано Beraterium, не только на бумаге",
        ],
        "faq": [
            ("Нужно переезжать?", "Нет — Beraterium координирует на месте. Вы — капитал и стратегические решения."),
            ("Отделение от RU-компании?", "Чистая структура по compliance — на стратегической сессии."),
            ("Что остаётся у меня?", "Капитал, продукт, согласования — операционный setup в DE через нас."),
            ("Как определяется цена?", "Индивидуально по scope — обычно 30.000–100.000 € нетто. Фикс — после стратегической сессии."),
            ("Юрист и Steuerberater?", "Да — координируем специалистов из сети. Юр./налог. услуги — через партнёров."),
        ],
        "cta_h2": "Освоить Германию?",
        "cta_body": "Стратегическая сессия — scope и бюджет.",
    },
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


def locale_paths(
    locale: str,
    slug: str,
    *,
    is_index: bool = False,
    stage_slug_key: str | None = None,
) -> tuple[str, int, str]:
    if locale == "ru":
        base = "ru/internationale-angebote"
        if is_index:
            return f"/{base}/", 2, "../" * 2
        if stage_slug_key:
            canonical = f"/{base}/{slug}/{stage_slug_key}/"
            return canonical, 4, "../" * 4
        return f"/{base}/{slug}/", 3, "../" * 3
    if locale == "en":
        base = "international-services"
        if is_index:
            return f"/{base}/", 1, "../" * 1
        if stage_slug_key:
            canonical = f"/{base}/{slug}/{stage_slug_key}/"
            return canonical, 3, "../" * 3
        return f"/{base}/{slug}/", 2, "../" * 2
    base = "internationale-angebote"
    if is_index:
        return f"/{base}/", 1, "../" * 1
    if stage_slug_key:
        canonical = f"/{base}/{slug}/{stage_slug_key}/"
        return canonical, 3, "../" * 3
    return f"/{base}/{slug}/", 2, "../" * 2


def international_team_section(
    *,
    pre: str,
    team_slugs: list[str],
    title: str,
    locale: str = "de",
    section_alt: bool = False,
    intro: str = "",
    tag: str = "",
    member_intros: dict[str, str] | None = None,
) -> str:
    by_slug = team_by_slug(load_team_members())
    members = [by_slug[s] for s in team_slugs if s in by_slug]
    depth = len(pre) // 3 if pre else 0
    lang_label = {"de": "Sprachen", "ru": "Языки", "en": "Languages"}[locale]
    default_lang = {"de": "Deutsch", "ru": "Немецкий", "en": "German"}[locale]
    ru_native_badge = {
        "de": "Russisch Muttersprache",
        "en": "Native Russian",
        "ru": "Русский — родной язык",
    }[locale]
    cards = []
    for m in members:
        href = team_member_url(pre, m.slug)
        media = img_html(
            m.image,
            m.image_alt,
            depth,
            css_class="brt-card__media-img",
            aspect="4/5",
        )
        if "brt-image-placeholder" in media:
            media_block = (
                f'<div class="brt-card__media brt-card__media--placeholder" role="img" '
                f'aria-label="{escape(m.image_alt)}">'
                f'<span class="brt-card__media-label">{escape(m.name)}</span></div>'
            )
        else:
            media_block = f'<div class="brt-card__media">{media}</div>'
        langs = ", ".join(m.languages) if m.languages else default_lang
        bio = (member_intros or {}).get(m.slug) or m.teaser_bio or ""
        ru_badge = ""
        if any("Russisch (Muttersprache)" in lang or "Russian (native)" in lang for lang in (m.languages or [])):
            ru_badge = f'<p class="brt-tag brt-int-team__ru-badge">{escape(ru_native_badge)}</p>'
        cards.append(
            f'<li class="brt-card brt-card--profile brt-hover-lift brt-int-team__card">'
            f'<a class="brt-card__link" href="{escape(href)}">'
            f"{media_block}"
            f'<div class="brt-card__body">'
            f"{ru_badge}"
            f'<h3 class="brt-h3">{escape(m.name)}</h3>'
            f'<p class="brt-meta brt-meta--accent">{escape(m.role_tag)}</p>'
            f'<p class="brt-body">{escape(bio)}</p>'
            f'<p class="brt-meta"><strong>{lang_label}:</strong> {escape(langs)}</p>'
            f"</div></a></li>"
        )
    tag_html = f'<p class="brt-tag">{escape(tag)}</p>' if tag else ""
    intro_html = f'<p class="brt-body">{escape(intro)}</p>' if intro else ""
    cards_html = "".join(cards)
    if len(cards) <= 3:
        team_block = f'<ul class="brt-cards-3col brt-stagger brt-fade-up">{cards_html}</ul>'
    else:
        slider_i18n = {
            "de": ("Beratungsteam", "Vorherige Person", "Nächste Person"),
            "en": ("Advisory team", "Previous team member", "Next team member"),
            "ru": ("Команда", "Предыдущий", "Следующий"),
        }[locale]
        team_block = cards_slider_block(
            cards_html,
            aria_label=slider_i18n[0],
            prev_label=slider_i18n[1],
            next_label=slider_i18n[2],
            autoplay_ms=10000,
        )
    return f"""<section class="brt-section{" brt-section--alt" if section_alt else ""} brt-int-team" id="team">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          {tag_html}
          <h2 class="brt-h2">{escape(title)}</h2>
          {intro_html}
        </header>
        {team_block}
      </div>
    </section>"""


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
    return f'<section class="brt-section brt-section--alt brt-int-legal"><div class="brt-container"><p class="brt-meta">{notice}</p></div></section>'


_L = dict  # locale string map shorthand


def _t(m: _L | str, locale: str) -> str:
    if isinstance(m, str):
        return m
    return m.get(locale, m.get("de", ""))


def int_faq_title(locale: str) -> str:
    return {"de": "Häufige Fragen", "en": "FAQ", "ru": "Частые вопросы"}[locale]


def int_team_member_intros(locale: str) -> dict[str, str]:
    return {
        "de": INT_INDEX_DE.get("team_member_intros", {}),
        "ru": INT_INDEX_RU.get("team_member_intros", {}),
        "en": INT_INDEX_EN.get("team_member_intros", {}),
    }.get(locale, {})


def _t_list(items: list, locale: str) -> list[str]:
    return [_t(x, locale) for x in items]


def _t_steps(steps: list[tuple], locale: str) -> list[tuple[str, str]]:
    return [(_t(t, locale), _t(b, locale)) for t, b in steps]


def _t_faq(faq: list[tuple], locale: str) -> list[tuple[str, str]]:
    return [(_t(q, locale), _t(a, locale)) for q, a in faq]


def international_journey_section(*, locale: str, pre: str, contact_href: str) -> str:
    steps = INT_JOURNEY.get(locale, INT_JOURNEY["de"])
    h2 = {"de": "Ihr Weg — von der Idee bis zum Wachstum", "en": "Your path — from idea to growth", "ru": "Ваш путь — от идеи до роста"}[locale]
    intro = {
        "de": "Vom kostenlosen Erstgespräch bis Launch — Sie starten dort, wo Sie stehen. Zwei Wege: Planung bei 0 oder direkt Umsetzung.",
        "en": "From free intro to launch — start where you are. Two paths: planning from zero or straight to execution.",
        "ru": "От бесплатной консультации до запуска — два пути: планирование с нуля или сразу реализация.",
    }[locale]
    cta = {"de": "Kostenlose Erstberatung", "en": "Free intro call", "ru": "Бесплатная консультация"}[locale]
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


def int_is_project_offer(parent_nr: str) -> bool:
    block = INT_STAGES.get(parent_nr)
    return bool(block and block.get("offer_model") == "project")


def international_project_section(*, parent_nr: str, locale: str, contact_href: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or block.get("offer_model") != "project":
        return ""
    phases = block.get("project_phases") or []
    phase_l = {"de": "Phase", "en": "Phase", "ru": "Фаза"}[locale]
    tag_l = {"de": "IHR PROJEKT", "en": "YOUR PROJECT", "ru": "ВАШ ПРОЕКТ"}[locale]
    cta = {"de": "Projekt besprechen", "en": "Discuss your project", "ru": "Обсудить проект"}[locale]
    cards = []
    for i, ph in enumerate(phases, 1):
        hl = "".join(f"<li>{x}</li>" for x in _t(ph["highlights"], locale))
        cards.append(
            f'<li class="brt-int-stage brt-int-project-phase brt-card brt-hover-lift" style="--int-i:{i}">'
            f'<div class="brt-int-stage__head"><span class="brt-int-stage__step">{phase_l} {i}</span></div>'
            f'<h3 class="brt-int-stage__title">{_t(ph["name"], locale)}</h3>'
            f'<p class="brt-int-stage__teaser">{_t(ph["teaser"], locale)}</p>'
            f'<ul class="brt-list-check brt-int-stage__hl">{hl}</ul>'
            f"</li>"
        )
    count_cls = f" brt-int-stages--n{len(phases)}" if len(phases) <= 6 else ""
    phases_html = f'<ul class="brt-int-stages brt-stagger{count_cls}">{"".join(cards)}</ul>'
    coord_h2 = _t(block["project_coordinated_h2"], locale)
    coord_intro = _t(block.get("project_coordinated_intro", ""), locale)
    coord_tag = {"de": "NETZWERK", "en": "NETWORK", "ru": "СЕТЬ"}[locale]
    coord_cards = []
    for i, item in enumerate(_t(block["project_coordinated"], locale), 1):
        title, _, detail = item.partition(" — ")
        if not detail:
            title, detail = item, ""
        coord_cards.append(
            f'<li class="brt-int-coordinated__card brt-card brt-hover-lift" style="--int-i:{i}">'
            f'<p class="brt-int-coordinated__title">{escape(title)}</p>'
            f'<p class="brt-int-coordinated__text">{escape(detail)}</p>'
            f"</li>"
        )
    coord_html = f'<ul class="brt-int-coordinated brt-stagger">{"".join(coord_cards)}</ul>'
    return f"""
    <section class="brt-section brt-section--alt brt-int-project-wrap" id="projekt" aria-labelledby="int-projekt-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{tag_l}</p>
          <h2 id="int-projekt-title" class="brt-h2">{_t(block["project_h2"], locale)}</h2>
          <p class="brt-body brt-int-stages__intro">{_t(block["project_intro"], locale)}</p>
        </header>
        {phases_html}
        <p class="brt-int-project__cta brt-fade-up"><a class="brt-btn" href="{contact_href}">{cta}</a></p>
      </div>
    </section>
    <section class="brt-section brt-int-coordinated-wrap" id="koordination" aria-labelledby="int-koord-title">
      <div class="brt-container brt-fade-up">
        <header class="brt-section__header brt-section__header--center">
          <p class="brt-tag">{coord_tag}</p>
          <h2 id="int-koord-title" class="brt-h2">{coord_h2}</h2>
          <p class="brt-body brt-int-coordinated__intro">{coord_intro}</p>
        </header>
        {coord_html}
      </div>
    </section>"""


def international_project_price_banner(*, parent_nr: str, locale: str, pre: str, contact_href: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or block.get("offer_model") != "project":
        return ""
    budget = _t(block["project_budget"], locale)
    if isinstance(budget, dict):
        range_txt = budget.get("range", "")
        note_txt = budget.get("note", "")
    else:
        range_txt, note_txt = "", str(budget)
    price_h2 = {"de": "Investition", "en": "Investment", "ru": "Инвестиция"}[locale]
    netto = {"de": "netto zzgl. USt.", "en": "net plus VAT", "ru": "нетто + НДС"}[locale]
    cta = {"de": "Strategiegespräch buchen", "en": "Book strategy call", "ru": "Записаться на сессию"}[locale]
    label = {"de": "Typisches Projektvolumen", "en": "Typical project volume", "ru": "Типичный объём"}[locale]
    return f"""
    <section class="brt-section brt-int-price-wrap" id="preis">
      <div class="brt-container brt-int-price-banner brt-fade-up">
        <p class="brt-tag brt-int-price-banner__tag">{netto.upper()}</p>
        <h2 class="brt-h2 brt-int-price-banner__h2">{price_h2}</h2>
        <p class="brt-int-price-banner__label">{label}</p>
        <p class="brt-int-price-banner__main">{range_txt}</p>
        <p class="brt-int-price-banner__detail">{note_txt}</p>
        <p class="brt-int-price-banner__meta"><a class="brt-btn brt-btn--on-dark" href="{contact_href}">{cta}</a></p>
      </div>
    </section>"""


def international_stages_section(*, parent_nr: str, locale: str, contact_href: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or not block.get("stages") or block.get("offer_model") == "project":
        return ""
    cta_detail = {"de": "Details", "en": "Details", "ru": "Подробнее"}[locale]
    cta_inquire = {"de": "Anfragen", "en": "Inquire", "ru": "Запрос"}[locale]
    step_l = {"de": "Stufe", "en": "Stage", "ru": "Этап"}[locale]
    stages = block["stages"]
    cards = []
    for i, st in enumerate(stages, 1):
        nr = st["nr"].lower()
        hl = "".join(f"<li>{x}</li>" for x in _t(st["highlights"], locale))
        detail_href = stage_detail_href(stage_nr=st["nr"], locale=locale)
        cards.append(
            f'<li class="brt-int-stage brt-card brt-hover-lift" id="{nr}" style="--int-i:{i}">'
            f'<div class="brt-int-stage__head">'
            f'<span class="brt-int-stage__step">{step_l} {i}</span>'
            f"</div>"
            f'<h3 class="brt-int-stage__title">{_t(st["name"], locale)}</h3>'
            f'<div class="brt-int-stage__price-row">'
            f'<span class="brt-int-stage__price">{stage_price_label(st, locale)}</span>'
            f'<span class="brt-int-stage__duration">{_t(st["duration"], locale)}</span>'
            f"</div>"
            f'<p class="brt-int-stage__teaser">{_t(st["teaser"], locale)}</p>'
            f'<ul class="brt-list-check brt-int-stage__hl">{hl}</ul>'
            f'<p class="brt-int-stage__cta">'
            f'<a class="brt-btn" href="{detail_href}">{cta_detail}</a> '
            f'<a class="brt-btn brt-btn--ghost" href="{contact_href}">{cta_inquire}</a>'
            f"</p>"
            f"</li>"
        )
    h2 = _t(block["stages_h2"], locale)
    intro = _t(block.get("stages_intro", ""), locale)
    solo_l = {"de": "Einzeln buchbar", "en": "Book individually", "ru": "По отдельности"}[locale]
    slider_i18n = {
        "de": ("Einzelstufen", "Vorherige Stufe", "Nächste Stufe"),
        "en": ("Individual stages", "Previous stage", "Next stage"),
        "ru": ("Этапы", "Предыдущий этап", "Следующий этап"),
    }[locale]
    if len(stages) > 3:
        cards_block = cards_slider_block(
            "".join(cards),
            aria_label=slider_i18n[0],
            prev_label=slider_i18n[1],
            next_label=slider_i18n[2],
            autoplay_ms=10000,
        )
        cards_html = f'<div class="brt-int-stages-slider">{cards_block}</div>'
    else:
        count_cls = f" brt-int-stages--n{len(stages)}" if len(stages) <= 6 else ""
        cards_html = f'<ul class="brt-int-stages brt-stagger{count_cls}">{"".join(cards)}</ul>'
    return f"""
    <section class="brt-section brt-section--alt brt-int-stages-wrap" id="stufen" aria-labelledby="int-stufen-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{solo_l.upper()}</p>
          <h2 id="int-stufen-title" class="brt-h2">{h2}</h2>
          <p class="brt-body brt-int-stages__intro">{intro}</p>
        </header>
        {cards_html}
      </div>
    </section>"""


def _pack_include_label(
    inc: str,
    *,
    block: dict,
    locale: str,
    pkgs: list[dict],
) -> str:
    """Human-readable chip label from stage/package data (not A/B/C codes)."""
    for st in block.get("stages") or []:
        if st["nr"] == inc:
            return _t(st["name"], locale)
    for pkg in pkgs:
        if pkg["nr"] == inc:
            return _t(pkg["name"], locale)
    return inc


_PACK_INCLUDE_STAGE_ALIAS: dict[str, str] = {
    "Top-5 schriftlich": "INT-03-A",
    "Behörden-Modul": "INT-02-B",
    "Kultur-Modul": "INT-02-B",
    "2 Mon. Begleitung": "INT-02-C",
}


def _pack_include_href(
    inc: str,
    *,
    locale: str,
    pkgs: list[dict],
    pre: str,
) -> str | None:
    from _internationale_stufen_detail import STAGE_SLUGS

    stage_nr = inc if inc in STAGE_SLUGS else _PACK_INCLUDE_STAGE_ALIAS.get(inc)
    if stage_nr:
        return stage_detail_href(stage_nr=stage_nr, locale=locale)
    for pkg in pkgs:
        if pkg["nr"] == inc:
            return f"#{pkg['nr'].lower()}"
    if inc == "RA-01":
        return f"{pre}{'angebote/kmu/' if locale != 'en' else 'services/smb/'}"
    if inc == "Förder-Check":
        return "#leistungen"
    return None


def _expanded_pkg_includes(pkg: dict, pkgs: list[dict]) -> frozenset[str]:
    """Resolve nested package includes (e.g. P3 → P2 → A+B+C+D)."""
    out: set[str] = set()
    for inc in pkg.get("includes", []):
        sub = next((p for p in pkgs if p["nr"] == inc), None)
        if sub is not None:
            out |= set(_expanded_pkg_includes(sub, pkgs))
        else:
            out.add(inc)
    return frozenset(out)


_INT01_MATRIX_EXTRAS: list[dict] = [
    {
        "key": "Förder-Check",
        "label": {"de": "Förder-Check", "en": "Funding check", "ru": "Проверка субсидий"},
        "solo": None,
        "href": "#leistungen",
    },
]


def _matrix_row_cells(item_key: str, *, pkgs: list[dict], locale: str = "de") -> list[str]:
    incl_aria = {"de": "Enthalten", "en": "Included", "ru": "Включено"}[locale]
    cells = []
    for pkg in pkgs:
        if item_key in _expanded_pkg_includes(pkg, pkgs):
            cells.append(f'<td><span class="brt-int-matrix__yes" aria-label="{incl_aria}">✓</span></td>')
        else:
            cells.append('<td><span class="brt-int-matrix__no" aria-hidden="true">—</span></td>')
    return cells


def _pack_include_chip(
    inc: str,
    *,
    block: dict,
    locale: str,
    pkgs: list[dict],
    pre: str,
) -> str:
    label = _pack_include_label(inc, block=block, locale=locale, pkgs=pkgs)
    href = _pack_include_href(inc, locale=locale, pkgs=pkgs, pre=pre)
    if href:
        return f'<li><a class="brt-int-pack__chip" href="{href}">{label}</a></li>'
    return f'<li><span class="brt-int-pack__chip">{label}</span></li>'


def _stage_row_label(snr: str, *, block: dict, locale: str) -> str:
    for st in block.get("stages") or []:
        if st["nr"] == snr:
            return _t(st["name"], locale)
    return customer_label(snr) if snr.startswith(("INT-", "RA-")) else snr


def _matrix_stage_keys(block: dict) -> list[str]:
    """Stage row keys for comparison matrix (INT-XX-X only)."""
    cols = block.get("package_cols") or []
    stage_keys = [c for c in cols if isinstance(c, str) and c.startswith("INT-")]
    if stage_keys:
        return stage_keys
    pkgs = block.get("packages") or []
    stages = block.get("stages") or []
    if len(pkgs) >= 2 and stages:
        return [s["nr"] for s in stages]
    return []


def international_packages_section(*, parent_nr: str, locale: str, contact_href: str, pre: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or not block.get("packages") or block.get("offer_model") == "project":
        return ""
    pkgs = block["packages"]
    h2 = _t(block.get("packages_h2", {"de": "Pakete", "en": "Bundles", "ru": "Пакеты"}), locale)
    save_l = {"de": "Sie sparen", "en": "You save", "ru": "Экономия"}[locale]
    incl_l = {"de": "Enthalten", "en": "Includes", "ru": "Включено"}[locale]
    btn_pkg = {"de": "Paket besprechen", "en": "Discuss bundle", "ru": "Обсудить"}[locale]
    badge_l = {"de": "Meistgebucht", "en": "Most popular", "ru": "Популярный"}[locale]
    compare_l = {"de": "Vergleich auf einen Blick", "en": "Compare at a glance", "ru": "Сравнение"}[locale]
    total_l = {"de": "Paketpreis", "en": "Bundle price", "ru": "Цена пакета"}[locale]
    alone_l = {"de": "Einzeln", "en": "Individual", "ru": "Отдельно"}[locale]
    cards = []
    for pkg in pkgs:
        feat = pkg.get("featured")
        feat_cls = " brt-int-pack--featured" if feat else ""
        sav = package_savings(pkg)
        sav_html = f'<p class="brt-int-pack__save">{save_l} {format_eur(sav)}</p>' if sav else ""
        badge = f'<span class="brt-int-pack__badge">{badge_l}</span>' if feat else ""
        chips = "".join(
            _pack_include_chip(inc, block=block, locale=locale, pkgs=pkgs, pre=pre)
            for inc in pkg["includes"]
        )
        teaser = _t(pkg.get("teaser", ""), locale)
        teaser_html = f'<p class="brt-int-pack__teaser">{teaser}</p>' if teaser else ""
        dur = _t(pkg.get("duration", ""), locale)
        dur_html = f'<p class="brt-int-pack__duration">{dur}</p>' if dur else ""
        cards.append(
            f'<li class="brt-int-pack brt-card brt-hover-lift{feat_cls}" id="{pkg["nr"].lower()}">'
            f"{badge}"
            f'<h3 class="brt-int-pack__title">{_t(pkg["name"], locale)}</h3>'
            f'<p class="brt-int-pack__price">{package_price_label(pkg, locale)}</p>'
            f"{dur_html}"
            f"{sav_html}"
            f"{teaser_html}"
            f'<p class="brt-int-pack__incl-label">{incl_l}</p>'
            f'<ul class="brt-int-pack__includes">{chips}</ul>'
            f'<p class="brt-int-pack__cta"><a class="brt-btn{" brt-btn--on-dark" if feat else ""}" href="{contact_href}">{btn_pkg}</a></p>'
            f"</li>"
        )
    matrix = ""
    stage_nrs = _matrix_stage_keys(block)
    if stage_nrs and pkgs:
        hdr = "".join(
            f'<th scope="col" class="brt-int-matrix__pkg{" brt-int-matrix__pkg--featured" if p.get("featured") else ""}">'
            f'<a class="brt-int-matrix__pkg-link" href="#{p["nr"].lower()}">'
            f'<span class="brt-int-matrix__pkg-name">{_t(p["name"], locale)}</span>'
            f"</a></th>"
            for p in pkgs
        )
        rows = []
        stage_by_nr = {s["nr"]: s for s in block.get("stages") or []}
        for snr in stage_nrs:
            cells = _matrix_row_cells(snr, pkgs=pkgs, locale=locale)
            stage_label = _stage_row_label(snr, block=block, locale=locale)
            stage_href = stage_detail_href(stage_nr=snr, locale=locale) if snr in stage_by_nr else None
            row_head = (
                f'<a class="brt-int-matrix__stage-link" href="{stage_href}">{stage_label}</a>'
                if stage_href
                else stage_label
            )
            solo_price = (
                stage_price_label(stage_by_nr[snr], locale) if snr in stage_by_nr else "—"
            )
            rows.append(
                f'<tr><th scope="row">{row_head}</th>'
                f'<td class="brt-int-matrix__solo">{solo_price}</td>'
                f'{"".join(cells)}</tr>'
            )
        extras = _INT01_MATRIX_EXTRAS if parent_nr == "INT-01" else []
        for extra in extras:
            key = extra["key"]
            label = _t(extra["label"], locale)
            href = extra.get("href")
            row_head = (
                f'<a class="brt-int-matrix__stage-link" href="{href}">{label}</a>'
                if href
                else label
            )
            solo = format_eur(extra["solo"]) if extra.get("solo") else "—"
            rows.append(
                f'<tr class="brt-int-matrix__extra-row"><th scope="row">{row_head}</th>'
                f'<td class="brt-int-matrix__solo">{solo}</td>'
                f'{"".join(_matrix_row_cells(key, pkgs=pkgs, locale=locale))}</tr>'
            )
        price_row = "".join(
            f'<td class="brt-int-matrix__total{" brt-int-matrix__total--featured" if p.get("featured") else ""}">'
            f'<strong>{package_price_label(p, locale)}</strong></td>'
            for p in pkgs
        )
        matrix = f"""
        <div class="brt-int-matrix brt-fade-up">
          <h3 class="brt-int-matrix__title">{compare_l}</h3>
          <div class="brt-int-matrix__scroll">
            <table class="brt-int-matrix__table">
              <caption class="brt-sr-only">{h2}</caption>
              <thead><tr><th scope="col">{"Stufe" if locale == "de" else "Stage" if locale == "en" else "Этап"}</th><th scope="col">{alone_l}</th>{hdr}</tr></thead>
              <tbody>{"".join(rows)}
                <tr class="brt-int-matrix__foot"><th scope="row">{total_l}</th><td></td>{price_row}</tr>
              </tbody>
            </table>
          </div>
        </div>"""
    pkgs_slider_i18n = {
        "de": ("Pakete", "Vorheriges Paket", "Nächstes Paket"),
        "en": ("Bundles", "Previous bundle", "Next bundle"),
        "ru": ("Пакеты", "Предыдущий пакет", "Следующий пакет"),
    }[locale]
    if len(pkgs) > 1:
        cards_block = cards_slider_block(
            "".join(cards),
            aria_label=pkgs_slider_i18n[0],
            prev_label=pkgs_slider_i18n[1],
            next_label=pkgs_slider_i18n[2],
            autoplay_ms=10000,
        )
        cards_html = f'<div class="brt-int-packs-slider">{cards_block}</div>'
    else:
        cards_html = f'<ul class="brt-int-packs brt-stagger brt-int-packs--solo">{"".join(cards)}</ul>'
    intro_pkg = _t(
        block.get(
            "packages_intro",
            {
                "de": "Wer mehrere Stufen kombiniert, zahlt weniger als die Summe der Einzelpreise.",
                "en": "Combine stages and pay less than the sum of individual prices.",
                "ru": "Комбинируйте этапы — дешевле, чем по отдельности.",
            },
        ),
        locale,
    )
    bundle_tag = {"de": "BUNDLE", "en": "BUNDLE", "ru": "ПАКЕТ"}[locale]
    return f"""
    <section class="brt-section brt-int-packs-wrap" id="pakete" aria-labelledby="int-pakete-title">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{bundle_tag}</p>
          <h2 id="int-pakete-title" class="brt-h2">{h2}</h2>
          <p class="brt-body">{intro_pkg}</p>
        </header>
        {cards_html}
        {matrix}
      </div>
    </section>"""


def international_excluded_section(*, parent_nr: str, locale: str) -> str:
    block = INT_STAGES.get(parent_nr)
    if not block or not block.get("excluded") or block.get("offer_model") == "project":
        return ""
    h2 = {"de": "Nicht enthalten", "en": "Not included", "ru": "Не входит"}[locale]
    items = "".join(f"<li>{x}</li>" for x in _t(block["excluded"], locale))
    return f"""
    <section class="brt-section brt-section--alt brt-int-excluded" id="ausgeschlossen">
      <div class="brt-container brt-int-excluded__inner brt-fade-up">
        <h2 class="brt-h2">{h2}</h2>
        <ul class="brt-list-check brt-int-excluded__list">{items}</ul>
      </div>
    </section>"""


def international_process_section(steps: list[tuple[str, str]], *, locale: str) -> str:
    h2 = {"de": "Typischer Ablauf", "en": "Typical process", "ru": "Типичный процесс"}[locale]
    items = []
    for i, (title, body) in enumerate(steps, 1):
        items.append(
            f'<li class="brt-int-process__item">'
            f'<span class="brt-int-process__num" aria-hidden="true">{i}</span>'
            f'<div class="brt-int-process__body"><h3 class="brt-int-process__title">{title}</h3>'
            f'<p class="brt-body">{body}</p></div></li>'
        )
    return f"""
    <section class="brt-section brt-int-process-wrap" id="ablauf">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <h2 class="brt-h2">{h2}</h2>
        </header>
        <ol class="brt-int-process brt-stagger">{"".join(items)}</ol>
      </div>
    </section>"""


def international_audience_section(
    *,
    intro: str,
    items: list[str],
    locale: str,
    depth: int,
    offer_nr: str,
    lead: str = "",
) -> str:
    tag = {"de": "ZIELGRUPPE", "en": "WHO IT'S FOR", "ru": "ДЛЯ КОГО"}[locale]
    ki_l = {"de": "KI-generiertes Bild", "en": "AI-generated image", "ru": "ИИ-изображение"}[locale]
    lead_html = f'<p class="brt-body">{lead}</p>' if lead else ""
    lis = "".join(f"<li>{x}</li>" for x in items)
    img_src = _INT_AUDIENCE_IMAGES.get(offer_nr)
    if img_src:
        alt = _INT_AUDIENCE_ALT.get(offer_nr, {}).get(locale, intro)
        media = f"""        <div class="brt-split__media brt-fade-up" style="--fade-delay: 120ms">
          {img_html(img_src, alt, depth, aspect="4/3")}
          <span class="brt-ki-image-label">{ki_l}</span>
        </div>"""
        return f"""
    <section class="brt-section" id="fuer-wen" aria-labelledby="fuer-wen-title">
      <div class="brt-container brt-split">
        <div class="brt-split__text brt-fade-up">
          <p class="brt-tag">{tag}</p>
          <h2 id="fuer-wen-title" class="brt-h2">{intro}</h2>
          {lead_html}
          <ul class="brt-list-check">{lis}</ul>
        </div>
{media}
      </div>
    </section>"""
    return f"""
    <section class="brt-section" id="fuer-wen" aria-labelledby="fuer-wen-title">
      <div class="brt-container brt-split brt-split--text-only">
        <div class="brt-split__text brt-fade-up">
          <p class="brt-tag">{tag}</p>
          <h2 id="fuer-wen-title" class="brt-h2">{intro}</h2>
          {lead_html}
          <ul class="brt-list-check">{lis}</ul>
        </div>
      </div>
    </section>"""


def international_outcome_section(*, items: list[str], locale: str) -> str:
    h2 = {"de": "Ihr Ergebnis", "en": "Your outcome", "ru": "Ваш результат"}[locale]
    cards = "".join(
        f'<li class="brt-int-outcome__item"><p class="brt-int-outcome__text">{x}</p></li>' for x in items
    )
    return f"""
    <section class="brt-section brt-section--alt brt-int-outcome-wrap" id="ergebnis">
      <div class="brt-container">
        <h2 class="brt-h2 brt-fade-up">{h2}</h2>
        <ul class="brt-int-outcome brt-stagger">{cards}</ul>
      </div>
    </section>"""


def international_stage_scope_section(
    *,
    leistungen: list[str],
    excluded: list[str],
    locale: str,
) -> str:
    """Included vs excluded — side-by-side on stage subpages."""
    incl_h2 = {"de": "Was Sie bekommen", "en": "What you get", "ru": "Что вы получаете"}[locale]
    excl_h2 = {"de": "Nicht enthalten", "en": "Not included", "ru": "Не входит"}[locale]
    section_tag = {"de": "Umfang", "en": "Scope", "ru": "Объём"}[locale]
    section_h2 = {
        "de": "Leistungsumfang — klar abgegrenzt",
        "en": "Scope — clearly defined",
        "ru": "Объём — чётко определён",
    }[locale]
    incl_label = {"de": "Enthalten", "en": "Included", "ru": "Включено"}[locale]
    excl_label = {"de": "Ausgeschlossen", "en": "Excluded", "ru": "Не входит"}[locale]
    incl_lis = "".join(f"<li>{x}</li>" for x in leistungen)
    dual = " brt-int-scope--dual" if excluded else ""
    excl_col = ""
    if excluded:
        excl_lis = "".join(f"<li>{x}</li>" for x in excluded)
        excl_col = f"""
          <article class="brt-int-scope__col brt-int-scope__col--excluded brt-card brt-hover-lift">
            <p class="brt-int-scope__label brt-int-scope__label--excluded">{excl_label}</p>
            <h3 class="brt-int-scope__title">{excl_h2}</h3>
            <ul class="brt-int-scope__list brt-int-scope__list--excluded">{excl_lis}</ul>
          </article>"""
    return f"""
    <section class="brt-section brt-section--alt brt-int-scope-wrap" id="leistungen">
      <div class="brt-container">
        <header class="brt-section__header brt-section__header--center brt-fade-up">
          <p class="brt-tag">{section_tag.upper()}</p>
          <h2 class="brt-h2">{section_h2}</h2>
        </header>
        <div class="brt-int-scope{dual} brt-stagger">
          <article class="brt-int-scope__col brt-int-scope__col--included brt-card brt-hover-lift">
            <p class="brt-int-scope__label brt-int-scope__label--accent">{incl_label}</p>
            <h3 class="brt-int-scope__title">{incl_h2}</h3>
            <ul class="brt-int-scope__list brt-int-scope__list--included">{incl_lis}</ul>
          </article>{excl_col}
        </div>
      </div>
    </section>"""


def international_leistungen_section(*, items: list[str], locale: str, section_alt: bool = False) -> str:
    h2 = {"de": "Was Sie bekommen", "en": "What you get", "ru": "Что вы получаете"}[locale]
    lis = "".join(f"<li>{x}</li>" for x in items)
    alt = " brt-section--alt" if section_alt else ""
    return f"""
    <section class="brt-section{alt}" id="leistungen">
      <div class="brt-container">
        <h2 class="brt-h2 brt-fade-up">{h2}</h2>
        <ul class="brt-list-check brt-fade-up">{lis}</ul>
      </div>
    </section>"""


def international_stage_excluded_section(*, items: list[str], locale: str) -> str:
    if not items:
        return ""
    h2 = {"de": "Nicht enthalten", "en": "Not included", "ru": "Не входит"}[locale]
    lis = "".join(f"<li>{x}</li>" for x in items)
    return f"""
    <section class="brt-section brt-section--alt brt-int-excluded" id="ausgeschlossen">
      <div class="brt-container brt-int-excluded__inner brt-fade-up">
        <h2 class="brt-h2">{h2}</h2>
        <ul class="brt-list-check brt-int-excluded__list">{lis}</ul>
      </div>
    </section>"""


def _find_package(pkg_nr: str) -> tuple[str, dict] | None:
    for parent, block in INT_STAGES.items():
        for pkg in block.get("packages") or []:
            if pkg["nr"] == pkg_nr:
                return parent, pkg
    return None


def _offer_rubric_url(*, offer_nr: str, locale: str, pre: str, anchor: str = "") -> str:
    if locale == "en":
        slug = EN_SLUG_MAP[offer_nr]
        path = f"international-services/{slug}/"
    elif locale == "ru":
        slug = RU_SLUG_MAP[offer_nr]
        path = f"ru/internationale-angebote/{slug}/"
    else:
        slug = next(c["slug"] for c in INT_OFFER_CONFIGS_DE if c["nr"] == offer_nr)
        path = f"internationale-angebote/{slug}/"
    frag = f"#{anchor}" if anchor else ""
    return f"{pre}{path}{frag}"


def _package_teaser(pkg: dict, block: dict, locale: str) -> str:
    if pkg.get("teaser"):
        return _t(pkg["teaser"], locale)
    parts: list[str] = []
    for inc in pkg.get("includes", []):
        if inc.startswith("INT-"):
            for st in block.get("stages", []):
                if st["nr"] == inc:
                    parts.append(_t(st["name"], locale))
                    break
        else:
            parts.append(customer_label(inc) if inc.startswith(("INT-", "RA-")) else inc)
    return humanize_customer_text(" + ".join(parts))


def international_next_stages_section(
    *,
    stage: dict,
    locale: str,
    pre: str,
) -> str:
    next_nrs = (stage.get("next") or [])[:3]
    if not next_nrs:
        return ""
    h2 = {
        "de": "Empfohlene Folgestufen",
        "en": "Recommended next stages",
        "ru": "Рекомендуемые следующие этапы",
    }[locale]
    cards = []
    for nr in next_nrs:
        target: dict | None = None
        href = ""
        price = ""
        name = ""
        teaser = ""
        try:
            target = merged_stage(nr)
            href = stage_url(nr, locale, pre)
            price = stage_price_label(target, locale)
            name = _t(target["name"], locale)
            teaser = _t(target.get("teaser", ""), locale)
        except KeyError:
            found = _find_package(nr)
            if found:
                parent, pkg = found
                block = INT_STAGES[parent]
                href = _offer_rubric_url(
                    offer_nr=parent,
                    locale=locale,
                    pre=pre,
                    anchor=pkg["nr"].lower(),
                )
                price = format_eur(pkg["price"])
                name = _t(pkg["name"], locale)
                teaser = _package_teaser(pkg, block, locale)
        if not target and not href:
            continue
        cards.append(
            f'<li class="brt-card brt-hover-lift brt-int-next__card">'
            f'<a class="brt-card__link" href="{href}">'
            f'<h3 class="brt-h3">{name}</h3>'
            f'<p class="brt-body">{teaser}</p>'
            f'<p class="brt-meta"><strong>{price}</strong></p>'
            f"</a></li>"
        )
    if not cards:
        return ""
    return f"""
    <section class="brt-section brt-int-next-wrap" id="folgestufen">
      <div class="brt-container">
        <h2 class="brt-h2 brt-fade-up">{h2}</h2>
        <ul class="brt-cards-3col brt-stagger">{"".join(cards)}</ul>
      </div>
    </section>"""


def _stage_price_display(stage: dict, locale: str) -> str:
    if stage.get("price") == 0:
        return {"de": "Kostenlos", "en": "Free", "ru": "Бесплатно"}[locale]
    return stage_price_label(stage, locale)


def international_single_stage_price_banner(
    *,
    stage: dict,
    locale: str,
    pre: str,
    contact_href: str | None = None,
) -> str:
    price_page = {"de": "preise", "en": "pricing", "ru": "preise"}[locale]
    link = {"de": "Alle Preise", "ru": "Все цены", "en": "All prices"}[locale]
    btn_book = {"de": "Termin anfragen", "en": "Request appointment", "ru": "Записаться"}[locale]
    tag = {
        "de": "PREIS (NETTO ZZGL. UST.)",
        "en": "PRICE (NET PLUS VAT)",
        "ru": "ЦЕНА (НЕТТО + НДС)",
    }[locale]
    contact = contact_href or f"{pre}{'contact' if locale == 'en' else 'kontakt'}/"
    stage_name = _t(stage["name"], locale)
    price = _stage_price_display(stage, locale)
    duration = _t(stage.get("duration", ""), locale)
    duration_part = f" · {duration}" if duration else ""
    return f"""<section class="brt-section brt-section--alt" id="preis">
      <div class="brt-container brt-highlight-box brt-fade-up">
        <p class="brt-tag">{tag}</p>
        <h2 class="brt-h2">{stage_name}</h2>
        <p class="brt-body"><strong>{price}</strong>{duration_part}</p>
        <p class="brt-page-hero__actions">
          <a class="brt-btn" href="{contact}">{btn_book}</a>
          <a class="brt-btn brt-btn--outline" href="{pre}{price_page}/#international">{link}</a>
        </p>
      </div>
    </section>"""


def _int_price_tier(
    *,
    name: str,
    price: str,
    href: str,
    sub: str = "",
    featured: bool = False,
) -> str:
    feat_cls = " brt-int-price-tier--featured" if featured else ""
    sub_html = f'<span class="brt-int-price-tier__sub">{sub}</span>' if sub else ""
    return (
        f'<li class="brt-int-price-tier{feat_cls}">'
        f'<a class="brt-int-price-tier__link" href="{href}">'
        f'<span class="brt-int-price-tier__body">'
        f'<span class="brt-int-price-tier__name">{name}</span>'
        f"{sub_html}"
        f"</span>"
        f'<span class="brt-int-price-tier__price">{price}</span>'
        f"</a></li>"
    )


def international_stages_price_banner(*, offer: dict, parent_nr: str, locale: str, pre: str) -> str:
    block = INT_STAGES.get(parent_nr)
    price_h2 = {"de": "Preise", "ru": "Цены", "en": "Pricing"}[locale]
    price_page = {"de": "preise", "en": "pricing", "ru": "preise"}[locale]
    link = {"de": "Alle Preise auf der Preisseite", "ru": "Все цены", "en": "All prices on pricing page"}[locale]
    netto = {"de": "netto zzgl. USt.", "en": "net plus VAT", "ru": "нетто + НДС"}[locale]
    if not block:
        detail = offer.get("price_detail", "")
        return f"""<section class="brt-section brt-int-price-wrap" id="preis">
      <div class="brt-container brt-int-price-banner brt-fade-up">
        <p class="brt-tag brt-int-price-banner__tag">{netto.upper()}</p>
        <h2 class="brt-h2 brt-int-price-banner__h2">{price_h2}</h2>
        <p class="brt-int-price-banner__main">{offer_price_text(offer)}</p>
        <p class="brt-int-price-banner__detail">{detail}</p>
        <p class="brt-int-price-banner__meta"><a class="brt-btn brt-btn--outline brt-btn--on-dark" href="{pre}{price_page}/#international">{link}</a></p>
      </div>
    </section>"""

    intro = {
        "de": "Einzelstufen oder Paket — Sie wählen die Tiefe. Pakete sind günstiger als die Summe der Einzelbuchungen.",
        "en": "Book individual stages or save with a bundle — you choose the depth.",
        "ru": "Отдельные этапы или пакет — вы выбираете глубину. Пакеты выгоднее суммы по отдельности.",
    }[locale]
    stages_h3 = {"de": "Einzelstufen", "en": "Individual stages", "ru": "Отдельные этапы"}[locale]
    pkgs_h3 = {"de": "Pakete", "en": "Bundles", "ru": "Пакеты"}[locale]
    save_l = {"de": "Sie sparen", "en": "You save", "ru": "Экономия"}[locale]
    erst_l = {
        "de": "Erstberatung kostenlos — unverbindlicher Einstieg.",
        "en": "Intro call free — no-obligation starting point.",
        "ru": "Первичная консультация бесплатно.",
    }[locale]

    pkgs = block.get("packages") or []
    stage_items = []
    for st in block.get("stages") or []:
        stage_items.append(
            _int_price_tier(
                name=_t(st["name"], locale),
                price=stage_price_label(st, locale),
                href=stage_detail_href(stage_nr=st["nr"], locale=locale),
            )
        )

    pkg_items = []
    for pkg in pkgs:
        sav = package_savings(pkg)
        sub = f"{save_l} {format_eur(sav)}" if sav else ""
        pkg_items.append(
            _int_price_tier(
                name=_t(pkg["name"], locale),
                price=format_eur(pkg["price"]),
                href=f"#{pkg['nr'].lower()}",
                sub=sub,
                featured=bool(pkg.get("featured")),
            )
        )

    if parent_nr == "INT-01":
        foerder_sub = {
            "de": "Enthalten in Paket P3",
            "en": "Included in bundle P3",
            "ru": "В пакете P3",
        }[locale]
        pkg_items.append(
            _int_price_tier(
                name=_t(_INT01_MATRIX_EXTRAS[0]["label"], locale),
                price="—",
                href="#leistungen",
                sub=foerder_sub,
            )
        )

    stages_block = ""
    if stage_items:
        stages_block = f"""
        <div class="brt-int-price-group brt-fade-up">
          <h3 class="brt-int-price-group__title">{stages_h3}</h3>
          <ul class="brt-int-price-tiers">{"".join(stage_items)}</ul>
        </div>"""

    pkgs_block = ""
    if pkg_items:
        pkgs_block = f"""
        <div class="brt-int-price-group brt-fade-up">
          <h3 class="brt-int-price-group__title">{pkgs_h3}</h3>
          <ul class="brt-int-price-tiers">{"".join(pkg_items)}</ul>
        </div>"""

    cols = " brt-int-price-board--dual" if stages_block and pkgs_block else ""
    return f"""<section class="brt-section brt-section--alt brt-int-price-wrap" id="preis">
      <div class="brt-container">
        <header class="brt-section__header brt-fade-up">
          <p class="brt-tag">{netto.upper()}</p>
          <h2 class="brt-h2">{price_h2}</h2>
          <p class="brt-body brt-int-price__intro">{intro}</p>
          <p class="brt-int-price__lead">{offer_price_text(offer)}</p>
        </header>
        <div class="brt-int-price-board{cols}">{stages_block}{pkgs_block}</div>
        <p class="brt-meta brt-int-price__foot brt-fade-up">{erst_l} <a href="{pre}{price_page}/#international">{link}</a></p>
      </div>
    </section>"""
