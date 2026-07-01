from __future__ import annotations

import re
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class EntityConsistencyInput(BaseModel):
    text: str = Field(
        ...,
        description=(
            "Text containing corporate entity data about a company — name, registration "
            "number, registered address, directors, UBOs, from one or more sources. "
            "The tool flags internal inconsistencies and suspicious patterns."
        ),
    )


class EntityConsistencyTool(BaseTool):
    name: str = "Entity Consistency Tool"
    description: str = (
        "Analyzes corporate entity data text for internal inconsistencies: name variations, "
        "address mismatches, director conflicts, suspicious registration patterns, or "
        "opacity signals. Returns CONSISTENT | INCONSISTENCIES_FOUND with details. "
        "Use during legal & compliance due diligence."
    )
    args_schema: Type[BaseModel] = EntityConsistencyInput

    _PATTERNS: list[tuple[str, str, str]] = [
        (r"\bdifferent\s+address\w*\b", "Address mismatch detected across sources", "MEDIUM"),
        (r"\bname\s+variation\w*\b", "Company name variation found", "MEDIUM"),
        (r"\bno\s+record\b", "No registration record found", "HIGH"),
        (r"\bregistration\s+expired\b", "Expired or lapsed registration", "HIGH"),
        (r"\bdirector\s+conflict\b", "Director information conflict", "MEDIUM"),
        (r"\bshell\s+compan\w*\b", "Shell company pattern detected", "HIGH"),
        (r"\bnominee\s+director\b", "Nominee director structure identified", "MEDIUM"),
        (
            r"\bultimate\s+beneficiar\w*\b.{0,50}\bunknown\b",
            "UBO identity is unknown or undisclosed",
            "HIGH",
        ),
        (r"\boffshore\b", "Offshore holding or registration present", "MEDIUM"),
        (
            r"\bmultiple\s+jurisdictions\b",
            "Entity registered across multiple jurisdictions",
            "MEDIUM",
        ),
        (r"\bfrequent\s+director\s+change\w*\b", "Frequent director changes flagged", "MEDIUM"),
        (r"\bregistered\s+agent\b", "Registered-agent-only presence (no operational address)", "LOW"),
        (r"\bpo\s+box\b", "PO Box as registered address (no physical office)", "LOW"),
        (r"\bdormant\b", "Company or subsidiary listed as dormant", "MEDIUM"),
    ]

    def _run(self, text: str) -> str:
        text_lower = text.lower()

        findings: list[tuple[str, str]] = []
        for pattern, label, severity in self._PATTERNS:
            if re.search(pattern, text_lower, re.DOTALL):
                findings.append((severity, label))

        if not findings:
            return (
                "Entity consistency check: CONSISTENT\n"
                "No major inconsistencies or opacity signals detected."
            )

        high = [f for s, f in findings if s == "HIGH"]
        medium = [f for s, f in findings if s == "MEDIUM"]
        low = [f for s, f in findings if s == "LOW"]

        result_lines = ["Entity consistency check: INCONSISTENCIES_FOUND"]
        if high:
            result_lines.append(f"\nHIGH severity ({len(high)}):")
            result_lines.extend(f"  ✗ {f}" for f in high)
        if medium:
            result_lines.append(f"\nMEDIUM severity ({len(medium)}):")
            result_lines.extend(f"  ! {f}" for f in medium)
        if low:
            result_lines.append(f"\nLOW severity ({len(low)}):")
            result_lines.extend(f"  ~ {f}" for f in low)

        return "\n".join(result_lines)
