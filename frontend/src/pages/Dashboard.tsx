import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Activity, Cpu, Database, Server, ShieldCheck, Zap } from 'lucide-react';

interface HealthData {
  status: string;
  app_name: string;
  environment: string;
}

interface ReadinessData {
  status: string;
  database: string;
}

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [readiness, setReadiness] = useState<ReadinessData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHealthMetrics = async () => {
      try {
        const [hRes, rRes] = await Promise.all([
          api.get<HealthData>('/health'),
          api.get<ReadinessData>('/health/readiness'),
        ]);
        setHealth(hRes.data);
        setReadiness(rRes.data);
      } catch (err) {
        console.error('Failed fetching health metrics', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHealthMetrics();
    const interval = setInterval(fetchHealthMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff' }}>System Telemetry Dashboard</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Real-time status monitor for JARVIS AI Operating System Foundation Services.
        </p>
      </div>

      <div className="card-grid">
        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">System Status</span>
            <ShieldCheck size={20} color="#10b981" />
          </div>
          <div className="metric-value" style={{ color: '#10b981' }}>
            {health?.status || (isLoading ? 'Checking...' : 'OFFLINE')}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Environment: {health?.environment || 'development'}</span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Database Engine</span>
            <Database size={20} color="#06b6d4" />
          </div>
          <div className="metric-value" style={{ color: '#06b6d4' }}>
            {readiness?.database || (isLoading ? 'Checking...' : 'DISCONNECTED')}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PostgreSQL 16 Async Connection Pool</span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Backend API</span>
            <Server size={20} color="#3b82f6" />
          </div>
          <div className="metric-value">FastAPI v1</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Dependency Injection Enabled</span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Desktop Shell</span>
            <Cpu size={20} color="#8b5cf6" />
          </div>
          <div className="metric-value">Electron 29</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>IPC Context Bridge Sandboxed</span>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem', marginTop: '1rem' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={18} color="#06b6d4" />
          <span>Foundation Services Architecture Verification</span>
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '0.25rem' }}>🔐 Security & Authentication</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>OAuth2 Password Bearer flow with Bcrypt password hashing & JWT token validation.</div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontWeight: 600, color: '#a78bfa', marginBottom: '0.25rem' }}>📜 Structured Telemetry</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Structlog JSON logging infrastructure with request correlation IDs.</div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontWeight: 600, color: '#34d399', marginBottom: '0.25rem' }}>⚡ Async DB Persistence</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>SQLAlchemy 2.0 Async engine with PostgreSQL pool & SQLite fallback.</div>
          </div>
        </div>
      </div>
    </div>
  );
};
