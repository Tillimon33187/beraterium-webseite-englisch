"""Page content for training subpages /training/<slug>/.

Data only (no imports from _gen_pages; imported from there).
Pricing/tiers come from _pricing.py (join via "nr"); editorial page content only.
Source: Angebote/training/*.md
"""
from __future__ import annotations

SCHULUNG_CONFIGS: list[dict] = [
    {
        "nr": "SCH-07",
        "slug": "risk-expert",
        "tag": "TRAINING · COMBINED FROM THREE PROGRAMMES",
        "h1": "Risk Expert training",
        "lead": (
            "The complete programme for anyone responsible for risk management in their "
            "organisation: this combined training brings together our three risk management "
            "programmes into one in-depth course — risk-awareness culture inspired by aviation, "
            "The Risk-Aware Manager, and Putting Risk Management into Practice. It equips "
            "managers and employees to build and run our method independently in their own "
            "business. Three intensive days, on-site or online, with certificate."
        ),
        "title": "Risk Expert training | Beraterium",
        "description": "Combined training from three programmes: risk culture, risk-aware leadership and practical risk analysis — 3 days, certificate, from 9,875 € excl. VAT (2 people 14,315 €).",
        "audience": "future risk owners, managers and employees",
        "fuer_wen_intro": "This training fits if any of the following applies:",
        "fuer_wen": [
            "You are building and owning risk management in the business — and want to master it from the ground up",
            "One topic is not enough: you want culture, leadership AND method in a single programme",
            "You are a manager or employee tasked with implementing the Beraterium method internally",
            "You want to solve risk management in-house long term, instead of buying it in permanently",
        ],
        "sessions": [
            ("Module 1 — Building a risk-awareness culture", [
                "Just Culture inspired by aviation: admit mistakes openly instead of covering them up",
                "Leadership structure: reporting channels, blameless debriefings, error rituals",
                "Involving the team: learn from mistakes instead of looking for someone to blame",
                "Practical simulation: debriefing a real (anonymised) incident",
            ]),
            ("Module 2 — Risk-aware leadership", [
                "Letting go of fear of mistakes and seeing risks as calculated opportunities",
                "Decision frameworks: expected value, worst-case capacity, reversibility",
                "Seeing your own business from the outside: pre-mortem and competitor perspective",
                "Leading by example: modelling an open risk culture",
            ]),
            ("Module 3 — Putting risk management into practice", [
                "The Beraterium system: from hazard through risk to measure",
                "Running a risk analysis with the team and scoring with the matrix",
                "Using the 3-level hazard catalogue — you receive the full catalogue",
                "Valuing risks in euros and deriving actionable measures that stick",
            ]),
            ("Closing — Certification & transfer", [
                "Bringing all modules together on a real area of your business",
                "Your transfer plan: how to roll out the method in the business over the coming weeks",
                "Check-in call after training: open questions, adjustments",
                "Certificate: Risk Expert — Beraterium Method",
            ]),
        ],
        "ergebnis": [
            "You master the full Beraterium method: culture, leadership and practical risk analysis",
            "You can build a risk-awareness culture, take calculated risks as a leader and run the analysis yourself",
            "The full 3-level hazard catalogue stays in the business and is ready to use immediately",
            "Risk Expert certificate plus transfer plan for implementation in your own organisation",
        ],
        "workload_iso": "PT24H",
        "faq": [
            ("What exactly is Risk Expert training?", "A combined programme that bundles our three risk management trainings into one continuous course: risk-awareness culture, The Risk-Aware Manager and Putting Risk Management into Practice. The goal: you master culture, leadership and method and can implement our approach independently in the business."),
            ("What does the training cost?", "9,875 € for one person, 14,315 € for two people, plus 4,440 € for each additional participant. For up to 4 people the flat rate of 22,875 € applies (max. 4 participants) — including hazard catalogue and certificate. The investment is deliberately comparable to our guided Risk Analysis 360° (3,475 €) and the XL full package (9,675 €) — you build the method in-house long term instead of buying risk management in permanently. All prices excl. VAT"),
            ("Who is this training for?", "Managers and employees who are building and owning risk management in the business — future risk owners who want the full toolkit in one go instead of individual topics one after another."),
            ("Is the combined programme worth it compared with individual trainings?", "Yes — in content and economically. The three individual intensive-format trainings (1:1 or small group) cost 12,425 € together. In the combined programme the modules run more compactly in one flow — for 9,875 € you get the full programme including certificate and transfer plan."),
            ("How long does the training take and is there a certificate?", "Three intensive days (approx. 24 hours) plus transfer phase — on-site or online, split across dates if needed. At the end you receive the Risk Expert — Beraterium Method certificate and a transfer plan for implementation."),
        ],
        "cta_h2": "Become the risk expert in your organisation",
        "cta_body": "In a free intro call we clarify prior knowledge, team size, format and dates — no obligation, 30 minutes.",
    },
    {
        "nr": "SCH-01",
        "slug": "risk-awareness-culture",
        "tag": "TRAINING · LEADERSHIP + TEAM",
        "h1": "Risk management: the path to a risk-awareness culture",
        "lead": (
            "This training shows how to prepare and lead a team so that risks and mistakes "
            "are no longer taboo but part of learning. Using aviation as the model, we build "
            "a learn-from-mistakes culture: mistakes are admitted openly and recognised "
            "instead of punished — away from blame culture, towards improving together. "
            "One day in intensive format (1:1 or small group), on-site or online — "
            "significantly deeper than the culture module in the combined Risk Expert programme."
        ),
        "title": "Risk-awareness culture training | Beraterium",
        "description": "Intensive format (1:1 or small group): deepen error culture and risk awareness — 1 day, from 3,975 € excl. VAT, team flat rate from 11,475 €.",
        "audience": "leaders and teams",
        "fuer_wen_intro": "This training fits if at least one of the following applies:",
        "fuer_wen": [
            "Mistakes are covered up instead of reported — and only surface when they become expensive",
            "When problems arise, people look for someone to blame before they look for the cause",
            "You want your team to raise risks early instead of staying silent and hoping",
            "You are introducing risk management and need the cultural foundation for it",
        ],
        "sessions": [
            ("Session 1 — Leadership & structure (3 h)", [
                "Risk awareness: risk consciousness vs. risk fear vs. risk blindness",
                "The anatomy of silence culture — why mistakes go unreported and what that costs",
                "Just Culture inspired by aviation: human error, risk-taking behaviour, gross negligence",
                "Implementing leadership structure: reporting channels, blameless debriefings, error rituals",
                "Celebrate mistakes instead of punishing them: formats that reward speaking up",
            ]),
            ("Session 2 — Team & participation (3 h)", [
                "Getting everyone involved: work on processes instead of staying silent and hoping",
                "Psychological safety in practice: exercises and conversation formats",
                "From mistake to process: the learning loop report → analyse → change → review",
                "Team early-warning system: employees as sensors for risks",
                "Practical simulation: debriefing a real (anonymised) incident using the aviation schema",
            ]),
            ("Transfer — Embedding in daily work (included)", [
                "30-day implementation plan: which rituals and reporting channels to introduce when",
                "Templates to keep: reporting schema, debriefing guide, error-ritual formats",
                "Check-in call after 4 weeks: what works, where it sticks, what to adjust",
            ]),
        ],
        "ergebnis": [
            "Concrete structure (reporting channels, rituals, debriefing format), ready to use from day 1",
            "The team has experienced: speaking up is rewarded, not punished",
            "Fewer covered-up mistakes — risks become visible earlier, damage stays smaller",
            "Cultural foundation for every further risk management measure",
        ],
        "workload_iso": "PT6H",
        "faq": [
            ("Who is the risk-awareness culture training for?", "Leaders and team together — culture only works when both sides learn the same principles. Bookable for individual employees, small groups or the whole team."),
            ("What does the training cost?", "Intensive format: 3,975 € for the first person, plus 995 € for each additional person. From 10 people the capped flat rate of 11,475 € applies. Significantly deeper and more personal than the culture module in the combined Risk Expert programme (9,875 €). All prices excl. VAT"),
            ("Why aviation as the model?", "Aviation is the most safety-critical industry in the world and has the most open error culture: Just Culture, sanction-free reporting systems and structured debriefings. These principles transfer directly to business — a reported near-miss is more valuable than a hidden loss."),
            ("How long is the training and in what format?", "One day with two sessions of 3 hours each — on-site at your premises or online. Session 1 focuses on leadership and structure, session 2 on the team and participation. Includes transfer package: 30-day plan, templates and a check-in call after 4 weeks."),
            ("How does this training differ from the Cultural Foundation workshop?", "The 180-minute workshop raises awareness of psychological safety. The training goes much deeper: you implement a complete leadership structure inspired by aviation — with reporting channels, debriefing formats and a practical simulation on a real incident."),
        ],
        "cta_h2": "Build a culture where risks become visible",
        "cta_body": "In a free intro call we clarify team size, format and date — no obligation, 30 minutes.",
    },
    {
        "nr": "SCH-02",
        "slug": "risk-aware-manager",
        "tag": "TRAINING · LEADERS ONLY",
        "h1": "The risk-aware manager",
        "lead": (
            "This training is specifically for managers: lose the fear of mistakes and see "
            "them as opportunities to grow, reduce fear of risk and take calculated risks — "
            "and look at your own business again with a neutral outside lens to regain a "
            "fresh feel for your processes and risks. One compact day, on-site or online."
        ),
        "title": "Training: The risk-aware manager | Beraterium",
        "description": "Intensive format for leaders (1:1): let go of fear of mistakes, take calculated risks — compact day from 3,475 € excl. VAT, leadership team flat rate 9,875 €.",
        "audience": "managing directors, leaders and founders",
        "fuer_wen_intro": "This training fits if you recognise yourself in any of the following:",
        "fuer_wen": [
            "You delay decisions because the risk feels hard to grasp",
            "Mistakes — yours or others' — feel like failure instead of learning material",
            "You are so deep in day-to-day operations that you can no longer see your processes neutrally",
            "You do not want to avoid risks — you want to take them consciously and with calculation",
        ],
        "sessions": [
            ("Block 1 — Your own attitude to mistakes (2 h)", [
                "Understanding fear of mistakes: where it comes from and what it does in leadership day to day",
                "Mistakes as growth opportunities: reframing from \"this must not happen\" to \"what do we learn?\"",
                "Leading by example: the team is only as open as its leadership",
            ]),
            ("Block 2 — Taking calculated risks (2 h)", [
                "Risk fear vs. risk competence: avoid, suppress or decide consciously",
                "Decision frameworks: expected value, worst-case capacity, reversibility",
                "The upside: risks worth taking — and how to justify them",
            ]),
            ("Block 3 — Seeing your business from the outside (2 h)", [
                "Operational blindness as a risk: why the neutral view disappears after years",
                "The outside lens: pre-mortem, competitor perspective, newcomer walkthrough",
                "Practical exercise: analyse your core process from the outside — top 3 risks and opportunities",
            ]),
        ],
        "ergebnis": [
            "Personal risk mindset: decide under uncertainty without freezing",
            "Concrete frameworks for calculated risk decisions in daily work",
            "Fresh outside view of your processes — including top risks and opportunities",
            "Foundation to model an open risk culture in the team",
        ],
        "workload_iso": "PT6H",
        "faq": [
            ("Who is The Risk-Aware Manager training for?", "Exclusively for leaders: managing directors, department and team leads, founders. The protected setting without your own employees is intentional — here you can speak openly about your own fears and mistakes."),
            ("What does the training cost?", "Intensive format: 3,475 € for the first leader, plus 875 € for each additional person. From 8 people the capped flat rate of 9,875 € applies. Protected 1:1 setting — significantly deeper than module 2 in the combined programme. All prices excl. VAT"),
            ("What does \"seeing the business from the outside\" mean?", "After a few years in your own company, nobody sees their processes neutrally any more — operational blindness is a risk in itself. With techniques like pre-mortem and competitor perspective you regain the outside view and spot risks and opportunities that daily work has made invisible."),
            ("How long is the training?", "One compact day with three blocks of 2 hours each — on-site or online. On request we split the blocks across two half-days."),
            ("Is this about taking more or fewer risks?", "Neither — it is about calculated risks: deciding consciously instead of avoiding or suppressing. You learn frameworks to assess which risks your business can carry and which opportunities are worth taking."),
        ],
        "cta_h2": "Lead with risk competence instead of risk fear",
        "cta_body": "In a free intro call we clarify whether the training fits your situation — no obligation, 30 minutes.",
    },
    {
        "nr": "SCH-03",
        "slug": "practical-risk-management",
        "tag": "TRAINING · TEAM + LEADERSHIP + RISK MANAGERS",
        "h1": "Putting risk management into practice",
        "lead": (
            "In this training you learn our risk assessment system — and how to apply it "
            "yourself: step by step run a risk analysis with the team, score risks with "
            "the matrix, work with the hazard catalogue (you receive our full catalogue), "
            "value risks in euros and derive actionable, understandable measures. How it "
            "is done in large corporations — broken down into practical steps."
        ),
        "title": "Practical risk management training | Beraterium",
        "description": "Intensive format: learn to run risk analysis yourself — matrix, hazard catalogue (included), euro valuation — 1.5 days, from 4,975 € excl. VAT, team flat rate 14,375 €.",
        "audience": "employees, leaders, risk managers and business owners",
        "fuer_wen_intro": "This training fits if any of the following applies:",
        "fuer_wen": [
            "You are a risk manager and want to understand how to do it properly — like in a large corporation, but practical",
            "You want to solve risk management in-house long term instead of buying it in",
            "Your team should run the annual risk analysis themselves in future",
            "You want to value risks in euros, not traffic lights, and derive real measures from them",
        ],
        "sessions": [
            ("Session 1 — Understanding the system (4 h)", [
                "The Beraterium approach in overview: from hazard to risk to measure",
                "The 3-level hazard catalogue: structure, logic, application — you receive the full catalogue",
                "Collecting hazards with the team: facilitation techniques for the assessment",
            ]),
            ("Session 2 — Scoring with matrix and euros (4 h)", [
                "Using the risk matrix correctly — and avoiding typical scoring mistakes",
                "From traffic lights to euros: expected value, ranges, worst case, prioritisation",
                "Practical part: full scoring on a real area of your business",
            ]),
            ("Session 3 — Deriving and embedding measures (4 h)", [
                "From number to measure: avoid, reduce, transfer, accept",
                "Budgeting measures: cost of the measure vs. euro risk",
                "Embedding in daily work: rhythm, ownership, review — routine instead of one-off project",
                "Closing: everyone leaves with a started, real risk analysis",
            ]),
        ],
        "ergebnis": [
            "You can run a risk analysis using the Beraterium system independently: assess → matrix → euros → measures",
            "The full 3-level hazard catalogue stays in the business and is ready to use immediately",
            "Corporate methodology at SME scale — same language, less bureaucracy",
            "A started real analysis as a direct starting point after training",
        ],
        "workload_iso": "PT12H",
        "faq": [
            ("Who is Putting Risk Management into Practice for?", "Employees and leaders who will run the risk analysis themselves in future — and explicitly also risk managers from businesses and owners who want to solve risk management internally instead of buying it in."),
            ("What does the training cost?", "Intensive format: 4,975 € for the first person, plus 1,175 € for each additional person. From 10 people the capped flat rate of 14,375 € applies — including the full hazard catalogue. Significantly more comprehensive than module 3 in the combined programme. All prices excl. VAT"),
            ("What is included in the hazard catalogue?", "All participants receive our full 3-level hazard catalogue — the same working tool we use in client projects. It ensures no hazard class is missed during assessment and stays in the business after training."),
            ("How does this training differ from a risk analysis done by Beraterium?", "In Risk Analysis 360° we run the analysis for you. In this training you learn to do it yourself — method, matrix, euro valuation and measure derivation. Many clients combine both: guided analysis first, then training for the team."),
            ("How long is the training?", "1.5 days with three sessions of 4 hours each — on-site or online. In the practical part participants work continuously on a real area of their business."),
        ],
        "cta_h2": "Learn to value risks in euros yourself",
        "cta_body": "In a free intro call we clarify prior knowledge, team size and date — no obligation, 30 minutes.",
    },
    {
        "nr": "SCH-04",
        "slug": "innovation-management",
        "tag": "TRAINING · LEADERSHIP + TEAM",
        "h1": "Innovation management training",
        "lead": (
            "Innovation management is a core part of business development. In this training "
            "the focus is on becoming and staying genuinely innovative — not launching one "
            "product and fading away, but staying innovative over years and competing even "
            "against much larger rivals. Team, atmosphere, management and innovation culture: "
            "how business, innovation and R&D work under one roof."
        ),
        "title": "Innovation management training | Beraterium",
        "description": "Innovation culture, pipeline and metrics — 1 day, on-site or online, from 2,995 € excl. VAT, team flat rate from 9,695 €.",
        "audience": "leaders and teams from business, product and R&D",
        "fuer_wen_intro": "This training fits if any of the following applies:",
        "fuer_wen": [
            "Your last successful product was a while ago — the pipeline behind it is thin",
            "There are plenty of ideas but no repeatable path from idea to market performance",
            "Day-to-day operations and innovation compete for the same people and budgets",
            "You want to compete against larger rivals without their budgets",
        ],
        "sessions": [
            ("Session 1 — Building innovation capability (3.5 h)", [
                "What innovative companies do differently: innovation as capability, not project",
                "Culture and atmosphere: psychological safety, experiment budget, handling failed ideas",
                "Team and roles: collecting ideas systematically from the whole team",
                "Management: portfolio thinking, light stage-gate for SMEs, kill criteria",
            ]),
            ("Session 2 — Business, innovation and R&D under one roof (3.5 h)", [
                "The balancing act: earn today, stay relevant tomorrow — resource split in practice",
                "Competing with giants: niche, speed and customer proximity as SME strengths",
                "Building an innovation pipeline: idea → validation → pilot → scale",
                "Measure and steer: a few meaningful metrics instead of innovation theatre",
                "Practical part: mini-pipeline for a real innovation topic of your own",
            ]),
            ("Transfer — Pipeline in daily work (included)", [
                "Templates to keep: pipeline board, kill-criteria checklist, experiment canvas",
                "Validation plan for the started innovation initiative — the next 30 days",
                "Check-in call after 4 weeks: pipeline review, adjust stumbling blocks",
            ]),
        ],
        "ergebnis": [
            "Shared understanding of what innovation capability means concretely in your business",
            "A lightweight, repeatable innovation process with clear decision points",
            "Clarity on roles, resource split and metrics — business and innovation working together",
            "A started real innovation initiative with validation plan",
        ],
        "workload_iso": "PT7H",
        "faq": [
            ("Who is the innovation management training for?", "Leaders and teams from business, product and R&D — together or separately. It is deliberately SME- and startup-friendly: no corporate framework, but processes that work with small teams."),
            ("What does the training cost?", "2,995 € for the first person, plus 745 € for each additional person. From 10 people the capped flat rate of 9,695 € applies. All prices excl. VAT"),
            ("What if we are already innovative?", "Being innovative once is easy — staying innovative is the problem. The training builds the structures that make innovation repeatable: pipeline, portfolio thinking, kill criteria and a resource split that does not cannibalise day-to-day operations."),
            ("How long is the training?", "One day with two sessions of 3.5 hours each — on-site or online. In the practical part participants work on a real innovation topic. Includes transfer package: templates, validation plan and a check-in call after 4 weeks."),
            ("How do innovation and risk management connect?", "Innovation means taking calculated risks. Those who assess innovation risks consciously — instead of avoiding or blindly taking them — invest in the right places. Both disciplines share the same foundation: a culture where failure is learning material."),
        ],
        "cta_h2": "Make innovation a repeatable capability",
        "cta_body": "In a free intro call we clarify your starting point, team size and date — no obligation, 30 minutes.",
    },
    {
        "nr": "SCH-05",
        "slug": "feedback-culture",
        "tag": "TRAINING · FOR EVERYONE",
        "h1": "Feedback culture & a 1+ working environment",
        "lead": (
            "In this training, leadership and team build a culture together where work "
            "is not a burden and everyone pulls in the same direction. Three core areas: "
            "feedback culture, understanding employees and finding out what they really "
            "want, and motivating people with the right leadership style. That includes "
            "making mission and vision transparent and communicating them. The result: "
            "less turnover, satisfied employees — even in difficult times."
        ),
        "title": "Feedback culture & leadership training | Beraterium",
        "description": "Feedback, motivation, leadership style, mission & vision — 1 day + follow-up, from 2,875 € excl. VAT, team flat rate from 9,395 €.",
        "audience": "leaders and employees",
        "fuer_wen_intro": "This training fits if any of the following applies:",
        "fuer_wen": [
            "Turnover and quiet quitting are rising — and you learn the reasons too late",
            "Feedback only happens in the annual review (or not at all)",
            "You are not sure what your employees really want",
            "Mission and vision are on the website but not in daily work",
        ],
        "sessions": [
            ("Session 1 — Feedback & understanding (3 h)", [
                "Building feedback culture: formats and rituals in both directions",
                "The feedback trap: why feedback without consequence destroys trust",
                "Understanding employees: 1:1 formats, stay interviews, anonymous channels",
                "Practical part: feedback exercises in the team's real situations",
            ]),
            ("Session 2 — Motivation, leadership style, mission & vision (3 h)", [
                "Understanding motivation: autonomy, competence, purpose — what really drives people",
                "Finding the right leadership style: situational leadership instead of one-size-fits-all",
                "Making mission & vision transparent: formulate together, translate into daily work",
                "Practical part: design a culture roadmap for your own team",
            ]),
            ("Follow-up — Review after 4 weeks (60 min.)", [
                "Culture roadmap check: what works, where it sticks, what to adjust",
            ]),
        ],
        "ergebnis": [
            "Less turnover, more satisfied employees, easier leadership",
            "Talent that comes to you — and employees who stay even in difficult times",
            "A concrete, jointly developed culture roadmap instead of values posters",
            "Mission and vision that everyone on the team understands and can apply",
        ],
        "workload_iso": "PT7H",
        "faq": [
            ("Who is the feedback culture training for?", "Everyone — leaders and employees, ideally together. Culture is not created by top-down instruction: the culture roadmap is developed jointly by leadership and team in the training."),
            ("What does the training cost?", "2,875 € for the first person, plus 725 € for each additional person. From 10 people the capped flat rate of 9,395 € applies — including follow-up call after 4 weeks. All prices excl. VAT"),
            ("What does a \"1+ working environment\" mean?", "A working environment where performance and contribution are not forced and work is not a burden — because employees and leadership work in the same direction. You see it in less turnover, easier recruiting and a team that stays even in difficult times."),
            ("How does this training connect to HR analyses?", "Ideal combined: HR analysis via questionnaire or leadership interviews deliver an honest picture of today; this training builds culture on top. Both can also be booked independently."),
            ("How long is the training?", "One day with two sessions of 3 hours each plus a 60-minute follow-up call around 4 weeks later — where the culture roadmap is reviewed and adjusted."),
        ],
        "cta_h2": "Build a working environment where everyone pulls together",
        "cta_body": "In a free intro call we clarify your starting point, team size and date — no obligation, 30 minutes.",
    },
    {
        "nr": "SCH-06",
        "slug": "cultural-management",
        "tag": "TRAINING · INTERNATIONAL TEAMS & PROJECTS",
        "h1": "Cross-cultural management training",
        "lead": (
            "An in-depth training on how to manage international teams and international "
            "projects — joint ventures, setting up subsidiaries and similar — successfully, "
            "with genuine understanding of the other culture. Especially important when "
            "you hire employees from other cultures. Based on Meyer, Hofstede and Schwartz, "
            "with first-hand experience from cross-cultural teams and businesses: from Germany "
            "and the EU via Russia, the USA and South America to Africa, India and Pakistan."
        ),
        "title": "Cross-cultural management training | Beraterium",
        "description": "Intensive format: cross-cultural management using Meyer, Hofstede & Schwartz — international teams, joint ventures — 1.5–2 days, from 3,475 € excl. VAT, team flat rate 9,875 €.",
        "audience": "leaders, project leads and international teams",
        "fuer_wen_intro": "This training fits if any of the following applies:",
        "fuer_wen": [
            "You lead or plan an international team, joint venture or subsidiary",
            "You hire employees from other cultures and want onboarding and leadership to be culturally sensitive",
            "Negotiations or projects with international partners move slowly — and you suspect cultural reasons",
            "You are expanding into a new cultural region and want to avoid the most expensive misunderstandings",
        ],
        "sessions": [
            ("Session 1 — The map: cultural dimensions (3 h)", [
                "Hofstede: power distance, individualism, uncertainty avoidance, long-term orientation",
                "Erin Meyer (Culture Map): communicating, evaluating, leading, deciding, trusting, scheduling",
                "Schwartz: the values circle and motivation across cultures",
                "Limits of the models: map, not pigeonhole",
            ]),
            ("Session 2 — Regional practice: first-hand experience (3 h)", [
                "Germany/EU internally, Russia & Eastern Europe, USA, South America, Africa, India & Pakistan",
                "Per region: communication style, hierarchy and time, negotiation logic",
                "Typical misunderstandings from real projects — and how to resolve them",
            ]),
            ("Session 3 — Leading international teams (3 h)", [
                "Hiring and integrating across cultures: reading interviews, culturally sensitive onboarding",
                "Managing mixed teams: meetings, feedback and decisions that work for all cultures",
                "Remote & time zones: communication rules that work across cultures",
            ]),
            ("Session 4 — International projects & structures (3 h)", [
                "Joint ventures & subsidiaries: cultural due diligence, workable governance",
                "Negotiating across cultures: pace, relationship-building, saving face",
                "Practical part: cultural risk analysis for your own international initiative",
            ]),
        ],
        "ergebnis": [
            "Confidence with international partners, teams and new hires — evidence-based, not anecdotal",
            "Concrete playbooks per region for communication, leadership and negotiation",
            "Spot cultural risks early — before they cost you a joint venture or key hire",
            "A started cultural risk analysis for your own international initiative",
        ],
        "workload_iso": "PT12H",
        "faq": [
            ("Who is cross-cultural management training for?", "Leaders, project leads and teams with an international dimension — from international teams via joint ventures and subsidiary setups to hiring employees from other cultures."),
            ("What does the training cost?", "3,475 € for the first person, plus 875 € for each additional person. From 8 people the capped flat rate of 9,875 € applies. All prices excl. VAT"),
            ("Which models is the training based on?", "Three established culture models: Erin Meyer's Culture Map, Hofstede's cultural dimensions and Schwartz's values theory — combined with first-hand experience from real cross-cultural teams and projects from Germany/EU via Russia, the USA and South America to Africa, India and Pakistan."),
            ("Which regions does the training cover?", "Germany/EU (including underestimated internal differences), Russia and Eastern Europe, the USA, South America, Africa, and India and Pakistan. On request we focus on the regions you work with directly."),
            ("How long is the training?", "1.5 to 2 days with four sessions of 3 hours each — on-site or online. In the practical part participants create a cultural risk analysis for their own international initiative."),
        ],
        "cta_h2": "Manage international teams with cultural understanding",
        "cta_body": "In a free intro call we clarify regional focus, team size and date — no obligation, 30 minutes.",
    },
]
