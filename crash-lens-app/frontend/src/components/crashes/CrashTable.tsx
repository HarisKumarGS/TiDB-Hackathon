import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, 
  Users, 
  Search,
  ExternalLink,
  Zap
} from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Crash } from '@/types';
import { cn } from '@/lib/utils';
import { apiService } from '@/services/apiService';
import { useToast } from '@/hooks/use-toast';

interface CrashTableProps {
  crashes: Crash[];
  className?: string;
  repositoryId?: string;
}

const severityColors = {
  critical: 'bg-destructive/10 text-destructive border-destructive/20',
  high: 'bg-warning/10 text-warning border-warning/20',
  medium: 'bg-accent/10 text-accent border-accent/20',
  low: 'bg-success/10 text-success border-success/20'
};

const statusColors = {
  open: 'bg-destructive/10 text-destructive border-destructive/20',
  'in progress': 'bg-warning/10 text-warning border-warning/20',
  resolved: 'bg-success/10 text-success border-success/20',
  closed: 'bg-muted/10 text-muted-foreground border-muted/20'
};

// Crash scenarios lookup from backend
const CRASH_SCENARIOS = [
  'paystack_timeout',
  'migration_type_mismatch',
  'taskq_oversell',
  'verify_payment_timeout',
  'db_startup_failure',
  'stripe_signature_error'
];

// Log formats
const LOG_FORMATS = ['plain', 'json'];

export function CrashTable({ crashes, className, repositoryId }: CrashTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isSimulating, setIsSimulating] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  console.log(`Repooository ${repositoryId}`)


  const filteredCrashes = crashes.filter(crash => {
    const matchesSearch = 
      crash.component.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (crash.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (crash.error_type || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSeverity = severityFilter === 'all' || crash.severity?.toLowerCase() === severityFilter;
    const matchesStatus = statusFilter === 'all' || crash.status?.toLowerCase() === statusFilter;
    
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const handleRowClick = (crashId: string) => {
    navigate(`/crashes/${crashId}`);
  };

  // Function to generate random values for simulation request
  const generateRandomSimulationData = () => {
    const randomScenario = CRASH_SCENARIOS[Math.floor(Math.random() * CRASH_SCENARIOS.length)];
    const randomFormat = LOG_FORMATS[Math.floor(Math.random() * LOG_FORMATS.length)];
    const randomMinLogs = Math.floor(Math.random() * 200) + 50; // 50-250
    const randomUsersImpacted = Math.floor(Math.random() * 5000) + 100; // 100-5100
    const randomNoJitter = Math.random() < 0.3; // 30% chance of no jitter

    return {
      scenario: randomScenario,
      format: randomFormat,
      min_logs: randomMinLogs,
      no_jitter: randomNoJitter,
      users_impacted: randomUsersImpacted,
      comment: `Simulated crash for testing - ${randomScenario}`
    };
  };

  const handleSimulateCrash = async () => {
    if (!repositoryId) {
      toast({
        title: "No Repository Selected",
        description: "Please select a repository before simulating a crash.",
        variant: "destructive",
      });
      return;
    }

    setIsSimulating(true);
    
    try {
      const simulationData = generateRandomSimulationData();
      
      const response = await apiService.simulateCrash({
        ...simulationData,
        repository_id: repositoryId,
      });

      toast({
        title: "Crash Simulation Started",
        description: `Successfully simulated ${response.scenario} crash`,
        action: (
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/crashes/${response.crash_id}`)}
            className="ml-2"
          >
            View Crash
          </Button>
        ),
      });

    } catch (error) {
      console.error('Error simulating crash:', error);
      toast({
        title: "Simulation Failed",
        description: "Failed to simulate crash. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <motion.div
      className={cn("glass rounded-xl glow-card overflow-hidden", className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-border/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <h3 className="text-lg font-semibold gradient-text">Recent Crashes</h3>
          <Button
            onClick={handleSimulateCrash}
            disabled={isSimulating || !repositoryId}
            className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white border-0"
            size="sm"
          >
            <Zap className="w-4 h-4 mr-2" />
            {isSimulating ? 'Simulating...' : 'Simulate Crash'}
          </Button>
        </div>
        
        {/* Filters */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <div className="relative flex-1 min-w-0">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search crashes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-secondary/50 border-border/30"
            />
          </div>
          
          <div className="flex gap-2">
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-full sm:w-32 bg-secondary/50 border-border/30">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent className="bg-card border border-border z-50">
                <SelectItem value="all">All Severity</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-32 bg-secondary/50 border-border/30">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent className="bg-card border border-border z-50">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in progress">In Progress</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border/30 hover:bg-transparent">
              <TableHead className="whitespace-nowrap">Component</TableHead>
              <TableHead className="whitespace-nowrap">Error Type</TableHead>
              <TableHead className="whitespace-nowrap">Severity</TableHead>
              <TableHead className="whitespace-nowrap hidden md:table-cell">Status</TableHead>
              <TableHead className="whitespace-nowrap">Impacted Users</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredCrashes.map((crash, index) => (
              <motion.tr
                key={crash.id}
                className="border-border/30 hover:bg-secondary/20 cursor-pointer transition-colors"
                onClick={() => handleRowClick(crash.id)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.01 }}
              >
                <TableCell>
                  <div className="flex items-center space-x-2 min-w-0">
                    <AlertTriangle className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                    <span className="font-medium truncate">{crash.component}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-sm font-mono truncate block max-w-[150px] lg:max-w-none">
                    {crash.error_type || 'Unknown'}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge 
                    variant="outline" 
                    className={cn("border text-xs capitalize", severityColors[crash.severity])}
                  >
                    {crash.severity}
                  </Badge>
                </TableCell>
                <TableCell className="hidden md:table-cell">
                  <Badge 
                    variant="outline" 
                    className={cn("border text-xs capitalize", statusColors[crash.status])}
                  >
                    {crash.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{crash.impacted_users?.toLocaleString() || '0'}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm">
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </TableCell>
              </motion.tr>
            ))}
          </TableBody>
        </Table>
      </div>
      
      {filteredCrashes.length === 0 && (
        <div className="p-8 text-center">
          <AlertTriangle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No crashes found matching your criteria</p>
        </div>
      )}
    </motion.div>
  );
}
