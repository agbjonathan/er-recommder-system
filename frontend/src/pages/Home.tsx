import { useState } from 'react';
import { getRecommendations } from '../api/client';
import type { Hospital } from '../api/client';
import { useLang } from '../i18n/LangContext';

export default function Home() {
  const { t } = useLang();
  const [address, setAddress] = useState('');
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [results, setResults] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) return;
    setLoading(true);
    setError(null);
    try {
      let lat: number, lng: number;
      if (coords) {
        lat = coords.lat;
        lng = coords.lng;
      } else {
        const geoRes = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`,
          { headers: { 'Accept-Language': 'en' } }
        );
        const geoData = await geoRes.json();
        if (!geoData.length) {
          setError('Address not found. Please try a more specific address.');
          return;
        }
        lat = parseFloat(geoData[0].lat);
        lng = parseFloat(geoData[0].lon);
      }
      const res = await getRecommendations(lat, lng);
      setResults(res.data.results);
    } catch {
      setError(t.home.error_fetch);
    } finally {
      setLoading(false);
    }
  };

  const handleLocateClick = () => {
    if (!navigator.geolocation) {
      setError(t.home.error_geo_unsupported);
      return;
    }
    setLocating(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        setCoords({ lat: latitude, lng: longitude });
        setAddress(`${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
        setLocating(false);
      },
      () => {
        setError(t.home.error_geo);
        setLocating(false);
      },
      { timeout: 8000 }
    );
  };

  const handleAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAddress(e.target.value);
    setCoords(null);
  };

  const getCongestionLevel = (pressure: number | null, risk: string | null): {
    key: string;
    label: string;
    accent: string;
    score: number;
  } => {
    const levels = {
      quiet:   { key: 'quiet',   label: t.home.cong_quiet,   accent: '#22c55e', score: 1 },
      calm:    { key: 'calm',    label: t.home.cong_calm,    accent: '#84cc16', score: 2 },
      busy:    { key: 'busy',    label: t.home.cong_busy,    accent: '#f59e0b', score: 3 },
      crowded: { key: 'crowded', label: t.home.cong_crowded, accent: '#f97316', score: 4 },
      packed:  { key: 'packed',  label: t.home.cong_packed,  accent: '#ef4444', score: 5 },
      unknown: { key: 'unknown', label: t.home.risk_unknown, accent: '#94a3b8', score: 0 },
    };
    if (pressure == null) {
      const r = risk?.toLowerCase();
      if (r === 'low')    return levels.calm;
      if (r === 'medium') return levels.busy;
      if (r === 'high')   return levels.crowded;
      return levels.unknown;
    }
    if (pressure < 0.25) return levels.quiet;
    if (pressure < 0.45) return levels.calm;
    if (pressure < 0.62) return levels.busy;
    if (pressure < 0.78) return levels.crowded;
    return levels.packed;
  };

  const mapsUrl = (lat: number, lng: number, name: string) =>
    `https://www.google.com/maps/search/?api=1&query=${lat},${lng}&query_place_id=${encodeURIComponent(name)}`;

  return (
    <div className="home-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg-grid" aria-hidden />
        <h1 className="hero-title">
          {t.home.hero_title}<br />
          <span className="hero-title-highlight">{t.home.hero_title_highlight}</span>
        </h1>
        <p className="hero-subtitle">{t.home.hero_subtitle}</p>
      </section>

      {/* Inline context banner — permanent, above search */}
      <div className="context-banner">
        <div className="context-banner-top">
          <span className="context-banner-icon">💡</span>
          <p className="context-banner-title">{t.home.context_title}</p>
        </div>
        <p className="context-banner-body">{t.home.context_body}</p>
        <div className="context-banner-tags">
          {(t.home.context_examples as string[]).map((ex, i) => (
            <span key={i} className="context-tag">{ex}</span>
          ))}
        </div>
        <p className="context-banner-note">{t.home.context_note}</p>
      </div>

      {/* Search */}
      <section className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <label className="search-label">{t.home.address_label}</label>
          <div className="search-row">
            <input
              type="text"
              value={address}
              onChange={handleAddressChange}
              placeholder={t.home.address_placeholder}
              className="search-input"
            />
            <button
              type="button"
              onClick={handleLocateClick}
              disabled={locating}
              className="btn btn-locate"
              title={t.home.btn_locate}
            >
              {locating ? '…' : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              )}
            </button>
          </div>
          <button
            type="submit"
            disabled={loading || !address.trim()}
            className="btn btn-primary btn-full"
          >
            {loading ? t.home.searching : t.home.btn_search}
          </button>
        </form>
        {error && <p className="error-msg">{error}</p>}
      </section>

      {/* Results */}
      {results.length > 0 && (
        <section className="results-section">
          <div className="results-header">
            <h2 className="results-title">
              {t.home.results_title}
              <span className="results-count">{results.length}</span>
            </h2>
            <p className="results-hint">{t.home.results_hint}</p>
          </div>

          <div className="results-grid">
            {results.map((h, i) => {
              const cong = getCongestionLevel(h.predicted_pressure, h.risk_level);
              const forecastTime = h.forecast_time
                ? new Date(h.forecast_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : null;

              return (
                <a
                  key={h.hospital_id}
                  href={mapsUrl(h.hospital_latitude, h.hospital_longitude, h.name)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hospital-card"
                  style={{ animationDelay: `${i * 70}ms` }}
                >
                  <div className="card-accent-bar" style={{ background: cong.accent }} />

                  <div className="card-top">
                    <span className="card-rank">#{i + 1}</span>
                    <span className="card-maps-hint">
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                        <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                      </svg>
                      Maps
                    </span>
                  </div>

                  <h3 className="card-name">{h.name}</h3>

                  <p className="card-distance">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{flexShrink:0}}>
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                    </svg>
                    {h.distance_km.toFixed(1)} {t.home.km_away}
                  </p>

                  <div className="card-cong-section">
                    <span className="cong-section-label">{t.home.forecasted_congestion}</span>
                    <div className="cong-badge-row">
                      <span className={`cong-badge cong-badge--${cong.key}`}>{cong.label}</span>
                    </div>
                    <div className="cong-dots" aria-label={`Congestion level ${cong.score} of 5`}>
                      {[1,2,3,4,5].map(n => (
                        <span key={n} className="cong-dot" style={{ background: n <= cong.score ? cong.accent : 'var(--border)' }} />
                      ))}
                    </div>
                  </div>

                  {forecastTime && (
                    <div className="card-footer-row">
                      <span className="forecast-chip">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                        </svg>
                        {t.home.forecast_at} {forecastTime}
                      </span>
                    </div>
                  )}
                </a>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}