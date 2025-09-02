import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDownIcon, SearchIcon, ExternalLinkIcon, TrendingUpIcon, TrendingDownIcon, UsersIcon, AlertTriangleIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { LineChart, Line, AreaChart, Area, ResponsiveContainer, Tooltip, BarChart, Bar } from "recharts";

interface CrashReport {
  id: string;
  timestamp: string;
  severity: "critical" | "high" | "medium" | "low";
  component: string;
  error: string;
  stackTrace: string;
  affectedUsers: number;
  status: "open" | "investigating" | "resolved";
  eventCount: number;
  userTrend: Array<{ time: string; users: number }>;
  eventTrend: Array<{ time: string; events: number }>;
  firstSeen: string;
  lastSeen: string;
  deviceBreakdown: Array<{ device: string; count: number }>;
  osBreakdown: Array<{ os: string; count: number }>;
}

interface CrashReportsTableProps {
  crashes: CrashReport[];
  onViewDetails: (crashId: string) => void;
}

const severityConfig = {
  critical: { label: "Critical", className: "severity-critical" },
  high: { label: "High", className: "severity-high" },
  medium: { label: "Medium", className: "severity-medium" },
  low: { label: "Low", className: "severity-low" }
};

const MiniChart = ({ data, dataKey, color, type = "line" }: {
  data: Array<any>;
  dataKey: string;
  color: string;
  type?: "line" | "area";
}) => {
  const ChartComponent = type === "area" ? AreaChart : LineChart;
  const DataComponent = type === "area" ? Area : Line;

  return (
    <ResponsiveContainer width="100%" height={40}>
      <ChartComponent data={data}>
        {type === "area" ? (
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            fill={color}
            fillOpacity={0.2}
            strokeWidth={1.5}
          />
        ) : (
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={1.5}
            dot={false}
          />
        )}
      </ChartComponent>
    </ResponsiveContainer>
  );
};

const MetricCard = ({ title, value, trend, color, icon: Icon }: {
  title: string;
  value: string | number;
  trend?: "up" | "down";
  color: string;
  icon: React.ComponentType<any>;
}) => (
  <div className="bg-card/50 border border-border rounded-lg p-3">
    <div className="flex items-center justify-between mb-2">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4" style={{ color }} />
        <span className="text-xs text-muted-foreground">{title}</span>
      </div>
      {trend && (
        trend === "up" ? 
          <TrendingUpIcon className="h-3 w-3 text-destructive" /> : 
          <TrendingDownIcon className="h-3 w-3 text-green-500" />
      )}
    </div>
    <div className="text-lg font-semibold">{value}</div>
  </div>
);

export function CrashReportsTable({ crashes, onViewDetails }: CrashReportsTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const filteredCrashes = crashes.filter(crash =>
    crash.error.toLowerCase().includes(searchTerm.toLowerCase()) ||
    crash.component.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleRow = (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const getTrendDirection = (data: Array<{ time: string; users?: number; events?: number }>, key: 'users' | 'events') => {
    if (data.length < 2) return undefined;
    const last = data[data.length - 1][key] || 0;
    const secondLast = data[data.length - 2][key] || 0;
    return last > secondLast ? "up" : "down";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Crash Reports</CardTitle>
          <div className="relative w-64">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Search crashes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {filteredCrashes.map((crash) => (
            <Collapsible key={crash.id}>
              <div className="border border-border rounded-lg overflow-hidden hover:border-primary/50 transition-colors">
                {/* Header Section */}
                <div className="p-4 bg-card/30">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <CollapsibleTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleRow(crash.id)}
                          className="p-0 h-auto hover:bg-transparent"
                        >
                          <ChevronDownIcon 
                            className={cn(
                              "h-4 w-4 transition-transform duration-200",
                              expandedRows.has(crash.id) && "rotate-180"
                            )} 
                          />
                        </Button>
                      </CollapsibleTrigger>
                      <Badge className={severityConfig[crash.severity].className}>
                        {severityConfig[crash.severity].label}
                      </Badge>
                      <span className="text-sm font-medium">{crash.component}</span>
                      <span className="text-xs text-muted-foreground">#{crash.id}</span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewDetails(crash.id)}
                      className="h-8"
                    >
                      <ExternalLinkIcon className="h-3 w-3 mr-1" />
                      RCA Details
                    </Button>
                  </div>

                  <div className="mb-3">
                    <p className="font-medium text-sm mb-1">{crash.error}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>First: {crash.firstSeen}</span>
                      <span>Last: {crash.lastSeen}</span>
                      <Badge variant={crash.status === "resolved" ? "default" : "secondary"} className="text-xs">
                        {crash.status}
                      </Badge>
                    </div>
                  </div>

                  {/* Metrics Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    <MetricCard
                      title="Affected Users"
                      value={crash.affectedUsers.toLocaleString()}
                      trend={getTrendDirection(crash.userTrend, 'users')}
                      color="hsl(var(--primary))"
                      icon={UsersIcon}
                    />
                    <MetricCard
                      title="Total Events"
                      value={crash.eventCount.toLocaleString()}
                      trend={getTrendDirection(crash.eventTrend, 'events')}
                      color="hsl(var(--destructive))"
                      icon={AlertTriangleIcon}
                    />
                    <MetricCard
                      title="Top Device"
                      value={crash.deviceBreakdown[0]?.device || "N/A"}
                      color="hsl(var(--chart-3))"
                      icon={TrendingUpIcon}
                    />
                    <MetricCard
                      title="Top OS"
                      value={crash.osBreakdown[0]?.os || "N/A"}
                      color="hsl(var(--chart-4))"
                      icon={TrendingUpIcon}
                    />
                  </div>

                  {/* Mini Charts */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium">User Impact Trend</span>
                        <span className="text-xs text-muted-foreground">
                          {crash.userTrend[crash.userTrend.length - 1]?.users || 0} users
                        </span>
                      </div>
                      <MiniChart
                        data={crash.userTrend}
                        dataKey="users"
                        color="hsl(var(--primary))"
                        type="area"
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium">Event Frequency</span>
                        <span className="text-xs text-muted-foreground">
                          {crash.eventTrend[crash.eventTrend.length - 1]?.events || 0} events
                        </span>
                      </div>
                      <MiniChart
                        data={crash.eventTrend}
                        dataKey="events"
                        color="hsl(var(--destructive))"
                        type="line"
                      />
                    </div>
                  </div>
                </div>

                {/* Expandable Content */}
                <CollapsibleContent>
                  <div className="p-4 border-t border-border space-y-4">
                    {/* Device & OS Breakdown */}
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                          <TrendingUpIcon className="h-4 w-4" />
                          Device Breakdown
                        </h4>
                        <div className="space-y-2">
                          {crash.deviceBreakdown.map((device, idx) => (
                            <div key={device.device} className="flex items-center justify-between">
                              <span className="text-sm">{device.device}</span>
                              <div className="flex items-center gap-2">
                                <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-gradient-to-r from-primary to-primary/60 rounded-full"
                                    style={{ 
                                      width: `${(device.count / Math.max(...crash.deviceBreakdown.map(d => d.count))) * 100}%` 
                                    }}
                                  />
                                </div>
                                <span className="text-xs text-muted-foreground min-w-[3rem] text-right">
                                  {device.count.toLocaleString()}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                          <TrendingUpIcon className="h-4 w-4" />
                          OS Breakdown
                        </h4>
                        <div className="space-y-2">
                          {crash.osBreakdown.map((os, idx) => (
                            <div key={os.os} className="flex items-center justify-between">
                              <span className="text-sm">{os.os}</span>
                              <div className="flex items-center gap-2">
                                <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-gradient-to-r from-chart-3 to-chart-3/60 rounded-full"
                                    style={{ 
                                      width: `${(os.count / Math.max(...crash.osBreakdown.map(o => o.count))) * 100}%` 
                                    }}
                                  />
                                </div>
                                <span className="text-xs text-muted-foreground min-w-[3rem] text-right">
                                  {os.count.toLocaleString()}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Stack Trace */}
                    <div>
                      <h4 className="text-sm font-medium mb-2">Stack Trace</h4>
                      <pre className="text-xs bg-muted/50 p-3 rounded-md overflow-x-auto border">
                        <code>{crash.stackTrace}</code>
                      </pre>
                    </div>
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}