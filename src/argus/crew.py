from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Process, Task
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    MDXSearchTool,
    ScrapeWebsiteTool,
    SerperDevTool,
    WebsiteSearchTool,
)
from langchain_openai import ChatOpenAI

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
        self._memory = os.getenv("ARGUS_MEMORY", "true").lower() == "true"

    # ── LLM helpers ───────────────────────────────────────────────────────────

    def _agent_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.2")),
        )

    def _manager_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=os.getenv("MANAGER_MODEL_NAME", "gpt-4o"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.2")),
        )

    # ── Shared tools ──────────────────────────────────────────────────────────

    def _tools_search(self) -> list:
        return [SerperDevTool()]

    def _tools_scrape(self) -> list:
        return [ScrapeWebsiteTool()]

    def _tools_intake(self) -> list:
        tools = [DirectoryReadTool(directory=str(_PLAYBOOKS_DIR)), FileReadTool()]
        return tools

    def _tools_financial(self) -> list:
        return [SerperDevTool(), ScrapeWebsiteTool(), FinancialHealthTool()]

    def _tools_reputational(self) -> list:
        return [SerperDevTool(), WebsiteSearchTool(), NewsSentimentTool()]

    def _tools_legal(self) -> list:
        return [SerperDevTool(), ScrapeWebsiteTool(), EntityConsistencyTool()]

    def _tools_operational(self) -> list:
        return [SerperDevTool(), ScrapeWebsiteTool(), RedFlagScorerTool()]

    def _tools_qa(self) -> list:
        if _POLICIES_FILE.exists():
            return [MDXSearchTool(mdx=str(_POLICIES_FILE))]
        return []

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
