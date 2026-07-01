from __future__ import annotations

import re

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RedFlagScorerInput(BaseModel):
    text: str = Field(
        ...,
        description=(
            "Text excerpt to score for corporate risk signals "
            "(e.g., operational descriptions, website content, news summaries). "
            "Returns a risk level and list of flagged signals."
        ),
    )


class RedFlagScorerTool(BaseTool):
    name: str = "Red Flag Scorer"
    description: str = (
        "Scores a text excerpt for corporate risk signals such as opacity, inconsistency, "
        "fraud language, or operational warning signs. "
        "Returns: risk level (low | medium | high) and flagged phrases found."
    )
    args_schema: type[BaseModel] = RedFlagScorerInput

    _HIGH_SIGNALS: list[str] = [
        r"\bfraud\b",
        r"\bscam\b",
        r"\bponzi\b",
        r"\bindicted\b",
        r"\barrested\b",
        r"\bsanction\w*\b",
        r"\bbankrupt\w*\b",
        r"\binsolvenc\w+\b",
        r"\bliquidat\w+\b",
        r"\bmoney\s+launder\w*\b",
        r"\bcorrupt\w+\b",
        r"\bshell\s+compan\w*\b",
        r"\bpyramid\s+scheme\b",
        r"\bgoing[\s-]concern\b",
    ]

    _MEDIUM_SIGNALS: list[str] = [
        r"\bcontrovers\w+\b",
        r"\blitigation\b",
        r"\blawsuit\b",
        r"\bpenalt\w+\b",
        r"\bfine\b",
        r"\bwhistle\w+\b",
        r"\bopaque\b",
        r"\bundisclosed\b",
        r"\boff[\s-]balance\b",
        r"\brelated[\s-]party\b",
        r"\binvestigat\w+\b",
        r"\bsanction\b",
        r"\bdefault\b",
        r"\bdebt\s+covenants?\b",
    ]

    def _run(self, text: str) -> str:
        text_lower = text.lower()

        high_hits = [p for p in self._HIGH_SIGNALS if re.search(p, text_lower)]
        med_hits = [p for p in self._MEDIUM_SIGNALS if re.search(p, text_lower)]

        if high_hits:
            level = "high"
        elif med_hits:
            level = "medium"
        else:
            level = "low"

        all_hits = high_hits + [m for m in med_hits if m not in high_hits]

        return (
            f"Risk level: {level}\n"
            f"Flagged signals ({len(all_hits)}): "
            f"{', '.join(all_hits) if all_hits else 'none detected'}\n"
            f"High severity hits: {len(high_hits)} | "
            f"Medium severity hits: {len(med_hits)}"
        )
