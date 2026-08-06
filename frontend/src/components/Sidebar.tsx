import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Settings, Activity, ShieldCheck, Sparkles, Brain, Network, Wrench, Monitor, Globe, Code, Users, Eye, Mic, GitMerge, Lock } from 'lucide-react';

export const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="brand-header">
        <div className="brand-logo">🤖</div>
        <div>
          <div className="brand-title">JARVIS AI OS</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Enterprise Kernel v1.0</div>
        </div>
      </div>

      <nav className="nav-menu">
        <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/ai-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Sparkles size={18} />
          <span>AI Core Console</span>
        </NavLink>
        <NavLink to="/security-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Lock size={18} />
          <span>Security & Vault</span>
        </NavLink>
        <NavLink to="/workflow-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <GitMerge size={18} />
          <span>Workflow Automation</span>
        </NavLink>
        <NavLink to="/voice-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Mic size={18} />
          <span>Voice Assistant</span>
        </NavLink>
        <NavLink to="/multi-agent-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Users size={18} />
          <span>Multi-Agent Swarm</span>
        </NavLink>
        <NavLink to="/vision-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Eye size={18} />
          <span>Computer Vision</span>
        </NavLink>
        <NavLink to="/planner-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Network size={18} />
          <span>Task Planner</span>
        </NavLink>
        <NavLink to="/swe-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Code size={18} />
          <span>SWE Agent</span>
        </NavLink>
        <NavLink to="/browser-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Globe size={18} />
          <span>Browser Automation</span>
        </NavLink>
        <NavLink to="/automation-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Monitor size={18} />
          <span>OS Automation</span>
        </NavLink>
        <NavLink to="/tool-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Wrench size={18} />
          <span>Tool Framework</span>
        </NavLink>
        <NavLink to="/memory-console" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Brain size={18} />
          <span>Memory Subsystem</span>
        </NavLink>
        <NavLink to="/audit-logs" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Activity size={18} />
          <span>Audit Logs</span>
        </NavLink>
        <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={18} />
          <span>Settings</span>
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldCheck size={14} color="#10b981" />
          <span>System Status: Online</span>
        </div>
      </div>
    </aside>
  );
};
