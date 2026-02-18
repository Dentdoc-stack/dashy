/* ── API client for the FastAPI backend ── */

import type {
  SituationKPIs,
  DelayBucket,
  StatusBreakdown,
  ComplianceSummary,
  PackageProgressItem,
  SiteRecord,
  PackageSummary,
  PackageDetail,
  DistrictSummary,
  TaskRecord,
  RiskScore,
  RiskBracket,
  TrendPoint,
  IPCStatus,
  PhotoEntry,
  HealthCheck,
} from "./types";

// In the browser, API_BASE is "" so all /api/* calls go to the same origin.
// Next.js rewrites proxy them to the backend — no CORS issues in Codespaces.
// On the server (SSR), use the explicit backend URL.
const API_BASE = typeof window !== "undefined" ? "" : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

async function fetchJSON<T>(path: string, params?: Record<string, string>): Promise<T> {
  let url = `${API_BASE}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => Boolean(v)))
    ).toString();
    if (qs) url += `?${qs}`;
  }
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
}

// ── Health ──
export const fetchHealth = () => fetchJSON<HealthCheck>("/api/health");

// ── Data ──
export const refreshData = async () => {
  const res = await fetch(`${API_BASE}/api/data/refresh`, { method: "POST", cache: "no-store" });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json();
};

// ── Filters ──
export const fetchPackageNames = () => fetchJSON<string[]>("/api/filters/packages");
export const fetchDistricts = (pkg?: string) =>
  fetchJSON<string[]>("/api/filters/districts", pkg ? { package_name: pkg } : undefined);
export const fetchSiteNames = (pkg?: string, dist?: string) =>
  fetchJSON<string[]>("/api/filters/sites", {
    ...(pkg ? { package_name: pkg } : {}),
    ...(dist ? { district: dist } : {}),
  });

// ── Situation Room ──
export const fetchSituationKPIs = (pkg?: string) =>
  fetchJSON<SituationKPIs>("/api/situation-room/kpis", pkg ? { package_name: pkg } : undefined);
export const fetchDelayDistribution = (pkg?: string) =>
  fetchJSON<DelayBucket[]>("/api/situation-room/delay-distribution", pkg ? { package_name: pkg } : undefined);
export const fetchStatusBreakdown = (pkg?: string) =>
  fetchJSON<StatusBreakdown[]>("/api/situation-room/status-breakdown", pkg ? { package_name: pkg } : undefined);
export const fetchCompliance = (pkg?: string) =>
  fetchJSON<ComplianceSummary>("/api/situation-room/compliance", pkg ? { package_name: pkg } : undefined);
export const fetchProgressByPackage = () =>
  fetchJSON<PackageProgressItem[]>("/api/situation-room/progress-by-package");
export const fetchRedList = (pkg?: string, limit = 20) =>
  fetchJSON<SiteRecord[]>("/api/situation-room/red-list", {
    ...(pkg ? { package_name: pkg } : {}),
    limit: String(limit),
  });

// ── Packages ──
export const fetchPackages = () => fetchJSON<PackageSummary[]>("/api/packages/");
export const fetchPackageDetail = (name: string) =>
  fetchJSON<PackageDetail>(`/api/packages/${encodeURIComponent(name)}`);
export const fetchPackageDistricts = (name: string) =>
  fetchJSON<DistrictSummary[]>(`/api/packages/${encodeURIComponent(name)}/districts`);
export const fetchPackageSites = (name: string, dist?: string) =>
  fetchJSON<SiteRecord[]>(`/api/packages/${encodeURIComponent(name)}/sites`, dist ? { district: dist } : undefined);
export const fetchPackageDelayChart = (name: string) =>
  fetchJSON<DelayBucket[]>(`/api/packages/${encodeURIComponent(name)}/delay-chart`);

// ── Risk ──
export const fetchRiskScores = (pkg?: string, dist?: string) =>
  fetchJSON<RiskScore[]>("/api/risk/scores", {
    ...(pkg ? { package_name: pkg } : {}),
    ...(dist ? { district: dist } : {}),
  });
export const fetchRiskDistribution = (pkg?: string) =>
  fetchJSON<RiskBracket[]>("/api/risk/distribution", pkg ? { package_name: pkg } : undefined);
export const fetchRecoveryCandidates = (pkg?: string, limit = 20) =>
  fetchJSON<SiteRecord[]>("/api/risk/recovery-candidates", {
    ...(pkg ? { package_name: pkg } : {}),
    limit: String(limit),
  });
export const fetchRiskTrends = () => fetchJSON<TrendPoint[]>("/api/risk/trends");

// ── Sites ──
export const fetchSiteDetail = (pkg: string, dist: string, site: string) =>
  fetchJSON<SiteRecord | null>("/api/sites/detail", {
    package_name: pkg,
    district: dist,
    site_name: site,
  });
export const fetchSiteTasks = (pkg: string, dist: string, site: string) =>
  fetchJSON<TaskRecord[]>("/api/sites/tasks", {
    package_name: pkg,
    district: dist,
    site_name: site,
  });
export const fetchSiteIPC = (pkg: string, dist: string, site: string) =>
  fetchJSON<IPCStatus>("/api/sites/ipc", {
    package_name: pkg,
    district: dist,
    site_name: site,
  });
export const fetchSitePhotos = (pkg: string, dist: string, site: string) =>
  fetchJSON<PhotoEntry[]>("/api/sites/photos", {
    package_name: pkg,
    district: dist,
    site_name: site,
  });
