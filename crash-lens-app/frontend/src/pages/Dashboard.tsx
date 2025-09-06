import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  AlertTriangle, 
  TrendingUp, 
  Users, 
  CheckCircle,
  GitBranch
} from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { 
  CrashRateChart, 
  WeeklyTrendChart
} from '@/components/dashboard/CrashChart';
import { ModernSeverityChart } from '@/components/dashboard/ModernSeverityChart';
import { ModernImpactedComponents } from '@/components/dashboard/ModernImpactedComponents';
import { CrashTable } from '@/components/crashes/CrashTable';
import { RepositoryManager } from '@/components/repositories/RepositoryManager';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { mockCrashes, mockRepositories, mockChartData, Repository } from '@/data/mockData';

export default function Dashboard() {
  const [repositories, setRepositories] = useState<Repository[]>(mockRepositories);
  const [selectedRepo, setSelectedRepo] = useState(repositories[0]?.id || '');

  const handleAddRepository = (newRepo: Omit<Repository, 'id'>) => {
    const repository: Repository = {
      ...newRepo,
      id: `repo-${Date.now()}`,
    };
    setRepositories(prev => [...prev, repository]);
  };

  const handleRemoveRepository = (id: string) => {
    setRepositories(prev => prev.filter(repo => repo.id !== id));
    if (selectedRepo === id) {
      const remaining = repositories.filter(repo => repo.id !== id);
      setSelectedRepo(remaining[0]?.id || '');
    }
  };

  const filteredCrashes = mockCrashes.filter(crash => 
    selectedRepo ? crash.repositoryId === selectedRepo : true
  );
  return (
    <div className="flex-1 overflow-auto">
      <div className="p-4 sm:p-6 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              AI-powered crash analysis and monitoring
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <Select value={selectedRepo} onValueChange={setSelectedRepo}>
              <SelectTrigger className="w-full sm:w-48 bg-secondary/50 border-border/30">
                <GitBranch className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Select repository" />
              </SelectTrigger>
              <SelectContent className="bg-card border border-border z-50">
                {repositories.map((repo) => (
                  <SelectItem key={repo.id} value={repo.id}>
                    {repo.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <RepositoryManager
              repositories={repositories}
              onRepositoryAdd={handleAddRepository}
              onRepositoryRemove={handleRemoveRepository}
            />
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Crashes"
            value="46"
            change={{ value: "12%", type: "increase" }}
            icon={AlertTriangle}
          />
          <StatCard
            title="Critical Issues"
            value="8"
            change={{ value: "3%", type: "decrease" }}
            icon={TrendingUp}
          />
          <StatCard
            title="Affected Users"
            value="4.2K"
            change={{ value: "8%", type: "increase" }}
            icon={Users}
          />
          <StatCard
            title="Resolved Today"
            value="12"
            change={{ value: "25%", type: "increase" }}
            icon={CheckCircle}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CrashRateChart data={mockChartData.crashRateByDay} />
          <WeeklyTrendChart data={mockChartData.weeklyTrend} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ModernSeverityChart 
            data={mockChartData.severityDistribution}
          />
          
          <ModernImpactedComponents 
            data={mockChartData.topComponents}
          />
        </div>

        {/* Recent Crashes Table */}
        <CrashTable crashes={filteredCrashes.slice(0, 5)} />
      </div>
    </div>
  );
}