from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _validate_env() -> None:
    missing = [k for k in ("OPENAI_API_KEY", "SERPER_API_KEY") if not os.getenv(k)]
    if missing:
        print(
            f"[ARGUS] ERROR: Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your API keys.\n"
            "Get a free Serper key at https://serper.dev",
            file=sys.stderr,
        )
        sys.exit(1)


def run(
    target_company: str,
    company_website: str,
    engagement_type: str,
    jurisdiction: str,
    risk_appetite: str,
    company_size: str,
) -> None:
    """
    Launch a full ARGUS due diligence investigation.

    Args:
        target_company:  Legal name of the company to investigate.
        company_website: Official website URL of the target.
        engagement_type: One of: new_supplier | strategic_partner | acquisition_target
        jurisdiction:    Primary jurisdiction (e.g. "Brazil", "United States", "EU - France").
        risk_appetite:   Caller's risk appetite: Low | Medium | High
        company_size:    Approximate size (e.g. "SME (50-500 employees)", "Large (>500 employees)").
    """
    _validate_env()

    # Late import so env is loaded before crewai initializes LangChain
    from argus.crew import ArgusCrew

    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    inputs = {
        "target_company": target_company,
        "company_website": company_website,
        "engagement_type": engagement_type,
        "jurisdiction": jurisdiction,
        "risk_appetite": risk_appetite,
        "company_size": company_size,
        "investigation_date": date.today().isoformat(),
    }

    print(
        f"\n{'=' * 60}\n"
        f"  ARGUS — Due Diligence Investigation\n"
        f"{'=' * 60}\n"
        f"  Target:      {target_company}\n"
        f"  Website:     {company_website}\n"
        f"  Type:        {engagement_type}\n"
        f"  Jurisdiction:{jurisdiction}\n"
        f"  Size:        {company_size}\n"
        f"  Risk appetite:{risk_appetite}\n"
        f"  Date:        {inputs['investigation_date']}\n"
        f"{'=' * 60}\n"
    )

    result = ArgusCrew().crew().kickoff(inputs=inputs)

    print(
        f"\n{'=' * 60}\n"
        f"  ARGUS — Investigation Complete\n"
        f"{'=' * 60}\n"
        f"  Outputs saved to: {outputs_dir.resolve()}\n"
        f"    - due_diligence_dossier.md\n"
        f"    - risk_briefing.md\n"
        f"    - risk_profile.json  (if Pydantic output succeeded)\n"
        f"{'=' * 60}\n"
    )

    return result


def main() -> None:
    """
    Default entry point — edit the inputs below to investigate your target company.
    Run with: python -m argus.main  OR  argus  (if installed with pip install -e .)
    """
    run(
        target_company="Acme Components Ltda",
        company_website="https://www.acmecomponents.com.br",
        engagement_type="new_supplier",
        jurisdiction="Brazil",
        risk_appetite="Medium",
        company_size="SME (50-500 employees)",
    )


if __name__ == "__main__":
    main()
