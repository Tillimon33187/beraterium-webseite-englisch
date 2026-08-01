"""Zentrale, normalisierte Preisquelle für die Seite /pricing/.

Einzige Quelle für sichtbare Price tablen, Offer/OfferCatalog-JSON-LD und
den Preis-Abschnitt in llms.txt. Normalisiert aus dem Angebotskatalog
`Angebote/Nagebot mit PREISEN .xlsx` (Sheets: RA / WS / ZUS / HR).

Preis-Modelle pro Angebot (genau eines):
- price:      Festpreis in EUR (0 = free)
- price_from: "ab"-Preis in EUR, mit optionalem unit ("per person" etc.);
              Staffel/Zusammensetzung als Klartext in price_detail
- price_base: Basispreis in EUR (1 Teilnehmer) + price_add je weiterem
              Teilnehmer + price_team (gedeckelte Team-Pauschale) ab
              team_from Personen; Staffel als Klartext in price_detail
Jedes Angebot hat details_html: eine ausklappbare Detail-Sektion auf
/pricing/ (Lead-Absatz + Bullet-Liste), normalisiert aus den Spalten
"Inhalt & Leistung"/"Resultate & Mehrwert" der xlsx-Sheets bzw. aus
Angebote/Beraterium_Angebote_UEBERSICHT.md (HR). Training (SCH-*) haben
zusätzlich slug (Unterseite /training/<slug>/) mit Link im Detail-Teaser;
Quelle der Schulungsinhalte: Angebote/training/*.md
Alle Preise excl. VAT excl. VAT
"""
from __future__ import annotations

from typing import Any


PRICE_CATEGORIES: list[dict[str, Any]] = [
    {
        "id": "analyse",
        "title": "Risk analysis & strategy",
        "tag": "ANALYSIS PACKAGES",
        "lede": "Festpreis-Pakete von der ersten Analyse bis zur begleiteten Umsetzung — das Kernpaket Risiko-Analyse 360° bündelt Analyse, Strategie und Budget in einem Festpreis.",
        "offers": [
            {
                "nr": "RA-01",
                "name": "Risiko-Analyse 360°",
                "desc": "Komplettpaket: Risiko-Beratung (Analyse), Strategie-Sitzung und Budgetplanung in einem Bundle — das Kernpaket für KMU mit Festpreis und doppelter Garantie.",
                "price": 3475,
                "price_detail": "Einzeln 5.150 € (1.725 + 2.175 + 1.250 €) · als Bundle 3.475 €",
                "duration": "3 Workshops + 3 Reports + Nachbereitungsgespräche",
                "details_html": (
                    "<p>Die Kombination aller drei Analyse-Bausteine — Analyse, Strategie und Budget — in einem durchgehenden Prozess mit Ihrem Team. Das Bundle ist günstiger als die Einzelbuchung und der empfohlene Einstieg für KMU.</p><ul><li>Analyse-Workshop: die Top 5–10 Risiken identifizieren, in Euro bewerten und nach Eintrittswahrscheinlichkeit einordnen</li><li>Strategie-Workshop: für die wichtigsten Risiken konkrete, umsetzbare Maßnahmen entwickeln — mit Umsetzungsplan</li><li>Budget-Workshop: eigene Ressourcen vs. externe Dienstleister abwägen, orientiert am Schaden aus der Analyse</li><li>Jede Phase endet mit einem Report und einem Nachbereitungsgespräch mit der Geschäftsführung</li></ul>"
                ),
            },
            {
                "nr": "RA-02",
                "name": "Risiko-Beratung (nur Analyse)",
                "desc": "Analyse-Phase: Top 5–10 Risiken identifizieren, in Euro bewerten und priorisieren — mit Report und Nachbereitungsgespräch.",
                "price": 1725,
                "duration": "1 Workshop (ca. 2–3 h) + Report + Nachbereitungsgespräch",
                "details_html": (
                    "<p>Ein Team-Workshop (2–3 Stunden) mit Ihrer Geschäftsführung und ausgewählten Mitarbeitenden, moderiert von uns. Ziel: aus Bauchgefühl wird eine priorisierte, in Euro bewertete Liste.</p><ul><li>Bewertung jedes Risikos nach Schadenshöhe in Euro und Eintrittswahrscheinlichkeit</li><li>Top 5–10 Risiken benannt und priorisiert — Basis für Versicherungs- oder Beiratsgespräche</li><li>Ergebnis als Report dokumentiert, inklusive Nachbereitungsgespräch zur Einordnung</li><li>Ideal, wenn Sie zunächst nur Klarheit über die Risikolage wollen, ohne direkt in die Maßnahmenplanung zu gehen</li></ul>"
                ),
            },
            {
                "nr": "RA-03",
                "name": "Risiko-Strategie-Sitzung mit Beratung",
                "desc": "Auf Basis der Analyse: gezielt Maßnahmen für die wichtigsten 5–10 Risiken entwickeln — mit Umsetzungsplan und Report.",
                "price": 2175,
                "duration": "1 Workshop (ca. 2–5 h) + Report",
                "details_html": (
                    "<p>Aufbauend auf einer vorherigen Analyse entwickeln wir gemeinsam mit Ihrem Team konkrete Maßnahmen gegen die wichtigsten Risiken — nicht nur Ideen, sondern einen Umsetzungsplan.</p><ul><li>Für jedes der Top-5–10-Risiken mindestens eine bewertete Maßnahme (Wirkung, Wirtschaftlichkeit, Umsetzbarkeit)</li><li>Priorisierter Umsetzungsfahrplan mit Verantwortlichkeiten und Timeline</li><li>Report als Strategiepapier — Grundlage für die anschließende Budgetplanung</li><li>Setzt eine vorherige Risikoanalyse voraus (z. B. Risiko-Beratung/Analyse oder Ihre eigene)</li></ul>"
                ),
            },
            {
                "nr": "RA-04",
                "name": "Budgetplanung (Risikokosten)",
                "desc": "Nach vorheriger Analyse: Budget für Risikomaßnahmen planen — eigene Ressourcen vs. externe Dienstleister, orientiert am Schaden aus der Analyse. Inkl. Angebotsvergleich.",
                "price": 1250,
                "duration": "1 Workshop (ca. 2 h) + Auswertung mit Angebotsvergleich",
                "details_html": (
                    "<p>Nach der Analyse steht fest, was ein Risiko im Schadensfall kostet — jetzt planen wir gemeinsam, wie viel Budget in welche Gegenmaßnahme fließt.</p><ul><li>Abgleich: eigene Ressourcen intern lösen oder externe Dienstleister beauftragen</li><li>Budgethöhe orientiert sich am Schaden aus der vorherigen Analyse — keine Über- oder Unterinvestition</li><li>Angebotsvergleich für externe Optionen inklusive</li><li>Ergebnis: ein Budgetplan mit Kosten-Nutzen-Einordnung je Maßnahme</li></ul>"
                ),
            },
            {
                "nr": "RA-06",
                "name": "Externe Risiko- & Business-Potential-Analyse",
                "desc": "GF-Interview plus Analyse externer Einflussfaktoren (Markt, Wettbewerb, Regulierung) — mit Chancen-Report.",
                "price": 1975,
                "duration": "1–1,5 h Interview + 2–3 Tage Analyse",
                "details_html": (
                    "<p>Ein Interview mit der Geschäftsführung (60–90 Minuten) plus eine strukturierte Analyse externer Einflussfaktoren — Markt, Wettbewerb, Regulierung — mit etablierten Werkzeugen (u. a. PESTLE, SWOT, VRIO, Porters Five Forces).</p><ul><li>Vergleich: aktuelle Position vs. ungenutztes Zukunftspotenzial</li><li>Chancen-Report mit priorisierten Wachstumsoptionen</li><li>Besonders wertvoll vor Expansion, Investorenrunden oder einem Generationenwechsel</li><li>Ergänzt die interne Risikoanalyse um den Blick von außen</li></ul>"
                ),
            },
            {
                "nr": "RA-05",
                "name": "Integration von Maßnahmen",
                "desc": "Intensive Team-Begleitung über mehrere Wochen, bis Maßnahmen im Alltag greifen — mit Schulung und Monitoring.",
                "price": 4675,
                "duration": "8–16 Wochen, 2–3 h/Woche",
                "details_html": (
                    "<p>Die intensivste Begleitung: Über mehrere Wochen arbeiten wir direkt mit Ihrem Team, bis die vereinbarten Maßnahmen wirklich im Alltag ankommen — nicht nur auf Papier.</p><ul><li>Regelmäßige Vor-Ort-Termine (2–3 h/Woche) über 8–16 Wochen</li><li>Schulung der Mitarbeitenden in den neuen Prozessen und Verantwortlichkeiten</li><li>Laufendes Monitoring des Umsetzungsstands mit Feinjustierung</li><li>Ziel: Ihr Team erkennt und behandelt Risiken am Ende eigenständig</li></ul>"
                ),
            },
            {
                "nr": "RA-07",
                "name": "Gesamtpaket L",
                "desc": "Risiko-Analyse 360° + Maßnahmen-Integration als Paket (Einzeln 8.150 €, als Paket 7.825 €).",
                "price": 7825,
                "duration": "24–32 Wochen Begleitung",
                "details_html": (
                    "<p>Risiko-Analyse 360° (Analyse, Strategie, Budget) plus die Maßnahmen-Integration in einem durchgehenden Begleitungspaket — von der ersten Bestandsaufnahme bis zur gelebten Umsetzung.</p><ul><li>Einzeln würden die enthaltenen Module 8.150 € kosten — im Paket sind es 7.825 €</li><li>24–32 Wochen Begleitung: 1 Woche Analyse, 2 Wochen Strategie, 1 Woche Budget, 16–20 Wochen Integration</li><li>Ein Ansprechpartner für den gesamten Prozess statt mehrerer Einzelbeauftragungen</li><li>Festpreis für den gesamten Prozess — abgesichert durch die doppelte Garantie</li></ul>"
                ),
            },
            {
                "nr": "RA-08",
                "name": "Gesamtpaket XL",
                "desc": "Gesamtpaket L plus externe Markt- und Potential-Analyse — die komplette Risiko-Transformation (Einzeln 9.800 €, als Paket 9.675 €).",
                "price": 9675,
                "duration": "28–36 Wochen Begleitung",
                "details_html": (
                    "<p>Das Gesamtpaket L, erweitert um die externe Markt- und Potential-Analyse — die komplette Risiko- und Strategie-Transformation, intern und extern.</p><ul><li>Einzeln würden die enthaltenen Module 9.800 € kosten — im Paket sind es 9.675 €</li><li>28–36 Wochen Begleitung von der Analyse bis zur gelebten Umsetzung, inklusive Markt-Perspektive</li><li>Ideal vor einer Finanzierungsrunde oder einem Generationenwechsel mit Marktveränderungen</li><li>Festpreis für den gesamten Prozess — abgesichert durch die doppelte Garantie</li></ul>"
                ),
            },
        ],
    },
    {
        "id": "workshops",
        "title": "Workshops",
        "tag": "TEAM WORKSHOPS",
        "lede": "Preis per person mit Mengenstaffel — je größer die Gruppe, desto günstiger pro Kopf. Alle Workshops in Präsenz.",
        "offers": [
            {
                "nr": "WS-01",
                "name": "Risiken allgemein (60 Min.)",
                "desc": "Einführung ins Risikomanagement: Was ist ein Risiko, warum betrifft es jedes Unternehmen — Team-Sensibilisierung.",
                "price_from": 57,
                "unit": "per person",
                "price_detail": "Einzeln 127 € · ab 4 Personen 118 € · ab 8 Personen 57 € per person",
                "duration": "60 Minuten",
                "details_html": (
                    "<p>Der niedrigschwellige Einstieg: Was ist überhaupt ein Risiko, warum betrifft es jedes Unternehmen — mit praktischen Beispielen statt Theorie.</p><ul><li>Team versteht: Risikomanagement muss nicht komplex sein</li><li>Erste Sensibilisierung als Grundlage für vertiefende Workshops (z. B. „Risiken sichtbar machen“)</li><li>Ideal vor oder direkt nach einer Analyse, um das ganze Team mitzunehmen</li></ul>"
                ),
            },
            {
                "nr": "WS-02",
                "name": "Risiken sichtbar machen (120 Min.)",
                "desc": "Wie erkennen Mitarbeitende und Führungskräfte Risiken im Alltag — und wie melden sie sie früh?",
                "price_from": 97,
                "unit": "per person",
                "price_detail": "Einzeln 185 € · ab 4 Personen 147 € · ab 8 Personen 97 € per person",
                "duration": "120 Minuten",
                "details_html": (
                    "<p>Wie erkennen Mitarbeitende und Führungskräfte Risiken im Alltag — und wie melden sie sie, bevor daraus ein Problem wird? Mit Szenarien, Rollenspielen und Fallbeispielen.</p><ul><li>Konkrete Handlungsschritte, wenn jemand ein Risiko bemerkt</li><li>Ziel: Probleme werden früh gemeldet statt spät entdeckt</li><li>Entlastet die Geschäftsführung, weil das Team proaktiv meldet statt zu schweigen</li></ul>"
                ),
            },
            {
                "nr": "WS-03",
                "name": "Risiko-Grundlagen, wiederholend (60 Min.)",
                "desc": "Vertiefung im Unternehmenskontext: das Team lernt, die eigenen Top-Risiken zu benennen und einzuordnen. Max. 20 Personen.",
                "price_from": 117,
                "unit": "per person",
                "price_detail": "ab 117 € per person, nach Gruppengröße",
                "duration": "60 Minuten",
                "details_html": (
                    "<p>Vertiefung direkt im Unternehmenskontext, meist im Anschluss an eine Risikoanalyse: das Team lernt, die eigenen Top-Risiken zu benennen, einzuordnen und zu priorisieren.</p><ul><li>Strukturierte Kategorisierung: strategisch, operativ, finanziell, HR</li><li>Max. 20 Personen, damit wirklich jeder mitdiskutiert</li><li>Bindeglied zwischen Analyse und Umsetzung — das Team spricht danach dieselbe Sprache</li></ul>"
                ),
            },
            {
                "nr": "WS-04",
                "name": "Kulturelle Grundlage (180 Min.)",
                "desc": "Kultur-Workshop zu psychologischer Sicherheit: das Team traut sich, Probleme und Risiken offen anzusprechen.",
                "price_from": 112,
                "unit": "per person",
                "price_detail": "Einzeln 197 € · ab 4 Personen 162 € · ab 8 Personen 112 € per person",
                "duration": "180 Minuten",
                "details_html": (
                    "<p>Kein Workshop über Risiken, sondern über die Kultur, die Risikomanagement erst möglich macht: psychologische Sicherheit, damit sich niemand scheut, Probleme offen anzusprechen.</p><ul><li>Team entwickelt gemeinsam, was es braucht, um sich sicher zu fühlen</li><li>Verteilte Verantwortung statt einer Geschäftsführung, die allein alles trägt</li><li>Besonders wirksam bei schnell wachsenden Teams oder im Generationenwechsel</li></ul>"
                ),
            },
            {
                "nr": "WS-05",
                "name": "Globale Risiken & Entwicklungen (60 Min.)",
                "desc": "Für international agierende Unternehmen: aktuelle globale Risikolandschaft, Regulierung und Expansions-Märkte.",
                "price_from": 177,
                "unit": "per person",
                "price_detail": "Einzeln 347 € · ab 4 Personen 287 € · ab 8 Personen 177 € per person",
                "duration": "60 Minuten",
                "details_html": (
                    "<p>Für Unternehmen mit internationalem Geschäft: aktuelle globale Risikolandschaft, Marktvolatilität, Geopolitik und Regulierung (z. B. ESG, Green Deal) verständlich eingeordnet.</p><ul><li>Länderspezifische Einschätzung passend zu Ihren Expansionsplänen</li><li>Hilft, Investitionen in die richtigen Märkte statt in instabile zu priorisieren</li><li>Besonders relevant vor internationaler Expansion oder Export</li></ul>"
                ),
            },
            {
                "nr": "WS-06",
                "name": "Risiken in der Expansionsphase (60 Min.)",
                "desc": "Speziell für Startups und schnell wachsende Unternehmen: welche Risiken jede Wachstumsphase mitbringt.",
                "price_from": 113,
                "unit": "per person",
                "price_detail": "Einzeln 197 € · ab 4 Personen 152 € · ab 8 Personen 113 € per person",
                "duration": "60 Minuten",
                "details_html": (
                    "<p>Speziell für Startups und schnell wachsende Unternehmen: welche Risiken jede Wachstumsphase typischerweise mitbringt — von 0–10 über 10–50 bis 50–200 Mitarbeitende.</p><ul><li>Fallbeispiele, wie andere Unternehmen diese Phasen gemeistert haben</li><li>Vorbereitung statt Überraschung: Kulturbrüche, erste Führungsprobleme, Burnout-Wellen vermeiden</li><li>Ideal kurz vor oder während einer Wachstumsphase</li></ul>"
                ),
            },
            {
                "nr": "WS-07",
                "name": "Themen-Workshop mit Experten (120 Min.)",
                "desc": "Tiefenthema zu einem spezifischen Risikobereich (z. B. IT-Sicherheit, Digitalisierung) mit Fachexperte. Max. 20 Personen.",
                "price_from": 117,
                "unit": "per person",
                "price_detail": "ab 117 € per person, abhängig von Thema und Experte",
                "duration": "120 Minuten",
                "details_html": (
                    "<p>Ein Tiefenthema zu einem spezifischen Risikobereich — etwa IT-Sicherheit, Datenschutz, Compliance oder Lieferketten — gemeinsam mit einer externen Fachperson.</p><ul><li>Lösungsorientiert statt nur theoretisch: konkrete Maßnahmen für genau diesen Bereich</li><li>Max. 20 Personen, Preis abhängig von Thema und Expertise</li><li>Macht Ihr Team unabhängiger von externen Beratern im Alltag</li></ul>"
                ),
            },
        ],
    },
    {
        "id": "schulungen",
        "title": "Training",
        "tag": "MULTI-DAY TRAINING",
        "lede": "Vertiefende Trainings über einen oder mehrere Tage — Einzelschulungen im Intensivformat (1:1 oder Kleinstgruppe, deutlich tiefer als in der Kombi), Kombi-Ausbildung zum Risikoexperten ab 9.875 €. Basispreis für die erste Person, Aufpreis je weiterem Teilnehmer, gedeckelte Team-Pauschale ab Gruppengröße. Details je Schulung ausklappen oder die Schulungsseite öffnen.",
        "offers": [
            {
                "nr": "SCH-07",
                "name": "Ausbildung zum Risikoexperten (Kombi-Schulung)",
                "desc": "Die komplette Ausbildung: Risk-Awareness-Kultur, risikobewusste Führung und praktisches Risikomanagement in einem Durchgang — befähigt, unsere Methode im eigenen Unternehmen umzusetzen.",
                "price_base": 9875,
                "price_add": 4440,
                "price_team": 22875,
                "team_from": 4,
                "team_max": 4,
                "price_detail": "9.875 € (1 Person) · 14.315 € (2 Personen) · +4.440 € je weiterer · max. 4 Personen 22.875 € pauschal · inkl. Gefahrenkatalog & Zertifikat",
                "duration": "3 Tage intensiv (ca. 24 h) + Transfer & Zertifikat",
                "slug": "risk-expert",
                "details_html": (
                    "<p>Die Kombi-Schulung vereint unsere drei Risikomanagement-Training zu einer vollständigen "
                    "Ausbildung: Risk-Awareness-Kultur, \u201eDer risikobewusste Manager\u201c und \u201eRisikomanagement "
                    "praktisch umsetzen\u201c. Für Manager und Mitarbeitende, die Risikomanagement im Unternehmen "
                    "verantworten und unsere Methode selbst umsetzen sollen.</p>"
                    "<p><strong>Investition in interne Risikokompetenz:</strong> Die Ausbildung liegt bewusst auf Augenh\u00f6he mit unserer begleiteten Risiko-Analyse 360\u00b0 (3.475 \u20ac) bzw. dem Gesamtpaket XL (9.675 \u20ac) \u2014 mit dem Unterschied, dass Sie die Methode dauerhaft im Haus aufbauen, statt Risikomanagement dauerhaft einzukaufen.</p>"
                    "<ul>"
                    "<li>Modul 1: Fehler- und Risk-Awareness-Kultur nach Luftfahrt-Vorbild aufbauen</li>"
                    "<li>Modul 2: als Führungskraft Risiken kalkuliert eingehen und das Unternehmen von außen sehen</li>"
                    "<li>Modul 3: Risikoanalyse selbst durchführen — Matrix, Gefahrenkatalog (inklusive), Euro-Bewertung, Maßnahmen</li>"
                    "<li>Abschluss: Zertifikat als Risikoexperte:in und Transferplan für das eigene Unternehmen</li>"
                    "</ul>"
                ),
            },
            {
                "nr": "SCH-01",
                "name": "Risikomanagement: Der Weg zur Risk-Awareness-Kultur",
                "desc": "Nach Luftfahrt-Vorbild eine Aus-Fehlern-lernen-Kultur aufbauen: weg vom Fingerzeigen, hin zum gemeinsamen Verbessern — für Führung und Team.",
                "price_base": 3975,
                "price_add": 995,
                "price_team": 11475,
                "team_from": 10,
                "price_detail": "Intensivformat: 3.975 € (1 Person) · +995 € je weiterer · ab 10 Personen 11.475 € pauschal · 1:1 oder Kleinstgruppe, deutlich tiefer als in der Kombi-Ausbildung",
                "duration": "1 Tag (2 Sessions à 3 h) + Transfer-Paket",
                "slug": "risk-awareness-culture",
                "details_html": (
                    "<p><strong>Intensivformat (1:1 oder Kleinstgruppe):</strong> Wesentlich detaillierter und persönlicher als das entsprechende Modul in der Kombi-Ausbildung zum Risikoexperten — ideal, wenn Sie nur dieses Thema vertiefen wollen.</p>"
                    "<p>Wie bereite ich ein Team so vor, dass Risiken kein No-Go mehr sind, sondern zum Lernprozess gehören? "
                    "Am Beispiel Luftfahrt wird eine Kultur aufgebaut, in der offen zugegebene Fehler gefeiert statt bestraft werden.</p>"
                    "<ul>"
                    "<li>Just Culture nach Luftfahrt-Vorbild: Meldewege, Debriefings, Fehler-Rituale</li>"
                    "<li>Führungsstruktur, in der aus Fehlern gelernt wird — statt Schuldige zu suchen</li>"
                    "<li>Team-Aspekt: alle bringen sich ein, statt Fehler unter den Tisch zu kehren</li>"
                    "<li>Praxis-Simulation: Debriefing eines echten (anonymisierten) Fehlerfalls</li>"
                    "</ul>"
                ),
            },
            {
                "nr": "SCH-02",
                "name": "Der risikobewusste Manager",
                "desc": "Speziell für Führungskräfte: Angst vor Fehlern und Risiken abbauen, Risiken kalkuliert eingehen — und die eigene Firma wieder neutral von außen sehen.",
                "price_base": 3475,
                "price_add": 875,
                "price_team": 9875,
                "team_from": 8,
                "price_detail": "Intensivformat: 3.475 € (1 Führungskraft) · +875 € je weiterer · ab 8 Personen 9.875 € pauschal · geschützter 1:1-Rahmen, deutlich tiefer als in der Kombi-Ausbildung",
                "duration": "1 Kompakt-Tag (6 h)",
                "slug": "risk-aware-manager",
                "details_html": (
                    "<p><strong>Intensivformat für Führungskräfte (1:1 oder Kleinstgruppe):</strong> Geschützter Rahmen ohne eigene Mitarbeitende — deutlich persönlicher und tiefer als Modul 2 in der Kombi-Ausbildung.</p>"
                    "<p>Nur für Manager:innen: Fehler als Chance zum Wachstum sehen, Risiken nicht fürchten, sondern als Chance "
                    "begreifen und kalkuliert eingehen — und das eigene Unternehmen mit der neutralen Außenbrille betrachten.</p>"
                    "<ul>"
                    "<li>Fehlerangst verstehen und ablegen — Vorbildwirkung für das Team</li>"
                    "<li>Entscheidungs-Frameworks für kalkulierte Risiken (Worst Case, Reversibilität)</li>"
                    "<li>Betriebsblindheit lösen: Pre-Mortem, Konkurrenz-Perspektive, Außensicht-Walkthrough</li>"
                    "<li>Praxisübung am eigenen Kernprozess: Top-3-Risiken und -Chancen</li>"
                    "</ul>"
                ),
            },
            {
                "nr": "SCH-03",
                "name": "Risikomanagement praktisch umsetzen",
                "desc": "Das Beraterium-System selbst anwenden lernen: Risikoanalyse mit dem Team, Matrix, Gefahrenkatalog (inklusive), Euro-Bewertung und umsetzbare Maßnahmen.",
                "price_base": 4975,
                "price_add": 1175,
                "price_team": 14375,
                "team_from": 10,
                "price_detail": "Intensivformat: 4.975 € (1 Person) · +1.175 € je weiterer · ab 10 Personen 14.375 € pauschal · inkl. Gefahrenkatalog · 1:1 oder Kleinstgruppe, deutlich tiefer als in der Kombi-Ausbildung",
                "duration": "1,5 Tage (3 Sessions à 4 h)",
                "slug": "practical-risk-management",
                "details_html": (
                    "<p><strong>Intensivformat (1:1 oder Kleinstgruppe):</strong> Volle Tiefe bei Matrix, Euro-Bewertung und Praxis an Ihrem echten Bereich — deutlich umfangreicher als Modul 3 in der Kombi-Ausbildung.</p>"
                    "<p>Schritt für Schritt unser System der Risikobewertung lernen — für Mitarbeitende, Führungskräfte, "
                    "Risikomanager aus Unternehmen und Unternehmer, die Risikomanagement intern lösen wollen. So wird es "
                    "im Großkonzern gemacht, heruntergebrochen auf KMU-taugliche Schritte.</p>"
                    "<ul>"
                    "<li>Risikoanalyse mit dem Team durchführen: Erhebung und Moderation</li>"
                    "<li>Risiken mit der Matrix bestimmen und typische Bewertungsfehler vermeiden</li>"
                    "<li>Mit dem 3-Ebenen-Gefahrenkatalog arbeiten — Teilnehmende erhalten den vollständigen Katalog</li>"
                    "<li>Risiken in Euro bewerten und daraus verständliche, umsetzbare Maßnahmen ableiten</li>"
                    "</ul>"
                ),
            },
            {
                "nr": "SCH-04",
                "name": "Schulung zu Innovationsmanagement",
                "desc": "Durch und durch innovativ werden und bleiben: Team, Atmosphäre, Management und Innovationskultur — Business, Innovation und R&D unter einem Hut.",
                "price_base": 2995,
                "price_add": 745,
                "price_team": 9695,
                "team_from": 10,
                "price_detail": "2.995 € (1 Person) · +745 € je weiterer · ab 10 Personen 9.695 € pauschal · Kleingruppe, Praxis am eigenen Thema",
                "duration": "1 Tag (2 Sessions à 3,5 h) + Transfer-Paket",
                "slug": "innovation-management",
                "details_html": (
                    "<p><strong>Kleingruppen-Schulung:</strong> Innovationskultur und Pipeline am eigenen Unternehmen — unter üblichen Inhouse-Preisen, mit Transfer-Paket.</p>"
                    "<p>Nicht einmal ein Produkt auf den Markt bringen und in Vergessenheit geraten — sondern über Jahre "
                    "innovativ bleiben und sich auch gegen große Konkurrenten durchsetzen.</p>"
                    "<ul>"
                    "<li>Innovationskultur: Team, Atmosphäre und Management der Innovation</li>"
                    "<li>Leichtgewichtige Innovations-Pipeline: Idee → Validierung → Pilot → Skalierung</li>"
                    "<li>Business, Innovation und R&amp;D unter einem Hut: Ressourcen-Split und Kennzahlen</li>"
                    "<li>Praxisteil: Mini-Pipeline für ein eigenes, reales Innovationsthema</li>"
                    "</ul>"
                ),
            },
            {
                "nr": "SCH-05",
                "name": "Feedbackkultur & eine 1+ Arbeitsumgebung",
                "desc": "Mit dem Team eine Kultur aufbauen, in der alle an einem Strang ziehen: Feedbackkultur, Mitarbeitende verstehen, motivieren — plus Mission & Vision transparent machen.",
                "price_base": 2875,
                "price_add": 725,
                "price_team": 9395,
                "team_from": 10,
                "price_detail": "2.875 € (1 Person) · +725 € je weiterer · ab 10 Personen 9.395 € pauschal · inkl. Follow-up nach 4 Wochen",
                "duration": "1 Tag (2 Sessions à 3 h) + Follow-up",
                "slug": "feedback-culture",
                "details_html": (
                    "<p><strong>Kleingruppen-Schulung:</strong> Feedbackkultur und Führungsstil im Team-Rahmen — inklusive Follow-up nach 4 Wochen.</p>"
                    "<p>Eine Arbeitsumgebung, in der Mitarbeitende und Führung in die gleiche Richtung arbeiten. "
                    "Drei Kernbereiche: Feedbackkultur, Mitarbeitende verstehen (was wollen sie wirklich?), "
                    "motivieren und den richtigen Führungsstil finden.</p>"
                    "<ul>"
                    "<li>Feedback-Formate und -Rituale, die Vertrauen aufbauen statt zerstören</li>"
                    "<li>Mission &amp; Vision gemeinsam transparent gestalten und kommunizieren</li>"
                    "<li>Ergebnis: weniger Fluktuation, Fachkräfte kommen von allein, Team bleibt auch in Krisenzeiten</li>"
                    "<li>Follow-up-Call nach 4 Wochen: Kultur-Fahrplan nachjustieren</li>"
                    "</ul>"
                ),
            },
            {
                "nr": "SCH-06",
                "name": "Schulung zum Kulturellen Management",
                "desc": "Internationale Teams und Projekte (Joint Ventures, Tochtergesellschaften) erfolgreich managen — basierend auf Meyer, Hofstede und Schwartz, mit First-Hand-Erfahrung.",
                "price_base": 3475,
                "price_add": 875,
                "price_team": 9875,
                "team_from": 8,
                "price_detail": "3.475 € (1 Person) · +875 € je weiterer · ab 8 Personen 9.875 € pauschal · Kleingruppe, internationale Praxis",
                "duration": "1,5–2 Tage (4 Sessions à 3 h)",
                "slug": "cultural-management",
                "details_html": (
                    "<p><strong>Kleingruppen-Schulung:</strong> Interkulturelles Management mit First-Hand-Erfahrung — Praxis für Ihr internationales Vorhaben.</p>"
                    "<p>Umfangreiche Schulung für internationale Teams, Joint Ventures, Tochtergründungen — und für alle, "
                    "die Mitarbeitende aus anderen Kulturen einstellen und führen. First-Hand-Erfahrung von DE/EU über "
                    "Russland, USA und Südamerika bis Afrika, Indien und Pakistan.</p>"
                    "<ul>"
                    "<li>Kulturdimensionen nach Meyer, Hofstede und Schwartz — praktisch angewendet</li>"
                    "<li>Regionen-Praxis: Kommunikation, Hierarchie, Verhandlung je Kulturraum</li>"
                    "<li>Interkulturell einstellen, onboarden und führen</li>"
                    "<li>Praxisteil: Kultur-Risiko-Analyse für das eigene internationale Vorhaben</li>"
                    "</ul>"
                ),
            },
        ],
    },
    {
        "id": "einstieg",
        "title": "Entry & compact checks",
        "tag": "ENTRY & ADD-ONS",
        "lede": "Vom freeen Erst-Check bis zur kompakten Kurzanalyse — der niedrigschwellige Einstieg ins Risikomanagement.",
        "offers": [
            {
                "nr": "ZUS-07",
                "name": "Risiko-Check für Startups",
                "desc": "1-Stunden-Check-Session für Neugründer (bis 10.000 € Umsatz): erste Orientierung plus konkrete Quick-Wins.",
                "price": 0,
                "duration": "60 Minuten",
                "details_html": (
                    "<p>Eine freee Stunde für Neugründer mit bis zu 10.000 € Umsatz: ein erster Blick von außen auf Ihr junges Unternehmen.</p><ul><li>Identifikation von Schwachstellen, die das Wachstum bremsen könnten</li><li>Konkrete Quick-Wins, die Sie direkt umsetzen können</li><li>Der ideale erste Kontakt, bevor Sie sich für ein größeres Paket entscheiden</li></ul>"
                ),
            },
            {
                "nr": "ZUS-04",
                "name": "Kurzanalyse bei kleinen Fällen",
                "desc": "Schnelle Risikoanalyse im kleinen Maßstab — ideal für Pre-MVP-/MVP-Startups, z. B. in Acceleratoren.",
                "price_from": 47,
                "price_detail": "47 € (30 Min.) · 92 € (60 Min.)",
                "duration": "30 oder 60 Minuten",
                "details_html": (
                    "<p>Eine kompakte Risikoanalyse im kleinen Maßstab — ideal für Pre-MVP- und MVP-Startups, etwa im Rahmen eines Acceleratoren-Programms.</p><ul><li>Gleiches Verfahren wie die große Analyse, verdichtet auf 30 oder 60 Minuten</li><li>Kompakter Report mit den wichtigsten Risiken und Empfehlungen</li><li>Zeigt Investoren, dass Sie sich mit Risiken bereits auseinandergesetzt haben</li></ul>"
                ),
            },
            {
                "nr": "ZUS-03",
                "name": "Dein Risiko-Plan (Einzel-Sessions)",
                "desc": "Maßgeschneiderte Risiko-Strategie für Gründer, iterativ in Einzel-Sessions aufgebaut — du bestimmst Tempo und Budget.",
                "price_from": 92,
                "price_detail": "92 € (30 Min.) · 147 € (60 Min.) je Session",
                "duration": "30 oder 60 Minuten je Session",
                "details_html": (
                    "<p>Für Gründer, die ihre Risiko-Strategie iterativ und ohne festes Paket aufbauen wollen: Einzel-Sessions à 30 oder 60 Minuten, genau so viele wie nötig.</p><ul><li>Kein Abo, keine Mindestlaufzeit — Sie bestimmen Tempo und Budget</li><li>Maßgeschneidert auf Ihre konkrete Situation statt Standard-Template</li><li>Besonders geeignet für die frühe Gründungsphase mit begrenztem Budget</li></ul>"
                ),
            },
            {
                "nr": "ZUS-02",
                "name": "Kurzer Risiko-Check",
                "desc": "Quick-Check-Sitzung: Wo steht Ihr Unternehmen beim Risiko-Status, was sind die Top-3-Risiken, welche Sofort-Maßnahmen?",
                "price": 97,
                "duration": "30 Minuten",
                "details_html": (
                    "<p>Eine 30-minütige Schnelleinschätzung für alle, die wenig Zeit oder Budget haben, aber sofort wissen wollen, wo sie stehen.</p><ul><li>Grobe Einordnung des aktuellen Risiko-Status</li><li>Top-3-Risiken benannt plus Sofort-Impulse für morgen</li><li>Guter erster Schritt, um zu entscheiden, ob eine tiefere Analyse sinnvoll ist</li></ul>"
                ),
            },
            {
                "nr": "ZUS-05",
                "name": "Risikoanalyse-Vorbereitung für Startups",
                "desc": "Wie Risikoanalyse in der Early-Stage funktioniert: Gründer verstehen ihr Risk-Landscape und können selbst erkennen.",
                "price": 295,
                "duration": "Session + Auswertung",
                "details_html": (
                    "<p>Für Gründer, die verstehen wollen, wie Risikoanalyse in der Early-Stage überhaupt funktioniert — bevor sie selbst oder mit uns tiefer einsteigen.</p><ul><li>Typische Risikofelder für Ihre Branche eingeordnet: Team, Markt, Technik, Finanzierung</li><li>Sie lernen, Risiken künftig selbst zu erkennen statt nur einmalig aufgelistet zu bekommen</li><li>Gute Vorbereitung auf Investorengespräche und die nächste Wachstumsphase</li></ul>"
                ),
            },
            {
                "nr": "ZUS-06",
                "name": "Aktuelle Risiken (Krisen-Check)",
                "desc": "Snap-Check bei akuten Ereignissen (Marktumbruch, Personalausfall, Kundenverlust): klare Prioritäten statt Ad-hoc-Panik.",
                "price": 475,
                "duration": "Kompakt-Session + Prioritätenliste",
                "details_html": (
                    "<p>Ein Notfall-Coaching für akute Situationen — Marktumbruch, plötzlicher Personalausfall, Kundenverlust, Reputationskrise. Ziel: Ruhe statt Panik.</p><ul><li>Klare Prioritäten statt Ad-hoc-Entscheidungen im Chaos</li><li>Aktionsplan für die nächsten 48 Stunden und die kommende Woche</li><li>Kompakte Session, sofort verfügbar bei akutem Bedarf</li></ul>"
                ),
            },
            {
                "nr": "ZUS-01",
                "name": "Risiko-Plan-Analyse (Validierung)",
                "desc": "Sie haben selbst einen Risikoplan erarbeitet? Wir validieren ihn, identifizieren Lücken und Über-Engineering.",
                "price": 625,
                "duration": "Review + Feedback-Gespräch",
                "details_html": (
                    "<p>Sie haben bereits selbst einen Risikoplan erarbeitet? In zwei 60-minütigen Sitzungen prüfen wir ihn: Sind die Strategien realistisch? Wo gibt es Lücken, wo ist er überdimensioniert?</p><ul><li>Review durch erfahrene Berater statt kompletter Neuanalyse — schneller und günstiger</li><li>Ergebnis: ein schlankerer, umsetzbarerer Plan mit höherer Erfolgswahrscheinlichkeit</li><li>Ideal, wenn intern schon Vorarbeit geleistet wurde und nur der Blick von außen fehlt</li></ul>"
                ),
            },
        ],
    },
    {
        "id": "hr",
        "title": "HR, culture & leadership",
        "tag": "HR MODULES",
        "lede": "Stimmung, Führungsqualität und Kultur datenbasiert sichtbar machen — Pauschale plus Pro-Kopf-Staffel, Report optional.",
        "offers": [
            {
                "nr": "HR-01",
                "name": "HR-Analyse per Fragebogen",
                "desc": "Anonymer Kultur-Health-Check für alle Mitarbeitenden: Zufriedenheit, Kommunikation, Führung, Belastung — mit aggregierten Insights.",
                "price_from": 12,
                "unit": "per person",
                "price_detail": "Pauschale 127 € + per person: ab 10 MA 27 € · ab 25 MA 22 € · ab 50 MA 17 € · ab 100 MA 12 € · Report +547 €",
                "duration": "Befragung + Auswertung",
                "details_html": (
                    "<p>Ein anonymer Kultur-Health-Check für alle Mitarbeitenden: Zufriedenheit, Kommunikation, Führungsqualität, Zugehörigkeitsgefühl, Stressbelastung und Veränderungsbereitschaft.</p><ul><li>Vollständig anonyme Antworten, aggregierte Insights für die Geschäftsführung</li><li>Deckt früh Warnsignale auf — etwa Burnout-Tendenzen oder verdeckte Unzufriedenheit</li><li>Optionaler Report (+547 €) mit Trends und konkreten Handlungsimpulsen</li></ul>"
                ),
            },
            {
                "nr": "HR-02",
                "name": "Führungskräfte-Interviews",
                "desc": "Tiefe 1:1-Interviews (je 1 h) mit Ihren Führungskräften, transkribiert und in Mustern ausgewertet.",
                "price_from": 197,
                "unit": "pro Interview",
                "price_detail": "Pauschale 257 € + pro Interview: einzeln 227 € · ab 10 222 € · ab 25 212 € · ab 50 197 € · Report +1.525 €",
                "duration": "1 h je Interview + Auswertung",
                "details_html": (
                    "<p>Vertrauliche 1:1-Interviews (je 1 Stunde) mit Ihren Führungskräften — zu Teamdynamik, Herausforderungen, Führungsansatz und Zusammenarbeit auf FK-Ebene.</p><ul><li>Interviews werden transkribiert und auf gemeinsame Muster analysiert</li><li>Deckt Spannungen zwischen Führungskräften auf, die von außen unsichtbar bleiben</li><li>Optionaler Report (+1.525 €) mit Cluster-Analyse und Handlungsempfehlungen</li></ul>"
                ),
            },
            {
                "nr": "HR-03",
                "name": "Auswertung & Handlungsempfehlungen",
                "desc": "Aus Fragebogen- und Interview-Daten werden konkrete Maßnahmen mit Prioritäten, Reihenfolge und Timeline — als Strategiepapier.",
                "price": 2475,
                "duration": "Workshop + Strategiepapier",
                "details_html": (
                    "<p>Auf Basis der Fragebogen- und/oder Interview-Daten entwickeln wir gemeinsam mit der Geschäftsführung konkrete Maßnahmen — mit Priorität, Reihenfolge und Ressourcenbedarf.</p><ul><li>Ergebnis: ein Strategiepapier statt einer bloßen Datensammlung</li><li>Klare Timeline mit Verantwortlichkeiten je Maßnahme</li><li>Macht den ROI von HR-Investitionen sichtbar und nachvollziehbar</li></ul>"
                ),
            },
        ],
    },
]


def format_eur(value: int) -> str:
    """3475 -> '3.475 €'; 0 -> 'free'."""
    if value == 0:
        return "free"
    return f"{value:,.0f}".replace(",", ".") + " €"


def offer_price_text(offer: dict[str, Any]) -> str:
    """Kompakter Anzeige-Preis für Tabelle/llms.txt (Detail via price_detail)."""
    if "price" in offer:
        return format_eur(offer["price"])
    if "price_base" in offer:
        return f"ab {format_eur(offer['price_base'])}"
    unit = offer.get("unit")
    base = f"ab {format_eur(offer['price_from'])}"
    return f"{base} {unit}" if unit else base


def _selfcheck() -> None:
    nrs: set[str] = set()
    for cat in PRICE_CATEGORIES:
        for o in cat["offers"]:
            assert o["nr"] not in nrs, f"duplicate {o['nr']}"
            nrs.add(o["nr"])
            models = sum(k in o for k in ("price", "price_from", "price_base"))
            assert models == 1, f"{o['nr']}: exactly one price model"
            assert o["name"] and o["desc"], o["nr"]
            assert o.get("details_html"), f"{o['nr']}: missing details_html"
            if "price_from" in o or "price_base" in o:
                assert o.get("price_detail"), f"{o['nr']}: staffel needs price_detail"
            if "price_base" in o:
                for key in ("price_add", "price_team", "team_from", "slug", "details_html"):
                    assert o.get(key), f"{o['nr']}: price_base needs {key}"
                assert o["price_team"] > o["price_base"], o["nr"]
    assert len(nrs) == 32, f"expected 32 offers, got {len(nrs)}"
    assert format_eur(3475) == "3.475 €" and format_eur(0) == "free"
    assert offer_price_text({"price_base": 745, "price_add": 125}) == "ab 745 €"
    print(f"pricing selfcheck OK ({len(nrs)} offers)")


if __name__ == "__main__":
    _selfcheck()
