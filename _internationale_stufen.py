"""Stage & package configs for international offers (INT-01 … INT-04).

Source: Angebote/Angebot RU/stufen/*.md
"""
from __future__ import annotations

from _pricing import format_eur

# Customer journey on /internationale-angebote/ index
INT_JOURNEY: dict[str, list[dict]] = {
    "de": [
        {"key": "start", "label": "START", "question": "Kostenlos klären: Passt Beraterium zu mir?", "nr": "INT-00", "price": 0},
        {"key": "orient", "label": "ORIENTIERUNG", "question": "Ich will erst verstehen, wie der Markt in DE funktioniert", "nr": "INT-01-E", "price": 150},
        {"key": "plan", "label": "PLANUNG", "question": "Noch keine konkrete Idee — ich brauche Begleitung bei 0", "nr": "INT-01-P0", "price": 2390},
        {"key": "launch", "label": "LAUNCH", "question": "Idee steht — ich brauche Umsetzung und Begleitung", "nr": "INT-01-P1", "price": 4490},
        {"key": "check", "label": "CHECK", "question": "Mein Business läuft — wo hakt es?", "nr": "INT-03-A", "price": 790},
    ],
    "en": [
        {"key": "start", "label": "START", "question": "Free intro: is Beraterium a fit?", "nr": "INT-00", "price": 0},
        {"key": "orient", "label": "ORIENTATION", "question": "I want to understand the German market first", "nr": "INT-01-E", "price": 150},
        {"key": "plan", "label": "PLANNING", "question": "No concrete idea yet — guide me from zero", "nr": "INT-01-P0", "price": 2390},
        {"key": "launch", "label": "LAUNCH", "question": "Idea is ready — I need execution support", "nr": "INT-01-P1", "price": 4490},
        {"key": "check", "label": "CHECK", "question": "Business is running — what's weak?", "nr": "INT-03-A", "price": 790},
    ],
    "ru": [
        {"key": "start", "label": "START", "question": "Бесплатно: подходит ли Beraterium?", "nr": "INT-00", "price": 0},
        {"key": "orient", "label": "ОРИЕНТАЦИЯ", "question": "Сначала хочу понять рынок Германии", "nr": "INT-01-E", "price": 150},
        {"key": "plan", "label": "ПЛАН", "question": "Нет конкретной идеи — нужна поддержка с нуля", "nr": "INT-01-P0", "price": 2390},
        {"key": "launch", "label": "LAUNCH", "question": "Идея есть — нужна реализация", "nr": "INT-01-P1", "price": 4490},
        {"key": "check", "label": "CHECK", "question": "Бизнес работает — где слабые места?", "nr": "INT-03-A", "price": 790},
    ],
}

_STAGE = dict  # alias for typing clarity

INT_STAGES: dict[str, dict] = {
    "INT-01": {
        "stages_h2": {"de": "Einzelstufen — einzeln buchbar", "en": "Individual stages — book separately", "ru": "Отдельные этапы"},
        "stages_intro": {
            "de": "Zwei Wege: Begleitung bei 0 (noch keine Idee) oder direkt Launch (Idee steht). Jede Stufe liefert ein klares Ergebnis — Pakete sparen gegenüber Einzelbuchung.",
            "en": "Two paths: starting from zero (no idea yet) or straight to launch (idea ready). Each stage delivers a clear outcome — bundles save vs. booking separately.",
            "ru": "Два пути: с нуля (идеи ещё нет) или сразу к запуску (идея готова). Каждый этап — понятный результат; пакеты выгоднее.",
        },
        "stages": [
            {
                "nr": "INT-01-E",
                "name": {"de": "Deutschland-Orientierung", "en": "Germany orientation", "ru": "Ориентация по Германии"},
                "teaser": {
                    "de": "1:1-Vortrag 45 Min. + 45 Min. Fragen: Markt, Rahmenbedingungen, typische Stolpersteine — bevor Sie gründen.",
                    "en": "1:1 briefing 45 min + 45 min Q&A: market, framework, typical pitfalls — before you commit.",
                    "ru": "1:1 брифинг 45 мин + 45 мин вопросы: рынок, условия, типичные ошибки.",
                },
                "price": 150,
                "duration": {"de": "1,5 h", "en": "1.5 h", "ru": "1,5 ч"},
                "highlights": {
                    "de": ["Markt & Branchenüberblick DE", "Rechtsformen & Behörden grob", "Was Gründer unterschätzen", "Ihre Fragen im 1:1"],
                    "en": ["German market overview", "Legal forms & authorities", "Common founder blind spots", "Your questions in 1:1"],
                    "ru": ["Обзор рынка DE", "Формы и ведомства", "Типичные ошибки", "Ваши вопросы 1:1"],
                },
            },
            {
                "nr": "INT-01-A",
                "name": {"de": "Business Check", "en": "Business Check", "ru": "Business Check"},
                "teaser": {
                    "de": "Standortbestimmung: Idee(n), Rechtsform, Budget, Top-Risiken — bevor Notar und Steuerberater.",
                    "en": "Reality check: idea(s), legal form, budget, top risks — before notary and tax advisor.",
                    "ru": "Оценка идеи, формы, бюджета и рисков — до нотариуса и Steuerberater.",
                },
                "price": 790,
                "duration": {"de": "2–3 h + Kurzprotokoll", "en": "2–3 h + brief report", "ru": "2–3 ч + отчёт"},
                "highlights": {
                    "de": ["Rechtsform-Optionen einordnen", "Behördenweg grob", "Top-5 Gründungsrisiken", "Nächste Schritte"],
                    "en": ["Legal form options explained", "Authority roadmap", "Top 5 founding risks", "Next steps"],
                    "ru": ["Формы бизнеса", "Путь через ведомства", "Топ-5 рисков", "Следующие шаги"],
                },
            },
            {
                "nr": "INT-01-B",
                "name": {"de": "Gründungsplanung", "en": "Founding planning", "ru": "Планирование основания"},
                "teaser": {
                    "de": "Gemeinsam Ihr Business planen — Markt, Wettbewerb, Modell, SWOT, PESTEL. Sie arbeiten, wir leiten an (kein investor-ready BP durch uns).",
                    "en": "Plan your business together — market, competitors, model, SWOT, PESTEL. You do the work, we guide (no investor-ready BP by us).",
                    "ru": "Планируем бизнес вместе — рынок, конкуренты, модель, SWOT, PESTEL. Вы делаете, мы ведём.",
                },
                "price": 1900,
                "duration": {"de": "Mehrere Sessions + Arbeitsdokument", "en": "Multiple sessions + workbook", "ru": "Несколько сессий + документ"},
                "highlights": {
                    "de": ["Markt- & Wettbewerbsanalyse", "Geschäftsmodell & Angebote", "SWOT & PESTEL", "Finanzplan-Struktur"],
                    "en": ["Market & competitor analysis", "Business model & offers", "SWOT & PESTEL", "Financial plan structure"],
                    "ru": ["Рынок и конкуренты", "Модель и предложения", "SWOT & PESTEL", "Структура финплана"],
                },
            },
            {
                "nr": "INT-01-F",
                "name": {"de": "Launch Roadmap", "en": "Launch Roadmap", "ru": "Launch Roadmap"},
                "teaser": {
                    "de": "Persönlicher Umsetzungsplan Woche 1 → Monat 3 — wenn Idee und Planung stehen.",
                    "en": "Personal execution plan week 1 → month 3 — when idea and planning are done.",
                    "ru": "План реализации неделя 1 → месяц 3 — когда идея и план готовы.",
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
        "packages_h2": {"de": "Pakete — der passende Weg", "en": "Bundles — your path", "ru": "Пакеты — ваш путь"},
        "packages": [
            {
                "nr": "INT-01-P0",
                "name": {"de": "Begleitung bei 0", "en": "Starting from zero", "ru": "С нуля"},
                "teaser": {
                    "de": "Noch keine konkrete Idee: Business Check plus Gründungsplanung — Sie arbeiten, wir führen Schritt für Schritt.",
                    "en": "No concrete idea yet: Business Check plus founding planning — you do the work, we guide each step.",
                    "ru": "Нет идеи: Business Check и планирование — вы работаете, мы ведём шаг за шагом.",
                },
                "price": 2390,
                "single_sum": 2690,
                "includes": ["INT-01-A", "INT-01-B"],
                "featured": False,
            },
            {
                "nr": "INT-01-P1",
                "name": {"de": "Launch-Paket", "en": "Launch bundle", "ru": "Пакет запуска"},
                "teaser": {
                    "de": "Idee steht: Launch Roadmap plus Gründungsbegleitung — operativ bis zur Gewerbeanmeldung.",
                    "en": "Idea ready: Launch Roadmap plus founding support — operational through trade registration.",
                    "ru": "Идея есть: Launch Roadmap и сопровождение — до регистрации Gewerbe.",
                },
                "price": 4490,
                "single_sum": 4800,
                "includes": ["INT-01-F", "INT-01-C"],
                "featured": False,
            },
            {
                "nr": "INT-01-P2",
                "name": {"de": "Gründung 360°", "en": "Founding 360°", "ru": "Gründung 360°"},
                "price": 7490,
                "single_sum": 8740,
                "includes": ["INT-01-A", "INT-01-B", "INT-01-F", "INT-01-C", "INT-01-D"],
                "featured": True,
            },
            {
                "nr": "INT-01-P3",
                "name": {"de": "Gründung 360° + Förder-Check", "en": "Founding 360° + funding check", "ru": "360° + Förder-Check"},
                "price": 7990,
                "single_sum": None,
                "includes": ["INT-01-P2", "Förder-Check"],
                "featured": False,
            },
        ],
        "package_cols": ["INT-01-A", "INT-01-B", "INT-01-F", "INT-01-C", "INT-01-D"],
        "excluded": {
            "de": [
                "Rechtsberatung (RDG) und Steuerberatung (StBerG)",
                "Gewerbeanmeldung oder Notartermine in unserem Namen",
                "Fertiger investor-ready Businessplan durch uns — wir leiten Sie an, Sie erstellen den Inhalt",
            ],
            "en": [
                "Legal advice (RDG) and tax advice (StBerG)",
                "Trade registration or notary appointments in our name",
                "Investor-ready business plan by us — we guide, you create the content",
            ],
            "ru": [
                "Юридические и налоговые услуги (RDG/StBerG)",
                "Регистрация от нашего имени",
                "Investor-ready бизнес-план от нас — мы ведём, содержание делаете вы",
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
        "packages_h2": {"de": "Pakete — vom Check bis Turnaround", "en": "Bundles — from check to turnaround", "ru": "Пакеты — от check до turnaround"},
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
            {"nr": "INT-03-P3", "name": {"de": "Scale-up + Risiko-Analyse 360°", "en": "Scale-up + 360° risk analysis", "ru": "Scale-up + анализ 360°"}, "price": 7900, "single_sum": None, "includes": ["INT-03-D", "RA-01"], "featured": False},
        ],
        "package_cols": [],
        "excluded": {
            "de": ["Keine Einzel-Risikoanalyse auf Abruf", "Quick Check ersetzt nicht die Risiko-Analyse 360°"],
            "en": ["No on-demand single risk analysis", "Quick check is not a full 360° risk analysis"],
            "ru": ["Не анализ по запросу", "Quick Check ≠ полный анализ 360°"],
        },
    },
    "INT-04": {
        "offer_model": "project",
        "project_h2": {
            "de": "Projektphasen — individuell geplant",
            "en": "Project phases — planned individually",
            "ru": "Фазы проекта — индивидуально",
        },
        "project_intro": {
            "de": (
                "Jede Expansion startet als neues Projekt. Umfang, Timeline und Team legen wir gemeinsam fest — "
                "abhängig von Ihrem Budget und Ihren Zielen. Es gibt keine festen Paketpreise."
            ),
            "en": (
                "Every expansion starts as a new project. Scope, timeline, and team are defined together — "
                "based on your budget and goals. There are no fixed bundle prices."
            ),
            "ru": (
                "Каждая экспансия — отдельный проект. Объём, сроки и команда определяются вместе — "
                "по вашему бюджету и целям. Фиксированных пакетных цен нет."
            ),
        },
        "project_phases": [
            {
                "name": {"de": "Strategie & Markt", "en": "Strategy & market", "ru": "Стратегия и рынок"},
                "teaser": {
                    "de": "Go/No-Go, Markt, Wettbewerb, Sanktions- und Compliance-Rahmen.",
                    "en": "Go/no-go, market, competition, sanctions and compliance framework.",
                    "ru": "Go/no-go, рынок, конкуренты, санкции и compliance.",
                },
                "highlights": {
                    "de": ["Marktanalyse DE/EU", "Risiko & Regulatorik", "Projekt-Roadmap"],
                    "en": ["DE/EU market analysis", "Risk & regulation", "Project roadmap"],
                    "ru": ["Анализ рынка DE/EU", "Риски и регуляторика", "Roadmap"],
                },
            },
            {
                "name": {"de": "Setup Tochtergesellschaft", "en": "Subsidiary setup", "ru": "Setup дочки"},
                "teaser": {
                    "de": "Gesellschaft, Konten, Prozesse — bis operativ, mit koordinierten Spezialisten.",
                    "en": "Entity, accounts, processes — until operational, with coordinated specialists.",
                    "ru": "Компания, счета, процессы — до запуска, с координацией специалистов.",
                },
                "highlights": {
                    "de": ["GmbH/UG/Zweigstelle", "Notar & Anwalt koordiniert", "Bank & Behörden"],
                    "en": ["GmbH/UG/branch", "Notary & attorney coordinated", "Bank & authorities"],
                    "ru": ["GmbH/UG", "Notar и юрист", "Банк и ведомства"],
                },
            },
            {
                "name": {"de": "Compliance & KYC", "en": "Compliance & KYC", "ru": "Compliance и KYC"},
                "teaser": {
                    "de": "Saubere Struktur bei GUS-Herkunft — KYC/AML, Geldflüsse, Dokumentation.",
                    "en": "Clean structure for CIS origin — KYC/AML, money flows, documentation.",
                    "ru": "Чистая структура для GUS — KYC/AML, потоки, документы.",
                },
                "highlights": {
                    "de": ["KYC/AML-Vorbereitung", "Sanktions-Check", "Banken-Dokumentation"],
                    "en": ["KYC/AML prep", "Sanctions check", "Bank documentation"],
                    "ru": ["KYC/AML", "Санкции", "Банк"],
                },
            },
            {
                "name": {"de": "Go-to-Market", "en": "Go-to-market", "ru": "Go-to-market"},
                "teaser": {
                    "de": "Vertrieb vor Ort, erste Kunden, lokale Präsenz — Dauer nach Projektplan.",
                    "en": "On-site sales, first customers, local presence — duration per project plan.",
                    "ru": "Продажи на месте, первые клиенты — по плану проекта.",
                },
                "highlights": {
                    "de": ["Erste Kunden DE", "LinkedIn & Netzwerk", "Reporting an HQ"],
                    "en": ["First DE customers", "LinkedIn & network", "HQ reporting"],
                    "ru": ["Клиенты DE", "LinkedIn", "Отчёт HQ"],
                },
            },
            {
                "name": {"de": "Laufendes Management", "en": "Ongoing management", "ru": "Управление"},
                "teaser": {
                    "de": "Team vor Ort, Eskalation, Betrieb — so lange, wie das Projekt es braucht.",
                    "en": "Local team, escalation, operations — as long as the project requires.",
                    "ru": "Команда на месте, эскалация, операции — по потребности проекта.",
                },
                "highlights": {
                    "de": ["Operatives DE-Management", "Team & Prozesse", "Langfristige Begleitung"],
                    "en": ["Operational DE management", "Team & processes", "Long-term support"],
                    "ru": ["Операционное управление", "Команда", "Долгосрочно"],
                },
            },
        ],
        "project_coordinated_h2": {
            "de": "Was wir koordinieren",
            "en": "What we coordinate",
            "ru": "Что мы координируем",
        },
        "project_coordinated_intro": {
            "de": (
                "Beraterium führt das Projekt — und bindet die Spezialisten ein, die Ihr Vorhaben braucht. "
                "Rechts- und Steuerberatung erbringen unsere Partner; wir koordinieren und übersetzen für Sie."
            ),
            "en": (
                "Beraterium leads the project and brings in the specialists your venture needs. "
                "Legal and tax services are delivered by our partners; we coordinate and bridge for you."
            ),
            "ru": (
                "Beraterium ведёт проект и подключает нужных специалистов. "
                "Юридические и налоговые услуги — через партнёров; мы координируем и переводим."
            ),
        },
        "project_coordinated": {
            "de": [
                "Anwälte, Notare und Steuerberater aus unserem Netzwerk — Auswahl und Koordination durch Beraterium",
                "Branchen-, IT- oder HR-Experten — je nach Projekt, wenn nötig",
                "Behörden, Banken, IHK — Termine vorbereiten, nichts geht verloren",
                "Projektmanagement DE/EN/RU — ein Ansprechpartner für Sie",
            ],
            "en": [
                "Attorneys, notaries, and tax advisors from our network — selected and coordinated by Beraterium",
                "Industry, IT, or HR experts — added per project when needed",
                "Authorities, banks, chambers — appointments prepared, nothing gets lost",
                "Project management DE/EN/RU — one point of contact for you",
            ],
            "ru": [
                "Юристы, нотариусы, Steuerberater из сети — подбор и координация Beraterium",
                "Отраслевые, IT или HR эксперты — по необходимости проекта",
                "Ведомства, банки, IHK — подготовка, ничего не теряется",
                "PM DE/EN/RU — один контакт для вас",
            ],
        },
        "project_budget": {
            "de": {
                "range": "30.000 – 100.000 € netto",
                "note": (
                    "Typisches Projektvolumen — je nach Umfang, Dauer und Experten. "
                    "Festes Angebot erst nach Strategiegespräch und Scope-Definition."
                ),
            },
            "en": {
                "range": "€30,000 – €100,000 net",
                "note": (
                    "Typical project volume — depending on scope, duration, and experts. "
                    "Fixed quote only after strategy call and scope definition."
                ),
            },
            "ru": {
                "range": "30.000 – 100.000 € нетто",
                "note": (
                    "Типичный объём проекта — по объёму, срокам и экспертам. "
                    "Фиксированное предложение — после стратегической сессии и scope."
                ),
            },
        },
    },
}


def stage_price_label(stage: dict, locale: str) -> str:
    pf = stage.get("price_from")
    unit = stage.get("unit", {})
    u = unit.get(locale, unit.get("de", "")) if isinstance(unit, dict) else unit
    base = f"ab {format_eur(stage['price'])}" if pf else format_eur(stage["price"])
    return f"{base}{u}" if u else base


def package_price_label(pkg: dict, locale: str) -> str:
    unit = pkg.get("unit", {})
    u = unit.get(locale, unit.get("de", "")) if isinstance(unit, dict) else unit
    base = format_eur(pkg["price"])
    return f"{base}{u}" if u else base


def package_savings(pkg: dict) -> int | None:
    if pkg.get("single_sum") and pkg.get("price"):
        return pkg["single_sum"] - pkg["price"]
    return None
