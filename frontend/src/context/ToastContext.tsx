import React, { createContext, useCallback, useContext, useRef, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (title: string, message?: string) => void;
  error: (title: string, message?: string) => void;
  info: (title: string, message?: string) => void;
  warning: (title: string, message?: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

const TOAST_ICONS: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
  warning: '⚠',
};

const TOAST_COLORS: Record<ToastType, { bg: string; border: string; color: string }> = {
  success: { bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.4)', color: '#34d399' },
  error:   { bg: 'rgba(244,63,94,0.12)',  border: 'rgba(244,63,94,0.4)',  color: '#fb7185' },
  info:    { bg: 'rgba(56,189,248,0.12)', border: 'rgba(56,189,248,0.4)', color: '#38bdf8' },
  warning: { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.4)', color: '#fbbf24' },
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
    const timer = timersRef.current.get(id);
    if (timer) { clearTimeout(timer); timersRef.current.delete(id); }
  }, []);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
    const duration = toast.duration ?? 4500;
    setToasts(prev => [...prev.slice(-4), { ...toast, id }]); // max 5 toasts
    const timer = setTimeout(() => removeToast(id), duration);
    timersRef.current.set(id, timer);
  }, [removeToast]);

  const success = useCallback((title: string, message?: string) => addToast({ type: 'success', title, message }), [addToast]);
  const error   = useCallback((title: string, message?: string) => addToast({ type: 'error',   title, message }), [addToast]);
  const info    = useCallback((title: string, message?: string) => addToast({ type: 'info',    title, message }), [addToast]);
  const warning = useCallback((title: string, message?: string) => addToast({ type: 'warning', title, message }), [addToast]);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, info, warning }}>
      {children}
      {/* Toast Container */}
      <div
        style={{
          position: 'fixed',
          bottom: '1.5rem',
          right: '1.5rem',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          gap: '0.6rem',
          pointerEvents: 'none',
        }}
      >
        {toasts.map(t => {
          const c = TOAST_COLORS[t.type];
          return (
            <div
              key={t.id}
              style={{
                pointerEvents: 'all',
                background: c.bg,
                border: `1px solid ${c.border}`,
                borderRadius: '10px',
                padding: '0.8rem 1.1rem',
                minWidth: '260px',
                maxWidth: '380px',
                backdropFilter: 'blur(20px)',
                boxShadow: '0 8px 30px rgba(0,0,0,0.4)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.65rem',
                animation: 'slideInRight 0.25s ease',
              }}
            >
              <span style={{ fontSize: '1rem', color: c.color, fontWeight: 800, flexShrink: 0, marginTop: '0.05rem' }}>
                {TOAST_ICONS[t.type]}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 700, fontSize: '0.84rem', color: '#f8fafc' }}>{t.title}</div>
                {t.message && <div style={{ fontSize: '0.77rem', color: '#94a3b8', marginTop: '0.2rem' }}>{t.message}</div>}
              </div>
              <button
                onClick={() => removeToast(t.id)}
                style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', fontSize: '1rem', flexShrink: 0 }}
              >×</button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextValue => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx;
};
