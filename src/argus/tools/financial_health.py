from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FinancialHealthInput(BaseModel):
    text: str = Field(
        ...,
        description=(
            "Financial data text about a company — annual reports, press releases, "
            "news about financials, or any textual financial information. "
            "The tool extracts health signals and returns a scored assessment."
        ),
    )


class FinancialHealthTool(BaseTool):
    name: str = "Financial Health Tool"
    description: str = (
        "Analyzes financial text for health signals and returns a score from 0 (distressed) "
        "to 100 (very healthy), plus a risk signal and brief rationale. "
        "Use for financial due diligence when evaluating company stability."
    )
    args_schema: Type[BaseModel] = FinancialHealthInput

    _NEGATIVE: list[str] = [
        r"\bgoing[\s-]concern\b",
        r"\binsolvenc\w+\b",
        r"\bbankrupt\w*\b",
        r"\bdefault\w*\b",
        r"\bdebt\s+restructur\w+\b",
        r"\bnegative\s+cash\s+flow\b",
        r"\bwrite[\s-]?off\b",
        r"\bimpairment\b",
        r"\bloss\b",
        r"\boverleverage\w*\b",
        r"\brestatement\b",
        r"\bliquidat\w+\b",
        r"\bcredit\s+rating\s+downgrade\b",
        r"\bdebt\s+covenants?\s+breach\b",
    ]

    _POSITIVE: list[str] = [
        r"\bprofitable\b",
        r"\brecord\s+revenue\b",
        r"\brevenue\s+growth\b",
        r"\bcash\s+flow\s+positive\b",
        r"\bstrong\s+balance\s+sheet\b",
        r"\bdebt[\s-]free\b",
        r"\binvestment[\s-]grade\b",
        r"\bdividend\b",
        r"\bexpansion\b",
        r"\bprofitabilit\w+\b",
        r"\bpositive\s+ebitda\b",
        r"\bmarket\s+leader\b",
        r"\bcredit\s+rating\s+upgrade\b",
    ]

    def _run(self, text: str) -> str:
        text_lower = text.lower()

        neg_count = sum(1 for p in self._NEGATIVE if re.search(p, text_lower))
        pos_count = sum(1 for p in self._POSITIVE if re.search(p, text_lower))

        base = 50
        score = max(0, min(100, base + (pos_count * 8) - (neg_count * 10)))

        if score >= 70:
            signal = "healthy"
            risk = "low"
        elif score >= 45:
            signal = "moderate concerns present"
            risk = "medium"
        else:
            signal = "significant distress signals"
            risk = "high"

        return (
            f"Financial health score: {score}/100\n"
            f"Signal: {signal} | Financial risk: {risk}\n"
            f"Positive indicators found: {pos_count} | "
            f"Negative indicators found: {neg_count}"
        )
