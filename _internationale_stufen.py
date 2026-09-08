"""Stage & package configs for international offers (INT-01 … INT-04).

Source: Angebote/Angebot RU/stufen/*.md
"""
from __future__ import annotations

from _pricing import format_eur

# Customer journey on /internationale-angebote/ index
INT_JOURNEY: dict[str, list[dict]] = {
    "de": [
        {"key": "start", "label": "START", "question": "Ich will in DE gründen — wo fange ich an?", "nr": "INT-00", "price": 50},
        {"key": "roadmap", "label": "ROADMAP", "question": "Ich will den gesamten Weg verstehen", "nr": "INT-01-B", "price": 1900},
        {"key": "launch", "label": "LAUNCH", "question": "Ich brauche Begleitung bei der Umsetzung", "nr": "INT-01-C", "price": 2900},
        {"key": "check", "label": "CHECK", "question": "Mein Business läuft — wo hakt es?", "nr": "INT-03-A", "price": 790},
        {"key": "scale", "label": "RISK & SCALE", "question": "Wir wollen wachsen — vorbereitet?", "nr": "INT-03-P3", "price": 7900},
    ],
    "en": [
        {"key": "start", "label": "START", "question": "I want to start in Germany — where do I begin?", "nr": "INT-00", "price": 50},
        {"key": "roadmap", "label": "ROADMAP", "question": "I want to understand the full path", "nr": "INT-01-B", "price": 1900},
        {"key": "launch", "label": "LAUNCH", "question": "I need hands-on launch support", "nr": "INT-01-C", "price": 2900},
        {"key": "check", "label": "CHECK", "question": "Business is running — what's weak?", "nr": "INT-03-A", "price": 790},
        {"key": "scale", "label": "RISK & SCALE", "question": "We're growing — are we ready?", "nr": "INT-03-P3", "price": 7900},
    ],
    "ru": [
        {"key": "start", "label": "START", "question": "Хочу открыть бизнес в Германии — с чего начать?", "nr": "INT-00", "price": 50},
        {"key": "roadmap", "label": "ROADMAP", "question": "Хочу понять весь путь", "nr": "INT-01-B", "price": 1900},
        {"key": "launch", "label": "LAUNCH", "question": "Нужно сопровождение при запуске", "nr": "INT-01-C", "price": 2900},
        {"key": "check", "label": "CHECK", "question": "Бизнес работает — где слабые места?", "nr": "INT-03-A", "price": 790},
        {"key": "scale", "label": "RISK & SCALE", "question": "Растём — готовы ли мы?", "nr": "INT-03-P3", "price": 7900},
    ],
}

_STAGE = dict  # alias for typing clarity

INT_STAGES: dict[str, dict] = {
    "INT-01": {
        "stages_h2": {"de": "Einzelstufen — einzeln buchbar", "en": "Individual stages — book separately", "ru": "Отдельные этапы"},
        "stages_intro": {
            "de": "Wie bei unserer Risikoanalyse: Sie wählen die Tiefe — jede Stufe liefert ein klares Ergebnis.",
            "en": "Like our risk analysis: you choose the depth — each stage delivers a clear outcome.",
            "ru": "Как при анализе рисков: вы выбираете глубину — каждый этап даёт понятный результат.",
        },
        "stages": [
            {
                "nr": "INT-01-A",
                "name": {"de": "Business Check", "en": "Business Check", "ru": "Business Check"},
                "teaser": {
                    "de": "Standortbestimmung: Idee, Rechtsform-Optionen, Budget, Top-Risiken — bevor Notar und Steuerberater.",
                    "en": "Reality check: idea, legal form options, budget, top risks — before notary and tax advisor.",
                    "ru": "Оценка идеи, формы бизнеса, бюджета и рисков — до нотариуса и Steuerberater.",
                },
                "price": 990,
                "duration": {"de": "2–3 h + Kurzprotokoll", "en": "2–3 h + brief report", "ru": "2–3 ч + отчёт"},
                "highlights": {
                    "de": ["Rechtsform-Optionen einordnen", "Behördenweg grob", "Top-5 Gründungsrisiken", "Nächste Schritte"],
                    "en": ["Legal form options explained", "Authority roadmap", "Top 5 founding risks", "Next steps"],
                    "ru": ["Формы бизнеса", "Путь через ведомства", "Топ-5 рисков", "Следующие шаги"],
                },
            },
            {
                "nr": "INT-01-B",
                "name": {"de": "Launch Roadmap", "en": "Launch Roadmap", "ru": "Launch Roadmap"},
                "teaser": {
                    "de": "Persönlicher Plan Woche 1 → Monat 3: Pre-Launch, Launch, erste Kunden, erste 90 Tage.",
                    "en": "Personal plan week 1 → month 3: pre-launch, launch, first clients, first 90 days.",
                    "ru": "План неделя 1 → месяц 3: подготовка, запуск, первые клиенты, 90 дней.",
                },
                "price": 1900,
                "duration": {"de": "Dokument + Review-Call", "en": "Document + review call", "ru": "Документ + созвон"},
                "highlights": {
                    "de": ["4 Phasen mit Checklisten", "ELSTER & IHK-Hinweise", "Vertrieb DE-Markt", "KPIs erste 90 Tage"],
                    "en": ["4 phases with checklists", "ELSTER & chamber hints", "German market sales", "First 90-day KPIs"],
                    "ru": ["4 фазы", "ELSTER и IHK", "Продажи в DE", "KPI 90 дней"],
                },
            },
            {
                "nr": "INT-01-C",
                "name": {"de": "Launch Begleitung", "en": "Launch Support", "ru": "Сопровождение запуска"},
                "teaser": {
                    "de": "Hands-on: Timelines, Spezialisten, Fragen vorbereiten — nichts geht verloren.",
                    "en": "Hands-on: timelines, specialists, prep for appointments — nothing gets lost.",
                    "ru": "Практика: сроки, специалисты, подготовка — ничего не теряется.",
                },
                "price": 2900,
                "duration": {"de": "4–12 Wochen", "en": "4–12 weeks", "ru": "4–12 недель"},
                "highlights": {
                    "de": ["Wöchentliche Calls DE/EN/RU", "Behörden & Bank vorbereiten", "Netzwerk Notar/Steuerberater", "Übergabeprotokoll"],
                    "en": ["Weekly calls DE/EN/RU", "Prep for authorities & bank", "Notary/tax advisor network", "Handover protocol"],
                    "ru": ["Еженедельные созвоны", "Подготовка к ведомствам", "Сеть специалистов", "Протокол передачи"],
                },
            },
            {
                "nr": "INT-01-D",
                "name": {"de": "Gründungs-Risiko-Check", "en": "Founding Risk Check", "ru": "Риск-чек перед запуском"},
                "teaser": {
                    "de": "Blind Spots vor Go-Live: Banking, Verträge, Aufenthalt — Top-5 priorisiert.",
                    "en": "Blind spots before go-live: banking, contracts, residence — prioritised top 5.",
                    "ru": "Слепые зоны: банк, договоры, Aufenthalt — топ-5.",
                },
                "price": 1250,
                "duration": {"de": "Workshop + Report", "en": "Workshop + report", "ru": "Воркшоп + отчёт"},
                "highlights": {
                    "de": ["Beraterium-Bewertungslogik", "Schaden in Euro grob", "Maßnahmen vor Launch", "Brücke zu RA-02"],
                    "en": ["Beraterium evaluation logic", "Rough euro impact", "Pre-launch actions", "Bridge to RA-02"],
                    "ru": ["Метод Beraterium", "Ущерб в €", "До запуска", "Связь с RA-02"],
                },
            },
        ],
        "packages_h2": {"de": "Pakete — günstiger als einzeln", "en": "Bundles — save vs. individual stages", "ru": "Пакеты — выгоднее"},
        "packages": [
            {
                "nr": "INT-01-P1",
                "name": {"de": "Roadmap + Begleitung", "en": "Roadmap + Support", "ru": "Roadmap + сопровождение"},
                "price": 4490,
                "single_sum": 4800,
                "includes": ["INT-01-B", "INT-01-C"],
                "featured": False,
            },
            {
                "nr": "INT-01-P2",
                "name": {"de": "Gründung 360°", "en": "Founding 360°", "ru": "Gründung 360°"},
                "price": 5490,
                "single_sum": 6140,
                "includes": ["INT-01-A", "INT-01-B", "INT-01-C", "INT-01-D"],
                "featured": True,
            },
            {
                "nr": "INT-01-P3",
                "name": {"de": "Gründung 360° + Förder-Check", "en": "Founding 360° + funding check", "ru": "360° + Förder-Check"},
                "price": 5990,
                "single_sum": None,
                "includes": ["INT-01-P2", "Förder-Check"],
                "featured": False,
            },
        ],
        "package_cols": ["INT-01-A", "INT-01-B", "INT-01-C", "INT-01-D"],
        "excluded": {
            "de": [
                "Rechtsberatung (RDG) und Steuerberatung (StBerG)",
                "Gewerbeanmeldung oder Notartermine in unserem Namen",
                "Fertiger Businessplan durch uns — Struktur ja, Inhalt mit Steuerberater",
            ],
            "en": [
                "Legal advice (RDG) and tax advice (StBerG)",
                "Trade registration or notary appointments in our name",
                "Full business plan by us — structure yes, content with your tax advisor",
            ],
            "ru": [
                "Юридические и налоговые услуги (RDG/StBerG)",
                "Регистрация от нашего имени",
                "Готовый бизнес-план — структура да, содержание со Steuerberater",
            ],
        },
    },
    "INT-02": {
        "stages_h2": {"de": "Module — flexibel buchbar", "en": "Modules — flexible booking", "ru": "Модули"},
        "stages_intro": {
            "de": "Einzelstunde, Themenmodul oder Monatsbegleitung — parallel zur Gründung oder danach.",
            "en": "Single hour, topic module, or monthly support — parallel to founding or after.",
            "ru": "Час, модуль или сопровождение — параллельно с Gründung или после.",
        },
        "stages": [
            {"nr": "INT-02-A", "name": {"de": "Einzelstunde", "en": "Single hour", "ru": "Час"}, "teaser": {"de": "1:1 Coaching — flexibles Thema.", "en": "1:1 coaching — flexible topic.", "ru": "1:1 — любая тема."}, "price": 180, "unit": {"de": "/ Std.", "en": "/ hour", "ru": "/ час"}, "duration": {"de": "60 Min.", "en": "60 min.", "ru": "60 мин."}, "highlights": {"de": ["Behördenbriefe", "Terminvorbereitung", "Kultur & Kommunikation"], "en": ["Authority letters", "Appointment prep", "Culture & communication"], "ru": ["Письма", "Подготовка", "Культура"]}},
            {"nr": "INT-02-B", "name": {"de": "Themenmodul", "en": "Topic module", "ru": "Тематический модуль"}, "teaser": {"de": "3× Session: Behörden, ELSTER, Kultur — wählbar.", "en": "3 sessions: authorities, ELSTER, culture — pick topics.", "ru": "3 сессии: ведомства, ELSTER, культура."}, "price": 490, "duration": {"de": "3× 60 Min.", "en": "3× 60 min.", "ru": "3× 60 мин."}, "highlights": {"de": ["Behörden-Modul", "ELSTER-Modul", "Kommunikation DE"], "en": ["Authorities module", "ELSTER module", "DE communication"], "ru": ["Ведомства", "ELSTER", "Коммуникация"]}},
            {"nr": "INT-02-C", "name": {"de": "6-Monats-Begleitung", "en": "6-month support", "ru": "6 месяцев"}, "teaser": {"de": "Kontinuierliche 1:1-Begleitung beim Ankommen.", "en": "Continuous 1:1 support while settling in.", "ru": "Постоянное сопровождение."}, "price": 2900, "duration": {"de": "6 Monate", "en": "6 months", "ru": "6 месяцев"}, "highlights": {"de": ["2×/Monat Sessions", "Asynchroner Support", "Individueller Plan"], "en": ["2×/month sessions", "Async support", "Individual plan"], "ru": ["2×/мес.", "Поддержка", "План"]}},
            {"nr": "INT-02-D", "name": {"de": "Objektsuche", "en": "Property search", "ru": "Поиск объекта"}, "teaser": {"de": "Wohnung oder Gewerbe — optional.", "en": "Residential or commercial — optional.", "ru": "Жильё или Gewerbe."}, "price": 1900, "price_from": True, "duration": {"de": "Nach Umfang", "en": "Scope-based", "ru": "По объёму"}, "highlights": {"de": ["Kriterien & Anschreiben", "Besichtigung", "Mietvertrag verstehen"], "en": ["Criteria & outreach", "Viewings", "Lease review"], "ru": ["Критерии", "Просмотры", "Договор"]}},
        ],
        "packages": [
            {"nr": "INT-02-P", "name": {"de": "Integrations-Paket", "en": "Integration bundle", "ru": "Интеграция"}, "price": 1490, "single_sum": 1680, "includes": ["Behörden-Modul", "Kultur-Modul", "2 Mon. Begleitung"], "featured": True},
        ],
        "package_cols": ["INT-02-B Behörden", "INT-02-B Kultur", "Begleitung"],
        "excluded": {"de": ["Kein Sprachkurs", "Keine Rechtsberatung bei Verträgen"], "en": ["Not a language course", "No legal advice on contracts"], "ru": ["Не языковой курс", "Не юруслуги"]},
    },
    "INT-03": {
        "stages_h2": {"de": "Einzelstufen", "en": "Individual stages", "ru": "Этапы"},
        "stages_intro": {
            "de": "Vom 90-Minuten-Check bis zur achtwöchigen Turnaround-Begleitung — BAFA für den vollen Health Check.",
            "en": "From 90-minute check to 8-week turnaround support — BAFA funding for full health check.",
            "ru": "От 90 минут до 8 недель сопровождения — BAFA для полного Health Check.",
        },
        "stages": [
            {"nr": "INT-03-A", "name": {"de": "Quick Business Check", "en": "Quick Business Check", "ru": "Quick Check"}, "teaser": {"de": "90–120 Min.: Top-5-Issues — schnelle Klarheit.", "en": "90–120 min.: top 5 issues — fast clarity.", "ru": "90–120 мин.: топ-5 проблем."}, "price": 790, "duration": {"de": "1 Session", "en": "1 session", "ru": "1 сессия"}, "highlights": {"de": ["Finanzen, Vertrieb, Prozesse", "Kurzmemo", "Empfehlung nächste Stufe"], "en": ["Finance, sales, processes", "Brief memo", "Next step recommendation"], "ru": ["Финансы, продажи", "Memo", "Рекомендация"]}},
            {"nr": "INT-03-B", "name": {"de": "Business Health Check", "en": "Business Health Check", "ru": "Health Check"}, "teaser": {"de": "Beraterium-Methode, Workshops, Risikomatrix — BAFA-förderfähig.", "en": "Beraterium method, workshops, risk matrix — BAFA-eligible.", "ru": "Метод Beraterium — BAFA."}, "price": 3500, "duration": {"de": "2–4 Wochen", "en": "2–4 weeks", "ru": "2–4 нед."}, "highlights": {"de": ["Top-5 Maßnahmen", "Euro-Bewertung", "Umsetzungsfahrplan"], "en": ["Top 5 actions", "Euro valuation", "Implementation roadmap"], "ru": ["Топ-5", "В €", "План"]}},
            {"nr": "INT-03-C", "name": {"de": "Team & Kultur", "en": "Team & culture", "ru": "Команда и культура"}, "teaser": {"de": "Micromanagement, DE-Kultur, Delegation — 4–6 Sessions.", "en": "Micromanagement, DE culture, delegation — 4–6 sessions.", "ru": "Микромanagement, культура DE."}, "price": 2400, "duration": {"de": "4–6 Sessions", "en": "4–6 sessions", "ru": "4–6 сессий"}, "highlights": {"de": ["Cross-kulturelle Führung", "Onboarding", "Founder-Abhängigkeit"], "en": ["Cross-cultural leadership", "Onboarding", "Founder dependency"], "ru": ["Лидерство", "Онбординг", "Зависимость"]}},
            {"nr": "INT-03-D", "name": {"de": "Scale-up Readiness", "en": "Scale-up readiness", "ru": "Scale-up"}, "teaser": {"de": "Checkliste vor Wachstum: People, Money, Sales, Ops.", "en": "Pre-growth checklist: people, money, sales, ops.", "ru": "Чеклист перед ростом."}, "price": 3900, "duration": {"de": "2 Workshops", "en": "2 workshops", "ru": "2 воркшопа"}, "highlights": {"de": ["5→15→30 MA", "Supply & IT", "Go/No-Go"], "en": ["5→15→30 staff", "Supply & IT", "Go/no-go"], "ru": ["Рост команды", "Supply", "Go/no-go"]}},
            {"nr": "INT-03-E", "name": {"de": "Einzelproblem", "en": "Single problem", "ru": "Одна проблема"}, "teaser": {"de": "Fluktuation, kein Cashflow, Lieferant — Diagnose → Plan.", "en": "Turnover, no cash, supplier — diagnosis → plan.", "ru": "Текучка, cash, поставщик."}, "price": 1900, "price_from": True, "duration": {"de": "1–2 Wochen", "en": "1–2 weeks", "ru": "1–2 нед."}, "highlights": {"de": ["Ein Schmerzthema", "Ursachen & Optionen", "Ab 1.900 €"], "en": ["One pain point", "Causes & options", "From €1,900"], "ru": ["Одна тема", "Причины", "От 1.900 €"]}},
            {"nr": "INT-03-F", "name": {"de": "Turnaround Begleitung", "en": "Turnaround support", "ru": "Turnaround"}, "teaser": {"de": "8 Wochen Umsetzung der Top-Maßnahmen.", "en": "8 weeks implementing top actions.", "ru": "8 недель внедрения."}, "price": 12500, "duration": {"de": "8 Wochen", "en": "8 weeks", "ru": "8 нед."}, "highlights": {"de": ["Wöchentliche Calls", "Blocker lösen", "Fortschritt tracken"], "en": ["Weekly calls", "Remove blockers", "Track progress"], "ru": ["Созвоны", "Блокеры", "Прогресс"]}},
        ],
        "packages": [
            {"nr": "INT-03-P1", "name": {"de": "Quick Check Plus", "en": "Quick Check Plus", "ru": "Quick Plus"}, "price": 990, "single_sum": None, "includes": ["INT-03-A", "Top-5 schriftlich"], "featured": False},
            {"nr": "INT-03-P2", "name": {"de": "Health Check + Turnaround", "en": "Health Check + Turnaround", "ru": "Health + Turnaround"}, "price": 14900, "single_sum": 16000, "includes": ["INT-03-B", "INT-03-F"], "featured": True},
            {"nr": "INT-03-P3", "name": {"de": "Scale-up + RA-01 360°", "en": "Scale-up + RA-01 360°", "ru": "Scale-up + RA-01"}, "price": 7900, "single_sum": None, "includes": ["INT-03-D", "RA-01"], "featured": False},
        ],
        "package_cols": [],
        "excluded": {
            "de": ["Keine Einzel-Risikoanalyse auf Abruf", "Quick Check ersetzt nicht RA-01"],
            "en": ["No on-demand single risk analysis", "Quick check is not RA-01"],
            "ru": ["Не RA-02 по запросу", "Quick Check ≠ RA-01"],
        },
    },
    "INT-04": {
        "stages_h2": {"de": "Bausteine", "en": "Building blocks", "ru": "Блоки"},
        "stages_intro": {
            "de": "Markt-Check, Setup, Compliance — Retainer für Go-to-Market und laufendes Management.",
            "en": "Market check, setup, compliance — retainer for go-to-market and ongoing management.",
            "ru": "Рынок, setup, compliance — retainer для продаж и управления.",
        },
        "stages": [
            {"nr": "INT-04-A", "name": {"de": "Markt- & Risiko-Check", "en": "Market & risk check", "ru": "Рынок и риски"}, "teaser": {"de": "Go/No-Go vor Investment in DE-Setup.", "en": "Go/no-go before DE setup investment.", "ru": "Go/no-go до setup."}, "price": 2900, "duration": {"de": "2–3 Wochen", "en": "2–3 weeks", "ru": "2–3 нед."}, "highlights": {"de": ["Markt & Wettbewerb", "Regulatorik-Überblick", "Sanktions-Risiko"], "en": ["Market & competition", "Regulatory overview", "Sanctions risk"], "ru": ["Рынок", "Регуляторика", "Санкции"]}},
            {"nr": "INT-04-B", "name": {"de": "Setup Tochtergesellschaft", "en": "Subsidiary setup", "ru": "Setup дочки"}, "teaser": {"de": "Koordination Notar, Konto, Prozesse — bis operativ.", "en": "Notary, account, processes — until operational.", "ru": "Notar, счёт, процессы."}, "price": 9500, "duration": {"de": "8–16 Wochen", "en": "8–16 weeks", "ru": "8–16 нед."}, "highlights": {"de": ["GmbH/UG/Zweigstelle", "Geschäftsführer vor Ort", "Projektmanagement"], "en": ["GmbH/UG/branch", "Local managing director", "Project management"], "ru": ["GmbH/UG", "GF", "PM"]}},
            {"nr": "INT-04-C", "name": {"de": "KYC / Sanktions-Modul", "en": "KYC / sanctions module", "ru": "KYC / санкции"}, "teaser": {"de": "Pflicht bei GUS-Herkunft — saubere Trennung.", "en": "Required for CIS origin — clean separation.", "ru": "Обязательно для GUS."}, "price": 1500, "duration": {"de": "Modul", "en": "Module", "ru": "Модуль"}, "highlights": {"de": ["KYC/AML-Vorbereitung", "Banken-Dokumentation", "Geldfluss"], "en": ["KYC/AML prep", "Bank documentation", "Money flows"], "ru": ["KYC", "Банк", "Потоки"]}},
            {"nr": "INT-04-D", "name": {"de": "Go-to-Market", "en": "Go-to-market", "ru": "Go-to-market"}, "teaser": {"de": "Vor-Ort-Vertrieb — ab 3 Monate.", "en": "On-site sales — from 3 months.", "ru": "Продажи на месте."}, "price": 4500, "unit": {"de": "/ Monat", "en": "/ month", "ru": "/ мес."}, "duration": {"de": "min. 3 Mon.", "en": "min. 3 mo.", "ru": "мин. 3 мес."}, "highlights": {"de": ["Erste Kunden DE", "LinkedIn & Netzwerk", "Wöchentliches Reporting"], "en": ["First DE customers", "LinkedIn & network", "Weekly reporting"], "ru": ["Клиенты", "LinkedIn", "Отчёты"]}},
            {"nr": "INT-04-E", "name": {"de": "Retainer Management", "en": "Management retainer", "ru": "Retainer"}, "teaser": {"de": "Laufendes DE-Management — min. 6 Monate.", "en": "Ongoing DE management — min. 6 months.", "ru": "Управление в DE."}, "price": 4500, "unit": {"de": "/ Monat", "en": "/ month", "ru": "/ мес."}, "duration": {"de": "min. 6 Mon.", "en": "min. 6 mo.", "ru": "мин. 6 мес."}, "highlights": {"de": ["Team vor Ort", "Eskalation", "Reporting an HQ"], "en": ["Local team", "Escalation", "HQ reporting"], "ru": ["Команда", "Эскалация", "HQ"]}},
        ],
        "packages": [
            {"nr": "INT-04-P", "name": {"de": "Setup-Paket", "en": "Setup bundle", "ru": "Setup-пакет"}, "price": 12900, "single_sum": 13900, "includes": ["INT-04-A", "INT-04-B", "INT-04-C"], "featured": True},
        ],
        "package_cols": ["INT-04-A", "INT-04-B", "INT-04-C"],
        "excluded": {"de": ["Keine Rechts- oder Steuerberatung"], "en": ["No legal or tax advice"], "ru": ["Не юр./налог. услуги"]},
    },
}


def stage_price_label(stage: dict, locale: str) -> str:
    pf = stage.get("price_from")
    unit = stage.get("unit", {})
    u = unit.get(locale, unit.get("de", "")) if isinstance(unit, dict) else unit
    base = f"ab {format_eur(stage['price'])}" if pf else format_eur(stage["price"])
    return f"{base}{u}" if u else base


def package_savings(pkg: dict) -> int | None:
    if pkg.get("single_sum") and pkg.get("price"):
        return pkg["single_sum"] - pkg["price"]
    return None
