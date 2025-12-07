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
  // Group schedule by date if dates are available
  const hasDates = schedule.some(item => item.date);
  const groupedSchedule = hasDates
    ? schedule.reduce((groups, item) => {
        const date = item.date || 'Other';
        if (!groups[date]) {
          groups[date] = [];
        }
        groups[date].push(item);
        return groups;
      }, {} as Record<string, typeof schedule>)
    : { 'All Events': schedule };

  // Format date for display
  const formatDate = (dateStr: string) => {
    if (!dateStr || dateStr === 'Other') return dateStr;
    try {
      const date = new Date(dateStr);
      if (!isNaN(date.getTime())) {
        return date.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
      }
    } catch {
      // If parsing fails, return as-is
    }
    return dateStr;
  };

  return (
    <div className="relative">
      {Object.entries(groupedSchedule).map(([date, daySchedule], dayIndex) => (
        <div key={date} className={dayIndex > 0 ? 'mt-8' : ''}>
          {/* Day header */}
          {hasDates && (
            <div className="mb-4 pb-2 border-b border-border">
              <h3 className="text-lg font-semibold text-foreground">
                {formatDate(date)}
              </h3>
            </div>
          )}
          
          <div className="space-y-4">
            {daySchedule.map((item, i) => {
              const config = typeConfig[item.type];
              const Icon = config.icon;
              const isLast = i === daySchedule.length - 1;
              const isLastDay = dayIndex === Object.keys(groupedSchedule).length - 1;

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
                        {item.speaker && item.speaker !== 'N/A' && (
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
                        {item.duration && (
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {item.duration}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
