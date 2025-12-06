import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
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

export function EventMap({ location, coords }: EventMapProps) {
  const position: [number, number] = coords 
    ? [coords.lat, coords.lng] 
    : [37.7749, -122.4194]; // Default to SF

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
      <Marker position={position}>
        <Popup>
          <span className="font-medium">{location}</span>
        </Popup>
      </Marker>
    </MapContainer>
  );
}
