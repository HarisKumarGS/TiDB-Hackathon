import { useState } from 'react';
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
import { mockCrashes, mockRepositories, Repository } from '@/data/mockData';

export default function CrashList() {
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
            <h1 className="text-3xl font-bold gradient-text">Crash Analysis</h1>
            <p className="text-muted-foreground mt-1">
              Monitor and analyze application crashes across repositories
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
                <p className="text-2xl font-bold mt-1">{filteredCrashes.length}</p>
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
                  {filteredCrashes.filter(c => c.severity === 'Critical').length}
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
                  {filteredCrashes.filter(c => c.status === 'Open').length}
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
                  {filteredCrashes.filter(c => c.status === 'Resolved').length}
                </p>
              </div>
              <div className="w-8 h-8 rounded-full bg-success/20 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-success" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Crashes Table */}
        <CrashTable crashes={filteredCrashes} />
      </div>
    </div>
  );
}