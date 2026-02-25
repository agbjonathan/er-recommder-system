import { useState } from 'react';
import { getRecommendations, Hospital } from '../api/client';
import { useLang } from '../i18n/LangContext';

export default function Home() {
  const { t } = useLang();
  const [address, setAddress] = useState('');
  const [results, setResults] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddressSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) return;
    setLoading(true);
    setError(null);
    try {
      // Geocode address using Nominatim (free, no key needed)
      const geoRes = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`,
        { headers: { 'Accept-Language': 'en' } }
      );
      const geoData = await geoRes.json();
      if (!geoData.length) {
        setError('Address not found. Please try a more specific address.');
        return;
      }
      const lat = parseFloat(geoData[0].lat);
      const lng = parseFloat(geoData[0].lon);
      const res = await getRecommendations(lat, lng);
      setResults(res.data.results);
    } catch {
      setError(t.home.error_fetch);
    } finally {
      setLoading(false);
    }
  };

  const handleLocate = () => {
    if (!navigator.geolocation) {
      setError(t.home.error_geo_unsupported);
      return;
    }
    setLocating(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const res = await getRecommendations(pos.coords.latitude, pos.coords.longitude);
          setResults(res.data.results);
        } catch {
          setError(t.home.error_fetch);
        } finally {
          setLocating(false);
        }
      },
      () => {
        setError(t.home.error_geo);
        setLocating(false);
      },
      { timeout: 8000 }
    );
  };

  const riskClass = (risk: string | null) => {
    switch (risk) {
      case 'low': return 'risk-badge risk-badge--low';
      case 'medium': return 'risk-badge risk-badge--medium';
      case 'high': return 'risk-badge risk-badge--high';
      default: return 'risk-badge risk-badge--unknown';
    }
  };

  const riskLabel = (risk: string | null) => {
    switch (risk) {
      case 'low': return t.home.risk_low;
      case 'medium': return t.home.risk_medium;
      case 'high': return t.home.risk_high;
      default: return t.home.risk_unknown;
    }
  };

  const pressureBar = (val: number | null) => {
    const pct = val != null ? Math.min(Math.max(val * 100, 0), 100) : 0;
    const color = val == null ? '#94a3b8' : val < 0.4 ? '#22c55e' : val < 0.7 ? '#f59e0b' : '#ef4444';
    return (
      <div className="pressure-bar-wrap">
        <div className="pressure-bar-track">
          <div className="pressure-bar-fill" style={{ width: `${pct}%`, background: color }} />
        </div>
        <span className="pressure-bar-val">{val != null ? val.toFixed(2) : '—'}</span>
      </div>
    );
  };

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

      {/* Disclaimer */}
      <div className="disclaimer-banner">
        <div className="disclaimer-inner">
          <p className="disclaimer-title">{t.home.disclaimer_title}</p>
          <p className="disclaimer-body">{t.home.disclaimer_body}</p>
        </div>
      </div>

      {/* Search */}
      <section className="search-section">
        <form onSubmit={handleAddressSearch} className="search-form">
          <label className="search-label">{t.home.address_label}</label>
          <div className="search-row">
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder={t.home.address_placeholder}
              className="search-input"
            />
            <button
              type="submit"
              disabled={loading || !address.trim()}
              className="btn btn-primary"
            >
              {loading ? t.home.searching : t.home.btn_search}
            </button>
          </div>
        </form>

        <div className="divider-row">
          <span className="divider-line" />
          <span className="divider-text">or</span>
          <span className="divider-line" />
        </div>

        <div className="locate-row">
          <button
            onClick={handleLocate}
            disabled={locating}
            className="btn btn-secondary"
          >
            <span className="btn-icon">📍</span>
            {locating ? t.home.locating : t.home.btn_locate}
          </button>
        </div>

        {error && <p className="error-msg">{error}</p>}
      </section>

      {/* Results */}
      {results.length > 0 && (
        <section className="results-section">
          <h2 className="results-title">{t.home.results_title}</h2>
          <div className="results-grid">
            {results.map((h, i) => (
              <div key={h.hospital_id} className="hospital-card" style={{ animationDelay: `${i * 60}ms` }}>
                <div className="card-header">
                  <span className="card-rank">#{i + 1}</span>
                  <span className={riskClass(h.risk_level)}>{riskLabel(h.risk_level)}</span>
                </div>
                <h3 className="card-name">{h.name}</h3>
                <p className="card-distance">
                  <span className="card-distance-icon">📍</span>
                  {h.distance_km.toFixed(1)} {t.home.km_away}
                </p>
                <div className="card-pressure-row">
                  <span className="pressure-label-text">{t.home.pressure_label}</span>
                  {pressureBar(h.predicted_pressure)}
                </div>
                {h.forecast_time && (
                  <p className="card-forecast-time">
                    🕐 {new Date(h.forecast_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
