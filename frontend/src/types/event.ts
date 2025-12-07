export interface EventFormData {
  eventType: string;
  customEventType?: string;
  eventName: string;
  dateType: 'single' | 'range';
  eventDate: string;
  endDate?: string;
  startTime?: string;
  endTime?: string;
  locationPreference: string;
  locationCoords?: { lat: number; lng: number };
  budgetMin: number;
  budgetMax: number;
  guestCountMin: number;
  guestCountMax: number;
  specialRequirements: string;
  enableSandbox?: boolean;
  enableSMS?: boolean;
}

export type AgentStatus = 'pending' | 'active' | 'completed';

export interface Agent {
  id: string;
  name: string;
  icon: string;
  status: AgentStatus;
  message: string;
  progress: number;
}

export type AppState = 'landing' | 'form' | 'processing' | 'results';

export interface VenueRecommendation {
  name: string;
  location: string;
  capacity: string;
  priceRange: string;
  rating: number;
  features: string[];
  link?: string;
}

export interface BudgetItem {
  category: string;
  amount: number;
  percentage: number;
  notes: string;
}

export interface ScheduleItem {
  time: string;
  title: string;
  duration: string;
  type: 'keynote' | 'session' | 'break' | 'networking' | 'meal' | 'activity';
  location?: string;
  speaker?: string;
  date?: string; // Date or day (e.g., "2026-06-15" or "Day 1")
  startTime?: string; // For sorting (HH:MM format)
  endTime?: string; // For sorting (HH:MM format)
}

export interface Speaker {
  name: string;
  title: string;
  company: string;
  topic: string;
  fee: string;
  image?: string;
}

export interface EventPlanResult {
  eventDetails: {
    name: string;
    type: string;
    date: string;
    time: string;
    location: string;
    coords?: { lat: number; lng: number };
    guestCount: string;
    budget: string;
  };
  planningPhase: {
    analysis: string;
    requiredAgents: string[];
    executionRationale: string;
    specialConsiderations: string[];
  };
  venues: VenueRecommendation[];
  budget: {
    total: number;
    breakdown: BudgetItem[];
    scenarios: string[];
    warnings: string[];
  };
  schedule: ScheduleItem[];
  speakers: Speaker[];
  catering: {
    menuPreview: string[];
    dietaryOptions: string[];
    estimatedCost: string;
  };
  activities: {
    name: string;
    description: string;
    duration: string;
  }[];
  entertainment: {
    type: string;
    description: string;
    cost: string;
  }[];
  communication: {
    timeline: { date: string; action: string }[];
    channels: string[];
    keyMessages: string[];
  };
  finalPlan: {
    executiveSummary: string;
    timeline: string[];
    risks: { risk: string; mitigation: string }[];
    actionItems: { task: string; owner: string; deadline: string; priority: 'high' | 'medium' | 'low' }[];
  };
  exports?: {
    calendarFile?: string;
    pdfFile?: string;
    formUrl?: string;
  };
  success: boolean;
}

export interface WorkflowResult {
  event_details?: Record<string, unknown>;
  planning_phase?: unknown;
  specialist_outputs?: Record<string, unknown>;
  final_plan?: unknown;
  calendar_invite?: unknown;
  registration_form?: Record<string, unknown>;
  pdf_report?: string | null;
  agents_used?: string[];
  success?: boolean;
  pdf_generated?: boolean;
}

export interface PlanApiResponse {
  status: string;
  event_details?: Record<string, unknown>;
  result: WorkflowResult;
}
