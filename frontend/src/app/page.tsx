"use client";

import { useQuery } from "@tanstack/react-query";
import {
  fetchSituationKPIs,
  fetchDelayDistribution,
  fetchStatusBreakdown,
  fetchCompliance,
  fetchProgressByPackage,
  fetchRedList,
  fetchPackageNames,
} from "@/lib/api";
import { KPICard } from "@/components/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import {
  Building2,
  Activity,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";
import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const DELAY_COLORS: Record<string, string> = {
  "On Track": "#22c55e",
  "1-30": "#f59e0b",
  "31-60": "#f97316",
  ">60": "#ef4444",
};

const STATUS_COLORS: Record<string, string> = {
  Active: "#3b82f6",
  Completed: "#22c55e",
  Inactive: "#94a3b8",
};

export default function SituationRoomPage() {
  const [selectedPkg, setSelectedPkg] = useState<string>("");

  const pkgFilter = selectedPkg && selectedPkg !== "all" ? selectedPkg : undefined;

  const { data: packages } = useQuery({
    queryKey: ["packages-list"],
    queryFn: fetchPackageNames,
  });

  const { data: kpis, isLoading } = useQuery({
    queryKey: ["situation-kpis", pkgFilter],
    queryFn: () => fetchSituationKPIs(pkgFilter),
  });

  const { data: delays } = useQuery({
    queryKey: ["delay-dist", pkgFilter],
    queryFn: () => fetchDelayDistribution(pkgFilter),
  });

  const { data: statuses } = useQuery({
    queryKey: ["status-breakdown", pkgFilter],
    queryFn: () => fetchStatusBreakdown(pkgFilter),
  });

  const { data: compliance } = useQuery({
    queryKey: ["compliance", pkgFilter],
    queryFn: () => fetchCompliance(pkgFilter),
  });

  const { data: pkgProgress } = useQuery({
    queryKey: ["progress-by-package"],
    queryFn: fetchProgressByPackage,
  });

  const { data: redList } = useQuery({
    queryKey: ["red-list", pkgFilter],
    queryFn: () => fetchRedList(pkgFilter),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse text-muted-foreground">Loading dashboard…</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Situation Room</h1>
          <p className="text-sm text-muted-foreground">
            Executive overview across all construction packages
          </p>
        </div>
        <Select value={selectedPkg} onValueChange={setSelectedPkg}>
          <SelectTrigger className="w-[260px]">
            <SelectValue placeholder="All Packages" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Packages</SelectItem>
            {packages?.map((p) => (
              <SelectItem key={p} value={p}>
                {p}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Sites"
          value={kpis?.total_sites ?? 0}
          icon={Building2}
        />
        <KPICard
          title="Average Progress"
          value={`${kpis?.avg_progress ?? 0}%`}
          icon={Activity}
          variant={
            (kpis?.avg_progress ?? 0) >= 50
              ? "success"
              : (kpis?.avg_progress ?? 0) >= 25
              ? "warning"
              : "danger"
          }
        />
        <KPICard
          title="Active Sites"
          value={kpis?.active ?? 0}
          subtitle={`${kpis?.completed ?? 0} completed · ${kpis?.inactive ?? 0} inactive`}
          icon={CheckCircle2}
        />
        <KPICard
          title="Critically Delayed (>60d)"
          value={kpis?.delayed_gt60 ?? 0}
          subtitle={`${kpis?.delayed_gt30 ?? 0} delayed >30d`}
          icon={AlertTriangle}
          variant={(kpis?.delayed_gt60 ?? 0) > 0 ? "danger" : "default"}
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Delay Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Delay Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={delays ?? []}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="bucket" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {delays?.map((entry) => (
                    <Cell
                      key={entry.bucket}
                      fill={DELAY_COLORS[entry.bucket] || "#64748b"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Site Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={statuses ?? []}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  label={(props) => {
                    const name = props.name ?? "";
                    const value = props.value ?? 0;
                    return `${name}: ${value}`;
                  }}
                >
                  {statuses?.map((entry) => (
                    <Cell
                      key={entry.status}
                      fill={STATUS_COLORS[entry.status] || "#64748b"}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Compliance + Package Progress */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Compliance Gauges */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Compliance Rates</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {[
              { label: "CESMPS", value: compliance?.cesmps ?? 0 },
              { label: "OHS Measures", value: compliance?.ohs ?? 0 },
              { label: "RFB Staff", value: compliance?.rfb ?? 0 },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-sm font-medium">{item.label}</span>
                  <span className="text-sm text-muted-foreground">{item.value}%</span>
                </div>
                <Progress value={item.value} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Package Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Progress by Package</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={pkgProgress ?? []}
                layout="vertical"
                margin={{ left: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis type="number" domain={[0, 100]} className="text-xs" />
                <YAxis
                  dataKey="package_name"
                  type="category"
                  className="text-xs"
                  width={150}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip />
                <Bar dataKey="avg_progress" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Red List Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            Red List — Highest Risk Sites
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Package</TableHead>
                  <TableHead>District</TableHead>
                  <TableHead>Site</TableHead>
                  <TableHead className="text-right">Progress</TableHead>
                  <TableHead className="text-right">Delay (d)</TableHead>
                  <TableHead>Risk</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {redList?.slice(0, 15).map((s, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-xs">{s.package_name}</TableCell>
                    <TableCell className="text-xs">{s.district}</TableCell>
                    <TableCell className="text-xs font-medium">{s.site_name}</TableCell>
                    <TableCell className="text-right text-xs">
                      {s.site_progress?.toFixed(1)}%
                    </TableCell>
                    <TableCell className="text-right text-xs">
                      {s.site_delay_days ?? "—"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          s.risk_score >= 80
                            ? "destructive"
                            : s.risk_score >= 40
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {s.risk_score}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{s.site_status}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
                {(!redList || redList.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      No data available
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
