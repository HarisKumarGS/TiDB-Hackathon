import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, 
  Users, 
  Search,
  ExternalLink 
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

interface CrashTableProps {
  crashes: Crash[];
  className?: string;
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

export function CrashTable({ crashes, className }: CrashTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const navigate = useNavigate();

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
