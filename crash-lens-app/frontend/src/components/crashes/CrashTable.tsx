import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, 
  Clock, 
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
import { Crash } from '@/data/mockData';
import { cn } from '@/lib/utils';

interface CrashTableProps {
  crashes: Crash[];
  className?: string;
}

const severityColors = {
  Critical: 'bg-destructive/10 text-destructive border-destructive/20',
  High: 'bg-warning/10 text-warning border-warning/20',
  Medium: 'bg-accent/10 text-accent border-accent/20',
  Low: 'bg-success/10 text-success border-success/20'
};

const statusColors = {
  Open: 'bg-destructive/10 text-destructive border-destructive/20',
  'In Progress': 'bg-warning/10 text-warning border-warning/20',
  Resolved: 'bg-success/10 text-success border-success/20',
  Closed: 'bg-muted/10 text-muted-foreground border-muted/20'
};

export function CrashTable({ crashes, className }: CrashTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const navigate = useNavigate();

  const filteredCrashes = crashes.filter(crash => {
    const matchesSearch = 
      crash.component.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crash.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crash.errorType.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSeverity = severityFilter === 'all' || crash.severity === severityFilter;
    const matchesStatus = statusFilter === 'all' || crash.status === statusFilter;
    
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
                <SelectItem value="Critical">Critical</SelectItem>
                <SelectItem value="High">High</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="Low">Low</SelectItem>
              </SelectContent>
            </Select>
          
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-32 bg-secondary/50 border-border/30">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent className="bg-card border border-border z-50">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="Open">Open</SelectItem>
                <SelectItem value="In Progress">In Progress</SelectItem>
                <SelectItem value="Resolved">Resolved</SelectItem>
                <SelectItem value="Closed">Closed</SelectItem>
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
              <TableHead className="whitespace-nowrap">Crash ID</TableHead>
              <TableHead className="whitespace-nowrap">Component</TableHead>
              <TableHead className="whitespace-nowrap hidden sm:table-cell">Error Type</TableHead>
              <TableHead className="whitespace-nowrap">Severity</TableHead>
              <TableHead className="whitespace-nowrap hidden md:table-cell">Status</TableHead>
              <TableHead className="whitespace-nowrap hidden lg:table-cell">Impacted Users</TableHead>
              <TableHead className="whitespace-nowrap hidden xl:table-cell">Timestamp</TableHead>
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
                <TableCell className="font-mono text-xs sm:text-sm">
                  <span className="truncate block max-w-[80px] sm:max-w-none">
                    {crash.id}
                  </span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2 min-w-0">
                    <AlertTriangle className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                    <span className="font-medium truncate">{crash.component}</span>
                  </div>
                </TableCell>
                <TableCell className="font-mono text-xs sm:text-sm hidden sm:table-cell">
                  <span className="truncate block max-w-[100px] lg:max-w-none">
                    {crash.errorType}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge 
                    variant="outline" 
                    className={cn("border text-xs", severityColors[crash.severity])}
                  >
                    {crash.severity}
                  </Badge>
                </TableCell>
                <TableCell className="hidden md:table-cell">
                  <Badge 
                    variant="outline" 
                    className={cn("border text-xs", statusColors[crash.status])}
                  >
                    {crash.status}
                  </Badge>
                </TableCell>
                <TableCell className="hidden lg:table-cell">
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{crash.impactedUsers.toLocaleString()}</span>
                  </div>
                </TableCell>
                <TableCell className="hidden xl:table-cell">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">
                      {new Date(crash.timestamp).toLocaleDateString()}
                    </span>
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