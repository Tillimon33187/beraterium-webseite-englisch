"""Page content for training subpages /training/<slug>/.

Reine Daten (keine Imports aus _gen_pages, wird von dort importiert).
Preise/Staffeln kommen NICHT von hier, sondern aus _pricing.py (Join über
"nr"); hier steht nur der redaktionelle Seiteninhalt.
Quelle der Inhalte: Angebote/training/*.md
"""
from __future__ import annotations

SCHULUNG_CONFIGS: list[dict] = [
    {
        "nr": "SCH-07",
        "slug": "risk-expert",
        "tag": "AUSBILDUNG · KOMBI AUS DREI SCHULUNGEN",
        "h1": "Ausbildung zum Risikoexperten",
        "lead": (
            "Die komplette Ausbildung für alle, die Risikomanagement im Unternehmen "
            "verantworten: Diese Kombi-Schulung vereint unsere drei Risikomanagement-Training "
            "zu einem tiefgreifenden Programm — die Risk-Awareness-Kultur nach Luftfahrt-Vorbild, "
            "„Der risikobewusste Manager“ und „Risikomanagement praktisch umsetzen“. Sie "
            "befähigt Manager und Mitarbeitende, unsere Methode eigenständig im eigenen "
            "Unternehmen aufzubauen und dauerhaft zu betreiben. Drei Tage intensiv, inhouse "
            "oder online, mit Zertifikat."
        ),
        "title": "Ausbildung zum Risikoexperten | Beraterium",
        "description": "Kombi-Schulung aus drei Trainings: Risikokultur, risikobewusste Führung und praktische Risikoanalyse — 3 Tage, Zertifikat, ab 9.875 € excl. VAT (2 Personen 14.315 €).",
        "audience": "künftige Risikoverantwortliche, Manager und Mitarbeitende",
        "fuer_wen_intro": "Diese Ausbildung passt, wenn einer dieser Punkte zutrifft:",
        "fuer_wen": [
            "Sie sollen Risikomanagement im Unternehmen aufbauen und verantworten — und wollen es von Grund auf beherrschen",
            "Ihnen reicht ein Einzelthema nicht: Sie wollen Kultur, Führung UND Methode in einem Durchgang",
            "Sie sind Manager:in oder Mitarbeiter:in mit der Aufgabe, die Beraterium-Methode intern umzusetzen",
            "Sie wollen Risikomanagement dauerhaft intern lösen, statt es dauerhaft einzukaufen",
        ],
        "sessions": [
            ("Modul 1 — Risk-Awareness-Kultur aufbauen", [
                "Just Culture nach Luftfahrt-Vorbild: Fehler offen zugeben statt vertuschen",
                "Führungsstruktur: Meldewege, Blameless Debriefings, Fehler-Rituale",
                "Team einbinden: aus Fehlern lernen statt Schuldige suchen",
                "Praxis-Simulation: Debriefing eines echten (anonymisierten) Fehlerfalls",
            ]),
            ("Modul 2 — Risikobewusste Führung", [
                "Fehlerangst ablegen und Risiken als kalkulierte Chance begreifen",
                "Entscheidungs-Frameworks: Erwartungswert, Worst-Case-Tragfähigkeit, Reversibilität",
                "Das eigene Unternehmen von außen sehen: Pre-Mortem und Konkurrenz-Perspektive",
                "Vorbildwirkung: eine offene Risikokultur vorleben",
            ]),
            ("Modul 3 — Risikomanagement praktisch umsetzen", [
                "Das Beraterium-System: von der Gefahr über das Risiko zur Maßnahme",
                "Risikoanalyse mit dem Team durchführen und mit der Matrix bewerten",
                "3-Ebenen-Gefahrenkatalog anwenden — Sie erhalten den vollständigen Katalog",
                "Risiken in Euro bewerten und umsetzbare Maßnahmen ableiten und verankern",
            ]),
            ("Abschluss — Zertifizierung & Transfer", [
                "Alle Module an einem eigenen, realen Unternehmensbereich zusammenführen",
                "Ihr Transferplan: wie Sie die Methode in den nächsten Wochen im Unternehmen ausrollen",
                "Check-in-Call nach der Ausbildung: offene Fragen, Nachjustieren",
                "Zertifikat „Risikoexperte:in — Beraterium-Methode“",
            ]),
        ],
        "ergebnis": [
            "Sie beherrschen die komplette Beraterium-Methode: Kultur, Führung und praktische Risikoanalyse",
            "Sie können eine Risk-Awareness-Kultur aufbauen, Risiken kalkuliert führen und die Analyse selbst durchführen",
            "Der vollständige 3-Ebenen-Gefahrenkatalog bleibt im Unternehmen und ist sofort einsetzbar",
            "Zertifikat als Risikoexperte:in plus Transferplan für die Umsetzung im eigenen Unternehmen",
        ],
        "workload_iso": "PT24H",
        "faq": [
            ("Was ist die Ausbildung zum Risikoexperten genau?", "Eine Kombi-Schulung, die unsere drei Risikomanagement-Training zu einem durchgängigen Programm bündelt: Risk-Awareness-Kultur, „Der risikobewusste Manager“ und „Risikomanagement praktisch umsetzen“. Das Ziel: Sie beherrschen Kultur, Führung und Methode und können unsere Vorgehensweise eigenständig im Unternehmen umsetzen."),
            ("Was kostet die Ausbildung?", "9.875 € für eine Person, 14.315 € für zwei Personen, plus 4.440 € je weiterem Teilnehmer. Für bis zu 4 Personen gilt die Pauschale von 22.875 € (max. 4 Teilnehmer) — inklusive Gefahrenkatalog und Zertifikat. Die Investition liegt bewusst auf Augenhöhe mit unserer begleiteten Risiko-Analyse 360° (3.475 €) bzw. dem Gesamtpaket XL (9.675 €) — Sie bauen die Methode dauerhaft intern auf, statt Risikomanagement dauerhaft einzukaufen. Alle Preise excl. VAT excl. VAT"),
            ("Für wen ist die Ausbildung gedacht?", "Für Manager und Mitarbeitende, die Risikomanagement im Unternehmen aufbauen und verantworten sollen — also künftige Risikoverantwortliche, die das komplette Rüstzeug in einem Durchgang wollen, statt einzelne Themen nacheinander."),
            ("Lohnt sich die Kombi gegenüber den Einzelschulungen?", "Ja — inhaltlich und wirtschaftlich. Die drei Einzelschulungen im Intensivformat (1:1 oder Kleinstgruppe) kosten einzeln zusammen 12.425 €. In der Kombi-Ausbildung laufen die Module kompakter im Durchgang — dafür zahlen Sie 9.875 € und erhalten das Gesamtprogramm inklusive Zertifikat und Transferplan."),
            ("Wie lange dauert die Ausbildung und gibt es ein Zertifikat?", "Drei Tage intensiv (ca. 24 Stunden) plus Transferphase — inhouse oder online, auf Wunsch auf mehrere Termine verteilt. Zum Abschluss erhalten Sie das Zertifikat „Risikoexperte:in — Beraterium-Methode“ und einen Transferplan für die Umsetzung."),
        ],
        "cta_h2": "Werden Sie zum Risikoexperten in Ihrem Unternehmen",
        "cta_body": "Im freeen Erstgespräch klären wir Vorkenntnisse, Teamgröße, Format und Termine — unverbindlich, in 30 Minuten.",
    },
    {
        "nr": "SCH-01",
        "slug": "risk-awareness-culture",
        "tag": "SCHULUNG · FÜHRUNG + TEAM",
        "h1": "Risikomanagement: Der Weg zur Risk-Awareness-Kultur",
        "lead": (
            "Diese Schulung zeigt, wie Sie ein Team so vorbereiten und führen, dass Risiken "
            "und Fehler kein Tabu mehr sind, sondern zum Lernprozess gehören. Am Vorbild der "
            "Luftfahrt bauen wir eine Aus-Fehlern-lernen-Kultur auf: Fehler werden offen "
            "zugegeben und gefeiert statt bestraft — weg von der Fingerzeig-Kultur, hin zum "
            "gemeinsamen Verbessern. Ein Tag im Intensivformat (1:1 oder Kleinstgruppe), inhouse oder online — wesentlich detaillierter als das Kultur-Modul in der Kombi-Ausbildung."
        ),
        "title": "Schulung Risk-Awareness-Kultur | Beraterium",
        "description": "Intensivformat (1:1 oder Kleinstgruppe): Fehlerkultur und Risk Awareness vertiefen — 1 Tag, ab 3.975 € netto, Team ab 11.475 € pauschal.",
        "audience": "Führungskräfte und Teams",
        "fuer_wen_intro": "Diese Schulung passt, wenn mindestens einer dieser Punkte zutrifft:",
        "fuer_wen": [
            "Fehler werden bei Ihnen vertuscht statt gemeldet — und fallen erst auf, wenn es teuer wird",
            "Bei Problemen wird zuerst nach dem Schuldigen gesucht, nicht nach der Ursache",
            "Sie wollen, dass Ihr Team Risiken früh anspricht, statt zu schweigen und zu hoffen",
            "Sie führen Risikomanagement ein und brauchen die kulturelle Grundlage dafür",
        ],
        "sessions": [
            ("Session 1 — Führung & Struktur (3 h)", [
                "Risk Awareness: Risikobewusstsein vs. Risikoangst vs. Risikoblindheit",
                "Die Anatomie der Schweigekultur — warum Fehler unter den Tisch fallen und was das kostet",
                "Just Culture nach Luftfahrt-Vorbild: menschlicher Fehler, Risikoverhalten, grobe Fahrlässigkeit",
                "Führungsstruktur implementieren: Meldewege, Blameless Debriefings, Fehler-Rituale",
                "Fehler feiern statt bestrafen: Formate, die das Zugeben belohnen",
            ]),
            ("Session 2 — Team & Mitarbeit (3 h)", [
                "Alle zum Mitarbeiten bringen: an Prozessen arbeiten statt schweigen und hoffen",
                "Psychologische Sicherheit praktisch: Übungen und Gesprächsformate",
                "Vom Fehler zum Prozess: die Lernschleife melden → analysieren → ändern → prüfen",
                "Frühwarnsystem Team: Mitarbeitende als Sensoren für Risiken",
                "Praxis-Simulation: Debriefing eines echten (anonymisierten) Fehlerfalls nach Luftfahrt-Schema",
            ]),
            ("Transfer — Verankerung im Alltag (inklusive)", [
                "30-Tage-Umsetzungsplan: welche Rituale und Meldewege wann eingeführt werden",
                "Arbeitsvorlagen zum Behalten: Meldeweg-Schema, Debriefing-Leitfaden, Fehler-Ritual-Formate",
                "Check-in-Call nach 4 Wochen: was funktioniert, wo hakt es, was wird nachjustiert",
            ]),
        ],
        "ergebnis": [
            "Konkrete Struktur (Meldewege, Rituale, Debriefing-Format), einführbar ab Tag 1",
            "Das Team hat erlebt: offenes Ansprechen wird belohnt, nicht bestraft",
            "Weniger vertuschte Fehler — Risiken werden früher sichtbar, Schäden kleiner",
            "Kulturelles Fundament für jede weitere Risikomanagement-Maßnahme",
        ],
        "workload_iso": "PT6H",
        "faq": [
            ("Für wen ist die Schulung Risk-Awareness-Kultur gedacht?", "Für Führungskräfte und Team gemeinsam — die Kultur entsteht nur, wenn beide Seiten dieselben Prinzipien lernen. Buchbar für einzelne Mitarbeitende, Kleingruppen oder das ganze Team."),
            ("Was kostet die Schulung?", "Intensivformat: 3.975 € für die erste Person, plus 995 € je weiterem. Ab 10 Personen gilt die gedeckelte Pauschale von 11.475 €. Wesentlich detaillierter und persönlicher als das Kultur-Modul in der Kombi-Ausbildung zum Risikoexperten (9.875 €). Alle Preise excl. VAT excl. VAT"),
            ("Warum die Luftfahrt als Vorbild?", "Die Luftfahrt ist die sicherheitskritischste Branche der Welt und hat zugleich die offenste Fehlerkultur: Just Culture, sanktionsfreie Meldesysteme und strukturierte Debriefings. Diese Prinzipien sind direkt auf Unternehmen übertragbar — ein gemeldeter Beinahe-Fehler ist wertvoller als ein vertuschter Schaden."),
            ("Wie lange dauert die Schulung und in welchem Format?", "Ein Tag mit zwei Sessions à 3 Stunden — inhouse bei Ihnen vor Ort oder online. Session 1 fokussiert Führung und Struktur, Session 2 das Team und die Mitarbeit. Inklusive Transfer-Paket: 30-Tage-Umsetzungsplan, Arbeitsvorlagen und ein Check-in-Call nach 4 Wochen."),
            ("Was unterscheidet die Schulung vom Workshop „Kulturelle Grundlage“?", "Der 180-Minuten-Workshop sensibilisiert für psychologische Sicherheit. Die Schulung geht deutlich tiefer: Sie implementiert eine komplette Führungsstruktur nach Luftfahrt-Vorbild — mit Meldewegen, Debriefing-Formaten und einer Praxis-Simulation an einem echten Fehlerfall."),
        ],
        "cta_h2": "Bauen Sie eine Kultur auf, in der Risiken sichtbar werden",
        "cta_body": "Im freeen Erstgespräch klären wir Teamgröße, Format und Termin — unverbindlich, in 30 Minuten.",
    },
    {
        "nr": "SCH-02",
        "slug": "risk-aware-manager",
        "tag": "SCHULUNG · NUR FÜHRUNGSKRÄFTE",
        "h1": "Der risikobewusste Manager",
        "lead": (
            "Diese Schulung ist speziell für Manager:innen: die Angst vor Fehlern verlieren "
            "und sie als Chance zum Wachstum sehen, die Angst vor Risiken abbauen und sie "
            "kalkuliert eingehen — und das eigene Unternehmen wieder mit einer neutralen "
            "Brille von außen betrachten, um ein frisches Gefühl für die eigenen Prozesse "
            "und Risiken zu bekommen. Ein Kompakt-Tag, inhouse oder online."
        ),
        "title": "Schulung: Der risikobewusste Manager | Beraterium",
        "description": "Intensivformat für Führungskräfte (1:1): Fehlerangst ablegen, Risiken kalkuliert eingehen — Kompakt-Tag ab 3.475 € netto, Führungsteam ab 9.875 € pauschal.",
        "audience": "Geschäftsführer, Führungskräfte und Gründer",
        "fuer_wen_intro": "Diese Schulung passt, wenn Sie sich in einem dieser Punkte wiederfinden:",
        "fuer_wen": [
            "Sie zögern Entscheidungen hinaus, weil das Risiko schwer greifbar ist",
            "Fehler — eigene wie fremde — fühlen sich wie Versagen an statt wie Lernstoff",
            "Sie stecken so tief im Tagesgeschäft, dass Sie die eigenen Prozesse nicht mehr neutral sehen",
            "Sie wollen Risiken nicht vermeiden, sondern bewusst und kalkuliert eingehen",
        ],
        "sessions": [
            ("Block 1 — Die eigene Haltung zu Fehlern (2 h)", [
                "Fehlerangst verstehen: woher sie kommt und was sie im Führungsalltag anrichtet",
                "Fehler als Wachstumschance: Reframing vom „Das darf nicht passieren“ zum „Was lernen wir daraus?“",
                "Vorbildwirkung: das Team ist nur so offen wie seine Führung",
            ]),
            ("Block 2 — Risiken kalkuliert eingehen (2 h)", [
                "Risikoangst vs. Risikokompetenz: Vermeiden, Verdrängen oder bewusst entscheiden",
                "Entscheidungs-Frameworks: Erwartungswert, Worst-Case-Tragfähigkeit, Reversibilität",
                "Die Chancen-Seite: Risiken, die man eingehen sollte — und wie man sie begründet",
            ]),
            ("Block 3 — Das eigene Unternehmen von außen sehen (2 h)", [
                "Betriebsblindheit als Risiko: warum der neutrale Blick nach Jahren verloren geht",
                "Die Außenbrille: Pre-Mortem, Konkurrenz-Perspektive, Neueinsteiger-Walkthrough",
                "Praxisübung: eigenen Kernprozess von außen analysieren — Top-3-Risiken und -Chancen",
            ]),
        ],
        "ergebnis": [
            "Persönliches Risiko-Mindset: unter Unsicherheit entscheiden, ohne zu lähmen",
            "Konkrete Frameworks für kalkulierte Risiko-Entscheidungen im Alltag",
            "Frischer Außenblick auf die eigenen Prozesse — inklusive Top-Risiken und -Chancen",
            "Fundament, um im Team eine offene Risikokultur vorzuleben",
        ],
        "workload_iso": "PT6H",
        "faq": [
            ("Für wen ist die Schulung „Der risikobewusste Manager“ gedacht?", "Ausschließlich für Führungskräfte: Geschäftsführer:innen, Bereichs- und Teamleitungen, Gründer:innen. Der geschützte Rahmen ohne eigene Mitarbeitende ist Absicht — hier darf offen über eigene Ängste und Fehler gesprochen werden."),
            ("Was kostet die Schulung?", "Intensivformat: 3.475 € für die erste Führungskraft, plus 875 € je weiterer. Ab 8 Personen gilt die gedeckelte Pauschale von 9.875 €. Geschützter 1:1-Rahmen — deutlich tiefer als Modul 2 in der Kombi-Ausbildung. Alle Preise excl. VAT excl. VAT"),
            ("Was bedeutet „das Unternehmen von außen betrachten“?", "Nach einigen Jahren im eigenen Unternehmen sieht niemand die eigenen Prozesse mehr neutral — Betriebsblindheit ist selbst ein Risiko. Mit Techniken wie Pre-Mortem und Konkurrenz-Perspektive gewinnen Sie den Außenblick zurück und erkennen Risiken und Chancen, die im Alltag unsichtbar geworden sind."),
            ("Wie lange dauert die Schulung?", "Ein Kompakt-Tag mit drei Blöcken à 2 Stunden — inhouse oder online. Auf Wunsch teilen wir die Blöcke auf zwei halbe Tage auf."),
            ("Geht es darum, mehr oder weniger Risiken einzugehen?", "Weder noch — es geht um kalkulierte Risiken: bewusst entscheiden statt vermeiden oder verdrängen. Sie lernen Frameworks, mit denen Sie einschätzen, welche Risiken Ihr Unternehmen tragen kann und welche Chancen das Eingehen wert sind."),
        ],
        "cta_h2": "Führen Sie mit Risikokompetenz statt Risikoangst",
        "cta_body": "Im freeen Erstgespräch klären wir, ob die Schulung zu Ihrer Situation passt — unverbindlich, in 30 Minuten.",
    },
    {
        "nr": "SCH-03",
        "slug": "practical-risk-management",
        "tag": "SCHULUNG · TEAM + FÜHRUNG + RISIKOMANAGER",
        "h1": "Risikomanagement praktisch umsetzen",
        "lead": (
            "In dieser Schulung lernen Sie unser System der Risikobewertung — und wie Sie es "
            "selbst anwenden: Schritt für Schritt eine Risikoanalyse mit dem Team durchführen, "
            "Risiken mit der Matrix bestimmen, mit dem Gefahrenkatalog arbeiten (Sie erhalten "
            "unseren vollständigen Katalog), Risiken in Euro bewerten und daraus umsetzbare, "
            "verständliche Maßnahmen ableiten. So wird es im Großkonzern gemacht — "
            "heruntergebrochen auf praxistaugliche Schritte."
        ),
        "title": "Schulung Risikomanagement praktisch | Beraterium",
        "description": "Intensivformat: Risikoanalyse selbst durchführen lernen — Matrix, Gefahrenkatalog (inklusive), Euro-Bewertung — 1,5 Tage, ab 4.975 € netto, Team 14.375 € pauschal.",
        "audience": "Mitarbeitende, Führungskräfte, Risikomanager und Unternehmer",
        "fuer_wen_intro": "Diese Schulung passt, wenn einer dieser Punkte zutrifft:",
        "fuer_wen": [
            "Sie sind Risikomanager:in und wollen verstehen, wie das Ganze richtig geht — wie im Großkonzern, aber praxistauglich",
            "Sie wollen Risikomanagement dauerhaft intern lösen, statt es einzukaufen",
            "Ihr Team soll die jährliche Risikoanalyse künftig selbst durchführen",
            "Sie wollen Risiken nicht in Ampelfarben, sondern in Euro bewerten und daraus echte Maßnahmen ableiten",
        ],
        "sessions": [
            ("Session 1 — Das System verstehen (4 h)", [
                "Das Beraterium-Vorgehen im Überblick: von der Gefahr zum Risiko zur Maßnahme",
                "Der 3-Ebenen-Gefahrenkatalog: Aufbau, Logik, Anwendung — Sie erhalten den vollständigen Katalog",
                "Gefahren sammeln mit dem Team: Moderationstechnik für die Erhebung",
            ]),
            ("Session 2 — Bewerten mit Matrix und Euro (4 h)", [
                "Die Risikomatrix richtig verwenden — und typische Bewertungsfehler vermeiden",
                "Von der Ampel zum Euro: Erwartungswert, Bandbreiten, Worst Case, Priorisierung",
                "Praxisteil: komplette Bewertung an einem eigenen, realen Bereich",
            ]),
            ("Session 3 — Maßnahmen ableiten und verankern (4 h)", [
                "Von der Zahl zur Maßnahme: vermeiden, vermindern, übertragen, tragen",
                "Maßnahmen budgetieren: Kosten der Maßnahme vs. Euro-Risiko",
                "Verankerung im Alltag: Rhythmus, Ownership, Review — Routine statt Einmalprojekt",
                "Abschluss: jede:r geht mit einer begonnenen, echten Risikoanalyse nach Hause",
            ]),
        ],
        "ergebnis": [
            "Sie führen eine Risikoanalyse nach Beraterium-System selbstständig durch: erheben → Matrix → Euro → Maßnahmen",
            "Der vollständige 3-Ebenen-Gefahrenkatalog bleibt im Unternehmen und ist sofort einsetzbar",
            "Konzern-Methodik in KMU-tauglichem Aufwand — gleiche Sprache, weniger Bürokratie",
            "Eine begonnene echte Analyse als direkter Startpunkt nach der Schulung",
        ],
        "workload_iso": "PT12H",
        "faq": [
            ("Für wen ist die Schulung „Risikomanagement praktisch umsetzen“ gedacht?", "Für Mitarbeitende und Führungskräfte, die die Risikoanalyse künftig selbst durchführen sollen — und ausdrücklich auch für Risikomanager aus Unternehmen sowie Unternehmer:innen, die Risikomanagement intern lösen wollen, statt es einzukaufen."),
            ("Was kostet die Schulung?", "Intensivformat: 4.975 € für die erste Person, plus 1.175 € je weiterem. Ab 10 Personen gilt die gedeckelte Pauschale von 14.375 € — inklusive vollständigem Gefahrenkatalog. Deutlich umfangreicher als Modul 3 in der Kombi-Ausbildung. Alle Preise excl. VAT excl. VAT"),
            ("Was ist im Gefahrenkatalog enthalten?", "Alle Teilnehmenden erhalten unseren vollständigen 3-Ebenen-Gefahrenkatalog — dasselbe Arbeitsmittel, das wir in Kundenprojekten einsetzen. Er stellt sicher, dass bei der Erhebung keine Gefahrenklasse übersehen wird, und bleibt nach der Schulung im Unternehmen."),
            ("Wie unterscheidet sich die Schulung von einer Risikoanalyse durch Beraterium?", "Bei der Risiko-Analyse 360° führen wir die Analyse für Sie durch. In dieser Schulung lernen Sie, es selbst zu tun — Methode, Matrix, Euro-Bewertung und Maßnahmenableitung. Viele Kunden kombinieren beides: erst die begleitete Analyse, dann die Schulung fürs Team."),
            ("Wie lange dauert die Schulung?", "1,5 Tage mit drei Sessions à 4 Stunden — inhouse oder online. Im Praxisteil arbeiten die Teilnehmenden durchgehend an einem eigenen, realen Unternehmensbereich."),
        ],
        "cta_h2": "Lernen Sie, Risiken selbst in Euro zu bewerten",
        "cta_body": "Im freeen Erstgespräch klären wir Vorkenntnisse, Teamgröße und Termin — unverbindlich, in 30 Minuten.",
    },
    {
        "nr": "SCH-04",
        "slug": "innovation-management",
        "tag": "SCHULUNG · FÜHRUNG + TEAM",
        "h1": "Schulung zu Innovationsmanagement",
        "lead": (
            "Innovationsmanagement ist ein Kern-Teilbereich der Unternehmensentwicklung. In "
            "dieser Schulung geht es darum, ein durch und durch innovatives Unternehmen zu "
            "werden und zu bleiben — nicht einmal ein Produkt auf den Markt bringen und in "
            "Vergessenheit geraten, sondern über Jahre innovativ bleiben und sich auch gegen "
            "große Konkurrenten durchsetzen. Team, Atmosphäre, Management und Innovationskultur: "
            "wie Business, Innovation und R&D unter einen Hut kommen."
        ),
        "title": "Schulung Innovationsmanagement | Beraterium",
        "description": "Innovationskultur, Pipeline und Kennzahlen — 1 Tag, inhouse oder online, ab 2.995 € netto, Team ab 9.695 € pauschal.",
        "audience": "Führungskräfte und Teams aus Business, Produkt und R&D",
        "fuer_wen_intro": "Diese Schulung passt, wenn einer dieser Punkte zutrifft:",
        "fuer_wen": [
            "Ihr letztes erfolgreiches Produkt ist eine Weile her — die Pipeline dahinter ist dünn",
            "Ideen gibt es viele, aber kein wiederholbarer Weg von der Idee zur Marktleistung",
            "Tagesgeschäft und Innovation konkurrieren um dieselben Leute und Budgets",
            "Sie wollen sich gegen größere Wettbewerber behaupten, ohne deren Budgets zu haben",
        ],
        "sessions": [
            ("Session 1 — Innovationsfähigkeit aufbauen (3,5 h)", [
                "Was innovative Unternehmen anders machen: Innovation als Fähigkeit statt Projekt",
                "Kultur und Atmosphäre: psychologische Sicherheit, Experimentierbudget, Umgang mit gescheiterten Ideen",
                "Team und Rollen: Ideen aus dem ganzen Team systematisch einsammeln",
                "Management: Portfolio-Denken, Stage-Gate light für KMU, Kill-Kriterien",
            ]),
            ("Session 2 — Business, Innovation und R&D unter einem Hut (3,5 h)", [
                "Der Spagat: heute Geld verdienen, morgen relevant bleiben — Ressourcen-Split in der Praxis",
                "Gegen Große bestehen: Nische, Geschwindigkeit und Kundennähe als KMU-Waffen",
                "Innovations-Pipeline bauen: Idee → Validierung → Pilot → Skalierung",
                "Messen und steuern: wenige sinnvolle Kennzahlen statt Innovationstheater",
                "Praxisteil: Mini-Pipeline für ein eigenes, reales Innovationsthema",
            ]),
            ("Transfer — Pipeline im Alltag (inklusive)", [
                "Arbeitsvorlagen zum Behalten: Pipeline-Board, Kill-Kriterien-Checkliste, Experiment-Canvas",
                "Validierungsplan für das begonnene Innovationsvorhaben — die nächsten 30 Tage",
                "Check-in-Call nach 4 Wochen: Pipeline im Review, Stolpersteine nachjustieren",
            ]),
        ],
        "ergebnis": [
            "Gemeinsames Verständnis, was Innovationsfähigkeit im eigenen Unternehmen konkret heißt",
            "Ein leichtgewichtiger, wiederholbarer Innovationsprozess mit klaren Entscheidungspunkten",
            "Klarheit über Rollen, Ressourcen-Split und Kennzahlen — Business und Innovation arbeiten zusammen",
            "Ein begonnenes, reales Innovationsvorhaben mit Validierungsplan",
        ],
        "workload_iso": "PT7H",
        "faq": [
            ("Für wen ist die Innovationsmanagement-Schulung gedacht?", "Für Führungskräfte und Teams aus Business, Produkt und R&D — gemeinsam oder getrennt. Sie ist bewusst KMU- und startup-tauglich gehalten: kein Konzern-Framework, sondern Prozesse, die mit kleinen Teams funktionieren."),
            ("Was kostet die Schulung?", "2.995 € für die erste Person, plus 745 € je weiterem. Ab 10 Personen gilt die gedeckelte Pauschale von 9.695 €. Alle Preise excl. VAT excl. VAT"),
            ("Was bringt mir die Schulung, wenn wir schon innovativ sind?", "Einmal innovativ sein ist leicht — innovativ bleiben ist das Problem. Die Schulung baut die Strukturen, mit denen Innovationskraft wiederholbar wird: Pipeline, Portfolio-Denken, Kill-Kriterien und ein Ressourcen-Split, der das Tagesgeschäft nicht kannibalisiert."),
            ("Wie lange dauert die Schulung?", "Ein Tag mit zwei Sessions à 3,5 Stunden — inhouse oder online. Im Praxisteil arbeiten die Teilnehmenden an einem eigenen, realen Innovationsthema. Inklusive Transfer-Paket: Arbeitsvorlagen, Validierungsplan und ein Check-in-Call nach 4 Wochen."),
            ("Wie hängen Innovation und Risikomanagement zusammen?", "Innovation heißt, kalkulierte Risiken einzugehen. Wer Innovationsrisiken bewusst bewertet — statt sie zu vermeiden oder blind einzugehen — investiert an den richtigen Stellen. Beide Disziplinen teilen dieselbe Grundlage: eine Kultur, in der Scheitern Lernstoff ist."),
        ],
        "cta_h2": "Machen Sie Innovation zur wiederholbaren Fähigkeit",
        "cta_body": "Im freeen Erstgespräch klären wir Ausgangslage, Teamgröße und Termin — unverbindlich, in 30 Minuten.",
    },
    {
        "nr": "SCH-05",
        "slug": "feedback-culture",
        "tag": "SCHULUNG · FÜR ALLE",
        "h1": "Feedbackkultur & eine 1+ Arbeitsumgebung",
        "lead": (
            "In dieser Schulung bauen Führung und Team gemeinsam eine Kultur auf, in der "
            "Arbeit kein Zwang ist und alle an einem Strang ziehen. Drei Kernbereiche: "
            "Feedbackkultur, Mitarbeitende verstehen und erfahren, was sie wirklich wollen, "
            "und Mitarbeitende motivieren mit dem richtigen Führungsstil. Dazu gehört auch, "
            "Mission und Vision transparent zu gestalten und zu kommunizieren. Das Ergebnis: "
            "weniger Fluktuation, zufriedene Mitarbeitende — auch in Krisenzeiten."
        ),
        "title": "Schulung Feedbackkultur & Führung | Beraterium",
        "description": "Feedback, Motivation, Führungsstil, Mission & Vision — 1 Tag + Follow-up, ab 2.875 € netto, Team ab 9.395 € pauschal.",
        "audience": "Führungskräfte und Mitarbeitende",
        "fuer_wen_intro": "Diese Schulung passt, wenn einer dieser Punkte zutrifft:",
        "fuer_wen": [
            "Fluktuation und stille Kündigungen nehmen zu — und Sie erfahren die Gründe zu spät",
            "Feedback findet nur im Jahresgespräch statt (oder gar nicht)",
            "Sie wissen nicht sicher, was Ihre Mitarbeitenden wirklich wollen",
            "Mission und Vision stehen auf der Website, aber nicht im Alltag",
        ],
        "sessions": [
            ("Session 1 — Feedback & Verstehen (3 h)", [
                "Feedbackkultur aufbauen: Formate und Rituale in beide Richtungen",
                "Die Feedback-Falle: warum Feedback ohne Konsequenz Vertrauen zerstört",
                "Mitarbeitende verstehen: 1:1-Formate, Stay-Interviews, anonyme Kanäle",
                "Praxisteil: Feedback-Übungen in Echt-Situationen des Teams",
            ]),
            ("Session 2 — Motivation, Führungsstil, Mission & Vision (3 h)", [
                "Motivation verstehen: Autonomie, Kompetenzerleben, Sinn — was wirklich antreibt",
                "Den richtigen Führungsstil finden: situativ führen statt Einheitsstil",
                "Mission & Vision transparent machen: gemeinsam formulieren, in den Alltag übersetzen",
                "Praxisteil: Kultur-Fahrplan für das eigene Team entwerfen",
            ]),
            ("Follow-up — Review nach 4 Wochen (60 Min.)", [
                "Kultur-Fahrplan im Check: was funktioniert, wo hakt es, was wird nachjustiert",
            ]),
        ],
        "ergebnis": [
            "Weniger Fluktuation, zufriedenere Mitarbeitende, leichteres Führen",
            "Fachkräfte, die von allein kommen — und Mitarbeitende, die auch in Krisenzeiten bleiben",
            "Ein konkreter, gemeinsam entwickelter Kultur-Fahrplan statt Werte-Poster",
            "Mission und Vision, die jede:r im Team versteht und anwenden kann",
        ],
        "workload_iso": "PT7H",
        "faq": [
            ("Für wen ist die Schulung Feedbackkultur gedacht?", "Für alle — Führungskräfte und Mitarbeitende, idealerweise gemeinsam. Kultur entsteht nicht per Anweisung von oben: Der Kultur-Fahrplan wird in der Schulung von Führung und Team zusammen entwickelt."),
            ("Was kostet die Schulung?", "2.875 € für die erste Person, plus 725 € je weiterem. Ab 10 Personen gilt die gedeckelte Pauschale von 9.395 € — inklusive Follow-up-Call nach 4 Wochen. Alle Preise excl. VAT excl. VAT"),
            ("Was bedeutet „1+ Arbeitsumgebung“?", "Eine Arbeitsumgebung, in der Leistung und Einbringung kein Muss und Arbeit kein Zwang ist — weil Mitarbeitende und Führung in die gleiche Richtung arbeiten. Messbar wird das an weniger Fluktuation, leichterem Recruiting und einem Team, das auch in Krisenzeiten bleibt."),
            ("Wie hängt die Schulung mit den HR-Analysen zusammen?", "Ideal kombiniert: Die HR-Analyse per Fragebogen oder die Führungskräfte-Interviews liefern das ehrliche Ist-Bild, diese Schulung baut darauf die Kultur. Beides ist aber auch unabhängig voneinander buchbar."),
            ("Wie lange dauert die Schulung?", "Ein Tag mit zwei Sessions à 3 Stunden plus ein 60-minütiger Follow-up-Call rund 4 Wochen später — dort wird der Kultur-Fahrplan überprüft und nachjustiert."),
        ],
        "cta_h2": "Bauen Sie eine Arbeitsumgebung, in der alle an einem Strang ziehen",
        "cta_body": "Im freeen Erstgespräch klären wir Ausgangslage, Teamgröße und Termin — unverbindlich, in 30 Minuten.",
    },
    {
        "nr": "SCH-06",
        "slug": "cultural-management",
        "tag": "SCHULUNG · INTERNATIONALE TEAMS & PROJEKTE",
        "h1": "Schulung zum Kulturellen Management",
        "lead": (
            "Eine umfangreiche Schulung, wie Sie internationale Teams und internationale "
            "Projekte — Joint Ventures, Gründung von Tochtergesellschaften und Ähnliches — "
            "erfolgreich managen, mit echtem Verständnis der anderen Kultur. Besonders wichtig "
            "auch, wenn Sie Mitarbeitende aus anderen Kulturen einstellen. Basierend auf Meyer, "
            "Hofstede und Schwartz, mit First-Hand-Erfahrung aus interkulturellen Teams und "
            "Businesses: von DE und EU über Russland, USA und Südamerika bis Afrika, Indien "
            "und Pakistan."
        ),
        "title": "Schulung Interkulturelles Management | Beraterium",
        "description": "Intensivformat: Interkulturelles Management nach Meyer, Hofstede & Schwartz — internationale Teams, Joint Ventures — 1,5–2 Tage, ab 3.475 € netto, Team 9.875 € pauschal.",
        "audience": "Führungskräfte, Projektleitungen und internationale Teams",
        "fuer_wen_intro": "Diese Schulung passt, wenn einer dieser Punkte zutrifft:",
        "fuer_wen": [
            "Sie führen oder planen ein internationales Team, Joint Venture oder eine Tochtergesellschaft",
            "Sie stellen Mitarbeitende aus anderen Kulturen ein und wollen Onboarding und Führung kultursensibel gestalten",
            "Verhandlungen oder Projekte mit internationalen Partnern laufen zäh — und Sie vermuten kulturelle Gründe",
            "Sie expandieren in einen neuen Kulturraum und wollen die teuersten Missverständnisse vermeiden",
        ],
        "sessions": [
            ("Session 1 — Die Landkarte: Kulturdimensionen (3 h)", [
                "Hofstede: Machtdistanz, Individualismus, Unsicherheitsvermeidung, Langzeitorientierung",
                "Erin Meyer (Culture Map): Kommunikation, Kritik, Führen, Entscheiden, Vertrauen, Zeit",
                "Schwartz: der Werte-Kreis und Motivation in verschiedenen Kulturen",
                "Grenzen der Modelle: Landkarte statt Schublade",
            ]),
            ("Session 2 — Regionen-Praxis: First-Hand-Erfahrung (3 h)", [
                "DE/EU intern, Russland & Osteuropa, USA, Südamerika, Afrika, Indien & Pakistan",
                "Je Region: Kommunikationsstil, Hierarchie- und Zeitverständnis, Verhandlungslogik",
                "Typische Missverständnisse aus realen Projekten — und wie man sie auflöst",
            ]),
            ("Session 3 — Internationale Teams führen (3 h)", [
                "Interkulturell einstellen und integrieren: Interviews lesen, Onboarding kultursensibel gestalten",
                "Gemischte Teams managen: Meetings, Feedback und Entscheidungen für alle Kulturen wirksam",
                "Remote & Zeitzonen: Kommunikationsregeln, die kulturübergreifend funktionieren",
            ]),
            ("Session 4 — Internationale Projekte & Strukturen (3 h)", [
                "Joint Ventures & Tochtergesellschaften: kulturelle Due Diligence, tragfähige Governance",
                "Verhandeln über Kulturen hinweg: Tempo, Beziehungsaufbau, Gesichtwahrung",
                "Praxisteil: Kultur-Risiko-Analyse für das eigene internationale Vorhaben",
            ]),
        ],
        "ergebnis": [
            "Sicherheit mit internationalen Partnern, Teams und Neueinstellungen — fundiert statt anekdotisch",
            "Konkrete Playbooks je Region für Kommunikation, Führung und Verhandlung",
            "Kulturelle Risiken früh erkennen — bevor sie Joint Venture oder Schlüsselkraft kosten",
            "Eine begonnene Kultur-Risiko-Analyse für das eigene internationale Vorhaben",
        ],
        "workload_iso": "PT12H",
        "faq": [
            ("Für wen ist die Schulung zum Kulturellen Management gedacht?", "Für Führungskräfte, Projektleitungen und Teams mit internationalem Bezug — vom internationalen Team über Joint Ventures und Tochtergründungen bis zur Einstellung von Mitarbeitenden aus anderen Kulturen."),
            ("Was kostet die Schulung?", "3.475 € für die erste Person, plus 875 € je weiterem. Ab 8 Personen gilt die gedeckelte Pauschale von 9.875 €. Alle Preise excl. VAT excl. VAT"),
            ("Auf welchen Modellen basiert die Schulung?", "Auf den drei etablierten Kulturmodellen: Erin Meyers Culture Map, Hofstedes Kulturdimensionen und der Werte-Theorie von Schwartz — kombiniert mit First-Hand-Erfahrung aus realen interkulturellen Teams und Projekten von DE/EU über Russland, USA und Südamerika bis Afrika, Indien und Pakistan."),
            ("Welche Regionen deckt die Schulung ab?", "Deutschland/EU (auch die unterschätzten internen Unterschiede), Russland und Osteuropa, USA, Südamerika, Afrika sowie Indien und Pakistan. Auf Wunsch legen wir den Schwerpunkt auf die Regionen, mit denen Sie konkret arbeiten."),
            ("Wie lange dauert die Schulung?", "1,5 bis 2 Tage mit vier Sessions à 3 Stunden — inhouse oder online. Im Praxisteil erstellen die Teilnehmenden eine Kultur-Risiko-Analyse für ihr eigenes internationales Vorhaben."),
        ],
        "cta_h2": "Managen Sie internationale Teams mit Kulturverständnis",
        "cta_body": "Im freeen Erstgespräch klären wir Regionen-Schwerpunkt, Teamgröße und Termin — unverbindlich, in 30 Minuten.",
    },
]
