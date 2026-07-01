"""Tests for ARGUS custom CrewAI tools."""

import pytest

from argus.tools import (
    EntityConsistencyTool,
    FinancialHealthTool,
    NewsSentimentTool,
    RedFlagScorerTool,
)


class TestRedFlagScorerTool:
    def setup_method(self):
        self.tool = RedFlagScorerTool()

    def test_clean_text_returns_low(self):
        result = self.tool._run("The company has good operations and a solid team.")
        assert "low" in result

    def test_fraud_returns_high(self):
        result = self.tool._run("The CEO was indicted for fraud and money laundering.")
        assert "high" in result

    def test_medium_signals(self):
        result = self.tool._run("The company is under investigation and paid a fine last year.")
        assert "medium" in result or "high" in result

    def test_bankruptcy_returns_high(self):
        result = self.tool._run("The company filed for bankruptcy protection in 2023.")
        assert "high" in result

    def test_output_structure(self):
        result = self.tool._run("Some text about related-party transactions and disputes.")
        assert "Risk level:" in result
        assert "Flagged signals" in result

    def test_empty_text_returns_low(self):
        result = self.tool._run("   ")
        assert "low" in result


class TestFinancialHealthTool:
    def setup_method(self):
        self.tool = FinancialHealthTool()

    def test_healthy_signals(self):
        result = self.tool._run(
            "Record revenue growth this year. The company is profitable with strong balance sheet. "
            "Investment-grade credit rating confirmed."
        )
        assert "healthy" in result
        assert "low" in result

    def test_distress_signals(self):
        result = self.tool._run(
            "Going-concern opinion issued. The company faces insolvency and filed for bankruptcy. "
            "Negative cash flow for three consecutive quarters. Restatement announced."
        )
        assert "distress" in result or "high" in result

    def test_score_in_range(self):
        result = self.tool._run("Revenue growth this year with some debt.")
        # Extract score from "Financial health score: X/100"
        import re
        match = re.search(r"Financial health score: (\d+)/100", result)
        assert match is not None
        score = int(match.group(1))
        assert 0 <= score <= 100

    def test_output_structure(self):
        result = self.tool._run("Mixed financial signals in the report.")
        assert "Financial health score:" in result
        assert "Financial risk:" in result


class TestNewsSentimentTool:
    def setup_method(self):
        self.tool = NewsSentimentTool()

    def test_positive_news(self):
        result = self.tool._run(
            "Company wins industry award for innovation. Record revenue growth. "
            "Successful partnership with major retailer. Expansion announced."
        )
        assert "positive" in result

    def test_negative_news(self):
        result = self.tool._run(
            "CEO accused of fraud. Massive layoffs announced. Company faces lawsuit. "
            "Regulatory breach confirmed. Crisis management team deployed."
        )
        assert "negative" in result

    def test_mixed_news(self):
        result = self.tool._run(
            "Company grows revenue but faces criticism. New product launch amid controversy."
        )
        # Should be mixed or leaning one way
        assert "Sentiment score:" in result

    def test_score_range(self):
        result = self.tool._run("Company posts record profits and wins award.")
        import re
        match = re.search(r"Sentiment score: ([+-]?\d+)/100", result)
        assert match is not None
        score = int(match.group(1))
        assert -100 <= score <= 100

    def test_output_structure(self):
        result = self.tool._run("Some news text here.")
        assert "Sentiment score:" in result
        assert "Reputational risk signal:" in result


class TestEntityConsistencyTool:
    def setup_method(self):
        self.tool = EntityConsistencyTool()

    def test_clean_entity_returns_consistent(self):
        result = self.tool._run(
            "Company registered at 123 Main St, São Paulo. Director: João Silva. "
            "CNPJ: 12.345.678/0001-99. Active registration confirmed."
        )
        assert "CONSISTENT" in result

    def test_shell_company_flag(self):
        result = self.tool._run(
            "The company appears to be a shell company with nominee directors "
            "and offshore registration."
        )
        assert "INCONSISTENCIES_FOUND" in result
        assert "shell" in result.lower() or "Shell" in result

    def test_ubo_unknown_flag(self):
        result = self.tool._run(
            "The ultimate beneficiary is unknown. Offshore structure present. "
            "Nominee director identified."
        )
        assert "INCONSISTENCIES_FOUND" in result

    def test_no_record_flag(self):
        result = self.tool._run("No record found in the corporate registry for this entity.")
        assert "INCONSISTENCIES_FOUND" in result
        assert "HIGH" in result

    def test_output_structure_inconsistent(self):
        result = self.tool._run(
            "Different address found in two different registries. "
            "Name variation detected between sources."
        )
        assert "INCONSISTENCIES_FOUND" in result
