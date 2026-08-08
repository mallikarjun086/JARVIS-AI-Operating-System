import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Search, Activity, Cpu, Menu } from 'lucide-react';

interface NavbarProps {
  onToggleMobileMenu?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileMenu }) => {
  const { user, logout } = useAuth();

  return (
    <header className="top-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {onToggleMobileMenu && (
          <button onClick={onToggleMobileMenu} className="mobile-toggle-btn" title="Toggle Navigation Menu">
            <Menu size={18} />
          </button>
        )}

        <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Cpu size={18} color="#06b6d4" />
          <span>JARVIS AI OS KERNEL</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0.35rem 0.75rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          <Activity size={14} color="#10b981" />
          <span style={{ color: '#34d399', fontWeight: 600 }}>8/8 Subsystems Online</span>
          <span style={{ color: 'var(--border-color)' }}>|</span>
          <span>10 Swarm Agents</span>
          <span style={{ color: 'var(--border-color)' }}>|</span>
          <span style={{ color: '#38bdf8' }}>Latency: 14ms</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '0.35rem 0.85rem',
          fontSize: '0.8rem',
          color: 'var(--text-dim)',
          cursor: 'pointer'
        }}>
          <Search size={14} />
          <span>Quick Command...</span>
          <kbd style={{ background: 'rgba(255, 255, 255, 0.08)', padding: '0.1rem 0.35rem', borderRadius: '4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>Ctrl + K</kbd>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '0.35rem 0.75rem' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'linear-gradient(135deg, #06b6d4, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.8rem', color: '#fff' }}>
            {user?.email?.charAt(0).toUpperCase() || 'A'}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#f8fafc' }}>{user?.full_name || user?.email}</span>
            {user?.is_superuser && (
              <span style={{ fontSize: '0.65rem', color: '#34d399', fontWeight: 700, letterSpacing: '0.05em' }}>SYS_ADMIN</span>
            )}
          </div>
        </div>

        <button
          onClick={logout}
          className="btn-secondary"
          style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
          title="Sign Out"
        >
          <LogOut size={14} />
          <span>Exit</span>
        </button>
      </div>
    </header>
  );
};
