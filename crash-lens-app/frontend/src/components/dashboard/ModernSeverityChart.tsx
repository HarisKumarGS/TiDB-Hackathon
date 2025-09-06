import { motion } from 'framer-motion';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import { cn } from '@/lib/utils';

interface SeverityData {
  name: string;
  value: number;
  color: string;
}

interface ModernSeverityChartProps {
  data: SeverityData[];
  className?: string;
}

const RADIAN = Math.PI / 180;

const renderCustomizedLabel = ({
  cx, cy, midAngle, innerRadius, outerRadius, percent
}: any) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text 
      x={x} 
      y={y} 
      fill="white" 
      textAnchor={x > cx ? 'start' : 'end'} 
      dominantBaseline="central"
      className="text-sm font-bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export function ModernSeverityChart({ data, className }: ModernSeverityChartProps) {
  // Empty state
  if (!data || data.length === 0) {
    return (
      <motion.div
        className={cn("glass p-4 sm:p-6 rounded-xl glow-card overflow-hidden", className)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold gradient-text">Severity Distribution</h3>
        </div>
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-16 h-16 rounded-full bg-muted/20 flex items-center justify-center mb-4">
            <div className="w-8 h-8 rounded-full bg-muted/40" />
          </div>
          <p className="text-muted-foreground text-sm text-center">No crash data available</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={cn("glass p-4 sm:p-6 rounded-xl glow-card overflow-hidden", className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold gradient-text">Severity Distribution</h3>
        <motion.div 
          className="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-primary animate-pulse-slow"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </div>
      
      {/* Center Stats Only */}
      <motion.div 
        className="flex flex-col items-center justify-center mb-4 sm:mb-6 p-6"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="text-3xl sm:text-4xl font-bold text-foreground mb-1">
          {data.reduce((sum, item) => sum + item.value, 0)}
        </div>
        <div className="text-sm text-muted-foreground">
          Total Crashes
        </div>
      </motion.div>

      {/* Interactive Legend */}
      <div className="space-y-2">
        {data.map((item, index) => (
            <motion.div
              key={item.name}
              className="flex items-center justify-between p-2 sm:p-3 rounded-lg glass hover:bg-secondary/20 transition-all duration-200 cursor-pointer group"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 + index * 0.1 }}
              whileHover={{ scale: 1.02, x: 4 }}
            >
              <div className="flex items-center space-x-2 sm:space-x-3">
                <motion.div 
                  className="w-3 h-3 sm:w-4 sm:h-4 rounded-full shadow-lg"
                  style={{ backgroundColor: item.color }}
                  animate={{ 
                    boxShadow: `0 0 20px ${item.color}50` 
                  }}
                  whileHover={{ 
                    scale: 1.2,
                    boxShadow: `0 0 30px ${item.color}80` 
                  }}
                />
                <span className="font-medium group-hover:text-primary transition-colors text-sm sm:text-base">
                  {item.name}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-muted-foreground text-xs sm:text-sm">
                  {item.value}
                </span>
                <motion.div
                  className="w-12 sm:w-16 h-1.5 sm:h-2 bg-muted/20 rounded-full overflow-hidden"
                  initial={{ width: 0 }}
                  animate={{ width: window.innerWidth < 640 ? 48 : 64 }}
                  transition={{ delay: 1 + index * 0.1 }}
                >
                  <motion.div
                    className="h-full rounded-full"
                    style={{ backgroundColor: item.color }}
                    initial={{ width: 0 }}
                    animate={{ 
                      width: `${(item.value / Math.max(...data.map(d => d.value))) * 100}%` 
                    }}
                    transition={{ delay: 1.2 + index * 0.1, duration: 0.8 }}
                  />
                </motion.div>
              </div>
            </motion.div>
        ))}
      </div>
    </motion.div>
  );
}