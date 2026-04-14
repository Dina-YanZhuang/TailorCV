/* ── TailorCV front-end logic ─────────────────────────────────────────── */
(function () {
  'use strict';

  const form        = document.getElementById('tailorForm');
  const cvFileInput = document.getElementById('cvFile');
  const jdFileInput = document.getElementById('jdFile');
  const jdTextArea  = document.getElementById('jdText');
  const cvPreview   = document.getElementById('cvPreview');
  const jdPreview   = document.getElementById('jdPreview');
  const cvLabel     = document.getElementById('cvLabel');
  const jdLabel     = document.getElementById('jdLabel');
  const submitBtn   = document.getElementById('submitBtn');
  const btnLabel    = document.getElementById('btnLabel');
  const btnSpinner  = document.getElementById('btnSpinner');
  const errorBanner = document.getElementById('errorBanner');
  const resultSec   = document.getElementById('resultSection');
  const resultDiv   = document.getElementById('resultContent');
  const copyBtn     = document.getElementById('copyBtn');
  const downloadBtn = document.getElementById('downloadBtn');

  let tailoredMarkdown = '';

  /* ── File-name preview helpers ──────────────────────────────────────── */
  function updateFilePreview(input, labelEl, previewEl) {
    if (input.files && input.files[0]) {
      const name = input.files[0].name;
      labelEl.textContent = '✅ ' + name;
      previewEl.textContent = formatBytes(input.files[0].size);
    } else {
      labelEl.textContent = 'Click to choose or drag & drop';
      previewEl.textContent = '';
    }
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  }

  cvFileInput.addEventListener('change', () => updateFilePreview(cvFileInput, cvLabel, cvPreview));
  jdFileInput.addEventListener('change', () => updateFilePreview(jdFileInput, jdLabel, jdPreview));

  /* ── Drag-and-drop for both cards ───────────────────────────────────── */
  function enableDragDrop(cardId, fileInput, labelEl, previewEl) {
    const card = document.getElementById(cardId);

    card.addEventListener('dragover', (e) => {
      e.preventDefault();
      card.classList.add('drag-over');
    });
    card.addEventListener('dragleave', () => card.classList.remove('drag-over'));
    card.addEventListener('drop', (e) => {
      e.preventDefault();
      card.classList.remove('drag-over');
      const files = e.dataTransfer.files;
      if (files && files[0]) {
        const dt = new DataTransfer();
        dt.items.add(files[0]);
        fileInput.files = dt.files;
        updateFilePreview(fileInput, labelEl, previewEl);
      }
    });
  }

  enableDragDrop('cvCard', cvFileInput, cvLabel, cvPreview);
  enableDragDrop('jdCard', jdFileInput, jdLabel, jdPreview);

  /* ── Helpers ─────────────────────────────────────────────────────────── */
  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.remove('hidden');
    resultSec.classList.add('hidden');
  }

  function clearError() {
    errorBanner.textContent = '';
    errorBanner.classList.add('hidden');
  }

  function setLoading(loading) {
    submitBtn.disabled = loading;
    btnLabel.textContent  = loading ? 'Working…' : '✨ Tailor My CV';
    btnSpinner.classList.toggle('hidden', !loading);
  }

  /* ── Form submission ─────────────────────────────────────────────────── */
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();

    // Basic client-side validation
    if (!cvFileInput.files || !cvFileInput.files[0]) {
      showError('Please upload your master CV.');
      return;
    }
    const hasJdFile = jdFileInput.files && jdFileInput.files[0];
    const hasJdText = jdTextArea.value.trim().length > 0;
    if (!hasJdFile && !hasJdText) {
      showError('Please upload a job description file or paste the job description text.');
      return;
    }

    const formData = new FormData();
    formData.append('cv_file', cvFileInput.files[0]);
    if (hasJdFile) {
      formData.append('jd_file', jdFileInput.files[0]);
    } else {
      formData.append('jd_text', jdTextArea.value.trim());
    }

    setLoading(true);
    resultSec.classList.add('hidden');

    try {
      const response = await fetch('/api/tailor', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        showError(data.detail || `Server error (${response.status})`);
        return;
      }

      tailoredMarkdown = data.tailored_cv || '';
      resultDiv.innerHTML = marked.parse(tailoredMarkdown);
      resultSec.classList.remove('hidden');
      resultSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      showError('Network error — please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  });

  /* ── Copy button ─────────────────────────────────────────────────────── */
  copyBtn.addEventListener('click', async () => {
    if (!tailoredMarkdown) return;
    try {
      await navigator.clipboard.writeText(tailoredMarkdown);
      const orig = copyBtn.textContent;
      copyBtn.textContent = '✅ Copied!';
      setTimeout(() => { copyBtn.textContent = orig; }, 2000);
    } catch (clipboardErr) {
      // Clipboard API may be unavailable in non-HTTPS / sandboxed contexts;
      // fall back to the legacy execCommand approach.
      const ta = document.createElement('textarea');
      ta.value = tailoredMarkdown;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
  });

  /* ── Download button ─────────────────────────────────────────────────── */
  downloadBtn.addEventListener('click', () => {
    if (!tailoredMarkdown) return;
    const blob = new Blob([tailoredMarkdown], { type: 'text/markdown' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'tailored_cv.md';
    a.click();
    URL.revokeObjectURL(url);
  });
})();
