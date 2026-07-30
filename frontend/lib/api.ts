const API_BASE = "http://127.0.0.1:8000/api";
const SESSION_TOKEN = "aigate-secret-session-token-2026-v1";

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const headers = {
    "X-Session-Token": SESSION_TOKEN,
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Errore sconosciuto" }));
    throw new Error(errorData.detail || `Errore HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  getHealth: () => fetchApi("/health"),
  getAudit: () => fetchApi("/audit"),
  
  // Privacy Center
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/documents`, {
      method: "POST",
      headers: { "X-Session-Token": SESSION_TOKEN },
      body: formData,
    });
    return res.json();
  },
  scanDocument: (id: string) => fetchApi(`/documents/${id}/scan`, { method: "POST" }),
  protectDocument: (id: string, payload: any) =>
    fetchApi(`/documents/${id}/protect`, { method: "POST", body: JSON.stringify(payload) }),
  getVersionDiff: (id: string) => fetchApi(`/versions/${id}/diff`),

  // Providers & Gate
  getProviders: () => fetchApi("/providers"),
  updateProvider: (id: string, privacyClass: string) =>
    fetchApi(`/providers/${id}`, { method: "PATCH", body: JSON.stringify({ privacy_class: privacyClass }) }),
  preflightCheck: (payload: any) =>
    fetchApi("/gate/preflight", { method: "POST", body: JSON.stringify(payload) }),
  chat: (payload: any) =>
    fetchApi("/chat", { method: "POST", body: JSON.stringify(payload) }),

  // Projects & Compliance
  createProject: (payload: any) => fetchApi("/projects", { method: "POST", body: JSON.stringify(payload) }),
  getProject: (id: string) => fetchApi(`/projects/${id}`),
  wizardNext: (id: string, answer?: any) =>
    fetchApi(`/projects/${id}/wizard/next`, { method: "POST", body: JSON.stringify({ answer }) }),
  assessProject: (id: string, deployDate?: string) =>
    fetchApi(`/projects/${id}/assess`, { method: "POST", body: JSON.stringify({ deploy_date: deployDate }) }),
  getAssessmentReport: (id: string) => fetchApi(`/assessments/${id}/report`),
  getComplianceChain: (assId: string, findingId: string) => fetchApi(`/assessments/${assId}/chain/${findingId}`),
  
  // KB
  getKbVersions: () => fetchApi("/kb/versions"),
  approveKbVersion: (id: string) => fetchApi(`/kb/versions/${id}/approve`, { method: "POST" }),
};
