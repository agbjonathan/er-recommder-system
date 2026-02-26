import { useState, useRef, useEffect } from 'react';
import { submitFeedback } from '../api/client';
import { useLang } from '../i18n/LangContext';

type Category = 'ui' | 'accuracy' | 'suggestion';
type Mode = 'idle' | 'open' | 'submitting' | 'done';

interface FeedbackWidgetProps {
  variant: 'inline' | 'floating';
}

export default function FeedbackWidget({ variant }: FeedbackWidgetProps) {
  const { t } = useLang();
  const [mode, setMode] = useState<Mode>('idle');
  const [category, setCategory] = useState<Category | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (variant !== 'floating' || mode !== 'open') return;
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setMode('idle');
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [variant, mode]);

  const reset = () => {
    setCategory(null);
    setMessage('');
    setError(null);
    setMode('idle');
  };

  const handleSubmit = async () => {
    if (!category) { setError(t.feedback.error_category); return; }
    setError(null);
    setMode('submitting');
    try {
      await submitFeedback({ category, message: message.trim() || null });
      setMode('done');
      if (variant === 'floating') setTimeout(reset, 3000);
    } catch {
      setError(t.feedback.error_submit);
      setMode('open');
    }
  };

  const categories: { key: Category; label: string; icon: string }[] = [
    { key: 'ui',         label: t.feedback.cat_ui,         icon: '🎨' },
    { key: 'accuracy',   label: t.feedback.cat_accuracy,   icon: '🎯' },
    { key: 'suggestion', label: t.feedback.cat_suggestion, icon: '💡' },
  ];

  const isOpen = mode === 'open' || mode === 'submitting';

  // ── INLINE variant ────────────────────────────────────────
  if (variant === 'inline') {
    return (
      <div className="fb-inline">
        {mode === 'done' ? (
          <div className="fb-done">
            <span className="fb-done-icon">✓</span>
            <p className="fb-done-text">{t.feedback.thanks}</p>
          </div>
        ) : isOpen ? (
          <>
            <div className="fb-inline-header">
              <span className="fb-inline-title">{t.feedback.inline_title}</span>
            </div>
            <div className="fb-form">
              <p className="fb-form-label">{t.feedback.category_label}</p>
              <div className="fb-categories">
                {categories.map(c => (
                  <button
                    key={c.key}
                    type="button"
                    onClick={() => setCategory(c.key)}
                    className={`fb-cat-btn ${category === c.key ? 'fb-cat-btn--active' : ''}`}
                  >
                    <span>{c.icon}</span>
                    {c.label}
                  </button>
                ))}
              </div>
              <textarea
                className="fb-textarea"
                placeholder={t.feedback.message_placeholder}
                value={message}
                onChange={e => setMessage(e.target.value)}
                maxLength={1000}
                rows={3}
              />
              <div className="fb-char-count">{message.length}/1000</div>
              {error && <p className="fb-error">{error}</p>}
              <div className="fb-actions">
                <button type="button" className="fb-btn-cancel" onClick={reset}>
                  {t.feedback.cancel}
                </button>
                <button
                  type="button"
                  className="fb-btn-submit"
                  onClick={handleSubmit}
                  disabled={mode === 'submitting'}
                >
                  {mode === 'submitting' ? t.feedback.sending : t.feedback.submit}
                </button>
              </div>
            </div>
          </>
        ) : (
          <button className="fb-inline-trigger" onClick={() => setMode('open')}>
            <span>💬</span>
            {t.feedback.inline_cta}
          </button>
        )}
      </div>
    );
  }

  // ── FLOATING variant ──────────────────────────────────────
  return (
    <div className="fb-floating-root" ref={panelRef}>
      {(isOpen || mode === 'done') && (
        <div className="fb-floating-panel">
          <div className="fb-floating-header">
            <span className="fb-floating-title">{t.feedback.floating_title}</span>
            <button className="fb-floating-close" onClick={reset} aria-label="Close">✕</button>
          </div>
          {mode === 'done' ? (
            <div className="fb-done">
              <span className="fb-done-icon">✓</span>
              <p className="fb-done-text">{t.feedback.thanks}</p>
            </div>
          ) : (
            <div className="fb-form">
              <p className="fb-form-label">{t.feedback.category_label}</p>
              <div className="fb-categories">
                {categories.map(c => (
                  <button
                    key={c.key}
                    type="button"
                    onClick={() => setCategory(c.key)}
                    className={`fb-cat-btn ${category === c.key ? 'fb-cat-btn--active' : ''}`}
                  >
                    <span>{c.icon}</span>
                    {c.label}
                  </button>
                ))}
              </div>
              <textarea
                className="fb-textarea"
                placeholder={t.feedback.message_placeholder}
                value={message}
                onChange={e => setMessage(e.target.value)}
                maxLength={1000}
                rows={3}
              />
              <div className="fb-char-count">{message.length}/1000</div>
              {error && <p className="fb-error">{error}</p>}
              <div className="fb-actions">
                <button type="button" className="fb-btn-cancel" onClick={reset}>
                  {t.feedback.cancel}
                </button>
                <button
                  type="button"
                  className="fb-btn-submit"
                  onClick={handleSubmit}
                  disabled={mode === 'submitting'}
                >
                  {mode === 'submitting' ? t.feedback.sending : t.feedback.submit}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      <button
        className={`fb-fab ${mode === 'open' ? 'fb-fab--active' : ''}`}
        onClick={() => mode === 'idle' ? setMode('open') : reset()}
        aria-label={t.feedback.fab_label}
        title={t.feedback.fab_label}
      >
        {mode === 'open' ? '✕' : '💬'}
      </button>
    </div>
  );
}