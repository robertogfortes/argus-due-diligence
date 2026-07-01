"""
ARGUS Demo Mode — generates a complete, schema-valid investigation result set
WITHOUT calling any external LLM or search API.

This exists so anyone can:
  1. See the exact shape of a real ARGUS output (risk_profile.json + dossier + briefing)
  2. Populate the live dashboard for a preview
  3. Validate the full pipeline offline (CI-friendly, no API keys)

The data below is ILLUSTRATIVE — a realistic but fictional example for the
company "Acme Components Ltda". It is NOT a real investigation. When you run the
real crew (`python -m argus.main` with API keys), the same models and files are
produced from live sources.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

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


def build_sample_profile() -> CompanyRiskProfile:
    """Build a realistic, fictional CompanyRiskProfile for demonstration."""
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
                "Stable revenue but limited public disclosure and moderate leverage "
                "warrant financial monitoring."
            ),
            top_findings=[
                "Revenue reported consistent across two independent sources (2023-2024).",
                "Debt-to-equity estimated above sector median from public filings.",
                "Ultimate beneficial owner disclosed and not sanctioned.",
            ],
        ),
        reputational=DimensionRisk(
            risk_level=RiskLevel.LOW,
            score=74,
            summary="Largely neutral-to-positive media coverage; isolated resolved complaints.",
            top_findings=[
                "No adverse media on fraud or corruption in 5-year lookback.",
                "Two resolved consumer complaints on Reclame Aqui (2022).",
                "Positive trade-press coverage on ISO 9001 certification (2023).",
            ],
        ),
        legal=DimensionRisk(
            risk_level=RiskLevel.MEDIUM,
            score=61,
            summary="Active commercial litigation of limited value; registration consistent.",
            top_findings=[
                "One active commercial lawsuit (contract dispute, ~R$ 480k).",
                "CNPJ active and consistent across Receita Federal and JUCESP.",
                "No sanctions matches on OFAC, EU, or COAF watch lists.",
            ],
        ),
        operational=DimensionRisk(
            risk_level=RiskLevel.MEDIUM,
            score=63,
            summary="Physical presence verified; headcount claims slightly overstated.",
            top_findings=[
                "Registered address matches street-view of an industrial facility.",
                "LinkedIn headcount (~180) below website claim of '250+ employees'.",
                "ISO 9001 certification verified with certifying body.",
            ],
        ),
        red_flags=[
            RedFlag(
                category=FindingCategory.LEGAL,
                description=(
                    "Active commercial lawsuit for alleged breach of a supply contract "
                    "(~R$ 480k in dispute), filed 2024. Not yet adjudicated."
                ),
                severity=RiskLevel.MEDIUM,
                evidence_url="https://esaj.tjsp.jus.br/cposg/search.do?processo=xxxxxxx",
                confidence=ConfidenceLevel.HIGH,
            ),
            RedFlag(
                category=FindingCategory.FINANCIAL,
                description=(
                    "Estimated debt-to-equity ratio exceeds the sector median, suggesting "
                    "moderate leverage. Based on public filing proxies, not audited figures."
                ),
                severity=RiskLevel.MEDIUM,
                evidence_url="https://www.jucesp.sp.gov.br/",
                confidence=ConfidenceLevel.MEDIUM,
            ),
            RedFlag(
                category=FindingCategory.OPERATIONAL,
                description=(
                    "Website claims '250+ employees' while LinkedIn and job-board signals "
                    "indicate approximately 180. Possible overstatement of capacity."
                ),
                severity=RiskLevel.LOW,
                evidence_url="https://www.linkedin.com/company/acme-components/",
                confidence=ConfidenceLevel.MEDIUM,
            ),
            RedFlag(
                category=FindingCategory.REPUTATIONAL,
                description=(
                    "Two consumer complaints on Reclame Aqui (2022), both marked resolved. "
                    "No pattern of unresolved grievances."
                ),
                severity=RiskLevel.LOW,
                evidence_url="https://www.reclameaqui.com.br/empresa/acme-components/",
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
            "Overall MEDIUM risk. No deal-killers (no sanctions, no fraud, verified physical "
            "presence and UBO). Concerns are a mid-value active lawsuit, moderate leverage, "
            "and a minor capacity overstatement — all manageable with standard contractual "
            "protections, hence a conditional proceed rather than an outright approval."
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


def _dossier_markdown(p: CompanyRiskProfile) -> str:
    flags_rows = "\n".join(
        f"| {f.category.value} | {f.severity.value.upper()} | {f.confidence.value} | "
        f"{f.description} | [source]({f.evidence_url}) |"
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

> ⚠️ ILLUSTRATIVE DEMO OUTPUT — fictional data generated by `argus-demo` to
> demonstrate the ARGUS output format. Not a real investigation.

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

---

## Recommendation

**{p.recommendation.value.replace('_', ' ').upper()}**

{p.conditions}
"""


def _briefing_markdown(p: CompanyRiskProfile) -> str:
    top = [f for f in p.red_flags if f.severity in (RiskLevel.HIGH, RiskLevel.MEDIUM)]
    bullets = "\n".join(
        f"- **[{f.severity.value.upper()}]** {f.description}" for f in top
    )
    return f"""# Executive Risk Briefing — {p.company_name}

> ⚠️ ILLUSTRATIVE DEMO OUTPUT — fictional data. Not a real investigation.

**Context.** {p.company_name} is under evaluation as a {p.engagement_type.replace('_', ' ')}
in {p.jurisdiction}. This briefing summarizes the ARGUS due diligence completed on
{p.investigation_date}.

**Key Findings.**
{bullets}

**Risk Rating: {p.overall_risk.value.upper()}.** {p.risk_rationale}

**Recommendation: {p.recommendation.value.replace('_', ' ').upper()}.**

{p.conditions}

Reviewed by: _________________________   Date: _______________
"""


def run_demo() -> CompanyRiskProfile:
    """Generate all demo outputs and write them to disk."""
    profile = build_sample_profile()

    _OUTPUTS.mkdir(exist_ok=True)
    _DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)

    profile_json = profile.model_dump(mode="json")

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
        "\n[ARGUS demo] Generated illustrative outputs:\n"
        f"  - outputs/risk_profile.json  ({len(profile.red_flags)} red flags)\n"
        "  - outputs/due_diligence_dossier.md\n"
        "  - outputs/risk_briefing.md\n"
        "  - dashboard/data/risk_profile.json  (powers the live dashboard)\n"
        f"\n  Company: {profile.company_name} | Overall risk: "
        f"{profile.overall_risk.value.upper()} | "
        f"Recommendation: {profile.recommendation.value.replace('_', ' ').upper()}\n"
        "\n  Open dashboard/index.html to see the panel.\n"
    )


if __name__ == "__main__":
    main()
