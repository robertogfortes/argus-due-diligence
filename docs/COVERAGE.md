# Spec Coverage — "Não Esquecemos de Nada"

This maps every concept from the ARGUS spec (`Projeto_ARGUS_DueDiligence_CrewAI_SDD_BMAD.md`,
section 12) to where it lives in the codebase. **35/35 covered.**

| # | Concept (course) | Where in ARGUS |
|---|---|---|
| 1 | Agent (role/goal/backstory) | [config/agents.yaml](../src/argus/config/agents.yaml) — 9 agents; built in [crew.py](../src/argus/crew.py) |
| 2 | Task (description/expected_output/agent) | [config/tasks.yaml](../src/argus/config/tasks.yaml) — 8 tasks |
| 3 | Crew (agents/tasks/verbose) | `ArgusCrew.crew()` in [crew.py](../src/argus/crew.py) |
| 4 | `kickoff(inputs={})` + `{var}` interpolation | [main.py](../src/argus/main.py) `kickoff(inputs=…)`; `{target_company}`, `{engagement_type}`… in the YAML |
| 5 | Sequential process (order matters) | Intake runs first; investigations depend on its scope (via `context`) |
| 6 | Role playing + domain keywords (FINRA) | `"FINRA-informed Forensic Financial Analyst"` in agents.yaml |
| 7 | Focus (one thing per agent) | Each analyst owns exactly one dimension |
| 8 | Right tools, right amount | Tools distributed per agent/task in crew.py |
| 9 | Cooperation / delegation / feedback | `allow_delegation=True` on specialists + QA; QA delegates fixes back |
| 10 | Guardrails (framework + custom) | Framework: CrewAI defaults. Custom: [constitution.md](../constitution.md) + task prompts |
| 11 | Memory (short/long/entity, `memory=True`) | `memory=True` in crew.py (real-source mode) |
| 12 | `allow_delegation` True/False | Intake=`False`; specialists & QA=`True` |
| 13 | QA agent pattern (review + delegate back) | Evidence Verification Specialist (Squad 3) |
| 14 | `SerperDevTool` / `ScrapeWebsiteTool` / `WebsiteSearchTool` | `_tools_*` in crew.py |
| 15 | `DirectoryReadTool` / `FileReadTool` | Intake tools (reads `./playbooks` + notes) |
| 16 | `MDXSearchTool` (RAG over .md) | QA tool over [policies.md](../policies.md) (real-source mode) |
| 17 | Tool-scoping as guardrail (1 URL) | `_scoped_scrape_tool()` locks scrape to the official site |
| 18 | Task-level tools override agent-level | `operational_task` sets its own `tools=[…]` in crew.py |
| 19 | Custom tools via `BaseTool` (name/description/_run) | [tools/](../src/argus/tools/) — 4 tools with typed schemas |
| 20 | Versatility + fault tolerance + cache | Typed tool inputs; CrewAI fault tolerance + cross-agent cache |
| 21 | Instruction folder per type | [playbooks/](../playbooks/) — new_supplier / strategic_partner / acquisition_target |
| 22 | "Think like a manager" (agents & tasks) | Specific roles + explicit task descriptions |
| 23 | Pydantic `output_json` | `output_json=CompanyRiskProfile` on `dossier_task` |
| 24 | `human_input=True` | `verification_task` (sign off adverse findings) |
| 25 | `async_execution=True` (parallel) | The 4 investigation tasks |
| 26 | `output_file` | `dossier_task` + `briefing_task` |
| 27 | Sequential × Parallel (dependencies) | Intake (seq) → 4 investigations (async) |
| 28 | Hierarchical (`Process.hierarchical` + `manager_llm`) | `crew()` in crew.py |
| 29 | Manager keeps the objective | Chief Investigation Officer (manager_llm) |
| 30 | `context=[tasks]` (wait + consume) | QA and synthesis tasks |
| 31 | Async + sequential + context combined | Full pipeline |
| 32 | Guardrail "don't make up info" | Task prompts + constitution ("no source, no finding") |
| 33 | Multiple output files | `risk_profile.json` + `due_diligence_dossier.md` + `risk_briefing.md` |
| 34 | Model by complexity (cheap × strong) | `_agent_llm` (gpt-4o-mini) vs `_manager_llm` (gpt-4o) |
| 35 | `verbose` (max logs) | `verbose=self._verbose` on agents and crew |

## Process layer (SDD + BMAD)

| Artifact | File |
|---|---|
| Constitution (non-negotiable principles) | [constitution.md](../constitution.md) |
| Internal risk policies (QA cross-reference) | [policies.md](../policies.md) |
| Investigation playbooks per engagement type | [playbooks/](../playbooks/) |
| Typed spec of the output contract | [models/risk_profile.py](../src/argus/models/risk_profile.py) |

## Beyond the spec (production hardening)

- Offline **mocked-source mode** (`ARGUS_MOCK_SOURCES=true`) — real AI result, simulated sources.
- **Preview generator** (`python -m argus.demo`) + interactive **dashboard** with a linked
  mocked-source corpus page.
- **Multi-provider LLM** (OpenAI / Anthropic / local Ollama via `ARGUS_LLM_MODEL`).
- **CI** (ruff + pytest on Python 3.11–3.13) and **GitHub Pages** deploy.
