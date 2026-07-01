"""
Mock source tools for ARGUS.

These replace the *network* tools (Serper search, website scrape, website RAG) with
deterministic, offline fixtures — WITHOUT touching the reasoning layer. When the crew runs
with ARGUS_MOCK_SOURCES=true and a valid LLM key, the agents still perform real analysis:
they read these fixture sources and the LLM genuinely produces the findings, scores, and
recommendation. Only the raw source lookups are faked (no Serper cost, fully reproducible).

In other words: the SOURCES are mocked, the RESULT is real.

`SOURCE_PAGES` is the single source of truth for the fixture corpus. It powers:
  1. the mock search/scrape tools below, and
  2. the human-viewable sources page (dashboard/sources.html), so that every "source" link
     on a finding leads to the actual mocked source inside this project.

The fixture is a fictional company, "Acme Components Ltda", seeded with realistic signals
across all four dimensions so a competent agent has genuine material to investigate.
"""

from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# ── Structured fixture corpus (single source of truth) ────────────────────────
# Each page has an anchor id (used by evidence_url as sources.html#<id>), a title,
# keyword triggers for the mock search tool, and a list of simulated source entries.

SOURCE_PAGES: list[dict] = [
    {
        "id": "financials",
        "title": "Financial signals",
        "keywords": ("financ", "revenue", "faturamento", "balanço", "receita", "annual",
                     "demonstr", "credit", "serasa", "leverage", "debt"),
        "entries": [
            {
                "source": "Valor Setorial",
                "date": "2025-03-11",
                "ref": "valorsetorial.com.br/acme-2024",
                "text": "Acme Components divulga receita de R$ 142 mi em 2024 — crescimento "
                        "~6% a/a. Empresa é de capital fechado e não publica demonstrações "
                        "auditadas completas; direção cita 'carteira de pedidos estável'.",
            },
            {
                "source": "Serasa Experian (resumo público)",
                "date": "2025-01-20",
                "ref": "serasa.com.br/empresas/acme-components",
                "text": "Perfil de crédito: moderado. Estimativa de dívida/patrimônio acima "
                        "da mediana do setor de autopeças; nenhum default registrado.",
            },
            {
                "source": "JUCESP — ficha cadastral",
                "date": "2024-11-02",
                "ref": "jucesp.sp.gov.br/acme",
                "text": "Dois sócios declarados; beneficiário final identificado e residente "
                        "no Brasil. Nenhuma holding offshore detectada.",
            },
        ],
    },
    {
        "id": "litigation",
        "title": "Litigation & sanctions",
        "keywords": ("lawsuit", "litig", "process", "court", "tribunal", "legal", "ação",
                     "acao", "judicial", "sanction", "sanções", "sancoes", "ofac"),
        "entries": [
            {
                "source": "TJSP / e-SAJ",
                "date": "2024-06-14",
                "ref": "esaj.tjsp.jus.br/cposg/search.do?processo=1023xxx",
                "text": "Processo nº 1023xxx-45.2024.8.26 — ATIVO. Um fornecedor alega "
                        "inadimplemento contratual; valor da causa ~R$ 480.000. Distribuído "
                        "em 2024, ainda não julgado.",
            },
            {
                "source": "Portal da Transparência / CGU",
                "date": "2025-02-01",
                "ref": "portaltransparencia.gov.br",
                "text": "Sem registros em CEIS/CNEP (sem inidoneidade/impedimento). "
                        "Nenhuma sanção administrativa.",
            },
            {
                "source": "OFAC SDN / EU consolidated list",
                "date": "2025-02-01",
                "ref": "sanctionssearch.ofac.treas.gov",
                "text": "Nenhuma correspondência na lista OFAC SDN nem na lista consolidada "
                        "da União Europeia.",
            },
        ],
    },
    {
        "id": "registration",
        "title": "Corporate registration",
        "keywords": ("cnpj", "registration", "registro", "cadastr", "receita federal",
                     "entity", "socios", "sócios", "endereço", "endereco"),
        "entries": [
            {
                "source": "Receita Federal — CNPJ",
                "date": "2025-01-05",
                "ref": "receita.fazenda.gov.br",
                "text": "CNPJ 12.345.678/0001-99 — ACME COMPONENTS LTDA — Situação: ATIVA. "
                        "Endereço: Av. Industrial 1200, Diadema/SP. CNAE principal: "
                        "fabricação de peças e acessórios para veículos. Abertura: 2011.",
            },
            {
                "source": "JUCESP",
                "date": "2024-11-02",
                "ref": "jucesp.sp.gov.br/acme",
                "text": "Razão social e endereço consistentes com a Receita Federal. Sem "
                        "variações de nome; sem flags de empresa dormente ou laranja. "
                        "Registro ativo desde 2011.",
            },
        ],
    },
    {
        "id": "reputation",
        "title": "Reputation & media",
        "keywords": ("news", "reputation", "media", "notícia", "noticia", "scandal",
                     "reclam", "sentiment", "iso", "certif"),
        "entries": [
            {
                "source": "Automotive Business",
                "date": "2023-08-02",
                "ref": "automotivebusiness.com.br/acme-iso",
                "text": "Acme Components conquista certificação ISO 9001 — cobertura "
                        "positiva de imprensa setorial sobre gestão de qualidade.",
            },
            {
                "source": "Reclame Aqui",
                "date": "2022-09-10",
                "ref": "reclameaqui.com.br/empresa/acme-components",
                "text": "Duas reclamações de consumidor em 2022, ambas marcadas como "
                        "RESOLVIDAS. Reputação 'Bom'. Nenhum padrão de problemas recorrentes.",
            },
            {
                "source": "Busca de mídia adversa (g1, Valor, Estadão)",
                "date": "2025-02-10",
                "ref": "news search — 5-year lookback",
                "text": "Nenhuma mídia adversa sobre fraude, suborno, corrupção ou incidentes "
                        "de segurança encontrada em busca de 5 anos.",
            },
        ],
    },
    {
        "id": "operations",
        "title": "Operations & workforce",
        "keywords": ("employ", "funcion", "headcount", "linkedin", "capacity", "operac",
                     "operation", "supply", "factory", "fábrica", "fabrica", "vagas", "job"),
        "entries": [
            {
                "source": "LinkedIn — company page",
                "date": "2025-02-08",
                "ref": "linkedin.com/company/acme-components",
                "text": "Página lista '51-200 funcionários'; ~180 perfis associados. "
                        "Sede em Diadema/SP.",
            },
            {
                "source": "Gupy / job boards",
                "date": "2025-02-07",
                "ref": "gupy.io/acme-components",
                "text": "Diversas vagas abertas em produção e qualidade — consistente com "
                        "uma planta de autopeças em operação.",
            },
            {
                "source": "Registro do organismo certificador ISO",
                "date": "2024-12-01",
                "ref": "certifier-registry/acme",
                "text": "Certificado ISO 9001 ativo e verificado para a unidade de Diadema. "
                        "OBS.: o site da empresa afirma '250+ funcionários', acima dos "
                        "sinais de LinkedIn/job boards (~180).",
            },
        ],
    },
]

# Official website content, returned by the mock scrape tool for the company domain.
_SITE_TEXT = (
    "[Website content — https://www.acmecomponents.com.br]\n"
    'Acme Components Ltda — "Precision auto parts since 2011."\n'
    'About: "We are a leading Brazilian manufacturer of precision automotive components, '
    'with 250+ employees and a state-of-the-art facility in Diadema, São Paulo."\n'
    "Certifications: ISO 9001 (quality management).\n"
    'Customers: "We supply major Tier-1 automotive assemblers across Mercosul."\n'
    "Contact: Av. Industrial 1200, Diadema/SP · contato@acmecomponents.com.br"
)

# Per-URL scrape responses for registry/court pages referenced in search results.
_SITE_CORPUS: dict[str, str] = {
    "acmecomponents": _SITE_TEXT,
    "esaj.tjsp": (
        "[Website content — TJSP e-SAJ]\n"
        "Processo nº 1023xxx-45.2024.8.26.0100 — Procedimento Comum Cível. "
        "Partes: [Fornecedor] x ACME COMPONENTS LTDA. Assunto: inadimplemento contratual. "
        "Valor da causa: R$ 480.000,00. Situação: EM ANDAMENTO (não julgado). Distribuído 2024."
    ),
    "receita.fazenda": (
        "[Website content — Receita Federal CNPJ]\n"
        "CNPJ 12.345.678/0001-99 — ACME COMPONENTS LTDA — Situação cadastral: ATIVA. "
        "Endereço: Av. Industrial 1200, Diadema/SP. Abertura: 2011."
    ),
}


def _page_as_text(page: dict) -> str:
    lines = [f"[Search results — {page['title']}]"]
    for i, e in enumerate(page["entries"], 1):
        lines.append(f"{i}. {e['source']} ({e['date']}) — {e['ref']}\n   {e['text']}")
    return "\n".join(lines)


_DEFAULT_SEARCH = (
    "[Search results] No specific public records matched this query for Acme Components Ltda. "
    "The company is a privately held Brazilian auto-parts manufacturer; some data is limited. "
    "Try queries about: financials, litigation, registration, reputation/news, or operations."
)

_DEFAULT_SITE = (
    "[Website content] Page not reachable in offline mode. Known official domain: "
    "acmecomponents.com.br."
)


class _SearchInput(BaseModel):
    search_query: str = Field(..., description="The search query string.")


class MockSearchTool(BaseTool):
    name: str = "Search the internet with Serper"
    description: str = (
        "A tool to search the internet. Input a search query and get back relevant results "
        "(titles, snippets, and URLs). Use it to research a company's financials, litigation, "
        "corporate registration, reputation, and operations."
    )
    args_schema: type[BaseModel] = _SearchInput

    def _run(self, search_query: str) -> str:
        q = (search_query or "").lower()
        blocks = [_page_as_text(p) for p in SOURCE_PAGES if any(k in q for k in p["keywords"])]
        return "\n\n".join(blocks) if blocks else _DEFAULT_SEARCH


class _ScrapeInput(BaseModel):
    website_url: str = Field(..., description="The URL of the website to read.")


class MockScrapeTool(BaseTool):
    name: str = "Read website content"
    description: str = (
        "A tool to read the content of a website. Input a URL and get back the page text. "
        "Use it to verify claims on a company's official site or public registry pages."
    )
    args_schema: type[BaseModel] = _ScrapeInput

    def _run(self, website_url: str) -> str:
        u = (website_url or "").lower()
        for key, text in _SITE_CORPUS.items():
            if key in u:
                return text
        return _DEFAULT_SITE


class MockWebsiteSearchTool(BaseTool):
    name: str = "Search in a specific website"
    description: str = (
        "A tool to semantically search the content of a specific website. Input a query and, "
        "optionally, a website URL, and get back the most relevant passages."
    )
    args_schema: type[BaseModel] = _SearchInput

    def _run(self, search_query: str) -> str:
        return _SITE_TEXT
