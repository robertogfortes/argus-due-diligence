# Playbook: New Supplier Due Diligence

**Engagement Type:** `new_supplier`
**Risk Exposure:** Medium (financial, operational, reputational contagion)
**Typical Investigation Depth:** Standard to Deep depending on contract value

---

## When to Use This Playbook

Use for any new third-party supplier, vendor, or service provider before signing a
commercial agreement. Applies to both goods suppliers and service providers.

---

## Investigation Dimensions & Depth

### 1. Financial (Standard → Deep if contract > USD 500K/year)
- Verify business registration and legal status
- Assess financial stability (ability to deliver long-term)
- Check for insolvency proceedings, tax liens, or unpaid judgments
- Identify ultimate beneficial owners (UBOs)
- For high-value contracts: request financials or use proxy signals (headcount, office size)

**Key questions:**
- Is this supplier financially stable enough to honor multi-year contracts?
- Are the beneficial owners known and not sanctioned?
- Is there evidence of financial distress that could disrupt supply?

### 2. Legal & Compliance (Standard)
- Verify CNPJ / corporate registration is active and consistent
- Check for active litigation involving contract breaches or fraud
- Screen against sanctions lists (OFAC, EU, COAF/TCU for Brazil)
- Verify required certifications (ISO, quality standards relevant to category)
- Check labor compliance history (key for manufacturing suppliers)

**Key questions:**
- Is the company legally registered and in good standing?
- Are there sanctions or compliance violations that prohibit engagement?
- Does the company have required quality certifications?

### 3. Reputational (Standard)
- Search for adverse media: fraud, bribery, labor violations, product recalls
- Check executive backgrounds for red flags
- Look for supplier-related controversies in social and trade press

**Key questions:**
- Has this supplier been linked to corruption, fraud, or unsafe practices?
- Are there employee or customer complaints patterns?

### 4. Operational (Deep)
- Verify physical presence (address, facilities photos if available)
- Validate claimed capacity (employee count, production certifications)
- Check digital footprint consistency (website age, social media, job postings)
- For manufacturing: verify supply chain and raw material sourcing claims

**Key questions:**
- Does this supplier have the real capacity to fulfill our orders?
- Do the claimed operations match observable evidence?

---

## Risk Thresholds for New Suppliers

| Finding | Action |
|---|---|
| Active sanctions | DECLINE — mandatory |
| Financial score < 35 | DECLINE or require financial guarantee |
| Financial score 35–55 | PROCEED WITH CONDITIONS + payment terms protection |
| No verifiable physical presence | DECLINE or require site visit |
| Labor compliance violations | PROCEED WITH CONDITIONS + audit clause |
| Minor reputational concerns | NOTE in contract, proceed |

---

## Standard Sources to Check

1. **Receita Federal** (CNPJ status) — `https://www.receita.fazenda.gov.br`
2. **JUCESP / Junta Comercial** (state filing)
3. **Portal da Transparência / CGU** (public contracts, sanctions)
4. **COAF / BACEN** (AML flags)
5. **Google News** — `site:g1.globo.com OR site:valor.globo.com "[company name]"`
6. **LinkedIn** — employee count and organizational verification
7. **Company website** — age, content consistency, certifications listed

---

## Required Outputs

- `CompanyRiskProfile.json` with all fields populated
- `due_diligence_dossier.md` covering all 4 dimensions
- `risk_briefing.md` for procurement / finance sign-off
- Recommendation must specify contract conditions if `proceed_with_conditions`
