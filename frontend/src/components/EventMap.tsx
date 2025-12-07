import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface EventMapProps {
  location: string;
  coords?: { lat: number; lng: number };
}

// Component to update map center when location changes
function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, 13);
  }, [map, center]);
  return null;
}

async function geocodeLocation(location: string): Promise<{ lat: number; lng: number } | null> {
  if (!location || location === 'Location TBD') {
    return null;
  }

  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}&limit=1`,
      {
        headers: {
          'User-Agent': 'AI-Event-Planner/1.0',
        },
      }
    );

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    if (data && data.length > 0) {
      return {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon),
      };
    }
  } catch (error) {
    console.error('Geocoding error:', error);
  }

  return null;
}

export function EventMap({ location, coords }: EventMapProps) {
  const [position, setPosition] = useState<[number, number] | null>(null);
  const [isLoading, setIsLoading] = useState(!coords);

  useEffect(() => {
    if (coords) {
      setPosition([coords.lat, coords.lng]);
      setIsLoading(false);
    } else if (location) {
      setIsLoading(true);
      geocodeLocation(location).then((geocoded) => {
        if (geocoded) {
          setPosition([geocoded.lat, geocoded.lng]);
        } else {
          // Fallback to a default location if geocoding fails
          setPosition([37.7749, -122.4194]);
        }
        setIsLoading(false);
      });
    } else {
      setPosition([37.7749, -122.4194]);
      setIsLoading(false);
    }
  }, [location, coords]);

  if (isLoading || !position) {
    return (
      <div className="flex items-center justify-center h-full min-h-[250px] rounded-r-2xl lg:rounded-l-none rounded-b-2xl lg:rounded-b-none bg-muted">
        <span className="text-muted-foreground">Loading map...</span>
      </div>
    );
  }

  return (
    <MapContainer
      center={position}
      zoom={13}
      scrollWheelZoom={false}
      style={{ height: '100%', width: '100%', minHeight: '250px' }}
      className="rounded-r-2xl lg:rounded-l-none rounded-b-2xl lg:rounded-b-none"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapUpdater center={position} />
      <Marker position={position}>
        <Popup>
          <span className="font-medium">{location}</span>
        </Popup>
      </Marker>
    </MapContainer>
  );
}
