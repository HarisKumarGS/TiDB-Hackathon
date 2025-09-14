import { motion } from 'framer-motion';
import { GitBranch, Plus, Zap, Shield, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface EmptyRepositoryStateProps {
  onAddRepository: () => void;
}

export function EmptyRepositoryState({ onAddRepository }: EmptyRepositoryStateProps) {
  const features = [
    {
      icon: Shield,
      title: "AI-Powered Analysis",
      description: "Get intelligent crash analysis and root cause identification"
    },
    {
      icon: BarChart3,
      title: "Real-time Insights",
      description: "Monitor crash trends and severity patterns in real-time"
    },
    {
      icon: Zap,
      title: "Automated Solutions",
      description: "Receive automated fix suggestions"
    }
  ];

  return (
    <div className="flex-1 flex items-center justify-center min-h-screen p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl w-full text-center space-y-8"
      >
        {/* Main Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="relative mx-auto w-32 h-32 mb-8"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-full blur-xl"></div>
          <div className="relative w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <GitBranch className="w-16 h-16 text-white" />
          </div>
        </motion.div>

        {/* Title and Description */}
        <div className="space-y-4">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-bold gradient-text"
          >
            Welcome to CrashLens
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-xl text-muted-foreground max-w-lg mx-auto"
          >
            Start monitoring your repositories for crashes and get AI-powered insights to improve your code quality.
          </motion.p>
        </div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 my-12"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
            >
              <Card className="glass border-border/30 hover:border-border/50 transition-colors">
                <CardContent className="p-6 text-center space-y-4">
                  <div className="mx-auto w-12 h-12 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-lg flex items-center justify-center">
                    <feature.icon className="w-6 h-6 text-blue-500" />
                  </div>
                  <h3 className="font-semibold text-foreground">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="space-y-6"
        >
          <Button
            onClick={onAddRepository}
            size="lg"
            className="bg-gradient-primary hover:opacity-90 px-8 py-3 text-lg font-semibold"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Your First Repository
          </Button>
        </motion.div>
      </motion.div>
    </div>
  );
}
