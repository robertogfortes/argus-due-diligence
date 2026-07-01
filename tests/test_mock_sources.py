"""Tests for the mocked-source tools and the fixture corpus."""

from argus.mock_sources import (
    SOURCE_PAGES,
    MockScrapeTool,
    MockSearchTool,
    MockWebsiteSearchTool,
)


class TestSourcePages:
    def test_pages_have_required_fields(self):
        for page in SOURCE_PAGES:
            assert page["id"]
            assert page["title"]
            assert page["keywords"]
            assert page["entries"]
            for entry in page["entries"]:
                assert entry["source"]
                assert entry["date"]
                assert entry["ref"]
                assert entry["text"]

    def test_anchor_ids_are_unique(self):
        ids = [p["id"] for p in SOURCE_PAGES]
        assert len(ids) == len(set(ids))

    def test_expected_anchors_exist(self):
        ids = {p["id"] for p in SOURCE_PAGES}
        # These anchors are referenced by evidence_url in the preview output.
        for anchor in ("financials", "litigation", "operations", "reputation"):
            assert anchor in ids


class TestMockSearchTool:
    def setup_method(self):
        self.tool = MockSearchTool()

    def test_name_matches_real_serper(self):
        # Must match SerperDevTool so agents call it identically.
        assert self.tool.name == "Search the internet with Serper"

    def test_financial_query_returns_financial_block(self):
        result = self.tool._run("what is the revenue and credit profile of the company")
        assert "142" in result or "credit" in result.lower()

    def test_litigation_query_returns_lawsuit(self):
        result = self.tool._run("any lawsuit or litigation against the company")
        assert "480" in result or "lawsuit" in result.lower() or "processo" in result.lower()

    def test_unknown_query_returns_default(self):
        result = self.tool._run("zzz totally unrelated query 12345")
        assert "No specific public records" in result

    def test_deterministic(self):
        q = "financial revenue"
        assert self.tool._run(q) == self.tool._run(q)


class TestMockScrapeTool:
    def setup_method(self):
        self.tool = MockScrapeTool()

    def test_name_matches_real_scrape(self):
        assert self.tool.name == "Read website content"

    def test_official_site_returns_company_content(self):
        result = self.tool._run("https://www.acmecomponents.com.br")
        assert "Acme Components" in result
        assert "250+" in result  # the overstated headcount claim, for the agent to catch

    def test_court_url_returns_case(self):
        result = self.tool._run("https://esaj.tjsp.jus.br/case")
        assert "480.000" in result or "ANDAMENTO" in result

    def test_unknown_url_returns_default(self):
        result = self.tool._run("https://unknown-domain.example")
        assert "not reachable" in result.lower()


class TestMockWebsiteSearchTool:
    def test_returns_site_text(self):
        result = MockWebsiteSearchTool()._run("employees")
        assert "Acme Components" in result
