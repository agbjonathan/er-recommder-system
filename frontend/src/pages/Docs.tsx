import { useState, useEffect } from 'react';
import { useLang } from '../i18n/LangContext';

// ─── Types ────────────────────────────────────────────────────────────────────

interface VersionEntry {
  version: string;
  date: string;
  type: 'major' | 'minor' | 'fix';
  title: string;
  changes: string[];
}

type DocSection = 'overview' | 'architecture' | 'pipeline' | 'api' | 'changelog';

// ─── Changelog data ───────────────────────────────────────────────────────────

const CHANGELOG: VersionEntry[] = [
  {
    version: '1.3.0',
    date: '2026-02-25',
    type: 'major',
    title: 'Analytics Dashboard',
    changes: [
      'Replaced static map page with full analytics dashboard',
      'Added global + per-hospital predicted vs observed pressure charts',
      'Added risk level distribution comparison (predicted vs observed)',
      'Added scatter plot for per-hospital calibration analysis',
      'Added new GET /api/dashboard/stats endpoint',
      'Fixed forecast timestamp corruption bug (future-dated forecasts)',
      'Added forecast_time sanity guard in forecast_service.py',
      'Added max_reasonable_future guard in forecast_storage.py',
      'Added retry logic for HTTP 503 ingestion failures',
    ],
  },
  {
    version: '1.2.1',
    date: '2026-02-20',
    type: 'fix',
    title: 'Bias Correction & Error Analysis',
    changes: [
      'Integrated get_recent_bias() into the forecast pipeline',
      'Added should_retrain() drift detection',
      'Fixed ARIMA model cache not invalidating after retrain',
      'Improved evaluate_forecasts scheduler reliability',
    ],
  },
  {
    version: '1.2.0',
    date: '2026-02-10',
    type: 'minor',
    title: 'Multi-horizon Forecasting',
    changes: [
      'Added support for horizon_hours in [1, 2, 4]',
      'Updated uq_forecast_unique constraint to include horizon_hours',
      'Per-hospital model cache keyed on (hospital_id, horizon_hours)',
      'Pressure → risk thresholds: LOW < 0.4, MEDIUM < 0.7, HIGH ≥ 0.7',
    ],
  },
  {
    version: '1.0.0',
    date: '2026-01-30',
    type: 'major',
    title: 'Initial Release',
    changes: [
      'ARIMA(2,1,2) per-hospital pressure forecasting pipeline',
      'Automated hourly ingestion from Québec open data portal',
      'APScheduler jobs: ingestion, forecasting, evaluation',
      'Hospital snapshot dataset builder with 72h lookback window',
      'FastAPI backend with SQLAlchemy + PostgreSQL',
      'React + TypeScript frontend',
    ],
  },
];

const TYPE_COLORS: Record<VersionEntry['type'], string> = {
  major: 'var(--teal)',
  minor: '#6366f1',
  fix: 'var(--accent)',
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function Code({ children }: { children: React.ReactNode }) {
  return <code className="docs-inline-code">{children}</code>;
}

function ApiRow({ method, path, desc }: { method: string; path: string; desc: string }) {
  const colors: Record<string, string> = {
    GET: 'var(--teal)', POST: '#6366f1', DELETE: '#ef4444', PATCH: 'var(--accent)',
  };
  return (
    <div className="api-row">
      <span className="api-method" style={{ color: colors[method] ?? 'var(--text-muted)' }}>{method}</span>
      <Code>{path}</Code>
      <span className="api-desc">{desc}</span>
    </div>
  );
}

function Section({ id, children }: { id: string; children: React.ReactNode }) {
  return <section id={id} className="docs-section">{children}</section>;
}

function H2({ children }: { children: React.ReactNode }) {
  return <h2 className="docs-h2">{children}</h2>;
}

function H3({ children }: { children: React.ReactNode }) {
  return <h3 className="docs-h3">{children}</h3>;
}

function P({ children }: { children: React.ReactNode }) {
  return <p className="docs-p">{children}</p>;
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Docs() {
  const { t } = useLang();
  const [activeSection, setActiveSection] = useState<DocSection>('overview');

  const SECTIONS: { id: DocSection; label: string; icon: string }[] = [
    { id: 'overview',     label: t.docs.nav_overview,      icon: '◈' },
    { id: 'architecture', label: t.docs.nav_architecture,  icon: '⬡' },
    { id: 'pipeline',     label: t.docs.nav_pipeline,      icon: '◎' },
    { id: 'api',          label: t.docs.nav_api,           icon: '⌘' },
    { id: 'changelog',    label: t.docs.nav_changelog,     icon: '◷' },
  ];

  // Track scroll to highlight active nav item
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(e => {
          if (e.isIntersecting) setActiveSection(e.target.id as DocSection);
        });
      },
      { threshold: 0.4 }
    );
    SECTIONS.forEach(s => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: DocSection) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="docs-page">
      <div className="docs-layout">

        {/* ── Sidebar ─────────────────────────────────────────── */}
        <aside className="docs-sidebar">
          <div className="docs-sidebar-identity">
            <div className="docs-logo">✚</div>
            <div>
              <div className="docs-app-name">ERGuide</div>
              <div className="docs-version-badge">v1.3.0</div>
            </div>
          </div>
          <p className="docs-sidebar-desc">{t.docs.sidebar_desc}</p>
          
          <nav className="docs-nav">
            {SECTIONS.map(s => (
              <button
                key={s.id}
                className={`docs-nav-link ${activeSection === s.id ? 'docs-nav-link--active' : ''}`}
                onClick={() => scrollTo(s.id)}
              >
                <span className="docs-nav-icon">{s.icon}</span>
                {s.label}
              </button>
            ))}
          </nav>

          <div className="docs-status-card">
            <div className="docs-status-title">{t.docs.status_title}</div>
            {[
              { label: t.docs.status_ingestion, ok: true },
              { label: t.docs.status_forecasting, ok: true },
              { label: t.docs.status_evaluation, ok: true },
              { label: t.docs.status_api, ok: true },
            ].map(s => (
              <div key={s.label} className="docs-status-row">
                <span className="docs-status-label">{s.label}</span>
                <span className={`docs-status-dot ${s.ok ? 'docs-status-dot--ok' : 'docs-status-dot--err'}`} />
              </div>
            ))}
          </div>
        </aside>

        {/* ── Content ─────────────────────────────────────────── */}
        <main className="docs-content">

          {/* Overview */}
          <Section id="overview">
            <div className="docs-hero">
              <div>
                <h1 className="docs-hero-title">{t.docs.hero_title}</h1>
                <div className="docs-hero-meta">
                <span className="docs-type-badge docs-type-badge--major">v1.3.0</span>
                <span className="docs-date">2026-02-25</span>
              </div>
              <P>{t.docs.hero_desc}</P>
              </div>
              <div>
                <a href="https://github.com/agbjonathan/er-recommder-system"
                target="_blank"
                rel="noopener noreferrer"
                className="docs-github-link"
                > 
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836a9.59 9.59 0 0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
                </svg>
                GitHub
                </a>
              </div>
            </div>

            <H2>{t.docs.overview_title}</H2>
            <div className="docs-feature-grid">
              {[
                { icon: '⬡', title: t.docs.feat_lookback_title, desc: t.docs.feat_lookback_desc },
                { icon: '◎', title: t.docs.feat_arima_title,    desc: t.docs.feat_arima_desc },
                { icon: '◈', title: t.docs.feat_bias_title,     desc: t.docs.feat_bias_desc },
                { icon: '✚', title: t.docs.feat_risk_title,     desc: t.docs.feat_risk_desc },
              ].map(f => (
                <div key={f.title} className="docs-feature-card">
                  <div className="docs-feature-icon">{f.icon}</div>
                  <div className="docs-feature-title">{f.title}</div>
                  <div className="docs-feature-desc">{f.desc}</div>
                </div>
              ))}
            </div>
          </Section>

          {/* Architecture */}
          <Section id="architecture">
            <H2>{t.docs.arch_title}</H2>
            <P>{t.docs.arch_desc}</P>

            <H3>{t.docs.arch_jobs_title}</H3>
            <div className="docs-code-block">
              {[
                { name: 'run_ingestion()',     interval: '1h', desc: t.docs.job_ingestion },
                { name: 'run_forecasting()',   interval: '1h', desc: t.docs.job_forecasting },
                { name: 'evaluate_forecasts()', interval: '1h', desc: t.docs.job_evaluation },
              ].map(j => (
                <div key={j.name} className="docs-code-row">
                  <span className="docs-code-key">{j.name}</span>
                  <span className="docs-code-tag">{j.interval}</span>
                  <span className="docs-code-desc">{j.desc}</span>
                </div>
              ))}
            </div>

            <H3>{t.docs.arch_structure_title}</H3>
            <div className="docs-code-block">
              {[
                ['app/ingestion/', t.docs.dir_ingestion],
                ['app/ml/',        t.docs.dir_ml],
                ['app/services/',  t.docs.dir_services],
                ['app/api/',       t.docs.dir_api],
                ['app/db/',        t.docs.dir_db],
              ].map(([path, desc]) => (
                <div key={path} className="docs-code-row">
                  <span className="docs-code-key" style={{ color: 'var(--teal)' }}>{path}</span>
                  <span className="docs-code-desc">{'# '}{desc}</span>
                </div>
              ))}
            </div>
          </Section>

          {/* ML Pipeline */}
          <Section id="pipeline">
            <H2>{t.docs.pipeline_title}</H2>
            <P>{t.docs.pipeline_desc}</P>

            <H3>{t.docs.pipeline_thresholds_title}</H3>
            <div className="docs-threshold-row">
              {[
                { label: 'LOW',    range: '< 0.4',      color: '#22c55e' },
                { label: 'MEDIUM', range: '0.4 – 0.7',  color: '#f59e0b' },
                { label: 'HIGH',   range: '≥ 0.7',      color: '#ef4444' },
              ].map(th => (
                <div key={th.label} className="docs-threshold-card" style={{ borderColor: th.color + '40' }}>
                  <div className="docs-threshold-label" style={{ color: th.color }}>{th.label}</div>
                  <div className="docs-threshold-range" style={{ color: th.color }}>{th.range}</div>
                </div>
              ))}
            </div>

            <H3>{t.docs.pipeline_known_title}</H3>
            <P>{t.docs.pipeline_known_desc}</P>
          </Section>

          {/* API Reference */}
          <Section id="api">
            <H2>{t.docs.api_title}</H2>
            <P>
              {t.docs.api_desc_before} <Code>http://localhost:8000</Code>.{' '}
              {t.docs.api_desc_swagger} <Code>/docs</Code> · <Code>/redoc</Code>.
            </P>

            <H3>{t.docs.api_forecasts}</H3>
            <ApiRow method="GET"  path="/api/forecasts"             desc={t.docs.api_forecasts_list} />
            <ApiRow method="GET"  path="/api/forecasts/{hospital_id}" desc={t.docs.api_forecasts_one} />

            <H3>{t.docs.api_hospitals}</H3>
            <ApiRow method="GET"  path="/api/hospitals"             desc={t.docs.api_hospitals_list} />
            <ApiRow method="GET"  path="/api/hospitals/{id}"        desc={t.docs.api_hospitals_one} />

            <H3>{t.docs.api_dashboard}</H3>
            <ApiRow method="GET"  path="/api/dashboard/congestion/map" desc={t.docs.api_dashboard_map} />
            <ApiRow method="GET"  path="/api/dashboard/stats"          desc={t.docs.api_dashboard_stats} />

            <div className="docs-callout">
              <span className="docs-callout-icon">💡</span>
              <div>
                <strong>{t.docs.api_new_endpoint_title}</strong>
                <p className="docs-p" style={{ marginTop: '.25rem' }}>
                  {t.docs.api_new_endpoint_desc}
                </p>
                <div className="docs-code-block" style={{ marginTop: '.75rem' }}>
                  <div className="docs-code-row"><span className="docs-code-desc">{'# GET /api/dashboard/stats?horizon_hours=1'}</span></div>
                  <div className="docs-code-row"><span className="docs-code-desc">{'# Returns: global_series, risk_comparison, hospital_stats'}</span></div>
                  <div className="docs-code-row"><span className="docs-code-desc">{'# File: app/api/forecasts.py  (or new dashboard.py)'}</span></div>
                  <div className="docs-code-row"><span className="docs-code-desc">{'# Queries Forecast + ERSnapshot and aggregates by hospital'}</span></div>
                </div>
              </div>
            </div>

            <H3>{t.docs.api_recommend}</H3>
            <ApiRow method="POST" path="/api/recommend"             desc={t.docs.api_recommend_desc} />

            <H3>{t.docs.api_feedback}</H3>
            <ApiRow method="POST" path="/api/feedback"              desc={t.docs.api_feedback_post} />
            <ApiRow method="GET"  path="/api/feedback"              desc={t.docs.api_feedback_get} />

            <H3>{t.docs.api_health}</H3>
            <ApiRow method="GET"  path="/api/health"                desc={t.docs.api_health_desc} />
          </Section>

          {/* Changelog */}
          <Section id="changelog">
            <H2>{t.docs.changelog_title}</H2>
            <div className="changelog">
              {CHANGELOG.map((entry, i) => (
                <div key={entry.version} className="changelog-entry" style={{ animationDelay: `${i * 60}ms` }}>
                  <div className="changelog-meta">
                    <span className="changelog-version">{entry.version}</span>
                    <div className="changelog-dot" style={{ background: TYPE_COLORS[entry.type] }} />
                  </div>
                  <div className="changelog-body">
                    <div className="changelog-header">
                      <span className="changelog-title">{entry.title}</span>
                      <span
                        className="docs-type-badge"
                        style={{ borderColor: TYPE_COLORS[entry.type] + '40', color: TYPE_COLORS[entry.type], background: TYPE_COLORS[entry.type] + '12' }}
                      >
                        {entry.type}
                      </span>
                      <span className="changelog-date">{entry.date}</span>
                    </div>
                    <ul className="changelog-list">
                      {entry.changes.map((c, j) => (
                        <li key={j} className="changelog-item">
                          <span className="changelog-dash">–</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </Section>
        </main>
      </div>
    </div>
  );
}