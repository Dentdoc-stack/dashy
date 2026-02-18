"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ShieldAlert,
  Package,
  MapPin,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { refreshData } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

const navItems = [
  {
    label: "Situation Room",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Risk & Recovery",
    href: "/risk",
    icon: ShieldAlert,
  },
  {
    label: "Package Deep Dive",
    href: "/packages",
    icon: Package,
  },
  {
    label: "Site Command Center",
    href: "/sites",
    icon: MapPin,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshData();
      queryClient.invalidateQueries();
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <aside className="flex h-screen w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex items-center gap-2 border-b px-6 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
          KP
        </div>
        <div>
          <h1 className="text-sm font-semibold leading-none">KP-HCIP</h1>
          <p className="text-[11px] text-muted-foreground">Executive Dashboard</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Refresh button */}
      <div className="border-t p-4">
        <Button
          variant="outline"
          className="w-full gap-2"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
          {refreshing ? "Refreshing…" : "Refresh Data"}
        </Button>
      </div>
    </aside>
  );
}
