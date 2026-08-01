"""PDF report copy for the Blindspot Quick Check (EN).

Sources: Risikoschnüffler method (offers / book), 3-level hazard catalog.
For the email PDF report only — not shown in the web result.
"""
from __future__ import annotations

GENERAL_RISK_TIPS: list[dict] = [
    {
        "title": "Start with people, not spreadsheets",
        "text": (
            "Good risk analysis comes from dialogue inside the business, not from "
            "complex spreadsheets alone. Invite people who know different areas — "
            "sales, finance, IT, production. Assess risks, not people. Individual "
            "views become a shared, reliable picture."
        ),
        "tips": [
            "Plan a 60–90 minute conversation with 3–5 people from different areas.",
            "Ask 'What happens if …?' questions instead of looking for blame.",
            "Record only facts and scenarios — no naming individuals when discussing weaknesses.",
        ],
        "text_solo": (
            "Even without a team, a structured outside view pays off: accountant, "
            "IT provider, mentor or a trusted colleague from your network will see "
            "blind spots you miss in day-to-day work. Assess risks, not people — "
            "individual views become a reliable picture."
        ),
        "tips_solo": [
            "Plan a 60–90 minute conversation with 2–3 external trusted contacts (accountant, IT, mentor).",
            "Ask 'What happens if …?' questions — even alone, in writing as a thought experiment.",
            "Record only facts and scenarios — no blame.",
        ],
    },
    {
        "title": "Use your inventory: what do you already have?",
        "text": (
            "Before planning new measures, capture what is already in place: "
            "insurance, contracts, backups, deputising rules, emergency contacts. "
            "Many businesses underestimate existing protection — or discover gaps "
            "exactly where nobody owns responsibility."
        ),
        "tips": [
            "List all policies, SLAs and maintenance contracts with expiry dates in one table.",
            "For each safeguard, check: who knows it, who triggers it in an emergency, when was it last tested?",
            "Mark gaps in red — that is where the next concrete step should go first.",
        ],
    },
    {
        "title": "Prioritise: not everything at once",
        "text": (
            "Spotting the few decisive risks among many possibilities is the core "
            "task. A risk portfolio sorted by impact and urgency stops you getting "
            "lost in individual topics. Start with the red points from this check, "
            "then the yellow ones."
        ),
        "tips": [
            "Choose at most three topics for the next 90 days — no more.",
            "For each topic, ask: what would the damage cost if it happened? What does protection cost?",
            "Assign one responsible person and a review date for each top risk.",
        ],
        "tips_solo": [
            "Choose at most three topics for the next 90 days — no more.",
            "For each topic, ask: what would the damage cost me if it happened? What does protection cost?",
            "Put a review date in your calendar for each top risk — you own the responsibility.",
        ],
    },
    {
        "title": "Think in pounds and euros, not just traffic lights",
        "text": (
            "Red, yellow and green give orientation. For decisions you need "
            "magnitude: what does an outage roughly cost? How likely is it? Even "
            "rough estimates (ranges) improve priorities significantly compared "
            "with gut feeling alone."
        ),
        "tips": [
            "For each critical scenario, estimate: damage per week of outage × probability per year.",
            "Compare measure costs with expected damage, not with fear.",
            "Document assumptions in writing so the team can follow up later.",
        ],
        "tips_solo": [
            "For each critical scenario, estimate: damage per week of outage × probability per year.",
            "Compare measure costs with expected damage, not with fear.",
            "Document assumptions in writing — for your accountant, bank or later decisions.",
        ],
    },
    {
        "title": "Rhythm, not a one-off",
        "text": (
            "Risks change with growth, people, market and technology. A one-off "
            "check is not enough. Set a fixed rhythm — e.g. review top risks "
            "quarterly, and take a broader view with the team annually."
        ),
        "text_solo": (
            "Risks change with workload, market and technology. A one-off check "
            "is not enough. Set a fixed rhythm — e.g. review your top risks "
            "quarterly, and take a broader view with your accountant or mentor "
            "annually."
        ),
        "tips": [
            "Block half a day per quarter for risk review in the calendar.",
            "Update immediately after major changes (new client, new hire, new software).",
            "Use this quick check as a starting point — the full analysis goes deeper across all areas.",
        ],
        "tips_solo": [
            "Block half a day per quarter for risk review in the calendar.",
            "Update immediately after major changes (new client, new tool, new supplier).",
            "Use this quick check as a starting point — the full analysis goes deeper across all areas.",
        ],
    },
    {
        "title": "Next step: full risk analysis",
        "text": (
            "This report covers a selection from more than 100 hazard areas. For "
            "robust decisions and a prioritised action programme we recommend "
            "Beraterium's risk analysis with the full 3-level hazard catalog — "
            "structured, valued in monetary terms, with your team."
        ),
        "tips": [
            "Book a free intro call — we will go through your red points in detail.",
            "Bring this report with you — it is a good starting point for going deeper.",
        ],
    },
]

REPORT_BY_ID: dict[str, dict] = {
    "m1": {
        "why": (
            "If decisions, payments, client relationships and access depend on one "
            "person, the whole operation can stop quickly when that person is "
            "absent. Missed deadlines, blocked accounts and unanswered client "
            "enquiries often follow within days, not weeks. It becomes especially "
            "critical when there is no written deputising arrangement, no powers of "
            "attorney and no tested emergency plan."
        ),
        "step": (
            "Put in writing who makes which decisions from when (deputising rules). "
            "Document critical access in a password vault with at least two "
            "authorised people and run through the absence scenario once as a "
            "test — without you."
        ),
        "tips": [
            "Give a trusted person a notarised power of attorney for bank and authorities.",
            "Keep an emergency checklist ready: top 5 clients, open invoices, active contracts.",
            "Review your disability and key-person insurance for appropriate cover levels.",
        ],
        "yellow_note": (
            "Without documented deputising, a short absence quickly becomes an "
            "existential risk once payments, deliveries or approvals depend on you."
        ),
    },
    "m2": {
        "why": (
            "Undocumented specialist knowledge leaves the business with the person. "
            "Processes, client contacts, passwords and informal agreements then "
            "have to be reconstructed under time pressure — often in the middle of "
            "day-to-day business. The more critical the role, the more expensive "
            "the loss — especially when there is no handover protocol and no "
            "succession planning."
        ),
        "step": (
            "Identify the three most important key roles and document core tasks, "
            "contacts, systems and decision limits for each. Introduce pairing or "
            "monthly knowledge-exchange sessions and centralise all access "
            "credentials."
        ),
        "tips": [
            "Agree a written handover period for every hire in a key role.",
            "Use short video or text guides for recurring specialist tasks.",
            "Review competition and confidentiality clauses in employment contracts.",
        ],
        "tips_solo": [
            "Document your most important workflows monthly — even as a short checklist.",
            "Use video or text guides for recurring specialist tasks.",
            "Name a trusted person who can access your records in an emergency.",
        ],
        "yellow_note": (
            "An unplanned departure becomes critical as soon as only one person "
            "runs a system, a major client or a supplier alone."
        ),
    },
    "m3": {
        "why": (
            "Without clear goals and task allocation you get activity instead of "
            "progress. Duplicated work, conflicting priorities and frustration "
            "cost you good people and delay decisions at leadership level. Growth "
            "amplifies the problem: the more people, the more expensive missing "
            "alignment becomes."
        ),
        "step": (
            "Write down three company goals for the next 12 months and derive "
            "clear responsibility per role. Introduce a monthly 30-minute "
            "alignment (goals, priorities, blockers)."
        ),
        "tips": [
            "Link every major task to a goal — cut or delegate tasks with no goal link.",
            "Use a simple RACI (Responsible/Accountable) for your five most important processes.",
            "Ask the team anonymously: 'What are we working on that nobody needs?'",
        ],
        "tips_solo": [
            "Write down three personal business goals for 12 months.",
            "Review weekly: which task drives revenue or security, and what is just busywork?",
            "Block 30 minutes per month in the calendar for a priorities review.",
        ],
        "step_solo": (
            "Write down three business goals for the next 12 months and align your "
            "most important tasks with them. Review monthly whether you are "
            "working towards the goals or just reacting."
        ),
        "yellow_note": (
            "When unclear direction turns into permanent friction, top performers "
            "leave and growth slows — even though there are more people."
        ),
    },
    "m4": {
        "why": (
            "Unspoken tensions slow decisions and block information flows. "
            "Conflicts often only become visible when top performers resign or "
            "projects stall. In small teams this escalates quickly because every "
            "delay hits revenue directly."
        ),
        "step": (
            "Establish a fixed feedback format (e.g. monthly, moderated). Clarify "
            "decision paths in writing: who decides what by when? Moderate early "
            "when tension is visible — without blame."
        ),
        "tips": [
            "Separate factual and relational levels explicitly in conflict conversations.",
            "For founder teams, bring in external moderation when needed.",
            "Document decisions briefly — that reduces later reinterpretation.",
        ],
        "tips_solo": [
            "Address tension with clients or partners early — not only when it escalates.",
            "For difficult decisions, use an external sparring partner (mentor, adviser).",
            "Document decisions briefly — that reduces later overthinking.",
        ],
        "step_solo": (
            "Plan a fixed feedback conversation with a trusted person (mentor, "
            "accountant, industry peer). Clarify decision paths in writing: what "
            "do you decide alone, and where do you seek input?"
        ),
        "yellow_note": (
            "Slow decisions are often the first warning sign before resignations follow."
        ),
    },
    "t1": {
        "why": (
            "A cyber attack hits twice: first systems and data fail, then the trust "
            "of clients and partners suffers. Reporting duties (e.g. GDPR within "
            "72 hours), compensation claims and reputational damage can become an "
            "existential question without backups, reporting channels and a "
            "communication plan — especially when payments or client data are "
            "affected."
        ),
        "step": (
            "Set up automatic, tested backups (trial restore once per quarter). "
            "Enforce two-factor authentication for email, cloud and banking. "
            "Create a one-page emergency plan: who reports what, to whom, in what "
            "order."
        ),
        "tips": [
            "Train all staff annually on phishing — one click is enough.",
            "Review cyber insurance and whether your IT provider has incident response defined.",
            "Keep offline contact details for lawyer, IT and insurer to hand.",
        ],
        "tips_solo": [
            "Train yourself annually on phishing and secure passwords — one click is enough.",
            "Review cyber insurance and whether your IT provider has incident response defined.",
            "Keep offline contact details for lawyer, IT and insurer to hand.",
        ],
        "yellow_note": (
            "Without a tested backup, every attack quickly becomes data loss with "
            "long downtime — even for seemingly small incidents."
        ),
    },
    "t2": {
        "why": (
            "Systems that do not scale force expensive migrations under time "
            "pressure later — usually when business is strongest. User limits, "
            "missing integrations and outdated software slow scaling and quality. "
            "The bottleneck often only shows when a new major client or a new "
            "compliance requirement arrives."
        ),
        "step": (
            "Review your tool landscape against your growth plan once a year: "
            "users, data volumes, integrations, costs. Document an exit or "
            "migration path for each core system before the bottleneck appears."
        ),
        "tips": [
            "Export critical data monthly to an open format (CSV, JSON).",
            "When renewing contracts, compare at least one alternative.",
            "Plan migration budget and capacity like a normal project — not ad hoc.",
        ],
        "yellow_note": (
            "Growth without a tool review typically ends in expensive emergency "
            "migrations in the middle of the peak phase."
        ),
    },
    "t3": {
        "why": (
            "Price increases, feature changes or account suspension by a single "
            "provider can hit operations, data and client access at the same time. "
            "Without a fallback you depend on a third party's goodwill and terms — "
            "for cloud, payment, shop or communication, often overnight."
        ),
        "step": (
            "List all critical SaaS/cloud services with monthly costs, data owner "
            "and export options. Back up exportable data weekly and define at "
            "least one alternative for each top-3 service."
        ),
        "tips": [
            "Avoid one provider controlling email, files and authentication at the same time.",
            "Read terms changes, notice periods and data portability with intent.",
            "Test data export every quarter — not only when cancelling.",
        ],
        "yellow_note": (
            "Single-provider lock-in becomes critical as soon as prices rise or "
            "the account is suspended without warning."
        ),
    },
    "o1": {
        "why": (
            "If a single client accounts for a large share of revenue, their "
            "budget or switch decides your liquidity. Losing them hits revenue, "
            "planning and often team morale at the same time — frequently without "
            "warning. From around 25% revenue share we speak of concentration risk "
            "that needs active management."
        ),
        "step": (
            "Make revenue share per client transparent (top-5 list). Run a "
            "'biggest client leaves' scenario including a liquidity reserve. "
            "Start active diversification from 25% dependence."
        ),
        "tips": [
            "Maintain at least two independent acquisition channels in parallel.",
            "Negotiate longer terms with major clients only in exchange for fairer conditions.",
            "Build a liquidity reserve equal to 2–3 months of fixed costs.",
        ],
        "yellow_note": (
            "High dependence becomes critical as soon as the client hesitates to "
            "pay or negotiations over terms begin."
        ),
    },
    "o2": {
        "why": (
            "Processes that only work under constant owner supervision do not "
            "scale. Every holiday or absence becomes a risk; mistakes only surface "
            "once they are expensive. The business stays tied to you — a structural "
            "problem for growth, sale and succession."
        ),
        "step": (
            "Standardise your three most important workflows in writing (checklists, "
            "quality criteria, escalation). Delegate responsibility including clear "
            "decision-making authority and review implementation after two weeks."
        ),
        "tips": [
            "Record workflows once with an external person — questions reveal gaps.",
            "Define 'definition of done' for each core process in three bullet points.",
            "Measure: can you take two weeks' holiday without quality dropping?",
        ],
        "tips_solo": [
            "Write your three most important workflows as a checklist, step by step.",
            "Define 'definition of done' for each core process in three bullet points.",
            "Measure: can you be away for a week without clients noticing?",
        ],
        "step_solo": (
            "Standardise your three most important workflows in writing (checklists, "
            "quality criteria). Assign recurring parts to freelancers or tools, "
            "with a clear brief."
        ),
        "yellow_note": (
            "As long as you have to co-decide everywhere, the business does not "
            "scale — and every absence becomes a bottleneck."
        ),
    },
    "o3": {
        "why": (
            "Individually manageable disruptions — a sick employee, a late "
            "delivery, an IT outage — compound when buffers and plan B are "
            "missing. In lean organisations the chain collapses quickly because "
            "there is no redundancy."
        ),
        "step": (
            "Define plan B for your three most critical workflows: who takes over, "
            "what gets paused, where is the buffer (time, money, spare parts). "
            "Mentally rehearse one incident per year."
        ),
        "tips": [
            "Keep a list of critical backup suppliers — not only the main supplier.",
            "Set an emergency budget in writing (e.g. 5% of fixed costs).",
            "Communicate clearly in the team: who calls whom when two things break at once?",
        ],
        "tips_solo": [
            "Keep a list of critical backup suppliers — not only the main supplier.",
            "Set an emergency budget in writing (e.g. 5% of fixed costs).",
            "Note emergency contacts (IT, lawyer, accountant) on one page, offline and to hand.",
        ],
        "step_solo": (
            "Define plan B for your three most critical workflows: what do you "
            "pause, who helps externally, where is the buffer (time, money)? "
            "Mentally rehearse one incident per year."
        ),
        "yellow_note": (
            "Without plan B, a second small disruption is often enough to stop operations."
        ),
    },
    "s1": {
        "why": (
            "Growth without growing structures creates friction: unclear "
            "responsibilities, quality problems, managers who only fight fires. "
            "New hires cannot orient themselves; clients feel inconsistency. The "
            "phase is expensive because revenue rises but margin and pace fall."
        ),
        "step": (
            "Before the next growth step, clarify roles, responsibilities and "
            "core processes in writing. Standardise onboarding before the next "
            "hires arrive — not after."
        ),
        "tips": [
            "Hire only once the process for the role is documented.",
            "Introduce weekly 15-minute stand-ups with clear owners.",
            "Assign one person explicitly to operations/processes — even in small teams.",
        ],
        "yellow_note": (
            "If headcount scales faster than structures, error rates and turnover "
            "explode — often invisible until the next funding round."
        ),
    },
    "s2": {
        "why": (
            "In due diligence, unanswered risk and structure questions decide "
            "valuation and closing. If you discover risks only in the data room, "
            "you negotiate from the back foot. Investors review dependencies, "
            "contracts, IP, people and compliance — gaps cost time, trust and "
            "terms."
        ),
        "step": (
            "Review the company once from an investor's perspective: top "
            "dependencies, contracts, key figures, IP, people risks. Document "
            "answers in a data-room preparation folder before external questions "
            "arrive."
        ),
        "tips": [
            "Create an FAQ document for the 20 most common investor questions.",
            "Have contracts and cap table reviewed by a lawyer for gaps.",
            "Run a mock due diligence with a trusted adviser.",
        ],
        "yellow_note": (
            "Unprepared answers delay every funding round and lower valuation."
        ),
    },
    "s3": {
        "why": (
            "If customer behaviour, competition or technology change faster than "
            "the roadmap, a head start quietly turns into a deficit. You often "
            "notice only when the pipeline dries up or churn rises — then "
            "catching up costs more than steering early."
        ),
        "step": (
            "Introduce a quarterly market review: competitors, customer feedback, "
            "technology trends. Align the product roadmap with real customer "
            "signals, not internal assumptions alone."
        ),
        "tips": [
            "Speak monthly with 3–5 customers who almost churned.",
            "Track one early indicator (e.g. trial-to-paid, repeat rate) in writing.",
            "Reserve 20% of development capacity to respond to market changes.",
        ],
        "yellow_note": (
            "Without a market rhythm, product decisions age quietly until revenue shows it."
        ),
    },
    "s4": {
        "why": (
            "Business models rest on a few untested core assumptions — about "
            "willingness to pay, regulation, partners or channels. If one tips, "
            "the model tips. Platform and marketplace models are especially "
            "vulnerable because many dependencies interact at once."
        ),
        "step": (
            "Name your three most critical core assumptions in writing. Define an "
            "early warning signal for each and run a pre-mortem: 'Assume we fail "
            "in two years — what caused it?'"
        ),
        "tips": [
            "Test assumptions with small experiments before you scale.",
            "Diversify revenue streams while the core assumption still holds.",
            "Review assumptions quarterly as a team — not only at board meetings.",
        ],
        "yellow_note": (
            "Untested assumptions become critical as soon as market or regulation "
            "shifts slightly — without you noticing immediately."
        ),
    },
    "s5": {
        "why": (
            "Under growth pressure, fundamental decisions — hiring, funding, "
            "locations, partnerships — are often made ad hoc. Wrong decisions in "
            "this phase have effects lasting years and tie up capital and focus. "
            "Speed without a framework costs more than one extra week of thought."
        ),
        "step": (
            "Set a simple framework for major decisions: worst-case affordability, "
            "reversibility, second opinion. Clarify decision authority in writing "
            "before the next pressure arrives."
        ),
        "tips": [
            "Sleep on decisions over €50,000 for at least one night.",
            "For irreversible steps, get an external second opinion.",
            "Document the rationale — that helps learning later, not blame.",
        ],
        "yellow_note": (
            "Ad-hoc decisions under growth pressure become critical as soon as "
            "reversal costs more than the original decision."
        ),
    },
    "k1": {
        "why": (
            "Gradual market changes — new competitors, shifting customer "
            "behaviour, substitutes — stay invisible in stable day-to-day "
            "business. By the time the numbers show it, competitors often have a "
            "head start. Stable revenue masks security while the relevance of your "
            "offer declines."
        ),
        "step": (
            "Run an honest market and competitor analysis once a year: who is "
            "winning your target customers, and why? Monitor early indicators "
            "(enquiries, conversion rates, price pressure) continuously."
        ),
        "tips": [
            "Subscribe to industry news and competitor alerts — 15 minutes per week.",
            "Ask systematically why you lost deals.",
            "Test a new offer segment on a small scale before the market forces you to.",
        ],
        "yellow_note": (
            "Stability without market monitoring becomes critical as soon as "
            "enquiries weaken in quality or prices come under pressure."
        ),
    },
    "k2": {
        "why": (
            "Client relationships, specialist knowledge and decision-making power "
            "tied to individuals are a double risk: in daily operations (illness, "
            "resignation) and in succession or a sale. Buyers and banks assess "
            "person dependency harshly — it lowers business value and agility."
        ),
        "step": (
            "Name critical person dependencies in writing. Organise deputies and "
            "knowledge transfer. Where the owner is the dependency, start "
            "succession or sale preparation early."
        ),
        "tips": [
            "Maintain at least two contact people in the business for key clients.",
            "Document decision logs for recurring client cases.",
            "Review key-person and business interruption insurance.",
        ],
        "yellow_note": (
            "Person dependency becomes critical at the first absence or when a "
            "sale/succession is pending."
        ),
    },
    "k3": {
        "why": (
            "Historically grown workflows hide duplicated work, single-person "
            "dependencies and compliance gaps. Every change — new software, new "
            "employees, certification — becomes expensive and risky when nobody "
            "knows the end-to-end process."
        ),
        "step": (
            "Map core processes end to end once: who does what, with what, why. "
            "Remove obvious legacy clutter and assign an owner per process."
        ),
        "tips": [
            "Start with the process that generates the most customer complaints.",
            "Visualise workflows on one page — complexity becomes visible.",
            "After mapping, check: where does everything hang on one person or one spreadsheet?",
        ],
        "yellow_note": (
            "Without a process overview, every major change becomes a gamble — "
            "errors accumulate gradually."
        ),
    },
    "k4": {
        "why": (
            "If energy, wages, purchasing or interest rise faster than your "
            "prices, margins shrink unnoticed. Without a liquidity reserve, a "
            "margin problem becomes a payment problem — often only visible when "
            "suppliers ask for prepayment or the bank enquires."
        ),
        "step": (
            "Track cost and margin development monthly per service or product. "
            "Review pricing annually and build a liquidity reserve as a fixed item."
        ),
        "tips": [
            "Calculate contribution margin per product/project monthly — not only in the annual accounts.",
            "Renegotiate purchase prices actively once material costs rise by more than 5%.",
            "Plan 2–3 months of fixed costs as a reserve on a separate account.",
        ],
        "yellow_note": (
            "Creeping margin pressure becomes critical as soon as customer payment "
            "terms outlast your own liquidity."
        ),
    },
    "k5": {
        "why": (
            "New laws, supply-chain breaks, natural events or geopolitical shocks "
            "hit unprepared businesses with full force. Prepared ones lose days; "
            "unprepared ones lose months. Regulation (NIS2, supply-chain due "
            "diligence, industry rules) increasingly affects SMEs without lead time."
        ),
        "step": (
            "Name the three most relevant external scenarios for your industry. "
            "Create one page of contingency plan per scenario: first steps, "
            "responsible people, internal and external communication."
        ),
        "tips": [
            "Subscribe to industry association updates on regulation — filter to your topic.",
            "Keep supplier alternatives for critical materials on a list.",
            "Run one emergency exercise per year (a tabletop exercise is enough — 60 minutes).",
        ],
        "yellow_note": (
            "External shocks become critical without a contingency plan — especially "
            "when several areas are affected at once."
        ),
    },
}


def apply_report_content(questions: list[dict]) -> None:
    """Mutates questions in place with PDF report fields."""
    for q in questions:
        extra = REPORT_BY_ID.get(q["id"])
        if not extra:
            raise ValueError(f"Missing report content for question {q['id']}")
        q.update(extra)
