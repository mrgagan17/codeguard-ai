import React, { useState } from 'react';
import { Copy, Check, Download } from 'lucide-react';

interface DiffViewerProps {
  diff: string;
  filename?: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ diff, filename = 'patch.diff' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(diff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([diff], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename.endsWith('.diff') ? filename : `${filename}.patch`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const lines = diff.split('\n');

  return (
    <div className="rounded-lg border border-[#1F1F1F] bg-[#0A0A0A] overflow-hidden font-mono text-xs shadow-xl">
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#141414] border-b border-[#1F1F1F]">
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
          <span className="w-3 h-3 rounded-full bg-yellow-500/80 inline-block"></span>
          <span className="w-3 h-3 rounded-full bg-green-500/80 inline-block"></span>
          <span className="text-[#888888] font-sans text-xs ml-2 font-medium">{filename}</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center px-2.5 py-1 text-[#CCCCCC] hover:text-white bg-[#1F1F1F] hover:bg-[#2A2A2A] rounded transition border border-[#2B2B2B]"
            title="Copy patch to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 mr-1 text-green-400" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
            <span>{copied ? 'Copied' : 'Copy Patch'}</span>
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center px-2.5 py-1 text-[#CCCCCC] hover:text-white bg-[#1F1F1F] hover:bg-[#2A2A2A] rounded transition border border-[#2B2B2B]"
            title="Download patch file"
          >
            <Download className="w-3.5 h-3.5 mr-1" />
            <span>Download</span>
          </button>
        </div>
      </div>

      <div className="p-3 overflow-x-auto max-h-[420px] select-text">
        {lines.map((line, idx) => {
          let lineClass = 'text-slate-300';
          let prefixBg = '';

          if (line.startsWith('+') && !line.startsWith('+++')) {
            lineClass = 'text-emerald-400 bg-emerald-950/40 font-semibold';
            prefixBg = 'text-emerald-500';
          } else if (line.startsWith('-') && !line.startsWith('---')) {
            lineClass = 'text-rose-400 bg-rose-950/40 line-through';
            prefixBg = 'text-rose-500';
          } else if (line.startsWith('@@')) {
            lineClass = 'text-indigo-400 bg-indigo-950/30';
          }

          return (
            <div key={idx} className={`flex px-2 py-0.5 rounded-sm ${lineClass}`}>
              <span className="w-8 select-none text-slate-600 text-right pr-3 font-mono opacity-60">
                {idx + 1}
              </span>
              <span className={`w-4 select-none ${prefixBg}`}>
                {line.startsWith('+') ? '+' : line.startsWith('-') ? '-' : ' '}
              </span>
              <span className="whitespace-pre">
                {line.startsWith('+') || line.startsWith('-') ? line.substring(1) : line}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
