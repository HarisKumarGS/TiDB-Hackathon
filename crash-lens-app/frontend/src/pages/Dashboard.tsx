import { useState, useEffect } from 'react';
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
import { Repository, Crash } from '@/data/mockData';
import { apiService } from '@/services/apiService';

export default function Dashboard() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [isLoadingRepos, setIsLoadingRepos] = useState(true);
  const [repoError, setRepoError] = useState<string | null>(null);
  const [crashes, setCrashes] = useState<Crash[]>([]);
  const [isLoadingCrashes, setIsLoadingCrashes] = useState(false);
  const [crashError, setCrashError] = useState<string | null>(null);

  // Placeholder chart data - replace with API data when available
  const chartData = {
    crashRateByDay: [],
    weeklyTrend: [],
    severityDistribution: [],
    topComponents: []
  };

  // Fetch crashes for selected repository
  const fetchCrashes = async (repositoryId?: string) => {
    try {
      setIsLoadingCrashes(true);
      setCrashError(null);
      const crashData = await apiService.getCrashes(repositoryId);
      // Ensure crashData is an array
      const crashesArray = Array.isArray(crashData) ? crashData : [];
      setCrashes(crashesArray);
    } catch (error) {
      console.error('Failed to fetch crashes:', error);
      setCrashError('Failed to load crashes. Please try again later.');
      setCrashes([]);
    } finally {
      setIsLoadingCrashes(false);
    }
  };

  // Fetch repositories on component initialization
  useEffect(() => {
    const fetchRepositories = async () => {
      try {
        setIsLoadingRepos(true);
        setRepoError(null);
        const repos = await apiService.getRepositories();
        setRepositories(repos);
        if (repos.length > 0) {
          setSelectedRepo(repos[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch repositories:', error);
        setRepoError('Failed to load repositories. Please try again later.');
        setRepositories([]);
      } finally {
        setIsLoadingRepos(false);
      }
    };

    fetchRepositories();
  }, []);

  // Fetch crashes when selected repository changes
  useEffect(() => {
    if (selectedRepo) {
      fetchCrashes(selectedRepo);
    } else {
      fetchCrashes(); // Fetch all crashes if no repository selected
    }
  }, [selectedRepo]);

  const handleAddRepository = (newRepo: Repository) => {
    setRepositories(prev => [...prev, newRepo]);
  };

  const handleRemoveRepository = (id: string) => {
    setRepositories(prev => prev.filter(repo => repo.id !== id));
    if (selectedRepo === id) {
      const remaining = repositories.filter(repo => repo.id !== id);
      setSelectedRepo(remaining[0]?.id || '');
    }
  };

  const filteredCrashes = Array.isArray(crashes) ? crashes : [];
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
          </div>
          
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
            <div className="flex flex-col gap-2">
              <Select 
                value={selectedRepo} 
                onValueChange={setSelectedRepo}
                disabled={isLoadingRepos}
              >
                <SelectTrigger className="w-full sm:w-48 bg-secondary/50 border-border/30">
                  <GitBranch className="w-4 h-4 mr-2" />
                  <SelectValue placeholder={isLoadingRepos ? "Loading repositories..." : "Select repository"} />
                </SelectTrigger>
                <SelectContent className="bg-card border border-border z-50">
                  {repositories.map((repo) => (
                    <SelectItem key={repo.id} value={repo.id}>
                      {repo.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {repoError && (
                <p className="text-sm text-yellow-600 dark:text-yellow-400">
                  {repoError}
                </p>
              )}
            </div>
            
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ModernSeverityChart 
            data={chartData.severityDistribution}
          />
          
          <ModernImpactedComponents 
            data={chartData.topComponents}
          />
        </div>

        {/* Recent Crashes Table */}
        {isLoadingCrashes ? (
          <div className="flex items-center justify-center p-8">
            <div className="text-muted-foreground">Loading crashes...</div>
          </div>
        ) : crashError ? (
          <div className="flex items-center justify-center p-8">
            <div className="text-red-500">{crashError}</div>
          </div>
        ) : (
          <CrashTable crashes={filteredCrashes.slice(0, 5)} />
        )}
      </div>
    </div>
  );
}