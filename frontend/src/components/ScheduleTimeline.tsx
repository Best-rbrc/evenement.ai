import { ScheduleItem } from '@/types/event';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { Mic, Coffee, Users, UtensilsCrossed, Sparkles, Clock } from 'lucide-react';

interface ScheduleTimelineProps {
  schedule: ScheduleItem[];
}

const typeConfig: Record<
  ScheduleItem['type'],
  { icon: React.ComponentType<{ className?: string }>; color: string; bg: string }
> = {
  keynote: { icon: Mic, color: 'text-primary', bg: 'bg-primary/10' },
  session: { icon: Users, color: 'text-accent', bg: 'bg-accent/10' },
  break: { icon: Coffee, color: 'text-gold', bg: 'bg-gold/10' },
  networking: { icon: Users, color: 'text-sage', bg: 'bg-sage/10' },
  meal: { icon: UtensilsCrossed, color: 'text-rose-gold', bg: 'bg-rose-gold/10' },
  activity: { icon: Sparkles, color: 'text-deep-teal', bg: 'bg-deep-teal/10' },
};

export function ScheduleTimeline({ schedule }: ScheduleTimelineProps) {
  return (
    <div className="relative">
      <div className="space-y-4">
        {schedule.map((item, i) => {
          const config = typeConfig[item.type];
          const Icon = config.icon;
          const isLast = i === schedule.length - 1;

          return (
            <div key={i} className="relative flex gap-4 items-start">
              {/* Timeline line segment - only between items, not through icons */}
              {!isLast && (
                <div
                  className="absolute left-6 top-12 w-0.5 bg-gradient-to-b from-primary via-accent to-sage z-0"
                  style={{ height: 'calc(1rem + 1px)' }}
                />
              )}

              {/* Timeline dot */}
              <div
                className={cn(
                  'w-12 h-12 rounded-xl flex items-center justify-center shrink-0 relative z-10',
                  config.bg
                )}
              >
                <Icon className={cn('w-5 h-5', config.color)} />
              </div>

              {/* Content */}
              <div className="flex-1 pb-4">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <h4 className="font-semibold text-foreground">{item.title}</h4>
                    {item.speaker && (
                      <p className="text-sm text-muted-foreground">Speaker: {item.speaker}</p>
                    )}
                    {item.location && (
                      <p className="text-sm text-muted-foreground">{item.location}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant="secondary" className="font-mono">
                      {item.time}
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.duration}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
