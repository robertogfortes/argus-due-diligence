/* ARGUS Dashboard — renders a CompanyRiskProfile into the panel. */

const RISK_COLORS = { low: "#22c55e", medium: "#f59e0b", high: "#ef4444" };
const DIM_ICONS = {
  financial: "M4 20V10M9 20V4M14 20v-7M19 20V8",
  reputational: "M12 2l2.4 7.4H22l-6 4.4 2.3 7.2L12 16.6 5.7 21l2.3-7.2-6-4.4h7.6z",
  legal: "M12 3v18M5 7h14M7 7l-3 7h6zM17 7l-3 7h6z",
  operational: "M12 8a4 4 0 100 8 4 4 0 000-8zM12 2v3M12 19v3M2 12h3M19 12h3",
};

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])
  );
}
function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
function prettyEng(s) { return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()); }

/* Circular progress ring SVG. score 0..100 (higher = safer → greener). */
function ring(score, size, stroke) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score));
  const off = c * (1 - pct / 100);
  const color = pct >= 67 ? RISK_COLORS.low : pct >= 45 ? RISK_COLORS.medium : RISK_COLORS.high;
  return `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none"
        stroke="rgba(255,255,255,0.08)" stroke-width="${stroke}" />
      <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none"
        stroke="${color}" stroke-width="${stroke}" stroke-linecap="round"
        stroke-dasharray="${c}" stroke-dashoffset="${off}" />
    </svg>`;
}

/* Overall-risk gauge: fill by risk severity (low→ small green? no—use inverse). */
function riskGauge(risk) {
  // Represent risk as a 3-step arc; more fill = more risk.
  const map = { low: 33, medium: 66, high: 100 };
  const pct = map[risk] ?? 50;
  const size = 220, stroke = 18, r = (size - stroke) / 2, c = 2 * Math.PI * r;
  const off = c * (1 - pct / 100);
  const color = RISK_COLORS[risk] || "#6366f1";
  return `
    <div class="gauge">
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="${stroke}" />
        <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${color}" stroke-width="${stroke}"
          stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${off}"
          style="filter: drop-shadow(0 0 10px ${color}66)" />
      </svg>
      <div class="center">
        <div class="risk-word" style="color:${color}">${risk.toUpperCase()}</div>
        <div class="risk-label">Overall Risk</div>
      </div>
    </div>`;
}

function recPill(rec) {
  const label = rec.replace(/_/g, " ").toUpperCase();
  let color = RISK_COLORS.medium, bg = "rgba(245,158,11,0.14)", bd = "rgba(245,158,11,0.4)";
  if (rec === "proceed") { color = RISK_COLORS.low; bg = "rgba(34,197,94,0.14)"; bd = "rgba(34,197,94,0.4)"; }
  if (rec === "decline") { color = RISK_COLORS.high; bg = "rgba(239,68,68,0.14)"; bd = "rgba(239,68,68,0.4)"; }
  return `<span class="rec-pill" style="color:${color};background:${bg};border:1px solid ${bd}">${label}</span>`;
}

function dimCard(key, d) {
  const icon = DIM_ICONS[key] || DIM_ICONS.operational;
  const findings = (d.top_findings || []).map((f) => `<li>${esc(f)}</li>`).join("");
  return `
    <div class="card dim">
      <div class="dim-top">
        <div class="dim-name">
          <svg class="dim-icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="${icon}"/></svg>
          ${cap(key)}
        </div>
        <span class="risk-badge r-${d.risk_level}">${d.risk_level}</span>
      </div>
      <div style="display:flex;align-items:center;gap:14px">
        <div class="meter">
          ${ring(d.score, 88, 9)}
          <div class="val">${d.score}</div>
        </div>
        <div class="dim-summary">${esc(d.summary)}</div>
      </div>
      <ul class="dim-findings">${findings}</ul>
    </div>`;
}

function flagCard(f) {
  return `
    <div class="flag sev-${f.severity}">
      <div class="rail"></div>
      <div class="body">
        <div class="flag-head">
          <span class="cat">${esc(f.category)}</span>
          <span class="risk-badge r-${f.severity}">${f.severity}</span>
        </div>
        <div class="desc">${esc(f.description)}</div>
      </div>
      <div class="side">
        <span class="conf">confidence <b>${esc(f.confidence)}</b></span>
        <a class="src" href="${esc(f.evidence_url)}" target="_blank" rel="noopener">source ↗</a>
      </div>
    </div>`;
}

function render(p) {
  const flagsSorted = [...(p.red_flags || [])].sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 };
    return order[a.severity] - order[b.severity];
  });

  const html = `
    <section class="summary-bar">
      <div class="company">
        <h2>${esc(p.company_name)}</h2>
        <span class="meta">${esc(p.jurisdiction)} · Investigated ${esc(p.investigation_date)}</span>
      </div>
      <span class="chip">${esc(prettyEng(p.engagement_type))}</span>
      ${p.verified ? '<span class="badge">Verified</span>' : ""}
      ${p.human_reviewed ? '<span class="badge">Human Reviewed</span>' : ""}
    </section>

    <div class="top-grid">
      <div class="card gauge-card">
        <h3>Aggregate Assessment</h3>
        ${riskGauge(p.overall_risk)}
        <div style="margin-top:10px;color:var(--muted);font-size:13px">
          Financial health score <b style="color:var(--text)">${p.financial_score}/100</b>
        </div>
      </div>
      <div class="card rec">
        <div class="rec-head">
          <h3 style="margin:0">Recommendation</h3>
          ${recPill(p.recommendation)}
        </div>
        <div class="rationale">${esc(p.risk_rationale)}</div>
        ${p.conditions ? `<div class="conditions"><b>Conditions:</b> ${esc(p.conditions)}</div>` : ""}
      </div>
    </div>

    <div class="section-title">Risk Dimensions</div>
    <div class="dims">
      ${dimCard("financial", p.financial)}
      ${dimCard("reputational", p.reputational)}
      ${dimCard("legal", p.legal)}
      ${dimCard("operational", p.operational)}
    </div>

    <div class="section-title">Red Flags · ${flagsSorted.length}</div>
    <div class="flags">
      ${flagsSorted.map(flagCard).join("")}
    </div>
  `;

  document.getElementById("app").innerHTML = html;
}

function boot() {
  const app = document.getElementById("app");
  if (window.ARGUS_DATA) {
    try { render(window.ARGUS_DATA); return; }
    catch (e) { console.error(e); }
  }
  // Fallback: try fetching the JSON (works when served over http)
  fetch("data/risk_profile.json")
    .then((r) => r.json())
    .then(render)
    .catch(() => {
      app.innerHTML =
        '<div class="loading">No investigation data found. Run <code>python -m argus.demo</code> to generate a preview.</div>';
    });
}

document.addEventListener("DOMContentLoaded", boot);
