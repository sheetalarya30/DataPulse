import {
  DashboardSummary,
  Pipeline,
  PipelineRun,
  ExecutionLog,
  QualityCheckItem,
  Incident,
  QualitySummaryResponse,
  RecoveryActionPlan,
  RecoveryAttemptResponse,
} from "../types";

const API_BASE = "/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = "API Request Failed";
    try {
      const errData = await response.json();
      errorDetail = errData.error?.message || errData.detail || JSON.stringify(errData);
    } catch {
      errorDetail = `HTTP ${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; database: { status: string; dialect: string }; timestamp: string }>(`${API_BASE}/health`),

  // Dashboard
  getDashboardSummary: () => fetchJson<DashboardSummary>(`${API_BASE}/dashboard/summary`),

  // Pipelines
  getPipelines: () => fetchJson<Pipeline[]>(`${API_BASE}/pipelines`),
  getPipeline: (id: string) => fetchJson<Pipeline>(`${API_BASE}/pipelines/${id}`),
  getPipelineRuns: (id: string) => fetchJson<PipelineRun[]>(`${API_BASE}/pipelines/${id}/runs`),
  triggerPipelineRun: (pipelineId: string, scenario: string = "success") =>
    fetchJson<PipelineRun>(`${API_BASE}/pipelines/${pipelineId}/runs`, {
      method: "POST",
      body: JSON.stringify({ scenario }),
    }),

  // Runs
  getRun: (id: string) => fetchJson<PipelineRun>(`${API_BASE}/runs/${id}`),
  getRunLogs: (id: string) => fetchJson<ExecutionLog[]>(`${API_BASE}/runs/${id}/logs`),
  getRunQualityChecks: (id: string) => fetchJson<QualityCheckItem[]>(`${API_BASE}/runs/${id}/quality-checks`),

  // Incidents
  getIncidents: (status?: string) => {
    const url = status ? `${API_BASE}/incidents?status=${status}` : `${API_BASE}/incidents`;
    return fetchJson<Incident[]>(url);
  },
  getIncident: (id: string) => fetchJson<Incident>(`${API_BASE}/incidents/${id}`),

  // Quality
  getQualitySummary: () => fetchJson<QualitySummaryResponse>(`${API_BASE}/quality/summary`),

  // Recovery & Diagnosis
  diagnoseRun: (runId: string) =>
    fetchJson<Incident>(`${API_BASE}/runs/${runId}/diagnose`, {
      method: "POST",
    }),
  getRecoveryPlan: (runId: string) => fetchJson<RecoveryActionPlan>(`${API_BASE}/runs/${runId}/recovery-plan`),
  executeRecovery: (runId: string, confirm: boolean = true, strategy: string = "IDEMPOTENT_MERGE") =>
    fetchJson<RecoveryAttemptResponse>(`${API_BASE}/runs/${runId}/retry`, {
      method: "POST",
      body: JSON.stringify({ confirm, strategy }),
    }),
};
