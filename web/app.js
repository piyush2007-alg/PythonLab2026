/**
 * PyQuality - Modern Code Quality & Comment Analyzer
 * Client-side Controller & Interactive Engine
 * (Zero dependency on sample_inputs)
 */

// Clean, PEP 8-compliant starter template
const STARTER_TEMPLATE = `"""Module for code quality calculation."""


def calculate_metrics(values):
    """Calculate and return average and total from a list of numbers."""
    if not values:
        return {"total": 0, "average": 0.0}
    total = sum(values)
    avg = total / len(values)
    return {"total": total, "average": round(avg, 2)}
`;

// --- Application State ---
const state = {
  activeFileName: "code.py",
  activeReports: [],
  currentReport: null,
  activeSeverityFilter: "ALL",
  activeCategoryFilter: "ALL",
  searchQuery: "",
  theme: localStorage.getItem("pyquality_theme") || "dark"
};

// --- DOM Element References ---
const elements = {
  html: document.documentElement,
  codeEditor: document.getElementById("codeEditor"),
  editorGutter: document.getElementById("editorGutter"),
  editorMetrics: document.getElementById("editorMetrics"),
  activeFileTitle: document.getElementById("activeFileTitle"),
  cursorPos: document.getElementById("cursorPos"),
  astSyntaxStatus: document.getElementById("astSyntaxStatus"),
  btnAnalyze: document.getElementById("btnAnalyze"),
  btnAutoFix: document.getElementById("btnAutoFix"),
  btnClearCode: document.getElementById("btnClearCode"),
  btnUploadFile: document.getElementById("btnUploadFile"),
  fileInput: document.getElementById("fileInput"),
  btnThemeToggle: document.getElementById("btnThemeToggle"),
  tabEditor: document.getElementById("tabEditor"),
  tabWorkspace: document.getElementById("tabWorkspace"),
  editorView: document.getElementById("editorView"),
  workspaceView: document.getElementById("workspaceView"),
  // Quick Actions
  btnNewFile: document.getElementById("btnNewFile"),
  btnPasteClipboard: document.getElementById("btnPasteClipboard"),
  btnLoadTemplate: document.getElementById("btnLoadTemplate"),
  // Gauge & Metrics
  scoreDisplay: document.getElementById("scoreDisplay"),
  gradeBadge: document.getElementById("gradeBadge"),
  gaugeProgress: document.getElementById("gaugeProgress"),
  statTotalIssues: document.getElementById("statTotalIssues"),
  tagHighCount: document.getElementById("tagHighCount"),
  tagMedCount: document.getElementById("tagMedCount"),
  tagLowCount: document.getElementById("tagLowCount"),
  statCommentRatio: document.getElementById("statCommentRatio"),
  ratioFill: document.getElementById("ratioFill"),
  statCommentHealth: document.getElementById("statCommentHealth"),
  statFuncCount: document.getElementById("statFuncCount"),
  statMaxComplexity: document.getElementById("statMaxComplexity"),
  statMaxNesting: document.getElementById("statMaxNesting"),
  // Issues & Filters
  issuesListContainer: document.getElementById("issuesListContainer"),
  searchIssues: document.getElementById("searchIssues"),
  countAll: document.getElementById("countAll"),
  countHigh: document.getElementById("countHigh"),
  countMed: document.getElementById("countMed"),
  countLow: document.getElementById("countLow"),
  complexityContainer: document.getElementById("complexityContainer"),
  // Workspace Scanner
  btnScanWorkspace: document.getElementById("btnScanWorkspace"),
  btnUploadBatch: document.getElementById("btnUploadBatch"),
  batchUploadInput: document.getElementById("batchUploadInput"),
  workspaceGrid: document.getElementById("workspaceGrid"),
  wsTotalFiles: document.getElementById("wsTotalFiles"),
  wsAvgScore: document.getElementById("wsAvgScore"),
  wsOverallGrade: document.getElementById("wsOverallGrade"),
  wsTotalIssues: document.getElementById("wsTotalIssues"),
  workspaceBadge: document.getElementById("workspaceBadge"),
  // Export Modal
  btnOpenExport: document.getElementById("btnOpenExport"),
  exportModal: document.getElementById("exportModal"),
  btnCloseExport: document.getElementById("btnCloseExport"),
  modalTabMarkdown: document.getElementById("modalTabMarkdown"),
  modalTabJson: document.getElementById("modalTabJson"),
  exportPreviewCode: document.getElementById("exportPreviewCode"),
  btnCopyExport: document.getElementById("btnCopyExport"),
  btnDownloadExport: document.getElementById("btnDownloadExport"),
  // Toast
  toast: document.getElementById("toast"),
  toastMsg: document.getElementById("toastMsg")
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initEditor();
  initNavigation();
  initQuickActions();
  initFilterControls();
  initExportModal();
  initWorkspaceScanner();

  // Load starter template on first launch
  loadTemplateCode();
});

// --- Theme Management ---
function initTheme() {
  elements.html.setAttribute("data-theme", state.theme);
  elements.btnThemeToggle.addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    elements.html.setAttribute("data-theme", state.theme);
    localStorage.setItem("pyquality_theme", state.theme);
    showToast(`Switched to ${state.theme === "dark" ? "Dark" : "Light"} Mode`);
  });
}

// --- Navigation Modes ---
function initNavigation() {
  const switchMode = (targetId) => {
    document.querySelectorAll(".segment-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.target === targetId);
    });
    document.querySelectorAll(".view-panel").forEach(panel => {
      panel.classList.toggle("active", panel.id === targetId);
    });
  };

  elements.tabEditor.addEventListener("click", () => switchMode("editorView"));
  elements.tabWorkspace.addEventListener("click", () => {
    switchMode("workspaceView");
    if (!state.activeReports || state.activeReports.length <= 1) {
      scanWorkspace();
    }
  });
}

// --- Quick Actions Bar ---
function initQuickActions() {
  if (elements.btnNewFile) {
    elements.btnNewFile.addEventListener("click", () => {
      elements.codeEditor.value = "";
      state.activeFileName = "untitled.py";
      elements.activeFileTitle.textContent = "untitled.py";
      updateGutter();
      runAnalysis();
      showToast("Created new blank file");
    });
  }

  if (elements.btnPasteClipboard) {
    elements.btnPasteClipboard.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          elements.codeEditor.value = text;
          state.activeFileName = "pasted_code.py";
          elements.activeFileTitle.textContent = "pasted_code.py";
          updateGutter();
          runAnalysis();
          showToast("Pasted code from clipboard");
        } else {
          showToast("Clipboard is empty");
        }
      } catch (err) {
        showToast("Clipboard permission required. Use Ctrl+V instead.");
      }
    });
  }

  if (elements.btnLoadTemplate) {
    elements.btnLoadTemplate.addEventListener("click", () => {
      loadTemplateCode();
      showToast("Inserted Clean PEP 8 Template");
    });
  }
}

function loadTemplateCode() {
  elements.codeEditor.value = STARTER_TEMPLATE;
  state.activeFileName = "code.py";
  elements.activeFileTitle.textContent = "code.py";
  updateGutter();
  runAnalysis();
}

// --- Code Editor Engine ---
function updateGutter() {
  const text = elements.codeEditor.value;
  const lines = text.split("\n");
  const count = lines.length;

  let gutterHtml = "";
  for (let i = 1; i <= count; i++) {
    gutterHtml += `<div class="gutter-line" id="gutter-line-${i}">${i}</div>`;
  }
  elements.editorGutter.innerHTML = gutterHtml;
  elements.editorGutter.scrollTop = elements.codeEditor.scrollTop;
  elements.editorMetrics.textContent = `${count} lines • ${text.length} chars`;
}

function initEditor() {
  elements.codeEditor.addEventListener("scroll", () => {
    elements.editorGutter.scrollTop = elements.codeEditor.scrollTop;
  });

  elements.codeEditor.addEventListener("keyup", updateCursorPos);
  elements.codeEditor.addEventListener("click", updateCursorPos);

  function updateCursorPos() {
    const pos = elements.codeEditor.selectionStart;
    const text = elements.codeEditor.value.substring(0, pos);
    const lines = text.split("\n");
    const curLine = lines.length;
    const curCol = lines[lines.length - 1].length + 1;
    elements.cursorPos.textContent = `Ln ${curLine}, Col ${curCol}`;
  }

  // Handle Tab key (indent 4 spaces)
  elements.codeEditor.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = elements.codeEditor.selectionStart;
      const end = elements.codeEditor.selectionEnd;
      const val = elements.codeEditor.value;
      elements.codeEditor.value = val.substring(0, start) + "    " + val.substring(end);
      elements.codeEditor.selectionStart = elements.codeEditor.selectionEnd = start + 4;
      updateGutter();
    }
  });

  elements.codeEditor.addEventListener("input", () => {
    updateGutter();
    elements.astSyntaxStatus.textContent = "Modified (Click Analyze)";
  });

  // Actions
  elements.btnAnalyze.addEventListener("click", () => runAnalysis());

  elements.btnClearCode.addEventListener("click", () => {
    elements.codeEditor.value = "";
    state.activeFileName = "untitled.py";
    elements.activeFileTitle.textContent = "untitled.py";
    updateGutter();
    runAnalysis();
    showToast("Editor cleared");
  });

  // Single file upload
  elements.btnUploadFile.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        elements.codeEditor.value = event.target.result;
        state.activeFileName = file.name;
        elements.activeFileTitle.textContent = file.name;
        updateGutter();
        runAnalysis();
        showToast(`Loaded ${file.name}`);
      };
      reader.readAsText(file);
    }
  });

  // Safe auto-fix
  elements.btnAutoFix.addEventListener("click", async () => {
    const code = elements.codeEditor.value;
    if (!code.trim()) {
      showToast("Editor is empty. Paste or write code first.");
      return;
    }

    try {
      showToast("Analyzing and applying auto-fixes...");
      const res = await fetch("/api/quick-fix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: code,
          filename: state.activeFileName
        })
      });
      const data = await res.json();
      if (data.success) {
        elements.codeEditor.value = data.fixed_code;
        updateGutter();
        runAnalysis();

        // Populate and display Auto-Fix Summary Modal
        const modal = document.getElementById("autoFixModal");
        const fixScoreBefore = document.getElementById("fixScoreBefore");
        const fixScoreAfter = document.getElementById("fixScoreAfter");
        const autoFixSummaryText = document.getElementById("autoFixSummaryText");
        const autoFixList = document.getElementById("autoFixList");

        if (fixScoreBefore) {
          fixScoreBefore.textContent = `Before: ${data.score_before} (${data.grade_before})`;
        }
        if (fixScoreAfter) {
          fixScoreAfter.textContent = `After: ${data.score_after} (${data.grade_after})`;
        }
        if (autoFixSummaryText) {
          autoFixSummaryText.textContent = data.fixes_count > 0
            ? `${data.fixes_count} automated repair(s) were applied to formatting, imports, and syntax.`
            : "Code style is already clean! No repairs needed.";
        }

        if (autoFixList) {
          if (data.fixes_applied && data.fixes_applied.length > 0) {
            autoFixList.innerHTML = data.fixes_applied.map(fix => `
              <div class="autofix-fix-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>${escapeHtml(fix)}</span>
              </div>
            `).join("");
          } else {
            autoFixList.innerHTML = `
              <div class="autofix-fix-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>All checked rules pass cleanly. No changes required.</span>
              </div>
            `;
          }
        }

        if (modal) {
          modal.classList.add("active");
        }
        showToast(data.fixes_count > 0 ? `Applied ${data.fixes_count} automated repairs!` : "Code already compliant.");
      }
    } catch (err) {
      console.warn("Backend unavailable, using client-side auto-fix engine:", err);
      const fixResult = runClientSideAutoFix(code, state.activeFileName);
      elements.codeEditor.value = fixResult.fixed_code;
      updateGutter();
      runAnalysis();

      const modal = document.getElementById("autoFixModal");
      const fixScoreBefore = document.getElementById("fixScoreBefore");
      const fixScoreAfter = document.getElementById("fixScoreAfter");
      const autoFixSummaryText = document.getElementById("autoFixSummaryText");
      const autoFixList = document.getElementById("autoFixList");

      if (fixScoreBefore) fixScoreBefore.textContent = `Before: ${fixResult.score_before} (${fixResult.grade_before})`;
      if (fixScoreAfter) fixScoreAfter.textContent = `After: ${fixResult.score_after} (${fixResult.grade_after})`;
      if (autoFixSummaryText) {
        autoFixSummaryText.textContent = fixResult.fixes_count > 0
          ? `${fixResult.fixes_count} automated repairs applied (Client-Side Engine).`
          : "Code style is already clean! No repairs needed.";
      }
      if (autoFixList) {
        if (fixResult.fixes_applied.length > 0) {
          autoFixList.innerHTML = fixResult.fixes_applied.map(fix => `
            <div class="autofix-fix-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <span>${escapeHtml(fix)}</span>
            </div>
          `).join("");
        } else {
          autoFixList.innerHTML = `<div class="autofix-fix-item"><span>All rules pass cleanly.</span></div>`;
        }
      }
      if (modal) modal.classList.add("active");
      showToast(fixResult.fixes_count > 0 ? `Applied ${fixResult.fixes_count} automated repairs!` : "Code already compliant.");
    }
  });

  // Modal dismiss handlers for Auto-Fix
  const autoFixModal = document.getElementById("autoFixModal");
  const btnCloseAutoFix = document.getElementById("btnCloseAutoFix");
  const btnAcceptAutoFix = document.getElementById("btnAcceptAutoFix");

  if (btnCloseAutoFix && autoFixModal) {
    btnCloseAutoFix.addEventListener("click", () => autoFixModal.classList.remove("active"));
  }
  if (btnAcceptAutoFix && autoFixModal) {
    btnAcceptAutoFix.addEventListener("click", () => autoFixModal.classList.remove("active"));
  }
  if (autoFixModal) {
    autoFixModal.addEventListener("click", (e) => {
      if (e.target === autoFixModal) {
        autoFixModal.classList.remove("active");
      }
    });
  }
}

// --- Analysis Execution ---
async function runAnalysis() {
  const code = elements.codeEditor.value;
  elements.btnAnalyze.classList.add("pulsing");

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: code,
        filename: state.activeFileName
      })
    });

    if (!res.ok) throw new Error("API server returned non-200");
    const data = await res.json();
    if (data.success && data.report) {
      state.currentReport = data.report;
      state.activeReports = [data.report];
      renderDashboard(data.report);
      elements.astSyntaxStatus.textContent = data.report.issues.some(i => i.category === "Syntax")
        ? "AST: Syntax Error"
        : "AST: Valid Tree (Server)";
      return;
    }
    throw new Error("Invalid response format");
  } catch (err) {
    // Client-side static analyzer fallback (for GitHub Pages)
    const report = runClientSideAnalysis(code, state.activeFileName);
    state.currentReport = report;
    state.activeReports = [report];
    renderDashboard(report);
    elements.astSyntaxStatus.textContent = "Engine: Client-Side (Static)";
  } finally {
    elements.btnAnalyze.classList.remove("pulsing");
  }
}

// --- Dashboard & Metrics Rendering ---
function renderDashboard(report) {
  // 1. Gauge Score & Circle animation
  const score = report.score;
  const grade = report.grade;
  elements.scoreDisplay.textContent = score;

  elements.gradeBadge.textContent = grade;
  elements.gradeBadge.className = `gauge-grade-badge grade-${grade.toLowerCase()}`;

  // Radial SVG Arc calculation (Circumference ~339.29)
  const circumference = 339.29;
  const offset = circumference - (score / 100) * circumference;
  elements.gaugeProgress.style.strokeDashoffset = offset;

  let strokeColor = "var(--accent-primary)";
  if (grade === "Best") strokeColor = "var(--accent-emerald)";
  else if (grade === "Good") strokeColor = "var(--accent-indigo)";
  else if (grade === "Average") strokeColor = "var(--accent-amber)";
  else strokeColor = "var(--accent-coral)";
  elements.gaugeProgress.style.stroke = strokeColor;

  // 2. Summary stats
  const stats = report.stats || {
    total: report.issues.length,
    high: 0,
    medium: 0,
    low: 0
  };

  elements.statTotalIssues.textContent = stats.total;
  elements.tagHighCount.textContent = `${stats.high} High`;
  elements.tagMedCount.textContent = `${stats.medium} Med`;
  elements.tagLowCount.textContent = `${stats.low} Low`;

  elements.countAll.textContent = stats.total;
  elements.countHigh.textContent = stats.high;
  elements.countMed.textContent = stats.medium;
  elements.countLow.textContent = stats.low;

  // Comment Ratio
  const ratioPct = Math.round(report.comment_ratio * 100);
  elements.statCommentRatio.textContent = `${ratioPct}%`;
  elements.ratioFill.style.width = `${Math.min(100, ratioPct * 2)}%`;
  elements.ratioFill.style.background = ratioPct >= 10 ? "var(--accent-emerald)" : "var(--accent-coral)";
  elements.statCommentHealth.textContent = ratioPct >= 10 ? "Healthy ratio (≥ 10%)" : "Low comment ratio (< 10%)";

  // Functions & Complexity
  const funcs = report.complexity_metrics || [];
  elements.statFuncCount.textContent = funcs.length;
  const maxComp = funcs.length ? Math.max(...funcs.map(f => f.complexity)) : 0;
  const maxNest = funcs.length ? Math.max(...funcs.map(f => f.nesting_depth)) : 0;
  elements.statMaxComplexity.textContent = `Peak Complexity: ${maxComp}`;
  elements.statMaxNesting.textContent = maxNest;

  // 3. Render Issues
  renderIssuesList();

  // 4. Render Complexity Breakdown
  renderComplexityTable(funcs);
}

// --- Issue List & Filters ---
function initFilterControls() {
  document.querySelectorAll(".filter-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      state.activeSeverityFilter = pill.dataset.sev;
      renderIssuesList();
    });
  });

  document.querySelectorAll(".filter-pill-cat").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".filter-pill-cat").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      state.activeCategoryFilter = pill.dataset.cat;
      renderIssuesList();
    });
  });

  elements.searchIssues.addEventListener("input", (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    renderIssuesList();
  });
}

function renderIssuesList() {
  if (!state.currentReport) return;
  const issues = state.currentReport.issues || [];

  const filtered = issues.filter(issue => {
    if (state.activeSeverityFilter !== "ALL" && issue.severity !== state.activeSeverityFilter) {
      return false;
    }
    if (state.activeCategoryFilter !== "ALL" && issue.category !== state.activeCategoryFilter) {
      return false;
    }
    if (state.searchQuery) {
      const text = `${issue.issue} ${issue.category} ${issue.line || ""} ${issue.tip || ""}`.toLowerCase();
      if (!text.includes(state.searchQuery)) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    elements.issuesListContainer.innerHTML = `
      <div class="empty-issues-placeholder">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <h4>No Issues Detected</h4>
        <p>Your code matches Python quality and PEP 8 standards cleanly!</p>
      </div>
    `;
    return;
  }

  elements.issuesListContainer.innerHTML = filtered.map(item => {
    const sevClass = `badge-sev-${item.severity.toLowerCase().substring(0, 3)}`;

    return `
      <div class="issue-card-item sev-${item.severity}">
        <div class="issue-item-header">
          <div class="issue-badge-group">
            <span class="badge-sev ${sevClass}">${item.severity}</span>
            <span class="badge-cat">${item.category || "General"}</span>
          </div>
          ${item.line ? `<button type="button" class="btn-jump-line" onclick="jumpToLine(${item.line})">Line ${item.line}</button>` : ""}
        </div>
        <div class="issue-item-title">${escapeHtml(item.issue)}</div>
        ${item.tip ? `
          <div class="issue-item-tip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>${escapeHtml(item.tip)}</span>
          </div>
        ` : ""}
      </div>
    `;
  }).join("");
}

// Jump and highlight line in code editor
window.jumpToLine = function(lineNum) {
  const text = elements.codeEditor.value;
  const lines = text.split("\n");
  if (lineNum > lines.length) return;

  let startPos = 0;
  for (let i = 0; i < lineNum - 1; i++) {
    startPos += lines[i].length + 1;
  }
  const endPos = startPos + lines[lineNum - 1].length;

  elements.codeEditor.focus();
  elements.codeEditor.setSelectionRange(startPos, endPos);

  const lineHeight = 24.5;
  elements.codeEditor.scrollTop = (lineNum - 4) * lineHeight;

  document.querySelectorAll(".gutter-line").forEach(g => g.classList.remove("highlight-active"));
  const gutterEl = document.getElementById(`gutter-line-${lineNum}`);
  if (gutterEl) {
    gutterEl.classList.add("highlight-active");
    setTimeout(() => gutterEl.classList.remove("highlight-active"), 2500);
  }
};

// --- Function Complexity Explorer ---
function renderComplexityTable(funcs) {
  if (!funcs || funcs.length === 0) {
    elements.complexityContainer.innerHTML = `
      <p style="font-size: 0.8rem; color: var(--text-dim); padding: 0.5rem 0;">No function definitions detected in this module.</p>
    `;
    return;
  }

  elements.complexityContainer.innerHTML = `
    <div class="complexity-grid">
      ${funcs.map(f => {
        const compClass = f.complexity > 10 ? "func-stat-danger" : (f.complexity > 5 ? "func-stat-warn" : "func-stat-ok");
        const nestClass = f.nesting_depth > 4 ? "func-stat-danger" : "func-stat-ok";
        const lenClass = f.length > 50 ? "func-stat-warn" : "func-stat-ok";

        return `
          <div class="func-metric-tile">
            <div class="func-tile-header">
              <span class="func-name-pill" title="${escapeHtml(f.function)}">${escapeHtml(f.function)}()</span>
              <span class="func-line-dim">Ln ${f.line}</span>
            </div>
            <div class="func-stats-row">
              <span class="func-stat-badge ${compClass}" title="Cyclomatic Complexity">CC: ${f.complexity}</span>
              <span class="func-stat-badge ${nestClass}" title="Nesting Depth">Nest: ${f.nesting_depth}</span>
              <span class="func-stat-badge ${lenClass}" title="Function Length">${f.length} lines</span>
            </div>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

// --- Workspace Scanner ---
function initWorkspaceScanner() {
  elements.btnScanWorkspace.addEventListener("click", () => scanWorkspace());

  elements.btnUploadBatch.addEventListener("click", () => elements.batchUploadInput.click());
  elements.batchUploadInput.addEventListener("change", async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    const payloadFiles = [];
    for (const f of files) {
      const text = await f.text();
      payloadFiles.push({ name: f.name, content: text });
    }

    try {
      showToast(`Analyzing ${payloadFiles.length} uploaded files...`);
      const res = await fetch("/api/analyze-files", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ files: payloadFiles })
      });
      const data = await res.json();
      if (data.success) {
        state.activeReports = data.reports;
        renderWorkspaceResults(data.reports, data.summary);
      }
    } catch (err) {
      console.error(err);
      showToast("Batch analysis failed");
    }
  });
}

async function scanWorkspace() {
  elements.btnScanWorkspace.classList.add("pulsing");
  try {
    showToast("Scanning project workspace files...");
    const res = await fetch("/api/analyze-workspace", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ directory: "" })
    });
    const data = await res.json();
    if (data.success) {
      state.activeReports = data.reports;
      renderWorkspaceResults(data.reports, data.summary);
      showToast(`Scanned ${data.reports.length} files successfully!`);
    }
  } catch (err) {
    console.error(err);
    showToast("Workspace scan error");
  } finally {
    elements.btnScanWorkspace.classList.remove("pulsing");
  }
}

function renderWorkspaceResults(reports, summary) {
  elements.wsTotalFiles.textContent = summary.total_files;
  elements.wsAvgScore.textContent = summary.average_score;
  elements.wsOverallGrade.textContent = summary.overall_grade;
  elements.wsTotalIssues.textContent = summary.total_issues;
  elements.workspaceBadge.textContent = summary.total_files;

  elements.workspaceGrid.innerHTML = reports.map((r, idx) => {
    const gradeClass = `grade-${r.grade.toLowerCase()}`;
    return `
      <div class="file-card-neu">
        <div class="file-card-top">
          <div class="file-card-title">${escapeHtml(r.filename)}</div>
          <span class="gauge-grade-badge ${gradeClass}">${r.grade}</span>
        </div>
        <div class="file-card-stats">
          <div class="file-stat-col">
            <span class="file-stat-label">Score</span>
            <span class="file-stat-num">${r.score}</span>
          </div>
          <div class="file-stat-col">
            <span class="file-stat-label">Issues</span>
            <span class="file-stat-num text-accent-coral">${r.issues.length}</span>
          </div>
          <div class="file-stat-col">
            <span class="file-stat-label">Comments</span>
            <span class="file-stat-num">${Math.round(r.comment_ratio * 100)}%</span>
          </div>
        </div>
        <div class="file-card-actions">
          <button type="button" class="btn-neu-small" onclick="loadWorkspaceFileIntoEditor(${idx})">
            <span>Inspect in Editor</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 12px; height: 12px;">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </div>
    `;
  }).join("");
}

window.loadWorkspaceFileIntoEditor = async function(index) {
  const report = state.activeReports[index];
  if (!report) return;

  try {
    const res = await fetch(`/api/file-content?path=${encodeURIComponent(report.filename)}`);
    const data = await res.json();
    if (data.success && data.content !== undefined) {
      elements.codeEditor.value = data.content;
      state.activeFileName = report.filename;
      elements.activeFileTitle.textContent = report.filename;
      updateGutter();
      runAnalysis();
      showToast(`Loaded ${report.filename}`);
    }
  } catch (err) {
    showToast(`Could not load ${report.filename}`);
  }

  // Switch back to editor tab
  elements.tabEditor.click();
};

// --- Export Report Modal ---
function initExportModal() {
  let exportMode = "markdown";

  const refreshPreview = async () => {
    const reports = state.activeReports.length > 0 ? state.activeReports : (state.currentReport ? [state.currentReport] : []);
    if (!reports.length) {
      elements.exportPreviewCode.textContent = "No analysis data available to export.";
      return;
    }

    if (exportMode === "markdown") {
      try {
        const res = await fetch("/api/export-markdown", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reports })
        });
        if (data && data.markdown) {
          elements.exportPreviewCode.textContent = data.markdown;
        } else {
          elements.exportPreviewCode.textContent = generateClientSideMarkdownReport(reports);
        }
      } catch {
        elements.exportPreviewCode.textContent = generateClientSideMarkdownReport(reports);
      }
    } else {
      elements.exportPreviewCode.textContent = JSON.stringify(reports, null, 2);
    }
  };

  elements.btnOpenExport.addEventListener("click", () => {
    elements.exportModal.classList.add("active");
    refreshPreview();
  });

  elements.btnCloseExport.addEventListener("click", () => {
    elements.exportModal.classList.remove("active");
  });

  elements.exportModal.addEventListener("click", (e) => {
    if (e.target === elements.exportModal) {
      elements.exportModal.classList.remove("active");
    }
  });

  elements.modalTabMarkdown.addEventListener("click", () => {
    exportMode = "markdown";
    elements.modalTabMarkdown.classList.add("active");
    elements.modalTabJson.classList.remove("active");
    elements.btnDownloadExport.querySelector("span").textContent = "Download Report (.md)";
    refreshPreview();
  });

  elements.modalTabJson.addEventListener("click", () => {
    exportMode = "json";
    elements.modalTabJson.classList.add("active");
    elements.modalTabMarkdown.classList.remove("active");
    elements.btnDownloadExport.querySelector("span").textContent = "Download JSON (.json)";
    refreshPreview();
  });

  elements.btnCopyExport.addEventListener("click", () => {
    const text = elements.exportPreviewCode.textContent;
    navigator.clipboard.writeText(text).then(() => {
      showToast("Report copied to clipboard!");
    });
  });

  elements.btnDownloadExport.addEventListener("click", () => {
    const text = elements.exportPreviewCode.textContent;
    const isMd = exportMode === "markdown";
    const filename = isMd ? "code_quality_report.md" : "code_quality_report.json";
    const mime = isMd ? "text/markdown" : "application/json";

    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`);
  });
}

// --- Utilities ---
function showToast(msg) {
  elements.toastMsg.textContent = msg;
  elements.toast.classList.add("show");
  clearTimeout(elements.toast._timer);
  elements.toast._timer = setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 2600);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ==========================================================================
// Client-Side Analyzer Engine (Static / GitHub Pages Standalone Support)
// ==========================================================================
function runClientSideAnalysis(code, filename = "code.py") {
  const lines = code.split("\n");
  const totalLines = lines.length;
  const issues = [];

  // Style checks
  const opRe = /[a-zA-Z0-9_)\]]=[a-zA-Z0-9_(\-]/;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const lineNum = i + 1;
    const stripped = line.replace(/\r$/, "");

    if (stripped.length > 79) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Style",
        issue: `Line exceeds 79 chars (${stripped.length})`,
        severity: "Low",
        tip: "Break this line across multiple lines or reformat to fit within 79 characters."
      });
    }
    if (stripped !== stripped.trimEnd()) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Style",
        issue: "Trailing whitespace",
        severity: "Low",
        tip: "Remove unnecessary spaces at the end of the line."
      });
    }
    if (line.includes("\t")) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Style",
        issue: "Tab character used for indentation",
        severity: "Medium",
        tip: "Use 4 spaces instead of tabs for standard Python indentation."
      });
    }
    if (stripped.includes(";") && !stripped.trim().startsWith("#")) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Style",
        issue: "Multiple statements on one line",
        severity: "Medium",
        tip: "Split statements onto separate lines rather than using semicolons."
      });
    }
    if (opRe.test(stripped) && !stripped.includes("==")) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Style",
        issue: "Missing whitespace around '='",
        severity: "Low",
        tip: "Surround assignment operators with a single space (e.g. 'x = 1')."
      });
    }
    if ((line.startsWith("def ") || line.startsWith("class ")) && i >= 2) {
      const prev2 = lines.slice(i - 2, i);
      if (prev2.filter(p => p.trim() === "").length < 2) {
        issues.push({
          file: filename,
          line: lineNum,
          category: "Style",
          issue: "Expected 2 blank lines before top-level def/class",
          severity: "Low",
          tip: "Add 2 empty lines before top-level class and function definitions per PEP 8."
        });
      }
    }
  }

  // Comment & Docstring checks
  const fillerRe = /^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$/i;
  let hasModuleDocstring = false;
  const firstNonEmpty = lines.find(l => l.trim() !== "");
  if (firstNonEmpty && (firstNonEmpty.trim().startsWith('"""') || firstNonEmpty.trim().startsWith("'''"))) {
    hasModuleDocstring = true;
  }
  if (!hasModuleDocstring && lines.some(l => l.trim())) {
    issues.push({
      file: filename,
      line: 1,
      category: "Comments",
      issue: "Module is missing a top-level docstring",
      severity: "Medium",
      tip: "Add a triple-quoted docstring at line 1 explaining the purpose of this module."
    });
  }

  const codeLines = lines.filter(l => l.trim() && !l.trim().startsWith("#"));
  const commentLines = lines.filter(l => l.trim().startsWith("#"));
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim().startsWith("#") && fillerRe.test(lines[i])) {
      issues.push({
        file: filename,
        line: i + 1,
        category: "Comments",
        issue: "Comment appears to be filler / non-descriptive",
        severity: "Low",
        tip: "Replace placeholder comment with meaningful context."
      });
    }
  }
  const ratio = codeLines.length ? Math.round((commentLines.length / codeLines.length) * 100) / 100 : 0;
  if (ratio < 0.1 && codeLines.length > 0) {
    issues.push({
      file: filename,
      line: null,
      category: "Comments",
      issue: `Low comment-to-code ratio (${ratio})`,
      severity: "Low",
      tip: "Aim for at least 10% explanatory comments."
    });
  }

  // Functions & Complexity estimation
  const complexityMetrics = [];
  const funcRe = /^(?:[ ]{0,4})(?:async\s+)?def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\):/gm;
  let match;
  while ((match = funcRe.exec(code)) !== null) {
    const funcName = match[1];
    const funcArgs = match[2];
    const pos = match.index;
    const lineNum = code.substring(0, pos).split("\n").length;

    if (!/^[a-z_][a-z0-9_]*$/.test(funcName) && !(funcName.startsWith("__") && funcName.endsWith("__"))) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Naming",
        issue: `'${funcName}' does not follow snake_case`,
        severity: "Medium",
        tip: `Rename '${funcName}' to follow standard snake_case convention.`
      });
    }

    if (funcArgs) {
      const argsList = funcArgs.split(",").map(a => a.trim().split("=")[0].split(":")[0].trim());
      for (const arg of argsList) {
        if (arg && arg !== "self" && arg !== "cls" && !/^[a-z_][a-z0-9_]*$/.test(arg)) {
          issues.push({
            file: filename,
            line: lineNum,
            category: "Naming",
            issue: `'${arg}' does not follow snake_case (parameter)`,
            severity: "Medium",
            tip: `Rename parameter '${arg}' to snake_case.`
          });
        }
      }
    }

    const remainingLines = lines.slice(lineNum - 1);
    let funcBody = [];
    let endLine = lineNum;
    for (let j = 1; j < remainingLines.length; j++) {
      const curr = remainingLines[j];
      if (curr.trim() !== "" && !curr.startsWith("    ") && !curr.startsWith("\t")) {
        break;
      }
      funcBody.push(curr);
      endLine = lineNum + j;
    }
    const funcBodyText = funcBody.join("\n");
    const decisionMatches = funcBodyText.match(/\b(if|elif|for|while|except|with|assert|and|or)\b/g) || [];
    const cc = 1 + decisionMatches.length;

    let maxNesting = 0;
    funcBody.forEach(l => {
      const indent = l.search(/\S|$/);
      const depth = Math.max(0, Math.floor((indent - 4) / 4));
      if (depth > maxNesting) maxNesting = depth;
    });

    const funcLength = endLine - lineNum + 1;
    complexityMetrics.push({
      function: funcName,
      line: lineNum,
      complexity: cc,
      nesting_depth: maxNesting,
      length: funcLength
    });

    if (cc > 10) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Complexity",
        issue: `Function '${funcName}' has high cyclomatic complexity (${cc})`,
        severity: "High",
        tip: "Decompose into smaller helper functions."
      });
    }
    if (maxNesting > 4) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Complexity",
        issue: `Function '${funcName}' has deep nesting (depth ${maxNesting})`,
        severity: "Medium",
        tip: "Use guard clauses and early returns."
      });
    }
    if (funcLength > 50) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Complexity",
        issue: `Function '${funcName}' is long (${funcLength} lines)`,
        severity: "Medium",
        tip: "Refactor long functions into modular parts."
      });
    }
  }

  // Class naming
  const classRe = /^(?:[ ]{0,4})class\s+([a-zA-Z0-9_]+)/gm;
  while ((match = classRe.exec(code)) !== null) {
    const className = match[1];
    const pos = match.index;
    const lineNum = code.substring(0, pos).split("\n").length;
    if (!/^[A-Z][a-zA-Z0-9]*$/.test(className)) {
      issues.push({
        file: filename,
        line: lineNum,
        category: "Naming",
        issue: `'${className}' does not follow PascalCase`,
        severity: "Medium",
        tip: `Rename class '${className}' to follow PascalCase convention.`
      });
    }
  }

  // Unused import detection
  const importLines = [];
  lines.forEach((l, idx) => {
    const m = l.match(/^\s*(?:import\s+([a-zA-Z0-9_]+)|from\s+([a-zA-Z0-9_]+)\s+import\s+([a-zA-Z0-9_]+))/);
    if (m) {
      const imp = m[1] || m[3];
      if (imp && imp !== "*") {
        importLines.push({ name: imp, line: idx + 1 });
      }
    }
  });
  importLines.forEach(imp => {
    const restCode = lines.filter((_, idx) => idx !== imp.line - 1).join("\n");
    const nameRe = new RegExp(`\\b${imp.name}\\b`);
    if (!nameRe.test(restCode)) {
      issues.push({
        file: filename,
        line: imp.line,
        category: "Unused Code",
        issue: `Imported name '${imp.name}' is never used`,
        severity: "Low",
        tip: `Remove unused import '${imp.name}'.`
      });
    }
  });

  // Calculate score & grade
  const severityWeights = { High: 5, Medium: 3, Low: 1 };
  const penalty = issues.reduce((acc, i) => acc + (severityWeights[i.severity] || 1), 0);
  const normalized = penalty / Math.max(1, totalLines / 30);
  const score = Math.max(0, Math.round((100 - normalized) * 10) / 10);
  const grade = score >= 90 ? "Best" : score >= 75 ? "Good" : score >= 50 ? "Average" : "Poor";

  const stats = {
    high: issues.filter(i => i.severity === "High").length,
    medium: issues.filter(i => i.severity === "Medium").length,
    low: issues.filter(i => i.severity === "Low").length,
    total: issues.length,
    code_lines: codeLines.length,
    comment_lines: commentLines.length
  };

  return {
    filename,
    total_lines: totalLines,
    issues,
    complexity_metrics: complexityMetrics,
    comment_ratio: ratio,
    score,
    grade,
    stats
  };
}

// Client-Side Auto-Fix Engine
function runClientSideAutoFix(source, filename = "code.py") {
  const reportBefore = runClientSideAnalysis(source, filename);
  const fixes = [];
  const lines = source.split("\n");

  const unusedImportLines = new Set();
  reportBefore.issues
    .filter(i => i.category === "Unused Code" && i.issue.includes("Imported name") && i.line)
    .forEach(i => unusedImportLines.add(i.line));

  const transformed = [];
  for (let i = 0; i < lines.length; i++) {
    const lineno = i + 1;
    let line = lines[i];

    if (unusedImportLines.has(lineno) && (line.trim().startsWith("import ") || line.trim().startsWith("from "))) {
      fixes.push(`Line ${lineno}: Removed unused import statement`);
      continue;
    }

    if (line.trim().startsWith("#") && /^\s*#\s*(fix\s*this|todo|fixme|xxx|code|stuff|do this)\s*$/i.test(line)) {
      fixes.push(`Line ${lineno}: Removed non-descriptive filler comment '${line.trim()}'`);
      continue;
    }

    if (line.includes("\t")) {
      line = line.replace(/\t/g, "    ");
      fixes.push(`Line ${lineno}: Converted indentation tabs to 4 spaces`);
    }

    const trimmed = line.trimEnd();
    if (trimmed !== line) {
      fixes.push(`Line ${lineno}: Trimmed trailing whitespace`);
      line = trimmed;
    }

    if (line.includes(";") && !line.trim().startsWith("#")) {
      const parts = line.split(";").map(p => p.trim()).filter(Boolean);
      if (parts.length > 1) {
        fixes.push(`Line ${lineno}: Split ${parts.length} semicolon statements onto separate lines`);
        parts.forEach(p => transformed.push(p.replace(/([a-zA-Z0-9_)\]])=([a-zA-Z0-9_(\-])/g, "$1 = $2")));
        continue;
      }
    }

    line = line.replace(/([a-zA-Z0-9_)\]])=([a-zA-Z0-9_(\-])/g, "$1 = $2");
    transformed.push(line);
  }

  const finalLines = [];
  for (let i = 0; i < transformed.length; i++) {
    const l = transformed[i];
    const isTopLevel = (l.startsWith("def ") || l.startsWith("class ")) && !l.startsWith("    ");
    if (isTopLevel && finalLines.length > 0) {
      let blanks = 0;
      let idx = finalLines.length - 1;
      while (idx >= 0 && finalLines[idx].trim() === "") {
        blanks++;
        idx--;
      }
      if (idx >= 0 && blanks < 2) {
        for (let b = 0; b < 2 - blanks; b++) {
          finalLines.push("");
        }
        fixes.push(`Line ${i + 1}: Added 2 blank lines before top-level definition`);
      }
    }
    finalLines.push(l);
  }

  let fixedCode = finalLines.join("\n");
  if (fixedCode && !fixedCode.endsWith("\n")) {
    fixedCode += "\n";
    fixes.push("End of file: Ensured standard newline");
  }

  const reportAfter = runClientSideAnalysis(fixedCode, filename);
  return {
    fixed_code: fixedCode,
    fixes_applied: fixes,
    fixes_count: fixes.length,
    score_before: reportBefore.score,
    grade_before: reportBefore.grade,
    score_after: reportAfter.score,
    grade_after: reportAfter.grade,
    report_after: reportAfter
  };
}

// Client-Side Markdown Generator Fallback
function generateClientSideMarkdownReport(reports) {
  if (!reports || !reports.length) return "# Code Quality Report\n\nNo reports available.";
  const total = reports.length;
  const avg = Math.round((reports.reduce((acc, r) => acc + r.score, 0) / total) * 10) / 10;
  const overallGrade = avg >= 90 ? "Best" : avg >= 75 ? "Good" : avg >= 50 ? "Average" : "Poor";

  let md = `# Python Code Quality & Comment Analyzer Report\n\n`;
  md += `- **Files analyzed:** ${total}\n`;
  md += `- **Average quality score:** ${avg}/100\n`;
  md += `- **Overall grade:** ${overallGrade}\n\n`;

  for (const r of reports) {
    md += `## ${r.filename}\n`;
    md += `- **Score:** ${r.score}/100\n`;
    md += `- **Grade:** ${r.grade}\n`;
    md += `- **Comment-to-code ratio:** ${r.comment_ratio}\n`;
    md += `- **Lines of code:** ${r.total_lines || "-"}\n\n`;

    md += `| Severity | Line | Category | Issue |\n`;
    md += `|---|---|---|---|\n`;
    if (r.issues && r.issues.length) {
      for (const i of r.issues) {
        md += `| ${i.severity} | ${i.line !== null && i.line !== undefined ? i.line : "-"} | ${i.category || "General"} | ${i.issue.replace(/\|/g, "\\|")} |\n`;
      }
    } else {
      md += `| - | - | - | No issues detected. Clean code! |\n`;
    }
    md += `\n`;
  }
  return md;
}
