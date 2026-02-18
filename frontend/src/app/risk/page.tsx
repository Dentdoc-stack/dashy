"use client";

import { useQuery } from "@tanstack/react-query";
import {
  fetchRiskScores,
  fetchRiskDistribution,
  fetchRecoveryCandidates,
  fetchRiskTrends,
  fetchPackageNames,
  fetchDistricts,
} from "@/lib/api";
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
import { ShieldAlert, TrendingDown, Target } from "lucide-react";
import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
} from "recharts";

const RISK_COLORS = ["#22c55e", "#84cc16", "#f59e0b", "#f97316", "#ef4444"];

function riskColor(score: number) {
  if (score >= 80) return "text-red-600 bg-red-50";
  if (score >= 60) return "text-orange-600 bg-orange-50";
  if (score >= 40) return "text-amber-600 bg-amber-50";
  if (score >= 20) return "text-lime-600 bg-lime-50";
  return "text-green-600 bg-green-50";
}

export default function RiskRecoveryPage() {
  const [selectedPkg, setSelectedPkg] = useState<string>("");
  const [selectedDist, setSelectedDist] = useState<string>("");

  const pkgFilter = selectedPkg && selectedPkg !== "all" ? selectedPkg : undefined;
  const distFilter = selectedDist && selectedDist !== "all" ? selectedDist : undefined;

  const { data: packages } = useQuery({
    queryKey: ["packages-list"],
    queryFn: fetchPackageNames,
  });

  const { data: districts } = useQuery({
    queryKey: ["districts", pkgFilter],
    queryFn: () => fetchDistricts(pkgFilter),
  });

  const { data: riskDist } = useQuery({
    queryKey: ["risk-distribution", pkgFilter],
    queryFn: () => fetchRiskDistribution(pkgFilter),
  });

  const { data: scores } = useQuery({
    queryKey: ["risk-scores", pkgFilter, distFilter],
    queryFn: () => fetchRiskScores(pkgFilter, distFilter),
  });

  const { data: candidates } = useQuery({
    queryKey: ["recovery-candidates", pkgFilter],
    queryFn: () => fetchRecoveryCandidates(pkgFilter),
  });

  const { data: trends } = useQuery({
    queryKey: ["risk-trends"],
    queryFn: fetchRiskTrends,
  });

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Risk & Recovery</h1>
          <p className="text-sm text-muted-foreground">
            Identify high-risk sites and recovery opportunities
          </p>
        </div>
        <div className="flex gap-3">
          <Select value={selectedPkg} onValueChange={(v) => { setSelectedPkg(v); setSelectedDist(""); }}>
            <SelectTrigger className="w-[240px]">
              <SelectValue placeholder="All Packages" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Packages</SelectItem>
              {packages?.map((p) => (
                <SelectItem key={p} value={p}>{p}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={selectedDist} onValueChange={setSelectedDist}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="All Districts" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Districts</SelectItem>
              {districts?.map((d) => (
                <SelectItem key={d} value={d}>{d}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Risk Distribution Chart + Stats */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <ShieldAlert className="h-4 w-4" />
              Risk Score Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={riskDist ?? []}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="bracket" className="text-xs" tick={{ fontSize: 10 }} />
                <YAxis className="text-xs" />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {riskDist?.map((_, i) => (
                    <Cell key={i} fill={RISK_COLORS[i % RISK_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <TrendingDown className="h-4 w-4" />
              Historical Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            {trends && trends.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="timestamp" className="text-xs" tick={{ fontSize: 10 }} />
                  <YAxis className="text-xs" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="avg_progress"
                    stroke="#3b82f6"
                    name="Avg Progress %"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="avg_risk_score"
                    stroke="#ef4444"
                    name="Avg Risk Score"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground text-sm">
                No trend data yet. Refresh data to start collecting snapshots.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recovery Candidates */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Target className="h-4 w-4 text-amber-500" />
            Recovery Candidates (Active + Risk ≥ 40)
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
                  <TableHead>Delay Bucket</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Mobilized</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {candidates?.map((s, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-xs">{s.package_name}</TableCell>
                    <TableCell className="text-xs">{s.district}</TableCell>
                    <TableCell className="text-xs font-medium">{s.site_name}</TableCell>
                    <TableCell className="text-right text-xs">
                      <div className="flex items-center gap-2 justify-end">
                        <Progress value={s.site_progress} className="h-1.5 w-16" />
                        <span>{s.site_progress?.toFixed(1)}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right text-xs">
                      {s.site_delay_days ?? "—"}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{s.delay_bucket}</Badge>
                    </TableCell>
                    <TableCell>
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${riskColor(s.risk_score)}`}>
                        {s.risk_score}
                      </span>
                    </TableCell>
                    <TableCell className="text-xs">
                      {s.mobilization_taken}
                      {s.mobilized_low_progress && (
                        <Badge variant="destructive" className="ml-1 text-[10px]">LOW</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {(!candidates || candidates.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                      No recovery candidates found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Full Risk Scores Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">All Site Risk Scores</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border max-h-[500px] overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Package</TableHead>
                  <TableHead>District</TableHead>
                  <TableHead>Site</TableHead>
                  <TableHead className="text-right">Progress</TableHead>
                  <TableHead className="text-right">Delay</TableHead>
                  <TableHead className="text-right">Risk</TableHead>
                  <TableHead className="text-right">Delay Score</TableHead>
                  <TableHead className="text-right">Progress Score</TableHead>
                  <TableHead className="text-right">Mob Score</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scores?.slice(0, 50).map((s, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-xs">{s.package_name}</TableCell>
                    <TableCell className="text-xs">{s.district}</TableCell>
                    <TableCell className="text-xs font-medium">{s.site_name}</TableCell>
                    <TableCell className="text-right text-xs">{s.site_progress?.toFixed(1)}%</TableCell>
                    <TableCell className="text-right text-xs">{s.site_delay_days ?? "—"}</TableCell>
                    <TableCell className="text-right">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${riskColor(s.risk_score)}`}>
                        {s.risk_score}
                      </span>
                    </TableCell>
                    <TableCell className="text-right text-xs">{s.delay_score}</TableCell>
                    <TableCell className="text-right text-xs">{s.progress_score}</TableCell>
                    <TableCell className="text-right text-xs">{s.mobilization_score}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{s.site_status}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Need Cell import for BarChart coloring
import { Cell } from "recharts";
