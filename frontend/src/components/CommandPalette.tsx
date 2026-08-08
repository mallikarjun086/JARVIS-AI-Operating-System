import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, LayoutDashboard, Terminal, Brain, Eye, Mic, GitBranch, Shield, Cpu, Globe, Settings, Search } from 'lucide-react';

interface CommandItem {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  action: () => void;
  shortcut?: string;
}

interface CommandPaletteProps {
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ onClose }) => {
  const [query, setQuery] = useState('');
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const navTo = useCallback((path: string) => { navigate(path); onClose(); }, [navigate, onClose]);

  const ALL_COMMANDS: CommandItem[] = [
    { id: 'jarvis', label: 'JARVIS Command Center', description: 'Open multimodal voice & chat HUD', icon: <Bot size={16} color="#00f2fe" />, action: () => navTo('/jarvis-command-center'), shortcut: '⌘J' },
    { id: 'dashboard', label: 'Dashboard', description: 'System overview and live metrics', icon: <LayoutDashboard size={16} color="#38bdf8" />, action: () => navTo('/dashboard') },
    { id: 'ai', label: 'AI Console', description: 'Multi-provider LLM chat interface', icon: <Cpu size={16} color="#c084fc" />, action: () => navTo('/ai-console') },
    { id: 'memory', label: 'Memory Console', description: 'ChromaDB vector memory RAG store', icon: <Brain size={16} color="#a78bfa" />, action: () => navTo('/memory-console') },
    { id: 'planner', label: 'Task Planner', description: 'DAG task decomposition engine', icon: <Terminal size={16} color="#34d399" />, action: () => navTo('/planner-console') },
    { id: 'multi-agent', label: 'Multi-Agent Swarm', description: '10-agent orchestration mesh', icon: <Cpu size={16} color="#fbbf24" />, action: () => navTo('/multi-agent-console') },
    { id: 'vision', label: 'Vision Console', description: 'Computer vision & screenshot AI', icon: <Eye size={16} color="#fb923c" />, action: () => navTo('/vision-console') },
    { id: 'voice', label: 'Voice Console', description: 'STT/TTS voice assistant engine', icon: <Mic size={16} color="#f472b6" />, action: () => navTo('/voice-console') },
    { id: 'browser', label: 'Browser Automation', description: 'Playwright web automation console', icon: <Globe size={16} color="#38bdf8" />, action: () => navTo('/browser-console') },
    { id: 'swe', label: 'SWE Agent', description: 'Software engineering automation', icon: <GitBranch size={16} color="#34d399" />, action: () => navTo('/swe-console') },
    { id: 'security', label: 'Security Console', description: 'RBAC, vault & compliance dashboard', icon: <Shield size={16} color="#fb7185" />, action: () => navTo('/security-console') },
    { id: 'settings', label: 'Settings', description: 'System configuration & preferences', icon: <Settings size={16} color="#94a3b8" />, action: () => navTo('/settings') },
  ];

  const filtered = query.trim()
    ? ALL_COMMANDS.filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase()) ||
        c.description.toLowerCase().includes(query.toLowerCase())
      )
    : ALL_COMMANDS;

  useEffect(() => { setSelectedIdx(0); }, [query]);

  useEffect(() => {
    inputRef.current?.focus();
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowDown') setSelectedIdx(i => Math.min(i + 1, filtered.length - 1));
      if (e.key === 'ArrowUp') setSelectedIdx(i => Math.max(i - 1, 0));
      if (e.key === 'Enter') { filtered[selectedIdx]?.action(); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [filtered, onClose, selectedIdx]);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(4,7,17,0.8)',
        backdropFilter: 'blur(12px)', zIndex: 500,
        display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
        paddingTop: '12vh',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: 'rgba(10,14,26,0.98)', border: '1px solid rgba(56,189,248,0.25)',
          borderRadius: '14px', width: '100%', maxWidth: '600px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(56,189,248,0.1)',
          overflow: 'hidden',
        }}
      >
        {/* Search Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem 1.2rem', borderBottom: '1px solid rgba(255,255,255,0.07)' }}>
          <Search size={18} color="#64748b" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search pages and actions…"
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: '#f8fafc', fontSize: '1rem', fontFamily: 'var(--font-family)',
            }}
          />
          <kbd style={{ fontSize: '0.7rem', color: '#475569', background: 'rgba(255,255,255,0.06)', padding: '0.15rem 0.4rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>ESC</kbd>
        </div>

        {/* Command List */}
        <div style={{ maxHeight: '380px', overflowY: 'auto' }}>
          {filtered.length === 0 ? (
            <div style={{ padding: '2.5rem', textAlign: 'center', color: '#475569', fontSize: '0.85rem' }}>
              No results for "{query}"
            </div>
          ) : (
            filtered.map((cmd, i) => (
              <div
                key={cmd.id}
                onClick={cmd.action}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.85rem',
                  padding: '0.8rem 1.2rem', cursor: 'pointer',
                  background: i === selectedIdx ? 'rgba(56,189,248,0.1)' : 'transparent',
                  borderLeft: i === selectedIdx ? '2px solid #38bdf8' : '2px solid transparent',
                  transition: 'all 0.12s',
                }}
                onMouseEnter={() => setSelectedIdx(i)}
              >
                <div style={{ flexShrink: 0 }}>{cmd.icon}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.87rem', color: i === selectedIdx ? '#f8fafc' : '#e2e8f0' }}>{cmd.label}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.1rem' }}>{cmd.description}</div>
                </div>
                {cmd.shortcut && (
                  <kbd style={{ fontSize: '0.7rem', color: '#475569', background: 'rgba(255,255,255,0.06)', padding: '0.15rem 0.4rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)', flexShrink: 0 }}>
                    {cmd.shortcut}
                  </kbd>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: '0.65rem 1.2rem', borderTop: '1px solid rgba(255,255,255,0.07)', display: 'flex', gap: '1rem', fontSize: '0.72rem', color: '#475569' }}>
          <span><kbd style={{ padding: '0.1rem 0.3rem', borderRadius: '3px', border: '1px solid rgba(255,255,255,0.1)', marginRight: '0.35rem' }}>↑↓</kbd>Navigate</span>
          <span><kbd style={{ padding: '0.1rem 0.3rem', borderRadius: '3px', border: '1px solid rgba(255,255,255,0.1)', marginRight: '0.35rem' }}>↵</kbd>Open</span>
          <span><kbd style={{ padding: '0.1rem 0.3rem', borderRadius: '3px', border: '1px solid rgba(255,255,255,0.1)', marginRight: '0.35rem' }}>Esc</kbd>Close</span>
        </div>
      </div>
    </div>
  );
};
