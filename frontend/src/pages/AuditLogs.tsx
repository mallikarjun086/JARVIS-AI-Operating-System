import React from 'react';
import { Activity, ShieldCheck, Terminal, Server } from 'lucide-react';

export const AuditLogsPage: React.FC = () => {
  const sampleLogs = [
    { id: 1, timestamp: '2026-08-03T17:10:05Z', level: 'INFO', event: 'SYSTEM_BOOTUP', details: 'JARVIS AI OS Kernel initialized successfully.' },
    { id: 2, timestamp: '2026-08-03T17:10:12Z', level: 'INFO', event: 'AUTH_SUCCESS', details: 'User admin@jarvis.ai authenticated via OAuth2 JWT.' },
    { id: 3, timestamp: '2026-08-03T17:11:00Z', level: 'INFO', event: 'DB_READINESS', details: 'PostgreSQL 16 connection pool verified healthy.' },
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff' }}>Structured System Audit Logs</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Structlog JSON telemetry stream events and security audit trail.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '0.75rem' }}>Timestamp</th>
              <th style={{ padding: '0.75rem' }}>Level</th>
              <th style={{ padding: '0.75rem' }}>Event</th>
              <th style={{ padding: '0.75rem' }}>Details</th>
            </tr>
          </thead>
          <tbody>
            {sampleLogs.map((log) => (
              <tr key={log.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>{log.timestamp}</td>
                <td style={{ padding: '0.75rem' }}>
                  <span className="badge-success">{log.level}</span>
                </td>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: '#38bdf8' }}>{log.event}</td>
                <td style={{ padding: '0.75rem', color: '#f8fafc' }}>{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
