from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _is_mock() -> bool:
    return os.getenv("ARGUS_MOCK_SOURCES", "false").lower() == "true"


def _uses_local_llm() -> bool:
    # Ollama (or any local model) needs no OpenAI key.
    model = (os.getenv("ARGUS_LLM_MODEL") or "").lower()
    return model.startswith("ollama/") or bool(os.getenv("ARGUS_LLM_BASE_URL"))


def _validate_env() -> None:
    required = []
    if not _uses_local_llm():
        required.append("OPENAI_API_KEY")
    # Serper is only needed when hitting the real search API (not in mock-sources mode).
    if not _is_mock():
        required.append("SERPER_API_KEY")

    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(
            f"[ARGUS] ERROR: Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your keys.\n"
            "Tips: set ARGUS_MOCK_SOURCES=true to skip Serper (mocked sources), or\n"
            "      set ARGUS_LLM_MODEL=ollama/<model> to run a local LLM with no OpenAI key.\n"
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

    # Scope the guardrailed scrape tool to this target's official site.
    os.environ["ARGUS_OFFICIAL_SITE"] = company_website

    # Late import so env is loaded before crewai initializes its LLM stack
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

    _persist_profile(result, outputs_dir)

    print(
        f"\n{'=' * 60}\n"
        f"  ARGUS — Investigation Complete\n"
        f"{'=' * 60}\n"
        f"  Outputs saved to: {outputs_dir.resolve()}\n"
        f"    - due_diligence_dossier.md\n"
        f"    - risk_briefing.md\n"
        f"    - risk_profile.json  (typed profile + processing metadata)\n"
        f"{'=' * 60}\n"
    )

    return result


def _persist_profile(result, outputs_dir: Path) -> None:
    """
    Write the typed CompanyRiskProfile to risk_profile.json and stamp the processing model
    (imitating a real crew run's trace). Best-effort: the crew writes the dossier .md, but
    the structured JSON is extracted from the run result here.
    """
    import json

    profile_dict = None
    # crewai exposes the structured output in a few ways depending on version.
    for attr in ("json_dict", "to_dict"):
        obj = getattr(result, attr, None)
        if callable(obj):
            try:
                profile_dict = obj()
                break
            except Exception:
                continue
        elif isinstance(obj, dict):
            profile_dict = obj
            break
    if profile_dict is None and getattr(result, "pydantic", None) is not None:
        try:
            profile_dict = result.pydantic.model_dump(mode="json")
        except Exception:
            profile_dict = None
    if not isinstance(profile_dict, dict):
        return  # nothing structured to persist; the .md files are still written by the crew

    model = os.getenv("ARGUS_LLM_MODEL") or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    profile_dict["analysis_model"] = model
    profile_dict["source_mode"] = "mocked-sources" if _is_mock() else "live"

    text = json.dumps(profile_dict, indent=2, ensure_ascii=False)
    (outputs_dir / "risk_profile.json").write_text(text, encoding="utf-8")

    dashboard_data = Path("dashboard") / "data"
    if dashboard_data.exists():
        (dashboard_data / "risk_profile.json").write_text(text, encoding="utf-8")
        (dashboard_data / "risk_profile.js").write_text(
            "// Auto-generated by a live ARGUS run.\n"
            f"window.ARGUS_DATA = {text};\n",
            encoding="utf-8",
        )


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
