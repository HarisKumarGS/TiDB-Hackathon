import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { cn } from '@/lib/utils';

interface ChartProps {
  data: any[];
  className?: string;
}

export function CrashRateChart({ data, className }: ChartProps) {
  if (!data || data.length === 0) {
    return (
      <motion.div
        className={cn("glass p-6 rounded-xl glow-card", className)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h3 className="text-lg font-semibold mb-4 gradient-text">Daily Crash Rate</h3>
        <div className="h-64 flex flex-col items-center justify-center">
          <div className="w-16 h-16 rounded-xl bg-muted/20 flex items-center justify-center mb-4">
            <div className="w-8 h-1 bg-muted/40 rounded" />
          </div>
          <p className="text-muted-foreground text-sm">No crash rate data available</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={cn("glass p-6 rounded-xl glow-card", className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3 className="text-lg font-semibold mb-4 gradient-text">Daily Crash Rate</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="date" 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                boxShadow: 'var(--shadow-card)'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="crashes" 
              stroke="hsl(var(--primary))" 
              strokeWidth={3}
              dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 6 }}
              activeDot={{ r: 8, stroke: 'hsl(var(--primary))', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export function WeeklyTrendChart({ data, className }: ChartProps) {
  if (!data || data.length === 0) {
    return (
      <motion.div
        className={cn("glass p-6 rounded-xl glow-card", className)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h3 className="text-lg font-semibold mb-4 gradient-text">Weekly Trend</h3>
        <div className="h-64 flex flex-col items-center justify-center">
          <div className="flex space-x-2 mb-4">
            <div className="w-6 h-12 bg-muted/20 rounded" />
            <div className="w-6 h-8 bg-muted/30 rounded" />
            <div className="w-6 h-10 bg-muted/20 rounded" />
          </div>
          <p className="text-muted-foreground text-sm">No weekly trend data available</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={cn("glass p-6 rounded-xl glow-card", className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h3 className="text-lg font-semibold mb-4 gradient-text">Weekly Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="week" 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                boxShadow: 'var(--shadow-card)'
              }}
            />
            <Bar 
              dataKey="crashes" 
              fill="hsl(var(--destructive))" 
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="resolved" 
              fill="hsl(var(--success))" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export function SeverityDistributionChart({ data, className }: ChartProps) {
  if (!data || data.length === 0) {
    return (
      <motion.div
        className={cn("glass p-6 rounded-xl glow-card", className)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h3 className="text-lg font-semibold mb-4 gradient-text">Severity Distribution</h3>
        <div className="h-64 flex flex-col items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-muted/20 flex items-center justify-center mb-4">
            <div className="w-8 h-8 rounded-full bg-muted/40" />
          </div>
          <p className="text-muted-foreground text-sm">No severity data available</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={cn("glass p-6 rounded-xl glow-card", className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h3 className="text-lg font-semibold mb-4 gradient-text">Severity Distribution</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={80}
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                boxShadow: 'var(--shadow-card)'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}