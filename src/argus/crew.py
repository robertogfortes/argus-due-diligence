from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    MDXSearchTool,
    ScrapeWebsiteTool,
    SerperDevTool,
    WebsiteSearchTool,
)

from argus.models.risk_profile import CompanyRiskProfile
from argus.tools import (
    EntityConsistencyTool,
    FinancialHealthTool,
    NewsSentimentTool,
    RedFlagScorerTool,
)

_HERE = Path(__file__).parent
_ROOT = _HERE.parent.parent
_PLAYBOOKS_DIR = _ROOT / "playbooks"
_POLICIES_FILE = _ROOT / "policies.md"
_OUTPUTS_DIR = _ROOT / "outputs"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class ArgusCrew:
    """
    ARGUS hierarchical due diligence crew.

    Orchestrates 8 specialist agents across 5 squads to produce:
    - CompanyRiskProfile (typed Pydantic JSON)
    - due_diligence_dossier.md
    - risk_briefing.md
    """

    def __init__(self) -> None:
        self._agents_cfg = _load_yaml(_HERE / "config" / "agents.yaml")
        self._tasks_cfg = _load_yaml(_HERE / "config" / "tasks.yaml")
        _OUTPUTS_DIR.mkdir(exist_ok=True)
        self._verbose = os.getenv("ARGUS_VERBOSE", "true").lower() == "true"
        # Mock-sources mode: fake the network lookups (search/scrape) but let the real
        # crew + LLM produce the result. Sources are mocked, the RESULT is real.
        self._mock_sources = os.getenv("ARGUS_MOCK_SOURCES", "false").lower() == "true"
        # Official site for URL-scoped scraping (a guardrail: the scoped scrape can only
        # read the target's own site). Set by main.py from the company_website input.
        self._official_site = os.getenv("ARGUS_OFFICIAL_SITE", "").strip()
        # Memory needs an embeddings provider; disable by default in mock mode so the
        # pipeline runs with any LLM provider without extra embedding credentials.
        default_memory = "false" if self._mock_sources else "true"
        self._memory = os.getenv("ARGUS_MEMORY", default_memory).lower() == "true"

    # ── LLM helpers ───────────────────────────────────────────────────────────

    def _make_llm(self, model: str) -> LLM:
        # base_url lets you point at a local Ollama server or any OpenAI-compatible endpoint.
        base_url = os.getenv("ARGUS_LLM_BASE_URL") or None
        kwargs: dict[str, Any] = {
            "model": model,
            "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.2")),
        }
        if base_url:
            kwargs["base_url"] = base_url
        return LLM(**kwargs)

    def _agent_llm(self) -> LLM:
        # ARGUS_LLM_MODEL wins (any provider, e.g. ollama/llama3.1); OPENAI_MODEL_NAME is the
        # OpenAI-specific fallback. Cheaper model for the specialists.
        model = os.getenv("ARGUS_LLM_MODEL") or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        return self._make_llm(model)

    def _manager_llm(self) -> LLM:
        # Stronger model for the Chief Investigation Officer (manager).
        model = os.getenv("ARGUS_MANAGER_MODEL") or os.getenv("MANAGER_MODEL_NAME", "gpt-4o")
        return self._make_llm(model)

    # ── Source tools (real network vs. mocked fixtures) ───────────────────────

    def _search_tool(self):
        if self._mock_sources:
            from argus.mock_sources import MockSearchTool

            return MockSearchTool()
        return SerperDevTool()

    def _scrape_tool(self):
        if self._mock_sources:
            from argus.mock_sources import MockScrapeTool

            return MockScrapeTool()
        return ScrapeWebsiteTool()

    def _scoped_scrape_tool(self):
        """Guardrail: a scrape tool locked to the target's official website (tool-scoping)."""
        if self._mock_sources:
            from argus.mock_sources import MockScrapeTool

            return MockScrapeTool()
        if self._official_site:
            return ScrapeWebsiteTool(website_url=self._official_site)
        return ScrapeWebsiteTool()

    def _website_search_tool(self):
        if self._mock_sources:
            from argus.mock_sources import MockWebsiteSearchTool

            return MockWebsiteSearchTool()
        return WebsiteSearchTool()

    # ── Per-agent tool sets ───────────────────────────────────────────────────

    def _tools_intake(self) -> list:
        return [DirectoryReadTool(directory=str(_PLAYBOOKS_DIR)), FileReadTool()]

    def _tools_financial(self) -> list:
        return [self._search_tool(), self._scrape_tool(), FinancialHealthTool()]

    def _tools_reputational(self) -> list:
        return [self._search_tool(), self._website_search_tool(), NewsSentimentTool()]

    def _tools_legal(self) -> list:
        return [self._search_tool(), self._scrape_tool(), EntityConsistencyTool()]

    def _tools_operational(self) -> list:
        return [self._search_tool(), self._scrape_tool(), RedFlagScorerTool()]

    def _tools_qa(self) -> list:
        # MDXSearchTool builds an OpenAI-embedded index; in mock mode we read the policy
        # file directly so QA works with any LLM provider and no embedding credentials.
        if not _POLICIES_FILE.exists():
            return []
        if self._mock_sources:
            return [FileReadTool()]
        return [MDXSearchTool(mdx=str(_POLICIES_FILE))]

    # ── Agents — Squad 1: Intake ──────────────────────────────────────────────

    def _intake_analyst(self) -> Agent:
        cfg = self._agents_cfg["intake_analyst"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=self._tools_intake(),
            allow_delegation=False,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    # ── Agents — Squad 2: Investigation (parallel) ───────────────────────────

    def _forensic_financial_analyst(self) -> Agent:
        cfg = self._agents_cfg["forensic_financial_analyst"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=self._tools_financial(),
            allow_delegation=True,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    def _reputation_intelligence_analyst(self) -> Agent:
        cfg = self._agents_cfg["reputation_intelligence_analyst"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=self._tools_reputational(),
            allow_delegation=True,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    def _legal_compliance_researcher(self) -> Agent:
        cfg = self._agents_cfg["legal_compliance_researcher"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=self._tools_legal(),
            allow_delegation=True,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    def _operational_footprint_analyst(self) -> Agent:
        cfg = self._agents_cfg["operational_footprint_analyst"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=self._tools_operational(),
            allow_delegation=True,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    # ── Agents — Squad 3: QA / Verification ──────────────────────────────────

    def _evidence_verification_specialist(self) -> Agent:
        cfg = self._agents_cfg["evidence_verification_specialist"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=self._tools_qa(),
            allow_delegation=True,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    # ── Agents — Squad 4: Synthesis & Report ─────────────────────────────────

    def _risk_dossier_strategist(self) -> Agent:
        cfg = self._agents_cfg["risk_dossier_strategist"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            allow_delegation=False,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    def _executive_briefing_editor(self) -> Agent:
        cfg = self._agents_cfg["executive_briefing_editor"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            allow_delegation=False,
            llm=self._agent_llm(),
            verbose=self._verbose,
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def _build_tasks(
        self,
        intake: Agent,
        financial: Agent,
        reputational: Agent,
        legal: Agent,
        operational: Agent,
        qa: Agent,
        strategist: Agent,
        editor: Agent,
    ) -> list[Task]:
        tc = self._tasks_cfg

        # Squad 1 — Intake (sequential-first, others depend on it)
        intake_task = Task(
            description=tc["intake_task"]["description"],
            expected_output=tc["intake_task"]["expected_output"],
            agent=intake,
        )

        # Squad 2 — Investigation (4 parallel async tasks)
        financial_task = Task(
            description=tc["financial_investigation_task"]["description"],
            expected_output=tc["financial_investigation_task"]["expected_output"],
            agent=financial,
            async_execution=True,
        )

        reputational_task = Task(
            description=tc["reputational_investigation_task"]["description"],
            expected_output=tc["reputational_investigation_task"]["expected_output"],
            agent=reputational,
            async_execution=True,
        )

        legal_task = Task(
            description=tc["legal_investigation_task"]["description"],
            expected_output=tc["legal_investigation_task"]["expected_output"],
            agent=legal,
            async_execution=True,
        )

        operational_task = Task(
            description=tc["operational_investigation_task"]["description"],
            expected_output=tc["operational_investigation_task"]["expected_output"],
            agent=operational,
            async_execution=True,
            # Task-level tools override the agent's tools for this task. Here we swap in a
            # URL-scoped scrape (guardrail: can only read the target's official site).
            tools=[self._search_tool(), self._scoped_scrape_tool(), RedFlagScorerTool()],
        )

        # Squad 3 — QA / Verification (waits for all 4, pauses for human review)
        verification_task = Task(
            description=tc["verification_task"]["description"],
            expected_output=tc["verification_task"]["expected_output"],
            agent=qa,
            context=[financial_task, reputational_task, legal_task, operational_task],
            human_input=True,
        )

        # Squad 4 — Synthesis (consumes everything)
        dossier_task = Task(
            description=tc["dossier_task"]["description"],
            expected_output=tc["dossier_task"]["expected_output"],
            agent=strategist,
            context=[
                intake_task,
                financial_task,
                reputational_task,
                legal_task,
                operational_task,
                verification_task,
            ],
            output_json=CompanyRiskProfile,
            output_file=str(_OUTPUTS_DIR / "due_diligence_dossier.md"),
        )

        briefing_task = Task(
            description=tc["briefing_task"]["description"],
            expected_output=tc["briefing_task"]["expected_output"],
            agent=editor,
            context=[intake_task, dossier_task],
            output_file=str(_OUTPUTS_DIR / "risk_briefing.md"),
        )

        return [
            intake_task,
            financial_task,
            reputational_task,
            legal_task,
            operational_task,
            verification_task,
            dossier_task,
            briefing_task,
        ]

    # ── Crew ──────────────────────────────────────────────────────────────────

    def crew(self) -> Crew:
        """Build and return the fully wired ARGUS hierarchical crew."""

        # Instantiate all agents
        intake = self._intake_analyst()
        financial = self._forensic_financial_analyst()
        reputational = self._reputation_intelligence_analyst()
        legal = self._legal_compliance_researcher()
        operational = self._operational_footprint_analyst()
        qa = self._evidence_verification_specialist()
        strategist = self._risk_dossier_strategist()
        editor = self._executive_briefing_editor()

        agents = [intake, financial, reputational, legal, operational, qa, strategist, editor]
        tasks = self._build_tasks(
            intake, financial, reputational, legal, operational, qa, strategist, editor
        )

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.hierarchical,
            manager_llm=self._manager_llm(),
            memory=self._memory,
            verbose=self._verbose,
        )
