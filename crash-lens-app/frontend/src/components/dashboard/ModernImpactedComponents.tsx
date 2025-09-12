import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, Zap, Activity, Users } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ComponentData {
  component: string;
  crashes: number;
  percentage?: number; // Optional for backward compatibility
}

interface ModernComponentsProps {
  data: ComponentData[];
  className?: string;
}

const componentIcons = {
  'UserAuth': AlertTriangle,
  'PaymentProcessor': TrendingUp,
  'DataSync': Activity,
  'ImageUpload': Zap,
  'LocationService': AlertTriangle,
  'PAYMENT SERVICE': TrendingUp,
  'AUTH SERVICE': AlertTriangle,
  'DATA SERVICE': Activity,
  'NOTIFICATION SERVICE': Zap,
  'USER SERVICE': Users,
  'ORDER SERVICE': Activity,
  'INVENTORY SERVICE': AlertTriangle,
};

export function ModernImpactedComponents({ data, className }: ModernComponentsProps) {
  // Empty state
  if (!data || data.length === 0) {
    return (
      <motion.div
        className={cn("glass p-3 sm:p-4 rounded-xl glow-card h-[500px] flex flex-col", className)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4">
          <h3 className="text-lg font-semibold gradient-text mb-2 sm:mb-0">
            Most Impacted Components
          </h3>
        </div>
        <div className="flex flex-col items-center justify-center py-8">
          <div className="w-12 h-12 rounded-lg bg-muted/20 flex items-center justify-center mb-3">
            <Activity className="w-6 h-6 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground text-sm text-center">No component data available</p>
        </div>
      </motion.div>
    );
  }

  const maxCrashes = Math.max(...data.map(d => d.crashes));

  return (
    <motion.div
      className={cn("glass p-3 sm:p-4 rounded-xl glow-card h-[500px] flex flex-col", className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      whileHover={{ scale: 1.01 }}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4">
        <h3 className="text-lg font-semibold gradient-text mb-2 sm:mb-0">
          Most Impacted Components
        </h3>
        <motion.div 
          className="flex items-center space-x-2 px-2 sm:px-3 py-1 rounded-full bg-primary/10 self-start"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <Activity className="w-3 h-3 sm:w-4 sm:h-4 text-primary" />
          <span className="text-xs sm:text-sm text-primary font-medium">Live</span>
        </motion.div>
      </div>
      
      <div className="space-y-2 flex-grow overflow-y-auto">
        {data.slice(0, 3).map((component, index) => {
          const IconComponent = componentIcons[component.component as keyof typeof componentIcons] || Activity;
          // Use API-provided percentage if available, otherwise calculate from max crashes
          const percentage = component.percentage !== undefined 
            ? component.percentage 
            : (component.crashes / maxCrashes) * 100;
          
          return (
            <motion.div
              key={component.component}
              className="group p-2 sm:p-3 rounded-lg bg-secondary/10 hover:bg-secondary/20 transition-all duration-300 cursor-pointer border border-transparent hover:border-primary/20"
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 + index * 0.15 }}
              whileHover={{ 
                scale: 1.02, 
                x: 8,
                boxShadow: "0 10px 25px rgba(0,0,0,0.1)" 
              }}
            >
              <div className="flex items-center justify-between mb-2 sm:mb-3">
                <div className="flex items-center space-x-2 sm:space-x-3 min-w-0">
                  <motion.div 
                    className="p-1.5 sm:p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors flex-shrink-0"
                    whileHover={{ rotate: 5, scale: 1.1 }}
                  >
                    <IconComponent className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                  </motion.div>
                  <div className="min-w-0">
                    <span className="font-medium text-foreground group-hover:text-primary transition-colors text-sm sm:text-base truncate block">
                      {component.component}
                    </span>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <span className="text-xs sm:text-sm text-muted-foreground">
                        {component.crashes} crashes
                      </span>
                      <motion.div
                        className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-destructive"
                        animate={{ 
                          scale: [1, 1.3, 1],
                          opacity: [0.5, 1, 0.5] 
                        }}
                        transition={{ 
                          duration: 2, 
                          repeat: Infinity,
                          delay: index * 0.3 
                        }}
                      />
                    </div>
                  </div>
                </div>
                
                <motion.div 
                  className="text-right flex-shrink-0"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 + index * 0.1 }}
                >
                  <div className="text-sm sm:text-lg font-bold text-destructive">
                    {percentage.toFixed(0)}%
                  </div>
                  <div className="text-xs text-muted-foreground hidden sm:block">
                    impact
                  </div>
                </motion.div>
              </div>
              
              {/* Animated Progress Bar */}
              <div className="relative">
                <div className="w-full h-1.5 sm:h-2 bg-muted/20 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-destructive via-warning to-primary rounded-full relative"
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ 
                      delay: 1.2 + index * 0.1, 
                      duration: 1,
                      ease: "easeOut" 
                    }}
                  >
                    <motion.div
                      className="absolute inset-0 bg-white/20 rounded-full"
                      animate={{ 
                        x: ['0%', '100%', '0%'] 
                      }}
                      transition={{ 
                        duration: 2, 
                        repeat: Infinity,
                        delay: 2 + index * 0.2 
                      }}
                    />
                  </motion.div>
                </div>
                
                {/* Floating Impact Indicator */}
                <motion.div
                  className="absolute -top-0.5 sm:-top-1 right-0 w-3 h-3 sm:w-4 sm:h-4 bg-destructive rounded-full border-2 border-background"
                  style={{ right: `${100 - percentage}%` }}
                  animate={{ 
                    scale: [1, 1.2, 1],
                    boxShadow: ["0 0 0 0 rgba(239, 68, 68, 0.7)", "0 0 0 10px rgba(239, 68, 68, 0)", "0 0 0 0 rgba(239, 68, 68, 0.7)"]
                  }}
                  transition={{ 
                    duration: 2, 
                    repeat: Infinity,
                    delay: 1.5 + index * 0.3 
                  }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>
      
      {/* AI Insights Footer */}
      <motion.div
        className="mt-4 p-3 sm:p-4 rounded-lg bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/10"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2 }}
      >
        <div className="flex items-start sm:items-center space-x-2">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            className="flex-shrink-0 mt-0.5 sm:mt-0"
          >
            <Zap className="w-3 h-3 sm:w-4 sm:h-4 text-primary" />
          </motion.div>
          <span className="text-xs sm:text-sm text-muted-foreground leading-tight">
            <span className="text-primary font-medium">AI Analysis:</span> Critical Issues Found
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
}