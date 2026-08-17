"""Blindspot Quick Check 2.0 — questions, scoring and result copy (EN).

Pure data (no imports from _gen_pages; imported from there). English
translation of Webseite/site/_blindspot.py — keep both files in sync when
the question catalog changes. Terminology follows EN_COPY_GLOSSARY.md
("3-level hazard catalog", "SME", "Solo self-employed").

The frontend (js/brt-blindspot.js) receives this data as inline JSON via
blindspot_frontend_config().
"""
from __future__ import annotations

import json

from _blindspot_report_content import GENERAL_RISK_TIPS, apply_report_content

# ---------------------------------------------------------------------------
# Rating scale (main question) + follow-up question on measures
# ---------------------------------------------------------------------------

LIKERT: list[dict] = [
    {"value": 0, "label": "No, not a problem at all"},
    {"value": 1, "label": "Could become a problem"},
    {"value": 2, "label": "Would be a major problem"},
    {"value": 3, "label": "Would threaten the business"},
]

MEASURE_QUESTION = "Have you already prepared concrete measures for this case?"
MEASURE_OPTIONS: list[dict] = [
    {"value": 0, "label": "Yes"},
    {"value": 1, "label": "No"},
]

MAX_POINTS_PER_QUESTION = 4  # 3 (Likert) + 1 (no measures)

# Traffic light per question (0-4 points)
TRAFFIC_LIGHT = {"green_max": 1, "yellow_max": 2}  # 3-4 = red

# Overall result in percent (points / max points of the question set)
RESULT_BANDS: list[dict] = [
    {
        "max_pct": 25,
        "key": "gut",
        "label": "Well prepared",
        "text": (
            "You appear well prepared in the areas covered. Individual points "
            "should still be reviewed regularly, as this quick check only covers "
            "a limited selection of possible risks."
        ),
    },
    {
        "max_pct": 50,
        "key": "teilweise",
        "label": "Partly prepared",
        "text": (
            "Your answers show that some risks have already been addressed, but "
            "relevant blind spots remain. The yellow and red areas in particular "
            "should be reviewed as a priority."
        ),
    },
    {
        "max_pct": 75,
        "key": "kritisch",
        "label": "Critical blind spots present",
        "text": (
            "Your answers show several critical blind spots. In these areas, a "
            "single event can already have significant operational, financial or "
            "legal consequences. A full risk analysis is recommended."
        ),
    },
    {
        "max_pct": 100,
        "key": "akut",
        "label": "Urgent need for action",
        "text": (
            "Your answers show critical blind spots in many areas at once — "
            "individual events could reinforce each other. We recommend "
            "addressing the red points promptly and carrying out a full risk "
            "analysis."
        ),
    },
]

# ---------------------------------------------------------------------------
# Categories (visible in the result)
# ---------------------------------------------------------------------------

CATEGORIES: dict[str, str] = {
    "mensch": "People",
    "technik": "Technology",
    "operativ": "Operations",
    "wachstum": "Growth & strategy",
    "markt": "Market & stability",
    "top_themen": "Top topics",
}

ACTIVE_TOP_THEMEN: list[str] = ["tt1", "tt2"]

_BASE_IDS = ["m1", "m2", "m3", "m4", "t1", "t2", "t3", "o1", "o2", "o3"]

# ---------------------------------------------------------------------------
# Question catalog 2.0
# ---------------------------------------------------------------------------
# id scheme: m=People, t=Technology, o=Operations, s=Startup extension,
# k=SME extension. "layer" = hidden hazard-catalog reference (not shown in
# the frontend, but the basis for the why/step texts).

QUESTIONS: list[dict] = [
    # ----- PEOPLE (base) -----
    {
        "id": "m1",
        "cat": "mensch",
        "short": "Your own absence",
        "short_solo": "Absence without plan B",
        "text": (
            "What happens if you are out tomorrow – and suddenly no one can "
            "make decisions?"
        ),
        "text_solo": (
            "What happens if you are unexpectedly unavailable — and ongoing "
            "client projects, appointments or deliveries are left without a plan B?"
        ),
        "layer": "Key persons — hazard catalog 7.2.1/7.2.2",
        "why": (
            "If decisions, payments and client relationships depend on one "
            "person, the whole business can grind to a halt when that person is "
            "absent — from missed deadlines to blocked accounts."
        ),
        "step": (
            "Define deputising rules and powers of attorney, document critical "
            "access and decision paths, and run through the emergency scenario "
            "once as a test."
        ),
    },
    {
        "id": "m2",
        "cat": "mensch",
        "short": "Knowledge loss on departure",
        "short_gruender": "Co-founder knowledge loss",
        "short_solo": "Knowledge only with you",
        "text": (
            "What happens if your most important employee leaves… and no one "
            "knows exactly what they actually did?"
        ),
        "text_gruender": (
            "What happens if a co-founder leaves… and no one knows exactly which "
            "contacts, contracts and decisions they owned?"
        ),
        "text_solo": (
            "What happens if you are out — and no one knows how your key "
            "processes, passwords and client contacts work?"
        ),
        "layer": "Knowledge transfer / turnover — hazard catalog 2.4.2, 7.2.3",
        "why": (
            "Undocumented specialist knowledge leaves the company with the "
            "person. Processes, contacts and passwords then have to be "
            "reconstructed at great cost — often in the middle of day-to-day "
            "business."
        ),
        "step": (
            "Document core tasks and specialist knowledge for each key role, "
            "introduce knowledge-transfer routines (pairing, handover protocols) "
            "and manage access credentials centrally."
        ),
    },
    {
        "id": "m3",
        "cat": "mensch",
        "short": "Team without shared direction",
        "short_gruender": "Founder team off track",
        "short_solo": "Busy, not moving forward",
        "text": (
            "What happens if your team is busy working… but not actually pulling "
            "in the same direction?"
        ),
        "text_gruender": (
            "What happens if you as founders are busy working… but not actually "
            "pulling in the same direction?"
        ),
        "text_solo": (
            "What happens if you work a lot… but not on the things that actually "
            "move your business forward?"
        ),
        "layer": "Leadership / objectives — hazard catalog 2.6.1/2.6.2",
        "why": (
            "Without clear goals and task allocation you get activity instead of "
            "progress: duplicated work, conflicting priorities and frustration "
            "that costs you good people."
        ),
        "step": (
            "Put company goals in writing, define clear responsibilities per "
            "role and align priorities in a fixed rhythm (e.g. quarterly goals)."
        ),
    },
    {
        "id": "m4",
        "cat": "mensch",
        "short": "Invisible conflicts",
        "short_gruender": "Founder team tensions",
        "short_solo": "Clients, freelancers & conflict",
        "text": (
            "What happens if conflicts in the team are not visible – but "
            "decisions keep getting slower?"
        ),
        "text_gruender": (
            "What happens if tensions between co-founders stay invisible – but "
            "decisions keep getting slower?"
        ),
        "text_solo": (
            "What happens if you are permanently overloaded, a client escalates "
            "or a freelancer drops out — and you don't address the conflict?"
        ),
        "layer": "Hidden conflicts — hazard catalog 2.5.4, 2.6.4",
        "why": (
            "Unspoken tensions slow down decisions, block information flows and "
            "often only escalate visibly when top performers resign."
        ),
        "step": (
            "Establish regular feedback formats, address conflicts actively "
            "(moderated, without blame) and relieve decision paths with clear "
            "responsibilities."
        ),
    },
    # ----- TECHNOLOGY (base) -----
    {
        "id": "t1",
        "cat": "operativ",
        "short": "Loss of trust & reputation",
        "text": (
            "What happens if clients, partners or investors lose trust in you "
            "— for example after an incident, poor communication or negative "
            "reports about you?"
        ),
        "text_solo": (
            "What happens if clients or partners lose trust in you — for example "
            "after a mistake, poor communication or negative reviews?"
        ),
        "layer": "Reputation / trust — hazard catalog 1.2, 4.4, 7.4",
        "why": (
            "Loss of trust often works more slowly than a technical outage but "
            "hits just as hard: orders slip, referrals dry up, negotiations "
            "get tougher. Without clear communication and remediation, one "
            "incident becomes a lasting image problem."
        ),
        "step": (
            "Define who speaks externally in a reputation crisis, which facts "
            "go to clients first and how you communicate transparency without "
            "panic. Keep statement and FAQ templates ready."
        ),
    },
    {
        "id": "t2",
        "cat": "technik",
        "short": "Software doesn't match growth",
        "text": (
            "What happens if your software stack (accounting, CRM, cloud storage, "
            "project tools) works today… but no longer scales with you tomorrow?"
        ),
        "text_solo": (
            "What happens if your software stack (accounting, CRM, cloud storage, "
            "project tools) works today… but no longer scales with you tomorrow?"
        ),
        "layer": "Outdated technology / digitalisation — hazard catalog 5.4.1, 5.5.2",
        "why": (
            "Systems that don't scale force expensive migrations under time "
            "pressure later — usually exactly when business is strongest and no "
            "capacity is available."
        ),
        "step": (
            "Review your tool landscape against your growth plans once a year: "
            "where are the limits (users, data volumes, interfaces)? Clarify "
            "exit and migration paths before the bottleneck."
        ),
    },
    {
        "id": "t3",
        "cat": "operativ",
        "short": "Dependence on provider, supplier & partner",
        "text": (
            "What happens if your business depends heavily on one software provider, "
            "supplier or strategic partner — and they suddenly change the rules or "
            "drop out?"
        ),
        "layer": "Provider/partner concentration — hazard catalog 1.4.3, 7.4.1",
        "why": (
            "Price increases, termination, supply stops or changed terms from a single "
            "provider, supplier or partner can hit production, delivery and revenue at "
            "the same time — with no short-term alternative."
        ),
        "step": (
            "List critical dependencies (software, suppliers, partners), check export "
            "and backup options and define at least one fallback for each top dependency."
        ),
    },
    # ----- OPERATIONS (base) -----
    {
        "id": "o1",
        "cat": "operativ",
        "short": "Dependence on your biggest client",
        "text": (
            "What happens if your biggest client walks away – and you realise "
            "how dependent you really are?"
        ),
        "layer": "Client concentration risk — hazard catalog 7.4.1, 4.4",
        "why": (
            "If a single client accounts for a large share of revenue, their "
            "budget round decides your liquidity. Losing them hits revenue and "
            "planning at the same time — often without warning."
        ),
        "step": (
            "Make revenue shares per client transparent, actively diversify "
            "from around 25 % dependence and run the numbers on a 'top client "
            "leaves' scenario including a liquidity reserve."
        ),
    },
    {
        "id": "o2",
        "cat": "operativ",
        "short": "Processes depend on you",
        "short_kmu": "Wrong advice",
        "text": (
            "What happens if your processes only work as long as you personally "
            "keep an eye on everything?"
        ),
        "text_kmu": (
            "What happens if you turn to the wrong advisers for important decisions "
            "— tax advisers, lawyers or consultants — and lose time, money and "
            "sometimes even more money through bad advice?"
        ),
        "layer": "Process dependence — hazard catalog 5.5.3, 7.2.1",
        "why": (
            "Processes that only work under constant owner supervision don't "
            "scale and turn every holiday or absence into a risk. Mistakes only "
            "surface once they have become expensive."
        ),
        "step": (
            "Standardise your three most important workflows in writing "
            "(checklists, clear quality criteria) and delegate responsibility "
            "including decision-making authority."
        ),
    },
    {
        "id": "o3",
        "cat": "operativ",
        "short": "Chain reaction of small problems",
        "text": (
            "What happens if several small problems suddenly occur at once – "
            "and reinforce each other?"
        ),
        "layer": "Missing contingency planning / redundancy — hazard catalog 3.1, 1.4.3",
        "why": (
            "Individually manageable disruptions — a sick employee, a late "
            "delivery, an IT problem — can compound into a chain when buffers "
            "and a plan B are missing."
        ),
        "step": (
            "Define simple plan-B answers for your most critical workflows (who "
            "takes over, what gets paused, where is the buffer) and mentally "
            "rehearse one incident per year."
        ),
    },
    # ----- STARTUP / FOUNDERS (extension) -----
    {
        "id": "s1",
        "cat": "wachstum",
        "short": "Structures don't grow with you",
        "text": (
            "What happens if you scale… but your structures don't grow with you?"
        ),
        "layer": "Organisation / processes — hazard catalog 5.5, 2.6.1",
        "why": (
            "Growth without growing structures creates friction everywhere: "
            "unclear responsibilities, quality problems and managers who only "
            "fight fires instead of steering."
        ),
        "step": (
            "Before the next growth step, clarify roles, responsibilities and "
            "core processes in writing — and standardise onboarding before the "
            "next hires arrive."
        ),
    },
    {
        "id": "s2",
        "cat": "wachstum",
        "short": "Unprepared investor questions",
        "text": (
            "What happens if investors ask questions you have never asked "
            "yourselves?"
        ),
        "layer": "Strategy / performance monitoring — hazard catalog 7.3, 3.5",
        "why": (
            "In due diligence, unanswered risk and structure questions decide "
            "valuation and closing. If you discover risks only in the data "
            "room, you negotiate from the back foot."
        ),
        "step": (
            "Review your own company from an investor's perspective once: "
            "document dependencies, contracts, key figures and risks cleanly "
            "before the questions come from outside."
        ),
    },
    {
        "id": "s3",
        "cat": "wachstum",
        "short": "Market faster than product",
        "text": (
            "What happens if your market changes faster than your product?"
        ),
        "layer": "Market / innovation — hazard catalog 5.4.2, 7.4.2",
        "why": (
            "If customer behaviour, competition or technology change faster "
            "than your roadmap, a head start quietly turns into a deficit — "
            "visible only once the pipeline dries up."
        ),
        "step": (
            "Introduce market and competitor monitoring as a fixed rhythm "
            "(quarterly review) and test the product roadmap regularly against "
            "real customer signals instead of internal assumptions."
        ),
    },
    {
        "id": "s4",
        "cat": "wachstum",
        "short": "False core assumptions",
        "text": (
            "What happens if your business model is built on assumptions that "
            "suddenly turn out to be wrong?"
        ),
        "layer": "Strategic assumptions — hazard catalog 7.3.1, 5.4.2",
        "why": (
            "Business models often rest on a few untested core assumptions — "
            "about willingness to pay, regulation or key partners. If one "
            "tips, the model tips."
        ),
        "step": (
            "Name your three most critical core assumptions, define an early "
            "warning signal for each and run a pre-mortem: 'Assume we fail in "
            "two years — what was the cause?'"
        ),
    },
    {
        "id": "s5",
        "cat": "wachstum",
        "short": "Decisions under growth pressure",
        "text": (
            "What happens if growth forces you to make decisions you are not "
            "ready for yet?"
        ),
        "layer": "Leadership / decision structure — hazard catalog 7.2.2, 2.6",
        "why": (
            "Under growth pressure, fundamental decisions — hiring, funding, "
            "locations — are often made ad hoc. Wrong decisions in this phase "
            "have effects lasting years."
        ),
        "step": (
            "Define a simple framework for big decisions (worst-case "
            "affordability, reversibility, second opinion) and clarify decision "
            "authority in advance."
        ),
    },
    # ----- SME (extension) -----
    {
        "id": "k1",
        "cat": "markt",
        "short": "Market turning quietly",
        "text": (
            "What happens if your business has run stably for years… but the "
            "market quietly turns against you?"
        ),
        "layer": "Market change — hazard catalog 4.4.3/4.4.4, 7.4.2",
        "why": (
            "Gradual changes — new competitors, shifting customer behaviour, "
            "substitutes — are invisible in stable day-to-day business. By the "
            "time the numbers show them, the others' head start is real."
        ),
        "step": (
            "Run an honest market and competitor analysis once a year: who is "
            "winning our target customers right now, and why? Continuously "
            "monitor early indicators (enquiries, conversion rates)."
        ),
    },
    {
        "id": "k2",
        "cat": "markt",
        "short": "Strength tied to individuals",
        "text": (
            "What happens if your company is strong – but only as long as "
            "certain people are there?"
        ),
        "layer": "Key persons / succession — hazard catalog 7.2, 7.1",
        "why": (
            "Client relationships, specialist knowledge and decision-making "
            "power tied to individuals are a double risk: in daily operations "
            "(illness, resignation) and in succession or a sale."
        ),
        "step": (
            "Name critical person dependencies, organise deputies and knowledge "
            "transfer and — where the owner is the dependency — start "
            "succession planning early."
        ),
    },
    {
        "id": "k3",
        "cat": "markt",
        "short": "Legacy processes without overview",
        "text": (
            "What happens if your processes have grown historically… and no one "
            "really has the full picture any more?"
        ),
        "layer": "Outdated business processes — hazard catalog 3.6.3, 5.5.3",
        "why": (
            "Historically grown workflows hide duplicated work, single-person "
            "dependencies and compliance gaps. Every change — new software, new "
            "employees, certification — becomes expensive and risky as a result."
        ),
        "step": (
            "Map the core processes end to end once (who does what, with what, "
            "why), remove obvious legacy clutter and assign an owner per "
            "process."
        ),
    },
    {
        "id": "k4",
        "cat": "markt",
        "short": "Creeping cost pressure",
        "text": (
            "What happens if rising costs slowly squeeze the air out of your "
            "business without anyone noticing at first?"
        ),
        "layer": "Financial planning — hazard catalog 3.5, 4.3.2, 5.5.1",
        "why": (
            "Energy, wages, purchasing, interest: if costs rise faster than "
            "prices, margins melt unnoticed. Without a liquidity reserve, a "
            "margin problem becomes a payment problem."
        ),
        "step": (
            "Track cost and margin development monthly per service/product, "
            "review pricing annually and build a liquidity reserve as a fixed "
            "item."
        ),
    },
    {
        "id": "k5",
        "cat": "markt",
        "short": "Unprepared for external shocks",
        "text": (
            "What happens if an external change arrives – and you realise you "
            "were never prepared for it?"
        ),
        "layer": "Environment / regulation / contingency planning — hazard catalog 4.1, 6, 3.1",
        "why": (
            "New laws, supply-chain breaks, natural events or geopolitical "
            "shocks hit unprepared companies with full force — prepared "
            "companies lose days, unprepared ones lose months."
        ),
        "step": (
            "Name the three most relevant external scenarios for your industry "
            "and create a one-page contingency plan per scenario: first steps, "
            "responsibilities, communication."
        ),
    },
    {
        "id": "k6",
        "cat": "mensch",
        "short": "Skills shortage",
        "text": (
            "What happens if you urgently need skilled staff — and roles stay "
            "unfilled for months or overtime is the only answer left?"
        ),
        "layer": "Workforce / recruiting — hazard catalog 2.4, 7.2.3",
        "why": (
            "Unfilled key roles delay projects, overload the existing team and "
            "drive wage costs. If you only react once a role has been open for "
            "months, you often lose internal know-how and sometimes client trust."
        ),
        "step": (
            "Prioritise the most critical open roles, define realistic requirements "
            "and a lean hiring process. Consider upskilling, freelancers or "
            "partnerships as a bridge."
        ),
    },
    {
        "id": "l1",
        "cat": "markt",
        "short": "Market turns quietly",
        "text": (
            "What happens if your business has been stable for years… but the "
            "market is quietly turning against you?"
        ),
        "layer": "Market change — hazard catalog 4.4.3/4.4.4, 7.4.2",
        "why": (
            "Gradual changes — new competitors, shifting client behaviour, "
            "substitutes — stay invisible in day-to-day work. By the time the "
            "numbers show it, others already have the lead."
        ),
        "step": (
            "Once a year, ask honestly: who is winning your target clients and "
            "why? Track early indicators (inquiries, conversion rates) monthly."
        ),
    },
    {
        "id": "l2",
        "cat": "markt",
        "short": "Everything depends on you",
        "text": (
            "What happens if your business only runs while you — or a single "
            "subcontractor — are available?"
        ),
        "layer": "Key persons — hazard catalog 7.2, 7.1",
        "why": (
            "Client relationships, specialist knowledge and decisions that hang "
            "on one person become a bottleneck when illness, holiday or "
            "freelancer absence hits."
        ),
        "step": (
            "Name critical dependencies in writing, document knowledge and "
            "identify backup partners for important freelancers."
        ),
    },
    {
        "id": "l3",
        "cat": "markt",
        "short": "Grown processes without overview",
        "text": (
            "What happens if your workflows grew over time… and even you lose "
            "the overview?"
        ),
        "layer": "Outdated business processes — hazard catalog 3.6.3, 5.5.3",
        "why": (
            "Historically grown routines hide duplicated work and single points "
            "of failure. Every new tool or major client gets more expensive when "
            "no one knows the thread."
        ),
        "step": (
            "Write down your three most important workflows end to end, cut "
            "obvious legacy steps and create a short checklist per workflow."
        ),
    },
    {
        "id": "l4",
        "cat": "markt",
        "short": "Creeping cost pressure",
        "text": (
            "What happens if rising costs slowly squeeze you without it being "
            "obvious at first?"
        ),
        "layer": "Financial planning — hazard catalog 3.5, 4.3.2, 5.5.1",
        "why": (
            "Energy, software, purchases, taxes: if costs rise faster than your "
            "prices, margin erodes unnoticed. Without a reserve, a margin "
            "problem becomes a cash-flow problem."
        ),
        "step": (
            "Track costs and margin monthly per service, review prices annually "
            "and build a liquidity reserve as a fixed item."
        ),
    },
    {
        "id": "l5",
        "cat": "markt",
        "short": "Unprepared for external shocks",
        "text": (
            "What happens if an external change arrives — and you realise you "
            "were never prepared for it?"
        ),
        "layer": "Environment / regulation / contingency — hazard catalog 4.1, 6, 3.1",
        "why": (
            "Regulation, supply chains or market shocks hit unprepared "
            "self-employed professionals with full force — prepared ones lose "
            "days, unprepared ones lose months."
        ),
        "step": (
            "Name the three most relevant external scenarios for your industry "
            "and create a one-page contingency plan per scenario."
        ),
    },
    {
        "id": "tt1",
        "cat": "top_themen",
        "short": "Phishing, hacking & AI attacks",
        "text": (
            "What happens if someone on your team — or via your AI workflows — "
            "gains access to systems or data through phishing, hacking, malicious "
            "images or prompt injection — and no one knows what to do immediately?"
        ),
        "text_solo": (
            "What happens if you or your AI tools lose access to systems or data "
            "through phishing, hacking, malicious images or prompt injection — "
            "and you don't know what to do immediately?"
        ),
        "layer": "Cyber / social engineering / AI — hazard catalog 1.1.2, RA Z1",
        "why": (
            "Phishing and AI-based attacks hit individuals and teams alike. "
            "Without training, reporting channels and rules for AI workflows, "
            "one click or manipulated prompt can mean data loss or account "
            "lockout."
        ),
        "step": (
            "Annual phishing awareness, two-factor authentication for email and "
            "cloud, clear AI rules (no real client data in public tools) and a "
            "one-page emergency plan."
        ),
    },
    {
        "id": "tt2",
        "cat": "top_themen",
        "short": "Liquidity reserve",
        "text": (
            "What happens if you urgently need money — and neither personal nor "
            "company reserves are sufficient?"
        ),
        "text_solo": (
            "What happens if you urgently need money — and neither personal nor "
            "business reserves are sufficient?"
        ),
        "layer": "Liquidity / reserves — hazard catalog 3.5, 4.3.2",
        "why": (
            "Without personal and business reserves, every unexpected bill, "
            "downtime or investment need becomes an existential risk — "
            "especially when revenue fluctuates or payments are delayed."
        ),
        "step": (
            "Maintain a monthly liquidity overview, define a target reserve "
            "(e.g. 3 months fixed costs) and document the private/business split."
        ),
    },
    {
        "id": "tt3",
        "cat": "top_themen",
        "short": "Privacy & AI law",
        "text": (
            "What happens if legal topics — data protection, AI regulation, "
            "contracts — burden you even though you've been putting them off?"
        ),
        "text_solo": (
            "What happens if legal topics — data protection, AI use, contracts — "
            "burden you even though you've been putting them off?"
        ),
        "layer": "Law / GDPR / AI Act — hazard catalog 6, RA Z4",
        "why": (
            "Data protection breaches and unclear AI use can trigger fines, "
            "contract penalties and reputational damage. What 'works' day to "
            "day often won't survive client or authority scrutiny."
        ),
        "step": (
            "Check data protection basics (processing records, DPAs), document "
            "AI use and get external advice on your biggest legal risks."
        ),
    },
]

apply_report_content(QUESTIONS)

# ---------------------------------------------------------------------------
# Audience sets (17 questions each: 10 base + ACTIVE_TOP_THEMEN + 5 extension)
# ---------------------------------------------------------------------------

SEGMENTS: list[dict] = [
    {
        "id": "gruender",
        "label": "Founders & startups",
        "cta": "Start the Blindspot Check for founders",
        "question_ids": _BASE_IDS + ACTIVE_TOP_THEMEN + ["s1", "s2", "s3", "s4", "s5"],
    },
    {
        "id": "solo",
        "label": "Solo self-employed",
        "cta": "Start the Blindspot Check for solo self-employed",
        "question_ids": _BASE_IDS + ACTIVE_TOP_THEMEN + ["l1", "l2", "l3", "l4", "l5"],
    },
    {
        "id": "kmu",
        "label": "Small & medium-sized enterprises",
        "cta": "Start the Blindspot Check for SMEs",
        "question_ids": _BASE_IDS + ACTIVE_TOP_THEMEN + ["k1", "k2", "k3", "k4", "k5", "k6"],
    },
]

QUESTIONS_PER_PAGE = 5

# ---------------------------------------------------------------------------
# UI strings (screens)
# ---------------------------------------------------------------------------

UI_STRINGS: dict = {
    "intro_headline": "Find your entrepreneurial blind spots",
    "intro_note": (
        "Important: This quick check is not a full risk analysis. It covers a "
        "selection from more than 100 possible hazard areas of our 3-level "
        "hazard catalog. Even if all questions come back uncritical, that does "
        "not automatically mean the remaining risks pose no danger. Answer the "
        "questions honestly to get a relevant result."
    ),
    "start_button": "Start the Blindspot Quick Check",
    "segment_headline": "Which situation describes you best?",
    "segment_text": (
        "So the questions fit your situation better, please choose the category "
        "that applies to you most closely."
    ),
    "howto_headline": "How the Blindspot Quick Check works",
    "howto_text": (
        "You answer short 'What happens if …' questions about typical "
        "entrepreneurial blind spots. For each question, you rate how critical "
        "the scenario would be for you — and whether you have already prepared "
        "concrete measures for it. The check only takes a few minutes. At the "
        "end you receive a compact evaluation with an assessment of your "
        "current risk profile."
    ),
    "howto_note": (
        "This quick check does not replace a full risk analysis. It looks at "
        "selected risks from a much larger hazard catalog. A good result "
        "therefore does not mean that all conceivable risks are ruled out."
    ),
    "howto_button": "Start the questions now",
    "howto_count_template": "{count} questions — {segment}.",
    "severity_question": "How critical would this scenario be for you?",
    "progress_template": "Question {from}–{to} of {total}",
    "back": "Back",
    "next": "Next",
    "evaluate": "Start evaluation",
    "loading_headline": "Please wait a moment. Your analysis is being carried out.",
    "loading_text": (
        "Your answers are being evaluated and your personal Blindspot Quick "
        "Check is being created. This may take a few seconds — thank you for "
        "your patience."
    ),
    "result_headline": "Your Blindspot Quick Check results",
    "result_thanks": (
        "Thank you for taking part in our Blindspot Quick Check and for the "
        "trust you have placed in us."
    ),
    "result_disclaimer": (
        "This analysis is a quick check. It covers only a selection from more "
        "than 100 possible risk questions. Even a good result does not "
        "automatically mean that no further risks exist."
    ),
    "result_categories_title": "Your areas at a glance",
    "result_red_title": "Your critical blind spots",
    "result_red_why": "Why critical:",
    "result_red_step": "First step:",
    "result_no_red": (
        "No acutely critical blind spots in the areas covered — still review "
        "the points marked yellow."
    ),
    "cta_booking": "Book a call directly",
    "cta_booking_sub": (
        "Find out in a personal conversation how to carry out a full risk "
        "analysis in your company."
    ),
    "cta_report": "Get the full report",
    "report_headline": "Receive your full Blindspot report by email",
    "report_text": (
        "Enter your details so we can send you your full report as a PDF by "
        "email."
    ),
    "report_salutation": "Title",
    "report_salutation_choose": "Please select",
    "report_salutation_herr": "Mr",
    "report_salutation_frau": "Ms",
    "report_first_name": "First name",
    "report_last_name": "Last name",
    "report_email": "Email address",
    "report_company": "Company (optional)",
    "report_privacy": (
        "I agree that my details will be processed to create and send my "
        "Blindspot report. More information in the privacy policy."
    ),
    "report_newsletter": (
        "I would also like to receive the Beraterium newsletter and can "
        "unsubscribe at any time."
    ),
    "report_submit": "Request report",
    "report_sending_headline": "Please wait — your report is being created",
    "report_sending_text": (
        "Your personal PDF report is being generated and will be sent to you "
        "by email. This may take a moment."
    ),
    "report_sending_hint": (
        "Please do not close or refresh this page, and do not click "
        "“Request report” again."
    ),
    "report_success": (
        "Thank you! Your report has been created and sent to your email address. "
        "Please also check your spam folder."
    ),
    "report_email_failed": (
        "Your PDF report was created, but the email could not be sent right now. "
        "Please try again in a few minutes or contact us via the contact form."
    ),
    "report_error_pdf": (
        "Your PDF report could not be created right now. Please try again in a "
        "few minutes or contact us via the contact form."
    ),
    "report_error_validation": (
        "Please fill in title, name, email, and agree to the privacy policy."
    ),
    "report_error": (
        "Your request could not be submitted right now. Please try again later "
        "or contact us via the contact form."
    ),
    "report_unavailable": (
        "The PDF report will be available shortly. Feel free to book a call "
        "directly — we will go through your results together."
    ),
    "validation_salutation": "Please select a title.",
    "validation_required": "Please fill in this field.",
    "validation_email": "Please enter a valid email address.",
    "validation_privacy": "Please agree to the privacy policy.",
    "validation_answer": "Please answer both parts of the question.",
    "restart": "Restart the check",
}


# ---------------------------------------------------------------------------
# Frontend configuration
# ---------------------------------------------------------------------------

_FRONTEND_QUESTION_KEYS = (
    "id",
    "cat",
    "short",
    "text",
    "why",
    "step",
    "short_gruender",
    "short_solo",
    "text_gruender",
    "text_solo",
    "why_gruender",
    "why_solo",
    "step_gruender",
    "step_solo",
)

def blindspot_frontend_config(
    *,
    locale: str = "en",
    submit_url: str = "",
    report_url: str = "",
    booking_url: str = "contact/",
    privacy_url: str = "privacy/",
) -> dict:
    """Complete configuration for js/brt-blindspot.js (embedded as inline
    JSON). URLs relative to the page or absolute."""
    return {
        "locale": locale,
        "submitUrl": submit_url,
        "reportUrl": report_url,
        "bookingUrl": booking_url,
        "privacyUrl": privacy_url,
        "likert": LIKERT,
        "measureQuestion": MEASURE_QUESTION,
        "measureOptions": MEASURE_OPTIONS,
        "maxPointsPerQuestion": MAX_POINTS_PER_QUESTION,
        "trafficLight": TRAFFIC_LIGHT,
        "resultBands": RESULT_BANDS,
        "categories": CATEGORIES,
        "questions": [
            {k: q[k] for k in _FRONTEND_QUESTION_KEYS if k in q}
            for q in QUESTIONS
        ],
        "segments": SEGMENTS,
        "questionsPerPage": QUESTIONS_PER_PAGE,
        "strings": UI_STRINGS,
    }


def blindspot_config_json(**kwargs) -> str:
    return json.dumps(blindspot_frontend_config(**kwargs), ensure_ascii=False)


# ---------------------------------------------------------------------------
# Selfcheck (called by the build)
# ---------------------------------------------------------------------------

# ponytail: SME has 18 questions (k6 skills shortage), founders/solo 17 each
_SEGMENT_QUESTION_COUNTS: dict[str, int] = {
    "gruender": 17,
    "solo": 17,
    "kmu": 18,
}

def selfcheck() -> None:
    ids = [q["id"] for q in QUESTIONS]
    assert len(ids) == len(set(ids)), "Blindspot: question ids not unique"
    for qid in ACTIVE_TOP_THEMEN:
        assert qid in ids, f"Blindspot: ACTIVE_TOP_THEMEN references unknown {qid}"
    for q in QUESTIONS:
        for key in ("id", "cat", "short", "text", "layer", "why", "step", "yellow_note"):
            assert q.get(key), f"Blindspot: question {q.get('id', '?')} missing '{key}'"
        tips = q.get("tips")
        assert isinstance(tips, list) and len(tips) >= 2, (
            f"Blindspot: question {q.get('id', '?')} needs at least 2 tips"
        )
        assert q["cat"] in CATEGORIES, f"Blindspot: unknown category {q['cat']}"
    for seg in SEGMENTS:
        unknown = [qid for qid in seg["question_ids"] if qid not in ids]
        assert not unknown, f"Blindspot: segment {seg['id']} references {unknown}"
        assert len(seg["question_ids"]) == len(set(seg["question_ids"]))
        assert len(seg["question_ids"]) == _SEGMENT_QUESTION_COUNTS[seg["id"]], (
            f"Blindspot: segment {seg['id']} needs "
            f"{_SEGMENT_QUESTION_COUNTS[seg['id']]} questions, "
            f"has {len(seg['question_ids'])}"
        )
    assert RESULT_BANDS[-1]["max_pct"] == 100


if __name__ == "__main__":
    selfcheck()
    print(f"OK - {len(QUESTIONS)} questions, {len(SEGMENTS)} segments")
