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
import { 
  Calendar, 
  MapPin, 
  DollarSign, 
  Users, 
  Sparkles, 
  Clock,
  Building2,
  PartyPopper
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
                    <Label htmlFor="endTime">End Time</Label>
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
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      {...register('locationPreference')}
                      className="pl-10"
                      placeholder="e.g., San Francisco, CA"
                    />
                  </div>
                  {errors.locationPreference && (
                    <p className="text-sm text-destructive">{errors.locationPreference.message}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Enter a city, region, or specific venue preference
                  </p>
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
