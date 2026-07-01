"""Tests for ARGUS Pydantic models."""

import pytest
from pydantic import ValidationError

from argus.models.risk_profile import (
    CompanyRiskProfile,
    ConfidenceLevel,
    DimensionRisk,
    FindingCategory,
    Recommendation,
    RedFlag,
    RiskLevel,
)


def make_dimension(risk: RiskLevel = RiskLevel.MEDIUM) -> DimensionRisk:
    return DimensionRisk(
        risk_level=risk,
        score=60,
        summary="Test dimension summary.",
        top_findings=["Finding A", "Finding B"],
    )


def make_red_flag(**kwargs) -> RedFlag:
    defaults = dict(
        category=FindingCategory.FINANCIAL,
        description="Test red flag description.",
        severity=RiskLevel.MEDIUM,
        evidence_url="https://example.com/source",
        confidence=ConfidenceLevel.HIGH,
    )
    defaults.update(kwargs)
    return RedFlag(**defaults)


class TestRedFlag:
    def test_valid(self):
        flag = make_red_flag()
        assert flag.category == FindingCategory.FINANCIAL
        assert flag.severity == RiskLevel.MEDIUM

    def test_all_categories(self):
        for cat in FindingCategory:
            flag = make_red_flag(category=cat)
            assert flag.category == cat

    def test_all_severities(self):
        for sev in RiskLevel:
            flag = make_red_flag(severity=sev)
            assert flag.severity == sev

    def test_requires_evidence_url(self):
        with pytest.raises(ValidationError):
            RedFlag(
                category=FindingCategory.LEGAL,
                description="No URL",
                severity=RiskLevel.HIGH,
                confidence=ConfidenceLevel.MEDIUM,
            )


class TestDimensionRisk:
    def test_valid(self):
        dim = make_dimension()
        assert dim.risk_level == RiskLevel.MEDIUM
        assert 0 <= dim.score <= 100

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            DimensionRisk(risk_level=RiskLevel.LOW, score=101, summary="x")
        with pytest.raises(ValidationError):
            DimensionRisk(risk_level=RiskLevel.LOW, score=-1, summary="x")


class TestCompanyRiskProfile:
    def _base(self, **kwargs) -> dict:
        base = dict(
            company_name="Acme Test Ltd",
            engagement_type="new_supplier",
            jurisdiction="Brazil",
            investigation_date="2026-07-01",
            overall_risk=RiskLevel.MEDIUM,
            financial_score=65,
            financial=make_dimension(RiskLevel.LOW),
            reputational=make_dimension(RiskLevel.MEDIUM),
            legal=make_dimension(RiskLevel.LOW),
            operational=make_dimension(RiskLevel.MEDIUM),
            red_flags=[make_red_flag()],
            verified=True,
            human_reviewed=True,
            recommendation=Recommendation.PROCEED_WITH_CONDITIONS,
            conditions="Require monthly financial reporting for the first year.",
            risk_rationale="Medium risk due to limited public financial data.",
        )
        base.update(kwargs)
        return base

    def test_valid_profile(self):
        profile = CompanyRiskProfile(**self._base())
        assert profile.company_name == "Acme Test Ltd"
        assert profile.recommendation == Recommendation.PROCEED_WITH_CONDITIONS
        assert profile.verified is True

    def test_financial_score_bounds(self):
        with pytest.raises(ValidationError):
            CompanyRiskProfile(**self._base(financial_score=101))
        with pytest.raises(ValidationError):
            CompanyRiskProfile(**self._base(financial_score=-1))

    def test_all_recommendations(self):
        for rec in Recommendation:
            profile = CompanyRiskProfile(**self._base(recommendation=rec))
            assert profile.recommendation == rec

    def test_empty_red_flags_allowed(self):
        profile = CompanyRiskProfile(**self._base(red_flags=[]))
        assert profile.red_flags == []

    def test_json_serialization(self):
        profile = CompanyRiskProfile(**self._base())
        json_str = profile.model_dump_json()
        assert "Acme Test Ltd" in json_str
        assert "proceed_with_conditions" in json_str

    def test_conditions_optional_for_proceed(self):
        profile = CompanyRiskProfile(**self._base(
            recommendation=Recommendation.PROCEED,
            conditions=None,
        ))
        assert profile.conditions is None
