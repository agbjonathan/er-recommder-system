import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { getCongestionMap, CongestionFeature } from '../api/client';
import 'leaflet/dist/leaflet.css';

export default function Map() {
  const [features, setFeatures] = useState<CongestionFeature[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCongestionMap()
      .then((res) => setFeatures(res.data.features))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const getRiskColor = (risk: string | null) => {
    switch (risk) {
      case 'low': return '#22c55e';
      case 'medium': return '#eab308';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading map...</div>;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">ER Congestion Map</h2>
      <div className="h-[600px] rounded-lg overflow-hidden shadow-lg">
        <MapContainer
          center={[45.5, -73.6]}
          zoom={10}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; OpenStreetMap'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {features.map((f) => (
            <CircleMarker
              key={f.properties.hospital_id}
              center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
              radius={12}
              fillColor={getRiskColor(f.properties.risk_level)}
              fillOpacity={0.8}
              stroke={true}
              color="#fff"
              weight={2}
            >
              <Popup>
                <div className="text-sm">
                  <strong>{f.properties.name}</strong>
                  <br />
                  Risk: {f.properties.risk_level ?? 'Unknown'}
                  <br />
                  Pressure: {f.properties.predicted_pressure?.toFixed(1) ?? 'N/A'}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      <div className="flex gap-4 justify-center">
        <span className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-green-500"></span> Low
        </span>
        <span className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-yellow-500"></span> Medium
        </span>
        <span className="flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-red-500"></span> High
        </span>
      </div>
    </div>
  );
}
