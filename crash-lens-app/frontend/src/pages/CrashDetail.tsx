import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Users, 
  AlertTriangle, 
  Clock, 
  FileText,
  GitBranch,
  ExternalLink,
  Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { CrashActions } from '@/components/crashes/CrashActions';
import { CrashDetail as CrashDetailType, ApiCrashDetailResponse } from '@/types';
import { apiService } from '@/services/apiService';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';


const severityColors = {
  critical: 'bg-destructive/10 text-destructive border-destructive/20',
  high: 'bg-warning/10 text-warning border-warning/20',
  medium: 'bg-accent/10 text-accent border-accent/20',
  low: 'bg-success/10 text-success border-success/20'
};

export default function CrashDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [crash, setCrash] = useState<CrashDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [crashStatus, setCrashStatus] = useState<string>('');

  // Fetch crash details from API
  useEffect(() => {
    const fetchCrashDetail = async () => {
      if (!id) {
        setError('No crash ID provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const apiResponse = await apiService.getCrashDetail(id);
        
        // Debug log to see the actual API response structure
        console.log('API Response:', apiResponse);
        
        // Check if the response has the expected nested structure
        if (!apiResponse.data || !apiResponse.data.crash) {
          throw new Error('Invalid API response structure: missing crash data');
        }
        
        // Extract crash and RCA data from the nested response structure
        const crashInfo = apiResponse.data.crash;
        const rcaInfo = apiResponse.data.rca;
        
        // Map API response to frontend interface
        const crashData: CrashDetailType = {
          id: crashInfo.id,
          repository_id: '', // Not provided in API response
          created_at: crashInfo.created_at,
          severity: crashInfo.severity || 'medium',
          status: crashInfo.status || 'open',
          component: crashInfo.component || 'Unknown',
          error_type: crashInfo.error_type || 'Unknown',
          description: rcaInfo?.description || '',
          impacted_users: crashInfo.impacted_users || 0,
          updated_at: crashInfo.updated_at,
          error_log: crashInfo.error_log,
          comment: crashInfo.comment,
          
          // RCA fields - map from snake_case to camelCase
          problemIdentification: rcaInfo?.problem_identification || '',
          dataCollection: rcaInfo?.data_collection || '',
          analysis: '', // Not provided in API response
          rootCause: rcaInfo?.root_cause_identification || '',
          solution: rcaInfo?.solution || '',
          changesRequired: '', // Not provided in API response
          gitDiff: '', // Not provided in API response
          
          // Optional fields with defaults
          author: rcaInfo?.author || null,
          stakeholders: [], // Not provided in API response
          supportingDocs: rcaInfo?.supporting_documents ? 
            rcaInfo.supporting_documents.map((doc: string) => ({
              title: doc,
              url: '#',
              type: 'Document'
            })) : []
        };
        
        setCrash(crashData);
        setCrashStatus(crashData.status);
      } catch (err) {
        console.error('Failed to fetch crash details:', err);
        setError(err instanceof Error ? err.message : 'Failed to load crash details');
        toast({
          title: 'Error',
          description: 'Failed to load crash details. Please try again.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCrashDetail();
  }, [id, toast]);

  const handleStatusUpdate = async (status: 'Resolved' | 'Closed', comment?: string) => {
    if (!crash) return;

    try {
      await apiService.updateCrashStatus(crash.id, status, comment);
      setCrashStatus(status);
      toast({
        title: 'Success',
        description: `Crash status updated to ${status}`,
      });
    } catch (err) {
      console.error('Failed to update crash status:', err);
      toast({
        title: 'Error',
        description: 'Failed to update crash status. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleViewLogFile = () => {
    if (!crash?.error_log) {
      toast({
        title: 'No Log File',
        description: 'No error log file is available for this crash.',
        variant: 'destructive',
      });
      return;
    }

    try {
      // Create a blob with the log content
      const blob = new Blob([crash.error_log], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      
      // Create a temporary link element and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `crash-${crash.id}-error.log`;
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast({
        title: 'Success',
        description: 'Log file downloaded successfully.',
      });
    } catch (err) {
      console.error('Failed to download log file:', err);
      toast({
        title: 'Error',
        description: 'Failed to download log file. Please try again.',
        variant: 'destructive',
      });
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-muted-foreground mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold mb-2">Loading Crash Details</h2>
          <p className="text-muted-foreground">
            Please wait while we fetch the crash analysis...
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !crash) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">
            {error ? 'Error Loading Crash' : 'Crash Not Found'}
          </h2>
          <p className="text-muted-foreground mb-4">
            {error || 'The requested crash analysis could not be found.'}
          </p>
          <div className="space-x-2">
            <Button onClick={() => navigate('/crashes')}>
              Back to Crashes
            </Button>
            {error && (
              <Button variant="outline" onClick={() => window.location.reload()}>
                Try Again
              </Button>
            )}
          </div>
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
              <h1 className="text-xl sm:text-xl font-bold gradient-text truncate">
                {crash.component} : {crash.error_type}
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
                  <div>
                    <p className="text-sm text-muted-foreground">Impacted Users</p>
                    <p className="text-md font-bold">{crash.impacted_users?.toLocaleString() || '0'}</p>
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
                  <div>
                    <p className="text-sm text-muted-foreground">Component</p>
                    <p className="text-md font-bold">{crash.component}</p>
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
                  <div>
                    <p className="text-sm text-muted-foreground">Severity</p>
                    <p className="text-md font-bold capitalize">{crash.severity}</p>
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
                  <div>
                    <p className="text-sm text-muted-foreground">Error Type</p>
                    <p className="text-md font-bold">{crash.error_type}</p>
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
              {crash.error_log && (
                <Button variant="outline" className="mt-4" onClick={handleViewLogFile}>
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
                { title: 'Root Cause Identification', content: crash.rootCause, delay: 0.9 },
                { title: 'Solution', content: crash.solution, delay: 1.0 }
              ].filter(section => section.content).map((section) => (
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
            {(crash.changesRequired || crash.gitDiff) && (
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
                {crash.changesRequired && (
                  <p className="text-muted-foreground mb-4">{crash.changesRequired}</p>
                )}
                
                {/* Git Diff */}
                {crash.gitDiff && (
                  <div className="bg-secondary/20 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                    <pre className="whitespace-pre-wrap">{crash.gitDiff}</pre>
                  </div>
                )}
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="xl:col-span-1 space-y-6">
            {/* Author */}
            {crash.author && (
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
                    <AvatarFallback>
                      {crash.author.name ? crash.author.name.split(' ').map(n => n[0]).join('') : 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{crash.author.name || 'Unknown'}</p>
                    <p className="text-sm text-muted-foreground">{crash.author.email || 'No email'}</p>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Stakeholders */}
            {crash.stakeholders && crash.stakeholders.length > 0 && (
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
                        <p className="font-medium">{stakeholder.name || 'Unknown'}</p>
                        <p className="text-sm text-muted-foreground">{stakeholder.role || 'No role'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Supporting Documents */}
            {crash.supportingDocs && crash.supportingDocs.length > 0 && (
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
                        <p className="font-medium">{doc.title || 'Untitled'}</p>
                        <p className="text-sm text-muted-foreground">{doc.type || 'Document'}</p>
                      </div>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
