from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingCategory(str, Enum):
    FINANCIAL = "financial"
    LEGAL = "legal"
    REPUTATIONAL = "reputational"
    OPERATIONAL = "operational"


class Recommendation(str, Enum):
    PROCEED = "proceed"
    PROCEED_WITH_CONDITIONS = "proceed_with_conditions"
    DECLINE = "decline"


class RedFlag(BaseModel):
    category: FindingCategory = Field(..., description="Investigation dimension")
    description: str = Field(..., description="Clear description of what was found")
    severity: RiskLevel = Field(..., description="Impact severity of this finding")
    evidence_url: str = Field(
        ..., description="Source URL, document name, or registry reference"
    )
    confidence: ConfidenceLevel = Field(
        ..., description="Analyst confidence in this finding"
    )


class DimensionRisk(BaseModel):
    risk_level: RiskLevel
    score: int = Field(..., ge=0, le=100, description="0=max risk, 100=no risk")
    summary: str = Field(..., description="One-sentence summary of dimension findings")
    top_findings: list[str] = Field(
        default_factory=list, description="Top 3 findings for this dimension"
    )


class CompanyRiskProfile(BaseModel):
    """Typed risk profile produced at the end of every ARGUS investigation."""

    company_name: str = Field(..., description="Target company legal name")
    engagement_type: str = Field(
        ..., description="Type of engagement: new_supplier | strategic_partner | acquisition_target"
    )
    jurisdiction: str = Field(..., description="Primary jurisdiction investigated")
    investigation_date: str = Field(..., description="ISO 8601 date (YYYY-MM-DD)")

    overall_risk: RiskLevel = Field(..., description="Aggregate risk rating across all dimensions")
    financial_score: int = Field(
        ..., ge=0, le=100, description="Financial health score (0=distressed, 100=very healthy)"
    )

    financial: DimensionRisk = Field(..., description="Financial dimension assessment")
    reputational: DimensionRisk = Field(..., description="Reputational dimension assessment")
    legal: DimensionRisk = Field(..., description="Legal & compliance dimension assessment")
    operational: DimensionRisk = Field(..., description="Operational dimension assessment")

    red_flags: list[RedFlag] = Field(
        default_factory=list, description="All red flags found, ordered by severity"
    )

    verified: bool = Field(
        ..., description="Whether the QA verification stage was completed"
    )
    human_reviewed: bool = Field(
        ..., description="Whether HIGH severity findings were reviewed by a human analyst"
    )

    recommendation: Recommendation = Field(..., description="Final recommendation")
    conditions: str | None = Field(
        None, description="Required conditions if recommendation is proceed_with_conditions"
    )
    risk_rationale: str = Field(
        ..., description="Brief explanation of the overall risk rating and recommendation"
    )
