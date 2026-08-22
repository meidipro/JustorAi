/**
 * src/pages/amendment-admin.ts
 * Justor TLRE — Internal Amendment Coverage & Verification Admin Monitor
 */

const escapeHtml = (val: string): string =>
  val.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

export async function renderAmendmentAdminPage(container: HTMLElement) {
  container.innerHTML = `
    <main id="page-content" class="section-shell" style="padding-top: 40px; padding-bottom: 80px;">
      <header style="margin-bottom: 32px;">
        <span class="section-kicker">Justor Temporal Legal Reasoning Engine</span>
        <h1 style="font-size: 32px; font-weight: 700; margin: 8px 0;">TLRE Statutory Coverage Monitor</h1>
        <p style="color: #475467; max-width: 720px;">
          Live view of Bangladesh statutes indexed, temporal provisions versioned, and human-verified amendment records under the two-person verification protocol.
        </p>
      </header>

      <div class="tlre-metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 32px;">
        <div style="background: #FFF; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
          <small style="color: #64748B; font-weight: 600; text-transform: uppercase;">Indexed Acts</small>
          <div id="stat-total-acts" style="font-size: 28px; font-weight: 700; color: #0F172A; margin-top: 4px;">—</div>
        </div>
        <div style="background: #FFF; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
          <small style="color: #64748B; font-weight: 600; text-transform: uppercase;">Active Provisions</small>
          <div id="stat-total-provs" style="font-size: 28px; font-weight: 700; color: #0020A0; margin-top: 4px;">—</div>
        </div>
        <div style="background: #FFF; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
          <small style="color: #64748B; font-weight: 600; text-transform: uppercase;">Verified Versions</small>
          <div id="stat-verified-vers" style="font-size: 28px; font-weight: 700; color: #027A48; margin-top: 4px;">—</div>
        </div>
        <div style="background: #FFF; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
          <small style="color: #64748B; font-weight: 600; text-transform: uppercase;">TLRE Verification State</small>
          <div style="font-size: 18px; font-weight: 700; color: #027A48; margin-top: 8px;">● Two-Reviewer Active</div>
        </div>
      </div>

      <section style="background: #FFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px; margin-bottom: 32px;">
        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 16px;">Statutory Coverage by Act</h2>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
            <thead>
              <tr style="border-bottom: 2px solid #E2E8F0; color: #64748B;">
                <th style="padding: 12px 16px;">Act Name</th>
                <th style="padding: 12px 16px;">Year</th>
                <th style="padding: 12px 16px;">Provisions</th>
                <th style="padding: 12px 16px;">Verified</th>
                <th style="padding: 12px 16px;">Coverage Status</th>
              </tr>
            </thead>
            <tbody id="tlre-coverage-tbody">
              <tr><td colspan="5" style="padding: 24px; text-align: center; color: #94A3B8;">Loading TLRE coverage metrics...</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section style="background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px;">
        <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 12px;">CLI Verification Guide</h2>
        <p style="font-size: 14px; color: #475467; margin-bottom: 16px;">
          To draft or verify statutory amendments under the human-in-the-loop protocol, run the CLI tool from your terminal:
        </p>
        <pre style="background: #0F172A; color: #F8FAFC; padding: 16px; border-radius: 8px; font-size: 13px; overflow-x: auto;">
# List all indexed acts
python tools/update_amendment.py list-acts

# View pending draft amendments awaiting human verification
python tools/update_amendment.py list-pending

# Verify and apply an amendment
python tools/update_amendment.py verify &lt;amendment_id&gt;

# Check coverage
python tools/update_amendment.py coverage
        </pre>
      </section>
    </main>
  `;

  // Fetch coverage metrics
  try {
    const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
    const res = await fetch(`${backendUrl}/amendment-coverage`);
    if (!res.ok) throw new Error('coverage-fetch-failed');
    const payload = await res.json();
    const acts = payload.acts || [];

    const totalProvs = acts.reduce((acc: number, a: any) => acc + (a.total_provisions || 0), 0);
    const verifiedVers = acts.reduce((acc: number, a: any) => acc + (a.verified_versions || 0), 0);

    const elTotalActs = document.getElementById('stat-total-acts');
    if (elTotalActs) elTotalActs.textContent = String(acts.length);
    const elTotalProvs = document.getElementById('stat-total-provs');
    if (elTotalProvs) elTotalProvs.textContent = String(totalProvs);
    const elVerifiedVers = document.getElementById('stat-verified-vers');
    if (elVerifiedVers) elVerifiedVers.textContent = String(verifiedVers);

    const tbody = document.getElementById('tlre-coverage-tbody');
    if (tbody) {
      tbody.innerHTML = acts.map((act: any) => {
        const badge = act.coverage_status === 'complete'
          ? '<span class="semantic-badge badge-primary-verified">● COMPLETE</span>'
          : act.coverage_status === 'partial'
            ? '<span class="semantic-badge badge-reporter-verified">◐ PARTIAL</span>'
            : '<span class="semantic-badge badge-pending-verified">○ PENDING</span>';

        return `
          <tr style="border-bottom: 1px solid #F1F5F9;">
            <td style="padding: 14px 16px; font-weight: 600; color: #1E293B;">${escapeHtml(act.act_name)}</td>
            <td style="padding: 14px 16px; color: #64748B;">${act.year || '—'}</td>
            <td style="padding: 14px 16px; color: #0F172A; font-weight: 600;">${act.total_provisions}</td>
            <td style="padding: 14px 16px; color: #027A48; font-weight: 600;">${act.verified_versions}</td>
            <td style="padding: 14px 16px;">${badge}</td>
          </tr>
        `;
      }).join('');
    }
  } catch (err) {
    const tbody = document.getElementById('tlre-coverage-tbody');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="5" style="padding: 24px; text-align: center; color: #B42318;">Unable to connect to TLRE backend metrics endpoint.</td></tr>`;
    }
  }
}
