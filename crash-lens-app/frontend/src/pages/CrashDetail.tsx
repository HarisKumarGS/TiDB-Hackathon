import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Users, 
  AlertTriangle, 
  Clock, 
  FileText,
  GitBranch,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { CrashActions } from '@/components/crashes/CrashActions';
import { mockCrashDetails } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

const severityColors = {
  Critical: 'bg-destructive/10 text-destructive border-destructive/20',
  High: 'bg-warning/10 text-warning border-warning/20',
  Medium: 'bg-accent/10 text-accent border-accent/20',
  Low: 'bg-success/10 text-success border-success/20'
};

export default function CrashDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [crashStatus, setCrashStatus] = useState<string>('');
  
  const crash = id ? mockCrashDetails[id] : null;

  // Initialize crash status
  if (crash && !crashStatus) {
    setCrashStatus(crash.status);
  }

  const handleStatusUpdate = (status: 'Resolved' | 'Closed', comment?: string) => {
    setCrashStatus(status);
    // Here you would typically call the API to update the crash status
    // apiService.updateCrashStatus(crash.id, status, comment);
  };

  if (!crash) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Crash Not Found</h2>
          <p className="text-muted-foreground mb-4">
            The requested crash analysis could not be found.
          </p>
          <Button onClick={() => navigate('/crashes')}>
            Back to Crashes
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto">
      <div className="p-4 sm:p-6 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row lg:items-center justify-between gap-4"
        >
          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate('/crashes')}
              className="flex-shrink-0"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold gradient-text truncate">
                {crash.id}
              </h1>
            </div>
          </div>
          
          <CrashActions
            crashId={crash.id}
            currentStatus={crashStatus}
            onStatusUpdate={handleStatusUpdate}
          />
        </motion.div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="xl:col-span-3 space-y-6">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <motion.div
                className="glass p-4 rounded-xl glow-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <div className="flex items-center space-x-3">
                  <Users className="w-8 h-8 text-destructive" />
                  <div>
                    <p className="text-sm text-muted-foreground">Impacted Users</p>
                    <p className="text-xl font-bold">{crash.impactedUsers.toLocaleString()}</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                className="glass p-4 rounded-xl glow-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="w-8 h-8 text-warning" />
                  <div>
                    <p className="text-sm text-muted-foreground">Component</p>
                    <p className="text-xl font-bold">{crash.component}</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                className="glass p-4 rounded-xl glow-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 flex items-center justify-center">
                    <Badge 
                      variant="outline" 
                      className={cn("border text-xs", severityColors[crash.severity])}
                    >
                      {crash.severity}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Severity</p>
                    <p className="text-xl font-bold">{crash.severity}</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                className="glass p-4 rounded-xl glow-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <div className="flex items-center space-x-3">
                  <Clock className="w-8 h-8 text-accent" />
                  <div>
                    <p className="text-sm text-muted-foreground">Error Type</p>
                    <p className="text-lg font-bold">{crash.errorType}</p>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Description */}
            <motion.div
              className="glass p-6 rounded-xl glow-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3 className="text-lg font-semibold mb-3 gradient-text">Description</h3>
              <p className="text-muted-foreground leading-relaxed">{crash.description}</p>
              {crash.logfileUrl && (
                <Button variant="outline" className="mt-4">
                  <FileText className="w-4 h-4 mr-2" />
                  View Log File
                </Button>
              )}
            </motion.div>

            {/* RCA Sections */}
            <div className="space-y-6">
              {[
                { title: 'Problem Identification', content: crash.problemIdentification, delay: 0.6 },
                { title: 'Data Collection', content: crash.dataCollection, delay: 0.7 },
                { title: 'Analysis', content: crash.analysis, delay: 0.8 },
                { title: 'Root Cause Identification', content: crash.rootCause, delay: 0.9 },
                { title: 'Solution', content: crash.solution, delay: 1.0 }
              ].map((section) => (
                <motion.div
                  key={section.title}
                  className="glass p-6 rounded-xl glow-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: section.delay }}
                >
                  <h3 className="text-lg font-semibold mb-3 gradient-text">
                    {section.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {section.content}
                  </p>
                </motion.div>
              ))}
            </div>

            {/* Changes Required */}
            <motion.div
              className="glass p-6 rounded-xl glow-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.1 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold gradient-text">Changes Required</h3>
                <Button className="bg-gradient-primary hover:opacity-90">
                  <GitBranch className="w-4 h-4 mr-2" />
                  Create Pull Request
                </Button>
              </div>
              <p className="text-muted-foreground mb-4">{crash.changesRequired}</p>
              
              {/* Git Diff */}
              <div className="bg-secondary/20 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                <pre className="whitespace-pre-wrap">{crash.gitDiff}</pre>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="xl:col-span-1 space-y-6">
            {/* Author */}
            <motion.div
              className="glass p-6 rounded-xl glow-card"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3 className="text-lg font-semibold mb-4 gradient-text">Author</h3>
              <div className="flex items-center space-x-3">
                <Avatar>
                  <AvatarImage src={crash.author.avatar} />
                  <AvatarFallback>{crash.author.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{crash.author.name}</p>
                  <p className="text-sm text-muted-foreground">{crash.author.email}</p>
                </div>
              </div>
            </motion.div>

            {/* Stakeholders */}
            <motion.div
              className="glass p-6 rounded-xl glow-card"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h3 className="text-lg font-semibold mb-4 gradient-text">Stakeholders</h3>
              <div className="space-y-3">
                {crash.stakeholders.map((stakeholder, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{stakeholder.name}</p>
                      <p className="text-sm text-muted-foreground">{stakeholder.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Supporting Documents */}
            <motion.div
              className="glass p-6 rounded-xl glow-card"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
            >
              <h3 className="text-lg font-semibold mb-4 gradient-text">Supporting Documents</h3>
              <div className="space-y-3">
                {crash.supportingDocs.map((doc, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{doc.title}</p>
                      <p className="text-sm text-muted-foreground">{doc.type}</p>
                    </div>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}