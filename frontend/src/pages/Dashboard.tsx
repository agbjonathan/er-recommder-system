import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import {
  LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts';
import { getCongestionMap, getDashboardStats } from '../api/client';
import type {
  CongestionFeature, DashboardStatsResponse,
  HospitalPressureStat, PressureSeriesPoint,
} from '../api/client';
import { useLang } from '../i18n/LangContext';
import 'leaflet/dist/leaflet.css';

// ─── Types ────────────────────────────────────────────────────────────────────

type Tab = 'overview' | 'pressure' | 'risk' | 'map';
type Horizon = 1 | 2 | 4;

// ─── Helpers ──────────────────────────────────────────────────────────────────

const RISK_COLORS: Record<string, string> = {
  LOW: '#22c55e',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444',
  low: '#22c55e',
  medium: '#f59e0b',
  high: '#ef4444',
};

const riskColor = (r: string | null) => RISK_COLORS[r ?? ''] ?? '#94a3b8';

const pressureColor = (v: number) =>
  v >= 1.0 ? '#ef4444' : v >= 0.7 ? '#f59e0b' : '#22c55e';

// Custom tooltip consistent with the app's design system
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      {label && <p className="chart-tooltip-label">{label}</p>}
      {payload.map((p: any) => (
        <p key={p.name} className="chart-tooltip-row" style={{ color: p.color }}>
          <span>{p.name}:</span>
          <span>{typeof p.value === 'number' ? p.value.toFixed(3) : p.value}</span>
        </p>
      ))}
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="chart-section-label">{children}</p>;
}

function ChartCard({ children, span2 = false }: { children: React.ReactNode; span2?: boolean }) {
  return (
    <div className={`chart-card ${span2 ? 'chart-card--span2' : ''}`}>
      {children}
    </div>
  );
}

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="kpi-card">
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Dashboard() {
  const { t } = useLang();

  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [horizon, setHorizon] = useState<Horizon>(1);
  const [selectedHospital, setSelectedHospital] = useState<number | 'all'>('all');

  // Data states
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [mapFeatures, setMapFeatures] = useState<CongestionFeature[]>([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [mapLoading, setMapLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load chart stats whenever horizon changes
  useEffect(() => {
    setStatsLoading(true);
    setError(null);
    getDashboardStats(horizon)
      .then(res => setStats(res.data))
      .catch(() => setError(t.dashboard.error_load))
      .finally(() => setStatsLoading(false));
  }, [horizon]);

  // Load map data once
  useEffect(() => {
    getCongestionMap(horizon)
      .then(res => setMapFeatures(res.data.features))
      .catch(console.error)
      .finally(() => setMapLoading(false));
  }, []);

  // Derived chart data
  const globalSeries: PressureSeriesPoint[] = stats?.global_series ?? [];
  const riskComparison = stats?.risk_comparison ?? [];
  const hospitalStats: HospitalPressureStat[] = stats?.hospital_stats ?? [];

  const filteredSeries =
    selectedHospital === 'all'
      ? globalSeries
      : globalSeries; // per-hospital series would come from a separate API call

  const scatterData = hospitalStats.map(h => ({
    name: h.name,
    x: h.mean_observed ?? 0,
    y: h.mean_predicted,
    risk: h.risk_level,
  }));

  // KPIs
  const highRiskCount = hospitalStats.filter(h => h.risk_level === 'HIGH').length;
  const meanPredicted = hospitalStats.length
    ? hospitalStats.reduce((s, h) => s + h.mean_predicted, 0) / hospitalStats.length
    : null;
  const evaluatedCount = riskComparison.reduce((s, r) => s + r.observed, 0);

  const TABS: { id: Tab; label: string }[] = [
    { id: 'overview', label: t.dashboard.tab_overview },
    { id: 'pressure', label: t.dashboard.tab_pressure },
    { id: 'risk',     label: t.dashboard.tab_risk },
    { id: 'map',      label: t.dashboard.tab_map },
  ];

  return (
    <div className="dashboard-page">

      {/* ── Page header ───────────────────────────────────────── */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">{t.dashboard.title}</h1>
          <p className="dashboard-subtitle">{t.dashboard.subtitle}</p>
        </div>

        <div className="dashboard-controls">
          {/* Horizon selector */}
          <div className="horizon-selector">
            {([1, 2, 4] as Horizon[]).map(h => (
              <button
                key={h}
                className={`horizon-btn ${horizon === h ? 'horizon-btn--active' : ''}`}
                onClick={() => setHorizon(h)}
              >
                +{h}h
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── KPI strip ─────────────────────────────────────────── */}
      <div className="dashboard-kpis">
        <KpiCard
          label={t.dashboard.kpi_mean_predicted}
          value={meanPredicted != null ? meanPredicted.toFixed(3) : '—'}
          sub={t.dashboard.kpi_horizon.replace('{h}', String(horizon))}
        />
        <KpiCard
          label={t.dashboard.kpi_high_risk}
          value={statsLoading ? '—' : String(highRiskCount)}
          sub={t.dashboard.kpi_hospitals.replace('{n}', String(hospitalStats.length))}
        />
        <KpiCard
          label={t.dashboard.kpi_evaluated}
          value={statsLoading ? '—' : String(evaluatedCount)}
          sub={t.dashboard.kpi_forecasts}
        />
        <KpiCard
          label={t.dashboard.kpi_updated}
          value={stats ? new Date(stats.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
        />
      </div>

      {/* ── Tabs ──────────────────────────────────────────────── */}
      <div className="dashboard-tabs">
        {TABS.map(tab => (
          <button
            key={tab.id}
            className={`dashboard-tab ${activeTab === tab.id ? 'dashboard-tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Error state ───────────────────────────────────────── */}
      {error && <p className="error-msg" style={{ marginBottom: '1.5rem' }}>{error}</p>}

      {/* ── Loading skeleton ──────────────────────────────────── */}
      {statsLoading && activeTab !== 'map' && (
        <div className="dashboard-loading">
          <div className="spinner" />
          <p>{t.dashboard.loading}</p>
        </div>
      )}

      {/* ── Tab content ───────────────────────────────────────── */}
      {!statsLoading && (
        <div className="dashboard-tab-content">

          {/* ── OVERVIEW ── */}
          {activeTab === 'overview' && (
            <div className="charts-grid">
              <ChartCard span2>
                <SectionLabel>{t.dashboard.chart_global_series}</SectionLabel>
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={filteredSeries}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="label" tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} domain={[0, 'auto']} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend wrapperStyle={{ fontSize: 12, fontFamily: 'DM Sans, sans-serif' }} />
                    <ReferenceLine y={0.7} stroke="#f59e0b" strokeDasharray="4 3" strokeOpacity={0.6} />
                    <ReferenceLine y={1.0} stroke="#ef4444" strokeDasharray="4 3" strokeOpacity={0.6} />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      name={t.dashboard.legend_predicted}
                      stroke="var(--teal)"
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="observed"
                      name={t.dashboard.legend_observed}
                      stroke="var(--navy-mid)"
                      strokeWidth={2}
                      strokeDasharray="5 3"
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard>
                <SectionLabel>{t.dashboard.chart_risk_distribution}</SectionLabel>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={riskComparison} barGap={4}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="risk" tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend wrapperStyle={{ fontSize: 12, fontFamily: 'DM Sans, sans-serif' }} />
                    <Bar dataKey="predicted" name={t.dashboard.legend_predicted} radius={[4, 4, 0, 0]}>
                      {riskComparison.map(entry => (
                        <Cell key={entry.risk} fill={riskColor(entry.risk)} />
                      ))}
                    </Bar>
                    <Bar dataKey="observed" name={t.dashboard.legend_observed} fill="var(--border)" stroke="var(--text-muted)" strokeWidth={1} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard>
                <SectionLabel>{t.dashboard.chart_hospital_bar}</SectionLabel>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={hospitalStats} layout="vertical" barSize={10}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                    <XAxis type="number" domain={[0, 1.5]} tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <Tooltip content={<ChartTooltip />} />
                    <ReferenceLine x={0.7} stroke="#f59e0b" strokeDasharray="3 3" strokeOpacity={0.7} />
                    <ReferenceLine x={1.0} stroke="#ef4444" strokeDasharray="3 3" strokeOpacity={0.7} />
                    <Bar dataKey="mean_predicted" name={t.dashboard.legend_predicted} radius={[0, 4, 4, 0]}>
                      {hospitalStats.map(h => (
                        <Cell key={h.hospital_id} fill={pressureColor(h.mean_predicted)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
          )}

          {/* ── PRESSURE ── */}
          {activeTab === 'pressure' && (
            <div className="charts-grid">
              <div className="chart-card chart-card--span2 pressure-tab-controls">
              <label className="search-label">{t.dashboard.all_hospitals}</label>
              <select
                className="hospital-select"
                value={selectedHospital}
                onChange={e =>
                  setSelectedHospital(e.target.value === 'all' ? 'all' : Number(e.target.value))
              }
            >
                <option value="all">{t.dashboard.all_hospitals}</option>
                {hospitalStats.map(h => (
                <option key={h.hospital_id} value={h.hospital_id}>{h.name}</option>
                ))}
              </select>
            </div>
              <ChartCard span2>
                <SectionLabel>
                  {selectedHospital === 'all' ? t.dashboard.chart_global_series : `${hospitalStats.find(h => h.hospital_id === selectedHospital)?.name ?? ''} · ${t.dashboard.chart_pressure_horizon.replace('{h}', String(horizon))}`}
                  {t.dashboard.chart_pressure_horizon.replace('{h}', String(horizon))}
                </SectionLabel>
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={filteredSeries}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="label" tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend wrapperStyle={{ fontSize: 12, fontFamily: 'DM Sans, sans-serif' }} />
                    <ReferenceLine y={0.7} label={{ value: 'MEDIUM', fontSize: 9, fill: '#f59e0b', fontFamily: 'Sora, sans-serif' }} stroke="#f59e0b" strokeDasharray="4 3" strokeOpacity={0.5} />
                    <ReferenceLine y={1.0} label={{ value: 'HIGH', fontSize: 9, fill: '#ef4444', fontFamily: 'Sora, sans-serif' }} stroke="#ef4444" strokeDasharray="4 3" strokeOpacity={0.5} />
                    <Line type="monotone" dataKey="predicted" name={t.dashboard.legend_predicted} stroke="var(--teal)" strokeWidth={2.5} dot={false} />
                    <Line type="monotone" dataKey="observed" name={t.dashboard.legend_observed} stroke="var(--accent)" strokeWidth={2} strokeDasharray="5 3" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard span2>
                <SectionLabel>{t.dashboard.chart_scatter}</SectionLabel>
                <p className="chart-hint">{t.dashboard.chart_scatter_hint}</p>
                <ResponsiveContainer width="100%" height={280}>
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis
                      dataKey="x"
                      name={t.dashboard.legend_observed}
                      tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }}
                      label={{ value: t.dashboard.legend_observed, position: 'insideBottom', offset: -10, fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }}
                    />
                    <YAxis
                      dataKey="y"
                      name={t.dashboard.legend_predicted}
                      tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }}
                      label={{ value: t.dashboard.legend_predicted, angle: -90, position: 'insideLeft', offset: 10, fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }}
                    />
                    <Tooltip content={<ChartTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                    {/* Perfect calibration line */}
                    <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 1.5, y: 1.5 }]} stroke="var(--border)" strokeDasharray="5 3" />
                    <Scatter data={scatterData} name={t.dashboard.chart_scatter}>
                      {scatterData.map((d, i) => (
                        <Cell key={i} fill={riskColor(d.risk)} fillOpacity={0.85} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
                <div className="chart-legend-row">
                  {(['LOW', 'MEDIUM', 'HIGH'] as const).map(r => (
                    <span key={r} className="chart-legend-item">
                      <span className="chart-legend-dot" style={{ background: riskColor(r) }} />
                      {r}
                    </span>
                  ))}
                  <span className="chart-legend-item" style={{ marginLeft: 'auto', fontStyle: 'italic', fontSize: '.72rem' }}>
                    {t.dashboard.scatter_diagonal}
                  </span>
                </div>
              </ChartCard>
            </div>
          )}

          {/* ── RISK ── */}
          {activeTab === 'risk' && (
            <div className="charts-grid">
              <ChartCard span2>
                <SectionLabel>{t.dashboard.chart_risk_global}</SectionLabel>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={riskComparison} barCategoryGap="35%">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="risk" tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'DM Sans, sans-serif' }} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend wrapperStyle={{ fontSize: 12, fontFamily: 'DM Sans, sans-serif' }} />
                    <Bar dataKey="predicted" name={t.dashboard.legend_predicted} radius={[4, 4, 0, 0]}>
                      {riskComparison.map(e => (
                        <Cell key={e.risk} fill={riskColor(e.risk)} />
                      ))}
                    </Bar>
                    <Bar dataKey="observed" name={t.dashboard.legend_observed} fill="#e2e8f0" stroke="var(--text-muted)" strokeWidth={1} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Per-hospital risk cards */}
              {hospitalStats.map(h => (
                <div key={h.hospital_id} className="hospital-stat-card">
                  <div className="hospital-stat-header">
                    <span className="hospital-stat-name">{h.name}</span>
                    <span className={`risk-badge risk-badge--${h.risk_level.toLowerCase()}`}>
                      {h.risk_level}
                    </span>
                  </div>
                  <div className="hospital-stat-bars">
                    <div className="pressure-bar-row">
                      <span className="pressure-bar-label">{t.dashboard.legend_predicted}</span>
                      <div className="pressure-bar-track">
                        <div
                          className="pressure-bar-fill"
                          style={{
                            width: `${Math.min(h.mean_predicted / 1.5 * 100, 100)}%`,
                            background: riskColor(h.risk_level),
                          }}
                        />
                      </div>
                      <span className="pressure-bar-value" style={{ color: riskColor(h.risk_level) }}>
                        {h.mean_predicted.toFixed(3)}
                      </span>
                    </div>
                    {h.mean_observed != null && (
                      <div className="pressure-bar-row">
                        <span className="pressure-bar-label">{t.dashboard.legend_observed}</span>
                        <div className="pressure-bar-track">
                          <div
                            className="pressure-bar-fill pressure-bar-fill--observed"
                            style={{ width: `${Math.min(h.mean_observed / 1.5 * 100, 100)}%` }}
                          />
                        </div>
                        <span className="pressure-bar-value" style={{ color: 'var(--text-muted)' }}>
                          {h.mean_observed.toFixed(3)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ── MAP ── */}
          {activeTab === 'map' && (
            <div>
              <p className="chart-hint" style={{ marginBottom: '1rem' }}>
                {t.dashboard.map_hint}
              </p>
              {mapLoading ? (
                <div className="map-loading">
                  <div className="spinner" />
                  <p>{t.dashboard.loading}</p>
                </div>
              ) : (
                <>
                  <div className="map-container">
                    <MapContainer center={[45.5, -73.6]} zoom={10} className="leaflet-map">
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      />
                      {mapFeatures.map(f => (
                        <CircleMarker
                          key={f.properties.hospital_id}
                          center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
                          radius={14}
                          fillColor={riskColor(f.properties.risk_level)}
                          fillOpacity={0.85}
                          stroke
                          color="#ffffff"
                          weight={2.5}
                        >
                          <Popup className="custom-popup">
                            <strong>{f.properties.name}</strong>
                            <br />
                            {t.dashboard.map_risk}: {f.properties.risk_level ?? t.dashboard.map_unknown}
                            <br />
                            {t.dashboard.map_pressure}: {f.properties.predicted_pressure?.toFixed(2) ?? 'N/A'}
                          </Popup>
                        </CircleMarker>
                      ))}
                    </MapContainer>
                  </div>
                  <div className="map-legend">
                    {(['LOW', 'MEDIUM', 'HIGH'] as const).map(r => (
                      <div key={r} className="legend-item">
                        <span className="legend-dot" style={{ background: riskColor(r) }} />
                        {t.dashboard[`map_legend_${r.toLowerCase()}` as keyof typeof t.dashboard]}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}