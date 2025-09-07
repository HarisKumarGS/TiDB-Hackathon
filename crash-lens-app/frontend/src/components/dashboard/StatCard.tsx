import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: {
    value: string;
    type: 'increase' | 'decrease';
  };
  icon: LucideIcon;
  className?: string;
}

export function StatCard({ title, value, change, icon: Icon, className }: StatCardProps) {
  return (
    <motion.div
      className={cn(
        "glass p-4 sm:p-6 rounded-xl hover-lift glow-card w-full",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-muted-foreground truncate">{title}</p>
          <motion.p 
            className="text-xl sm:text-2xl font-bold mt-1"
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
          >
            {value}
          </motion.p>
        </div>
        
        <motion.div 
          className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-primary/10 flex-shrink-0"
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <Icon className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
        </motion.div>
      </div>
    </motion.div>
  );
}