/**
 * src/pages/qa-admin.ts
 * Justor AI — Legal QA Review Queue & Evaluation Workspace
 */

const escapeHtml = (val: string): string =>
  val.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

export async function renderQaAdminPage(container: HTMLElement) {
  container.innerHTML = `
    <main id="page-content" class="section-shell" style="padding-top: 40px; padding-bottom: 80px;">
      <header style="margin-bottom: 32px; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
        <div>
          <span class="section-kicker">Justor Pilot Quality Assurance</span>
          <h1 style="font-size: 32px; font-weight: 700; margin: 8px 0;">Legal QA Evaluation Queue</h1>
          <p style="color: #475467; max-width: 720px;">
            Review logged queries and flagged user feedback. Triage legal correctness, mark severity, and submit gold-standard corrected citations.
          </p>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <input id="qa-admin-token" type="password" placeholder="Admin Secret Token..." value="justor-pilot-admin-2026" style="padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-size: 13px;">
          <button id="qa-refresh-btn" class="button button-small" type="button">Refresh Queue</button>
        </div>
      </header>

      <div class="qa-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <!-- Left: Queue List -->
        <section style="background: #FFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 20px; max-height: 80vh; overflow-y: auto;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="font-size: 18px; font-weight: 700; margin: 0;">Evaluation Queue (<span id="qa-queue-count">—</span>)</h2>
            <small style="color: #64748B;">Showing recent pilot items</small>
          </div>
          <div id="qa-queue-list" style="display: flex; flex-direction: column; gap: 12px;">
            <p style="color: #94A3B8; text-align: center; padding: 24px;">Loading review queue from backend...</p>
          </div>
        </section>

        <!-- Right: Active Evaluation Form -->
        <section id="qa-evaluation-panel" style="background: #FFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px;">
          <div style="text-align: center; color: #94A3B8; padding: 60px 20px;">
            <p style="font-size: 16px; font-weight: 500;">Select a query from the queue to review and submit legal verdict.</p>
          </div>
        </section>
      </div>
    </main>
  `;

  let queueItems: any[] = [];
  let selectedIndex = -1;

  const loadQueue = async () => {
    try {
      const token = (document.getElementById('qa-admin-token') as HTMLInputElement)?.value || '';
      const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
      const res = await fetch(`${backendUrl}/api/qa/queue`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('failed-to-load');
      const data = await res.json();
      queueItems = data.queue || [];
      const countEl = document.getElementById('qa-queue-count');
      if (countEl) countEl.textContent = String(queueItems.length);

      const listEl = document.getElementById('qa-queue-list');
      if (!listEl) return;

      if (queueItems.length === 0) {
        listEl.innerHTML = `<p style="color: #027A48; text-align: center; padding: 24px;">✓ Queue is clear! All flagged answers have been evaluated.</p>`;
        return;
      }

      listEl.innerHTML = queueItems.map((item, idx) => {
        const ratingBadge = item.feedback_rating === -1
          ? '<span class="semantic-badge badge-conflict-verified" style="font-size: 11px;">👎 Flagged Issue</span>'
          : item.feedback_rating === 1
            ? '<span class="semantic-badge badge-primary-verified" style="font-size: 11px;">👍 Positive</span>'
            : '<span class="semantic-badge badge-pending-verified" style="font-size: 11px;">○ Unrated</span>';

        return `
          <div class="qa-item-card" data-idx="${idx}" style="padding: 14px; border: 1px solid #E2E8F0; border-radius: 8px; cursor: pointer; transition: all 120ms ease; background: ${idx === selectedIndex ? '#F0F5FF' : '#FFF'}; border-color: ${idx === selectedIndex ? '#0020A0' : '#E2E8F0'};">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              ${ratingBadge}
              <small style="color: #64748B;">${item.role || 'General'}</small>
            </div>
            <p style="margin: 0 0 6px; font-weight: 600; font-size: 14px; color: #0F172A; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${escapeHtml(item.query || 'No query text recorded')}</p>
            ${item.feedback_category ? `<small style="color: #B42318; font-weight: 600;">Category: ${escapeHtml(item.feedback_category)}</small>` : ''}
          </div>
        `;
      }).join('');

      // Add click events to queue cards
      listEl.querySelectorAll('.qa-item-card').forEach((card) => {
        card.addEventListener('click', () => {
          const idx = parseInt((card as HTMLElement).dataset.idx || '0', 10);
          selectedIndex = idx;
          renderEvaluationForm(queueItems[idx]);
          loadQueue();
        });
      });
    } catch (e) {
      const listEl = document.getElementById('qa-queue-list');
      if (listEl) listEl.innerHTML = `<p style="color: #B42318; text-align: center; padding: 24px;">Error connecting to QA Queue endpoint.</p>`;
    }
  };

  const renderEvaluationForm = (item: any) => {
    const panel = document.getElementById('qa-evaluation-panel');
    if (!panel) return;

    panel.innerHTML = `
      <form id="qa-review-form" style="display: flex; flex-direction: column; gap: 16px;">
        <span class="section-kicker">Reviewing Case #${escapeHtml(item.query_run_id || item.id || 'N/A')}</span>
        <h2 style="font-size: 18px; font-weight: 700; margin: 0;">Legal Correctness Assessment</h2>
        
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
          <strong style="font-size: 13px; color: #475467;">User Prompt:</strong>
          <p style="margin: 4px 0 0; font-size: 14px; color: #0F172A;">${escapeHtml(item.query || 'N/A')}</p>
        </div>

        ${item.feedback_comment ? `
          <div style="background: #FEF3F2; border: 1px solid #FECDCA; padding: 12px; border-radius: 8px;">
            <strong style="font-size: 12px; color: #B42318;">User Feedback:</strong>
            <p style="margin: 2px 0 0; font-size: 13px; color: #912018;">${escapeHtml(item.feedback_comment)}</p>
          </div>
        ` : ''}

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
          <div>
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">QA Verdict</label>
            <select name="verdict" required style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; background: #FFF;">
              <option value="Correct">✓ Correct (Legally Sound)</option>
              <option value="Partial">◐ Partial (Minor citation/clarification error)</option>
              <option value="Incorrect">✕ Incorrect (Wrong statute / Halucinated case)</option>
            </select>
          </div>
          <div>
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Severity Rating</label>
            <select name="severity" required style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; background: #FFF;">
              <option value="Minor">Minor (Formatting / minor wording)</option>
              <option value="Material">Material (Missing prerequisite / timeline)</option>
              <option value="Dangerous">Dangerous (Wrong legal advice / repealed law)</option>
            </select>
          </div>
        </div>

        <div>
          <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Corrected Controlling Authority</label>
          <input name="corrected_authority" placeholder="e.g. Order XXXIX Rules 1-2 CPC / NI Act s.138" style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1;">
        </div>

        <div>
          <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Reviewer Notes & Evaluation Rationale</label>
          <textarea name="reviewer_note" rows="3" placeholder="Explain the legal reasoning or evidence defect..." style="width: 100%; padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1;"></textarea>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px;">
          <button class="button" type="submit">Submit Evaluation Record ↗</button>
        </div>
      </form>
    `;

    const form = document.getElementById('qa-review-form') as HTMLFormElement;
    if (form) {
      form.addEventListener('submit', async (ev) => {
        ev.preventDefault();
        const fd = new FormData(form);
        const verdict = String(fd.get('verdict') || 'Correct');
        const severity = String(fd.get('severity') || 'Minor');
        const corrected_authority = String(fd.get('corrected_authority') || '');
        const reviewer_note = String(fd.get('reviewer_note') || '');
        const token = (document.getElementById('qa-admin-token') as HTMLInputElement)?.value || '';

        try {
          const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
          const res = await fetch(`${backendUrl}/api/qa/review`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              query_run_id: item.query_run_id || item.id || `run_${Date.now()}`,
              verdict,
              severity,
              corrected_authority,
              reviewer_note,
              reviewer_id: 'lawyer-qa-reviewer'
            })
          });
          if (!res.ok) throw new Error('review-submission-failed');
          panel.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
              <div style="font-size: 36px; color: #027A48; margin-bottom: 12px;">✓</div>
              <h3 style="font-size: 20px; font-weight: 700; color: #0F172A; margin: 0 0 8px;">Evaluation Submitted Successfully</h3>
              <p style="color: #475467;">Recorded verdict: <strong>${escapeHtml(verdict)}</strong> (${escapeHtml(severity)}). Case added to gold standard evaluation repository.</p>
            </div>
          `;
          await loadQueue();
        } catch (err) {
          alert('Failed to submit evaluation to backend. Please check network / admin secret.');
        }
      });
    }
  };

  document.getElementById('qa-refresh-btn')?.addEventListener('click', loadQueue);
  await loadQueue();
}
