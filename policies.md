# ARGUS — Internal Risk Policies

> This document is used by the Evidence Verification Specialist (QA agent)
> via MDXSearchTool for semantic cross-reference during the verification stage.

---

## Risk Appetite Framework

### Low Risk Appetite
- Any HIGH severity red flag → automatic DECLINE recommendation.
- More than 2 MEDIUM severity red flags → DECLINE or escalate.
- Financial score below 40 → DECLINE.
- Active litigation involving fraud or regulatory sanctions → DECLINE.

### Medium Risk Appetite (default)
- Single HIGH severity flag with no active litigation → PROCEED WITH CONDITIONS.
- Financial score 40–60 → PROCEED WITH CONDITIONS with financial monitoring clause.
- Multiple MEDIUM flags without HIGH → PROCEED WITH CONDITIONS.
- Reputational concerns without substantiation → note in dossier, proceed.

### High Risk Appetite
- Decline only on confirmed fraud, active sanctions, or financial score below 25.
- Multiple HIGH flags require board-level sign-off, not automatic decline.

---

## Red Flag Classification Guide

### Financial Red Flags
| Signal | Severity |
|---|---|
| Going-concern audit opinion | HIGH |
| Active insolvency proceedings | HIGH |
| Restatement of financial statements | HIGH |
| Beneficial owner unknown or offshore shell | HIGH |
| Negative cash flow for 3+ consecutive periods | MEDIUM |
| Debt-to-equity ratio above 3x (sector-adjusted) | MEDIUM |
| Related-party transactions above 20% of revenue | MEDIUM |
| Revenue inconsistency across sources | MEDIUM |
| Missing public financial data (private company) | LOW |

### Legal & Compliance Red Flags
| Signal | Severity |
|---|---|
| Active sanctions (OFAC, EU, UN) | HIGH |
| Criminal conviction of directors or UBOs | HIGH |
| Active regulatory action (SEC, CVM, BACEN) | HIGH |
| AML / money laundering investigation | HIGH |
| Multiple active commercial lawsuits | MEDIUM |
| Corporate registration inconsistencies | MEDIUM |
| Expired or lapsed certifications | MEDIUM |
| Nominee directors with no operational role | MEDIUM |
| Minor regulatory violations (resolved) | LOW |

### Reputational Red Flags
| Signal | Severity |
|---|---|
| Major fraud or corruption scandal (verified) | HIGH |
| Executive criminal indictment | HIGH |
| Mass product recall with safety implications | HIGH |
| Sustained negative media coverage (6+ months) | MEDIUM |
| Consumer protection complaints (pattern) | MEDIUM |
| Employee misconduct pattern (Glassdoor, court docs) | MEDIUM |
| Single unverified negative article | LOW |
| ESG violations without regulatory action | LOW |

### Operational Red Flags
| Signal | Severity |
|---|---|
| No verifiable physical presence for claimed operations | HIGH |
| Significant discrepancy between claimed and observed employee count | MEDIUM |
| Website recently created (< 1 year) for established company | MEDIUM |
| No traceable supply chain for manufacturing claims | MEDIUM |
| Job postings inconsistent with claimed business activity | LOW |
| Limited digital footprint for size claimed | LOW |

---

## Source Quality Hierarchy

1. **Tier 1 — Official registries:** Corporate registries, court databases, regulatory filings,
   official sanctions lists (OFAC, EU). Confidence: HIGH.
2. **Tier 2 — Major media:** Reuters, Bloomberg, Financial Times, Valor Econômico,
   national newspaper of record. Confidence: MEDIUM-HIGH.
3. **Tier 3 — Trade press & analysts:** Industry publications, analyst reports,
   professional associations. Confidence: MEDIUM.
4. **Tier 4 — Social & crowdsourced:** Glassdoor, Reddit, forums, unverified blogs.
   Confidence: LOW (corroborating only, never primary).

---

## Mandatory QA Checklist

Before any finding enters the dossier, verify:
- [ ] Source URL is provided and accessible
- [ ] Publication/filing date is noted
- [ ] Source tier is identified (Tier 1–4 above)
- [ ] Confidence level is assigned
- [ ] Severity is assigned per the Red Flag Classification Guide
- [ ] Finding does not contain PII of private individuals
- [ ] Finding is within corporate scope (no political individuals)
- [ ] HIGH severity finding is flagged for human review

---

## Jurisdictional Notes

### Brazil
- Corporate registry: Receita Federal (CNPJ), JUCESP / Juntas Comerciais estaduais.
- Sanctions: COAF watch lists, TCU, CGU (Portal da Transparência).
- Litigation: TJSP / TRF system, CNJ (Conselho Nacional de Justiça).
- Financial regulators: CVM (securities), BACEN (banking), SUSEP (insurance).

### United States
- Corporate registry: State SOS filings, SEC EDGAR.
- Sanctions: OFAC SDN list.
- Litigation: PACER federal courts.

### European Union
- Corporate registry: BRIS (Business Registers Interconnection System) per country.
- Sanctions: EU Consolidated Sanctions List.
- AML: Financial Intelligence Units per country.
