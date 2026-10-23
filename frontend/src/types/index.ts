export interface ExecutionLog {
  id: number;
  run_id: string;
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  stage: "EXTRACT" | "VALIDATE" | "TRANSFORM" | "LOAD" | "QUALITY_CHECK" | "RECOVERY";
  message: string;
  context_data?: string | null;
}

export interface QualityCheckItem {
  id: number;
  run_id?: string;
  check_name: string;
  check_type: "COMPLETENESS" | "UNIQUENESS" | "RECONCILIATION" | "FORMAT" | "SCHEMA" | "VOLUME";
  status: "PASSED" | "WARNING" | "FAILED";
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  records_evaluated: number;
  records_failed: number;
  details?: Record<string, any>;
  details_json?: string;
  execution_time_ms: number;
  created_at: string;
}


export interface Incident {
  id: string;
  run_id: string;
  pipeline_id: string;
  pipeline_name?: string;
  pipeline_code?: string;
  run_status?: string;
  run_scenario?: string;
  title: string;
  category: "RECORD_LOSS" | "DUPLICATE_KEYS" | "NULL_VIOLATION" | "FORMAT_ERROR" | "SCHEMA_MISMATCH" | "SYSTEM_FAILURE";
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "UNRESOLVED" | "INVESTIGATING" | "RECOVERING" | "RESOLVED";
  root_cause_summary: string;
  confidence_score: number;
  evidence_json: string;
  parsed_evidence?: Record<string, any>;
  recommendation: string;
  created_at: string;
  resolved_at?: string | null;
  recovery_attempts?: any[];
}

export interface PipelineRun {
  id: string;
  pipeline_id: string;
  pipeline_name?: string;
  pipeline_code?: string;
  scenario: string;
  status: "pending" | "running" | "success" | "failed";
  started_at: string;
  completed_at?: string | null;
  duration_ms: number;
  source_record_count: number;
  target_record_count: number;
  records_inserted: number;
  records_updated: number;
  records_rejected: number;
  error_message?: string | null;
  is_retry: boolean;
  parent_run_id?: string | null;
  logs?: ExecutionLog[];
  quality_checks?: QualityCheckItem[];
  incidents?: Incident[];
  recovery_attempts?: any[];
}

export interface Pipeline {
  id: string;
  name: string;
  code: string;
  description: string;
  source_type: string;
  target_type: string;
  schedule: string;
  status: "active" | "paused" | "failed";
  created_at: string;
  updated_at: string;
  total_runs: number;
  last_run_status?: string | null;
  last_run_time?: string | null;
  last_run_duration_ms?: number | null;
  success_rate: number;
}

export interface FailureTrendPoint {
  date: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  success_rate: number;
}

export interface QualityMetricSummary {
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  pass_rate: number;
}

export interface DashboardSummary {
  total_pipeline_runs: number;
  successful_runs: number;
  failed_runs: number;
  success_rate: number;
  avg_duration_ms: number;
  unresolved_incidents: number;
  recent_runs: PipelineRun[];
  active_incidents: Incident[];
  failure_trends: FailureTrendPoint[];
  quality_summary: QualityMetricSummary;
}

export interface QualitySummaryResponse {
  total_checks: number;
  passed_checks: number;
  warning_checks: number;
  failed_checks: number;
  pass_rate: number;
  checks_by_type: Record<string, { PASSED: number; WARNING: number; FAILED: number; TOTAL: number }>;
  recent_failures: QualityCheckItem[];
}

export interface RecoveryActionPlan {
  run_id: string;
  incident_id?: string | null;
  strategy: string;
  action_description: string;
  safety_checks_passed: boolean;
  requires_confirmation: boolean;
  estimated_records_to_process: number;
  duplicate_protection_active: boolean;
  warning_notes?: string | null;
}

export interface RecoveryAttemptResponse {
  id: string;
  incident_id: string;
  original_run_id: string;
  recovery_run_id?: string | null;
  strategy: string;
  status: "INITIATED" | "IN_PROGRESS" | "SUCCESS" | "FAILED";
  records_recovered: number;
  validation_passed: boolean;
  notes: string;
  created_at: string;
}
