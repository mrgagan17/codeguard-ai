import React from 'react';

interface CodeViewerProps {
  code: string;
  startLine?: number;
  highlightLine?: number;
  filename?: string;
  maxHeight?: string;
}

export const CodeViewer: React.FC<CodeViewerProps> = ({
  code,
  startLine = 1,
  highlightLine,
  filename,
  maxHeight = 'max-h-72',
}) => {
  const lines = code ? code.split('\n') : [];

  return (
    <div className="rounded-lg border border-[#1F1F1F] bg-[#050505] overflow-hidden font-mono text-xs shadow-inner">
      {filename && (
        <div className="px-4 py-1.5 bg-[#141414] border-b border-[#1F1F1F] text-[#888888] font-sans text-xs flex justify-between items-center">
          <span>{filename}</span>
          <span className="text-[#555555] text-[11px] font-mono">Lines {startLine} - {startLine + lines.length - 1}</span>
        </div>
      )}
      <div className={`p-3 overflow-x-auto ${maxHeight}`}>
        {lines.map((line, idx) => {
          const currentLineNum = startLine + idx;
          const isHighlighted = highlightLine !== undefined && currentLineNum === highlightLine;

          return (
            <div
              key={idx}
              className={`flex items-center px-2 py-0.5 rounded transition ${
                isHighlighted ? 'bg-amber-500/20 border-l-2 border-amber-400 font-semibold' : 'hover:bg-[#111111]'
              }`}
            >
              <span className="w-10 select-none text-[#555555] text-right pr-4 font-mono">
                {currentLineNum}
              </span>
              <span className="whitespace-pre text-[#E0E0E0]">{line || ' '}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
