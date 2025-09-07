import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, GitBranch } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CrashTable } from '@/components/crashes/CrashTable';
import { RepositoryManager } from '@/components/repositories/RepositoryManager';
import { Repository, Crash } from '@/data/mockData';
import { apiService } from '@/services/apiService';

export default function CrashList() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [isLoadingRepos, setIsLoadingRepos] = useState(true);
  const [repoError, setRepoError] = useState<string | null>(null);
  const [crashes, setCrashes] = useState<Crash[]>([]);
  const [isLoadingCrashes, setIsLoadingCrashes] = useState(false);
  const [crashError, setCrashError] = useState<string | null>(null);

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
            <h1 className="text-3xl font-bold gradient-text">Crash Analysis</h1>
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

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            className="glass p-6 rounded-xl glow-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Crashes</p>
                <p className="text-2xl font-bold mt-1">
                  {isLoadingCrashes ? "..." : (filteredCrashes.length || 0)}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-destructive" />
            </div>
          </motion.div>

          <motion.div
            className="glass p-6 rounded-xl glow-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Critical</p>
                <p className="text-2xl font-bold mt-1 text-destructive">
                  {isLoadingCrashes ? "..." : (filteredCrashes.filter(c => c.severity?.toLowerCase() === 'critical').length || 0)}
                </p>
              </div>
              <div className="w-8 h-8 rounded-full bg-destructive/20 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-destructive" />
              </div>
            </div>
          </motion.div>

          <motion.div
            className="glass p-6 rounded-xl glow-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Open Issues</p>
                <p className="text-2xl font-bold mt-1 text-warning">
                  {isLoadingCrashes ? "..." : (filteredCrashes.filter(c => c.status?.toLowerCase() === 'open').length || 0)}
                </p>
              </div>
              <div className="w-8 h-8 rounded-full bg-warning/20 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-warning" />
              </div>
            </div>
          </motion.div>

          <motion.div
            className="glass p-6 rounded-xl glow-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Resolved</p>
                <p className="text-2xl font-bold mt-1 text-success">
                  {isLoadingCrashes ? "..." : (filteredCrashes.filter(c => c.status?.toLowerCase() === 'resolved').length || 0)}
                </p>
              </div>
              <div className="w-8 h-8 rounded-full bg-success/20 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-success" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Crashes Table */}
        {isLoadingCrashes ? (
          <div className="flex items-center justify-center p-8">
            <div className="text-muted-foreground">Loading crashes...</div>
          </div>
        ) : crashError ? (
          <div className="flex items-center justify-center p-8">
            <div className="text-red-500">{crashError}</div>
          </div>
        ) : (
          <CrashTable crashes={filteredCrashes} />
        )}
      </div>
    </div>
  );
}