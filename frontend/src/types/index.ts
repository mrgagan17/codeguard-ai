export type Severity = 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational';
export type Category = 'security' | 'quality' | 'style' | 'complexity' | 'secret' | 'bug_risk';
export type FindingStatus = 'open' | 'accepted' | 'fixed' | 'false_positive' | 'resolved';

export interface Finding {
  id: string;
  scan_id: string;
  rule_id: string;
  title: string;
  description: string;
  category: Category;
  severity: Severity;
  confidence: string;
  file_path: string;
  start_line: number;
  end_line: number;
  snippet?: string;
  tool: string;
  why_it_matters?: string;
  recommended_remediation?: string;
  references?: string;
  status: FindingStatus;
  status_justification?: string;
  created_at: string;
}

export interface ToolRun {
  tool_name: string;
  version?: string;
  status: string;
  duration_ms: number;
  findings_count: number;
  error_message?: string;
}

export interface Scan {
  id: string;
  project_id?: string;
  target_name: string;
  trigger_type: string;
  status: string;
  total_files: number;
  total_lines: number;
  total_findings: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  info_count: number;
  duration_ms: number;
  cache_hit_count: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface ScanDetail extends Scan {
  tool_runs: ToolRun[];
  findings: Finding[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  repository_type: string;
  local_path?: string;
  created_at: string;
  updated_at: string;
  scans?: Scan[];
}

export interface DashboardSummary {
  has_data: boolean;
  total_scans: number;
  total_findings: number;
  severity_counts: Record<Severity, number>;
  status_counts: Record<FindingStatus, number>;
  category_distribution: Array<{ category: string; count: number }>;
  recent_scans: Array<{
    id: string;
    target_name: string;
    trigger_type: string;
    status: string;
    total_findings: number;
    critical_count: number;
    high_count: number;
    duration_ms: number;
    created_at: string;
  }>;
  average_duration_ms: number;
  historical_trends: Array<{
    scan_id: string;
    target: string;
    findings: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    date: string;
  }>;
}

export interface AnalyzerStatus {
  name: string;
  display_name: string;
  version: string;
  is_available: boolean;
  enabled: boolean;
  description: string;
}

export interface OllamaStatus {
  available: boolean;
  url: string;
  current_model: string;
  installed_models: string[];
  message: string;
}

export interface FixSuggestion {
  id: string;
  finding_id: string;
  original_code: string;
  suggested_code: string;
  patch_diff: string;
  explanation: string;
  trade_offs?: string;
  suggested_tests?: string;
  is_ai_generated: boolean;
  model_used?: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

