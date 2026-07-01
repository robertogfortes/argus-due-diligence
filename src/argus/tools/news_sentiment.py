from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class NewsSentimentInput(BaseModel):
    text: str = Field(
        ...,
        description=(
            "Concatenated news headlines or article excerpts about a company. "
            "Provide as much text as available for more accurate results. "
            "Returns sentiment distribution and an overall sentiment score."
        ),
    )


class NewsSentimentTool(BaseTool):
    name: str = "News Sentiment Tool"
    description: str = (
        "Analyzes news text for corporate sentiment. Returns positive/neutral/negative "
        "signal distribution and an overall score from -100 (very negative) "
        "to +100 (very positive). Use for reputational due diligence."
    )
    args_schema: Type[BaseModel] = NewsSentimentInput

    _NEGATIVE: list[str] = [
        r"\bscandal\b",
        r"\blayoff\w*\b",
        r"\bfired\b",
        r"\baccused\b",
        r"\bfraud\b",
        r"\bbreach\b",
        r"\bcritici\w+\b",
        r"\bcollaps\w+\b",
        r"\brecall\b",
        r"\bcrisis\b",
        r"\bdeclin\w+\b",
        r"\bcontrovers\w+\b",
        r"\blawsuit\b",
        r"\bregulatory\s+action\b",
        r"\bfine\b",
        r"\bmisconduct\b",
    ]

    _POSITIVE: list[str] = [
        r"\baward\b",
        r"\bgrowth\b",
        r"\bpartnership\b",
        r"\blaunch\b",
        r"\bexpand\w*\b",
        r"\brecord\s+\w+\b",
        r"\bprofitable\b",
        r"\binnovat\w+\b",
        r"\bapproval\b",
        r"\bmilestone\b",
        r"\bsuccessful\b",
        r"\bleader\w*\b",
        r"\bacquisition\b",
        r"\bcertif\w+\b",
    ]

    def _run(self, text: str) -> str:
        text_lower = text.lower()

        neg = sum(1 for p in self._NEGATIVE if re.search(p, text_lower))
        pos = sum(1 for p in self._POSITIVE if re.search(p, text_lower))
        total = pos + neg or 1

        raw_score = int(((pos - neg) / total) * 100)
        score = max(-100, min(100, raw_score))

        pos_pct = int((pos / total) * 100)
        neg_pct = 100 - pos_pct

        if score > 25:
            label = "positive"
        elif score < -25:
            label = "negative"
        else:
            label = "mixed/neutral"

        if label == "negative":
            risk = "high"
        elif label == "mixed/neutral":
            risk = "medium"
        else:
            risk = "low"

        return (
            f"Sentiment score: {score:+d}/100 ({label})\n"
            f"Reputational risk signal: {risk}\n"
            f"Positive signals: {pos_pct}% | Negative signals: {neg_pct}%\n"
            f"Positive hits: {pos} | Negative hits: {neg}"
        )
