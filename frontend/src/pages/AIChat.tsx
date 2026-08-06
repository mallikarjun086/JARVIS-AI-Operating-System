import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Cpu, DollarSign, MessageSquare, Send, Sparkles } from 'lucide-react';

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
}

export const AIChatPage: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('mock-gpt');
  const [templateName, setTemplateName] = useState<string>('');
  const [inputPrompt, setInputPrompt] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'assistant', text: 'Hello! I am JARVIS AI Core Engine. Select a model provider and enter a prompt to begin.' }
  ]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [metrics, setMetrics] = useState<CostMetrics | null>(null);

  const fetchModelsAndMetrics = async () => {
    try {
      const [mRes, cRes] = await Promise.all([
        api.get<ModelInfo[]>('/ai/models'),
        api.get<CostMetrics>('/ai/metrics'),
      ]);
      setModels(mRes.data);
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
    setInputPrompt('');
    setMessages((prev: Message[]) => [...prev, { sender: 'user', text: userText }]);
    setIsGenerating(true);

    try {
      const resp = await api.post('/ai/chat/completions', {
        model: selectedModel,
        messages: [{ role: 'user', content: userText }],
        temperature: 0.2,
      }, {
        params: templateName ? { template_name: templateName } : {}
      });

      setMessages((prev: Message[]) => [...prev, { sender: 'assistant', text: resp.data.content }]);
      await fetchModelsAndMetrics();
    } catch (err: any) {
      setMessages((prev: Message[]) => [
        ...prev,
        { sender: 'assistant', text: `⚠️ Error: ${err.response?.data?.detail || 'Generation failed.'}` }
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles color="#06b6d4" />
            <span>AI Core Model Abstraction Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Multi-Provider Router (OpenAI, Claude, Gemini) with cost telemetry and token management.
          </p>
        </div>
      </div>

      {/* Model & Cost Telemetry Banner */}
      <div className="card-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Active Model</span>
            <Cpu size={18} color="#06b6d4" />
          </div>
          <div className="metric-value" style={{ fontSize: '1.25rem', color: '#38bdf8' }}>
            {selectedModel}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Provider: {models.find((m: ModelInfo) => m.model_id === selectedModel)?.provider || 'Mock'}
          </span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Cumulative Tokens</span>
            <MessageSquare size={18} color="#a78bfa" />
          </div>
          <div className="metric-value">{metrics?.total_tokens || 0}</div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>In: {metrics?.total_input_tokens || 0} | Out: {metrics?.total_output_tokens || 0}</span>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="metric-title">Cost Telemetry ($USD)</span>
            <DollarSign size={18} color="#10b981" />
          </div>
          <div className="metric-value" style={{ color: '#10b981' }}>
            ${metrics?.total_cost_usd?.toFixed(4) || '0.0000'}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Requests: {metrics?.total_requests || 0}</span>
        </div>
      </div>

      {/* Main Console Interface */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '520px' }}>
        {/* Top Control Settings */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Select Provider Model</label>
            <select
              value={selectedModel}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedModel(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
            >
              {models.map((m: ModelInfo) => (
                <option key={m.model_id} value={m.model_id}>
                  {m.name} ({m.provider})
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Prompt Template</label>
            <select
              value={templateName}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setTemplateName(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
            >
              <option value="">None (Standard User Input)</option>
              <option value="system_assistant">System Assistant Persona</option>
              <option value="code_generator">Software Architect Code Gen</option>
              <option value="summarizer">Technical Text Summarizer</option>
            </select>
          </div>
        </div>

        {/* Chat History Box */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', paddingRight: '0.5rem' }}>
          {messages.map((msg: Message, idx: number) => (
            <div
              key={idx}
              style={{
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
                padding: '0.85rem 1.1rem',
                borderRadius: '12px',
                background: msg.sender === 'user' ? 'linear-gradient(135deg, #0284c7, #2563eb)' : 'rgba(30, 41, 59, 0.8)',
                color: '#fff',
                border: msg.sender === 'assistant' ? '1px solid var(--border-color)' : 'none',
                fontSize: '0.925rem',
                lineHeight: '1.5'
              }}
            >
              <div style={{ fontSize: '0.75rem', opacity: 0.7, marginBottom: '0.25rem', fontWeight: 600 }}>
                {msg.sender === 'user' ? 'User Operator' : `JARVIS Core (${selectedModel})`}
              </div>
              {msg.text}
            </div>
          ))}
        </div>

        {/* Prompt Input Form */}
        <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <input
            type="text"
            value={inputPrompt}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputPrompt(e.target.value)}
            placeholder="Type your prompt for OpenAI, Claude, or Gemini..."
            disabled={isGenerating}
            style={{ flex: 1, padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
          />
          <button type="submit" className="btn-primary" disabled={isGenerating} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Send size={16} />
            <span>{isGenerating ? 'Routing...' : 'Execute'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
