import React from 'react';
import {
  ShieldCheck,
  Cpu,
  Lock,
  Zap,
  Code2,
  FileCheck2,
  Sparkles,
  Server,
  Layers,
  Terminal,
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="text-center space-y-3 pb-6 border-b border-[#1A1A1A]">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-mono text-[#AAAAAA] mb-2">
          <ShieldCheck className="w-3.5 h-3.5 text-white" />
          <span>Next-Generation Static Code Security</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          About CodeGuard AI
        </h1>
        <p className="text-sm text-[#888888] max-w-2xl mx-auto leading-relaxed">
          An enterprise-grade, air-gapped static code review and automated remediation platform.
          Engineered to inspect personal scripts, full repositories, and pull requests without transmitting proprietary code to third-party clouds.
        </p>
      </div>

      {/* Core Mission Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-[#0A0A0A] border border-[#1A1A1A] p-6 rounded-2xl space-y-3 hover:border-[#2A2A2A] transition">
          <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">100% Air-Gapped & Private</h3>
          <p className="text-xs text-[#888888] leading-relaxed">
            Your source code never leaves your infrastructure. Zero external API calls, zero telemetry, and zero third-party cloud leakage.
          </p>
        </div>

        <div className="bg-[#0A0A0A] border border-[#1A1A1A] p-6 rounded-2xl space-y-3 hover:border-[#2A2A2A] transition">
          <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">Multi-Analyzer Engine</h3>
          <p className="text-xs text-[#888888] leading-relaxed">
            Harnesses Custom Python AST rules, Ruff linter, Bandit security scanner, Semgrep rule suites, and Radon maintainability metrics concurrently.
          </p>
        </div>

        <div className="bg-[#0A0A0A] border border-[#1A1A1A] p-6 rounded-2xl space-y-3 hover:border-[#2A2A2A] transition">
          <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white">
            <Sparkles className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">Instant AI Remediation</h3>
          <p className="text-xs text-[#888888] leading-relaxed">
            Generates copy-pasteable unified diff patches and plain-English root-cause explanations backed by local Ollama AI or deterministic rules.
          </p>
        </div>
      </div>

      {/* 6-Analyzer Architecture Deep Dive */}
      <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl p-6 sm:p-8 space-y-6">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Layers className="w-4 h-4 text-white" />
            <span>Integrated Analysis Engines</span>
          </h2>
          <p className="text-xs text-[#777777] mt-1">
            Every audit triggers an orchestrator pipeline executing 6 specialized engines in sandboxed parallel subprocesses:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[#050505] border border-[#1E1E1E] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <Code2 className="w-3.5 h-3.5 text-blue-400" />
                <span>Custom Python AST Engine</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">Active</span>
            </div>
            <p className="text-[11px] text-[#888888] leading-relaxed">
              Direct abstract syntax tree verification for syntax errors, mutable defaults, swallowed exceptions, dangerous dynamic code evaluation (`eval`/`exec`), and trailing semicolons.
            </p>
          </div>

          <div className="bg-[#050505] border border-[#1E1E1E] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <Lock className="w-3.5 h-3.5 text-red-400" />
                <span>Secret & Credential Scanner</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">Active</span>
            </div>
            <p className="text-[11px] text-[#888888] leading-relaxed">
              Detects leaked AWS Access Keys, GitHub PATs, private SSH keys, and database passwords with automatic safe redaction masking.
            </p>
          </div>

          <div className="bg-[#050505] border border-[#1E1E1E] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>Ruff Fast Linter</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">Active</span>
            </div>
            <p className="text-[11px] text-[#888888] leading-relaxed">
              Rust-powered linter scanning for syntax mistakes, undefined variables, unused imports, style violations, and formatting irregularities at microsecond latency.
            </p>
          </div>

          <div className="bg-[#050505] border border-[#1E1E1E] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Bandit Security Scanner</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active</span>
            </div>
            <p className="text-[11px] text-[#888888] leading-relaxed">
              Audits common Python security vulnerabilities including unsafe subprocess executions, SQL injections, insecure cryptographic algorithms, and weak random number generation.
            </p>
          </div>

          <div className="bg-[#050505] border border-[#1E1E1E] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <Server className="w-3.5 h-3.5 text-purple-400" />
                <span>Radon Complexity & Maintainability</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">Active</span>
            </div>
            <p className="text-[11px] text-[#888888] leading-relaxed">
              Calculates Cyclomatic Complexity (CC) and Maintainability Index (MI) scores to identify cognitive overload and technical debt in codebases.
            </p>
          </div>

          <div className="bg-[#050505] border border-[#1E1E1E] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                <span>Semgrep Engine</span>
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Active</span>
            </div>
            <p className="text-[11px] text-[#888888] leading-relaxed">
              Pattern-matching static analysis identifying anti-patterns, OWASP Top 10 vulnerabilities, and security flaws across complex multi-file projects.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
