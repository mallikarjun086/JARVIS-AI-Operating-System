import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Wrench, ShieldAlert, Cpu, Play, CheckCircle2, AlertTriangle, Layers, Lock } from 'lucide-react';

interface ToolMetadata {
  name: string;
  description: string;
  version: string;
  permission_level: number;
  category: string;
  timeout_seconds: number;
  max_retries: number;
  input_schema_json: any;
  output_schema_json: any;
}

interface ToolExecutionResult {
  tool_name: string;
  status: string;
  output?: any;
  error_message?: string;
  execution_time_seconds: number;
  retry_count: number;
}

export const ToolConsolePage: React.FC = () => {
  const [tools, setTools] = useState<ToolMetadata[]>([]);
  const [selectedTool, setSelectedTool] = useState<ToolMetadata | null>(null);
  const [paramInput, setParamInput] = useState<string>('{"message": "Hello Tool Framework"}');
  const [execResult, setExecResult] = useState<ToolExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const fetchTools = async () => {
    try {
      const resp = await api.get<ToolMetadata[]>('/tools');
      setTools(resp.data);
      if (resp.data.length > 0) {
        setSelectedTool(resp.data[0]);
      }
    } catch (err: any) {
      setErrorMsg('Failed to load tool registry metadata.');
    }
  };

  useEffect(() => {
    fetchTools();
  }, []);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTool) return;

    setIsExecuting(true);
    setErrorMsg('');
    setExecResult(null);

    try {
      let parsedParams = {};
      if (paramInput.trim()) {
        parsedParams = JSON.parse(paramInput);
      }

      const resp = await api.post<ToolExecutionResult>('/tools/execute', {
        tool_name: selectedTool.name,
        parameters: parsedParams,
      });

      setExecResult(resp.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Execution error or invalid JSON input.');
    } finally {
      setIsExecuting(false);
    }
  };

  const getPermissionBadge = (level: number) => {
    switch (level) {
      case 0: return <span className="badge-success">PUBLIC (0)</span>;
      case 1: return <span className="badge-success">USER_READ (1)</span>;
      case 2: return <span className="badge-warning">USER_WRITE (2)</span>;
      case 3: return <span className="badge-danger">ADMIN (3)</span>;
      case 4: return <span className="badge-danger">CRITICAL_SYSTEM (4)</span>;
      default: return <span className="badge-warning">LEVEL {level}</span>;
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Wrench color="#06b6d4" />
            <span>Tool System Framework Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Dynamic Discovery, Permission Guards, Pydantic Schema Validation, Timeouts, Exponential Retries & Parallel Execution.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          ⚠️ {errorMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        {/* Registered Tool Directory */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers color="#a78bfa" size={18} />
            <span>Registered System Tools</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', overflowY: 'auto', maxHeight: '500px' }}>
            {tools.map((t: ToolMetadata) => (
              <div
                key={t.name}
                onClick={() => setSelectedTool(t)}
                style={{
                  padding: '0.85rem 1rem',
                  borderRadius: '8px',
                  background: selectedTool?.name === t.name ? 'rgba(6, 182, 212, 0.2)' : 'rgba(15, 23, 42, 0.6)',
                  border: selectedTool?.name === t.name ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <strong style={{ color: '#fff', fontSize: '0.9rem' }}>{t.name}</strong>
                  {getPermissionBadge(t.permission_level)}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.description}</div>
              </div>
            ))}
            {tools.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '1rem' }}>
                Framework ready. No tools registered yet.
              </div>
            )}
          </div>
        </div>

        {/* Selected Tool Schema & Test Execution Runner */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {selectedTool ? (
            <>
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>{selectedTool.name}</h2>
                  {getPermissionBadge(selectedTool.permission_level)}
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>{selectedTool.description}</p>

                <div style={{ display: 'flex', gap: '2rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                  <span>Timeout: <strong style={{ color: '#fff' }}>{selectedTool.timeout_seconds}s</strong></span>
                  <span>Max Retries: <strong style={{ color: '#fff' }}>{selectedTool.max_retries}</strong></span>
                  <span>Category: <strong style={{ color: '#fff' }}>{selectedTool.category}</strong></span>
                </div>

                {/* Execution Test Form */}
                <form onSubmit={handleExecute} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Input Parameters JSON (Validated against Pydantic Input Schema)</label>
                  <textarea
                    rows={3}
                    value={paramInput}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setParamInput(e.target.value)}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff', fontFamily: 'monospace', fontSize: '0.85rem' }}
                  />

                  <button type="submit" className="btn-primary" disabled={isExecuting} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', alignSelf: 'flex-start', padding: '0.6rem 1.25rem' }}>
                    <Play size={16} />
                    <span>{isExecuting ? 'Executing Framework...' : 'Execute Tool'}</span>
                  </button>
                </form>
              </div>

              {/* Execution Result Box */}
              {execResult && (
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>Execution Result</span>
                    <span className={execResult.status === 'SUCCESS' ? 'badge-success' : 'badge-danger'}>{execResult.status}</span>
                  </div>

                  <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                    <span>Execution Time: {execResult.execution_time_seconds}s</span>
                    <span>Retry Count: {execResult.retry_count}</span>
                  </div>

                  {execResult.output && (
                    <pre style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', color: '#38bdf8', fontSize: '0.85rem', overflowX: 'auto' }}>
                      {JSON.stringify(execResult.output, null, 2)}
                    </pre>
                  )}

                  {execResult.error_message && (
                    <div style={{ color: '#fca5a5', background: 'rgba(239, 68, 68, 0.15)', padding: '0.75rem 1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                      {execResult.error_message}
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a registered tool from the left directory.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
