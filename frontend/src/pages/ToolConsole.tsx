import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Wrench, Layers, Play, CheckCircle2, AlertTriangle, RefreshCw, Terminal, Search, Filter, ShieldCheck } from 'lucide-react';

interface ToolMetadata {
  name: string;
  description: string;
  version: string;
  permission_level: number;
  category: string;
  timeout_seconds: number;
  max_retries: number;
  input_schema_json?: any;
  output_schema_json?: any;
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
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedTool, setSelectedTool] = useState<ToolMetadata | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [paramInput, setParamInput] = useState<string>('{\n  "message": "Execute tool diagnostic call"\n}');
  const [execResult, setExecResult] = useState<ToolExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [isReloading, setIsReloading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const fetchTools = async () => {
    try {
      const [toolsResp, catResp] = await Promise.all([
        api.get<ToolMetadata[]>('/tools'),
        api.get<string[]>('/tools/categories')
      ]);
      setTools(toolsResp.data || []);
      setCategories(catResp.data || []);
      if (toolsResp.data && toolsResp.data.length > 0) {
        setSelectedTool(toolsResp.data[0]);
        updateParamPreset(toolsResp.data[0]);
      }
    } catch (err: any) {
      setErrorMsg('Failed to fetch registered tool metadata.');
    }
  };

  useEffect(() => {
    fetchTools();
  }, []);

  const updateParamPreset = (tool: ToolMetadata) => {
    let preset: any = { message: "Hello JARVIS Tool Framework" };
    if (tool.name.includes("browser") || tool.name.includes("web")) {
      preset = { url: "https://example.com", action: "navigate" };
    } else if (tool.name.includes("code") || tool.name.includes("ast") || tool.name.includes("swe")) {
      preset = { file_path: "backend/app/main.py", language: "python" };
    } else if (tool.name.includes("memory") || tool.name.includes("vector")) {
      preset = { query: "multi-agent swarm architecture", limit: 3 };
    } else if (tool.name.includes("vision") || tool.name.includes("ocr")) {
      preset = { image_source: "sample_snapshot.png", mode: "ocr_extraction" };
    } else if (tool.name.includes("voice") || tool.name.includes("tts")) {
      preset = { text: "JARVIS AI OS system operational.", voice: "en_us_male" };
    }

    setParamInput(JSON.stringify(preset, null, 2));
  };

  const handleSelectTool = (t: ToolMetadata) => {
    setSelectedTool(t);
    setExecResult(null);
    setErrorMsg('');
    updateParamPreset(t);
  };

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
      setErrorMsg(err.response?.data?.detail || 'Execution error or invalid JSON input parameter.');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleHotReload = async () => {
    setIsReloading(true);
    try {
      await api.post('/tools/hot-reload');
      await fetchTools();
    } catch {
      await fetchTools();
    } finally {
      setIsReloading(false);
    }
  };

  const filteredTools = tools.filter((t) => {
    const matchesCat = selectedCategory === 'ALL' || t.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchesQuery = !searchQuery || t.name.toLowerCase().includes(searchQuery.toLowerCase()) || t.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesQuery;
  });

  const getPermissionBadge = (level: number) => {
    switch (level) {
      case 0: return <span className="badge-success">PUBLIC (0)</span>;
      case 1: return <span className="badge-info">USER_READ (1)</span>;
      case 2: return <span className="badge-amber">USER_WRITE (2)</span>;
      case 3: return <span className="badge-purple">ADMIN (3)</span>;
      case 4: return <span className="badge-danger">CRITICAL_SYSTEM (4)</span>;
      default: return <span className="badge-info">LEVEL {level}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Wrench size={26} color="#06b6d4" /> 11-Category Enterprise Tool Framework
          </h1>
          <p className="page-subtitle">
            Pydantic Schema Validation, RBAC Guards, Timeouts, Exponential Retries, Audit Logging & Hot-Reload Engine.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button onClick={handleHotReload} disabled={isReloading} className="btn-secondary">
            <RefreshCw size={15} className={isReloading ? 'spin' : ''} /> {isReloading ? 'Scanning...' : 'Hot-Reload Modules'}
          </button>
        </div>
      </div>

      {errorMsg && <div className="alert-banner error"><AlertTriangle size={16} /> {errorMsg}</div>}

      {/* Category Tabs & Search Bar */}
      <div className="panel" style={{ padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', overflowX: 'auto', paddingBottom: '0.2rem' }}>
            <button
              onClick={() => setSelectedCategory('ALL')}
              className={`btn-secondary ${selectedCategory === 'ALL' ? 'active' : ''}`}
              style={{
                padding: '0.35rem 0.85rem',
                fontSize: '0.8rem',
                background: selectedCategory === 'ALL' ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255,255,255,0.04)',
                borderColor: selectedCategory === 'ALL' ? '#06b6d4' : 'var(--border-color)',
                color: selectedCategory === 'ALL' ? '#38bdf8' : 'var(--text-muted)'
              }}
            >
              ALL ({tools.length})
            </button>
            {categories.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCategory(c)}
                style={{
                  padding: '0.35rem 0.85rem',
                  fontSize: '0.8rem',
                  background: selectedCategory === c ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255,255,255,0.04)',
                  border: selectedCategory === c ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                  color: selectedCategory === c ? '#38bdf8' : 'var(--text-muted)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                {c.toUpperCase()}
              </button>
            ))}
          </div>

          <div style={{ position: 'relative', width: '240px' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
            <input
              type="text"
              placeholder="Search registered tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field"
              style={{ paddingLeft: '2rem', fontSize: '0.8rem' }}
            />
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem' }}>
        {/* Tool Directory List */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '650px' }}>
          <div className="panel-header" style={{ marginBottom: '0.5rem', paddingBottom: '0.5rem' }}>
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} color="#a855f7" /> Registered Tools ({filteredTools.length})
            </h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', overflowY: 'auto', paddingRight: '0.3rem' }}>
            {filteredTools.map((t) => (
              <div
                key={t.name}
                onClick={() => handleSelectTool(t)}
                style={{
                  padding: '0.85rem 1rem',
                  borderRadius: '10px',
                  background: selectedTool?.name === t.name ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.18), rgba(139, 92, 246, 0.12))' : 'rgba(4, 7, 17, 0.6)',
                  border: selectedTool?.name === t.name ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: selectedTool?.name === t.name ? '0 4px 18px rgba(6, 182, 212, 0.2)' : 'none'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <strong style={{ color: selectedTool?.name === t.name ? '#38bdf8' : '#fff', fontSize: '0.9rem' }}>{t.name}</strong>
                  {getPermissionBadge(t.permission_level)}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>{t.description}</div>
              </div>
            ))}

            {filteredTools.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '2rem' }}>
                No tools match the selected category or search filter.
              </div>
            )}
          </div>
        </div>

        {/* Selected Tool Schema & Test Launcher */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {selectedTool ? (
            <>
              <div className="panel">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#fff' }}>{selectedTool.name}</h2>
                  {getPermissionBadge(selectedTool.permission_level)}
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '1.2rem', lineHeight: '1.4' }}>
                  {selectedTool.description}
                </p>

                <div style={{ display: 'flex', gap: '2rem', fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1.25rem', background: 'rgba(4, 7, 17, 0.5)', padding: '0.65rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <span>Category: <strong style={{ color: '#38bdf8' }}>{selectedTool.category}</strong></span>
                  <span>Timeout: <strong style={{ color: '#fff' }}>{selectedTool.timeout_seconds}s</strong></span>
                  <span>Max Retries: <strong style={{ color: '#fff' }}>{selectedTool.max_retries}</strong></span>
                  <span>Version: <strong style={{ color: '#34d399' }}>v{selectedTool.version}</strong></span>
                </div>

                <form onSubmit={handleExecute} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-dim)' }}>
                    Input Parameters (JSON payload validated against Pydantic schema)
                  </label>
                  <textarea
                    rows={6}
                    value={paramInput}
                    onChange={(e) => setParamInput(e.target.value)}
                    className="input-field"
                    style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
                    required
                  />

                  <button type="submit" className="btn-primary" disabled={isExecuting} style={{ alignSelf: 'flex-start' }}>
                    <Play size={16} /> {isExecuting ? 'Executing Framework...' : 'Execute Tool Call'}
                  </button>
                </form>
              </div>

              {/* Execution Result Panel */}
              {execResult && (
                <div className="panel">
                  <div className="panel-header" style={{ marginBottom: '0.75rem' }}>
                    <h3 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Terminal size={18} color="#38bdf8" /> Execution Result Output
                    </h3>
                    <span className={execResult.status === 'SUCCESS' ? 'badge-success' : 'badge-danger'}>
                      {execResult.status}
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
                    <span>Execution Time: <strong style={{ color: '#fff' }}>{execResult.execution_time_seconds}s</strong></span>
                    <span>Retry Count: <strong style={{ color: '#fff' }}>{execResult.retry_count}</strong></span>
                  </div>

                  {execResult.output && (
                    <pre style={{ background: 'rgba(4, 7, 17, 0.9)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', color: '#38bdf8', fontSize: '0.85rem', overflowX: 'auto', fontFamily: 'monospace' }}>
                      {JSON.stringify(execResult.output, null, 2)}
                    </pre>
                  )}

                  {execResult.error_message && (
                    <div className="alert-banner error" style={{ marginTop: '0.5rem' }}>
                      {execResult.error_message}
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Select a registered tool from the directory on the left.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
