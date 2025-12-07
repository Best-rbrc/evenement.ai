import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from '@/components/ui/command';
import { Check, MapPin } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LocationSuggestion {
  display_name: string;
  lat: string;
  lon: string;
}

interface LocationAutocompleteProps {
  value: string;
  onChange: (value: string, coords?: { lat: number; lng: number }) => void;
  placeholder?: string;
  className?: string;
  icon?: React.ReactNode;
}

export function LocationAutocomplete({
  value,
  onChange,
  placeholder = 'e.g., San Francisco, CA',
  className,
  icon,
}: LocationAutocompleteProps) {
  const [open, setOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Clear previous timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Don't search if value is too short or empty
    if (!value || value.length < 2) {
      setSuggestions([]);
      setOpen(false);
      return;
    }

    // Debounce the search
    debounceTimer.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(value)}&limit=5&addressdetails=1&accept-language=en`,
          {
            headers: {
              'User-Agent': 'AI-Event-Planner/1.0',
              'Accept-Language': 'en',
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setSuggestions(data);
          setOpen(data.length > 0);
        } else {
          setSuggestions([]);
          setOpen(false);
        }
      } catch (error) {
        console.error('Location search error:', error);
        setSuggestions([]);
        setOpen(false);
      } finally {
        setIsLoading(false);
      }
    }, 300); // 300ms debounce

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [value]);

  const handleSelect = (suggestion: LocationSuggestion) => {
    onChange(suggestion.display_name, {
      lat: parseFloat(suggestion.lat),
      lng: parseFloat(suggestion.lon),
    });
    setOpen(false);
  };

  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  return (
    <div className="relative">
      {icon && (
        <div className="absolute left-3 top-1/2 -translate-y-1/2 z-10 pointer-events-none">
          {icon}
        </div>
      )}
      <Input
        ref={inputRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={cn(icon && 'pl-10', className)}
        onFocus={() => {
          if (suggestions.length > 0) {
            setOpen(true);
          }
        }}
        onBlur={(e) => {
          // Don't close if clicking on a suggestion
          const relatedTarget = e.relatedTarget as HTMLElement;
          if (relatedTarget?.closest('[role="option"]') || dropdownRef.current?.contains(relatedTarget)) {
            return;
          }
          // Small delay to allow click events to fire
          setTimeout(() => setOpen(false), 200);
        }}
      />
      {open && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 rounded-md border bg-popover text-popover-foreground shadow-md"
          style={{ top: '100%' }}
        >
          <Command shouldFilter={false}>
            <CommandList>
              {isLoading ? (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  Searching...
                </div>
              ) : suggestions.length === 0 ? (
                <CommandEmpty>No locations found.</CommandEmpty>
              ) : (
                <CommandGroup>
                  {suggestions.map((suggestion, index) => (
                    <CommandItem
                      key={index}
                      value={suggestion.display_name}
                      onSelect={() => handleSelect(suggestion)}
                      className="cursor-pointer"
                      onMouseDown={(e) => {
                        // Prevent input blur when clicking
                        e.preventDefault();
                        handleSelect(suggestion);
                      }}
                    >
                      <MapPin className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                      <span className="flex-1">{suggestion.display_name}</span>
                      <Check
                        className={cn(
                          'ml-auto h-4 w-4',
                          value === suggestion.display_name ? 'opacity-100' : 'opacity-0'
                        )}
                      />
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </div>
      )}
    </div>
  );
}

