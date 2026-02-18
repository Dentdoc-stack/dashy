"use client";

import { useQuery } from "@tanstack/react-query";
import {
  fetchPackageNames,
  fetchDistricts,
  fetchSiteNames,
  fetchSiteDetail,
  fetchSiteTasks,
  fetchSiteIPC,
  fetchSitePhotos,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KPICard } from "@/components/kpi-card";
import { Separator } from "@/components/ui/separator";
import {
  MapPin,
  ListTodo,
  FileCheck2,
  Camera,
  Activity,
  Clock,
  ShieldAlert,
} from "lucide-react";
import { useState } from "react";

const IPC_LABELS: Record<string, string> = {
  ipc_1: "IPC 1",
  ipc_2: "IPC 2",
  ipc_3: "IPC 3",
  ipc_4: "IPC 4",
  ipc_5: "IPC 5",
  ipc_6: "IPC 6",
};

const IPC_STATUS_COLOR: Record<string, string> = {
  "Released": "bg-green-100 text-green-800 border-green-300",
  "In Process": "bg-blue-100 text-blue-800 border-blue-300",
  "Submitted": "bg-amber-100 text-amber-800 border-amber-300",
  "Not Submitted": "bg-gray-100 text-gray-600 border-gray-300",
};

export default function SiteCommandCenterPage() {
  const [pkg, setPkg] = useState("");
  const [dist, setDist] = useState("");
  const [site, setSite] = useState("");

  const { data: packages } = useQuery({
    queryKey: ["packages-list"],
    queryFn: fetchPackageNames,
  });

  const { data: districts } = useQuery({
    queryKey: ["districts", pkg],
    queryFn: () => fetchDistricts(pkg || undefined),
    enabled: !!pkg,
  });

  const { data: siteNames } = useQuery({
    queryKey: ["site-names", pkg, dist],
    queryFn: () => fetchSiteNames(pkg || undefined, dist || undefined),
    enabled: !!pkg && !!dist,
  });

  const siteSelected = !!pkg && !!dist && !!site;

  const { data: detail } = useQuery({
    queryKey: ["site-detail", pkg, dist, site],
    queryFn: () => fetchSiteDetail(pkg, dist, site),
    enabled: siteSelected,
  });

  const { data: tasks } = useQuery({
    queryKey: ["site-tasks", pkg, dist, site],
    queryFn: () => fetchSiteTasks(pkg, dist, site),
    enabled: siteSelected,
  });

  const { data: ipc } = useQuery({
    queryKey: ["site-ipc", pkg, dist, site],
    queryFn: () => fetchSiteIPC(pkg, dist, site),
    enabled: siteSelected,
  });

  const { data: photos } = useQuery({
    queryKey: ["site-photos", pkg, dist, site],
    queryFn: () => fetchSitePhotos(pkg, dist, site),
    enabled: siteSelected,
  });

  return (
    <div className="space-y-6 p-6">
      {/* Header + Filters */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Site Command Center</h1>
        <p className="text-sm text-muted-foreground mb-4">
          Select a site to see full task, IPC, and photo details
        </p>
        <div className="flex flex-wrap gap-3">
          <Select value={pkg} onValueChange={(v) => { setPkg(v); setDist(""); setSite(""); }}>
            <SelectTrigger className="w-[260px]">
              <SelectValue placeholder="Select Package" />
            </SelectTrigger>
            <SelectContent>
              {packages?.map((p) => (
                <SelectItem key={p} value={p}>{p}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={dist} onValueChange={(v) => { setDist(v); setSite(""); }} disabled={!pkg}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select District" />
            </SelectTrigger>
            <SelectContent>
              {districts?.map((d) => (
                <SelectItem key={d} value={d}>{d}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={site} onValueChange={setSite} disabled={!dist}>
            <SelectTrigger className="w-[260px]">
              <SelectValue placeholder="Select Site" />
            </SelectTrigger>
            <SelectContent>
              {siteNames?.map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Prompt */}
      {!siteSelected && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <MapPin className="h-12 w-12 mb-4 opacity-30" />
            <p className="text-lg font-medium">Select a package, district, and site above</p>
            <p className="text-sm">to view detailed task-level information</p>
          </CardContent>
        </Card>
      )}

      {/* Site Detail */}
      {siteSelected && detail && (
        <>
          {/* KPIs */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <KPICard
              title="Site Progress"
              value={`${detail.site_progress?.toFixed(1)}%`}
              icon={Activity}
              variant={
                detail.site_progress >= 80
                  ? "success"
                  : detail.site_progress >= 40
                  ? "warning"
                  : "danger"
              }
            />
            <KPICard
              title="Delay Days"
              value={detail.site_delay_days ?? 0}
              subtitle={`Bucket: ${detail.delay_bucket}`}
              icon={Clock}
            />
            <KPICard
              title="Risk Score"
              value={detail.risk_score}
              icon={ShieldAlert}
              variant={
                detail.risk_score >= 80
                  ? "danger"
                  : detail.risk_score >= 40
                  ? "warning"
                  : "default"
              }
            />
            <KPICard
              title="Status"
              value={detail.site_status}
              subtitle={`Mobilized: ${detail.mobilization_taken}`}
            />
          </div>

          {/* Tabs: Tasks / IPC / Photos */}
          <Tabs defaultValue="tasks">
            <TabsList>
              <TabsTrigger value="tasks">
                <ListTodo className="h-3.5 w-3.5 mr-1.5" />
                Tasks ({tasks?.length ?? 0})
              </TabsTrigger>
              <TabsTrigger value="ipc">
                <FileCheck2 className="h-3.5 w-3.5 mr-1.5" />
                IPC Status
              </TabsTrigger>
              <TabsTrigger value="photos">
                <Camera className="h-3.5 w-3.5 mr-1.5" />
                Photos ({photos?.length ?? 0})
              </TabsTrigger>
            </TabsList>

            {/* Tasks */}
            <TabsContent value="tasks" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="rounded-md border max-h-[500px] overflow-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Discipline</TableHead>
                          <TableHead>Task</TableHead>
                          <TableHead>Planned Start</TableHead>
                          <TableHead>Planned Finish</TableHead>
                          <TableHead>Actual Start</TableHead>
                          <TableHead>Actual Finish</TableHead>
                          <TableHead className="text-right">Progress</TableHead>
                          <TableHead className="text-right">Delay (d)</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {tasks?.map((t, i) => (
                          <TableRow key={i}>
                            <TableCell className="text-xs">{t.discipline}</TableCell>
                            <TableCell className="text-xs font-medium">{t.task_name}</TableCell>
                            <TableCell className="text-xs">{fmtDate(t.planned_start)}</TableCell>
                            <TableCell className="text-xs">{fmtDate(t.planned_finish)}</TableCell>
                            <TableCell className="text-xs">{fmtDate(t.actual_start)}</TableCell>
                            <TableCell className="text-xs">{fmtDate(t.actual_finish)}</TableCell>
                            <TableCell className="text-right text-xs">
                              <div className="flex items-center gap-2 justify-end">
                                <Progress value={t.progress_pct} className="h-1.5 w-12" />
                                <span>{t.progress_pct}%</span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right text-xs">
                              {t.task_delay_days ?? "—"}
                            </TableCell>
                            <TableCell>
                              <Badge
                                variant={
                                  t.task_status === "Completed"
                                    ? "default"
                                    : t.task_status === "In Progress"
                                    ? "secondary"
                                    : "outline"
                                }
                              >
                                {t.task_status}
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                        {(!tasks || tasks.length === 0) && (
                          <TableRow>
                            <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                              No tasks found
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* IPC */}
            <TabsContent value="ipc" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">IPC Milestones</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
                    {Object.entries(IPC_LABELS).map(([key, label]) => {
                      const status = ipc?.[key as keyof typeof ipc] ?? "Not Submitted";
                      const colorClass = IPC_STATUS_COLOR[status] || IPC_STATUS_COLOR["Not Submitted"];
                      return (
                        <div
                          key={key}
                          className={`rounded-lg border p-4 text-center ${colorClass}`}
                        >
                          <p className="text-xs font-medium mb-1">{label}</p>
                          <p className="text-sm font-semibold">{status}</p>
                        </div>
                      );
                    })}
                  </div>
                  {ipc?.ipc_best_stage && (
                    <div className="mt-4 text-sm text-muted-foreground">
                      Best IPC stage: <strong>{ipc.ipc_best_stage}</strong>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Photos */}
            <TabsContent value="photos" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Before / After Photos</CardTitle>
                </CardHeader>
                <CardContent>
                  {photos && photos.length > 0 ? (
                    <div className="space-y-6">
                      {photos.map((p, i) => (
                        <div key={i} className="border rounded-lg p-4">
                          <div className="text-sm font-medium mb-2">
                            {p.discipline} — {p.task_name}
                          </div>
                          <div className="grid gap-4 md:grid-cols-2">
                            {p.before_photo_direct_url && (
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Before</p>
                                <img
                                  src={p.before_photo_direct_url}
                                  alt={`Before - ${p.task_name}`}
                                  className="rounded-md border w-full max-h-64 object-cover"
                                />
                              </div>
                            )}
                            {p.after_photo_direct_url && (
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">After</p>
                                <img
                                  src={p.after_photo_direct_url}
                                  alt={`After - ${p.task_name}`}
                                  className="rounded-md border w-full max-h-64 object-cover"
                                />
                              </div>
                            )}
                          </div>
                          {(p.before_photo_share_url || p.after_photo_share_url) && (
                            <div className="flex gap-3 mt-2">
                              {p.before_photo_share_url && (
                                <a
                                  href={p.before_photo_share_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs text-blue-600 hover:underline"
                                >
                                  Before (full)
                                </a>
                              )}
                              {p.after_photo_share_url && (
                                <a
                                  href={p.after_photo_share_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs text-blue-600 hover:underline"
                                >
                                  After (full)
                                </a>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center py-12 text-muted-foreground">
                      <Camera className="h-8 w-8 mr-3 opacity-30" />
                      No photos available for this site
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}
