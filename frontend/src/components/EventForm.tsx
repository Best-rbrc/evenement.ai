import * as React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { EventFormData } from '@/types/event';
import { LocationAutocomplete } from '@/components/LocationAutocomplete';
import { 
  Calendar, 
  MapPin, 
  DollarSign, 
  Users, 
  Sparkles, 
  Clock,
  Building2,
  PartyPopper,
  Mic,
  MicOff,
  Loader2
} from 'lucide-react';

const eventTypes = [
  'Tech Conference',
  'Workshop',
  'Hackathon',
  'Corporate Gala',
  'Wedding',
  'Academic Symposium',
  'Festival',
  'Other',
];

const formSchema = z.object({
  eventType: z.string().min(1, 'Please select an event type'),
  customEventType: z.string().optional(),
  eventName: z.string().min(3, 'Event name must be at least 3 characters'),
  dateType: z.enum(['single', 'range']),
  eventDate: z.string().min(1, 'Please select a date'),
  endDate: z.string().optional(),
  startTime: z.string().optional(),
  endTime: z.string().optional(),
  locationPreference: z.string().min(2, 'Please enter a location'),
  budgetMin: z.number().min(0),
  budgetMax: z.number().min(0),
  guestCountMin: z.number().min(1),
  guestCountMax: z.number().min(1),
  specialRequirements: z.string(),
});

interface EventFormProps {
  onSubmit: (data: EventFormData) => void;
}

export function EventForm({ onSubmit }: EventFormProps) {
  const [isListening, setIsListening] = React.useState(false);
  const [isProcessing, setIsProcessing] = React.useState(false);
  const transcriptRef = React.useRef('');
  const recognitionRef = React.useRef<any>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid },
  } = useForm<EventFormData>({
    resolver: zodResolver(formSchema),
    mode: 'onChange',
    defaultValues: {
      eventType: 'Tech Conference',
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
    },
  });

  const eventType = watch('eventType');
  const dateType = watch('dateType');
  const budgetMin = watch('budgetMin');
  const budgetMax = watch('budgetMax');
  const guestCountMin = watch('guestCountMin');
  const guestCountMax = watch('guestCountMax');

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      transcriptRef.current = '';
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' ';
        }
      }
      if (finalTranscript) {
        transcriptRef.current += finalTranscript;
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopVoiceInput = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);

      const transcript = transcriptRef.current.trim();
      if (transcript) {
        setIsProcessing(true);
        try {
          const response = await fetch('http://localhost:8000/api/voice-to-form', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript })
          });

          if (!response.ok) throw new Error('Failed to process voice input');

          const data = await response.json();
          
          // Auto-fill form with extracted data (only non-null values)
          if (data.eventType) setValue('eventType', data.eventType, { shouldValidate: true });
          if (data.customEventType) setValue('customEventType', data.customEventType, { shouldValidate: true });
          if (data.eventName) setValue('eventName', data.eventName, { shouldValidate: true });
          if (data.dateType) setValue('dateType', data.dateType, { shouldValidate: true });
          if (data.eventDate) setValue('eventDate', data.eventDate, { shouldValidate: true });
          if (data.endDate) setValue('endDate', data.endDate, { shouldValidate: true });
          if (data.startTime) setValue('startTime', data.startTime, { shouldValidate: true });
          if (data.endTime) setValue('endTime', data.endTime, { shouldValidate: true });
          if (data.locationPreference) setValue('locationPreference', data.locationPreference, { shouldValidate: true });
          if (data.budgetMin !== null && data.budgetMin !== undefined) setValue('budgetMin', data.budgetMin, { shouldValidate: true });
          if (data.budgetMax !== null && data.budgetMax !== undefined) setValue('budgetMax', data.budgetMax, { shouldValidate: true });
          if (data.guestCountMin !== null && data.guestCountMin !== undefined) setValue('guestCountMin', data.guestCountMin, { shouldValidate: true });
          if (data.guestCountMax !== null && data.guestCountMax !== undefined) setValue('guestCountMax', data.guestCountMax, { shouldValidate: true });
          if (data.specialRequirements) setValue('specialRequirements', data.specialRequirements, { shouldValidate: true });

          transcriptRef.current = '';
        } catch (error) {
          console.error('Error processing voice input:', error);
          alert('Failed to process voice input. Please try again.');
        } finally {
          setIsProcessing(false);
        }
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-5xl mx-auto px-4"
    >
      <motion.div variants={itemVariants} className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-display font-bold text-foreground mb-4">
          Plan Your Perfect Event
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Tell us about your event and our AI agents will create a comprehensive plan tailored to your needs.
        </p>
        
        {/* Voice Input Button */}
        <div className="mt-6 flex flex-col items-center gap-3">
          <Button
            type="button"
            onClick={isListening ? stopVoiceInput : startVoiceInput}
            disabled={isProcessing}
            variant={isListening ? "destructive" : "outline"}
            size="lg"
            className="min-w-[200px]"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : isListening ? (
              <>
                <MicOff className="w-5 h-5" />
                Stop Recording
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                Describe Your Event
              </>
            )}
          </Button>
          {isListening && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="px-4 py-2 bg-primary/10 rounded-full border border-primary/20"
            >
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                Listening...
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Event Basics */}
          <motion.div variants={itemVariants}>
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PartyPopper className="w-5 h-5 text-primary" />
                  Event Basics
                </CardTitle>
                <CardDescription>What kind of event are you planning?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="eventType">Event Type</Label>
                  <Select
                    value={eventType}
                    onValueChange={(value) => setValue('eventType', value, { shouldValidate: true })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select event type" />
                    </SelectTrigger>
                    <SelectContent>
                      {eventTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.eventType && (
                    <p className="text-sm text-destructive">{errors.eventType.message}</p>
                  )}
                </div>

                {eventType === 'Other' && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="space-y-2"
                  >
                    <Label htmlFor="customEventType">Describe your event type</Label>
                    <Input
                      {...register('customEventType')}
                      placeholder="e.g., Product Launch, Team Retreat"
                    />
                  </motion.div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="eventName">Event Name</Label>
                  <Input
                    {...register('eventName')}
                    placeholder="e.g., AI Innovation Summit 2026"
                  />
                  {errors.eventName && (
                    <p className="text-sm text-destructive">{errors.eventName.message}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Schedule & Timing */}
          <motion.div variants={itemVariants}>
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-primary" />
                  Schedule & Timing
                </CardTitle>
                <CardDescription>When will your event take place?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="dateType">Date Range</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Single Day</span>
                    <Switch
                      checked={dateType === 'range'}
                      onCheckedChange={(checked) =>
                        setValue('dateType', checked ? 'range' : 'single')
                      }
                    />
                    <span className="text-sm text-muted-foreground">Multi-Day</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="eventDate">{dateType === 'range' ? 'Start Date' : 'Event Date'}</Label>
                    <Input type="date" {...register('eventDate')} />
                    {errors.eventDate && (
                      <p className="text-sm text-destructive">{errors.eventDate.message}</p>
                    )}
                  </div>

                  {dateType === 'range' && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="space-y-2"
                    >
                      <Label htmlFor="endDate">End Date</Label>
                      <Input type="date" {...register('endDate')} />
                    </motion.div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="startTime" className="flex items-center gap-1">
                      <Clock className="w-3 h-3" /> Start Time
                    </Label>
                    <Input type="time" {...register('startTime')} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="endTime" className="flex items-center gap-1">
                      <Clock className="w-3 h-3" /> End Time
                    </Label>
                    <Input type="time" {...register('endTime')} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Location */}
          <motion.div variants={itemVariants}>
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-primary" />
                  Location
                </CardTitle>
                <CardDescription>Where should we look for venues?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="locationPreference">Preferred Location</Label>
                  <LocationAutocomplete
                    value={watch('locationPreference')}
                    onChange={(value, coords) => {
                      setValue('locationPreference', value, { shouldValidate: true });
                      if (coords) {
                        setValue('locationCoords', coords);
                      }
                    }}
                    placeholder="e.g., San Francisco, CA or Barcelona, Spain"
                    icon={<Building2 className="w-4 h-4 text-muted-foreground" />}
                  />
                  {errors.locationPreference && (
                    <p className="text-sm text-destructive">{errors.locationPreference.message}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Budget & Guests */}
          <motion.div variants={itemVariants}>
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-primary" />
                  Budget & Guests
                </CardTitle>
                <CardDescription>Set your budget and expected attendance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Budget Range</Label>
                    <span className="text-sm font-medium text-primary">
                      {formatCurrency(budgetMin)} – {formatCurrency(budgetMax)}
                    </span>
                  </div>
                  <div className="px-2">
                    <Slider
                      value={[budgetMin, budgetMax]}
                      min={1000}
                      max={500000}
                      step={1000}
                      onValueChange={([min, max]) => {
                        setValue('budgetMin', min);
                        setValue('budgetMax', max);
                      }}
                      className="w-full"
                    />
                  </div>
                  <div className="flex gap-4">
                    <div className="flex-1 space-y-1">
                      <Label className="text-xs text-muted-foreground">Min</Label>
                      <Input
                        type="number"
                        value={budgetMin}
                        onChange={(e) => setValue('budgetMin', Number(e.target.value))}
                      />
                    </div>
                    <div className="flex-1 space-y-1">
                      <Label className="text-xs text-muted-foreground">Max</Label>
                      <Input
                        type="number"
                        value={budgetMax}
                        onChange={(e) => setValue('budgetMax', Number(e.target.value))}
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label className="flex items-center gap-1">
                      <Users className="w-4 h-4" /> Expected Guests
                    </Label>
                    <span className="text-sm font-medium text-primary">
                      {guestCountMin} – {guestCountMax}
                    </span>
                  </div>
                  <div className="px-2">
                    <Slider
                      value={[guestCountMin, guestCountMax]}
                      min={10}
                      max={2000}
                      step={10}
                      onValueChange={([min, max]) => {
                        setValue('guestCountMin', min);
                        setValue('guestCountMax', max);
                      }}
                      className="w-full"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Special Requirements - Full Width */}
        <motion.div variants={itemVariants}>
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-primary" />
                Special Requirements
              </CardTitle>
              <CardDescription>
                Any specific needs, themes, or preferences for your event?
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                {...register('specialRequirements')}
                placeholder="e.g., AI/ML focus, keynote speakers, networking sessions, accessibility needs, dietary restrictions, specific entertainment preferences..."
                className="min-h-[120px]"
              />
            </CardContent>
          </Card>
        </motion.div>

        {/* Submit Button */}
        <motion.div variants={itemVariants} className="flex justify-center pt-4">
          <Button
            type="submit"
            variant="hero"
            size="xl"
            disabled={!isValid}
            className="min-w-[250px]"
          >
            <Sparkles className="w-5 h-5" />
            Start AI Planning
          </Button>
        </motion.div>
      </form>
    </motion.div>
  );
}
