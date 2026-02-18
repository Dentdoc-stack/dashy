"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  className?: string;
  variant?: "default" | "success" | "warning" | "danger";
}

const variantStyles = {
  default: "",
  success: "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950",
  warning: "border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950",
  danger: "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950",
};

export function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  className,
  variant = "default",
}: KPICardProps) {
  return (
    <Card className={cn("transition-shadow hover:shadow-md", variantStyles[variant], className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}
