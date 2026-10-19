import {
  Scan,
  ScanDetail,
  Finding,
  DashboardSummary,
  AnalyzerStatus,
  OllamaStatus,
  FixSuggestion,
  Project,
  FindingStatus,
  User,
  AuthResponse,
} from '../types';

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (typeof window !== 'undefined' && window.location.port === '5173'
    ? 'http://127.0.0.1:8000/api'
    : '/api');

const TOKEN_KEY = 'codeguard_token';

export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
};

const getHeaders = (customHeaders: Record<string, string> = {}): Record<string, string> => {
  const token = getToken();
  const headers: Record<string, string> = { ...customHeaders };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Authentication
  async register(data: { email: string; username: string; password: string; full_name?: string }): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Registration failed.');
    }
    const authData: AuthResponse = await res.json();
    setToken(authData.access_token);
    return authData;
  },

  async login(data: { username_or_email: string; password: string }): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid username/email or password.');
    }
    const authData: AuthResponse = await res.json();
    setToken(authData.access_token);
    return authData;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  logout() {
    removeToken();
  },

  // Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  // Dashboard
  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/dashboard/summary`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  // Analyzers
  async getAnalyzers(): Promise<{ analyzers: AnalyzerStatus[] }> {
    const res = await fetch(`${API_BASE}/analyzers`);
    if (!res.ok) throw new Error('Failed to fetch analyzers');
    return res.json();
  },

  // Scans
  async getScans(skip = 0, limit = 50): Promise<Scan[]> {
    const res = await fetch(`${API_BASE}/scans?skip=${skip}&limit=${limit}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch scans');
    return res.json();
  },

  async getScanDetail(scanId: string): Promise<ScanDetail> {
    const res = await fetch(`${API_BASE}/scans/${scanId}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch scan detail');
    return res.json();
  },

  async clearScanHistory(): Promise<{ message: string; deleted_count: number }> {
    const res = await fetch(`${API_BASE}/scans/history`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to clear scan history');
    }
    return res.json();
  },

  async deleteScan(scanId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/scans/${scanId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to delete scan');
    }
  },

  async createSnippetScan(name: string, code: string, language = 'python'): Promise<Scan> {
    const res = await fetch(`${API_BASE}/scans`, {
      method: 'POST',
      headers: getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ name, code, language }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Scan failed');
    }
    return res.json();
  },

  async uploadFilesScan(formData: FormData): Promise<Scan> {
    const headers: Record<string, string> = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/scans/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'File upload scan failed');
    }
    return res.json();
  },

  async uploadZipScan(formData: FormData): Promise<Scan> {
    const headers: Record<string, string> = {};
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/scans/upload-zip`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ZIP archive scan failed');
    }
    return res.json();
  },



  async scanGitRepo(repoPath: string, baseRef?: string, name?: string): Promise<Scan> {
    const params = new URLSearchParams();
    params.append('repo_path', repoPath);
    if (baseRef) params.append('base_ref', baseRef);
    if (name) params.append('name', name);

    const res = await fetch(`${API_BASE}/scans/git`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Git repository scan failed');
    }
    return res.json();
  },

  // Findings
  async getScanFindings(scanId: string, filters: Record<string, string> = {}): Promise<{
    scan_id: string;
    total: number;
    findings: Finding[];
  }> {
    const query = new URLSearchParams(filters).toString();
    const res = await fetch(`${API_BASE}/scans/${scanId}/findings?${query}`);
    if (!res.ok) throw new Error('Failed to fetch findings');
    return res.json();
  },

  async updateFindingStatus(findingId: string, status: FindingStatus, justification?: string): Promise<Finding> {
    const res = await fetch(`${API_BASE}/findings/${findingId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, justification }),
    });
    if (!res.ok) throw new Error('Failed to update finding status');
    return res.json();
  },

  async explainFinding(findingId: string, customModel?: string) {
    const url = new URL(`${API_BASE}/findings/${findingId}/explain`);
    if (customModel) url.searchParams.append('custom_model', customModel);
    const res = await fetch(url.toString(), { method: 'POST' });
    if (!res.ok) throw new Error('Failed to explain finding');
    return res.json();
  },

  async suggestFix(findingId: string, customModel?: string): Promise<FixSuggestion> {
    const url = new URL(`${API_BASE}/findings/${findingId}/suggest-fix`);
    if (customModel) url.searchParams.append('custom_model', customModel);
    const res = await fetch(url.toString(), { method: 'POST' });
    if (!res.ok) throw new Error('Failed to generate fix suggestion');
    return res.json();
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`);
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
  },

  async createProject(data: Partial<Project>): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create project');
    return res.json();
  },

  async deleteProject(id: string) {
    const res = await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete project');
    return res.json();
  },

  // AI & Settings
  async getOllamaStatus(): Promise<OllamaStatus> {
    const res = await fetch(`${API_BASE}/ai/ollama-status`);
    if (!res.ok) throw new Error('Failed to check Ollama status');
    return res.json();
  },

  async getSettings(): Promise<{ settings: Record<string, string> }> {
    const res = await fetch(`${API_BASE}/settings`);
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  },

  async updateSettings(settings: Record<string, string>) {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings }),
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  getReportDownloadUrl(scanId: string, format: string) {
    return `${API_BASE}/scans/${scanId}/report?format=${format}`;
  },
};
