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
        "Lokales Wissen, deutsch-russisches Team und Risikoanalyse von Anfang an — "
        "für Unternehmer aus dem postsowjetischen Raum. Auf Deutsch, Englisch und Russisch."
    ),
    "title": "Internationale Angebote | Beraterium",
    "description": (
        "Beratung für russischsprachige Gründer in Deutschland: Gründung, Integration, "
        "Turnaround und EU-Expansion — DE/EN/RU, ab 50 € Erstberatung."
    ),
    "why_h2": "Warum Beraterium für internationale Gründer?",
    "why_intro": (
        "Deutsches Regulatorium-Wissen plus muttersprachliche Betreuung — "
        "und Risikoanalyse, die kein Gründungsdienstleister bietet."
    ),
    "why_cards": [
        ("Deutsch-russisches Team", "Veronika Berdnikova und Aleksandra Polosukhina sprechen Russisch; Till Blania lebt und arbeitet in Russland (HSE St. Petersburg)."),
        ("Lokales Netzwerk", "Notare, Anwälte, Steuerberater, IHK — wir kennen den Weg."),
        ("Risiko von Anfang an", "Blind Spots: Aufenthalt, Rechtsform, Steuern, Banken, Kultur."),
        ("Dreisprachig DE · EN · RU", "Echte indexierbare Seiten unter beraterium.de/ru/."),
    ],
    "faq": [
        ("Für wen sind die internationalen Angebote?", "Unternehmer aus dem postsowjetischen Raum — in DE, in Planung oder mit Unternehmen im Ausland."),
        ("Sprechen Sie Russisch?", "Ja — Veronika, Aleksandra und Till (DE/EN/RU)."),
        ("Ist das Rechtsberatung?", "Nein — unternehmerische Beratung und Koordination mit Partneranwälten."),
        ("Was kostet der Einstieg?", "Erstberatung 30 Min. für 50 € netto. Pakete ab 1.900 €."),
        ("BAFA-Förderung?", "Ja, für Business Health Check (INT-03) bis 80 %."),
    ],
    "cta_h2": "Welches Angebot passt zu Ihrer Situation?",
    "cta_body": "Erstberatung für 50 € buchen — 30 Min., unverbindlich, DE/EN/RU.",
}

INT_OFFER_CONFIGS_DE: list[dict] = [
    {
        "nr": "INT-01",
        "slug": "gruendung-deutschland",
        "tag": "GRÜNDUNG · DEUTSCHLAND",
        "h1": "Business in Deutschland gründen — mit Plan und Risikoschutz",
        "lead": (
            "Registrierung ist nur ein Teil des Wegs. Rechtsform, Budget, Behörden, Banking, deutsche Kunden — "
            "wir begleiten Sie Schritt für Schritt, auf Deutsch, Englisch oder Russisch. "
            "Einzelne Bausteine oder Komplettpaket — Sie entscheiden."
        ),
        "title": "Gründung in Deutschland | Internationale Angebote | Beraterium",
        "description": "Gründungsbegleitung für russischsprachige Unternehmer: Stufen ab 990 €, Paket Gründung 360° 5.490 € netto.",
        "audience": "Gründer mit Migrationshintergrund",
        "fuer_wen_intro": "Dieses Angebot passt, wenn:",
        "fuer_wen": [
            "Sie in Deutschland sind oder kommen wollen und sich selbstständig machen",
            "Sie nicht wissen, welche Rechtsform passt (GmbH, UG, GbR, Einzelunternehmen)",
            "Sie Hilfe bei Gewerbeanmeldung, ELSTER, Finanzamt brauchen",
            "Sie Risiken von Anfang an im Blick haben wollen",
        ],
        "leistungen": [
            "Rechtsform-Optionen verständlich einordnen",
            "Businessplan-Struktur und Finanzplan begleiten",
            "Koordination Gewerbeanmeldung, ELSTER, IHK/HWK",
            "Vermittlung Notar, Anwalt, Steuerberater",
            "Fördermittel-Recherche und Risikoanalyse",
        ],
        "steps": [
            ("Erstberatung", "30 Min.: Situation, Ziel, passende Stufe — 50 € (wird angerechnet)."),
            ("Stufe wählen", "Business Check, Roadmap, Begleitung oder Risiko-Check — einzeln buchbar."),
            ("Umsetzung", "Workshops, Calls, Checklisten — mit Spezialisten aus dem Netzwerk."),
            ("Go-Live", "Dokumentierter Status, Risikoplan, optional Folgepaket INT-03."),
        ],
        "ergebnis": [
            "Klarer Gründungsfahrplan — Woche für Woche",
            "Netzwerk Notar, Steuerberater, IHK eingebunden",
            "Typische Blind Spots erkannt, bevor sie teuer werden",
        ],
        "team_slugs": ["veronika-berdnikova", "aleksandra-polosukhina", "till-blania"],
        "faq": [
            ("Kann ich als Ausländer gründen?", "Ja — je nach Aufenthaltstitel. Wir klären das in INT-00 oder INT-01-A."),
            ("Was kostet es?", "Einzelstufen ab 990 € · Roadmap + Begleitung 4.490 € · Gründung 360° 5.490 € netto."),
            ("Einzeln oder Paket?", "Wie bei der Risikoanalyse: jede Stufe einzeln — Pakete günstiger als die Summe."),
            ("Rechtsberatung?", "Nein — Koordination mit Partneranwälten und Steuerberatern."),
        ],
        "cta_h2": "Gründung planen?",
        "cta_body": "Erstberatung buchen — 50 €, 30 Min., DE/EN/RU.",
        "card_teaser": "Stufen ab 990 € · Paket Gründung 360° 5.490 €.",
    },
    {
        "nr": "INT-02",
        "slug": "leben-arbeiten-deutschland",
        "tag": "INTEGRATION · DEUTSCHLAND",
        "h1": "Leben und Arbeiten in Deutschland",
        "lead": "Behördenbriefe, deutsche Direktheit, ELSTER — praxisnah erklärt, 1-zu-1, modular wie unsere Gründungsangebote.",
        "title": "Leben & Arbeiten in Deutschland | Beraterium",
        "description": "Coaching: deutsche Kultur, Behörden, Fettnäpfchen — ab 180 €/Std., Paket 2.900 €.",
        "audience": "Neu angekommene Gründer",
        "fuer_wen_intro": "Passt, wenn:",
        "fuer_wen": [
            "Deutsche Business-Kommunikation unklar ist",
            "Behördenbriefe überfordern",
            "Sie Finanzamt, Gewerbeamt, Ausländerbehörde verstehen wollen",
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
        "lead": "Finanzen, Team, Prozesse — wenn etwas hakt, finden wir es strukturiert. Vom Quick Check bis zur Turnaround-Begleitung.",
        "title": "Business Turnaround | Beraterium",
        "description": "Engpässe finden, Lösungen priorisieren — ab 3.500 €, BAFA-förderfähig.",
        "audience": "Laufende Unternehmen mit Problemen",
        "fuer_wen_intro": "Passt, wenn:",
        "fuer_wen": [
            "Finanzamt oder Regulatorik Probleme macht",
            "Umsatz da, kein Cashflow",
            "Sie nicht wissen, wo anfangen",
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
        "ergebnis": ["Klarheit über Engpässe", "Priorisierte Maßnahmen", "Umsetzungsfahrplan"],
        "team_slugs": ["till-blania", "veronika-berdnikova", "peter-muenstermann"],
        "faq": [
            ("BAFA?", "Ja — voller Health Check (INT-03-B) ab 3.500 € förderfähig."),
            ("Quick Check vs. voller Check?", "Quick Check (790 €) = 90 Min. Diagnose. Voller Check = Beraterium-Methode mit Workshops."),
            ("Einzelrisiken?", "Nein — nur im Paket-Kontext (RA-02)."),
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
        "lead": "Tochtergesellschaft aufbauen, Vor-Ort-Vertrieb — Fulfillment im Heimatland möglich.",
        "title": "Expansion DE | Beraterium",
        "description": "EU-Markteintritt: Setup, Compliance, Retainer — ab 9.500 €.",
        "audience": "Unternehmen im Ausland",
        "fuer_wen_intro": "Passt, wenn:",
        "fuer_wen": [
            "EU-Markt ohne sofortigen Umzug",
            "Tochtergesellschaft in DE nötig",
            "Compliance/Sanktionen relevant",
        ],
        "leistungen": [
            "Markteintritts- und Risikoanalyse",
            "Tochtergesellschaft — Koordination Notar/Anwalt",
            "KYC/AML, Sanktions-Check",
            "Vor-Ort-Management und Retainer",
        ],
        "steps": [
            ("Strategie", "Markt, Struktur, Compliance."),
            ("Setup", "Gesellschaft, Konten, Team."),
            ("Go-to-Market", "Vertrieb, erste Kunden."),
            ("Retainer", "Laufendes Management."),
        ],
        "ergebnis": ["DE-Präsenz ohne Umzug", "Compliance-sichere Struktur", "Lokales Netzwerk"],
        "team_slugs": ["till-blania", "veronika-berdnikova", "aleksandra-polosukhina"],
        "faq": [
            ("Trennung von RU-Firma?", "Saubere Struktur nach Compliance — im Strategiegespräch."),
            ("Retainer?", "Ab 4.500 €/Monat, min. 6 Monate."),
        ],
        "cta_h2": "EU-Markt erschließen?",
        "cta_body": "Strategiegespräch buchen.",
        "card_teaser": "Tochtergesellschaft, Vor-Ort-Management.",
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
    "lead": INT_INDEX_DE["lead"].replace("Auf Deutsch, Englisch und Russisch.", "In German, English, and Russian."),
    "title": "International Services | Beraterium",
    "description": "Consulting for Russian-speaking entrepreneurs: founding, integration, turnaround, EU expansion — from €50 intro call.",
    "why_h2": "Why Beraterium for international founders?",
    "why_intro": "German regulatory knowledge plus native-language support — and risk analysis no formation agent offers.",
    "why_cards": [
        ("German-Russian team", "Veronika Berdnikova and Aleksandra Polosukhina speak Russian; Till Blania has lived and worked in Russia (HSE St. Petersburg)."),
        ("Local network", "Notaries, attorneys, tax advisors, chambers — we know the path."),
        ("Risk from day one", "Blind spots: residence, legal form, taxes, banking, culture."),
        ("Trilingual DE · EN · RU", "Real indexable pages at beraterium.de/ru/."),
    ],
    "faq": [
        ("Who is this for?", "Entrepreneurs from the post-Soviet space — in Germany, planning to move, or expanding from abroad."),
        ("Do you speak Russian?", "Yes — Veronika, Aleksandra, and Till (DE/EN/RU)."),
        ("Is this legal advice?", "No — business consulting and coordination with partner attorneys."),
        ("Entry price?", "Intro call 30 min for €50 net. Packages from €1,900."),
    ],
    "cta_h2": "Which offer fits your situation?",
    "cta_body": "Book the intro call for €50 — 30 minutes, no obligation, DE/EN/RU.",
}

_EN_OVERRIDES: dict[str, dict] = {
    "INT-01": {"h1": "Start a business in Germany — with plan and risk protection", "tag": "FOUNDING · GERMANY", "card_teaser": "Business plan, authorities, network, risk analysis."},
    "INT-02": {"h1": "Living and working in Germany", "tag": "INTEGRATION · GERMANY", "card_teaser": "Culture, authorities, ELSTER — modular."},
    "INT-03": {"h1": "Business Health Check", "tag": "TURNAROUND", "card_teaser": "Risk analysis for running businesses."},
    "INT-04": {"h1": "Expansion to Germany", "tag": "EXPANSION · EU", "card_teaser": "Subsidiary and on-site management."},
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
