"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchPackages, fetchPackageDetail, fetchPackageNames } from "@/lib/api";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KPICard } from "@/components/kpi-card";
import {
  Package,
  MapPin,
  Building2,
  Activity,
  AlertTriangle,
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
  Cell,
} from "recharts";

const DELAY_COLORS: Record<string, string> = {
  "On Track": "#22c55e",
  "1-30": "#f59e0b",
  "31-60": "#f97316",
  ">60": "#ef4444",
};

export default function PackageDeepDivePage() {
  const [selectedPkg, setSelectedPkg] = useState<string>("");

  const { data: packages } = useQuery({
    queryKey: ["packages-table"],
    queryFn: fetchPackages,
  });

  const { data: packageNames } = useQuery({
    queryKey: ["packages-list"],
    queryFn: fetchPackageNames,
  });

  const { data: detail } = useQuery({
    queryKey: ["package-detail", selectedPkg],
    queryFn: () => fetchPackageDetail(selectedPkg),
    enabled: !!selectedPkg && selectedPkg !== "all",
  });

  const showDetail = selectedPkg && selectedPkg !== "all" && detail;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Package Deep Dive</h1>
          <p className="text-sm text-muted-foreground">
            Drill into package → district → site performance
          </p>
        </div>
        <Select value={selectedPkg} onValueChange={setSelectedPkg}>
          <SelectTrigger className="w-[280px]">
            <SelectValue placeholder="Select a package…" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Packages (Table)</SelectItem>
            {packageNames?.map((p) => (
              <SelectItem key={p} value={p}>{p}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Overview Table (when no specific package selected) */}
      {(!selectedPkg || selectedPkg === "all") && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Package className="h-4 w-4" />
              All Packages Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Package</TableHead>
                    <TableHead className="text-right">Sites</TableHead>
                    <TableHead className="text-right">Avg Progress</TableHead>
                    <TableHead className="text-right">Active</TableHead>
                    <TableHead className="text-right">Completed</TableHead>
                    <TableHead className="text-right">Inactive</TableHead>
                    <TableHead className="text-right">&gt;30d</TableHead>
                    <TableHead className="text-right">&gt;60d</TableHead>
                    <TableHead className="text-right">Mob Low</TableHead>
                    <TableHead className="text-right">CESMPS %</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {packages?.map((p) => (
                    <TableRow
                      key={p.package_name}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => setSelectedPkg(p.package_name)}
                    >
                      <TableCell className="font-medium text-sm">{p.package_name}</TableCell>
                      <TableCell className="text-right text-sm">{p.total_sites}</TableCell>
                      <TableCell className="text-right text-sm">
                        <div className="flex items-center gap-2 justify-end">
                          <Progress value={p.avg_progress} className="h-1.5 w-16" />
                          <span>{p.avg_progress?.toFixed(1)}%</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right text-sm">{p.active_sites}</TableCell>
                      <TableCell className="text-right text-sm">{p.completed_sites}</TableCell>
                      <TableCell className="text-right text-sm">{p.inactive_sites}</TableCell>
                      <TableCell className="text-right text-sm">
                        {p.sites_gt30_delayed > 0 ? (
                          <Badge variant="secondary">{p.sites_gt30_delayed}</Badge>
                        ) : 0}
                      </TableCell>
                      <TableCell className="text-right text-sm">
                        {p.sites_gt60_delayed > 0 ? (
                          <Badge variant="destructive">{p.sites_gt60_delayed}</Badge>
                        ) : 0}
                      </TableCell>
                      <TableCell className="text-right text-sm">
                        {p.mobilized_low_progress_count}
                      </TableCell>
                      <TableCell className="text-right text-sm">
                        {p.cesmps_pct_yes?.toFixed(0) ?? "—"}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed Package View */}
      {showDetail && (
        <>
          {/* Package KPIs */}
          {detail.package && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <KPICard
                title="Total Sites"
                value={detail.package.total_sites}
                icon={Building2}
              />
              <KPICard
                title="Avg Progress"
                value={`${detail.package.avg_progress?.toFixed(1)}%`}
                icon={Activity}
              />
              <KPICard
                title="Active Sites"
                value={detail.package.active_sites}
                subtitle={`${detail.package.completed_sites} done · ${detail.package.inactive_sites} inactive`}
              />
              <KPICard
                title="Delayed >60d"
                value={detail.package.sites_gt60_delayed}
                icon={AlertTriangle}
                variant={detail.package.sites_gt60_delayed > 0 ? "danger" : "default"}
              />
            </div>
          )}

          <Tabs defaultValue="districts">
            <TabsList>
              <TabsTrigger value="districts">
                <MapPin className="h-3.5 w-3.5 mr-1.5" />
                Districts
              </TabsTrigger>
              <TabsTrigger value="sites">
                <Building2 className="h-3.5 w-3.5 mr-1.5" />
                All Sites
              </TabsTrigger>
            </TabsList>

            {/* Districts Tab */}
            <TabsContent value="districts" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>District</TableHead>
                          <TableHead className="text-right">Sites</TableHead>
                          <TableHead className="text-right">Avg Progress</TableHead>
                          <TableHead className="text-right">&gt;60d Delay</TableHead>
                          <TableHead className="text-right">Mob Low</TableHead>
                          <TableHead className="text-right">Inactive</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {detail.districts?.map((d) => (
                          <TableRow key={d.district}>
                            <TableCell className="font-medium text-sm">{d.district}</TableCell>
                            <TableCell className="text-right text-sm">{d.total_sites}</TableCell>
                            <TableCell className="text-right text-sm">
                              <div className="flex items-center gap-2 justify-end">
                                <Progress value={d.avg_progress} className="h-1.5 w-16" />
                                <span>{d.avg_progress}%</span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right text-sm">
                              {d.sites_gt60_delayed > 0 ? (
                                <Badge variant="destructive">{d.sites_gt60_delayed}</Badge>
                              ) : 0}
                            </TableCell>
                            <TableCell className="text-right text-sm">
                              {d.mobilized_low_progress_count}
                            </TableCell>
                            <TableCell className="text-right text-sm">{d.inactive_sites}</TableCell>
                          </TableRow>
                        ))}
                        {(!detail.districts || detail.districts.length === 0) && (
                          <TableRow>
                            <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                              No district data
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Sites Tab */}
            <TabsContent value="sites" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="rounded-md border max-h-[600px] overflow-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>District</TableHead>
                          <TableHead>Site</TableHead>
                          <TableHead className="text-right">Progress</TableHead>
                          <TableHead className="text-right">Delay (d)</TableHead>
                          <TableHead>Delay Bucket</TableHead>
                          <TableHead>Risk</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>IPC Stage</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {detail.sites?.map((s, i) => (
                          <TableRow key={i}>
                            <TableCell className="text-xs">{s.district}</TableCell>
                            <TableCell className="text-xs font-medium">{s.site_name}</TableCell>
                            <TableCell className="text-right text-xs">
                              <div className="flex items-center gap-2 justify-end">
                                <Progress value={s.site_progress} className="h-1.5 w-12" />
                                <span>{s.site_progress?.toFixed(1)}%</span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right text-xs">{s.site_delay_days ?? "—"}</TableCell>
                            <TableCell>
                              <Badge
                                variant="outline"
                                className={
                                  s.delay_bucket === ">60"
                                    ? "border-red-300 text-red-700"
                                    : s.delay_bucket === "31-60"
                                    ? "border-orange-300 text-orange-700"
                                    : ""
                                }
                              >
                                {s.delay_bucket}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge
                                variant={
                                  s.risk_score >= 80 ? "destructive" : s.risk_score >= 40 ? "secondary" : "outline"
                                }
                              >
                                {s.risk_score}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">{s.site_status}</Badge>
                            </TableCell>
                            <TableCell className="text-xs">{s.ipc_best_stage ?? "—"}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}
