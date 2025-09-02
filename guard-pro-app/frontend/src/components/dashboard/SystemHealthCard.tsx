import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface SystemHealthCardProps {
  title: string;
  status: "healthy" | "warning" | "critical" | "unknown";
  uptime: number;
  responseTime: number;
  lastCheck: string;
  metrics: {
    cpu: number;
    memory: number;
    errors: number;
  };
  className?: string;
}

const statusConfig = {
  healthy: {
    label: "Healthy",
    className: "status-healthy",
    bgClass: "from-emerald-500/10 to-emerald-600/10 border-emerald-500/20"
  },
  warning: {
    label: "Warning",
    className: "status-warning", 
    bgClass: "from-amber-500/10 to-amber-600/10 border-amber-500/20"
  },
  critical: {
    label: "Critical",
    className: "status-critical",
    bgClass: "from-red-500/10 to-red-600/10 border-red-500/20"
  },
  unknown: {
    label: "Unknown",
    className: "status-unknown",
    bgClass: "from-gray-500/10 to-gray-600/10 border-gray-500/20"
  }
};

export function SystemHealthCard({ 
  title, 
  status, 
  uptime, 
  responseTime, 
  lastCheck, 
  metrics,
  className 
}: SystemHealthCardProps) {
  const config = statusConfig[status];

  return (
    <Card className={cn(
      "dashboard-card bg-gradient-to-br border-2 transition-all duration-300",
      config.bgClass,
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">{title}</CardTitle>
          <Badge className={config.className} variant="secondary">
            {config.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Uptime</p>
            <p className="font-medium">{uptime}%</p>
          </div>
          <div>
            <p className="text-muted-foreground">Response</p>
            <p className="font-medium">{responseTime}ms</p>
          </div>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-muted-foreground">CPU</span>
              <span className="font-medium">{metrics.cpu}%</span>
            </div>
            <Progress value={metrics.cpu} className="h-2" />
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-muted-foreground">Memory</span>
              <span className="font-medium">{metrics.memory}%</span>
            </div>
            <Progress value={metrics.memory} className="h-2" />
          </div>
        </div>

        <div className="pt-2 border-t border-border/50">
          <div className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground">Errors (24h)</span>
            <span className={cn(
              "font-medium",
              metrics.errors > 10 ? "text-red-400" : 
              metrics.errors > 5 ? "text-amber-400" : "text-emerald-400"
            )}>
              {metrics.errors}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Last check: {lastCheck}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}