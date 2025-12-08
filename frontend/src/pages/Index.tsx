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

// Map backend agent names to frontend agent definitions
const agentDefinitions: Record<string, { name: string; icon: string }> = {
  venue: { name: 'Venue Agent', icon: 'Building2' },
  budgeting: { name: 'Budgeting Agent', icon: 'DollarSign' },
  budget: { name: 'Budgeting Agent', icon: 'DollarSign' },
  programme: { name: 'Programme Agent', icon: 'Calendar' },
  speakers: { name: 'Speakers Agent', icon: 'Mic' },
  catering: { name: 'Catering Agent', icon: 'UtensilsCrossed' },
  activities: { name: 'Activities Agent', icon: 'Sparkles' },
  entertainment: { name: 'Entertainment Agent', icon: 'Music' },
  scheduling: { name: 'Scheduling Agent', icon: 'Clock' },
  communication: { name: 'Communication Agent', icon: 'MessageSquare' },
  calendar: { name: 'Calendar Agent', icon: 'CalendarCheck' },
  form: { name: 'Registration Form Agent', icon: 'FileText' },
  logo: { name: 'Logo Agent', icon: 'Image' },
};

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

  // Frontend now relies ONLY on final_plan - all specialist data should be in final_plan.recommendations
  const planningPhase = parseJson<JsonRecord>(workflow.planning_phase) || {};
  const eventDetailsSource = parseJson<JsonRecord>(workflow.event_details) || {};

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
    coords: formData?.locationCoords || (finalPlan.coords as EventPlanResult['eventDetails']['coords']) || (eventDetailsSource?.coords as any),
    guestCount:
      (eventDetailsSource?.guest_count as string) ||
      (formData ? `${formData.guestCountMin}-${formData.guestCountMax}` : 'Guest count TBD'),
    budget: budgetRange,
  } as EventPlanResult['eventDetails'];

  // Use only final_plan.recommendations.venue - no fallbacks
  const venueCandidates = asArray(finalPlan?.recommendations?.venue?.venues) || [];

  // Helper function to format prices with $ symbol
  const formatPrice = (value: any): string => {
    if (!value || value === 'TBD' || value === 'N/A' || value === '') return 'TBD';
    
    const str = String(value).trim();
    
    // If it already starts with $, clean it up and return formatted
    if (str.startsWith('$')) {
      // Remove $ and parse
      const cleaned = str.substring(1).replace(/[^0-9.,-]/g, '');
      // Handle ranges like "$25,000-$100,000" or "$25,000,100,000" (malformed)
      if (cleaned.includes('-')) {
        const parts = cleaned.split('-').map(p => p.replace(/,/g, ''));
        const nums = parts.map(p => parseFloat(p)).filter(n => !isNaN(n));
        if (nums.length === 2) {
          return `$${nums[0].toLocaleString('en-US')} - $${nums[1].toLocaleString('en-US')}`;
        }
      }
      // Handle malformed commas like "$25,000,100,000" -> treat as range if reasonable
      const parts = cleaned.split(',').filter(p => p.length > 0);
      if (parts.length > 2) {
        // Likely malformed, try to extract meaningful numbers
        const nums = parts.map(p => parseFloat(p.replace(/,/g, ''))).filter(n => !isNaN(n) && n > 0);
        if (nums.length >= 2) {
          // Take first and last as range
          return `$${nums[0].toLocaleString('en-US')} - $${nums[nums.length - 1].toLocaleString('en-US')}`;
        }
      }
      // Single value with $, clean and format
      const num = parseFloat(cleaned.replace(/,/g, ''));
      if (!isNaN(num) && num > 0) {
        return `$${num.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
      }
      return str; // Return original if parsing fails
    }
    
    // Handle ranges without $ like "25,000-100,000"
    if (str.includes('-')) {
      const parts = str.split('-').map(p => p.trim().replace(/[^0-9.,]/g, ''));
      const nums = parts.map(p => parseFloat(p.replace(/,/g, ''))).filter(n => !isNaN(n));
      if (nums.length === 2) {
        return `$${nums[0].toLocaleString('en-US')} - $${nums[1].toLocaleString('en-US')}`;
      }
    }
    
    // If it's a number or numeric string, add $
    const num = parseFloat(str.replace(/[^0-9.-]/g, ''));
    if (!isNaN(num) && num > 0) {
      // Format with commas for thousands
      return `$${num.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
    }
    
    // If it contains text like "per day" or other descriptors, try to extract numbers
    const numMatch = str.match(/([\d,]+(?:\.\d+)?)/g);
    if (numMatch && numMatch.length > 0) {
      const firstNum = parseFloat(numMatch[0].replace(/,/g, ''));
      if (!isNaN(firstNum) && firstNum > 0) {
        // Try to preserve context if it's a range or has descriptors
        if (str.toLowerCase().includes('per day') || str.toLowerCase().includes('per event')) {
          const rangeMatch = str.match(/([\d,]+(?:\.\d+)?)\s*[-–]\s*\$?([\d,]+(?:\.\d+)?)/i);
          if (rangeMatch) {
            const min = parseFloat(rangeMatch[1].replace(/,/g, ''));
            const max = parseFloat(rangeMatch[2].replace(/,/g, ''));
            if (!isNaN(min) && !isNaN(max)) {
              return `$${min.toLocaleString('en-US')} - $${max.toLocaleString('en-US')} per day`;
            }
          }
          return `$${firstNum.toLocaleString('en-US')} per day`;
        }
        return `$${firstNum.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
      }
    }
    
    // Return original string if we can't parse it
    return str;
  };

  // Helper function to validate and clean URLs
  const cleanUrl = (url: any): string | undefined => {
    if (!url || typeof url !== 'string') return undefined;
    
    // Trim whitespace
    let cleaned = url.trim();
    
    // If empty or just whitespace, return undefined
    if (!cleaned || cleaned === '' || cleaned === 'N/A' || cleaned === 'TBD') return undefined;
    
    // Remove any URL encoding artifacts that shouldn't be there
    // Decode first to handle double-encoding
    try {
      cleaned = decodeURIComponent(cleaned);
    } catch (e) {
      // If decoding fails, use original
    }
    
    // Check if it's already a valid URL
    try {
      const urlObj = new URL(cleaned);
      // If it's a valid URL, return it
      return urlObj.href;
    } catch (e) {
      // Not a valid URL, try to fix it
    }
    
    // If it starts with http:// or https:// but still invalid, return undefined
    if (cleaned.startsWith('http://') || cleaned.startsWith('https://')) {
      // Try to fix common issues
      cleaned = cleaned.replace(/\s+/g, ''); // Remove all whitespace
      try {
        const urlObj = new URL(cleaned);
        return urlObj.href;
      } catch (e) {
        return undefined; // Still invalid, skip it
      }
    }
    
    // If it looks like a domain (contains . but no protocol), try adding https://
    if (cleaned.includes('.') && !cleaned.includes(' ')) {
      // Remove any leading slashes
      cleaned = cleaned.replace(/^\/+/, '');
      // Add https:// if no protocol
      if (!cleaned.startsWith('http://') && !cleaned.startsWith('https://')) {
        cleaned = 'https://' + cleaned;
        try {
          const urlObj = new URL(cleaned);
          return urlObj.href;
        } catch (e) {
          return undefined;
        }
      }
    }
    
    // If it contains spaces or looks like plain text, it's not a valid URL
    if (cleaned.includes(' ') || cleaned.length < 4) {
      return undefined;
    }
    
    // Last resort: return undefined for anything that doesn't look like a URL
    return undefined;
  };

  const venues = venueCandidates.map((item) => ({
    name: item.name || item.option || 'Venue',
    location: item.location || item.address || eventDetails.location,
    capacity: String(item.capacity || 'N/A'),
    priceRange: formatPrice(item.priceRange || item.estimated_cost || item.cost || 'TBD'),
    rating: Number(item.rating) || 0,
    features: asArray(item.amenities || item.features),
    link: cleanUrl(item.website || item.link || item.url),
  }));

  // Extract budget breakdown - use ONLY final_plan.budget.by_category
  let budgetBreakdowns: Record<string, any> = {};
  
  if (finalPlan?.budget?.by_category && typeof finalPlan.budget.by_category === 'object') {
    budgetBreakdowns = finalPlan.budget.by_category;
  }
  
  // Also check final_plan.recommendations.budgeting for detailed breakdown if needed
  if (!budgetBreakdowns || Object.keys(budgetBreakdowns).length === 0) {
    const budgetingRec = finalPlan?.recommendations?.budgeting;
    // Fallback to detailed breakdown from recommendations if simple breakdown is empty
    if (budgetingRec?.major_category_breakdowns && typeof budgetingRec.major_category_breakdowns === 'object') {
      // Convert nested structure to simple dict
      Object.entries(budgetingRec.major_category_breakdowns).forEach(([category, data]: [string, any]) => {
        if (data && typeof data === 'object' && typeof data.recommended_spend === 'number') {
          budgetBreakdowns[category] = data.recommended_spend;
        }
      });
    }
  }
  
  // Calculate total for percentages
  const breakdownTotal = Object.values(budgetBreakdowns).reduce((sum: number, value: any) => {
    if (typeof value === 'number') return sum + value;
    if (typeof value === 'string') {
      const num = parseFloat(value.replace(/[^0-9.]/g, ''));
      return sum + (isNaN(num) ? 0 : num);
    }
    if (value && typeof value === 'object' && typeof value.recommended_spend === 'number') {
      return sum + value.recommended_spend;
    }
    return sum;
  }, 0);
  
  const breakdown = Object.entries(budgetBreakdowns).map(([category, data]: [string, any]) => {
    // Extract amount - handle different formats
    let amount = 0;
    if (typeof data === 'number') {
      amount = data;
    } else if (typeof data === 'string') {
      // Handle currency strings like "$90,000" or "90000"
      const num = parseFloat(data.replace(/[^0-9.]/g, ''));
      amount = isNaN(num) ? 0 : num;
    } else if (data && typeof data === 'object') {
      // Handle object format from budgeting agent: {recommended_spend: 90000, pct_of_total: 51.4}
      amount = Number(data.recommended_spend || data.amount || data || 0);
    }
    
    // Calculate percentage
    const percentage = breakdownTotal > 0 ? Math.round((amount / breakdownTotal) * 100) : 0;
    
    return {
      category: category.charAt(0).toUpperCase() + category.slice(1),
      amount,
      percentage,
      notes: asArray(data?.key_assumptions || []).join('; '),
    };
  }).filter(item => item.amount > 0); // Only include categories with amounts > 0
  
  // Debug logging
  if (breakdown.length === 0) {
    console.warn('No budget breakdown found. Available data:', {
      finalPlanBudget: finalPlan?.budget,
      budgetingRec: finalPlan?.recommendations?.budgeting,
      budgetBreakdownsKeys: Object.keys(budgetBreakdowns),
    });
  } else {
    console.log(`✅ Found ${breakdown.length} budget categories:`, breakdown.map(b => b.category).join(', '));
  }

  const budgetTotal = Number(finalPlan?.budget?.total_allocated) || breakdown.reduce((sum, entry) => sum + entry.amount, 0);
  const budgetingRec = finalPlan?.recommendations?.budgeting;
  const scenarios = asArray(budgetingRec?.what_if_scenarios || [])
    .map((scenario: any) => {
      if (!scenario) return '';
      if (typeof scenario === 'string') return scenario;
      return `${scenario.name || 'Scenario'}: ${scenario.impact || ''} ${scenario.recommendation ? `(${scenario.recommendation})` : ''}`.trim();
    })
    .filter(Boolean);

  // Extract schedule - use ONLY final_plan.schedule.sessions
  let scheduleSessions: any[] = [];
  
  if (finalPlan?.schedule?.sessions && Array.isArray(finalPlan.schedule.sessions)) {
    scheduleSessions = finalPlan.schedule.sessions;
  }
  
  // Fallback: check final_plan.recommendations.scheduling if schedule.sessions is empty
  if (scheduleSessions.length === 0) {
    const schedulingRec = finalPlan?.recommendations?.scheduling;
    if (schedulingRec?.optimized_schedule && Array.isArray(schedulingRec.optimized_schedule)) {
      scheduleSessions = schedulingRec.optimized_schedule;
    }
  }

  // Extract event date for multi-day events
  const eventDate = eventDetails.date;
  const eventDates = eventDate?.includes(' to ') 
    ? eventDate.split(' to ').map(d => d.trim())
    : eventDate ? [eventDate] : [];
  
  // First pass: map sessions and extract date/day information
  const scheduleWithDates = scheduleSessions.map((item: any, index: number) => {
    const startTime = item.start_time || '';
    const endTime = item.end_time || '';
    const timeWindow = [startTime, endTime].filter(Boolean).join(' - ');
    const duration = item.duration ? `${item.duration} min` : item.duration_minutes ? `${item.duration_minutes} min` : '';
    
    // Extract date/day information - check multiple sources
    let date: string | undefined;
    const title = (item.name || item.session_name || item.title || '').toLowerCase();
    
    // Check if date is explicitly provided
    if (item.date) {
      date = item.date;
    } else if (item.day) {
      date = item.day;
    } 
    // Check if title contains day information (e.g., "Day 1", "Day 2")
    else if (title.includes('day 1') || title.includes('(day 1)')) {
      date = eventDates[0] || 'Day 1';
    } else if (title.includes('day 2') || title.includes('(day 2)')) {
      date = eventDates[1] || eventDates[0] || 'Day 2';
    } else if (title.includes('day 3') || title.includes('(day 3)')) {
      date = eventDates[2] || eventDates[1] || eventDates[0] || 'Day 3';
    }
    // For single-day events, assign the date
    else if (eventDates.length === 1) {
      date = eventDates[0];
    }
    
    // Determine type based on title/keywords
    let itemType: ScheduleItem['type'] = 'session';
    if (title.includes('keynote') || title.includes('opening') || title.includes('closing')) {
      itemType = 'keynote';
    } else if (title.includes('break') || title.includes('coffee') || title.includes('networking')) {
      itemType = 'break';
    } else if (title.includes('lunch') || title.includes('dinner') || title.includes('meal')) {
      itemType = 'meal';
    } else if (title.includes('networking')) {
      itemType = 'networking';
    } else if (title.includes('demo') || title.includes('workshop') || title.includes('activity')) {
      itemType = 'activity';
    }
    
    return {
      time: timeWindow || item.time || 'TBD',
      title: item.name || item.session_name || item.title || item.activity || 'Session',
      duration: duration,
      type: itemType,
      location: item.room || item.location,
      speaker: item.speaker || item.presenter,
      date: date,
      startTime: startTime, // For sorting
      endTime: endTime, // For sorting
      originalIndex: index, // Preserve original order for day detection
    };
  });
  
  // For multi-day events without explicit dates, detect day boundaries
  // by looking for time resets (e.g., 09:00 appearing after later times)
  if (eventDates.length > 1 && scheduleWithDates.some(item => !item.date)) {
    let currentDay = 0;
    let lastTime = '';
    
    scheduleWithDates.forEach((item, index) => {
      if (!item.date && item.startTime) {
        // If we see an earlier time after a later time, it's likely a new day
        if (lastTime && item.startTime < lastTime && item.startTime <= '12:00') {
          currentDay = Math.min(currentDay + 1, eventDates.length - 1);
        }
        lastTime = item.startTime;
        
        // Assign date based on detected day
        if (currentDay < eventDates.length) {
          item.date = eventDates[currentDay];
        }
      }
    });
  }
  
  // Sort schedule by date (if available) and then by start time
  const schedule = scheduleWithDates.sort((a, b) => {
    // First sort by date
    if (a.date && b.date) {
      const dateCompare = a.date.localeCompare(b.date);
      if (dateCompare !== 0) return dateCompare;
    } else if (a.date) return -1;
    else if (b.date) return 1;
    
    // Then sort by start time
    if (a.startTime && b.startTime) {
      return a.startTime.localeCompare(b.startTime);
    } else if (a.startTime) return -1;
    else if (b.startTime) return 1;
    
    // Fallback to original order
    return (a.originalIndex || 0) - (b.originalIndex || 0);
  }).map(({ originalIndex, ...item }) => item); // Remove originalIndex from final output

  // Debug logging
  if (schedule.length === 0) {
    console.warn('No schedule found. Available data:', {
      finalPlanSchedule: finalPlan?.schedule,
      schedulingRec: finalPlan?.recommendations?.scheduling,
      finalPlanKeys: finalPlan ? Object.keys(finalPlan) : [],
    });
  } else {
    console.log(`✅ Found ${schedule.length} schedule items`);
  }

  // Use only final_plan.recommendations.speakers
  const speakersRec = finalPlan?.recommendations?.speakers;
  const speakersSource = asArray(speakersRec?.speakers_recommendations?.top_speaker_options || []);

  const speakers = speakersSource.map((item: any) => ({
    name: item.name || 'Speaker',
    title: item.bio || '',
    company: item.company || '',
    topic: item.ideal_role || item.topic || '',
    fee: formatPrice(item.estimated_fee || ''),
    image: item.image,
  }));

  // Use only final_plan.recommendations.catering
  const cateringRec = finalPlan?.recommendations?.catering || {};

  // Use only final_plan.recommendations.activities
  const activitiesRec = finalPlan?.recommendations?.activities;
  const activitiesSource = asArray(activitiesRec?.activity_planning?.recommendations || []);

  const activities = activitiesSource.map((item: any) => ({
    name: item.name || 'Activity',
    description: item.description || '',
    duration: String(item.duration || ''),
  }));

  // Use only final_plan.recommendations.entertainment
  const entertainmentRec = finalPlan?.recommendations?.entertainment;
  const entertainmentSource = asArray(entertainmentRec?.entertainment_recommendations?.specific_options || []);

  const entertainment = entertainmentSource.map((item: any) => ({
    type: item.name || 'Entertainment',
    description: item.description || '',
    cost: formatPrice(item.cost_estimate || item.cost || ''),
  }));

  // Use only final_plan.recommendations.communication
  const commRecommendations = finalPlan?.recommendations?.communication?.communication_recommendations || {};
  const communication = {
    timeline: asArray(commRecommendations.timeline || []).map((entry: any) =>
      typeof entry === 'string' ? { date: '', action: entry } : { date: entry.date || '', action: entry.action || entry }
    ),
    channels: asArray(commRecommendations.channels || []),
    keyMessages: asArray(commRecommendations.key_messages || []),
  };

  // Extract timeline from finalPlan.timeline (expected format: array of objects with phase, tasks, deadline)
  // The backend schema ensures timeline is always present (even if empty array)
  const timelineData = finalPlan?.timeline;
  let timelineItems: string[] = [];
  
  if (timelineData) {
    if (Array.isArray(timelineData)) {
      // Handle array of timeline items (objects or strings)
      timelineItems = timelineData.map((item: any) => {
        if (!item) return null;
        // Handle string items
        if (typeof item === 'string') {
          return item;
        }
        // Handle object items (expected format: {phase, tasks, deadline})
        if (typeof item === 'object') {
          const tasks = asArray(item.tasks || []).join(', ');
          const deadline = item.deadline ? ` (by ${item.deadline})` : '';
          const phase = item.phase || 'Phase';
          const result = `${phase}: ${tasks}${deadline}`.trim();
          return result || null;
        }
        return String(item);
      }).filter((item): item is string => Boolean(item));
    } else if (typeof timelineData === 'string') {
      // Handle string timeline (comma-separated or newline-separated)
      timelineItems = timelineData.split(/[,\n]/).map(s => s.trim()).filter(Boolean);
    }
  }
  
  // Debug logging
  if (timelineItems.length === 0) {
    console.warn('Timeline is empty. Available data:', {
      finalPlanTimeline: finalPlan?.timeline,
      timelineDataType: timelineData ? typeof timelineData : 'undefined',
      timelineDataIsArray: Array.isArray(timelineData),
      finalPlanKeys: finalPlan ? Object.keys(finalPlan) : [],
      finalPlanPreview: finalPlan ? JSON.stringify(finalPlan).substring(0, 500) : 'No finalPlan',
    });
  } else {
    console.log(`✅ Found ${timelineItems.length} timeline items:`, timelineItems);
  }

  // Use only final_plan.risks
  const risks = asArray(finalPlan?.risks || []).map((item: any) => ({
    risk: item.risk || String(item),
    mitigation: item.mitigation || 'Review and address',
  }));

  // Use only final_plan.action_items
  const actionItems = asArray(finalPlan?.action_items || []).map((item: any, index: number) => ({
    task: item.action || item.task || String(item),
    owner: item.owner || 'Event Coordinator',
    deadline: item.deadline || 'Before event date',
    priority: (item.priority as 'high' | 'medium' | 'low') || (index < 3 ? 'high' : 'medium'),
  }));

  // Extract executive summary - handle both string and JSON object formats
  let executiveSummary: string = '';
  if (finalPlan?.executive_summary) {
    const summary = finalPlan.executive_summary;
    if (typeof summary === 'string') {
      const trimmed = summary.trim();
      // Check if it's a JSON string that needs parsing
      if (trimmed.startsWith('{') && trimmed.includes('"executive_summary"')) {
        try {
          // Try to parse the JSON - handle both complete and incomplete JSON
          let jsonStr = trimmed;
          // If it's incomplete (missing closing brace), try to complete it
          if (!jsonStr.endsWith('}')) {
            // Find the last complete quote and add closing brace
            const lastQuote = jsonStr.lastIndexOf('"');
            if (lastQuote > 0) {
              jsonStr = jsonStr.substring(0, lastQuote + 1) + '}';
            }
          }
          const parsed = JSON.parse(jsonStr);
          if (typeof parsed === 'object' && parsed !== null && parsed.executive_summary) {
            executiveSummary = String(parsed.executive_summary);
          } else {
            executiveSummary = trimmed;
          }
        } catch (e) {
          // If JSON parsing fails, try to extract the text manually
          // Find the start of the value (after "executive_summary": ")
          const startPattern = /"executive_summary"\s*:\s*"/;
          const startMatch = trimmed.match(startPattern);
          
          if (startMatch && startMatch.index !== undefined) {
            const startIdx = startMatch.index + startMatch[0].length;
            // Find the end - look for the last quote before closing brace or end of string
            // Handle escaped quotes properly
            let endIdx = startIdx;
            let inString = true;
            let escaped = false;
            
            for (let i = startIdx; i < trimmed.length; i++) {
              const char = trimmed[i];
              if (escaped) {
                escaped = false;
                continue;
              }
              if (char === '\\') {
                escaped = true;
                continue;
              }
              if (char === '"' && inString) {
                // Check if this is the closing quote (not followed by more content before })
                const remaining = trimmed.substring(i + 1).trim();
                if (remaining.startsWith('}') || remaining === '') {
                  endIdx = i;
                  break;
                }
              }
            }
            
            if (endIdx > startIdx) {
              executiveSummary = trimmed.substring(startIdx, endIdx)
                .replace(/\\n/g, '\n')
                .replace(/\\"/g, '"')
                .replace(/\\\\/g, '\\')
                .replace(/\\t/g, '\t')
                .replace(/\\r/g, '\r');
            } else {
              // No closing quote found, take everything after the opening quote
              executiveSummary = trimmed.substring(startIdx)
                .replace(/\\n/g, '\n')
                .replace(/\\"/g, '"')
                .replace(/\\\\/g, '\\')
                .replace(/\\t/g, '\t')
                .replace(/\\r/g, '\r');
            }
          } else {
            // Last resort: just remove the JSON wrapper
            executiveSummary = trimmed
              .replace(/^\{\s*"executive_summary"\s*:\s*"/, '')
              .replace(/"\s*\}$/, '')
              .replace(/\\n/g, '\n')
              .replace(/\\"/g, '"')
              .replace(/\\\\/g, '\\');
          }
        }
      } else {
        executiveSummary = trimmed;
      }
    } else if (typeof summary === 'object' && summary !== null) {
      // If it's already an object, try to extract the value
      if ('executive_summary' in summary) {
        executiveSummary = String(summary.executive_summary);
      } else {
        executiveSummary = JSON.stringify(summary);
      }
    } else {
      executiveSummary = String(summary);
    }
  }
  
  // Clean up escaped characters
  if (executiveSummary) {
    executiveSummary = executiveSummary
      .replace(/\\n/g, '\n')
      .replace(/\\"/g, '"')
      .replace(/\\\\/g, '\\')
      .replace(/\\t/g, '\t')
      .trim();
  }
  
  // Fallback if no executive summary found
  if (!executiveSummary) {
    const schedulingRec = finalPlan?.recommendations?.scheduling;
    const schedulingStatus = schedulingRec?.status || finalPlan?.schedule?.status;
    executiveSummary = `${eventDetails.name} is a ${eventDetails.type} scheduled for ${eventDetails.date} at ${eventDetails.location}. ` +
      `Expected attendance: ${eventDetails.guestCount} guests. Budget: ${eventDetails.budget}.` +
      (schedulingStatus === 'infeasible' ? ` Note: Scheduling conflicts detected.` : '');
  }

  // Extract export data
  const calendarInvite = parseJson<JsonRecord>(workflow.calendar_invite) || {};
  const registrationForm = workflow.registration_form as JsonRecord | undefined;
  const logoData = workflow.logo as JsonRecord | undefined;
  const calendarFile = calendarInvite?.calendar_file_path as string | undefined;
  const pdfFile = workflow.pdf_report as string | undefined;
  const formUrl = cleanUrl(registrationForm?.form_url as string | undefined);
  const logoFile = logoData?.logo_file_path as string | undefined;

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
      warnings: asArray(budgetingRec?.warnings || []),
    },
    schedule,
    speakers,
    catering: {
      menuPreview: asArray(cateringRec.menu_overview || []),
      dietaryOptions: asArray(cateringRec.dietary_accommodations || []),
      estimatedCost: formatPrice(cateringRec.budget_estimate?.total || cateringRec.estimated_total || cateringRec.estimatedCost || 'TBD'),
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
    exports: {
      calendarFile,
      pdfFile,
      formUrl,
      logoFile,
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
  const [originalWorkflowResult, setOriginalWorkflowResult] = useState<PlanApiResponse | null>(null);
  const [formData, setFormData] = useState<EventFormData | null>(null);
  const [devSettings, setDevSettings] = useState<DevSettings>({ enableSandbox: false, enableSMS: false });
  const { toast } = useToast();

  // Keep the loading screen active while the backend workflow runs
  useEffect(() => {
    if (appState !== 'processing') return;

    let progressInterval: NodeJS.Timeout | null = null;

    // Poll for progress updates every 500ms
    progressInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/plan/status`);
        if (response.ok) {
          const progress = await response.json();
          
          console.log('Progress update:', progress);
          
          // Check if workflow is complete
          if (progress.status === 'completed' || progress.phase === 'complete') {
            // Final update - ensure all agents show as completed
            if (progress.agents && progress.agents.length > 0) {
              const backendStatuses = progress.agents as Array<{ name: string; status: string }>;
              const usedAgents: Agent[] = backendStatuses.map((bs) => {
                const agentDef = agentDefinitions[bs.name] || { name: bs.name, icon: 'Sparkles' };
                return {
                  id: bs.name,
                  name: agentDef.name,
                  icon: agentDef.icon,
                  status: 'completed' as const,
                  message: 'Completed',
                  progress: 100,
                };
              });
              setAgents(usedAgents);
            }
            // Stop polling - workflow is done
            if (progressInterval) {
              clearInterval(progressInterval);
            }
            return;
          }
          
          // If phase_2 or phase_4 is active and we have agents, populate them
          if ((progress.phase === 'phase_2' || progress.phase === 'phase_4') && progress.agents && progress.agents.length > 0) {
            const backendStatuses = progress.agents as Array<{ name: string; status: string }>;
            
            const usedAgents: Agent[] = backendStatuses.map((bs) => {
              const agentDef = agentDefinitions[bs.name] || { name: bs.name, icon: 'Sparkles' };
              
              let frontendStatus: 'pending' | 'active' | 'completed' = 'pending';
              if (bs.status === 'done') {
                frontendStatus = 'completed';
              } else if (bs.status === 'working') {
                frontendStatus = 'active';
              }
              
              return {
                id: bs.name,
                name: agentDef.name,
                icon: agentDef.icon,
                status: frontendStatus,
                message: frontendStatus === 'completed' ? 'Completed' : 'Working...',
                progress: frontendStatus === 'completed' ? 100 : 60,
              };
            });
            
            setAgents(usedAgents);
          }
        }
      } catch (error) {
        console.log('Progress poll error (expected during startup):', error);
      }
    }, 500);

    return () => {
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
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
          setOriginalWorkflowResult(apiResponse);
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
    // Start with empty agents - the orchestrator phase will show
    setAgents([]);
    setAppState('processing');

    // Merge dev settings into form data
    const dataWithSettings = { ...data, ...devSettings };

    planMutation.mutate(dataWithSettings, {
        onSuccess: (apiResponse) => {
          const mapped = mapWorkflowToEventResult(apiResponse, data);
          setEventResult(mapped);
          setOriginalWorkflowResult(apiResponse);
          
          // Log the response for debugging
          console.log('API Response:', apiResponse);
        console.log('Agent statuses:', apiResponse.result?.agent_statuses);
        
        // Map backend agent_statuses to frontend agents
        if (apiResponse.result?.agent_statuses && Array.isArray(apiResponse.result.agent_statuses)) {
          const backendStatuses = apiResponse.result.agent_statuses as Array<{ name: string; status: string }>;
          console.log('Processing agent statuses:', backendStatuses);
          
          // Create frontend agents only for the ones actually used by the orchestrator
          const usedAgents: Agent[] = backendStatuses.map((bs) => {
            const agentDef = agentDefinitions[bs.name] || { name: bs.name, icon: 'Sparkles' };
            
            // Map backend statuses to frontend statuses
            let frontendStatus: 'pending' | 'active' | 'completed' = 'pending';
            if (bs.status === 'done') {
              frontendStatus = 'completed';
            } else if (bs.status === 'working') {
              frontendStatus = 'active';
            }
            
            return {
              id: bs.name,
              name: agentDef.name,
              icon: agentDef.icon,
              status: frontendStatus,
              message: frontendStatus === 'completed' ? 'Completed' : 'In progress',
              progress: frontendStatus === 'completed' ? 100 : 50,
            };
          });
          
          console.log('Setting agents:', usedAgents);
          setAgents(usedAgents);
        } else {
          console.log('No agent_statuses found in response, using all as completed');
          // Fallback if agent_statuses not available
          setAgents((prev) => prev.map((agent) => ({ ...agent, status: 'completed', message: 'Completed', progress: 100 })));
        }
        
        setAppState('results');
      },
      onError: (error) => {
        console.error(error);
        toast({
          title: 'Planning failed',
          description: error.message || 'Unexpected error while running the agents.',
          variant: 'destructive',
        });
        setAgents([]);
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
    <div className="min-h-screen gradient-hero flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-panel border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => setAppState('landing')}
              className="flex items-center gap-2 hover:opacity-80 transition-opacity group"
            >
              <div className="relative w-10 h-10 flex items-center justify-center">
                {/* Custom logo - stylized "E" with event elements */}
                <svg 
                  viewBox="0 0 40 40" 
                  className="w-10 h-10 group-hover:scale-105 transition-transform"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  {/* Background circle with gradient */}
                  <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#E67E5A" />
                      <stop offset="100%" stopColor="#D4A574" />
                    </linearGradient>
                  </defs>
                  <circle cx="20" cy="20" r="18" fill="url(#logoGradient)" className="drop-shadow-lg" />
                  
                  {/* Stylized "E" letter */}
                  <path 
                    d="M12 10 L12 30 M12 10 L28 10 M12 20 L24 20 M12 30 L28 30" 
                    stroke="white" 
                    strokeWidth="2.5" 
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  
                  {/* Decorative event dots */}
                  <circle cx="26" cy="14" r="2" fill="white" opacity="0.9" />
                  <circle cx="26" cy="26" r="2" fill="white" opacity="0.9" />
                </svg>
              </div>
              <span className="text-xl font-display font-bold text-foreground">
                Évènement.ai
              </span>
            </button>
            <StepIndicator currentState={appState} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8 md:py-12 flex-1">
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
              <ResultsView 
                result={eventResult} 
                onStartOver={handleStartOver}
                originalWorkflowResult={originalWorkflowResult}
                onPlanUpdate={(updatedResult) => {
                  // Remap the updated workflow result to EventPlanResult
                  const mapped = mapWorkflowToEventResult(updatedResult, formData);
                  setEventResult(mapped);
                  setOriginalWorkflowResult(updatedResult);
                  toast({
                    title: 'Plan Updated',
                    description: 'Your event plan has been updated based on your request.',
                  });
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="py-6 border-t border-border/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-muted-foreground">
          Powered by 12 agents and 1 coordinator • Built with love and a lot of pain
        </div>
      </footer>

      {/* Dev Menu */}
      <DevMenu onSettingsChange={setDevSettings} />
    </div>
  );
};

export default Index;
