import { motion } from 'framer-motion';
import { EventPlanResult } from '@/types/event';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  MapPin, 
  Calendar, 
  Users, 
  DollarSign, 
  Clock,
  Building2,
  Star,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Download,
  RotateCcw,
  Mic,
  UtensilsCrossed,
  Sparkles,
  Music,
  MessageSquare,
  FileText,
  Utensils,
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { BudgetChart } from './BudgetChart';
import { ScheduleTimeline } from './ScheduleTimeline';
import { EventMap } from './EventMap';
import { ExportMenu } from './ExportMenu';
import { ChatPanel } from './ChatPanel';

interface ResultsViewProps {
  result: EventPlanResult;
  onStartOver: () => void;
  originalWorkflowResult?: any; // The full workflow result from backend
  onPlanUpdate?: (updatedWorkflowResult: any) => void; // Callback when plan is updated
}

export function ResultsView({ result, onStartOver, originalWorkflowResult, onPlanUpdate }: ResultsViewProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    venues: true,
    budget: true,
    schedule: true,
    speakers: false,
    catering: false,
    activities: false,
    entertainment: false,
    communication: false,
    finalPlan: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  // Helper function to format speaker fee with dollar sign
  const formatFee = (fee: string | undefined): string => {
    if (!fee || fee === 'TBD' || fee === 'N/A' || fee === '') return fee || 'TBD';
    const str = String(fee);
    // If it already starts with $, return as is
    if (str.startsWith('$')) return str;
    // If it's a number or numeric string, add $
    const num = parseFloat(str.replace(/[^0-9.-]/g, ''));
    if (!isNaN(num)) {
      // Format with commas for thousands
      return `$${num.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
    }
    return str;
  };

  // Helper function to validate URL before using in href
  const isValidUrl = (url: string | undefined): boolean => {
    if (!url) return false;
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-6xl mx-auto px-4 pb-12"
    >
      {/* Header Actions */}
      <motion.div variants={itemVariants} className="flex justify-between items-center mb-8">
        <h2 className="text-3xl md:text-4xl font-display font-bold text-foreground">
          Your Event Plan
        </h2>
        <div className="flex gap-3">
          <Button variant="outline" size="sm" onClick={onStartOver}>
            <RotateCcw className="w-4 h-4" />
            Start Over
          </Button>
          <ExportMenu
            calendarFile={result.exports?.calendarFile}
            pdfFile={result.exports?.pdfFile}
            formUrl={result.exports?.formUrl}
            logoFile={result.exports?.logoFile}
          />
        </div>
      </motion.div>

      {/* Event Summary Header */}
      <motion.div variants={itemVariants}>
        <Card variant="gradient" className="mb-8 overflow-hidden">
          <CardContent className="p-0">
            <div className="grid grid-cols-1 lg:grid-cols-2">
              {/* Event Info */}
              <div className="p-8 relative">
                {/* Logo in top-right corner */}
                {result.exports?.logoFile && result.exports.logoFile !== 'Error' && (() => {
                  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                  const filePath = result.exports.logoFile.replace(/^event_outputs[\/\\]/, '');
                  const logoUrl = `${API_BASE_URL}/api/files/${encodeURIComponent(filePath)}`;
                  return (
                    <div className="absolute top-4 right-4 z-10">
                      <img 
                        src={logoUrl} 
                        alt="Event Logo" 
                        className="h-16 w-16 object-contain rounded-lg bg-background/50 p-1 shadow-sm"
                      />
                    </div>
                  );
                })()}
                <Badge className="mb-4 bg-primary/10 text-primary border-primary/20">
                  {result.eventDetails.type}
                </Badge>
                <h1 className="text-3xl md:text-4xl font-display font-bold text-foreground mb-4">
                  {result.eventDetails.name}
                </h1>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-5 h-5 text-primary" />
                    <span>{result.eventDetails.date}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="w-5 h-5 text-primary" />
                    <span>{result.eventDetails.time}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <MapPin className="w-5 h-5 text-primary" />
                    <span>{result.eventDetails.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Users className="w-5 h-5 text-primary" />
                    <span>{result.eventDetails.guestCount} guests</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground col-span-2">
                    <DollarSign className="w-5 h-5 text-primary" />
                    <span>{result.eventDetails.budget}</span>
                  </div>
                </div>
              </div>
              {/* Map */}
              <div className="h-64 lg:h-auto min-h-[250px] relative z-0">
                <EventMap 
                  location={result.eventDetails.location} 
                  coords={result.eventDetails.coords}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Planning Phase */}
      <motion.div variants={itemVariants}>
        <Card variant="glass" className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              Planning Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">{result.planningPhase.analysis}</p>
            <div>
              <h4 className="font-semibold mb-2">Special Considerations</h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {result.planningPhase.specialConsiderations.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Collapsible Sections */}
      <div className="space-y-4">
        {/* Venues */}
        <motion.div variants={itemVariants}>
          <CollapsibleSection
            title="Venue Recommendations"
            icon={<Building2 className="w-5 h-5 text-primary" />}
            isOpen={expandedSections.venues}
            onToggle={() => toggleSection('venues')}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {result.venues.map((venue, i) => (
                <Card key={i} variant="elevated" className="overflow-hidden">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold">{venue.name}</h4>
                      <div className="flex items-center gap-1 text-gold">
                        <Star className="w-4 h-4 fill-current" />
                        <span className="text-sm">{venue.rating}</span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{venue.location}</p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {venue.features.slice(0, 3).map((f, j) => (
                        <Badge key={j} variant="secondary" className="text-xs">
                          {f}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-primary">{venue.priceRange}</span>
                      {venue.link && isValidUrl(venue.link) && (
                        <a
                          href={venue.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-accent hover:underline flex items-center gap-1 text-sm"
                        >
                          Visit <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CollapsibleSection>
        </motion.div>

        {/* Budget */}
        <motion.div variants={itemVariants}>
          <CollapsibleSection
            title="Budget Breakdown"
            icon={<DollarSign className="w-5 h-5 text-primary" />}
            isOpen={expandedSections.budget}
            onToggle={() => toggleSection('budget')}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BudgetChart breakdown={result.budget.breakdown} total={result.budget.total} />
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Budget Scenarios</h4>
                  <ul className="space-y-2">
                    {result.budget.scenarios.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground p-2 bg-muted/50 rounded-lg">
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
                {result.budget.warnings.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-gold" />
                      Warnings
                    </h4>
                    <ul className="space-y-1">
                      {result.budget.warnings.map((w, i) => (
                        <li key={i} className="text-sm text-muted-foreground">
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </CollapsibleSection>
        </motion.div>

        {/* Schedule */}
        {result.schedule && result.schedule.length > 0 && (
          <motion.div variants={itemVariants}>
            <CollapsibleSection
              title="Event Schedule"
              icon={<Clock className="w-5 h-5 text-primary" />}
              isOpen={expandedSections.schedule}
              onToggle={() => toggleSection('schedule')}
            >
              <ScheduleTimeline schedule={result.schedule} />
            </CollapsibleSection>
          </motion.div>
        )}

        {/* Speakers */}
        {result.speakers && result.speakers.length > 0 && (
          <motion.div variants={itemVariants}>
            <CollapsibleSection
              title="Speakers"
              icon={<Mic className="w-5 h-5 text-primary" />}
              isOpen={expandedSections.speakers}
              onToggle={() => toggleSection('speakers')}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.speakers.map((speaker, i) => (
                <Card key={i} variant="elevated">
                  <CardContent className="p-4 flex gap-4">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center shrink-0">
                      <Mic className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-semibold">{speaker.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {speaker.title}, {speaker.company}
                      </p>
                      <p className="text-sm mt-1">{speaker.topic}</p>
                      <Badge variant="secondary" className="mt-2">
                        {formatFee(speaker.fee)}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CollapsibleSection>
        </motion.div>
        )}

        {/* Catering */}
        {result.catering && result.catering.menuPreview && result.catering.menuPreview.length > 0 && (
        <motion.div variants={itemVariants}>
          <CollapsibleSection
            title="Catering"
            icon={<UtensilsCrossed className="w-5 h-5 text-primary" />}
            isOpen={expandedSections.catering}
            onToggle={() => toggleSection('catering')}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3">Menu Preview</h4>
                <ul className="space-y-2">
                  {result.catering.menuPreview.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <Utensils className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Dietary Options</h4>
                <div className="flex flex-wrap gap-2 mb-4">
                  {result.catering.dietaryOptions.map((opt, i) => (
                    <Badge key={i} variant="secondary">
                      {opt}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">
                  Estimated Cost: <span className="font-medium text-primary">{result.catering.estimatedCost}</span>
                </p>
              </div>
            </div>
          </CollapsibleSection>
        </motion.div>
        )}

        {/* Activities */}
        {result.activities && result.activities.length > 0 && (
        <motion.div variants={itemVariants}>
          <CollapsibleSection
            title="Activities"
            icon={<Sparkles className="w-5 h-5 text-primary" />}
            isOpen={expandedSections.activities}
            onToggle={() => toggleSection('activities')}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.activities.map((activity, i) => (
                <Card key={i} variant="elevated">
                  <CardContent className="p-4">
                    <h4 className="font-semibold mb-1">{activity.name}</h4>
                    <p className="text-sm text-muted-foreground mb-2">{activity.description}</p>
                    <Badge variant="secondary">{activity.duration}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CollapsibleSection>
        </motion.div>
        )}

        {/* Entertainment */}
        {result.entertainment && result.entertainment.length > 0 && (
          <motion.div variants={itemVariants}>
            <CollapsibleSection
              title="Entertainment"
              icon={<Music className="w-5 h-5 text-primary" />}
              isOpen={expandedSections.entertainment}
              onToggle={() => toggleSection('entertainment')}
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {result.entertainment.map((item, i) => (
                  <Card key={i} variant="elevated">
                    <CardContent className="p-4 text-center">
                      <div className="w-12 h-12 mx-auto rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-3">
                        <Music className="w-5 h-5 text-primary" />
                      </div>
                      <h4 className="font-semibold mb-1">{item.type}</h4>
                      <p className="text-sm text-muted-foreground mb-2">{item.description}</p>
                      <Badge variant="secondary">{item.cost}</Badge>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CollapsibleSection>
          </motion.div>
        )}

        {/* Communication */}
        {result.communication && result.communication.timeline && result.communication.timeline.length > 0 && (
          <motion.div variants={itemVariants}>
            <CollapsibleSection
              title="Communication Plan"
              icon={<MessageSquare className="w-5 h-5 text-primary" />}
              isOpen={expandedSections.communication}
              onToggle={() => toggleSection('communication')}
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Timeline</h4>
                  <div className="space-y-3">
                    {result.communication.timeline.map((item, i) => (
                    <div key={i} className="flex gap-3 items-start">
                      <div className="w-2 h-2 rounded-full bg-primary mt-2 shrink-0" />
                      <div>
                        <p className="text-sm font-medium">{item.date}</p>
                        <p className="text-sm text-muted-foreground">{item.action}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Channels</h4>
                <div className="flex flex-wrap gap-2 mb-4">
                  {result.communication.channels.map((ch, i) => (
                    <Badge key={i} variant="secondary">
                      {ch}
                    </Badge>
                  ))}
                </div>
                <h4 className="font-semibold mb-3">Key Messages</h4>
                <ul className="space-y-2">
                  {result.communication.keyMessages.map((msg, i) => (
                    <li key={i} className="text-sm text-muted-foreground p-2 bg-muted/50 rounded-lg">
                      {msg}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CollapsibleSection>
        </motion.div>
        )}

        {/* Final Plan */}
        <motion.div variants={itemVariants}>
          <CollapsibleSection
            title="Final Plan"
            icon={<FileText className="w-5 h-5 text-primary" />}
            isOpen={expandedSections.finalPlan}
            onToggle={() => toggleSection('finalPlan')}
          >
            <div className="space-y-6">
              <div>
                <h4 className="font-semibold mb-2">Executive Summary</h4>
                <p className="text-muted-foreground">{result.finalPlan.executiveSummary}</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {result.finalPlan.timeline && result.finalPlan.timeline.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3">Timeline</h4>
                    <div className="space-y-2">
                      {result.finalPlan.timeline.map((item, i) => (
                        <div key={i} className="flex gap-3 items-start text-sm">
                          <CheckCircle2 className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="font-semibold mb-3">Risks & Mitigations</h4>
                  <div className="space-y-3">
                    {result.finalPlan.risks.map((item, i) => (
                      <div key={i} className="p-3 bg-muted/50 rounded-lg">
                        <p className="text-sm font-medium flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-gold" />
                          {item.risk}
                        </p>
                        <p className="text-sm text-muted-foreground mt-1 ml-6">
                          {item.mitigation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-3">Action Items</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2 font-medium">Task</th>
                        <th className="text-left p-2 font-medium">Owner</th>
                        <th className="text-left p-2 font-medium">Deadline</th>
                        <th className="text-left p-2 font-medium">Priority</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.finalPlan.actionItems.map((item, i) => (
                        <tr key={i} className="border-b border-border/50">
                          <td className="p-2">{item.task}</td>
                          <td className="p-2 text-muted-foreground">{item.owner}</td>
                          <td className="p-2 text-muted-foreground">{item.deadline}</td>
                          <td className="p-2">
                            <Badge
                              variant={
                                item.priority === 'high'
                                  ? 'destructive'
                                  : item.priority === 'medium'
                                  ? 'default'
                                  : 'secondary'
                              }
                            >
                              {item.priority}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </CollapsibleSection>
        </motion.div>
      </div>

      {/* Chat Panel for Plan Refinement */}
      {originalWorkflowResult && onPlanUpdate && (
        <motion.div variants={itemVariants} className="mt-8">
          <ChatPanel
            currentPlan={result}
            originalWorkflowResult={originalWorkflowResult}
            onPlanUpdate={(updatedWorkflowResult) => {
              // Call the parent's update handler
              if (onPlanUpdate) {
                onPlanUpdate(updatedWorkflowResult);
              }
            }}
          />
        </motion.div>
      )}
    </motion.div>
  );
}

interface CollapsibleSectionProps {
  title: string;
  icon: React.ReactNode;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function CollapsibleSection({ title, icon, isOpen, onToggle, children }: CollapsibleSectionProps) {
  return (
    <Collapsible open={isOpen} onOpenChange={onToggle}>
      <Card variant="glass">
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/30 transition-colors">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {icon}
                {title}
              </CardTitle>
              {isOpen ? (
                <ChevronUp className="w-5 h-5 text-muted-foreground" />
              ) : (
                <ChevronDown className="w-5 h-5 text-muted-foreground" />
              )}
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent>{children}</CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}
