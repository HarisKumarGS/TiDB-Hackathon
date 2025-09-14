import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  AlertTriangle, 
  Zap,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRepository } from '@/contexts/RepositoryContext';

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Crashes', href: '/crashes', icon: AlertTriangle },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { selectedRepository } = useRepository();

  return (
    <motion.div 
      className={cn(
        "relative flex flex-col h-screen glass border-r border-border/30 transition-all duration-300 flex-shrink-0",
        collapsed ? "w-16" : "w-48 sm:w-64"
      )}
      initial={false}
      animate={{ width: collapsed ? 64 : window.innerWidth < 640 ? 192 : 256 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border/30">
        <motion.div 
          className="flex items-center space-x-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-primary">
            <Zap className="w-5 h-5 text-primary-foreground" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="text-lg font-bold gradient-text">CrashLens</h1>
              <p className="text-xs text-muted-foreground">AI Analysis Bot</p>
            </div>
          )}
        </motion.div>
        
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-secondary/50 transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 group",
                "hover:bg-secondary/50 hover-lift",
                isActive
                  ? "bg-primary/10 text-primary border border-primary/20 glow-primary"
                  : "text-muted-foreground hover:text-foreground"
              )
            }
          >
            <item.icon className={cn(
              collapsed ? "w-6 h-6" : "w-5 h-5",
              "transition-transform duration-200 group-hover:scale-110"
            )} />
            {!collapsed && (
              <motion.span 
                className="font-medium"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
              >
                {item.name}
              </motion.span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* AI Status Indicator - Only show when repository status is not pending */}
      {selectedRepository && selectedRepository.status !== 'pending' && (
        <div className="p-4 border-t border-border/30">
          <div className={cn(
            "flex items-center p-3 rounded-lg glass",
            collapsed ? "justify-center" : "space-x-3"
          )}>
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-success/20 flex-shrink-0">
              <div className="w-3 h-3 rounded-full bg-success animate-pulse-slow" />
            </div>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <p className="text-sm font-medium text-success">AI Online</p>
                <p className="text-xs text-muted-foreground">Ready to analyze</p>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}
