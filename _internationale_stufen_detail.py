"""Page-level detail for INT stage subpages (INT-00 + INT-01…04 stages).

Source: Angebote/Angebot RU/stufen/*.md — merged at runtime with _internationale_stufen.py cards.
"""
from __future__ import annotations

from _internationale_angebote import EN_SLUG_MAP, INT_OFFER_CONFIGS_DE, RU_SLUG_MAP
from _internationale_stufen import INT_STAGES, stage_price_label

_DE_PARENT_SLUG = {c["nr"]: c["slug"] for c in INT_OFFER_CONFIGS_DE}

STAGE_SLUGS: dict[str, dict[str, str]] = {

    "INT-00": {"de": "erstberatung", "en": "intro-call", "ru": "pervaya-konsultatsiya"},
    "INT-01-E": {"de": "deutschland-orientierung", "en": "germany-orientation", "ru": "orientatsiya-germaniya"},
    "INT-01-A": {"de": "business-check", "en": "business-check", "ru": "biznes-chek"},
    "INT-01-B": {"de": "gruendungsplanung", "en": "founding-planning", "ru": "planirovanie-osnovaniya"},
    "INT-01-F": {"de": "launch-roadmap", "en": "launch-roadmap", "ru": "launch-roadmap"},
    "INT-01-C": {"de": "launch-begleitung", "en": "launch-support", "ru": "soprovozhdenie-zapuska"},
    "INT-01-D": {"de": "gruendungs-risiko-check", "en": "founding-risk-check", "ru": "risk-chek-osnovaniya"},
    "INT-02-A": {"de": "einzelstunde", "en": "single-hour", "ru": "odin-chas"},
    "INT-02-B": {"de": "themenmodul", "en": "topic-module", "ru": "tematicheskiy-modul"},
    "INT-02-C": {"de": "6-monats-begleitung", "en": "6-month-support", "ru": "6-mesyacev-soprovozhdenie"},
    "INT-02-D": {"de": "objektsuche", "en": "property-search", "ru": "poisk-obekta"},
    "INT-03-A": {"de": "quick-business-check", "en": "quick-business-check", "ru": "quick-check"},
    "INT-03-B": {"de": "business-health-check", "en": "business-health-check", "ru": "health-check"},
    "INT-03-C": {"de": "team-kultur", "en": "team-culture", "ru": "komanda-i-kultura"},
    "INT-03-D": {"de": "scale-up-readiness", "en": "scale-up-readiness", "ru": "scale-up-gotovnost"},
    "INT-03-E": {"de": "einzelproblem", "en": "single-problem", "ru": "odna-problema"},
    "INT-03-F": {"de": "turnaround-begleitung", "en": "turnaround-support", "ru": "turnaround-soprovozhdenie"},
    "INT-04-A": {"de": "markt-risiko-check", "en": "market-risk-check", "ru": "rynok-i-riski"},
    "INT-04-B": {"de": "setup-tochtergesellschaft", "en": "subsidiary-setup", "ru": "setup-dochernoy"},
    "INT-04-C": {"de": "kyc-sanktions-modul", "en": "kyc-sanctions-module", "ru": "kyc-sankcii"},
    "INT-04-D": {"de": "go-to-market", "en": "go-to-market", "ru": "go-to-market"},
    "INT-04-E": {"de": "retainer-management", "en": "management-retainer", "ru": "retainer-upravlenie"},
}

STAGE_PARENT_NR: dict[str, str | None] = {
    "INT-00": None,
    "INT-01-E": 'INT-01',
    "INT-01-A": 'INT-01',
    "INT-01-B": 'INT-01',
    "INT-01-F": 'INT-01',
    "INT-01-C": 'INT-01',
    "INT-01-D": 'INT-01',
    "INT-02-A": 'INT-02',
    "INT-02-B": 'INT-02',
    "INT-02-C": 'INT-02',
    "INT-02-D": 'INT-02',
    "INT-03-A": 'INT-03',
    "INT-03-B": 'INT-03',
    "INT-03-C": 'INT-03',
    "INT-03-D": 'INT-03',
    "INT-03-E": 'INT-03',
    "INT-03-F": 'INT-03',
    "INT-04-A": 'INT-04',
    "INT-04-B": 'INT-04',
    "INT-04-C": 'INT-04',
    "INT-04-D": 'INT-04',
    "INT-04-E": 'INT-04',
}

STAGE_PAGE_FIELDS: dict[str, dict] = {
    "INT-00": 
{   'ergebnis': [   'Konkrete Klarheit, ob und wie wir weiterhelfen können',
                    'Empfehlung für den nächsten Baustein auf dem Gründungsweg',
                    'Kostenlos und unverbindlich — kein Verkaufsdruck'],
    'excluded': [   'Keine Rechtsberatung (RDG), keine Steuerberatung (StBerG)',
                    'Kein schriftlicher Report — dafür gibt es die jeweiligen Leistungen (z. B. Deutschland-Orientierung)',
                    'Keine Gewerbeanmeldung oder Behördentermine in unserem Namen'],
    'faq': [   (   'Muss ich danach ein Paket buchen?',
                   'Nein. Sie entscheiden frei — viele starten mit Orientierung oder einer einzelnen Stufe.'),
               (   'Reicht das für Gründungsberatung?',
                   'Als Einstieg ja. Für Marktüberblick → Deutschland-Orientierung; für Planung → Business Check, Gründungsplanung oder Paket „Begleitung bei 0“.'),
               (   'Kann ich direkt eine Stufe buchen?',
                   'Ja — wenn Ihr Bedarf klar ist. Die Erstberatung lohnt sich bei Unsicherheit.')],
    'fuer_wen': [   '„Ich will gründen, weiß aber nicht, wo ich anfangen soll.“',
                    '„Welche Rechtsform, welches Budget, welche Behörden — in welcher Reihenfolge?“',
                    '„Mein Business läuft, aber irgendetwas hakt — Finanzen, Team, Kunden.“',
                    '„Wir wollen in den EU-Markt expandieren — was brauchen wir in Deutschland?“'],
    'fuer_wen_intro': 'Sie planen ein Business in Deutschland — oder Ihr Unternehmen läuft bereits — und wollen ohne '
                      'Verkaufsdruck klären, ob und wie Beraterium helfen kann.',
    'leistungen': [   'Strukturiertes Gespräch zu Situation, Zielen und Zeitplan',
                      'Einordnung, welche Rubrik passt (Gründung · Integration · Turnaround · Expansion)',
                      'Empfehlung der passenden Stufe oder des Pakets — einzeln buchbar',
                      'Klare nächste Schritte — auch wenn Sie danach alleine weitermachen'],
    'name': {'de': 'Erstberatung', 'en': 'Intro call', 'ru': 'Первая консультация'},
    'next': ['INT-01-E', 'INT-01-P0', 'INT-03-A'],
    'steps': [   ('Termin buchen', 'Online, 30 Min., DE/EN/RU — kostenlos.'),
                 ('Kurze Vorbereitung', 'Optional: Idee, Unternehmen, aktueller Stand.'),
                 ('Gespräch', 'Situation, Zielmarkt, Aufenthalt, Budget, Unsicherheiten.'),
                 ('Empfehlung', 'Nächster Schritt — z. B. Orientierung, Begleitung bei 0 oder Launch-Paket.')],
    'tag': {'de': 'INTERNATIONALE ANGEBOTE', 'en': 'INTERNATIONAL SERVICES', 'ru': 'МЕЖДУНАРОДНЫЕ УСЛУГИ'},
    'team_slugs': ['veronika-berdnikova', 'aleksandra-polosukhina', 'till-blania'],
    'teaser': {   'de': '30 Minuten, kostenlos — ohne Verkaufsdruck die passende Stufe finden. DE/EN/RU.',
                  'en': '30 minutes, free — find the right stage with no sales pressure. DE/EN/RU.',
                  'ru': '30 минут, бесплатно — найти подходящий этап без давления. DE/EN/RU.'}}
,
    "INT-01-E":
{   'ergebnis': [   'Realistisches Bild vom Gründen in Deutschland',
                    'Klarheit, ob und wie der Weg für Sie tragfähig wirkt',
                    'Grundlage für die Entscheidung: Orientierung reicht oder nächste Stufe'],
    'excluded': [   'Keine Rechts- oder Steuerberatung',
                    'Kein individueller Businessplan oder Gründungsfahrplan',
                    'Keine Empfehlung zu konkreten Verträgen oder Behördenterminen'],
    'faq': [   ('Brauche ich vorher die kostenlose Erstberatung?', 'Empfohlen, aber nicht Pflicht — bei klarem Bedarf direkt buchbar.'),
               ('Reicht das zum Gründen?', 'Als Informationsbasis ja. Für Planung → Business Check, Gründungsplanung oder Paket „Begleitung bei 0“.'),
               ('Auf Russisch?', 'Ja — DE/EN/RU.')],
    'fuer_wen': [   'Sie wissen noch nicht, ob Gründung in DE für Sie Sinn macht',
                    'Sie wollen Markt, Rahmenbedingungen und typische Stolpersteine verstehen',
                    'Sie haben viele offene Fragen, bevor Sie Geld in eine Stufe investieren',
                    'Nach der kostenlosen Erstberatung: Sie brauchen mehr Tiefe als 30 Minuten'],
    'fuer_wen_intro': 'Sie wollen sich informieren — über Deutschland, den Markt, was es gibt und was man beachten muss — '
                      'bevor Sie sich festlegen.',
    'leistungen': [   '1:1-Vortrag (45 Min.): Gründungskontext DE, Markt, Behörden, typische Risiken',
                      'Fragen & Antworten (45 Min.): Ihre Situation, Ihre Unsicherheiten',
                      'Einordnung möglicher nächster Schritte (ohne Verkaufsdruck)',
                      'Sprachen: DE / EN / RU'],
    'next': ['INT-01-A', 'INT-01-P0', 'INT-01-P1'],
    'steps': [   ('Termin buchen', '1,5 h Block, online oder vor Ort.'),
                 ('Vortrag (45 Min.)', 'Markt, Rahmenbedingungen, typische Gründerfehler.'),
                 ('Q&A (45 Min.)', 'Ihre Fragen, Ihre Situation.'),
                 ('Empfehlung', 'Optional: Business Check, Begleitung bei 0 oder Launch-Paket.')]}
,
    "INT-01-A": 
{   'ergebnis': [   'Ehrliche Einschätzung, ob und in welche Richtung Gründung in DE Sinn macht',
                    'Kosten und benötigte Spezialisten grob klar',
                    'Nächster Schritt definiert — Gründungsplanung oder Launch'],
    'excluded': [   'Keine Rechts- oder Steuerberatung',
                    'Kein fertiger Businessplan — Struktur ja, Inhalt erstellen Sie (mit Anleitung in INT-01-B)',
                    'Keine Gewerbeanmeldung oder Termine in unserem Namen',
                    'Kein Wochen-für-Wochen-Umsetzungsplan (→ INT-01-F)'],
    'faq': [   ('Brauche ich vorher die kostenlose Erstberatung?', 'Empfohlen bei Unsicherheit. Bei klarem Bedarf direkt buchbar.'),
               (   'Ist das eine Risikoanalyse?',
                   'Überblick über Gründungsrisiken — keine vollständige RA (→ INT-01-D oder RA-02).'),
               ('Noch keine konkrete Idee?', 'Genau dafür gedacht — oft zusammen mit INT-01-B im Paket P0.')],
    'fuer_wen': [   'Sie sind neu in Deutschland oder planen anzukommen',
                    'Sie haben noch keine oder nur vage Geschäftsidee(n)',
                    'Rechtsform, Budget und typische Risiken realistisch einschätzen',
                    'Vor der gemeinsamen Gründungsplanung oder dem Paket „Begleitung bei 0“'],
    'fuer_wen_intro': 'Standortbestimmung — ob und wie Gründung in Deutschland für Sie tragfähig ist, bevor Notar, '
                      'Steuerberater oder tiefere Planung.',
    'leistungen': [   'Standortbestimmung: Idee(n), Zielkunden, grober Wettbewerb',
                      'Ausgangslage: Aufenthalt, Sprache, Qualifikationen, Netzwerk',
                      'Rechtsform-Optionen einordnen (keine Rechtsberatung)',
                      'Grobe Kostenübersicht: Gründung, Fixkosten, Startkapital',
                      'Spezialisten: Notar, Steuerberater, Versicherungen, IHK/HWK',
                      'Top-5-Risiken für Gründer mit Migrationshintergrund',
                      'Empfohlene Reihenfolge der nächsten Schritte'],
    'next': ['INT-01-B', 'INT-01-P0', 'INT-01-F'],
    'steps': [   ('Vorbereitung', 'Kurzer Fragebogen (Stand, Ideen, Dokumente).'),
                 ('Workshop (2–3 h)', 'Online oder vor Ort — alle Themenblöcke.'),
                 ('Kurzprotokoll', '5–8 Seiten innerhalb von 5 Werktagen.'),
                 ('Nachbesprechung', 'Optional 30 Min. zum Protokoll.')]}
,
    "INT-01-B": 
{   'ergebnis': [   'Ihr Gründungsplan in Ihren Worten — Markt, Modell, Analyse',
                    'SWOT, PESTEL und Finanzplan-Struktur ausgearbeitet',
                    'Grundlage für Launch Roadmap (INT-01-F) oder Umsetzung'],
    'excluded': [   'Keine Rechts- oder Steuerberatung',
                    'Kein investor-ready Businessplan durch uns — Sie erstellen, wir leiten an',
                    'Keine laufende Umsetzungsbegleitung (→ INT-01-C)',
                    'Kein Wochen-für-Wochen-Launch-Plan (→ INT-01-F)'],
    'faq': [   ('Macht ihr den Businessplan für mich?', 'Nein. Wir führen Sie durch die Schritte — Inhalt und Zahlen liefern Sie.'),
               ('Brauche ich INT-01-A?', 'Stark empfohlen im Paket P0. Bei klarer Ausgangslage direkt möglich.'),
               ('Reicht das für die Bank?', 'Struktur und Tiefe für Gründung — investor-ready Format liegt bei Ihnen/Steuerberater.')],
    'fuer_wen': [   'Sie wissen noch nicht genau, was Sie gründen wollen',
                    'Sie wollen Markt, Wettbewerber und Geschäftsmodell gemeinsam erarbeiten',
                    'Sie sind bereit, selbst zu arbeiten — mit strukturierter Anleitung',
                    'Nach Business Check oder Orientierung — „Begleitung bei 0“'],
    'fuer_wen_intro': 'Gemeinsam Ihr Business planen: Markt analysieren, Modell definieren, SWOT & PESTEL — '
                      'Sie arbeiten, wir leiten Schritt für Schritt an.',
    'leistungen': [   'Markt- und Wettbewerbsanalyse (Methodik + Ihre Recherche)',
                      'Geschäftsmodell und Angebote definieren',
                      'SWOT- und PESTEL-Analyse',
                      'Finanzplan-Struktur und Plausibilität (keine Steuerberatung)',
                      'Arbeitsdokument / Vorlagen — Ihr Plan entsteht bei Ihnen',
                      'Mehrere Coaching-Sessions + Review zwischen den Schritten'],
    'next': ['INT-01-F', 'INT-01-C', 'INT-01-D'],
    'steps': [   ('Kick-off', 'Stand, Ziel, Zeitrahmen, welche Bausteine zuerst.'),
                 ('Arbeitsphasen', 'Sessions zu Markt, Modell, Analyse, Finanzstruktur.'),
                 ('Eigenarbeit', 'Recherche und Ausfüllen zwischen Terminen.'),
                 ('Review', 'Gemeinsamer Durchgang — bereit für Launch Roadmap oder Begleitung.')]}
,
    "INT-01-F": 
{   'ergebnis': [   'Umsetzbarer Fahrplan Woche 1 → Monat 3',
                    'Checklisten für Behörden, Dokumente, Termine',
                    'Allein oder mit INT-01-C abarbeitbar'],
    'excluded': [   'Keine Rechts- oder Steuerberatung',
                    'Keine laufende Begleitung bei Terminen (→ INT-01-C)',
                    'Keine Businessplan-Erstellung — setzt Planung voraus (INT-01-B oder eigene Vorarbeit)',
                    'Notar-, Anwalts- und Steuerberaterhonorare separat'],
    'faq': [   ('Reicht das ohne Begleitung?', 'Ja — wenn Sie diszipliniert umsetzen. Viele buchen danach INT-01-C.'),
               ('Enthält das Fördermittel-Recherche?', 'Grundlegende Hinweise ja. Tiefe Recherche → INT-01-P3.'),
               ('Idee steht schon — brauche ich B?', 'Nein — wenn Markt, Modell und Planung bei Ihnen liegen, starten Sie hier oder mit Paket P1.')],
    'fuer_wen': [   'Geschäftsidee und Planung stehen — Sie wissen, was Sie gründen',
                    'Sie brauchen den **Umsetzungs**-Fahrplan, nicht nochmal Businessplan',
                    'Klarheit: Pre-Launch, Launch, erste Kunden, erste 90 Tage',
                    'Einstieg für Paket P1 (Launch Roadmap + Begleitung)'],
    'fuer_wen_intro': 'Persönlicher Launch-Plan Woche 1 bis Monat 3 — wenn Idee und Gründungsplanung geklärt sind.',
    'leistungen': [   'Phase 1 Pre-Launch: Rechtsform vorbereiten, Genehmigungen, Versicherungen',
                      'Phase 2 Launch: Gewerbe, Finanzamt, ELSTER, Banking, Verträge',
                      'Phase 3 First Clients: Positionierung, Preise, B2B-Vertrieb DE',
                      'Phase 4 First 90 Days: KPIs, Prozesse, Key Risks',
                      'Roadmap-Dokument (PDF, DE/EN/RU) + Checklisten pro Phase',
                      '1 Review-Call (60 Min.) nach Lieferung'],
    'next': ['INT-01-C', 'INT-01-D', 'INT-01-P1'],
    'steps': [   ('Kick-off', 'Status, vorhandene Planung, Zieltermin Gründung.'),
                 ('Workshop', 'Alle vier Phasen, Lücken identifizieren.'),
                 ('Roadmap-Lieferung', 'Innerhalb von 10 Werktagen.'),
                 ('Review-Call', 'Durchgang, Fragen, Feintuning.')]}
,
    "INT-01-C": 
{   'ergebnis': [   'Gründung ohne Chaos',
                    'Immer klar: nächster Schritt, Ansprechpartner, Unterlagen',
                    'Nichts versandet in E-Mail-Ordnern'],
    'excluded': [   'Keine Rechts- oder Steuerberatung',
                    'Keine Vertretung vor Behörden oder Notar',
                    'Keine Businessplan-Erstellung durch uns',
                    'Honorare für Notar, Anwalt, Steuerberater — direkt an Partner'],
    'faq': [   ('Wie lange reichen 2.900 €?', 'Typisch 4–8 Wochen. Bei UG/GmbH bis 12 Wochen — im Kick-off klären.'),
               ('Brauche ich INT-01-F?', 'Stark empfohlen. Ohne Launch Roadmap: Mini-Roadmap in Woche 1 (im Preis).')],
    'fuer_wen': [   'Launch Roadmap vorhanden (INT-01-F) — oder Parallelstart mit Mini-Roadmap',
                    'Behörden, Banken und Fachdeutsch überfordern',
                    'Spezialisten brauchen, wissen aber nicht wen',
                    'Angst, Termine oder Fristen zu verpassen'],
    'fuer_wen_intro': 'Sie wollen gründen und brauchen aktive Begleitung — nicht nur einmal einen Plan.',
    'leistungen': [   'Timelines managen — diese Woche vs. nächste Woche',
                      'Behördenbriefe und Fachjargon in Klartext übersetzen',
                      'Spezialisten aus Netzwerk finden (Sie schließen Verträge)',
                      'Fragen und Unterlagen vor jedem Termin vorbereiten',
                      'Offene Punkte tracken, Erinnerungen, Follow-ups',
                      'Wöchentliche Calls (30–45 Min.) + Fair-Use-Support werktags'],
    'next': ['INT-01-D', 'INT-03-A', 'INT-01-P1'],
    'steps': [   ('Kick-off (90 Min.)', 'Ist-Stand, Roadmap, Zeithorizont, Blocker.'),
                 ('Wochen 1–12', 'Regelmäßige Calls + asynchroner Support.'),
                 ('Meilensteine', 'Gewerbe, ELSTER, Konto, ggf. Gesellschaft.'),
                 ('Abschluss', 'Übergabeprotokoll, optional INT-01-D oder INT-03-A.')]}
,
    "INT-01-D": 
{   'ergebnis': ['Bewusst live gehen — oder wissen, was in 90 Tagen abzusichern ist', 'Aus Bauchgefühl wird Klarheit'],
    'excluded': [   'Keine vollständige Risiko-Analyse 360° (Standardangebot für KMU)',
                    'Keine Einzel-Risikoanalyse auf Abruf (dafür: Risiko-Beratung Analyse)',
                    'Keine Rechts- oder Steuerberatung'],
    'faq': [   (   'Unterschied zur Risiko-Analyse 360°?',
                   'Launch-Fokus, 3 h, Top-5. Risiko-Analyse 360° = vollständige Unternehmensanalyse ab ca. 3.475 €.'),
               ('Vor oder nach Gründung?', 'Ideal vor Go-Live — auch in den ersten Wochen sinnvoll.')],
    'fuer_wen': [   'Business Check und/oder Roadmap liegen vor',
                    'Risiken bekannt — aber nicht welche die größten für Sie sind',
                    'Banking (GUS), Verträge, Steuer, Aufenthalt, Versicherungen unsicher',
                    'Priorisierte Top-5-Liste statt 200-Seiten-Report'],
    'fuer_wen_intro': 'Kurz vor dem Launch — oder gerade gegründet — wollen Sie typische Blind Spots erkennen, bevor '
                      'sie teuer werden.',
    'leistungen': [   'Workshop (ca. 3 h): kritische Gründungsrisiken für Ihren Fall',
                      'Report (8–12 Seiten): Top-5 mit Schadensspanne und Gegenmaßnahmen',
                      'Maßnahmenplan: vor Go-Live vs. kann warten',
                      'Optional: Brücke zur Risiko-Beratung (Analyse) oder Risiko-Analyse 360° nach Launch',
                      'Beraterium-Logik: Gefahren → bewerten → priorisieren in Euro'],
    'next': ['INT-03-A', 'INT-03-B', 'INT-02-B'],
    'steps': [   ('Vorbereitung', 'Fragebogen + Dokumente.'),
                 ('Workshop', 'Risiken identifizieren und bewerten.'),
                 ('Report', 'Innerhalb von 7 Werktagen.'),
                 ('Nachbesprechung', 'Prioritäten und nächste Schritte.')]}
,
    "INT-02-A": 
{   'ergebnis': ['Konkretes Thema geklärt', 'Nächste Schritte definiert'],
    'excluded': ['Kein Sprachkurs', 'Keine Rechtsberatung bei Verträgen'],
    'faq': [('Minimum Buchung?', '1 Stunde. Verlängerung in 30-Min.-Schritten.')],
    'fuer_wen': [   'Behördenbrief verstehen und Antwort vorbereiten',
                    'Termin beim Finanzamt — Erwartungen und Unterlagen',
                    'Gespräch mit Vermieter oder Partner vorbereiten',
                    'Kultureller Missverständnis aufarbeiten',
                    'ELSTER-Grundlagen, Belege, Fristen'],
    'fuer_wen_intro': 'Ein konkretes Thema — Sie brauchen keine langfristige Begleitung.',
    'leistungen': [   '1:1 Coaching, online oder vor Ort, DE/EN/RU',
                      'Mindestens 1 Stunde, Buchung in 30-Min.-Schritten',
                      'Flexibles Thema nach Ihrem Bedarf'],
    'next': ['INT-02-B', 'INT-02-C', 'INT-01-E'],
    'steps': [   ('Termin buchen', 'Thema kurz beschreiben.'),
                 ('Session (60+ Min.)', '1:1, praxisnah.'),
                 ('Optional Follow-up', 'Weitere Stunde oder Modul buchbar.')]}
,
    "INT-02-B": 
{   'ergebnis': ['Thema sicher beherrschen', 'Checkliste für den Alltag'],
    'excluded': ['Kein Sprachkurs', 'Keine Rechtsberatung bei Miet- oder Arbeitsverträgen'],
    'faq': [('Mehrere Module?', 'Ja — z. B. Integrations-Paket INT-02-P.')],
    'fuer_wen': [   'Mehr als eine Stunde nötig — strukturiertes Modul',
                    'Behörden, ELSTER oder Kommunikation DE gezielt lernen',
                    'Parallel zur Gründung (INT-01) oder danach'],
    'fuer_wen_intro': 'Sie wollen ein Thema vertiefen — Behörden, ELSTER, Kultur oder Rechte & Pflichten.',
    'leistungen': [   '3× Sessions à 60 Min. — Modul wählbar',
                      'Behörden: Finanzamt, Gewerbeamt, Ausländerbehörde',
                      'ELSTER & Buchhaltung: Registrierung, USt, Belege',
                      'Kommunikation & Kultur: wie ticken Deutsche im Business',
                      'Checkliste/Hausaufgaben zwischen Terminen'],
    'next': ['INT-02-C', 'INT-02-D', 'INT-01-A'],
    'steps': [   ('Modul wählen', 'Behörden, ELSTER, Kultur oder Rechte.'),
                 ('3 Sessions', 'Wöchentlich oder nach Rhythmus.'),
                 ('Hausaufgaben', 'Konkrete Aufgaben zwischen Terminen.')]}
,
    "INT-02-C": 
{   'ergebnis': ['Mehr Sicherheit im Alltag und Business', 'Behörden, Kultur, Kommunikation abgedeckt'],
    'excluded': ['Kein Sprachkurs', 'Keine Rechtsberatung bei Verträgen'],
    'faq': [('Kürzere Laufzeit?', 'Standard 6 Monate — Einzelstunden/Module parallel möglich.')],
    'fuer_wen': [   'Neu in DE oder parallel zur Gründung',
                    'Behörden, Kultur und Business-Alltag aus einer Hand',
                    'Regelmäßiger Rhythmus statt Einzeltermine'],
    'fuer_wen_intro': 'Kontinuierliche Unterstützung beim Ankommen — nicht nur punktuelle Stunden.',
    'leistungen': [   'Individueller Plan zu Beginn (Themen, Prioritäten)',
                      '2×/Monat Sessions à 60 Min.',
                      'Asynchroner Support (Fair-Use, werktags)',
                      'Review alle 6 Wochen — Plan anpassen',
                      'Laufzeit 6 Monate'],
    'next': ['INT-02-D', 'INT-02-B', 'INT-01-F'],
    'steps': [   ('Kick-off', 'Plan und Rhythmus festlegen.'),
                 ('Monate 1–6', 'Sessions + Support.'),
                 ('Reviews', 'Alle 6 Wochen Fortschritt.'),
                 ('Abschluss', 'Status und Empfehlung Folgeleistungen.')]}
,
    "INT-02-D": 
{   'ergebnis': ['Passendes Objekt gefunden oder klare Kriterien', 'Vertrag verstanden — nächste Schritte klar'],
    'excluded': ['Keine Rechtsberatung beim Mietvertrag', 'Keine Bürgschaft oder Garantieübernahme'],
    'faq': [('Ab 1.900 €?', 'Ja — abhängig von Region und Umfang.')],
    'fuer_wen': [   'Wohnungssuche: Kriterien, Anschreiben, Besichtigung',
                    'Gewerbeobjekt: Lage, Nutzbarkeit, Anforderungen',
                    'Mietvertrag verstehen (keine Rechtsberatung)'],
    'fuer_wen_intro': 'Wohnung oder Gewerbeobjekt — optional, wenn Suche und Verständnis des Mietvertrags Hilfe '
                      'brauchen.',
    'leistungen': [   'Kriterien definieren und Anschreiben formulieren',
                      'Begleitung bei Besichtigungen (optional)',
                      'Mietvertrag verständlich erklären',
                      'Preis nach Umfang — im Erstgespräch fixiert'],
    'next': ['INT-02-C', 'INT-02-B', 'INT-02-A'],
    'steps': [   ('Erstgespräch', 'Variante, Region, Dringlichkeit.'),
                 ('Suche', 'Anschreiben, Termine, Besichtigungen.'),
                 ('Abschluss', 'Vertrag verstehen, Übergabe.')]}
,
    "INT-03-A": 
{   'ergebnis': ['Wissen, wo es brennt', 'Empfehlung: B, E, F oder RA-01 als nächster Schritt'],
    'excluded': [   'Keine vollständige Risikomatrix (→ INT-03-B)',
                    'Keine Einzel-Risikoanalyse auf Abruf (kein RA-02-Ersatz)'],
    'faq': [('Ersetzt RA-01?', 'Nein — Quick Check ist Einstieg, keine 360°-Analyse.')],
    'fuer_wen': [   'Spürbare Reibung — Finanzen, Team, Prozesse unklar',
                    'Schnelle Diagnose ohne sofort 3.500 € Health Check',
                    'Top-5-Issues in 90–120 Minuten'],
    'fuer_wen_intro': 'Der Betrieb läuft — aber etwas stimmt nicht. Schnelle Klarheit, ob tiefer eingestiegen werden '
                      'muss.',
    'leistungen': [   'Diagnose-Session: Finanzen, Kunden, Vertrieb, MA, Prozesse, IT, Founder',
                      'Mündliche Top-5-Issues am Ende',
                      'Kurzmemo (2–3 Seiten) innerhalb 3 Werktagen'],
    'next': ['INT-03-B', 'INT-03-E', 'INT-03-F'],
    'steps': [   ('Vorbereitung', 'Kurzer Fragebogen zur Ist-Situation.'),
                 ('Session (90–120 Min.)', 'Strukturierte Diagnose.'),
                 ('Kurzmemo', 'Top-5 schriftlich.')]}
,
    "INT-03-B": 
{   'ergebnis': ['Klarheit: was zuerst, was warten kann', 'Basis für INT-03-F oder Eigenumsetzung'],
    'excluded': ['Keine Rechts- oder Steuerberatung', 'Keine Einzel-Risikoanalyse auf Abruf'],
    'faq': [('BAFA?', 'Förderfähig — Sie stellen Antrag, wir liefern Bemessungsgrundlage.')],
    'fuer_wen': [   'Mehr als ein Gespräch nötig',
                    'Risikomatrix und Top-5-Maßnahmen gewünscht',
                    'BAFA-Förderung (50–80 %) möglich'],
    'fuer_wen_intro': 'Strukturelle Engpässe — Finanzamt, Cashflow, Team, Prozesse. Volle Beraterium-Methode.',
    'leistungen': [   'Kick-off (90 Min.) + Workshops mit Schlüsselpersonen',
                      'Risikomatrix: identifizieren, in Euro bewerten, priorisieren',
                      'Report: Top-5-Maßnahmen mit Verantwortlichkeiten',
                      'Strategie-Session zur Freigabe',
                      'Optional: Nachbesprechung nach 30 Tagen',
                      'Hinweise zu BAFA-Antrag'],
    'next': ['INT-03-F', 'INT-03-D', 'INT-03-E'],
    'steps': [   ('Kick-off', '90 Min. Ist-Situation.'),
                 ('Workshops', 'Risikomatrix erstellen.'),
                 ('Report', 'Top-5 und Fahrplan.'),
                 ('Strategie-Session', 'Freigabe Maßnahmenplan.')]}
,
    "INT-03-C": 
{   'ergebnis': ['Konkreter Plan für Gründer/in und Team', 'Keine Rechtsberatung — unternehmerische Beratung'],
    'excluded': ['Keine Rechtsberatung Arbeitsrecht', 'Keine Einzel-Risikoanalyse auf Abruf'],
    'faq': [('Nur für Gründer?', 'Auch für GF mit wachsendem Team in DE.')],
    'fuer_wen': [   '„Deutsche MA arbeiten nicht wie gewohnt.“',
                    '„10 Leute und mehr Stress als alleine.“',
                    'Cross-kulturelle Führung und Founder-Abhängigkeit'],
    'fuer_wen_intro': 'Team und Kultur hakt — Micromanagement, DE-Kultur, Delegation.',
    'leistungen': [   'Micromanagement vs. Delegation analysieren',
                      'Verantwortung und Entscheidungswege klären',
                      'Kommunikation und Feedback (DE-Kultur)',
                      'Onboarding, Offboarding, Wissensverlust',
                      '4–6 Sessions + konkreter HR/Organisationsplan'],
    'next': ['INT-03-B', 'INT-03-F', 'INT-03-E'],
    'steps': [   ('Analyse', 'Ist-Situation Team und Kultur.'),
                 ('Sessions (4–6)', 'Coaching und konkrete Übungen.'),
                 ('Plan', 'Was ändern, welche Prozesse, nächste Schritte.')]}
,
    "INT-03-D": 
{   'ergebnis': ['Fundierte Entscheidung vor der nächsten Wachstumsstufe', 'Brücke zu INT-03-P3 + RA-01'],
    'excluded': ['Keine Rechts- oder Steuerberatung', 'Quick Check ersetzt nicht RA-01'],
    'faq': [('Nach Health Check?', 'Ideal nach INT-03-B — auch eigenständig buchbar.')],
    'fuer_wen': [   'Wachstumspläne — unsicher ob Struktur hält',
                    'Team von 5 → 15 → 30 Mitarbeitende',
                    'Go/No-Go vor nächster Wachstumsstufe'],
    'fuer_wen_intro': '„Wir wollen wachsen.“ — Bevor Sie skalieren: People, Money, Sales, Ops mitwachsen?',
    'leistungen': [   'Checkliste: People, Money, Sales, Operations, Supply, Management',
                      '2 Workshops + Report',
                      'Pre-Growth-Risiko-Assessment',
                      'Go/No-Go-Empfehlung und Top-Risiken'],
    'next': ['INT-03-P3', 'INT-03-B', 'INT-03-F'],
    'steps': [   ('Workshop 1', 'Ist-Stand und Wachstumsziele.'),
                 ('Workshop 2', 'Lücken in People, Money, Sales, Ops.'),
                 ('Report', 'Go/No-Go und Top-Risiken.')]}
,
    "INT-03-E": 
{   'ergebnis': ['Klarer Plan für das dominierende Problem', 'Preis im Kick-off fixiert'],
    'excluded': ['Kein Ersatz für vollständigen Health Check', 'Keine Rechts- oder Steuerberatung'],
    'faq': [('Ab 1.900 €?', 'Ja — abhängig von Komplexität, im Erstgespräch fixiert.')],
    'fuer_wen': [   'Hohe Fluktuation oder operativer Overload',
                    'Umsatz wächst, Geld fehlt trotzdem',
                    'Lieferant verspätet, Kunden unzufrieden',
                    '„Wir können nicht skalieren“'],
    'fuer_wen_intro': 'Ein konkretes Problem dominiert — Diagnose und Plan, kein Full Health Check.',
    'leistungen': [   'Diagnose → Ursachen → Optionen → Maßnahmenplan',
                      '1–2 Wochen, Preis ab 1.900 € nach Komplexität',
                      'Fokus auf ein Schmerzthema'],
    'next': ['INT-03-B', 'INT-03-F', 'INT-03-A'],
    'steps': [   ('Kick-off', 'Problem eingrenzen, Umfang fixieren.'),
                 ('Diagnose', 'Ursachen und Optionen.'),
                 ('Maßnahmenplan', '2–4 Wochen Umsetzungsvorschlag.')]}
,
    "INT-03-F": 
{   'ergebnis': ['Maßnahmen angestoßen und verfolgt', 'Nicht im Schubladen-Report gelandet'],
    'excluded': ['Keine Rechts- oder Steuerberatung', 'Externe Honorare direkt an Partner'],
    'faq': [('Ohne INT-03-B?', 'Möglich bei vergleichbarer Diagnose — im Kick-off klären.')],
    'fuer_wen': [   'Top-Maßnahmen aus Health Check liegen vor',
                    '8 Wochen wöchentliche Begleitung gewünscht',
                    'Blocker aktiv lösen, Fortschritt tracken'],
    'fuer_wen_intro': 'Nach Diagnose (INT-03-B o. ä.): Umsetzung wollen — nicht nur Report in der Schublade.',
    'leistungen': [   'Abgleich Top-Maßnahmen aus Health Check',
                      '8 Wochen wöchentliche Begleitungs-Calls',
                      'Priorisierung: diese Woche, Blocker, Verantwortliche',
                      'Koordination externer Spezialisten bei Bedarf',
                      'Fortschritts-Tracking und Abschluss-Review'],
    'next': ['INT-03-D', 'INT-03-B', 'INT-03-E'],
    'steps': [   ('Kick-off', 'Maßnahmenplan und Wochenrhythmus.'),
                 ('Wochen 1–8', 'Wöchentliche Calls + Tracking.'),
                 ('Abschluss-Review', 'Status, offene Punkte, Folgeempfehlung.')]}
,
    "INT-04-A": 
{   'ergebnis': ['Fundierte Entscheidung: lohnt DE/EU für Ihr Produkt?', 'Empfohlene Struktur und nächste Schritte'],
    'excluded': ['Keine Rechts- oder Steuerberatung'],
    'faq': [('Pflicht vor Setup?', 'Stark empfohlen — spart Fehl-Investitionen.')],
    'fuer_wen': ['Expansion nach DE/EU geplant', 'Go/No-Go vor Investment', 'Sanktions- und GUS-Kontext relevant'],
    'fuer_wen_intro': 'Etabliertes Unternehmen im Ausland — bevor Geld in DE-Setup fließt.',
    'leistungen': [   'Markteintritt: Segment, Wettbewerb, Preisniveau DE/EU',
                      'Regulatorischer Überblick (keine Rechtsberatung)',
                      'Risiko: Sanktionen, Geldfluss, Trennung Heimat/DE',
                      'Go/No-Go-Empfehlung + nächste Schritte'],
    'next': ['INT-04-B', 'INT-04-C', 'INT-04-D'],
    'steps': [   ('Kick-off', 'Produkt, Heimatmarkt, Ziele.'),
                 ('Analyse (2–3 Wochen)', 'Markt, Regulatorik, Risiken.'),
                 ('Report', 'Go/No-Go und Empfehlung Struktur.')]}
,
    "INT-04-B": 
{   'ergebnis': ['Gesellschaft operativ in DE', 'Saubere Trennung Heimat/DE'],
    'excluded': ['Notar- und Anwaltshonorare, Stammkapital', 'Laufende Buchhaltung'],
    'faq': [('Mit INT-04-C?', 'Bei GUS-Herkunft: KYC-Modul Pflicht — im Setup-Paket enthalten.')],
    'fuer_wen': [   'Go-Entscheidung gefallen',
                    'GmbH, UG oder Zweigniederlassung',
                    'Geschäftsführer vor Ort, Prozesse Startphase'],
    'fuer_wen_intro': 'Tochtergesellschaft aufbauen — Koordination bis operativ.',
    'leistungen': [   'Koordination Notar, Anwalt, Steuerberater (Sie beauftragen)',
                      'Struktur: GmbH, UG, Zweigniederlassung vorbereiten',
                      'Geschäftskonto, Buchhaltungs-Setup, Prozesse',
                      'HR-/Organisationsfragen (GF vor Ort, Vollmachten)',
                      'Projektmanagement bis „Gesellschaft operativ“'],
    'next': ['INT-04-D', 'INT-04-E', 'INT-04-C'],
    'steps': [   ('Kick-off', 'Struktur, Timeline, Partner.'),
                 ('Setup-Phase (8–16 Wochen)', 'Notar, Konto, Prozesse.'),
                 ('Operativ', 'Übergabe und optional Retainer.')]}
,
    "INT-04-C": 
{   'ergebnis': ['Bankfähige Dokumentation', 'Saubere Trennung Heimat/DE'],
    'excluded': ['Keine Steuerberatung', 'Keine Rechtsberatung — Koordination'],
    'faq': [('Ohne C kein Paket?', 'Bei GUS-Herkunft: Pflichtmodul für INT-04-P.')],
    'fuer_wen': [   'Gründer/Shareholder aus GUS oder Hochrisikokontext',
                    'Bank verlangt Dokumentationspaket',
                    'Geldflüsse zwischen Gesellschaften nachvollziehbar'],
    'fuer_wen_intro': 'Pflicht bei GUS-Herkunft — saubere Trennung, KYC/AML für Bank und Partner.',
    'leistungen': [   'Compliance-Check: Trennung Gesellschaften, Geldflüsse',
                      'KYC/AML-Vorbereitung für Bank und Partner',
                      'Dokumentationspaket für deutsche Banken',
                      'Abstimmung mit Anwalt bei komplexen Fällen'],
    'next': ['INT-04-B', 'INT-04-D', 'INT-04-E'],
    'steps': [   ('Ist-Analyse', 'Struktur, Geldflüsse, Risiken.'),
                 ('Dokumentation', 'Paket für Bank/Partner.'),
                 ('Abstimmung', 'Mit Anwalt bei Bedarf.')]}
,
    "INT-04-D": 
{   'ergebnis': ['Erste DE-Kunden und Pipeline', 'Klares wöchentliches Reporting'],
    'excluded': ['Keine Rechtsberatung', 'Mindestlaufzeit 3 Monate'],
    'faq': [('4.500 €/Monat?', 'Ja netto — min. 3 Monate.')],
    'fuer_wen': [   'Setup abgeschlossen oder läuft',
                    'Erste Kunden in DE gewünscht',
                    'Lokale Präsenz ohne sofortigen Umzug'],
    'fuer_wen_intro': 'Vor-Ort-Vertrieb in DE — ab 3 Monate Retainer.',
    'leistungen': [   'Vor-Ort- oder Remote-Vertrieb DE',
                      'Erste Kundenakquise, Messen, LinkedIn, Partner',
                      'Lokale Präsenz repräsentieren',
                      'Wöchentliches Reporting'],
    'next': ['INT-04-E', 'INT-04-B', 'INT-03-A'],
    'steps': [   ('Kick-off', 'Zielkunden, Kanäle, KPIs.'),
                 ('Monate 1–3+', 'Akquise und Reporting.'),
                 ('Review', 'Optional Verlängerung oder INT-04-E.')]}
,
    "INT-04-E": 
{   'ergebnis': ['DE-Operation aus einer Hand koordiniert', 'HQ informiert und entlastet'],
    'excluded': ['Keine Rechts- oder Steuerberatung', 'Mindestlaufzeit 6 Monate'],
    'faq': [('Mit INT-04-D kombinierbar?', 'Ja — GTM zuerst, dann Management-Retainer.')],
    'fuer_wen': [   'Tochter operativ — laufende Steuerung nötig',
                    'Reporting an HQ im Heimatland',
                    'Eskalation und operative Entscheidungen'],
    'fuer_wen_intro': 'Laufendes DE-Management — Koordination Team, Lieferanten, Kunden vor Ort.',
    'leistungen': [   'Koordination Team vor Ort, Lieferanten, Kunden',
                      'Reporting an Geschäftsführung HQ',
                      'Eskalation im vereinbarten Rahmen',
                      'Optional: Umzug Inhaber nach DE vorbereiten'],
    'next': ['INT-04-D', 'INT-04-B', 'INT-04-C'],
    'steps': [   ('Kick-off', 'Mandat, Eskalationswege, Reporting.'),
                 ('Laufend (min. 6 Mon.)', 'Management und Reporting.'),
                 ('Review', 'Anpassung Mandat oder Exit.')]}
,
}

# ponytail: customer-facing copy — replace internal offer codes with product names
_CUSTOMER_CODE_LABELS: tuple[tuple[str, str], ...] = (
    ("INT-01-P3", "Paket „Gründung 360° + Förder-Check“"),
    ("INT-01-P2", "Paket „Gründung 360°“"),
    ("INT-01-P1", "Launch-Paket"),
    ("INT-01-P0", "Paket „Begleitung bei 0“"),
    ("INT-03-P3", "Paket „Scale-up + Risiko-Analyse 360°“"),
    ("INT-03-P2", "Paket „Health Check + Turnaround“"),
    ("INT-03-P1", "Quick Check Plus"),
    ("INT-02-P", "Integrations-Paket"),
    ("INT-04-P", "Setup-Paket"),
    ("INT-01-E", "Deutschland-Orientierung"),
    ("INT-01-A", "Business Check"),
    ("INT-01-B", "Gründungsplanung"),
    ("INT-01-F", "Launch Roadmap"),
    ("INT-01-C", "Launch Begleitung"),
    ("INT-01-D", "Gründungs-Risiko-Check"),
    ("INT-02-A", "Einzelstunde"),
    ("INT-02-B", "Themenmodul"),
    ("INT-02-C", "6-Monats-Begleitung"),
    ("INT-02-D", "Objektsuche"),
    ("INT-03-A", "Quick Business Check"),
    ("INT-03-B", "Business Health Check"),
    ("INT-03-C", "Team & Kultur"),
    ("INT-03-D", "Scale-up Readiness"),
    ("INT-03-E", "Einzelproblem"),
    ("INT-03-F", "Turnaround Begleitung"),
    ("INT-04-A", "Markt- & Risiko-Check"),
    ("INT-04-B", "Setup Tochtergesellschaft"),
    ("INT-04-C", "KYC- & Sanktions-Modul"),
    ("INT-04-D", "Go-to-Market"),
    ("INT-04-E", "Retainer Management"),
    ("INT-04", "Expansion Tochtergesellschaft"),
    ("INT-03", "Business-Turnaround"),
    ("INT-02", "Leben & Arbeiten Deutschland"),
    ("INT-01", "Gründung Deutschland"),
    ("INT-00", "Erstberatung"),
    ("RA-01", "Risiko-Analyse 360°"),
    ("RA-02", "Risiko-Beratung (Analyse)"),
)

_CUSTOMER_PHRASE_FIXES: tuple[tuple[str, str], ...] = (
    ("Paket P1", "Launch-Paket"),
    ("Paket P0", "Paket „Begleitung bei 0“"),
    (
        "Empfehlung: B, E, F oder RA-01 als nächster Schritt",
        "Empfehlung: Business Health Check, Einzelproblem, Turnaround Begleitung "
        "oder Risiko-Analyse 360° als nächster Schritt",
    ),
    ("keine vollständige RA (", "keine vollständige Risikoanalyse ("),
    ("kein RA-02-Ersatz", "kein Ersatz für die Risiko-Beratung (Analyse)"),
    ("Ohne C kein Paket?", "Ohne KYC-Modul kein Setup-Paket?"),
    ("Mit INT-04-C?", "Mit dem KYC- & Sanktions-Modul?"),
    ("INT-03-B o. ä.", "Business Health Check o. ä."),
    ("Brücke zu INT-03-P3 + RA-01", "Brücke zum Paket „Scale-up + Risiko-Analyse 360°“"),
    ("Quick Check ersetzt nicht RA-01", "Quick Check ersetzt nicht die Risiko-Analyse 360°"),
    ("Scale-up Readiness + RA-01", "Scale-up Readiness + Risiko-Analyse 360°"),
)

_HUMANIZE_FIELDS = frozenset({
    "ergebnis", "excluded", "faq", "fuer_wen", "fuer_wen_intro", "leistungen", "steps", "teaser", "name",
})


def customer_label(code: str) -> str:
    for c, label in _CUSTOMER_CODE_LABELS:
        if c == code:
            return label
    return code


def humanize_customer_text(text: str) -> str:
    if not text:
        return text
    out = text
    for old, new in _CUSTOMER_PHRASE_FIXES:
        out = out.replace(old, new)
    for code, label in sorted(_CUSTOMER_CODE_LABELS, key=lambda x: -len(x[0])):
        out = out.replace(code, label)
    return out


def _humanize_value(value):
    if isinstance(value, str):
        return humanize_customer_text(value)
    if isinstance(value, list):
        return [_humanize_value(x) for x in value]
    if isinstance(value, tuple):
        return tuple(_humanize_value(x) for x in value)
    if isinstance(value, dict):
        return {k: _humanize_value(v) for k, v in value.items()}
    return value


def _find_card(nr: str) -> dict | None:
    if nr == "INT-00":
        return None
    prefix = nr.rsplit("-", 1)[0]
    block = INT_STAGES.get(prefix)
    if not block:
        return None
    for st in block.get("stages", []):
        if st["nr"] == nr:
            return st
    return None


def parent_nr(stage_nr: str) -> str | None:
    return STAGE_PARENT_NR.get(stage_nr)


def parent_slug(stage_nr: str, locale: str) -> str | None:
    pn = parent_nr(stage_nr)
    if pn is None:
        return None
    if locale == "en":
        return EN_SLUG_MAP[pn]
    if locale == "ru":
        return RU_SLUG_MAP[pn]
    return _DE_PARENT_SLUG[pn]


def stage_slug(stage_nr: str, locale: str) -> str:
    return STAGE_SLUGS[stage_nr][locale]


def merged_stage(stage_nr: str) -> dict:
    """Card data + page fields + slug."""
    card = _find_card(stage_nr) or {}
    fields = STAGE_PAGE_FIELDS[stage_nr]
    out = {**card, **fields, "nr": stage_nr, "slug": STAGE_SLUGS[stage_nr]}
    if stage_nr == "INT-00":
        out.setdefault("price", 50)
    for key in _HUMANIZE_FIELDS:
        if key in out:
            out[key] = _humanize_value(out[key])
    return out


def all_stage_nrs() -> list[str]:
    return list(STAGE_SLUGS.keys())


def iter_stage_pages() -> list[tuple[str, dict]]:
    """(parent_offer_nr, merged_stage) — INT-00 has parent None."""
    out: list[tuple[str | None, dict]] = []
    for nr in all_stage_nrs():
        pn = parent_nr(nr)
        out.append((pn, merged_stage(nr)))
    return out  # type: ignore[return-value]


def stage_de_route(stage_nr: str) -> str:
    sl = STAGE_SLUGS[stage_nr]["de"]
    pn = parent_nr(stage_nr)
    if pn is None:
        return f"internationale-angebote/{sl}"
    return f"internationale-angebote/{_DE_PARENT_SLUG[pn]}/{sl}"


def stage_en_route(stage_nr: str) -> str:
    sl = STAGE_SLUGS[stage_nr]["en"]
    pn = parent_nr(stage_nr)
    if pn is None:
        return f"international-services/{sl}"
    return f"international-services/{EN_SLUG_MAP[pn]}/{sl}"


def stage_ru_route(stage_nr: str) -> str:
    sl = STAGE_SLUGS[stage_nr]["ru"]
    pn = parent_nr(stage_nr)
    if pn is None:
        return f"ru/internationale-angebote/{sl}"
    return f"ru/internationale-angebote/{RU_SLUG_MAP[pn]}/{sl}"


def build_i18n_stage_routes() -> tuple[dict[str, str], dict[str, str], list[str]]:
    """STATIC additions, RU additions, sitemap canonical paths (DE site)."""
    static: dict[str, str] = {}
    ru: dict[str, str] = {}
    sitemap: list[str] = []
    for nr in all_stage_nrs():
        de = stage_de_route(nr)
        en = stage_en_route(nr)
        ru_p = stage_ru_route(nr)
        static[de] = en
        ru[de] = ru_p
        sitemap.append(f"/{de}/")
        sitemap.append(f"/{ru_p}/")
    return static, ru, sitemap


def en_sitemap_paths() -> list[str]:
    static, _, _ = build_i18n_stage_routes()
    return [f"/{path}/" for path in static.values()]


def stage_rel_path(stage_nr: str, locale: str) -> str:
    route = {"de": stage_de_route, "en": stage_en_route, "ru": stage_ru_route}[locale](stage_nr)
    return f"{route}/index.html"


def stage_url(stage_nr: str, locale: str, pre: str) -> str:
    route = {"de": stage_de_route, "en": stage_en_route, "ru": stage_ru_route}[locale](stage_nr)
    return f"{pre}{route}/"


def stage_detail_href(*, stage_nr: str, locale: str) -> str:
    """Relative href from parent offer page directory."""
    return f"{stage_slug(stage_nr, locale)}/"
