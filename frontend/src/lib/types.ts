/* ── TypeScript types matching backend API responses ── */

export interface SummaryKPIs {
  total_sites: number;
  total_tasks: number;
  active_sites: number;
  completed_sites: number;
  inactive_sites: number;
  avg_progress: number;
  sites_gt30_delayed: number;
  sites_gt60_delayed: number;
  mobilized_low_progress: number;
  cache_timestamp: string | null;
  warnings: string[];
}

export interface SituationKPIs {
  total_sites: number;
  avg_progress: number;
  active: number;
  completed: number;
  inactive: number;
  delayed_gt30: number;
  delayed_gt60: number;
  mobilized_low_progress: number;
}

export interface DelayBucket {
  bucket: string;
  count: number;
}

export interface StatusBreakdown {
  status: string;
  count: number;
}

export interface ComplianceSummary {
  cesmps: number;
  ohs: number;
  rfb: number;
}

export interface PackageSummary {
  package_name: string;
  total_sites: number;
  avg_progress: number;
  active_sites: number;
  inactive_sites: number;
  completed_sites: number;
  sites_gt30_delayed: number;
  sites_gt60_delayed: number;
  mobilized_low_progress_count: number;
  no_ipc_released_count: number;
  cesmps_pct_yes?: number;
  ohs_pct_yes?: number;
  rfb_pct_yes?: number;
}

export interface PackageProgressItem {
  package_name: string;
  avg_progress: number;
  total_sites: number;
  active_sites: number;
  completed_sites: number;
  inactive_sites: number;
}

export interface DistrictSummary {
  package_name: string;
  district: string;
  total_sites: number;
  avg_progress: number;
  sites_gt60_delayed: number;
  mobilized_low_progress_count: number;
  inactive_sites: number;
}

export interface SiteRecord {
  package_name: string;
  district: string;
  site_name: string;
  site_progress: number;
  site_delay_days: number | null;
  delay_bucket: string;
  risk_score: number;
  site_status: string;
  mobilization_taken: string;
  mobilized_low_progress: boolean;
  ipc_best_stage?: string;
  no_ipc_released?: boolean;
  task_count?: number;
  earliest_planned_start?: string | null;
  last_updated?: string | null;
  cesmps?: string;
  ohs_yesno?: string;
  rfb_staff_yesno?: string;
  delay_score?: number;
  progress_score?: number;
  mobilization_score?: number;
}

export interface TaskRecord {
  discipline: string;
  task_name: string;
  planned_start: string | null;
  planned_finish: string | null;
  actual_start: string | null;
  actual_finish: string | null;
  planned_duration_days: number | null;
  progress_pct: number;
  task_delay_days: number | null;
  task_status: string;
  delay_flag_calc?: string;
  remarks?: string;
}

export interface RiskScore {
  package_name: string;
  district: string;
  site_name: string;
  site_progress: number;
  site_delay_days: number | null;
  delay_bucket: string;
  risk_score: number;
  delay_score: number;
  progress_score: number;
  mobilization_score: number;
  site_status: string;
  mobilization_taken: string;
  mobilized_low_progress: boolean;
}

export interface RiskBracket {
  bracket: string;
  min: number;
  max: number;
  count: number;
}

export interface TrendPoint {
  timestamp: string;
  avg_progress: number;
  avg_risk_score: number;
  total_sites: number;
}

export interface IPCStatus {
  ipc_1?: string;
  ipc_2?: string;
  ipc_3?: string;
  ipc_4?: string;
  ipc_5?: string;
  ipc_6?: string;
  ipc_best_stage?: string;
}

export interface PhotoEntry {
  task_name: string;
  discipline: string;
  before_photo_share_url: string | null;
  before_photo_direct_url: string | null;
  after_photo_share_url: string | null;
  after_photo_direct_url: string | null;
}

export interface PackageDetail {
  package: PackageSummary | null;
  districts: DistrictSummary[];
  sites: SiteRecord[];
}

export interface HealthCheck {
  status: string;
  rows_tasks: number;
  rows_sites: number;
  cache_timestamp: string | null;
}
