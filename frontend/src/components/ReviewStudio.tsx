import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ScanDetail, Finding, FixSuggestion, User } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { CategoryBadge } from './CategoryBadge';
import { DiffViewer } from './DiffViewer';
import {
  Play,
  Upload,
  FileCode,
  ShieldAlert,
  ShieldCheck,
  Download,
  FileText,
  Copy,
  Check,
  Wrench,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Bot,
  ExternalLink,
  Lock,
  LogIn,
} from 'lucide-react';

interface ReviewStudioProps {
  currentUser?: User | null;
  onRequireAuth?: () => void;
}

export const ReviewStudio: React.FC<ReviewStudioProps> = ({
  currentUser = null,
  onRequireAuth = () => {},
}) => {
  const [inputMode, setInputMode] = useState<'paste' | 'upload'>('paste');
  const [reviewName, setReviewName] = useState('');
  const [code, setCode] = useState('');
  const [pendingCode, setPendingCode] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If user attempted to paste before login, automatically transfer code after login
  useEffect(() => {
    if (currentUser && pendingCode) {
      setCode(pendingCode);
      setPendingCode('');
    }
  }, [currentUser, pendingCode]);

  // Results State
  const [activeScan, setActiveScan] = useState<ScanDetail | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [fixSuggestion, setFixSuggestion] = useState<FixSuggestion | null>(null);
  const [loadingFix, setLoadingFix] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [loadingExplain, setLoadingExplain] = useState(false);

  const calculateHealthGrade = (scan: ScanDetail) => {
    if (scan.critical_count > 0) return { grade: 'F', color: 'text-red-500', bg: 'bg-red-500/10 border-red-500/30', label: 'Critical Risk' };
    if (scan.high_count > 0) return { grade: 'D', color: 'text-orange-500', bg: 'bg-orange-500/10 border-orange-500/30', label: 'High Risk' };
    if (scan.medium_count > 2) return { grade: 'C', color: 'text-amber-500', bg: 'bg-amber-500/10 border-amber-500/30', label: 'Moderate Quality Debt' };
    if (scan.medium_count > 0 || scan.low_count > 2) return { grade: 'B', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/30', label: 'Good' };
    return { grade: 'A', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', label: 'Excellent' };
  };

  const handleRunScan = async () => {
    if (!currentUser) {
      onRequireAuth();
      return;
    }
    setError(null);
    if (inputMode === 'paste') {
      if (!code.trim()) {
        setError('Please paste your source code to begin analysis.');
        return;
      }
      try {
        setLoading(true);
        const scan = await api.createSnippetScan(
          reviewName.trim() || 'Custom Code Review',
          code,
          'python'
        );
        const detail = await api.getScanDetail(scan.id);
        setActiveScan(detail);
        if (detail.findings.length > 0) {
          selectFinding(detail.findings[0]);
        } else {
          setSelectedFinding(null);
          setFixSuggestion(null);
        }
      } catch (err: any) {
        setError(err.message || 'Scan failed.');
      } finally {
        setLoading(false);
      }
    } else {
      if (!uploadFile) {
        setError('Please select a file or ZIP archive to upload.');
        return;
      }
      try {
        setLoading(true);
        const formData = new FormData();
        formData.append('name', reviewName.trim() || uploadFile.name);

        let scan;
        if (uploadFile.name.endsWith('.zip')) {
          formData.append('zip_file', uploadFile);
          scan = await api.uploadZipScan(formData);
        } else {
          formData.append('files', uploadFile);
          scan = await api.uploadFilesScan(formData);
        }
        const detail = await api.getScanDetail(scan.id);
        setActiveScan(detail);
        if (detail.findings.length > 0) {
          selectFinding(detail.findings[0]);
        }
      } catch (err: any) {
        setError(err.message || 'Upload analysis failed.');
      } finally {
        setLoading(false);
      }
    }
  };

  const selectFinding = async (finding: Finding) => {
    setSelectedFinding(finding);
    setFixSuggestion(null);
    setExplanation(null);
    try {
      setLoadingFix(true);
      const fix = await api.suggestFix(finding.id);
      setFixSuggestion(fix);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingFix(false);
    }
  };

  const handleExplain = async () => {
    if (!selectedFinding) return;
    try {
      setLoadingExplain(true);
      const res = await api.explainFinding(selectedFinding.id);
      setExplanation(res.explanation);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingExplain(false);
    }
  };

  const handleReset = () => {
    setActiveScan(null);
    setSelectedFinding(null);
    setFixSuggestion(null);
    setExplanation(null);
    setError(null);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* 1. Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1C1C1C] gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>Code Review Studio</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Air-Gapped &bull; 100% Private
            </span>
          </h1>
          <p className="text-xs text-[#888888] mt-1">
            Analyze your personal Python code, repositories, or scripts against Ruff, Bandit, Radon, AST rules, and secret detectors.
          </p>
        </div>

        {activeScan && (
          <button
            onClick={handleReset}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-[#141414] hover:bg-[#202020] text-[#A0A0A0] hover:text-white border border-[#222222] transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Scan</span>
          </button>
        )}
      </div>

      {error && (
        <div className="p-3.5 bg-red-950/20 border border-red-800/40 rounded-xl flex items-center space-x-3 text-red-400 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 2. Input Workspace (Hidden when scan results are displayed to keep interface focused) */}
      {!activeScan && (
        <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-6 space-y-5 shadow-2xl">
          {/* Mode Tabs */}
          <div className="flex items-center justify-between border-b border-[#1A1A1A] pb-3">
            <div className="flex space-x-2">
              <button
                onClick={() => setInputMode('paste')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                  inputMode === 'paste'
                    ? 'bg-[#1C1C1C] text-white border border-[#333333]'
                    : 'text-[#888888] hover:text-white hover:bg-[#121212]'
                }`}
              >
                <FileCode className="w-3.5 h-3.5" />
                <span>Paste Code</span>
              </button>

              <button
                onClick={() => setInputMode('upload')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                  inputMode === 'upload'
                    ? 'bg-[#1C1C1C] text-white border border-[#333333]'
                    : 'text-[#888888] hover:text-white hover:bg-[#121212]'
                }`}
              >
                <Upload className="w-3.5 h-3.5" />
                <span>Upload File or ZIP</span>
              </button>
            </div>

            <span className="text-[11px] text-[#666666] font-mono">
              {inputMode === 'paste' ? `${code.split('\n').length} lines | ${code.length} chars` : ''}
            </span>
          </div>

          {/* Optional Title */}
          <div>
            <input
              type="text"
              placeholder="Audit Label (e.g., Auth Service Refactor, PR #12) — Optional"
              value={reviewName}
              onChange={(e) => setReviewName(e.target.value)}
              className="w-full bg-[#050505] border border-[#222222] rounded-lg px-3.5 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
            />
          </div>

          {/* Code Textarea or File Upload */}
          {inputMode === 'paste' ? (
            <div className="relative group">
              <textarea
                rows={16}
                value={code}
                onChange={(e) => {
                  if (!currentUser) {
                    onRequireAuth();
                    return;
                  }
                  setCode(e.target.value);
                }}
                onPaste={(e) => {
                  if (!currentUser) {
                    e.preventDefault();
                    const text = e.clipboardData.getData('text');
                    if (text) {
                      setPendingCode(text);
                    }
                    onRequireAuth();
                  }
                }}
                onKeyDown={(e) => {
                  if (!currentUser) {
                    e.preventDefault();
                    onRequireAuth();
                  }
                }}
                onClick={() => {
                  if (!currentUser) onRequireAuth();
                }}
                placeholder={
                  currentUser
                    ? "Paste your custom Python code here..."
                    : "Please sign in or create an account to paste and review code..."
                }
                readOnly={!currentUser}
                className={`w-full bg-[#030303] border ${
                  !currentUser
                    ? 'border-[#222222] cursor-pointer'
                    : 'border-[#1F1F1F] focus:border-[#444444]'
                } rounded-xl p-4 font-mono text-xs text-[#E0E0E0] placeholder-[#555555] focus:outline-none leading-relaxed resize-y select-text shadow-inner transition`}
              ></textarea>

              {!currentUser && (
                <div
                  onClick={() => onRequireAuth()}
                  className="absolute inset-0 bg-[#000000]/80 backdrop-blur-[2px] rounded-xl flex flex-col items-center justify-center p-6 text-center cursor-pointer transition hover:bg-[#000000]/75 border border-[#222222]/80 group-hover:border-[#333333]"
                >
                  <div className="w-11 h-11 rounded-2xl bg-[#111111] border border-[#282828] flex items-center justify-center mb-3 shadow-md">
                    <Lock className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-sm font-bold text-white mb-1 tracking-tight">
                    Sign In to Paste & Review Code
                  </h3>
                  <p className="text-xs text-[#888888] max-w-sm mb-4 leading-relaxed">
                    Authentication is required to paste Python code, run deep static security analysis, and save your private audit history.
                  </p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRequireAuth();
                    }}
                    className="flex items-center space-x-2 px-5 py-2.5 bg-white hover:bg-[#EDEDED] text-black rounded-xl text-xs font-bold transition shadow-lg active:scale-95 cursor-pointer"
                  >
                    <LogIn className="w-3.5 h-3.5 fill-black" />
                    <span>Sign In / Create Account</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div
              onClick={() => {
                if (!currentUser) onRequireAuth();
              }}
              className="relative border border-dashed border-[#262626] hover:border-[#444444] rounded-xl p-10 text-center space-y-3 bg-[#030303] transition"
            >
              <Upload className="w-10 h-10 text-[#666666] mx-auto" />
              <div>
                <p className="text-sm font-semibold text-white">Select a Python File (.py) or Repository Archive (.zip)</p>
                <p className="text-xs text-[#666666] mt-0.5">Tested safely in a sandboxed temporary environment without code execution.</p>
              </div>
              <input
                type="file"
                accept=".py,.pyw,.zip"
                disabled={!currentUser}
                onChange={(e) => {
                  if (!currentUser) {
                    onRequireAuth();
                    return;
                  }
                  if (e.target.files && e.target.files[0]) setUploadFile(e.target.files[0]);
                }}
                className="block mx-auto text-xs text-[#888888] file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-[#1F1F1F] file:text-white hover:file:bg-[#2E2E2E] cursor-pointer disabled:opacity-40"
              />
              {uploadFile && (
                <div className="text-xs text-emerald-400 font-mono mt-2">
                  Selected: {uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)
                </div>
              )}

              {!currentUser && (
                <div
                  onClick={() => onRequireAuth()}
                  className="absolute inset-0 bg-[#000000]/80 backdrop-blur-[2px] rounded-xl flex flex-col items-center justify-center p-6 text-center cursor-pointer transition hover:bg-[#000000]/75"
                >
                  <div className="w-11 h-11 rounded-2xl bg-[#111111] border border-[#282828] flex items-center justify-center mb-3 shadow-md">
                    <Lock className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-sm font-bold text-white mb-1">Sign In to Upload Files</h3>
                  <p className="text-xs text-[#888888] max-w-sm mb-4">
                    Please sign in or create an account to upload Python files or ZIP archives for analysis.
                  </p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRequireAuth();
                    }}
                    className="flex items-center space-x-2 px-5 py-2.5 bg-white hover:bg-[#EDEDED] text-black rounded-xl text-xs font-bold transition shadow-lg active:scale-95 cursor-pointer"
                  >
                    <LogIn className="w-3.5 h-3.5 fill-black" />
                    <span>Sign In / Create Account</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Action Row */}
          <div className="flex items-center justify-between pt-2">
            <span className="text-xs text-[#555555]">
              Instant local static analysis &bull; Zero external data transfer
            </span>

            <button
              onClick={handleRunScan}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2.5 bg-white hover:bg-[#E5E5E5] text-black disabled:opacity-40 rounded-xl text-xs font-bold transition shadow-lg active:scale-95 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              <span>{loading ? 'Analyzing Code...' : 'Run Security & Quality Review'}</span>
            </button>
          </div>
        </div>
      )}

      {/* 3. Real-World Live Scan Results Dashboard */}
      {activeScan && (
        <div className="space-y-6">
          {/* Executive Score & Metric Banner */}
          {(() => {
            const health = calculateHealthGrade(activeScan);
            return (
              <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-6 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-center space-x-5">
                  <div className={`w-14 h-14 rounded-2xl border flex flex-col items-center justify-center font-bold ${health.bg}`}>
                    <span className={`text-2xl leading-none ${health.color}`}>{health.grade}</span>
                    <span className="text-[9px] uppercase tracking-wider text-[#888888]">Score</span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-lg font-bold text-white">{activeScan.target_name}</h2>
                      <span className={`text-xs font-semibold ${health.color}`}>({health.label})</span>
                    </div>
                    <p className="text-xs text-[#777777] font-mono mt-1">
                      {activeScan.total_files} file(s) &bull; {activeScan.total_lines} lines of code &bull; Completed in {activeScan.duration_ms} ms
                    </p>
                  </div>
                </div>

                {/* Severity Breakdown Pills */}
                <div className="flex items-center space-x-2">
                  <div className="px-3 py-1.5 rounded-lg bg-[#111111] border border-[#1F1F1F] text-center">
                    <span className="text-[10px] text-red-400 font-semibold uppercase block">Critical</span>
                    <span className="text-sm font-bold text-red-400">{activeScan.critical_count}</span>
                  </div>
                  <div className="px-3 py-1.5 rounded-lg bg-[#111111] border border-[#1F1F1F] text-center">
                    <span className="text-[10px] text-orange-400 font-semibold uppercase block">High</span>
                    <span className="text-sm font-bold text-orange-400">{activeScan.high_count}</span>
                  </div>
                  <div className="px-3 py-1.5 rounded-lg bg-[#111111] border border-[#1F1F1F] text-center">
                    <span className="text-[10px] text-amber-400 font-semibold uppercase block">Medium</span>
                    <span className="text-sm font-bold text-amber-400">{activeScan.medium_count}</span>
                  </div>
                  <div className="px-3 py-1.5 rounded-lg bg-[#111111] border border-[#1F1F1F] text-center">
                    <span className="text-[10px] text-blue-400 font-semibold uppercase block">Low</span>
                    <span className="text-sm font-bold text-blue-400">{activeScan.low_count}</span>
                  </div>

                  <a
                    href={api.getReportDownloadUrl(activeScan.id, 'pdf')}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center space-x-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition ml-2 shadow-sm cursor-pointer"
                    title="Open print dialog and save formatted report as PDF"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>Save as PDF</span>
                  </a>

                  <a
                    href={api.getReportDownloadUrl(activeScan.id, 'html')}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center space-x-1.5 px-3 py-2 bg-[#1C1C1C] hover:bg-[#282828] text-white border border-[#333333] rounded-lg text-xs font-semibold transition cursor-pointer"
                    title="Download standalone offline HTML file"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>HTML</span>
                  </a>
                </div>
              </div>
            );
          })()}

          {/* Main Inspection Split Screen */}
          {activeScan.findings.length === 0 ? (
            <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-12 text-center text-[#888888] space-y-3">
              <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto" />
              <h3 className="text-base font-bold text-white">No Vulnerabilities or Flaws Detected</h3>
              <p className="text-xs text-[#666666] max-w-md mx-auto">
                Your code passed all AST checks, Ruff lint rules, Bandit security assertions, secret detectors, and Radon complexity metrics.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              {/* Left Column: Finding List (5 Cols) */}
              <div className="lg:col-span-5 bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-4 space-y-3">
                <span className="text-xs font-bold text-[#888888] uppercase tracking-wider block px-1">
                  Detected Findings ({activeScan.findings.length})
                </span>

                <div className="space-y-2 max-h-[620px] overflow-y-auto pr-1">
                  {activeScan.findings.map((f) => {
                    const isSelected = selectedFinding?.id === f.id;
                    return (
                      <div
                        key={f.id}
                        onClick={() => selectFinding(f)}
                        className={`p-3.5 rounded-xl border cursor-pointer transition ${
                          isSelected
                            ? 'bg-[#141414] border-white/40 shadow-lg'
                            : 'bg-[#050505] border-[#1C1C1C] hover:bg-[#0F0F0F]'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <SeverityBadge severity={f.severity} />
                          <span className="text-[10px] text-[#666666] font-mono">
                            Line {f.start_line} &bull; {f.tool.toUpperCase()}
                          </span>
                        </div>
                        <h4 className="text-xs font-bold text-white line-clamp-1">{f.title}</h4>
                        <p className="text-[11px] text-[#777777] font-mono mt-0.5 truncate">{f.file_path}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right Column: Code Context & Instant Fix Patch (7 Cols) */}
              <div className="lg:col-span-7 space-y-5">
                {selectedFinding && (
                  <>
                    {/* Finding Detail Card */}
                    <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <SeverityBadge severity={selectedFinding.severity} />
                          <CategoryBadge category={selectedFinding.category} />
                          <span className="text-xs font-mono text-[#666666]">[{selectedFinding.rule_id}]</span>
                        </div>

                        <button
                          onClick={handleExplain}
                          disabled={loadingExplain}
                          className="flex items-center space-x-1.5 px-2.5 py-1 bg-[#141414] hover:bg-[#1E1E1E] text-white border border-[#262626] rounded-md text-[11px] font-semibold transition"
                        >
                          <Bot className="w-3.5 h-3.5 text-blue-400" />
                          <span>{loadingExplain ? 'Explaining...' : 'Explain Root Cause'}</span>
                        </button>
                      </div>

                      <h3 className="text-sm font-bold text-white">{selectedFinding.title}</h3>
                      <p className="text-xs text-[#999999] leading-relaxed bg-[#050505] p-3 rounded-lg border border-[#181818]">
                        {selectedFinding.description}
                      </p>

                      {explanation && (
                        <div className="p-3.5 bg-blue-950/20 border border-blue-900/40 rounded-lg text-xs text-[#D1D5DB] leading-relaxed whitespace-pre-line animate-fadeIn">
                          <strong className="text-blue-400 block mb-1">Root Cause & Remediation Explanation:</strong>
                          {explanation}
                        </div>
                      )}
                    </div>

                    {/* Flagged Code Evidence */}
                    {selectedFinding.snippet && (
                      <div className="space-y-1.5">
                        <span className="text-xs font-semibold text-[#888888] uppercase tracking-wider block">
                          Flagged Code Evidence (Line {selectedFinding.start_line})
                        </span>
                        <div className="bg-[#030303] border border-[#1F1F1F] rounded-xl p-3.5 font-mono text-xs text-[#E0E0E0] overflow-x-auto">
                          <pre className="text-amber-300 font-semibold">{selectedFinding.snippet}</pre>
                        </div>
                      </div>
                    )}

                    {/* Unified Diff Patch */}
                    <div className="space-y-2">
                      <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <Wrench className="w-3.5 h-3.5" />
                        <span>Proposed Remediation Patch</span>
                      </span>

                      {loadingFix ? (
                        <div className="p-8 bg-[#0A0A0A] border border-[#1A1A1A] rounded-xl text-center text-xs text-[#777777]">
                          Generating clean unified diff patch...
                        </div>
                      ) : fixSuggestion ? (
                        <DiffViewer
                          diff={fixSuggestion.patch_diff}
                          filename={selectedFinding.file_path}
                        />
                      ) : (
                        <div className="p-4 bg-[#0A0A0A] border border-[#1A1A1A] rounded-xl text-xs text-[#777777]">
                          Follow the remediation recommendation above to address this finding.
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
