import React from 'react';
import { ShieldCheck, Lock, EyeOff, ServerOff, Trash2, CheckCircle2 } from 'lucide-react';

export const PrivacyPolicyPage: React.FC = () => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-4xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="text-center space-y-3 pb-6 border-b border-[#1A1A1A]">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-xs font-mono text-emerald-400 mb-2">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Air-Gapped Privacy Architecture</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Privacy Policy
        </h1>
        <p className="text-xs text-[#777777] font-mono">
          Effective Date: October 2026 &bull; CodeGuard AI v1.0
        </p>
      </div>

      {/* Highlights Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0A0A0A] border border-[#1C1C1C] p-5 rounded-2xl space-y-2">
          <ServerOff className="w-5 h-5 text-emerald-400" />
          <h3 className="text-xs font-bold text-white">0% Cloud Transmission</h3>
          <p className="text-[11px] text-[#777777] leading-relaxed">
            Your Python code is analyzed strictly on your local host server. No telemetry or external API calls are made.
          </p>
        </div>
        <div className="bg-[#0A0A0A] border border-[#1C1C1C] p-5 rounded-2xl space-y-2">
          <EyeOff className="w-5 h-5 text-emerald-400" />
          <h3 className="text-xs font-bold text-white">Automatic Redaction</h3>
          <p className="text-[11px] text-[#777777] leading-relaxed">
            API keys, tokens, and database passwords in source code snippets are masked before logging or report generation.
          </p>
        </div>
        <div className="bg-[#0A0A0A] border border-[#1C1C1C] p-5 rounded-2xl space-y-2">
          <Trash2 className="w-5 h-5 text-emerald-400" />
          <h3 className="text-xs font-bold text-white">User Deletion Rights</h3>
          <p className="text-[11px] text-[#777777] leading-relaxed">
            You retain full ownership of all data. You can permanently wipe your entire scan history at any time.
          </p>
        </div>
      </div>

      {/* Detailed Policy Clauses */}
      <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-6 sm:p-8 space-y-8 text-xs text-[#A0A0A0] leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <span className="text-white font-mono">1.</span>
            <span>Zero Third-Party Cloud Transmission</span>
          </h2>
          <p>
            CodeGuard AI was built intentionally for privacy-sensitive engineering organizations and individual developers who cannot risk leaking proprietary code. We do not use third-party cloud LLM APIs (such as OpenAI, Anthropic, or Google Cloud) to inspect your code. When AI explanations are requested, they are routed through your local, offline Ollama instance or served via deterministic, hardcoded security rules.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <span className="text-white font-mono">2.</span>
            <span>Safe Static Analysis & Zero Code Execution</span>
          </h2>
          <p>
            When you paste code or upload Python files or ZIP archives, the platform treats all source files strictly as passive text and AST (Abstract Syntax Tree) structures. Uploaded files are placed in sandboxed temporary folders with zip-slip validation, inspected by local static CLI binaries (Ruff, Bandit, Radon, Semgrep), and deleted immediately after analysis. Your files are never executed, imported, or executed as scripts.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <span className="text-white font-mono">3.</span>
            <span>Account Security & User Data Isolation</span>
          </h2>
          <p>
            All user passwords are encrypted using industry-standard PBKDF2-HMAC-SHA256 password hashing with unique salt. Session authentication uses cryptographically signed JWT tokens. Scan results and historical audits are strictly tied to your authenticated user ID; no user can view, edit, or delete another user&apos;s code reviews or reports.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <span className="text-white font-mono">4.</span>
            <span>Data Retention & Right to Erasure</span>
          </h2>
          <p>
            We adhere strictly to the principle of data minimization. You have continuous, permanent control over your stored records:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-[#888888]">
            <li>You can delete individual scans directly from the Audit History table.</li>
            <li>You can click &quot;Clear History&quot; to permanently and irreversibly wipe all scans, findings, and metrics from the database.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <span className="text-white font-mono">5.</span>
            <span>Cookies and Local Storage</span>
          </h2>
          <p>
            CodeGuard AI uses browser `localStorage` solely to store your authentication session token (`codeguard_token`) and user profile cache (`codeguard_user`). We do not use marketing cookies, tracking pixels, or third-party analytics trackers.
          </p>
        </section>

        <div className="pt-4 border-t border-[#1C1C1C] flex items-center justify-between text-[11px] text-[#666666]">
          <span>Security & Compliance: Air-Gapped Standard</span>
          <span>Contact: gagansecurity@gmail.com</span>
        </div>
      </div>
    </div>
  );
};
