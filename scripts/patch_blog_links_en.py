#!/usr/bin/env python3
"""Add internal money-page links to EN blog posts (mirror of DE SEO plan)."""
from __future__ import annotations

from pathlib import Path

BLOG = Path(__file__).resolve().parents[1] / "content" / "blog"

EDITS: list[tuple[str, str, str]] = [
    (
        "mid-market-focus-risk-management.md",
        "This article shows which thinking and behaviour patterns hold mid-market businesses back",
        "This article shows which thinking and behaviour patterns hold mid-market businesses back — and how a [structured risk check for SMBs](/services/smb/) helps regain clarity.",
    ),
    (
        "what-is-risk-management.md",
        "With clear definitions and practical examples, we show how risk management helps create clarity",
        "With clear definitions and practical examples, we show how risk management helps create clarity — including [risk assessment in euros](/method/) instead of traffic lights.",
    ),
    (
        "risk-management-clarity-hazard-catalog.md",
        "That is why Beraterium relies on **risk dialogue**",
        "That is why Beraterium relies on **risk dialogue** and the [3-level hazard catalogue](/method/)",
    ),
    (
        "external-risk-factors-smb-8-threats.md",
        "The question is not whether these risks will hit your business",
        "The question is not whether these risks will hit your business — a [structured risk assessment for SMBs](/services/smb/) helps prioritise external shocks in euros.",
    ),
    (
        "theory-practice-risk-management-standards-smb.md",
        "Anyone searching for risk management quickly lands on standards, checklists and certificates",
        "Anyone searching for risk management quickly lands on standards, checklists and certificates — deeper [training in risk management](/training/) builds on that framework.",
    ),
    (
        "eu-ai-act-germany-companies.md",
        "Shortly before the deadline, the EU adopted the so-called",
        "Regulatory duties belong in your risk inventory — like [cyber attacks on SMBs](/solutions/cyber-attack/). Shortly before the deadline, the EU adopted the so-called",
    ),
    (
        "ai-business-risks-agents-marie-ossenkopf.md",
        "Not as future music, but as ongoing operations.",
        "See also [Cyber attack — what to do?](/solutions/cyber-attack/). Not as future music, but as ongoing operations.",
    ),
    (
        "why-employees-make-risky-decisions.md",
        "Management pressure — for example through tight resources, shortened onboarding or permanent urgency — reinforces this behaviour.",
        "Management pressure — for example through tight resources, shortened onboarding or permanent urgency — reinforces this behaviour. A [risk management method](/method/) that involves people addresses these blind spots.",
    ),
    (
        "intellectual-property-patent-protection-tips.md",
        "If you think internationally (sales, production, suppliers), you need to think early about patents",
        "If you think internationally (sales, production, suppliers), you need to think early about patents — and assess risks through [risk management consulting](/services/).",
    ),
    (
        "people-trust-risk-management.md",
        "Those who understand this see risk management not as a control instrument, but as cultural work:",
        "Those who understand this see [risk management](/method/) not as a control instrument, but as cultural work:",
    ),
]

HEADING_INSERTS: list[tuple[str, str, str]] = [
    (
        "risk-radar-episode-1-who-is-beraterium.md",
        "## Who is Beraterium?",
        "\nBeraterium is [risk management consulting for SMBs, startups and solo founders](/services/) — facilitated, valued in euros, with a double guarantee.\n",
    ),
    (
        "take-control-of-your-risks-before-they-control-you.md",
        "## Take control before risks control you",
        "\nThe first step is a clear picture — our [services overview](/services/) shows which check fits your situation.\n",
    ),
    (
        "risk-radar-community-experts-entrepreneurs.md",
        "## What is Risk Radar?",
        "\nThe [Risk Radar community](/risk-radar/) connects founders with vetted experts — alongside [risk management consulting](/services/).\n",
    ),
    (
        "family-succession-generational-conflict-risk.md",
        "## Why succession is more than a contract",
        "\nSuccession risks can be mapped structurally — see our [business succession solution page](/solutions/succession/).\n",
    ),
    (
        "iran-conflict-oil-price-supply-chains.md",
        "## Supply chains under pressure",
        "\nExternal shocks belong in the risk picture — the [SMB clarity roadmap](/services/smb/) values supply-chain and energy risks in euros.\n",
    ),
    (
        "employee-awareness-risk-conscious-culture.md",
        "## Why awareness is not a one-off event",
        "\nCulture and method work together — the [3-level hazard catalogue](/method/) makes team risks visible.\n",
    ),
    (
        "ai-and-risk-management-people-first.md",
        "## AI and risk management — people first",
        "\nTechnology does not replace [structured risk assessment](/method/) — it supports people in setting priorities.\n",
    ),
    (
        "taking-risks-consciously.md",
        "## Taking risks consciously",
        "\nConscious decisions need numbers — our [method](/method/) values residual risk in euros.\n",
    ),
    (
        "international-expansion-risks-location-strategy.md",
        "## Location choice and risk",
        "\nInternational expansion needs a risk picture — [services and checks](/services/) by company size.\n",
    ),
    (
        "founder-health-risk-management-nutrition.md",
        "## Founder health as a risk factor",
        "\nKey-person risk hits founding teams especially hard — the [4-week startup risk check](/services/startups/) addresses dependencies early.\n",
    ),
    (
        "emotional-leadership-smb-iceberg-model-risk.md",
        "## Emotional leadership and the iceberg model",
        "\nLeadership and culture risks belong in the SMB risk picture — see [risk management consulting for SMBs](/services/smb/).\n",
    ),
    (
        "business-security-risk-management-smb.md",
        "## Business security — more than alarms",
        "\n[Cyber attacks on SMBs](/solutions/cyber-attack/) are among the most common operational risks today — alongside physical security.\n",
    ),
]


def main() -> None:
    for name, old, new in EDITS:
        p = BLOG / name
        if not p.exists():
            print(f"MISS file {name}")
            continue
        t = p.read_text(encoding="utf-8")
        if old not in t:
            print(f"MISS replace {name}")
            continue
        if new in t:
            print(f"SKIP replace {name}")
            continue
        p.write_text(t.replace(old, new, 1), encoding="utf-8")
        print(f"OK replace {name}")

    for name, heading, insert in HEADING_INSERTS:
        p = BLOG / name
        if not p.exists():
            print(f"MISS file {name}")
            continue
        t = p.read_text(encoding="utf-8")
        if insert.strip() in t:
            print(f"SKIP heading {name}")
            continue
        anchor = heading if heading in t else next((ln for ln in t.splitlines() if ln.startswith("## ")), "")
        if not anchor:
            print(f"MISS heading {name}")
            continue
        p.write_text(t.replace(anchor, anchor + insert, 1), encoding="utf-8")
        print(f"OK heading {name}")


if __name__ == "__main__":
    main()
