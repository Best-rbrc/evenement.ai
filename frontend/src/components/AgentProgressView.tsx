import { motion, AnimatePresence } from 'framer-motion';
import { Agent } from '@/types/event';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
  Building2,
  DollarSign,
  Calendar,
  Mic,
  UtensilsCrossed,
  Sparkles,
  Music,
  Clock,
  MessageSquare,
  CalendarCheck,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  Building2,
  DollarSign,
  Calendar,
  Mic,
  UtensilsCrossed,
  Sparkles,
  Music,
  Clock,
  MessageSquare,
  CalendarCheck,
};

interface AgentProgressViewProps {
  agents: Agent[];
}

export function AgentProgressView({ agents }: AgentProgressViewProps) {
  // Check if we're in the initial "orchestrator selecting" phase
  const hasStartedWork = agents.some(a => a.status !== 'pending');
  
  // Only show agents that have been selected (not pending before they start)
  const activeAgents = agents.filter(a => a.status !== 'pending' || hasStartedWork);
  
  const completedCount = activeAgents.filter((a) => a.status === 'completed').length;
  const overallProgress = activeAgents.length > 0 ? (completedCount / activeAgents.length) * 100 : 0;

  return (
    <div className="max-w-4xl mx-auto px-4">
      {/* Show orchestrator phase before any agents are selected */}
      {!hasStartedWork && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12 py-12"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex justify-center mb-8"
          >
            <div className="relative w-32 h-32">
              {/* Rotating ring */}
              <motion.div
                className="absolute inset-0 rounded-full border-4 border-dashed border-primary/30"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              />
              {/* Pulsing core */}
              <motion.div
                className="absolute inset-4 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <motion.div
                  className="w-16 h-16 rounded-full bg-gradient-to-br from-soft-coral to-rose-gold flex items-center justify-center"
                  animate={{ rotate: -360 }}
                  transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
                >
                  <Sparkles className="w-8 h-8 text-primary-foreground" />
                </motion.div>
              </motion.div>
            </div>
          </motion.div>
          
          <h2 className="text-3xl md:text-4xl font-display font-bold text-foreground mb-3">
            Orchestrator is Deciding
          </h2>
          <p className="text-lg text-muted-foreground mb-2">
            Analyzing your event requirements...
          </p>
          <p className="text-base text-muted-foreground/80">
            The orchestrator is choosing which specialized workers are needed for your event.
          </p>
        </motion.div>
      )}

      {/* Show agents once they've been selected */}
      {hasStartedWork && (
        <>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
        <h2 className="text-3xl md:text-4xl font-display font-bold text-foreground mb-4">
          AI Agents at Work
        </h2>
        <p className="text-lg text-muted-foreground mb-6">
          Our specialized agents are collaborating to create your perfect event plan
        </p>
        
        {/* Overall Progress */}
        <div className="max-w-md mx-auto mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">Overall Progress</span>
            <span className="text-sm font-bold text-primary">{Math.round(overallProgress)}%</span>
          </div>
          <Progress value={overallProgress} className="h-3" />
        </div>
        </motion.div>

      {/* Central Animation */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex justify-center mb-10"
      >
        <div className="relative w-48 h-48">
          {/* Rotating ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-dashed border-primary/30"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          />
          {/* Pulsing core */}
          <motion.div
            className="absolute inset-4 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <motion.div
              className="w-24 h-24 rounded-full bg-gradient-to-br from-soft-coral to-rose-gold flex items-center justify-center shadow-glow"
              animate={{ rotate: -360 }}
              transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="w-10 h-10 text-primary-foreground" />
            </motion.div>
          </motion.div>
          {/* Orbiting dots */}
          {[0, 1, 2, 3].map((i) => (
            <motion.div
              key={i}
              className="absolute w-3 h-3 rounded-full bg-accent"
              style={{
                top: '50%',
                left: '50%',
              }}
              animate={{
                x: Math.cos((i * Math.PI) / 2) * 80,
                y: Math.sin((i * Math.PI) / 2) * 80,
                rotate: 360,
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                delay: i * 0.5,
                ease: 'linear',
              }}
            />
          ))}
        </div>
      </motion.div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AnimatePresence mode="popLayout">
          {activeAgents.map((agent, index) => {
            const Icon = iconMap[agent.icon] || Sparkles;
            
            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                layout
              >
                <Card
                  className={cn(
                    'agent-card transition-all duration-500',
                    agent.status === 'pending' && 'pending',
                    agent.status === 'active' && 'active pulse-soft',
                    agent.status === 'completed' && 'completed'
                  )}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      {/* Icon */}
                      <div
                        className={cn(
                          'w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300',
                          agent.status === 'pending' && 'bg-muted',
                          agent.status === 'active' && 'bg-primary/10',
                          agent.status === 'completed' && 'bg-accent/10'
                        )}
                      >
                        {agent.status === 'active' ? (
                          <Loader2
                            className={cn(
                              'w-6 h-6 animate-spin',
                              'text-primary'
                            )}
                          />
                        ) : agent.status === 'completed' ? (
                          <CheckCircle2 className="w-6 h-6 text-accent" />
                        ) : (
                          <Icon
                            className={cn(
                              'w-6 h-6',
                              agent.status === 'pending' && 'text-muted-foreground'
                            )}
                          />
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="font-semibold text-foreground truncate">
                            {agent.name}
                          </h3>
                          <span
                            className={cn(
                              'text-xs font-medium px-2 py-1 rounded-full',
                              agent.status === 'pending' && 'bg-muted text-muted-foreground',
                              agent.status === 'active' && 'bg-primary/10 text-primary',
                              agent.status === 'completed' && 'bg-accent/10 text-accent'
                            )}
                          >
                            {agent.status === 'pending' && 'Pending'}
                            {agent.status === 'active' && 'Working...'}
                            {agent.status === 'completed' && 'Done'}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          {agent.message}
                        </p>
                        {agent.status === 'active' && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="mt-2"
                          >
                            <Progress value={agent.progress} className="h-1.5" />
                          </motion.div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
        </>
      )}
    </div>
  );
}
