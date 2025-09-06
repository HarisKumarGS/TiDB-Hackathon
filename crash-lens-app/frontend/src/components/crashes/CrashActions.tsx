import { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
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

interface CrashActionsProps {
  crashId: string;
  currentStatus: string;
  onStatusUpdate: (status: 'Resolved' | 'Closed', comment?: string) => void;
}

export function CrashActions({ crashId, currentStatus, onStatusUpdate }: CrashActionsProps) {
  const [isCommentDialogOpen, setIsCommentDialogOpen] = useState(false);
  const [comment, setComment] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleResolve = async () => {
    setIsLoading(true);
    try {
      onStatusUpdate('Resolved');
      toast({
        title: "Crash Resolved",
        description: "The crash has been marked as resolved successfully.",
      });
    } catch (error) {
      toast({
        title: "Failed to resolve crash",
        description: "Please try again later.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseWithComment = async () => {
    if (!comment.trim()) {
      toast({
        title: "Comment required",
        description: "Please provide a comment before closing the crash.",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      onStatusUpdate('Closed', comment);
      toast({
        title: "Crash Closed",
        description: "The crash has been closed with your comment.",
      });
      setIsCommentDialogOpen(false);
      setComment('');
    } catch (error) {
      toast({
        title: "Failed to close crash",
        description: "Please try again later.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (currentStatus === 'Resolved' || currentStatus === 'Closed') {
    return (
      <motion.div
        className="flex items-center space-x-2 p-4 rounded-lg bg-success/10 border border-success/20"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <CheckCircle className="w-5 h-5 text-success" />
        <span className="text-success font-medium">
          This crash has been {currentStatus.toLowerCase()}
        </span>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="flex items-center space-x-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Dialog open={isCommentDialogOpen} onOpenChange={setIsCommentDialogOpen}>
        <DialogTrigger asChild>
          <Button variant="outline" disabled={isLoading}>
            <MessageSquare className="w-4 h-4 mr-2" />
            Close with Comment
          </Button>
        </DialogTrigger>
        <DialogContent className="glass max-w-md sm:max-w-lg mx-4">
          <DialogHeader>
            <DialogTitle className="gradient-text">Close Crash Report</DialogTitle>
            <DialogDescription>
              Provide a comment explaining why this crash is being closed.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="comment">Comment</Label>
              <Textarea
                id="comment"
                placeholder="Explain the reason for closing this crash report..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="bg-secondary/50 border-border/30 min-h-24"
              />
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setIsCommentDialogOpen(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCloseWithComment}
              disabled={isLoading}
              className="bg-gradient-danger hover:opacity-90"
            >
              {isLoading ? 'Closing...' : 'Close Crash'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Button 
        onClick={handleResolve}
        disabled={isLoading}
        className="bg-gradient-success hover:opacity-90"
      >
        <CheckCircle className="w-4 h-4 mr-2" />
        {isLoading ? 'Resolving...' : 'Mark Resolved'}
      </Button>
    </motion.div>
  );
}