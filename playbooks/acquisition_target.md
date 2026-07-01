# Playbook: Acquisition Target Due Diligence

**Engagement Type:** `acquisition_target`
**Risk Exposure:** Critical (full financial, legal, and operational integration risk)
**Typical Investigation Depth:** Maximum — all dimensions, deepest available data

---

## When to Use This Playbook

Use when evaluating a company as a potential M&A target: full acquisition, majority stake,
minority investment, or earnout structure. This is the highest-stakes investigation type.

> ⚠️ Note: For full M&A due diligence, this AI-powered OSINT investigation is a
> **preliminary screening** phase. It does not replace legal, financial, and technical
> due diligence performed by licensed professionals with access to private company data.

---

## Investigation Dimensions & Depth

### 1. Financial (Maximum)
M&A financial due diligence aims to validate valuation and uncover hidden liabilities.
At the OSINT stage, focus on all publicly available proxies for financial health.

- All available financial disclosures (filings, news, credit databases)
- Revenue and growth trajectory signals from public sources
- Debt structure and off-balance-sheet obligations (operating leases, contingent liabilities)
- Beneficial ownership and controlling shareholder structure
- Any shareholder disputes or board-level conflicts
- Recent fundraising history and valuation signals (for private targets)
- Tax compliance signals (public auction records, tax liens)
- Any history of financial statement restatements

**Key questions:**
- What is the realistic financial picture before private data access?
- Are there hidden liabilities that public signals suggest?
- Is the ownership structure clean and transferable?

### 2. Legal & Compliance (Maximum)
Post-acquisition, all legal liabilities transfer to the acquirer.

- Complete litigation mapping (all jurisdictions the target operates in)
- Regulatory and enforcement history (full 10-year lookback)
- IP portfolio health: patents, trademarks, copyrights — and any disputes
- Employment law exposure: class actions, labor disputes, WARN Act notices
- Environmental compliance (if relevant to sector)
- Data protection compliance: any GDPR/LGPD violations, data breaches
- Key contracts: change-of-control clauses that could terminate on acquisition
- Director and officer history: any past corporate failures or investigations

**Key questions:**
- What legal liabilities would we inherit on day one of closing?
- Are there regulatory approvals (antitrust, CADE, ANATEL) needed for the deal?
- Do key contracts survive a change of control?

### 3. Reputational (Deep)
- Full media analysis: 7-year lookback on all significant coverage
- Brand equity assessment: consumer perception, NPS proxies
- ESG and corporate governance reputation
- Founder and CEO personal brand (acquirer often inherits the founder narrative)
- Glassdoor, Indeed, and employee sentiment (culture due diligence proxy)
- Customer retention signals and public churn indicators

**Key questions:**
- Are there reputational liabilities that would damage our brand post-acquisition?
- Is there a culture or values mismatch that signals integration risk?

### 4. Operational (Maximum)
In acquisitions, operational reality often diverges from the pitch deck.

- Technology infrastructure signals (job postings, tech stack from public sources)
- Actual headcount vs. claimed (LinkedIn, job boards)
- Customer concentration risk (top 3 customers representing > 50% revenue is a flag)
- Geographic footprint verification
- Key person risk: who actually runs the business day-to-day?
- Supply chain depth and single-source dependencies
- Product/service roadmap consistency with public claims

**Key questions:**
- Does the operational reality match the valuation narrative?
- What is the key-person risk profile?
- Are there operational dependencies that create integration complexity?

---

## Risk Thresholds for Acquisition Targets

| Finding | Action |
|---|---|
| Active sanctions on target or UBOs | DECLINE — mandatory, deal-killer |
| Undisclosed controlling beneficial owner | HALT — require full UBO disclosure before proceeding |
| Ongoing fraud investigation | HALT — require resolution or restructure as asset deal |
| Financial score < 30 (public signals) | Flag for valuation discount; require private financial audit |
| Active material litigation (> 10% of estimated deal value) | Require representation & warranty insurance |
| Data breach not publicly disclosed | Escalate to legal — potential disclosure liability |
| Key customer concentration > 60% | Flag for earnout structure tied to retention |
| IP ownership unclear or disputed | Require IP audit before LOI |

---

## Required Outputs

- `CompanyRiskProfile.json` with all dimensions rated
- `due_diligence_dossier.md` — investment committee-ready
- `risk_briefing.md` — for board and deal team
- Red flags section must include estimated deal impact for each HIGH/MEDIUM finding
- Recommended deal structure adjustments based on findings
