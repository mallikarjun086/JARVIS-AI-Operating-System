import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Settings, Activity, ShieldCheck, Sparkles, Brain, Network, Wrench, Monitor, Globe, Code, Users, Eye, Mic, GitMerge, Lock, Bot, Cpu, X } from 'lucide-react';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = false, onClose }) => {
  const handleNavClick = () => {
    if (onClose) onClose();
  };

  return (
    <>
      <div className={`sidebar-backdrop ${isOpen ? 'active' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${isOpen ? 'mobile-open' : ''}`}>
        <div className="brand-header">
          <div className="brand-logo">
            <Bot size={24} color="#ffffff" />
          </div>
          <div style={{ flex: 1 }}>
            <div className="brand-title">JARVIS AI OS</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.15rem' }}>
              <span className="badge-info" style={{ padding: '0.1rem 0.4rem', fontSize: '0.65rem' }}>v1.0 PROD</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Swarm Kernel</span>
            </div>
          </div>
          {onClose && (
            <button onClick={onClose} className="mobile-toggle-btn" title="Close Drawer">
              <X size={18} />
            </button>
          )}
        </div>

        <nav className="nav-menu">
          <div className="nav-section-label">⚡ Core System</div>
          <NavLink to="/jarvis-command-center" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} style={{ background: 'linear-gradient(135deg, rgba(0, 242, 254, 0.18), rgba(139, 92, 246, 0.12))', border: '1px solid rgba(0, 242, 254, 0.3)' }}>
            <Bot size={17} color="#00f2fe" />
            <span style={{ color: '#00f2fe', fontWeight: 700 }}>JARVIS Command Center</span>
          </NavLink>
          <NavLink to="/dashboard" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={17} />
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/multi-agent-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Users size={17} />
            <span>10-Agent Swarm</span>
          </NavLink>
          <NavLink to="/planner-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Network size={17} />
            <span>Task Planner DAG</span>
          </NavLink>
          <NavLink to="/workflow-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <GitMerge size={17} />
            <span>Workflow Kernel</span>
          </NavLink>

          <div className="nav-section-label" style={{ marginTop: '0.5rem' }}>🤖 AI Intelligence</div>
          <NavLink to="/ai-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Sparkles size={17} />
            <span>7-Stage LLM Router</span>
          </NavLink>
          <NavLink to="/memory-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Brain size={17} />
            <span>Vector Memory Vault</span>
          </NavLink>
          <NavLink to="/dataset-trainer" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Cpu size={17} />
            <span>Dataset Trainer</span>
          </NavLink>
          <NavLink to="/swe-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Code size={17} />
            <span>SWE Software Agent</span>
          </NavLink>
          <NavLink to="/vision-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Eye size={17} />
            <span>Computer Vision OCR</span>
          </NavLink>
          <NavLink to="/voice-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Mic size={17} />
            <span>Voice Intelligence</span>
          </NavLink>

          <div className="nav-section-label" style={{ marginTop: '0.5rem' }}>🌐 Automation & Tools</div>
          <NavLink to="/browser-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Globe size={17} />
            <span>Playwright Web Engine</span>
          </NavLink>
          <NavLink to="/automation-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Monitor size={17} />
            <span>OS Desktop Automation</span>
          </NavLink>
          <NavLink to="/tool-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Wrench size={17} />
            <span>11-Tool Framework</span>
          </NavLink>

          <div className="nav-section-label" style={{ marginTop: '0.5rem' }}>🛡️ Security & Ops</div>
          <NavLink to="/security-console" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Lock size={17} />
            <span>Security & Vault</span>
          </NavLink>
          <NavLink to="/audit-logs" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Activity size={17} />
            <span>Audit Stream</span>
          </NavLink>
          <NavLink to="/settings" onClick={handleNavClick} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Settings size={17} />
            <span>System Settings</span>
          </NavLink>
        </nav>

        <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="beacon-dot"></span>
              <span style={{ fontWeight: 600, color: '#f8fafc' }}>Kernel Operational</span>
            </div>
            <ShieldCheck size={16} color="#10b981" />
          </div>
        </div>
      </aside>
    </>
  );
};
