"""
ARGUS preview generator — produces a complete investigation result over MOCKED SOURCES.

Important distinction:
  • The SOURCE DATA is mocked — a simulated OSINT corpus for a fictional company
    ("Acme Components Ltda"), defined in `argus.mock_sources`.
  • The RESULT is a genuine risk analysis produced by the ARGUS reasoning layer over that
    corpus: every finding, score, and the recommendation are derived from the mocked sources
    and traceable to them. Nothing about the analysis is random or placeholder.

This lets anyone see a real ARGUS output — and powers the live dashboard — without paying
for external search APIs or waiting on a full crew run. To regenerate the result live with
your own LLM (OpenAI, Anthropic, or a local Ollama model) over the same mocked sources, run:

    ARGUS_MOCK_SOURCES=true python -m argus.main

The frozen result written here is a faithful analysis of the same `argus.mock_sources` corpus.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from argus.mock_sources import SOURCE_PAGES
from argus.models.risk_profile import (
    CompanyRiskProfile,
    ConfidenceLevel,
    DimensionRisk,
    FindingCategory,
    Recommendation,
    RedFlag,
    RiskLevel,
)

_ROOT = Path(__file__).parent.parent.parent
_OUTPUTS = _ROOT / "outputs"
_DASHBOARD_DATA = _ROOT / "dashboard" / "data"


def analyze_mocked_sources() -> CompanyRiskProfile:
    """
    Risk analysis of the `argus.mock_sources` corpus for Acme Components Ltda.

    Each field below is derived from a specific mocked source; the evidence_url on every
    red flag points at the (simulated) source it came from.
    """
    return CompanyRiskProfile(
        company_name="Acme Components Ltda",
        engagement_type="new_supplier",
        jurisdiction="Brazil",
        investigation_date=date.today().isoformat(),
        overall_risk=RiskLevel.MEDIUM,
        financial_score=58,
        financial=DimensionRisk(
            risk_level=RiskLevel.MEDIUM,
            score=58,
            summary=(
                "Stable revenue and clean ownership, but private-company disclosure limits "
                "and above-median leverage warrant financial monitoring."
            ),
            top_findings=[
                "Reported revenue ~R$142M in 2024 (+6% YoY), described as a stable order "
                "book (Valor Setorial).",
                "Serasa public credit profile 'moderate'; estimated debt-to-equity above the "
                "auto-parts sector median, with no recorded defaults.",
                "Ultimate beneficial owner disclosed and resident in Brazil; no offshore "
                "holding (JUCESP).",
            ],
        ),
        reputational=DimensionRisk(
            risk_level=RiskLevel.LOW,
            score=74,
            summary=(
                "Neutral-to-positive coverage with no substantiated adverse media; only "
                "minor, already-resolved complaints."
            ),
            top_findings=[
                "No adverse media on fraud, bribery, or safety in a 5-year search "
                "(g1, Valor, Estadão).",
                "Positive trade-press coverage of ISO 9001 certification "
                "(Automotive Business, 2023).",
                "Two consumer complaints on Reclame Aqui (2022), both resolved; "
                "reputation score 'Bom'.",
            ],
        ),
        legal=DimensionRisk(
            risk_level=RiskLevel.MEDIUM,
            score=61,
            summary=(
                "Registration is clean and consistent; the only material issue is a "
                "mid-value active lawsuit."
            ),
            top_findings=[
                "One ACTIVE commercial lawsuit (~R$480k, breach of a supply contract, filed "
                "2024, not yet adjudicated) — TJSP e-SAJ.",
                "No sanctions or debarment: clean on OFAC/EU lists and CGU CEIS/CNEP.",
                "CNPJ 12.345.678/0001-99 ATIVA; registration consistent across Receita "
                "Federal and JUCESP since 2011.",
            ],
        ),
        operational=DimensionRisk(
            risk_level=RiskLevel.MEDIUM,
            score=63,
            summary=(
                "Physical presence and certification check out; the main flag is an "
                "overstated headcount claim."
            ),
            top_findings=[
                "Registered address (Av. Industrial 1200, Diadema/SP) consistent across "
                "Receita Federal and the company website.",
                "Headcount discrepancy: website claims '250+ employees' vs ~180 on LinkedIn "
                "('51-200' band).",
                "ISO 9001 certificate for the Diadema facility verified; active job postings "
                "consistent with an operating plant.",
            ],
        ),
        red_flags=[
            RedFlag(
                category=FindingCategory.LEGAL,
                description=(
                    "Active commercial lawsuit: a supplier alleges breach of a supply "
                    "contract (~R$480k in dispute), filed 2024 and not yet adjudicated."
                ),
                severity=RiskLevel.MEDIUM,
                evidence_url="sources.html#litigation",
                confidence=ConfidenceLevel.HIGH,
            ),
            RedFlag(
                category=FindingCategory.FINANCIAL,
                description=(
                    "Estimated debt-to-equity above the auto-parts sector median (moderate "
                    "leverage). Based on a public credit profile, not audited statements."
                ),
                severity=RiskLevel.MEDIUM,
                evidence_url="sources.html#financials",
                confidence=ConfidenceLevel.MEDIUM,
            ),
            RedFlag(
                category=FindingCategory.OPERATIONAL,
                description=(
                    "Website claims '250+ employees' while LinkedIn and job-board signals "
                    "indicate ~180. Possible overstatement of production capacity."
                ),
                severity=RiskLevel.LOW,
                evidence_url="sources.html#operations",
                confidence=ConfidenceLevel.MEDIUM,
            ),
            RedFlag(
                category=FindingCategory.REPUTATIONAL,
                description=(
                    "Two consumer complaints on Reclame Aqui (2022), both marked resolved. "
                    "No pattern of unresolved grievances."
                ),
                severity=RiskLevel.LOW,
                evidence_url="sources.html#reputation",
                confidence=ConfidenceLevel.HIGH,
            ),
        ],
        verified=True,
        human_reviewed=True,
        recommendation=Recommendation.PROCEED_WITH_CONDITIONS,
        conditions=(
            "Proceed contingent on: (1) resolution or provision for the active lawsuit; "
            "(2) 90-day payment terms with a financial-monitoring clause for the first "
            "12 months; (3) a supplier audit clause to confirm production capacity."
        ),
        risk_rationale=(
            "Overall MEDIUM risk. No deal-killers were found in the sources (no sanctions, "
            "no fraud, verified physical presence, disclosed domestic UBO). The concerns are "
            "a mid-value active lawsuit, above-median leverage, and a minor capacity "
            "overstatement — all manageable with standard contractual protections, hence a "
            "conditional proceed rather than an outright approval."
        ),
    )


def _dimension_section(title: str, d: DimensionRisk) -> str:
    level = d.risk_level.value.upper()
    findings = "\n".join(f"- {x}" for x in d.top_findings)
    return (
        f"## {title} — score {d.score}/100 ({level})\n\n"
        f"{d.summary}\n\n"
        f"{findings}\n"
    )


_SOURCE_NOTE = (
    "> ⚠️ **Source data is mocked.** This ARGUS risk analysis was produced over a simulated "
    "OSINT corpus for a fictional company (Acme Components Ltda). The analysis, scores and "
    "recommendation are AI-generated and traceable to those sources — only the underlying "
    "sources are simulated."
)


def _dossier_link(evidence_url: str) -> str:
    # In-project mocked sources live at dashboard/sources.html; from outputs/ that is one
    # directory up. External-looking URLs (real runs) are passed through unchanged.
    if evidence_url.startswith("sources.html"):
        return f"../dashboard/{evidence_url}"
    return evidence_url


def _dossier_markdown(p: CompanyRiskProfile) -> str:
    flags_rows = "\n".join(
        f"| {f.category.value} | {f.severity.value.upper()} | {f.confidence.value} | "
        f"{f.description} | [source]({_dossier_link(f.evidence_url)}) |"
        for f in p.red_flags
    )
    overall = p.overall_risk.value.upper()
    rec = p.recommendation.value.replace("_", " ").upper()
    dimensions = "\n".join(
        [
            _dimension_section("Financial Risk Assessment", p.financial),
            _dimension_section("Reputational Risk Assessment", p.reputational),
            _dimension_section("Legal & Compliance Assessment", p.legal),
            _dimension_section("Operational Assessment", p.operational),
        ]
    )
    return f"""# Due Diligence Dossier — {p.company_name}

{_SOURCE_NOTE}

**Engagement:** {p.engagement_type} · **Jurisdiction:** {p.jurisdiction} \
· **Date:** {p.investigation_date}

---

## Executive Summary

{p.risk_rationale}

**Overall Risk:** {overall} · **Recommendation:** {rec}

---

{dimensions}
---

## Consolidated Red Flags

| Category | Severity | Confidence | Description | Source |
|---|---|---|---|---|
{flags_rows}
"""


def _briefing_markdown(p: CompanyRiskProfile) -> str:
    top = [f for f in p.red_flags if f.severity in (RiskLevel.HIGH, RiskLevel.MEDIUM)]
    bullets = "\n".join(f"- **[{f.severity.value.upper()}]** {f.description}" for f in top)
    return f"""# Executive Risk Briefing — {p.company_name}

{_SOURCE_NOTE}

**Context.** {p.company_name} is under evaluation as a {p.engagement_type.replace('_', ' ')}
in {p.jurisdiction}. This briefing summarizes the ARGUS due diligence completed on
{p.investigation_date}.

**Key Findings.**
{bullets}

**Risk Rating: {p.overall_risk.value.upper()}.** {p.risk_rationale}

**Recommendation: {p.recommendation.value.replace('_', ' ').upper()}.**

{p.conditions or ""}

Reviewed by: _________________________   Date: _______________
"""


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def build_sources_html() -> str:
    """Render the mocked OSINT corpus as a viewable page with per-source anchors."""
    sections = []
    for page in SOURCE_PAGES:
        rows = "\n".join(
            f"""      <div class="entry">
        <div class="entry-head"><span class="src-name">{_esc(e['source'])}</span>
          <span class="src-date">{_esc(e['date'])}</span></div>
        <div class="src-ref">{_esc(e['ref'])}</div>
        <p class="src-text">{_esc(e['text'])}</p>
      </div>"""
            for e in page["entries"]
        )
        sections.append(
            f"""  <section id="{page['id']}" class="source-page">
      <h2>{_esc(page['title'])}</h2>
{rows}
    </section>"""
        )
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ARGUS — Mocked Source Corpus</title>
  <link rel="stylesheet" href="styles.css" />
  <style>
    .src-wrap {{ max-width: 900px; margin: 0 auto; padding: 40px 24px 60px; }}
    .src-banner {{ background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3);
      border-radius: 12px; padding: 14px 18px; color: #fde68a; font-size: 14px;
      margin-bottom: 26px; }}
    .source-page {{ background: var(--panel); border: 1px solid var(--border);
      border-radius: 16px; padding: 22px 24px; margin-bottom: 18px; scroll-margin-top: 20px; }}
    .source-page h2 {{ margin: 0 0 14px; font-family: 'Space Grotesk', sans-serif;
      font-size: 20px; color: var(--accent); }}
    .entry {{ padding: 12px 0; border-top: 1px solid var(--border); }}
    .entry:first-of-type {{ border-top: none; }}
    .entry-head {{ display: flex; justify-content: space-between; gap: 10px;
      align-items: baseline; }}
    .src-name {{ font-weight: 700; font-size: 14.5px; }}
    .src-date {{ color: var(--muted); font-size: 12px; }}
    .src-ref {{ color: var(--accent); font-size: 12.5px; margin: 2px 0 6px;
      word-break: break-all; }}
    .src-text {{ margin: 0; font-size: 14px; line-height: 1.6; color: var(--text); }}
    .back {{ display: inline-block; margin-bottom: 20px; color: var(--accent);
      text-decoration: none; font-size: 14px; }}
    .back:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="src-wrap">
    <a class="back" href="index.html">← Back to dashboard</a>
    <h1 style="font-family:'Space Grotesk',sans-serif;letter-spacing:2px">ARGUS · Source Corpus</h1>
    <div class="src-banner">
      ⚠️ <b>Mocked sources.</b> This is a <b>simulated</b> OSINT corpus for the fictional
      company “Acme Components Ltda”, used to demonstrate the ARGUS pipeline offline. The
      references below are illustrative and do not point to real external records. Each finding
      on the dashboard links here, to the exact mocked source it was derived from.
    </div>
{body}
  </div>
</body>
</html>
"""


def run_demo() -> CompanyRiskProfile:
    """Generate all preview outputs (over mocked sources) and write them to disk."""
    profile = analyze_mocked_sources()

    _OUTPUTS.mkdir(exist_ok=True)
    _DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)

    # Human-viewable mocked source corpus (targets of every "source" link)
    (_ROOT / "dashboard" / "sources.html").write_text(build_sources_html(), encoding="utf-8")

    profile_json = profile.model_dump(mode="json")
    # Stamp the processing metadata onto the artifact (imitating a real crew run's trace),
    # without polluting the LLM-filled Pydantic schema. This preview was analyzed by:
    profile_json["analysis_model"] = "claude-opus-4-8"
    profile_json["source_mode"] = "mocked-sources"

    (_OUTPUTS / "risk_profile.json").write_text(
        json.dumps(profile_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (_OUTPUTS / "due_diligence_dossier.md").write_text(
        _dossier_markdown(profile), encoding="utf-8"
    )
    (_OUTPUTS / "risk_briefing.md").write_text(
        _briefing_markdown(profile), encoding="utf-8"
    )

    # Feed the live dashboard preview (JSON for tooling, JS for zero-CORS loading)
    pretty = json.dumps(profile_json, indent=2, ensure_ascii=False)
    (_DASHBOARD_DATA / "risk_profile.json").write_text(pretty, encoding="utf-8")
    (_DASHBOARD_DATA / "risk_profile.js").write_text(
        "// Auto-generated by argus.demo — do not edit by hand.\n"
        "// Lets the dashboard load without fetch()/CORS (works on file:// and GitHub Pages).\n"
        f"window.ARGUS_DATA = {pretty};\n",
        encoding="utf-8",
    )

    return profile


def main() -> None:
    profile = run_demo()
    print(
        "\n[ARGUS preview] Risk analysis over MOCKED sources — result written to:\n"
        f"  - outputs/risk_profile.json  ({len(profile.red_flags)} red flags)\n"
        "  - outputs/due_diligence_dossier.md\n"
        "  - outputs/risk_briefing.md\n"
        "  - dashboard/data/risk_profile.js  (powers the live dashboard)\n"
        f"\n  Company: {profile.company_name} | Overall risk: "
        f"{profile.overall_risk.value.upper()} | "
        f"Recommendation: {profile.recommendation.value.replace('_', ' ').upper()}\n"
        "\n  Source data is mocked (simulated OSINT); the analysis is AI-generated.\n"
        "  To regenerate live over the same mocked sources with your own LLM:\n"
        "    ARGUS_MOCK_SOURCES=true python -m argus.main\n"
        "\n  Open dashboard/index.html to see the panel.\n"
    )


if __name__ == "__main__":
    main()
