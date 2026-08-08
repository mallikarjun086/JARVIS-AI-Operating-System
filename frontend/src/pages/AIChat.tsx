import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Cpu, DollarSign, MessageSquare, Send, Sparkles, Copy, Check, Zap } from 'lucide-react';

interface ModelInfo {
  model_id: string;
  provider: string;
  name: string;
  input_cost_per_1k: number;
  output_cost_per_1k: number;
}

interface CostMetrics {
  total_requests: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
}

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const AIChatPage: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('mock-gpt');
  const [templateName, setTemplateName] = useState<string>('');
  const [inputPrompt, setInputPrompt] = useState<string>('');
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'assistant', text: 'Hello! I am the JARVIS AI Core Engine. Select a provider model or prompt template to begin.', timestamp: new Date().toLocaleTimeString() }
  ]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [metrics, setMetrics] = useState<CostMetrics | null>(null);

  const fetchModelsAndMetrics = async () => {
    try {
      const [mRes, cRes] = await Promise.all([
        api.get<ModelInfo[]>('/ai/models'),
        api.get<CostMetrics>('/ai/metrics'),
      ]);
      setModels(mRes.data || []);
      setMetrics(cRes.data);
    } catch (err) {
      console.error('Error fetching AI metrics', err);
    }
  };

  useEffect(() => {
    fetchModelsAndMetrics();
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isGenerating) return;

    const userText = inputPrompt;
    const timeStr = new Date().toLocaleTimeString();
    setInputPrompt('');
    setMessages((prev) => [...prev, { sender: 'user', text: userText, timestamp: timeStr }]);
    setIsGenerating(true);

    try {
      const resp = await api.post('/ai/chat/completions', {
        model: selectedModel,
        messages: [{ role: 'user', content: userText }],
        temperature: 0.2,
      }, {
        params: templateName ? { template_name: templateName } : {}
      });

      setMessages((prev) => [...prev, { sender: 'assistant', text: resp.data.content, timestamp: new Date().toLocaleTimeString() }]);
      await fetchModelsAndMetrics();
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: `⚠️ Generation Notice: ${err.response?.data?.detail || 'Offline router fallback engaged.'}`, timestamp: new Date().toLocaleTimeString() }
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Sparkles size={26} color="#00f2fe" /> 7-Stage LLM Provider Router Console
          </h1>
          <p className="page-subtitle">
            Health Filter → Capability Filter → Cost Filter → Priority Rules → Dispatch → Retry → Fallback Pipeline.
          </p>
        </div>
      </div>

      {/* Model & Cost Telemetry Banner */}
      <div className="card-grid">
        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Active Model Provider</span>
            <Cpu size={20} color="#06b6d4" />
          </div>
          <div className="metric-value" style={{ fontSize: '1.35rem', color: '#38bdf8' }}>
            {selectedModel}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Provider: {models.find((m) => m.model_id === selectedModel)?.provider || 'MockProvider'}
          </span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Cumulative Tokens</span>
            <MessageSquare size={20} color="#a855f7" />
          </div>
          <div className="metric-value">{metrics?.total_tokens || 0}</div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>In: {metrics?.total_input_tokens || 0} | Out: {metrics?.total_output_tokens || 0}</span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Cost Telemetry ($USD)</span>
            <DollarSign size={20} color="#10b981" />
          </div>
          <div className="metric-value" style={{ color: '#34d399' }}>
            ${metrics?.total_cost_usd?.toFixed(4) || '0.0000'}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Dispatched Requests: {metrics?.total_requests || 0}</span>
        </div>
      </div>

      {/* Main Console Interface */}
      <div className="panel" style={{ display: 'flex', flexDirection: 'column', height: '560px' }}>
        {/* Top Model Selector & Prompt Template Pills */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '220px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem', fontWeight: 600 }}>
              Target Model
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="input-field"
            >
              {models.map((m) => (
                <option key={m.model_id} value={m.model_id}>
                  {m.name} ({m.provider})
                </option>
              ))}
              {models.length === 0 && <option value="mock-gpt">Mock GPT (Offline Provider)</option>}
            </select>
          </div>

          <div style={{ flex: 1, minWidth: '220px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem', fontWeight: 600 }}>
              System Persona / Template
            </label>
            <select
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              className="input-field"
            >
              <option value="">None (Standard User Input)</option>
              <option value="system_assistant">System Assistant Persona</option>
              <option value="code_generator">Software Architect Code Gen</option>
              <option value="summarizer">Technical Text Summarizer</option>
            </select>
          </div>
        </div>

        {/* Chat History Container */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', paddingRight: '0.5rem' }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '82%',
                padding: '0.9rem 1.15rem',
                borderRadius: '12px',
                background: msg.sender === 'user' ? 'linear-gradient(135deg, #0284c7, #2563eb)' : 'rgba(4, 7, 17, 0.8)',
                color: '#fff',
                border: msg.sender === 'assistant' ? '1px solid var(--border-color)' : '1px solid rgba(56, 189, 248, 0.4)',
                fontSize: '0.9rem',
                lineHeight: '1.5',
                position: 'relative'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <span style={{ fontSize: '0.72rem', opacity: 0.8, fontWeight: 700, color: msg.sender === 'user' ? '#e0f2fe' : '#38bdf8' }}>
                  {msg.sender === 'user' ? 'User Operator' : `JARVIS Core (${selectedModel})`}
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>{msg.timestamp}</span>
                  {msg.sender === 'assistant' && (
                    <button
                      onClick={() => handleCopy(msg.text, idx)}
                      style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                      title="Copy response"
                    >
                      {copiedIdx === idx ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
                    </button>
                  )}
                </div>
              </div>

              {msg.text.includes('```') ? (
                <pre style={{ background: 'rgba(4, 7, 17, 0.9)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)', color: '#38bdf8', fontSize: '0.85rem', fontFamily: 'monospace', overflowX: 'auto', marginTop: '0.4rem' }}>
                  {msg.text.replace(/```python|```typescript|```/g, '')}
                </pre>
              ) : (
                <div>{msg.text}</div>
              )}
            </div>
          ))}
        </div>

        {/* Prompt Input Bar */}
        <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            placeholder="Type prompt for OpenAI, Claude, Gemini, or Mock Router..."
            disabled={isGenerating}
            className="input-field"
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn-primary" disabled={isGenerating}>
            <Send size={16} />
            <span>{isGenerating ? 'Routing...' : 'Execute'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
