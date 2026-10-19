import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Scan } from '../types';
import {
  History,
  FileCode,
  Clock,
  Search,
  ExternalLink,
  Trash2,
  AlertTriangle,
} from 'lucide-react';

interface ScanHistoryPageProps {
  onNavigate: () => void;
}

export const ScanHistoryPage: React.FC<ScanHistoryPageProps> = ({ onNavigate }) => {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadScans();
  }, []);

  const loadScans = async () => {
    try {
      setLoading(true);
      const data = await api.getScans(0, 50);
      setScans(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const executeClearHistory = async () => {
    try {
      setClearing(true);
      await api.clearScanHistory();
      setScans([]);
      setShowClearConfirm(false);
    } catch (err: any) {
      alert(err.message || 'Failed to clear history');
    } finally {
      setClearing(false);
    }
  };

  const handleDeleteScan = async (scanId: string) => {
    try {
      await api.deleteScan(scanId);
      setScans((prev) => prev.filter((s) => s.id !== scanId));
    } catch (err: any) {
      alert(err.message || 'Failed to delete scan');
    }
  };

  const filteredScans = scans.filter((s) =>
    s.target_name.toLowerCase().includes(search.toLowerCase()) ||
    s.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1C1C1C] gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Audit History</h2>
          <p className="text-xs text-[#888888] mt-1">
            Private audit log of your personal code reviews and security scans.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative w-full md:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-[#555555]" />
            <input
              type="text"
              placeholder="Search scans..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#0A0A0A] border border-[#222222] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
            />
          </div>

          {showClearConfirm ? (
            <div className="flex items-center space-x-2 bg-[#1A0A0A] border border-red-800/60 px-3 py-1.5 rounded-lg animate-fadeIn shrink-0">
              <span className="text-[11px] text-red-300 font-semibold flex items-center space-x-1">
                <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                <span>Delete all from DB?</span>
              </span>
              <button
                onClick={executeClearHistory}
                disabled={clearing}
                className="px-2.5 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-[11px] font-bold transition cursor-pointer shadow-sm disabled:opacity-40"
              >
                {clearing ? 'Deleting...' : 'Yes, Delete All'}
              </button>
              <button
                onClick={() => setShowClearConfirm(false)}
                className="px-2 py-1 bg-[#1E1E1E] hover:bg-[#2A2A2A] text-[#888888] hover:text-white rounded text-[11px] font-medium transition cursor-pointer"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowClearConfirm(true)}
              disabled={clearing || scans.length === 0}
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-red-950/20 hover:bg-red-900/30 text-red-400 border border-red-800/40 rounded-lg text-xs font-semibold transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
              title="Permanently delete all audit history from database"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          )}
        </div>
      </div>

      <div className="bg-[#0A0A0A] border border-[#1A1A1A] rounded-2xl overflow-hidden shadow-2xl">
        {loading ? (
          <div className="p-12 text-center text-xs text-[#777777]">Loading audit history...</div>
        ) : filteredScans.length === 0 ? (
          <div className="p-12 text-center text-[#777777] space-y-2">
            <History className="w-10 h-10 text-[#444444] mx-auto" />
            <p className="text-sm font-semibold text-white">No Historical Reviews Found</p>
            <p className="text-xs text-[#666666]">Run an audit in Review Studio to see it listed here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#CCCCCC]">
              <thead className="bg-[#050505] text-[#888888] uppercase text-[10px] font-semibold tracking-wider border-b border-[#1A1A1A]">
                <tr>
                  <th className="py-3 px-4">Audit Target</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Files / LOC</th>
                  <th className="py-3 px-4">Total Issues</th>
                  <th className="py-3 px-4">Critical / High</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4 text-right">Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#141414]">
                {filteredScans.map((s) => (
                  <tr key={s.id} className="hover:bg-[#0F0F0F] transition">
                    <td className="py-3.5 px-4 font-semibold text-white flex items-center space-x-2">
                      <FileCode className="w-4 h-4 text-blue-400 shrink-0" />
                      <span className="truncate max-w-xs">{s.target_name}</span>
                    </td>
                    <td className="py-3.5 px-4 capitalize text-[#888888]">
                      {s.trigger_type.replace('_', ' ')}
                    </td>
                    <td className="py-3.5 px-4 text-[#777777] font-mono text-[11px]">
                      {new Date(s.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-[#888888]">
                      {s.total_files} <span className="text-[#555555]">({s.total_lines} lines)</span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-white">
                      {s.total_findings}
                    </td>
                    <td className="py-3.5 px-4 font-semibold">
                      <span className="text-red-400">{s.critical_count}</span>
                      <span className="text-[#555555] mx-1">/</span>
                      <span className="text-orange-400">{s.high_count}</span>
                    </td>
                    <td className="py-3.5 px-4 text-[#777777] font-mono">
                      {s.duration_ms} ms
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <a
                          href={api.getReportDownloadUrl(s.id, 'pdf')}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center space-x-1 px-2.5 py-1 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 rounded text-[11px] font-medium transition"
                          title="Save Audit Report as PDF"
                        >
                          <span>PDF</span>
                          <ExternalLink className="w-3 h-3 text-blue-400" />
                        </a>
                        <a
                          href={api.getReportDownloadUrl(s.id, 'html')}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center space-x-1 px-2.5 py-1 bg-[#141414] hover:bg-[#202020] text-white border border-[#222222] rounded text-[11px] font-medium transition"
                          title="Open HTML Audit Report"
                        >
                          <span>HTML</span>
                          <ExternalLink className="w-3 h-3 text-[#777777]" />
                        </a>
                        <button
                          onClick={() => handleDeleteScan(s.id)}
                          className="p-1 text-[#555555] hover:text-red-400 hover:bg-red-950/20 rounded transition cursor-pointer"
                          title="Delete this audit from database"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
