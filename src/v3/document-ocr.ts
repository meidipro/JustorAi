/**
 * Justor AI — Legal Document Vision OCR Modal
 * Enables lawyers and students to scan deeds, khatians, FIRs, and court orders
 * powered by Google Cloud Vertex AI OCR.
 */

import { analytics } from './analytics';

export function openDocumentOcrModal(
  language: 'en' | 'bn' = 'en',
  onSendToChat?: (prompt: string) => void
): void {
  // Remove any existing modal
  const existing = document.querySelector('.ocr-modal-backdrop');
  if (existing) existing.remove();

  const isBn = language === 'bn';
  const backdrop = document.createElement('div');
  backdrop.className = 'ocr-modal-backdrop';
  backdrop.innerHTML = `
    <div class="ocr-modal-drawer" role="dialog" aria-modal="true" aria-labelledby="ocr-modal-title">
      <div class="ocr-modal-header">
        <div>
          <span class="ocr-badge-kicker">Google Cloud Vision OCR · Vertex AI</span>
          <h2 id="ocr-modal-title">${isBn ? 'আইনি দলিল ও নথিপত্র বিশ্লেষণ' : 'Legal Document & Deed Analyzer'}</h2>
        </div>
        <button class="modal-close-btn" type="button" data-action="close-ocr-modal" aria-label="Close modal">✕</button>
      </div>
      
      <div class="ocr-modal-body">
        <div class="ocr-upload-zone" id="ocr-dropzone">
          <input type="file" id="ocr-file-input" accept=".pdf,.jpg,.jpeg,.png,.webp" style="display:none;" />
          <div class="ocr-drop-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
          </div>
          <div class="ocr-drop-text">
            <strong>${isBn ? 'দলিল, খতিয়ান বা এজাহারের ছবি/পিডিএফ আপলোড করুন' : 'Click or drag scanned deed, khatian, FIR or court order'}</strong>
            <span>${isBn ? 'সমর্থিত ফরম্যাট: PDF, JPG, PNG, WEBP (সর্বোচ্চ ১৫ মেগাবাইট)' : 'Supported formats: PDF, JPG, PNG, WEBP (Max 15MB)'}</span>
          </div>
          <button type="button" class="button button-outline ocr-browse-btn" id="ocr-browse-btn">
            ${isBn ? 'ফাইল নির্বাচন করুন' : 'Browse File'}
          </button>
        </div>

        <div id="ocr-file-preview-card" class="ocr-file-preview-card" style="display:none;">
          <div class="ocr-preview-info">
            <span class="ocr-file-icon">📄</span>
            <div>
              <strong id="ocr-preview-name">document.jpg</strong>
              <small id="ocr-preview-size">1.2 MB</small>
            </div>
          </div>
          <button type="button" class="button button-primary ocr-run-btn" id="ocr-run-btn">
            ${isBn ? 'বিশ্লেষণ ও স্ক্যান শুরু করুন' : 'Analyze with Vision OCR'}
          </button>
        </div>

        <div id="ocr-loading-state" class="ocr-loading-state" style="display:none;">
          <div class="ocr-scanning-radar">
            <div class="radar-sweep"></div>
          </div>
          <p><strong>${isBn ? 'Google Cloud Vision OCR দিয়ে আইনি তথ্য স্ক্যান করা হচ্ছে...' : 'Scanning document with Google Cloud Vertex AI Vision...'}</strong></p>
          <small>${isBn ? 'বাংলা ও ইংরেজি হাতের লেখা, দলিলদাতা/গ্রহীতা এবং আইনগত ধারা চিহ্নিত করা হচ্ছে' : 'Extracting parties, property schedule, and statutory provisions...'}</small>
        </div>

        <div id="ocr-results-container" class="ocr-results-container" style="display:none;"></div>
      </div>
    </div>
  `;

  document.body.appendChild(backdrop);

  // Close handlers
  const closeModal = () => backdrop.remove();
  backdrop.querySelector('[data-action="close-ocr-modal"]')?.addEventListener('click', closeModal);
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) closeModal();
  });

  const dropzone = backdrop.querySelector('#ocr-dropzone') as HTMLElement;
  const fileInput = backdrop.querySelector('#ocr-file-input') as HTMLInputElement;
  const browseBtn = backdrop.querySelector('#ocr-browse-btn') as HTMLButtonElement;
  const previewCard = backdrop.querySelector('#ocr-file-preview-card') as HTMLElement;
  const previewName = backdrop.querySelector('#ocr-preview-name') as HTMLElement;
  const previewSize = backdrop.querySelector('#ocr-preview-size') as HTMLElement;
  const runBtn = backdrop.querySelector('#ocr-run-btn') as HTMLButtonElement;
  const loadingState = backdrop.querySelector('#ocr-loading-state') as HTMLElement;
  const resultsContainer = backdrop.querySelector('#ocr-results-container') as HTMLElement;

  let selectedFile: File | null = null;

  const handleSelectedFile = (file: File) => {
    selectedFile = file;
    previewName.textContent = file.name;
    previewSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    dropzone.style.display = 'none';
    previewCard.style.display = 'flex';
    resultsContainer.style.display = 'none';
  };

  browseBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      handleSelectedFile(fileInput.files[0]);
    }
  });

  // Drag & drop
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('is-dragover');
  });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('is-dragover'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('is-dragover');
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  // Run OCR
  runBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    previewCard.style.display = 'none';
    loadingState.style.display = 'flex';

    try {
      const backendUrl = (
        (import.meta as any).env?.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com'
      ).replace(/\/$/, '');

      const formData = new FormData();
      formData.append('file', selectedFile);

      const resp = await fetch(`${backendUrl}/api/document/ocr-analyze`, {
        method: 'POST',
        body: formData,
      });

      loadingState.style.display = 'none';

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: 'Failed to analyze document.' }));
        resultsContainer.innerHTML = `
          <div class="ocr-error-box">
            <strong>${isBn ? 'বিশ্লেষণ ব্যর্থ হয়েছে' : 'Analysis Failed'}</strong>
            <p>${err.detail || err.message || 'Please check the file format or try another image.'}</p>
            <button type="button" class="button button-outline" id="ocr-retry-btn">${isBn ? 'আবার চেষ্টা করুন' : 'Try Again'}</button>
          </div>
        `;
        resultsContainer.style.display = 'block';
        resultsContainer.querySelector('#ocr-retry-btn')?.addEventListener('click', () => {
          resultsContainer.style.display = 'none';
          dropzone.style.display = 'flex';
        });
        return;
      }

      const resData = await resp.json();
      const a = resData.analysis || {};

      analytics.trackDocumentOCR(a.document_type || 'Unknown', selectedFile.name);

      // Render Results
      resultsContainer.innerHTML = `
        <div class="ocr-results-wrapper">
          <div class="ocr-result-topbar">
            <div>
              <span class="ocr-doc-type-badge">${escapeHtml(a.document_type || 'Legal Record')}</span>
              <span class="ocr-lang-badge">${escapeHtml(a.language || 'Bilingual')}</span>
            </div>
            <button type="button" class="button button-outline ocr-reset-btn" id="ocr-new-file-btn">
              ${isBn ? 'অন্য ফাইল আপলোড' : 'Scan Another File'}
            </button>
          </div>

          <!-- Key Identifiers Grid -->
          <div class="ocr-identifiers-grid">
            <div class="ocr-id-card">
              <label>${isBn ? 'প্রথম পক্ষ / বিক্রেতা / বাদী' : '1st Party / Vendor / Petitioner'}</label>
              <strong>${(a.parties?.first_party || []).join(', ') || 'Not explicitly stated'}</strong>
            </div>
            <div class="ocr-id-card">
              <label>${isBn ? 'দ্বিতীয় পক্ষ / ক্রেতা / বিবাদী' : '2nd Party / Vendee / Respondent'}</label>
              <strong>${(a.parties?.second_party || []).join(', ') || 'Not explicitly stated'}</strong>
            </div>
            <div class="ocr-id-card">
              <label>${isBn ? 'দলিল / মামলা নং' : 'Deed / Case No'}</label>
              <strong>${a.identifiers?.deed_or_case_number || 'N/A'}</strong>
            </div>
            <div class="ocr-id-card">
              <label>${isBn ? 'মৌজা ও খতিয়ান' : 'Mouza & Khatian'}</label>
              <strong>${a.identifiers?.mouza || ''} ${a.identifiers?.khatian_no ? `(খতিয়ান: ${a.identifiers.khatian_no})` : ''}</strong>
            </div>
            <div class="ocr-id-card">
              <label>${isBn ? 'দাগ / প্লট ও জমির পরিমাণ' : 'Dag/Plot & Quantum'}</label>
              <strong>${a.identifiers?.dag_plot_no || ''} ${a.identifiers?.land_area ? `— ${a.identifiers.land_area}` : ''}</strong>
            </div>
            <div class="ocr-id-card">
              <label>${isBn ? 'থানা ও জেলা' : 'Thana & District'}</label>
              <strong>${a.identifiers?.thana || ''}, ${a.identifiers?.district || ''}</strong>
            </div>
          </div>

          <!-- Detected Legal Provisions with Action Chips -->
          ${
            (a.statutory_provisions || []).length > 0
              ? `
            <div class="ocr-provisions-box">
              <h4>${isBn ? 'নথিতে উল্লেখিত বা সংশ্লিষ্ট আইনি ধারা:' : 'Detected Governing Statutory Provisions:'}</h4>
              <div class="ocr-provisions-chips">
                ${(a.statutory_provisions || [])
                  .map(
                    (p: string) => `
                  <button type="button" class="ocr-prov-chip" data-query="Explain legal requirements and validity of ${escapeHtml(p)} in Bangladesh">
                    ⚖️ ${escapeHtml(p)} ➔
                  </button>
                `
                  )
                  .join('')}
              </div>
            </div>
          `
              : ''
          }

          <!-- Red Flags / Notices -->
          ${
            (a.potential_risks_or_notices || []).length > 0
              ? `
            <div class="ocr-risks-box">
              <h4>⚠️ ${isBn ? 'আইনি ঝুঁকি বা লক্ষণীয় বিষয়সমূহ:' : 'Potential Legal Risks & Notices:'}</h4>
              <ul>
                ${(a.potential_risks_or_notices || []).map((r: string) => `<li>${escapeHtml(r)}</li>`).join('')}
              </ul>
            </div>
          `
              : ''
          }

          <!-- Transcription Box -->
          <div class="ocr-transcript-box">
            <div class="ocr-transcript-header">
              <h4>${isBn ? 'নথির সম্পূর্ণ পাঠ্য (Transcription):' : 'Full Transcription Text:'}</h4>
              <div class="ocr-transcript-actions">
                <button type="button" class="button button-outline ocr-copy-btn" id="ocr-copy-btn">
                  📋 ${isBn ? 'কপি করুন' : 'Copy Text'}
                </button>
                <button type="button" class="button button-primary ocr-send-chat-btn" id="ocr-send-chat-btn">
                  💬 ${isBn ? 'চ্যাটে পাঠান' : 'Research in Chat'}
                </button>
              </div>
            </div>
            <div class="ocr-transcript-content">
              <pre>${escapeHtml(a.transcription_markdown || 'No transcription extracted.')}</pre>
            </div>
          </div>
        </div>
      `;

      resultsContainer.style.display = 'block';

      // Reset handler
      resultsContainer.querySelector('#ocr-new-file-btn')?.addEventListener('click', () => {
        resultsContainer.style.display = 'none';
        dropzone.style.display = 'flex';
        selectedFile = null;
      });

      // Copy text handler
      resultsContainer.querySelector('#ocr-copy-btn')?.addEventListener('click', () => {
        if (a.transcription_markdown) {
          navigator.clipboard.writeText(a.transcription_markdown);
          const btn = resultsContainer.querySelector('#ocr-copy-btn') as HTMLElement;
          btn.textContent = isBn ? '✓ কপি হয়েছে!' : '✓ Copied!';
          setTimeout(() => {
            btn.textContent = isBn ? '📋 কপি করুন' : '📋 Copy Text';
          }, 2000);
        }
      });

      // Send to chat handler
      resultsContainer.querySelector('#ocr-send-chat-btn')?.addEventListener('click', () => {
        const summaryPrompt = `Analyze this ${a.document_type || 'legal document'}: \n\n${a.transcription_markdown?.slice(0, 1200) || ''}`;
        closeModal();
        if (onSendToChat) {
          onSendToChat(summaryPrompt);
        }
      });

      // Click on statutory provision chip
      resultsContainer.querySelectorAll('.ocr-prov-chip').forEach((chip) => {
        chip.addEventListener('click', () => {
          const q = chip.getAttribute('data-query');
          if (q) {
            closeModal();
            if (onSendToChat) {
              onSendToChat(q);
            }
          }
        });
      });
    } catch (e: any) {
      loadingState.style.display = 'none';
      resultsContainer.innerHTML = `<div class="ocr-error-box"><p>${e.message || 'Error occurred.'}</p></div>`;
      resultsContainer.style.display = 'block';
    }
  });
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
