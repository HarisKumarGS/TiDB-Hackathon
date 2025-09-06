import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, GitBranch, Trash2, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Repository } from '@/data/mockData';

interface RepositoryManagerProps {
  repositories: Repository[];
  onRepositoryAdd: (repository: Omit<Repository, 'id'>) => void;
  onRepositoryRemove: (id: string) => void;
}

export function RepositoryManager({ 
  repositories, 
  onRepositoryAdd, 
  onRepositoryRemove 
}: RepositoryManagerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const parseGitHubUrl = (url: string) => {
    try {
      const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/);
      if (!match) throw new Error('Invalid GitHub URL');
      
      return {
        owner: match[1],
        name: match[2].replace('.git', '')
      };
    } catch {
      throw new Error('Please enter a valid GitHub repository URL');
    }
  };

  const handleAddRepository = async () => {
    if (!repoUrl.trim()) return;

    setIsLoading(true);
    try {
      const { owner, name } = parseGitHubUrl(repoUrl);
      
      // Check if repository already exists
      const exists = repositories.some(repo => repo.url === repoUrl);
      if (exists) {
        toast({
          title: "Repository already exists",
          description: "This repository is already being monitored.",
          variant: "destructive"
        });
        return;
      }

      const newRepo = {
        name,
        url: repoUrl,
        owner,
        crashCount: 0,
        lastCrash: new Date().toISOString()
      };

      onRepositoryAdd(newRepo);
      
      toast({
        title: "Repository added successfully",
        description: `${owner}/${name} is now being monitored for crashes.`,
      });

      setRepoUrl('');
      setIsOpen(false);
    } catch (error) {
      toast({
        title: "Failed to add repository",
        description: error instanceof Error ? error.message : "Invalid repository URL",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveRepository = (id: string, name: string) => {
    onRepositoryRemove(id);
    toast({
      title: "Repository removed",
      description: `${name} has been removed from monitoring.`,
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gradient-primary hover:opacity-90">
          <Plus className="w-4 h-4 mr-2" />
          Add Repository
        </Button>
      </DialogTrigger>
        <DialogContent className="glass max-w-md sm:max-w-lg mx-4">
          <DialogHeader>
          <DialogTitle className="gradient-text">Add GitHub Repository</DialogTitle>
          <DialogDescription>
            Add a GitHub repository to monitor for crashes and analyze with AI.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="repo-url">Repository URL</Label>
            <Input
              id="repo-url"
              placeholder="https://github.com/owner/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="bg-secondary/50 border-border/30"
            />
          </div>
          
          {repositories.length > 0 && (
            <div className="space-y-2">
              <Label>Current Repositories</Label>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {repositories.map((repo) => (
                  <motion.div
                    key={repo.id}
                    className="flex items-center justify-between p-2 rounded-lg bg-secondary/20"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <div className="flex items-center space-x-2">
                      <GitBranch className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-medium">{repo.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {repo.crashCount} crashes
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(repo.url, '_blank')}
                      >
                        <ExternalLink className="w-3 h-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveRepository(repo.id, repo.name)}
                      >
                        <Trash2 className="w-3 h-3 text-destructive" />
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleAddRepository}
            disabled={!repoUrl.trim() || isLoading}
            className="bg-gradient-primary hover:opacity-90"
          >
            {isLoading ? 'Adding...' : 'Add Repository'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}