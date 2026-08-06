import React, { useState } from 'react';
import { Save, Sliders, Shield, Database, Bell } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [logLevel, setLogLevel] = useState('INFO');
  const [dbTimeout, setDbTimeout] = useState('30');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff' }}>System Configuration Settings</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Configure kernel variables, database timeouts, and log verbosity.
        </p>
      </div>

      {saved && (
        <div style={{ background: 'rgba(16, 185, 129, 0.2)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#6ee7b7', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          ✓ Configuration changes saved successfully.
        </div>
      )}

      <form onSubmit={handleSave} className="glass-panel" style={{ padding: '2rem', maxWidth: '650px' }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>
            <Sliders size={16} color="#06b6d4" />
            <span>Structured Logging Verbosity</span>
          </label>
          <select
            value={logLevel}
            onChange={(e) => setLogLevel(e.target.value)}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', color: '#fff' }}
          >
            <option value="DEBUG">DEBUG (Verbose Tracing)</option>
            <option value="INFO">INFO (Standard Production)</option>
            <option value="WARNING">WARNING (Errors & Warnings)</option>
            <option value="ERROR">ERROR (Errors Only)</option>
          </select>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>
            <Database size={16} color="#3b82f6" />
            <span>Database Query Timeout (Seconds)</span>
          </label>
          <input
            type="number"
            value={dbTimeout}
            onChange={(e) => setDbTimeout(e.target.value)}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', color: '#fff' }}
          />
        </div>

        <button type="submit" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Save size={16} />
          <span>Save Settings</span>
        </button>
      </form>
    </div>
  );
};
