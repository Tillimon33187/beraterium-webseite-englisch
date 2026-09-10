"""Editorial configs for /internationale-angebote/ (DE), /international-services/ (EN), /ru/... (RU).

Imported by Webseite/site/_gen_pages.py (gen_international_index, gen_international_offer).
Prices join via _pricing.py on field "nr". Source: Angebote/Angebot RU/*.md
"""
from __future__ import annotations

INT_OFFER_NRS = ("INT-01", "INT-02", "INT-03", "INT-04")

LEGAL_NOTICE_DE = (
    "Beraterium erbringt unternehmerische Beratung und Koordination — "
    "keine Rechtsberatung im Sinne des RDG und keine Steuerberatung im Sinne des StBerG. "
    "Rechtliche und steuerliche Leistungen werden durch unsere Partneranwälte und Steuerberater erbracht."
)
LEGAL_NOTICE_EN = (
    "Beraterium provides business consulting and coordination — "
    "not legal advice under the RDG or tax advice under the StBerG. "
    "Legal and tax services are provided by our partner attorneys and tax advisors."
)
LEGAL_NOTICE_RU = (
    "Beraterium оказывает предпринимательское консультирование и координацию — "
    "не юридические услуги в смысле RDG и не налоговое консультирование в смысле StBerG. "
    "Юридические и налоговые услуги оказывают наши партнёры-юристы и налоговые консультанты."
)

INT_INDEX_DE = {
    "tag": "INTERNATIONALE ANGEBOTE",
    "h1": "Beratung für russischsprachige Gründer in Deutschland",
    "lead": (
        "Das Beste aus beiden Welten: deutsche Gründungs- und Regulierungsexpertise plus "
        "russischsprachige Beraterinnen, bei denen Sie sich wie unter Landsleuten fühlen — "
        "Gründung, Behörden, Kultur, EU-Vorgaben und Risiken. DE · EN · RU."
    ),
    "title": "Internationale Angebote | Beraterium",
    "description": (
        "Beratung für russischsprachige Gründer in Deutschland: Gründung, Integration, "
        "Turnaround und EU-Expansion — DE/EN/RU, kostenlose Erstberatung."
    ),
    "why_h2": "Warum Beraterium für internationale Gründer?",
    "why_intro": (
        "Wir verbinden lokale Expertise und Netzwerk in Deutschland mit dem kulturellen Bezug "
        "zu Russland — damit Sie fachlich sicher und persönlich verstanden beraten werden."
    ),
    "why_cards": [
        (
            "Russisch Muttersprache — bei Landsleuten",
            "Veronika Berdnikova und Aleksandra Polosukhina sprechen Russisch als Muttersprache. "
            "Auf Wunsch beraten wir durchgängig auf Russisch — ohne Übersetzungsverluste und mit dem Gefühl, unter Landsleuten zu sein.",
        ),
        (
            "Deutschland-Expertise",
            "Till Blania kennt Gründung, Behörden, Gesetze, deutsche Geschäftskultur, EU-Verordnungen "
            "und typische Risiken aus jahrelanger Praxis — von der Idee bis zur operativen Umsetzung in DE.",
        ),
        (
            "Beide Welten vereint",
            "Lokales Netzwerk (Notare, Anwälte, Steuerberater, IHK) plus Verständnis für russische "
            "Denk- und Kommunikationsweisen — Sie müssen nicht zwischen „deutsch korrekt“ und „zuhause fühlen“ wählen.",
        ),
        (
            "Risiko von Anfang an",
            "Blind Spots früh erkennen: Aufenthalt, Rechtsform, Steuern, Banken, Sanktionen, Kultur — "
            "mit Berateriums Bewertungslogik in Euro, nicht nur Bauchgefühl.",
        ),
        (
            "Dreisprachig DE · EN · RU",
            "Echte indexierbare Seiten unter beraterium.de/ru/ — Sie wählen die Sprache, wir passen uns an.",
        ),
    ],
    "team_tag": "IHR TEAM",
    "team_h2": "Deutsch-russisches Beratungsteam — Sie sind in guten Händen",
    "team_intro": (
        "Zwei russischsprachige Muttersprachlerinnen und deutschlanderfahrene Gründungs- und Risikoexpertise "
        "in einem Team: Veronika und Aleksandra für Vertrauen und Verständnis auf Russisch, Till für den Weg "
        "durch deutsche Behörden, Gesetze und Regeln. So kombinieren wir beide Welten — fachlich und menschlich."
    ),
    "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
    "team_member_intros": {
        "veronika-berdnikova": (
            "Russisch Muttersprache — Ihre Ansprechpartnerin für Gründer aus Russland und der GUS. "
            "Klar, einfühlsam, ohne Verkaufsdruck."
        ),
        "aleksandra-polosukhina": (
            "Russisch Muttersprache — internationale Kommunikation, Marketing und Teamkultur. "
            "Brücke zwischen russischer und deutscher Business-Welt."
        ),
        "till-blania": (
            "Gründung in Deutschland, Behörden, Gesetze, EU-Vorgaben und Risikomanagement — "
            "plus HSE St. Petersburg und Verständnis für den postsowjetischen Raum."
        ),
    },
    "faq": [
        ("Für wen sind die internationalen Angebote?", "Unternehmer aus dem postsowjetischen Raum — in DE, in Planung oder mit Unternehmen im Ausland."),
        (
            "Sprechen Sie Russisch?",
            "Ja — Veronika und Aleksandra sind russische Muttersprachlerinnen; Till berät auf Deutsch, Englisch "
            "und Russisch (B1, weiter in Ausbildung). Auf Wunsch führen wir das gesamte Gespräch auf Russisch.",
        ),
        ("Ist das Rechtsberatung?", "Nein — unternehmerische Beratung und Koordination mit Partneranwälten."),
        ("Was kostet der Einstieg?", "Erstberatung 30 Min. kostenlos. Orientierung 150 €. Paket Begleitung bei 0 ab 2.390 € netto."),
        ("BAFA-Förderung?", "Ja, für Business Health Check (INT-03) bis 80 %."),
    ],
    "cta_h2": "Welches Angebot passt zu Ihrer Situation?",
    "cta_body": "Kostenlose Erstberatung buchen — 30 Min., unverbindlich, DE/EN/RU.",
}

INT_OFFER_CONFIGS_DE: list[dict] = [
    {
        "nr": "INT-01",
        "slug": "gruendung-deutschland",
        "tag": "GRÜNDUNG · DEUTSCHLAND",
        "h1": "Business in Deutschland gründen — mit Plan und Risikoschutz",
        "lead": (
            "Registrierung ist nur ein Teil des Wegs. Ob Sie noch keine Idee haben oder startklar sind — "
            "wir begleiten Sie Schritt für Schritt, auf Deutsch, Englisch oder Russisch. "
            "Kostenlose Erstberatung, dann Orientierung, Planung bei 0 oder direkt Launch."
        ),
        "title": "Gründung in Deutschland | Internationale Angebote | Beraterium",
        "description": "Gründungsbegleitung für russischsprachige Unternehmer: kostenlose Erstberatung, Orientierung ab 150 €, Paket Begleitung bei 0 ab 2.390 € netto.",
        "audience": "Gründer mit Migrationshintergrund",
        "fuer_wen_intro": "Dieses Angebot passt, wenn:",
        "fuer_wen": [
            "Sie in Deutschland sind oder kommen wollen — mit oder ohne konkrete Idee",
            "Sie erst verstehen wollen, wie der Markt funktioniert (Orientierung)",
            "Sie bei null starten und Business planen lernen wollen (Paket P0)",
            "Ihre Idee steht und Sie Launch-Umsetzung brauchen (Paket P1)",
        ],
        "leistungen": [
            "Kostenlose Erstberatung und Deutschland-Orientierung (1:1)",
            "Gründungsplanung: Markt, Modell, SWOT, PESTEL — Sie arbeiten, wir leiten an",
            "Launch Roadmap und hands-on Begleitung bei Behörden & Bank",
            "Koordination Notar, Anwalt, Steuerberater aus dem Netzwerk",
            "Fördermittel-Recherche und Risikoanalyse",
        ],
        "steps": [
            ("Erstberatung", "30 Min. kostenlos: Situation, Ziel, passender Weg — unverbindlich."),
            ("Orientierung (optional)", "Deutschland-Orientierung 1,5 h — Markt, Rahmen, Ihre Fragen (150 €)."),
            ("Zwei Wege", "Begleitung bei 0 (Check + Planung) — oder Launch (Roadmap + Umsetzung), wenn Idee steht."),
            ("Go-Live", "Dokumentierter Status, Risikoplan, optional Folgepaket INT-03."),
        ],
        "ergebnis": [
            "Klarer Weg — Orientierung, Planung bei 0 oder Launch",
            "Ihr Gründungsplan in eigenen Worten — nicht von uns abgeschrieben",
            "Netzwerk Notar, Steuerberater, IHK eingebunden",
            "Typische Blind Spots erkannt, bevor sie teuer werden",
        ],
        "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
        "faq": [
            ("Kann ich als Ausländer gründen?", "Ja — je nach Aufenthaltstitel. Wir klären das in der kostenlosen Erstberatung oder im Business Check."),
            ("Was kostet es?", "Orientierung 150 € · Begleitung bei 0 ab 2.390 € · Launch-Paket 4.490 € · Gründung 360° 7.490 € netto."),
            ("Einzeln oder Paket?", "Zwei Wege: Planung bei 0 (P0) oder Launch (P1) — voller Weg als Gründung 360° (P2)."),
            ("Rechtsberatung?", "Nein — Koordination mit Partneranwälten und Steuerberatern."),
        ],
        "cta_h2": "Gründung planen?",
        "cta_body": "Kostenlose Erstberatung buchen — 30 Min., DE/EN/RU.",
        "card_teaser": "Kostenlose Erstberatung · Orientierung 150 € · Paket ab 2.390 €.",
    },
    {
        "nr": "INT-02",
        "slug": "leben-arbeiten-deutschland",
        "tag": "INTEGRATION · DEUTSCHLAND",
        "h1": "Leben und Arbeiten in Deutschland",
        "lead": (
            "Behörden, Sprache, Kultur — wer sich in Deutschland nicht einfindet, kann kein Business "
            "stabil aufbauen. Wir machen den Weg leichter: praxisnah, 1-zu-1, auf Russisch oder Deutsch."
        ),
        "title": "Leben & Arbeiten in Deutschland | Beraterium",
        "description": "Coaching: deutsche Kultur, Behörden, Fettnäpfchen — ab 180 €/Std., Paket 2.900 €.",
        "audience": "Neu angekommene Gründer",
        "fuer_wen_intro": "Passt, wenn:",
        "fuer_wen_lead": (
            "In Deutschland scheitert Integration selten am fehlenden Willen — sondern an Sprache, Behörden, "
            "ungeschriebenen Regeln und dem Gefühl, fremd zu bleiben. Erst privat einfinden, Hürden aus dem "
            "Weg räumen — dann Business. Genau dabei unterstützen wir: mit Local Know-how, russischsprachigen "
            "Beraterinnen und dem Verständnis beider Welten."
        ),
        "fuer_wen": [
            "Deutsche Business-Kommunikation, Direktheit und Smalltalk sich fremd anfühlen",
            "Behördenbriefe überfordern — Finanzamt, Gewerbeamt, Ausländerbehörde: unklar, was zu tun ist",
            "ELSTER, Steuer, Versicherungen — deutsche Regeln wirken wie ein undurchsichtiges Labyrinth",
            "Sie sind fachlich stark, fühlen sich in DE aber wie jemand, der das System nicht regeln kann",
            "Privat muss es erst passen (Sprache, Alltag, Wohnung) — sonst trägt kein Business stabil",
            "Sie wollen verstehen und selbst handeln — nicht nur übersetzen oder ratlos bleiben",
            "Russischsprachige Beraterinnen plus Deutschland-Erfahrung — verstanden und begleitet, nicht allein",
            "Parallel zur Gründung oder danach — modular buchbar, ohne Sprachkurs",
        ],
        "leistungen": [
            "Geschäfts- und Alltagskultur",
            "Behörden-Navigation und ELSTER",
            "Typische Fettnäpfchen",
            "Optional: Objektsuche",
        ],
        "steps": [
            ("Bedarf klären", "Module und Zeitrahmen."),
            ("Sessions", "1-zu-1, praxisnah."),
            ("Hausaufgaben", "Konkrete Aufgaben."),
            ("Review", "Anpassung nach Modul."),
        ],
        "ergebnis": ["Sicherheit bei Behörden", "Kulturverständnis", "Individueller Plan"],
        "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
        "faq": [
            ("Sprachkurs?", "Nein — Soft Skills und Behördenwissen."),
            ("Module einzeln?", "Ja — ab 180 €/Std., Modul ab 490 €, Paket 2.900 €."),
        ],
        "cta_h2": "Deutschland verstehen?",
        "cta_body": "Erstgespräch buchen — passende Module finden.",
        "card_teaser": "Kultur, Behörden, ELSTER — modular.",
    },
    {
        "nr": "INT-03",
        "slug": "business-turnaround",
        "tag": "TURNAROUND",
        "h1": "Business Health Check",
        "lead": (
            "In Deutschland gegründet — es läuft, aber irgendwie nicht stabil? Finanzamt, IHK, Arbeitsschutz, "
            "Datenschutz: plötzlich Druck von allen Seiten. Vom Quick Check bis zur Turnaround-Begleitung finden "
            "wir strukturiert, wo es hakt — und entwickeln Strategien, die Sie auch umsetzen können."
        ),
        "title": "Business Turnaround | Beraterium",
        "description": "Engpässe finden, Lösungen priorisieren — ab 3.500 €, BAFA-förderfähig.",
        "audience": "Laufende Unternehmen mit Problemen",
        "fuer_wen_intro": "Passt, wenn:",
        "fuer_wen_lead": (
            "Viele Gründer merken erst nach dem Start: Der Umsatz stimmt, aber Cashflow, Behörden und Regeln "
            "überfordern. Finanzamt, IHK, Arbeitsschutz, Datenschutzprüfungen mit Abmahnung — es türmen sich "
            "Dinge auf, mit denen niemand gerechnet hat. Genau dann passt der Business Health Check: gemeinsam "
            "Engpässe finden, Prioritäten setzen und umsetzbare Strategien entwickeln — mit Begleitung bis zur Umsetzung."
        ),
        "fuer_wen": [
            "Sie haben in Deutschland gegründet — es läuft, aber irgendwie nicht stabil",
            "Finanzamt, IHK oder Gewerbeamt machen Druck — unklar, was zuerst zu tun ist",
            "Arbeitsschutz, Datenschutz oder Abmahnungen — unerwartete Themen türmen sich",
            "Umsatz da, kein Cashflow — Sie wissen nicht, wo anfangen",
            "Zweite Location geplant (z. B. Salon, Filiale) — diesmal ohne Fehler der ersten Niederlassung",
            "Einzelunternehmen in GmbH umwandeln — unsicher, ob sinnvoll und welche Optionen es gibt",
            "Sie wollen Klarheit und einen Plan, den Sie Schritt für Schritt umsetzen können",
        ],
        "leistungen": [
            "Risikoanalyse Beraterium-Methode",
            "Engpass-Diagnose",
            "Priorisierte Maßnahmen",
        ],
        "steps": [
            ("Kick-off", "90 Min. Ist-Situation."),
            ("Diagnose", "Workshops, Risikomatrix."),
            ("Strategie", "Top-5-Maßnahmen."),
            ("Übergabe", "Report, optional Begleitung."),
        ],
        "ergebnis": [
            "Klarheit, wo es wirklich hakt — Finanzen, Team, Prozesse, Behörden",
            "Priorisierte Maßnahmen statt Aktionismus",
            "Umsetzungsfahrplan, den wir gemeinsam auch begleiten können",
        ],
        "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania", "peter-muenstermann"],
        "faq": [
            ("BAFA?", "Ja — voller Health Check ab 3.500 € förderfähig."),
            ("Quick Check vs. voller Check?", "Quick Check (790 €) = 90 Min. Diagnose. Voller Check = Beraterium-Methode mit Workshops."),
            ("Einzelrisiken?", "Nein — nur im Paket-Kontext der Risikoanalyse."),
        ],
        "cta_h2": "Wo hakt es?",
        "cta_body": "Health Check anfragen.",
        "card_teaser": "Risikoanalyse für laufende Unternehmen.",
    },
    {
        "nr": "INT-04",
        "slug": "expansion-tochtergesellschaft",
        "tag": "EXPANSION · EU",
        "h1": "Expansion nach Deutschland",
        "lead": (
            "Erfolgreiches Business in Russland — und Expansion nach Deutschland? Oft scheitert es nicht am "
            "Produkt, sondern an Einschränkungen, Compliance und fehlenden Partnern vor Ort. Wir realisieren "
            "alles in Deutschland: Marktanalyse, Vertriebsaufbau, Firmengründung, Verträge, Anmeldungen — "
            "Rund-um-sorglos. Sie stellen das Kapital bereit, Beraterium kümmert sich vor Ort."
        ),
        "title": "Expansion DE | Beraterium",
        "description": "EU-Markteintritt: individuelles Expansionsprojekt — Scope und Budget im Strategiegespräch.",
        "audience": "Unternehmen im Ausland",
        "fuer_wen_intro": "Passt, wenn:",
        "fuer_wen_lead": (
            "Viele Unternehmer mit laufendem Business in Russland wollen den deutschen Markt — aber "
            "Sanktionen, regulatorische Hürden und fehlende lokale Kontakte bremsen. Jede Expansion "
            "ist ein eigenes Projekt: Umfang, Team und Budget planen wir gemeinsam — typisch zwischen "
            "30.000 und 100.000 €, je nachdem was Sie brauchen."
        ),
        "fuer_wen": [
            "Erfolgreiches Business in Russland/CIS — Expansion nach Deutschland gewünscht",
            "Sanktionen, Compliance oder fehlende lokale Partner blockieren den Markteintritt",
            "Marktanalyse, Vertrieb und Firmengründung in DE — aber kein Team vor Ort",
            "Tochtergesellschaft, Verträge, Anmeldungen — alles aus einer Hand",
            "Sie wollen sich nicht um Behörden, Notar und Setup in DE kümmern müssen",
            "Produktion/Fulfillment kann im Heimatland bleiben — Präsenz und Vertrieb in Deutschland",
            "Rund-um-sorglos: Kapital bereitstellen, Beraterium erledigt den Rest vor Ort",
        ],
        "leistungen": [
            "Marktanalyse und Risikobewertung für Deutschland",
            "Aufbau Vertrieb und Go-to-Market vor Ort",
            "Gründung Tochtergesellschaft — Notar, Anwalt, Anmeldungen",
            "Verträge, KYC/AML, Sanktions-Check, Compliance-Struktur",
            "Vor-Ort-Management und Retainer — laufende Betreuung",
        ],
        "steps": [
            ("Strategie", "Markt, Struktur, Compliance."),
            ("Setup", "Gesellschaft, Konten, Team."),
            ("Go-to-Market", "Vertrieb, erste Kunden."),
            ("Retainer", "Laufendes Management."),
        ],
        "ergebnis": [
            "DE-Präsenz ohne Umzug — Sie müssen sich vor Ort um fast nichts kümmern",
            "Compliance-sichere Struktur — Sanktionen, KYC, saubere Trennung",
            "Markt, Vertrieb und Gesellschaft — von Beraterium umgesetzt, nicht nur geplant",
        ],
        "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
        "faq": [
            ("Muss ich nach Deutschland umziehen?", "Nein — Beraterium managt vor Ort. Sie stellen Kapital und strategische Entscheidungen."),
            ("Trennung von RU-Firma?", "Saubere Struktur nach Compliance — im Strategiegespräch."),
            ("Was bleibt bei mir?", "Kapital, Produktstrategie, Freigaben — der operative Aufbau in DE läuft über uns."),
            ("Wie wird der Preis festgelegt?", "Individuell nach Scope — typisch 30.000–100.000 € netto. Festes Angebot nach Strategiegespräch."),
            ("Anwalt und Steuerberater?", "Ja — wir koordinieren Spezialisten aus unserem Netzwerk. Rechts- und Steuerleistungen erbringen unsere Partner."),
        ],
        "cta_h2": "Deutschland erschließen?",
        "cta_body": "Strategiegespräch buchen — Scope und Budget klären.",
        "card_teaser": "Individuelles Expansionsprojekt — maßgeschneidert.",
    },
]

# RU slugs (transliterated)
RU_SLUG_MAP = {
    "INT-01": "osnovanie-biznesa-germaniya",
    "INT-02": "zhizn-i-rabota-germaniya",
    "INT-03": "biznes-zdorovye-proverka",
    "INT-04": "ekspansiya-dochernaya-kompaniya",
}

EN_SLUG_MAP = {
    "INT-01": "founding-germany",
    "INT-02": "living-working-germany",
    "INT-03": "business-turnaround",
    "INT-04": "expansion-subsidiary",
}

INT_INDEX_EN = {
    "tag": "INTERNATIONAL SERVICES",
    "h1": "Consulting for Russian-speaking founders in Germany",
    "lead": (
        "The best of both worlds: German founding and regulatory expertise plus Russian-native advisors "
        "who make you feel at home — authorities, culture, EU rules, and risks. DE · EN · RU."
    ),
    "title": "International Services | Beraterium",
    "description": "Consulting for Russian-speaking entrepreneurs: founding, integration, turnaround, EU expansion — from €50 intro call.",
    "why_h2": "Why Beraterium for international founders?",
    "why_intro": (
        "We combine local expertise and networks in Germany with a cultural bridge to Russia — "
        "so you get sound advice and personal understanding."
    ),
    "why_cards": [
        (
            "Native Russian — among your own",
            "Veronika Berdnikova and Aleksandra Polosukhina are native Russian speakers. "
            "On request, we advise entirely in Russian — no loss in translation, with the feeling of being among your own.",
        ),
        (
            "Germany expertise",
            "Till Blania knows founding, authorities, laws, German business culture, EU regulations, "
            "and typical risks from years of practice — from idea to operational setup in Germany.",
        ),
        (
            "Both worlds combined",
            "Local network (notaries, attorneys, tax advisors, chambers) plus understanding of Russian "
            "mindsets and communication — you don't have to choose between “correct in German” and “feeling at home”.",
        ),
        (
            "Risk from day one",
            "Spot blind spots early: residence, legal form, taxes, banking, sanctions, culture — "
            "with Beraterium's euro-based evaluation logic, not gut feeling alone.",
        ),
        (
            "Trilingual DE · EN · RU",
            "Real indexable pages at beraterium.de/ru/ — you choose the language, we adapt.",
        ),
    ],
    "team_tag": "YOUR TEAM",
    "team_h2": "German-Russian advisory team — you're in good hands",
    "team_intro": (
        "Two native Russian speakers plus Germany-experienced founding and risk expertise in one team: "
        "Veronika and Aleksandra for trust and understanding in Russian, Till for the path through German "
        "authorities, laws, and rules. We combine both worlds — professionally and personally."
    ),
    "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
    "team_member_intros": {
        "veronika-berdnikova": (
            "Native Russian — your contact for founders from Russia and the CIS. Clear, empathetic, no sales pressure."
        ),
        "aleksandra-polosukhina": (
            "Native Russian — international communication, marketing, and team culture. "
            "Bridge between Russian and German business worlds."
        ),
        "till-blania": (
            "Founding in Germany, authorities, laws, EU requirements, and risk management — "
            "plus HSE St. Petersburg and understanding of the post-Soviet space."
        ),
    },
    "faq": [
        ("Who is this for?", "Entrepreneurs from the post-Soviet space — in Germany, planning to move, or expanding from abroad."),
        (
            "Do you speak Russian?",
            "Yes — Veronika and Aleksandra are native Russian speakers; Till advises in German, English, "
            "and Russian (B1, improving). On request, we run the entire conversation in Russian.",
        ),
        ("Is this legal advice?", "No — business consulting and coordination with partner attorneys."),
        ("Entry price?", "Intro call 30 min for €50 net. Packages from €1,900."),
    ],
    "cta_h2": "Which offer fits your situation?",
    "cta_body": "Book the intro call for €50 — 30 minutes, no obligation, DE/EN/RU.",
}

_EN_OVERRIDES: dict[str, dict] = {
    "INT-01": {"h1": "Start a business in Germany — with plan and risk protection", "tag": "FOUNDING · GERMANY", "card_teaser": "Business plan, authorities, network, risk analysis."},
    "INT-02": {
        "h1": "Living and working in Germany",
        "tag": "INTEGRATION · GERMANY",
        "card_teaser": "Culture, authorities, ELSTER — modular.",
        "lead": (
            "Authorities, language, culture — if you don't feel at home in Germany, you can't build a "
            "stable business. We clear the hurdles: practical, 1-on-1, in Russian or German."
        ),
        "fuer_wen_lead": (
            "Integration in Germany rarely fails for lack of will — but because of language, authorities, "
            "unwritten rules, and feeling like an outsider. Settle in privately first, clear the obstacles — "
            "then business. That's where we help: local know-how, Russian-native advisors, and both worlds combined."
        ),
        "fuer_wen": [
            "German business communication, directness, and small talk feel foreign",
            "Authority letters overwhelm — tax office, trade office, immigration: unclear what to do",
            "ELSTER, tax, insurance — German rules feel like an opaque maze",
            "You're professionally strong but feel unable to navigate the system in Germany",
            "Private life must work first (language, daily life, housing) — otherwise business won't hold",
            "You want to understand and act yourself — not just get translations or stay stuck",
            "Russian-native advisors plus Germany experience — understood and guided, not alone",
            "Parallel to founding or after — modular booking, not a language course",
        ],
    },
    "INT-03": {
        "h1": "Business Health Check",
        "tag": "TURNAROUND",
        "card_teaser": "Authorities, cash flow, growth — structured diagnosis.",
        "lead": (
            "Founded in Germany — it runs, but not quite stable? Tax office, chamber of commerce, occupational "
            "safety, data protection: pressure from every side. From quick check to turnaround support we find "
            "where it sticks — and build strategies you can actually implement."
        ),
        "fuer_wen_lead": (
            "Many founders notice only after launch: revenue looks fine, but cash flow, authorities, and rules "
            "overwhelm. Tax office, IHK, occupational safety, data protection audits with warnings — issues pile "
            "up nobody planned for. That's when the Business Health Check fits: find bottlenecks together, set "
            "priorities, and develop actionable strategies — with support through implementation."
        ),
        "fuer_wen": [
            "You founded in Germany — it runs, but doesn't feel stable",
            "Tax office, chamber, or trade office apply pressure — unclear what to tackle first",
            "Occupational safety, data protection, or warnings — unexpected topics pile up",
            "Revenue there, no cash flow — you don't know where to start",
            "Second location planned (e.g. salon, branch) — without repeating first-site mistakes",
            "Converting sole proprietorship to GmbH — unsure if it makes sense and what options exist",
            "You want clarity and a step-by-step plan you can execute",
        ],
    },
    "INT-04": {
        "h1": "Expansion to Germany",
        "tag": "EXPANSION · EU",
        "card_teaser": "Individual expansion project — scope and budget by agreement.",
        "description": "EU market entry: individual expansion project — scope and budget in strategy call.",
        "lead": (
            "Successful business in Russia — and expansion to Germany? Often it's not the product that "
            "blocks you, but restrictions, compliance, and no local partners. We deliver in Germany: "
            "market analysis, sales setup, company formation, contracts, registrations — as an individual "
            "project. You provide capital and strategy, Beraterium coordinates on-site execution."
        ),
        "fuer_wen_lead": (
            "Many entrepreneurs with running businesses in Russia want the German market — but sanctions, "
            "regulatory hurdles, and missing local contacts hold them back. Each expansion is its own "
            "project: we plan scope, team, and budget together — typically between €30,000 and €100,000, "
            "depending on what you need."
        ),
        "fuer_wen": [
            "Successful business in Russia/CIS — expansion to Germany desired",
            "Sanctions, compliance, or missing local partners block market entry",
            "Market analysis, sales, and company setup in DE — but no on-site team",
            "Subsidiary, contracts, registrations — coordinated from one source",
            "You don't want to handle authorities, notary, and setup in DE yourself",
            "Production/fulfillment can stay at home — presence and sales in Germany",
            "Individual project: you provide capital, Beraterium coordinates on-site delivery",
        ],
        "ergebnis": [
            "DE presence without relocation — minimal on-site operational burden",
            "Compliance-safe structure — sanctions, KYC, clean separation",
            "Market, sales, and company — implemented by Beraterium, not just planned",
        ],
        "faq": [
            ("Do I need to relocate?", "No — Beraterium coordinates on site. You provide capital and strategic decisions."),
            ("Separation from RU company?", "Clean compliance structure — discussed in the strategy call."),
            ("What stays with me?", "Capital, product strategy, approvals — operational setup in DE runs through us."),
            ("How is pricing determined?", "Individual by scope — typically €30,000–100,000 net. Fixed quote after strategy call."),
            ("Attorney and tax advisor?", "Yes — we coordinate specialists from our network. Legal/tax services via partners."),
        ],
        "cta_h2": "Enter the German market?",
        "cta_body": "Book strategy call — clarify scope and budget.",
    },
}


def en_offer_configs() -> list[dict]:
    out: list[dict] = []
    for cfg in INT_OFFER_CONFIGS_DE:
        en = dict(cfg)
        en["slug"] = EN_SLUG_MAP[cfg["nr"]]
        en.update(_EN_OVERRIDES.get(cfg["nr"], {}))
        en["title"] = f"{en['h1']} | Beraterium"
        out.append(en)
    return out
