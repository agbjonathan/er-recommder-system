import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import Map from './pages/Map';
import { LangProvider, useLang } from './i18n/LangContext';
import FeedbackWidget from './components/FeedbackWidget';

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const location = useLocation();
  const active = location.pathname === to;
  return (
    <Link to={to} className={`nav-link ${active ? 'nav-link--active' : ''}`}>
      {children}
    </Link>
  );
}

function Layout() {
  const { lang, setLang, t } = useLang();

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <span className="brand-cross">✚</span>
            <span className="brand-name">{t.nav.appName}</span>
          </div>
          <nav className="header-nav">
            <NavLink to="/">{t.nav.home}</NavLink>
            <NavLink to="/map">{t.nav.map}</NavLink>
          </nav>
          <div className="lang-switcher">
            <button onClick={() => setLang('en')} className={`lang-btn ${lang === 'en' ? 'lang-btn--active' : ''}`}>EN</button>
            <span className="lang-sep">|</span>
            <button onClick={() => setLang('fr')} className={`lang-btn ${lang === 'fr' ? 'lang-btn--active' : ''}`}>FR</button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/map" element={<Map />} />
        </Routes>
      </main>

      <footer className="app-footer">
        <div className="footer-inner">
          <div className="footer-meta">
            <span>{t.footer.demo_note}</span>
            <span className="footer-dot">·</span>
            <a href="https://jonathan-agba.com" target="_blank" rel="noopener noreferrer" className="footer-link">
              Jonathan Agba ↗
            </a>
          </div>
          <div className="footer-tagline">{t.footer.tagline}</div>
        </div>
      </footer>
      {/* Floating feedback button — always visible */}
      <FeedbackWidget variant="floating" />
    </div>
  );
}

export default function App() {
  return (
    <LangProvider>
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    </LangProvider>
  );
}