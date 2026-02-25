import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { getCongestionMap } from '../api/client';
import type { CongestionFeature } from '../api/client';
import { useLang } from '../i18n/LangContext';
import 'leaflet/dist/leaflet.css';

export default function Map() {
  const { t } = useLang();
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
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#94a3b8';
    }
  };

  if (loading) {
    return (
      <div className="map-loading">
        <div className="spinner" />
        <p>{t.map.loading}</p>
      </div>
    );
  }

  return (
    <div className="map-page">
      <h2 className="map-title">{t.map.title}</h2>
      <div className="map-container">
        <MapContainer center={[45.5, -73.6]} zoom={10} className="leaflet-map">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {features.map((f) => (
            <CircleMarker
              key={f.properties.hospital_id}
              center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
              radius={14}
              fillColor={getRiskColor(f.properties.risk_level)}
              fillOpacity={0.85}
              stroke
              color="#ffffff"
              weight={2.5}
            >
              <Popup className="custom-popup">
                <strong>{f.properties.name}</strong>
                <br />
                {t.map.risk_label}: {f.properties.risk_level ?? t.map.unknown}
                <br />
                {t.map.pressure_label}: {f.properties.predicted_pressure?.toFixed(2) ?? 'N/A'}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#22c55e' }} />
          {t.map.legend_low}
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#f59e0b' }} />
          {t.map.legend_medium}
        </div>
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#ef4444' }} />
          {t.map.legend_high}
        </div>
      </div>
    </div>
  );
}
