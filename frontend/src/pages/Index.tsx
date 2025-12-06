import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useMutation } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { LandingPage } from '@/components/LandingPage';
import { EventForm } from '@/components/EventForm';
import { AgentProgressView } from '@/components/AgentProgressView';
import { ResultsView } from '@/components/ResultsView';
import { StepIndicator } from '@/components/StepIndicator';
import { DevMenu, DevSettings } from '@/components/DevMenu';
import { AppState, Agent, EventFormData, EventPlanResult, PlanApiResponse } from '@/types/event';
import { initialAgents, agentMessages } from '@/lib/mockData';
import { useToast } from '@/hooks/use-toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

type JsonRecord = Record<string, any>;

const safeParse = <T,>(value: unknown): T | null => {
  if (!value) return null;
  if (typeof value !== 'string') return value as T;

  // Only attempt to parse if the string looks like JSON
  const trimmed = value.trim();
  if (!(trimmed.startsWith('{') || trimmed.startsWith('['))) return null;

  // Strip markdown fences and control chars that break JSON.parse
  const cleaned = trimmed
    .replace(/^```json\s*/i, '')
    .replace(/```\s*$/, '')
    .replace(/[\u0000-\u001F]+/g, '');

  try {
    const parsed = JSON.parse(cleaned) as T;
    console.log('✅ safeParse success:', cleaned.substring(0, 100));
    return parsed;
  } catch (error) {
    console.warn('❌ safeParse failed for:', cleaned.substring(0, 120), error);
    return null;
  }
};

const firstArray = (candidates: unknown[]): any[] | undefined => {
  return candidates.find((item) => Array.isArray(item)) as any[] | undefined;
};

const asArray = (value: unknown): any[] => {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
};

const mapWorkflowToEventResult = (response: PlanApiResponse, formData?: EventFormData): EventPlanResult => {
  const workflow = response.result || {};

  const parseJson = <T,>(value: unknown): T | null => {
    if (typeof value === 'string') return safeParse<T>(value);
    if (value && typeof value === 'object') return value as T;
    return null;
  };

  const finalPlan = parseJson<JsonRecord>(workflow.final_plan) || {};

  const specialistOutputs: JsonRecord = Object.fromEntries(
    Object.entries(workflow.specialist_outputs || {}).map(([key, value]) => {
      const parsed = parseJson<JsonRecord>(value);
      return [key, parsed ?? value];
    })
  );

  const planningPhase = parseJson<JsonRecord>(workflow.planning_phase) || {};
  const eventDetailsSource = parseJson<JsonRecord>(workflow.event_details) || {};

  const budgetingData = parseJson<JsonRecord>(specialistOutputs?.budgeting) || {};
  const schedulingData = parseJson<JsonRecord>(specialistOutputs?.scheduling) || {};
  const venueData = parseJson<JsonRecord>(specialistOutputs?.venue) || {};
  const programmeData = parseJson<JsonRecord>(specialistOutputs?.programme) || {};
  const speakersData = parseJson<JsonRecord>(specialistOutputs?.speakers) || {};
  const cateringData = parseJson<JsonRecord>(specialistOutputs?.catering) || {};
  const activitiesData = parseJson<JsonRecord>(specialistOutputs?.activities) || {};
  const entertainmentData = parseJson<JsonRecord>(specialistOutputs?.entertainment) || {};
  const communicationData = parseJson<JsonRecord>(specialistOutputs?.communication) || {};

  const budgetRange = formData
    ? `$${formData.budgetMin.toLocaleString()} - $${formData.budgetMax.toLocaleString()}`
    : (eventDetailsSource?.budget_range as string | undefined) || 'Budget TBD';

  const eventDetails = {
    name: formData?.eventName || (finalPlan.event_name as string) || (eventDetailsSource?.event_name as string) || 'Your Event',
    type:
      (formData?.eventType === 'Other' ? formData.customEventType : formData?.eventType) ||
      (finalPlan.event_type as string) ||
      (eventDetailsSource?.event_type as string) ||
      'Event',
    date:
      (formData?.endDate ? `${formData.eventDate} to ${formData.endDate}` : formData?.eventDate) ||
      (eventDetailsSource?.event_date as string) ||
      'Date TBD',
    time:
      (eventDetailsSource?.time_window as string) ||
      (finalPlan.schedule?.event_hours as string) ||
      (formData?.startTime && formData?.endTime ? `${formData.startTime} - ${formData.endTime}` : 'Time TBD'),
    location:
      formData?.locationPreference || (finalPlan.location as string) || (eventDetailsSource?.location_preference as string) || 'Location TBD',
    coords: (finalPlan.coords as EventPlanResult['eventDetails']['coords']) || (eventDetailsSource?.coords as any),
    guestCount:
      (eventDetailsSource?.guest_count as string) ||
      (formData ? `${formData.guestCountMin}-${formData.guestCountMax}` : 'Guest count TBD'),
    budget: budgetRange,
  } as EventPlanResult['eventDetails'];

  const venueCandidates = firstArray([
    finalPlan?.recommendations?.venue?.venues,
    venueData?.venues,
    programmeData?.programme_recommendations?.options,
  ]) || [];

  const venues = venueCandidates.map((item) => ({
    name: item.name || item.option || 'Venue',
    location: item.location || item.address || eventDetails.location,
    capacity: String(item.capacity || 'N/A'),
    priceRange: item.priceRange || item.estimated_cost || item.cost || 'TBD',
    rating: Number(item.rating) || 0,
    features: asArray(item.amenities || item.features),
    link: item.website || item.link || item.url,
  }));

  const budgetBreakdowns = budgetingData.major_category_breakdowns || {};
  const breakdown = Object.entries(budgetBreakdowns).map(([category, data]: [string, any]) => ({
    category: category.charAt(0).toUpperCase() + category.slice(1),
    amount: Number(data?.recommended_spend || data?.amount || 0),
    percentage: Math.round(Number(data?.pct_of_total || 0)),
    notes: asArray(data?.key_assumptions).join('; '),
  }));

  const budgetTotal = Number(finalPlan?.budget?.total_allocated) || breakdown.reduce((sum, entry) => sum + entry.amount, 0);
  const scenarios = asArray(budgetingData.what_if_scenarios)
    .map((scenario: any) => {
      if (!scenario) return '';
      if (typeof scenario === 'string') return scenario;
      return `${scenario.name || 'Scenario'}: ${scenario.impact || ''} ${scenario.recommendation ? `(${scenario.recommendation})` : ''}`.trim();
    })
    .filter(Boolean);

  const scheduleSessions = firstArray([
    finalPlan?.schedule?.sessions,
    schedulingData?.optimized_schedule,
    programmeData?.programme_recommendations?.daily_schedule,
    programmeData?.daily_schedule,
  ]) || [];

  const schedule = scheduleSessions.map((item: any) => {
    const timeWindow = [item.start_time, item.end_time].filter(Boolean).join(' - ');
    const duration = item.duration ? `${item.duration} min` : item.duration_minutes ? `${item.duration_minutes} min` : '';
    return {
      time: timeWindow || item.time || 'TBD',
      title: item.name || item.session_name || item.title || item.activity || 'Session',
      duration: duration,
      type: (item.type || 'session') as ScheduleItem['type'],
      location: item.room || item.location,
      speaker: item.speaker || item.presenter,
    };
  });

  const speakersSource = firstArray([
    finalPlan?.recommendations?.speakers?.top_speaker_options,
    speakersData?.speakers_recommendations?.top_speaker_options,
  ]) || [];

  const speakers = speakersSource.map((item: any) => ({
    name: item.name || 'Speaker',
    title: item.bio || '',
    company: item.company || '',
    topic: item.ideal_role || item.topic || '',
    fee: String(item.estimated_fee || ''),
    image: item.image,
  }));

  const cateringRec = cateringData?.catering_recommendations || cateringData;
  const cateringSource = cateringRec || {};

  const activitiesSource = firstArray([
    finalPlan?.recommendations?.activities?.recommendations,
    activitiesData?.activity_planning?.recommendations,
  ]) || [];

  const activities = activitiesSource.map((item: any) => ({
    name: item.name || 'Activity',
    description: item.description || '',
    duration: String(item.duration || ''),
  }));

  const entertainmentSource = firstArray([
    finalPlan?.recommendations?.entertainment?.specific_options,
    entertainmentData?.entertainment_recommendations?.specific_options,
  ]) || [];

  const entertainment = entertainmentSource.map((item: any) => ({
    type: item.name || 'Entertainment',
    description: item.description || '',
    cost: String(item.cost_estimate || item.cost || ''),
  }));

  const commRecommendations = communicationData?.communication_recommendations || communicationData || {};
  const communication = {
    timeline: asArray(commRecommendations.timeline || []).map((entry: any) =>
      typeof entry === 'string' ? { date: '', action: entry } : { date: entry.date || '', action: entry.action || entry }
    ),
    channels: asArray(commRecommendations.channels || []),
    keyMessages: asArray(commRecommendations.key_messages || []),
  };

  const timelineItems = asArray(finalPlan?.timeline || []).map((item: any) => {
    if (!item) return 'Timeline item';
    const tasks = asArray(item.tasks || []).join(', ');
    const deadline = item.deadline ? ` (by ${item.deadline})` : '';
    return `${item.phase || 'Phase'}: ${tasks}${deadline}`.trim();
  });

  const risks = asArray(finalPlan?.risks || schedulingData?.conflicts_explained || []).map((item: any) => ({
    risk: item.risk || item.conflict || String(item),
    mitigation: item.mitigation || item.impact || 'Review scheduling constraints',
  }));

  const actionItems = asArray(finalPlan?.action_items || schedulingData?.actionable_suggestions || []).map((item: any, index: number) => ({
    task: item.action || item.task || item.suggestion || String(item),
    owner: item.owner || 'Event Coordinator',
    deadline: item.deadline || 'Before event date',
    priority: (item.priority as 'high' | 'medium' | 'low') || (index < 3 ? 'high' : 'medium'),
  }));

  const executiveSummary = finalPlan?.executive_summary ||
    `${eventDetails.name} is a ${eventDetails.type} scheduled for ${eventDetails.date} at ${eventDetails.location}. ` +
    `Expected attendance: ${eventDetails.guestCount} guests. Budget: ${eventDetails.budget}.` +
    (schedulingData?.status === 'infeasible' ? ` Note: ${schedulingData.message || ''}` : '');

  return {
    eventDetails,
    planningPhase: {
      analysis: (planningPhase?.analysis as string) || executiveSummary,
      requiredAgents: (planningPhase?.required_agents as string[]) || (workflow.agents_used as string[]) || [],
      executionRationale: (planningPhase?.execution_order_rationale as string) || '',
      specialConsiderations: asArray(planningPhase?.special_considerations || []),
    },
    venues,
    budget: {
      total: budgetTotal,
      breakdown,
      scenarios,
      warnings: asArray(budgetingData.warnings || []),
    },
    schedule,
    speakers,
    catering: {
      menuPreview: asArray(cateringSource.menu_overview || []),
      dietaryOptions: asArray(cateringSource.dietary_accommodations || []),
      estimatedCost: cateringSource.budget_estimate?.total || cateringSource.estimated_total || cateringSource.estimatedCost || 'TBD',
    },
    activities,
    entertainment,
    communication,
    finalPlan: {
      executiveSummary,
      timeline: timelineItems,
      risks,
      actionItems,
    },
    success: Boolean(workflow.success ?? true),
  };
};

const Index = () => {
  // Skip to results if VITE_SKIP_TO_RESULTS is set
  const skipToResults = import.meta.env.VITE_SKIP_TO_RESULTS === 'true';
  const [appState, setAppState] = useState<AppState>(skipToResults ? 'processing' : 'landing');
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [eventResult, setEventResult] = useState<EventPlanResult | null>(null);
  const [formData, setFormData] = useState<EventFormData | null>(null);
  const [devSettings, setDevSettings] = useState<DevSettings>({ enableSandbox: false, enableSMS: false });
  const { toast } = useToast();

  // Keep the loading screen active while the backend workflow runs
  useEffect(() => {
    if (appState !== 'processing') return;

    const interval = setInterval(() => {
      setAgents((prev) =>
        prev.map((agent, index) => {
          const messages = agentMessages[agent.id] || ['Working...'];
          const message = messages[(Date.now() / 700 + index) % messages.length | 0];
          const progress = agent.status === 'completed' ? 100 : 50 + ((index % 3) * 10);
          return {
            ...agent,
            status: 'active',
            message,
            progress,
          };
        })
      );
    }, 700);

    return () => clearInterval(interval);
  }, [appState]);

  const planMutation = useMutation<PlanApiResponse, Error, EventFormData>({
    mutationFn: async (payload: EventFormData) => {
      // Use cached result if VITE_USE_CACHED_RESULT is set
      if (import.meta.env.VITE_USE_CACHED_RESULT === 'true') {
        const response = await fetch(`${API_BASE_URL}/api/plan/last`);
        if (response.ok) {
          console.log('Using cached result from last successful run');
          return response.json();
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || 'Planning request failed');
      }

      return response.json();
    },
  });

  // Auto-trigger if skipping to results
  useEffect(() => {
    if (skipToResults && appState === 'processing' && !planMutation.isPending && !eventResult) {
      // Mock form data with realistic values for testing
      const mockFormData: EventFormData = {
        eventType: 'Conference',
        eventName: 'AI Innovation Summit 2026',
        dateType: 'range',
        eventDate: '2026-06-15',
        endDate: '2026-06-17',
        startTime: '09:00',
        endTime: '18:00',
        locationPreference: 'San Francisco, CA',
        budgetMin: 75000,
        budgetMax: 150000,
        guestCountMin: 200,
        guestCountMax: 500,
        specialRequirements: 'Keynote speakers from major AI companies, interactive demo sessions, networking dinner on day 1',
      };
      
      planMutation.mutate(mockFormData, {
        onSuccess: (apiResponse) => {
          const mapped = mapWorkflowToEventResult(apiResponse, mockFormData);
          setEventResult(mapped);
          setAgents((prev) => prev.map((agent) => ({ ...agent, status: 'completed', message: 'Completed', progress: 100 })));
          setAppState('results');
        },
        onError: (error) => {
          console.error(error);
          toast({
            title: 'Failed to load cached result',
            description: error.message || 'Make sure you have run POST /api/plan at least once to populate the cache.',
            variant: 'destructive',
          });
          setAppState('landing');
        },
      });
    }
  }, [skipToResults, appState, planMutation, eventResult, toast]);

  const handleGetStarted = () => {
    setAppState('form');
  };

  const handleFormSubmit = (data: EventFormData) => {
    setFormData(data);
    setEventResult(null);
    setAgents(initialAgents.map((a) => ({ ...a, status: 'pending', message: 'Waiting to start...', progress: 0 })));
    setAppState('processing');

    // Merge dev settings into form data
    const dataWithSettings = { ...data, ...devSettings };

    planMutation.mutate(dataWithSettings, {
      onSuccess: (apiResponse) => {
        const mapped = mapWorkflowToEventResult(apiResponse, data);
        setEventResult(mapped);
        setAgents((prev) => prev.map((agent) => ({ ...agent, status: 'completed', message: 'Completed', progress: 100 })));
        setAppState('results');
      },
      onError: (error) => {
        console.error(error);
        toast({
          title: 'Planning failed',
          description: error.message || 'Unexpected error while running the agents.',
          variant: 'destructive',
        });
        setAgents(initialAgents.map((a) => ({ ...a, status: 'pending', message: 'Waiting to start...', progress: 0 })));
        setAppState('form');
      },
    });
  };

  const handleStartOver = () => {
    setFormData(null);
    setEventResult(null);
    setAgents(initialAgents.map((a) => ({ ...a, status: 'pending', message: 'Waiting to start...', progress: 0 })));
    setAppState('landing');
  };

  // Show landing page without header/footer wrapper
  if (appState === 'landing') {
    return <LandingPage onGetStarted={handleGetStarted} />;
  }

  return (
    <div className="min-h-screen gradient-hero">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-panel border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => setAppState('landing')}
              className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-soft-coral to-rose-gold flex items-center justify-center shadow-glow">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-display font-bold text-foreground">
                EventAI
              </span>
            </button>
            <StepIndicator currentState={appState} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8 md:py-12">
        <AnimatePresence mode="wait">
          {appState === 'form' && (
            <motion.div
              key="form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <EventForm onSubmit={handleFormSubmit} />
            </motion.div>
          )}

          {appState === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <AgentProgressView agents={agents} />
            </motion.div>
          )}

          {appState === 'results' && eventResult && (
            <motion.div
              key="results"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <ResultsView result={eventResult} onStartOver={handleStartOver} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="py-6 border-t border-border/50">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-muted-foreground">
          Powered by AI Agents • Built with love
        </div>
      </footer>

      {/* Dev Menu */}
      <DevMenu onSettingsChange={setDevSettings} />
    </div>
  );
};

export default Index;
