import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SystemHealthCard } from "@/components/dashboard/SystemHealthCard";
import { MetricsChart } from "@/components/dashboard/MetricsChart";
import { CrashReportsTable } from "@/components/dashboard/CrashReportsTable";
import { useNavigate } from "react-router-dom";

// Mock data for the dashboard
const systemHealthData = [
  {
    title: "Frontend",
    status: "healthy" as const,
    uptime: 99.8,
    responseTime: 120,
    lastCheck: "2 minutes ago",
    metrics: { cpu: 25, memory: 45, errors: 2 }
  },
  {
    title: "Backend",
    status: "warning" as const,
    uptime: 98.5,
    responseTime: 340,
    lastCheck: "1 minute ago", 
    metrics: { cpu: 78, memory: 62, errors: 8 }
  },
  {
    title: "Database",
    status: "healthy" as const,
    uptime: 99.9,
    responseTime: 45,
    lastCheck: "30 seconds ago",
    metrics: { cpu: 35, memory: 55, errors: 0 }
  },
  {
    title: "Cloud Billing",
    status: "critical" as const,
    uptime: 95.2,
    responseTime: 890,
    lastCheck: "5 minutes ago",
    metrics: { cpu: 95, memory: 88, errors: 15 }
  }
];

const crashReports = [
  {
    id: "CR001",
    timestamp: "2024-01-15 14:30:25",
    severity: "critical" as const,
    component: "Backend API",
    error: "Database connection timeout",
    stackTrace: `at DatabaseConnection.connect (db.js:45)\n  at APIHandler.process (api.js:123)\n  at async processRequest (server.js:89)`,
    affectedUsers: 1247,
    status: "investigating" as const,
    eventCount: 8542,
    firstSeen: "2024-01-15 10:15:32",
    lastSeen: "2024-01-15 14:30:25",
    userTrend: [
      { time: "10:00", users: 120 },
      { time: "11:00", users: 245 },
      { time: "12:00", users: 420 },
      { time: "13:00", users: 680 },
      { time: "14:00", users: 1247 }
    ],
    eventTrend: [
      { time: "10:00", events: 245 },
      { time: "11:00", events: 890 },
      { time: "12:00", events: 1540 },
      { time: "13:00", events: 3200 },
      { time: "14:00", events: 8542 }
    ],
    deviceBreakdown: [
      { device: "Mobile", count: 4521 },
      { device: "Desktop", count: 2890 },
      { device: "Tablet", count: 1131 }
    ],
    osBreakdown: [
      { os: "iOS", count: 2890 },
      { os: "Android", count: 3245 },
      { os: "Windows", count: 1654 },
      { os: "macOS", count: 753 }
    ]
  },
  {
    id: "CR002", 
    timestamp: "2024-01-15 13:45:12",
    severity: "high" as const,
    component: "Frontend",
    error: "React component rendering failure",
    stackTrace: `at Component.render (Component.jsx:67)\n  at ReactDOM.render (react-dom.js:234)\n  at App.mount (app.js:12)`,
    affectedUsers: 523,
    status: "open" as const,
    eventCount: 1894,
    firstSeen: "2024-01-15 11:20:15",
    lastSeen: "2024-01-15 13:45:12",
    userTrend: [
      { time: "11:00", users: 45 },
      { time: "12:00", users: 156 },
      { time: "13:00", users: 334 },
      { time: "14:00", users: 523 }
    ],
    eventTrend: [
      { time: "11:00", events: 78 },
      { time: "12:00", events: 345 },
      { time: "13:00", events: 890 },
      { time: "14:00", events: 1894 }
    ],
    deviceBreakdown: [
      { device: "Desktop", count: 1245 },
      { device: "Mobile", count: 434 },
      { device: "Tablet", count: 215 }
    ],
    osBreakdown: [
      { os: "Windows", count: 890 },
      { os: "macOS", count: 567 },
      { os: "iOS", count: 245 },
      { os: "Android", count: 192 }
    ]
  },
  {
    id: "CR003",
    timestamp: "2024-01-15 12:20:08", 
    severity: "medium" as const,
    component: "Billing Service",
    error: "Payment processing failed",
    stackTrace: `at PaymentProcessor.charge (payment.js:156)\n  at BillingService.processPayment (billing.js:78)\n  at OrderHandler.complete (orders.js:234)`,
    affectedUsers: 89,
    status: "resolved" as const,
    eventCount: 234,
    firstSeen: "2024-01-15 09:30:22",
    lastSeen: "2024-01-15 12:20:08",
    userTrend: [
      { time: "09:00", users: 12 },
      { time: "10:00", users: 34 },
      { time: "11:00", users: 56 },
      { time: "12:00", users: 89 }
    ],
    eventTrend: [
      { time: "09:00", events: 23 },
      { time: "10:00", events: 67 },
      { time: "11:00", events: 134 },
      { time: "12:00", events: 234 }
    ],
    deviceBreakdown: [
      { device: "Mobile", count: 156 },
      { device: "Desktop", count: 67 },
      { device: "Tablet", count: 11 }
    ],
    osBreakdown: [
      { os: "Android", count: 98 },
      { os: "iOS", count: 67 },
      { os: "Windows", count: 45 },
      { os: "macOS", count: 24 }
    ]
  }
];

const performanceData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}:00`,
  cpu: Math.floor(Math.random() * 40) + 20,
  memory: Math.floor(Math.random() * 30) + 40,
  responseTime: Math.floor(Math.random() * 200) + 100
}));

export default function Dashboard() {
  const navigate = useNavigate();

  const handleViewCrashDetails = (crashId: string) => {
    navigate(`/rca/${crashId}`);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Observability Dashboard</h1>
            <p className="text-muted-foreground">Monitor your application architecture in real-time</p>
          </div>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="issues">Issues</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {systemHealthData.map((system, index) => (
                <SystemHealthCard key={index} {...system} />
              ))}
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <MetricsChart
                title="CPU Usage"
                description="Average CPU utilization across all services"
                data={performanceData}
                dataKey="cpu"
                color="hsl(var(--chart-1))"
                type="area"
              />
              <MetricsChart
                title="Response Time"
                description="Average API response time in milliseconds"
                data={performanceData}
                dataKey="responseTime"
                color="hsl(var(--chart-2))"
                type="line"
              />
            </div>
          </TabsContent>

          <TabsContent value="issues" className="space-y-6">
            <CrashReportsTable 
              crashes={crashReports}
              onViewDetails={handleViewCrashDetails}
            />
          </TabsContent>

          <TabsContent value="metrics" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <MetricsChart
                title="Memory Usage"
                description="Memory consumption by service"
                data={performanceData}
                dataKey="memory"
                color="hsl(var(--chart-3))"
                type="area"
              />
              <MetricsChart
                title="CPU Utilization"
                description="CPU usage over time"
                data={performanceData}
                dataKey="cpu"
                color="hsl(var(--chart-1))"
                type="line"
              />
              <MetricsChart
                title="Response Times"
                description="API response latency"
                data={performanceData}
                dataKey="responseTime"
                color="hsl(var(--chart-2))"
                type="area"
              />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}