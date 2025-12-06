import { AppState } from '@/types/event';
import { motion } from 'framer-motion';
import { ClipboardList, Cpu, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StepIndicatorProps {
  currentState: AppState;
}

const steps = [
  { id: 'form', label: 'Event Details', icon: ClipboardList },
  { id: 'processing', label: 'AI Planning', icon: Cpu },
  { id: 'results', label: 'Your Plan', icon: CheckCircle },
];

export function StepIndicator({ currentState }: StepIndicatorProps) {
  const currentIndex = steps.findIndex((s) => s.id === currentState);

  return (
    <div className="flex items-center justify-center gap-2 md:gap-4">
      {steps.map((step, index) => {
        const isActive = step.id === currentState;
        const isCompleted = index < currentIndex;
        const Icon = step.icon;

        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center gap-2">
              <motion.div
                className={cn(
                  'step-dot relative',
                  isActive && 'active',
                  isCompleted && 'completed',
                  !isActive && !isCompleted && 'pending'
                )}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                {isActive && (
                  <motion.div
                    className="absolute inset-0 rounded-full bg-primary/30"
                    animate={{ scale: [1, 1.3, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                )}
                <Icon className="w-5 h-5 relative z-10" />
              </motion.div>
              <span
                className={cn(
                  'text-xs font-medium hidden md:block',
                  isActive && 'text-primary',
                  isCompleted && 'text-accent',
                  !isActive && !isCompleted && 'text-muted-foreground'
                )}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  'w-8 md:w-16 h-0.5 mx-2 md:mx-4 rounded-full transition-colors duration-500',
                  index < currentIndex ? 'bg-accent' : 'bg-muted'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
