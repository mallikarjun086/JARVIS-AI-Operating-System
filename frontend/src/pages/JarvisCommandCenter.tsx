import React, { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../services/api';
import {
  Bot,
  Mic,
  Volume2,
  VolumeX,
  Send,
  Terminal,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Copy,
  Check,
  Loader2,
  Zap,
  Brain,
  Code2,
  RotateCcw,
} from 'lucide-react';

/* ─────────── TypeScript Interfaces ─────────── */
interface ExecutionStep {
  step_id: number;
  agent_role: string;
  title: string;
  status: string;
  message: string;
  latency_ms?: number;
}

interface ApprovalPayload {
  approval_id: string;
  command: string;
  risk_level: string;
  action_summary: string;
  target_tool?: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'jarvis';
  text: string;
  timestamp: string;
  voiceInput?: boolean;
  steps?: ExecutionStep[];
  generatedCode?: string;
  riskLevel?: string;
  approvalRequired?: ApprovalPayload;
  memoriesRetrieved?: number;
  totalMs?: number;
}

const WELCOME_MSG: ChatMessage = {
  id: 'init_welcome',
  sender: 'jarvis',
  text: 'Hello, Operator! I am JARVIS — your Unified AI OS Command Center. Speak or type any goal and I will automatically orchestrate the 10‑Agent Swarm, 35 Tools, ChromaDB Vector Memory, and Code Synthesis Engine to execute it end‑to‑end.',
  timestamp: new Date().toLocaleTimeString(),
};

const QUICK_COMMANDS = [
  'Build microservice REST API for user order processing',
  'Research latest AI agent frameworks and summarize',
  'Analyze this codebase and refactor for performance',
  'Create a Python FastAPI endpoint with JWT auth',
];

/* ─────────── Step Status Icon ─────────── */
const StepStatusIcon: React.FC<{ status: string }> = ({ status }) => {
  if (status === 'COMPLETED') return <CheckCircle2 size={15} color="#34d399" />;
  if (status === 'RUNNING') return <Loader2 size={15} color="#38bdf8" className="spin" />;
  if (status === 'FAILED') return <AlertTriangle size={15} color="#fb7185" />;
  return <Zap size={15} color="#64748b" />;
};

/* ─────────── Agent Role Badge Color ─────────── */
const agentColor: Record<string, string> = {
  MEMORY: '#c084fc',
  PLANNER: '#38bdf8',
  CODING: '#34d399',
  RESEARCH: '#fbbf24',
  VERIFIER: '#10b981',
  BROWSER: '#fb923c',
  DESKTOP: '#a78bfa',
};

/* ═══════════════════════════════════════════════════════ */
/*   JARVIS COMMAND CENTER — Main Component               */
/* ═══════════════════════════════════════════════════════ */
export const JarvisCommandCenterPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MSG]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeSteps, setActiveSteps] = useState<ExecutionStep[]>([]);
  const [pendingApproval, setPendingApproval] = useState<ApprovalPayload | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [sessionId] = useState(() => `sess_${Math.random().toString(36).slice(2, 10)}`);

  const chatBottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  // Stable ref so STT callback always calls the latest dispatch
  const dispatchRef = useRef<(cmd?: string, isVoice?: boolean) => void>(() => {});

  /* ── Speech Recognition Init ── */
  useEffect(() => {
    const SpeechRecognitionAPI =
      (window as unknown as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition })
        .SpeechRecognition ||
      (window as unknown as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition })
        .webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) return;
    const rec = new SpeechRecognitionAPI();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = 'en-US';

    rec.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setIsListening(false);
      setInputText('');
      dispatchRef.current(transcript, true);
    };
    rec.onerror = () => setIsListening(false);
    rec.onend = () => setIsListening(false);

    recognitionRef.current = rec;
  }, []);

  /* ── Auto‑scroll chat ── */
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /* ── TTS Voice Output ── */
  const speak = useCallback((text: string) => {
    if (!ttsEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleaned = text.replace(/```[\s\S]*?```/g, 'Code output generated.').slice(0, 280);
    const utt = new SpeechSynthesisUtterance(cleaned);
    utt.rate = 1.05;
    utt.pitch = 1.0;
    window.speechSynthesis.speak(utt);
  }, [ttsEnabled]);

  /* ── Toggle Mic ── */
  const toggleMic = () => {
    if (!recognitionRef.current) {
      setErrorMsg('Web Speech API is not supported in this browser. Please type your command instead.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setErrorMsg('');
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  /* ── Core Command Dispatch ── */
  const dispatch = useCallback(async (commandOverride?: string, isVoice = false) => {
    const cmd = commandOverride ?? inputText;
    if (!cmd.trim() || isExecuting) return;

    setInputText('');
    setErrorMsg('');
    setIsExecuting(true);
    setActiveSteps([]);

    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: cmd,
      timestamp: new Date().toLocaleTimeString(),
      voiceInput: isVoice,
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const resp = await api.post('/jarvis/execute', {
        command: cmd,
        session_id: sessionId,
        voice_input: isVoice,
        auto_execute: true,
      });
      const data = resp.data;

      setActiveSteps(data.steps ?? []);

      if (data.status === 'REQUIRES_APPROVAL' && data.approval_required) {
        setPendingApproval(data.approval_required);
      }

      const jarvisMsg: ChatMessage = {
        id: `jrv_${Date.now()}`,
        sender: 'jarvis',
        text: data.response_text,
        timestamp: new Date().toLocaleTimeString(),
        steps: data.steps,
        generatedCode: data.generated_code ?? null,
        riskLevel: data.risk_level,
        approvalRequired: data.approval_required ?? null,
        memoriesRetrieved: data.memories_retrieved ?? 0,
        totalMs: data.total_execution_ms ?? 0,
      };
      setMessages(prev => [...prev, jarvisMsg]);
      speak(data.response_text);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const errText = axiosErr.response?.data?.detail ?? 'Backend orchestration service not responding.';
      setErrorMsg(`Orchestration Error: ${errText}`);

      setMessages(prev => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'jarvis',
          text: `⚠️ ${errText}. Please ensure the backend server is running on port 8000.`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsExecuting(false);
      inputRef.current?.focus();
    }
  }, [inputText, isExecuting, sessionId, speak]);

  // Keep dispatchRef synced with the latest dispatch function
  useEffect(() => { dispatchRef.current = dispatch; }, [dispatch]);

  /* ── Approval Decision ── */
  const handleApproval = async (approved: boolean) => {
    if (!pendingApproval) return;
    try {
      const resp = await api.post('/jarvis/approve', {
        approval_id: pendingApproval.approval_id,
        approved,
        reason: approved ? 'Operator authorized via UI' : 'Operator rejected via UI',
      });
      setPendingApproval(null);
      const msg = resp.data.message ?? (approved ? '✓ Action authorized and executing.' : '❌ Action rejected.');
      setMessages(prev => [
        ...prev,
        { id: `appr_${Date.now()}`, sender: 'jarvis', text: msg, timestamp: new Date().toLocaleTimeString() },
      ]);
      speak(msg);
    } catch {
      setErrorMsg('Failed to process approval decision. Please try again.');
    }
  };

  /* ── Copy Code ── */
  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    });
  };

  /* ── Clear Chat ── */
  const clearChat = () => {
    setMessages([WELCOME_MSG]);
    setActiveSteps([]);
    setErrorMsg('');
    speak('Chat history cleared. Ready for your next command, Operator.');
  };

  /* ═══════════════════ RENDER ═══════════════════ */
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* ── Page Header ── */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', marginBottom: '0.4rem' }}>
            <span className="badge-purple">JARVIS COMMAND CENTER v1.0</span>
            <span className="beacon-dot" />
            <span style={{ fontSize: '0.78rem', color: '#34d399', fontWeight: 700 }}>ORCHESTRATOR ONLINE</span>
          </div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
            <Bot size={24} color="#00f2fe" />
            Unified Multimodal Voice &amp; Chat HUD
          </h1>
          <p className="page-subtitle">
            Speak or type any goal — JARVIS automatically orchestrates 10‑Agent Swarm, 35 Tools, ChromaDB Memory &amp; Code Synthesis.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', flexShrink: 0 }}>
          <button
            className="btn-secondary"
            onClick={() => setTtsEnabled(v => !v)}
            title={ttsEnabled ? 'Mute TTS Voice Output' : 'Enable TTS Voice Output'}
          >
            {ttsEnabled ? <Volume2 size={15} color="#34d399" /> : <VolumeX size={15} />}
            {ttsEnabled ? 'Voice On' : 'Voice Off'}
          </button>
          <button className="btn-secondary" onClick={clearChat} title="Clear Chat History">
            <RotateCcw size={15} />
            Clear
          </button>
        </div>
      </div>

      {/* ── Error Alert ── */}
      {errorMsg && (
        <div className="alert-banner error">
          <AlertTriangle size={15} />
          {errorMsg}
        </div>
      )}

      {/* ── Main Grid: Chat | Execution Log ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', minHeight: 0 }}>

        {/* LEFT: Conversational Interface */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', height: '600px' }}>
          <div className="panel-header">
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Sparkles size={17} color="#00f2fe" />
              Conversational Interface
            </h2>
            <span className="badge-info">STT + TTS ENABLED</span>
          </div>

          {/* Messages scroll area */}
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.9rem', paddingRight: '0.25rem' }}>
            {messages.map(m => (
              <div
                key={m.id}
                style={{
                  alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '88%',
                }}
              >
                {/* Bubble */}
                <div
                  style={{
                    padding: '0.8rem 1rem',
                    borderRadius: m.sender === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                    background:
                      m.sender === 'user'
                        ? 'linear-gradient(135deg, #0369a1, #1e40af)'
                        : 'rgba(10, 14, 26, 0.9)',
                    border:
                      m.sender === 'user'
                        ? '1px solid rgba(56,189,248,0.35)'
                        : '1px solid rgba(255,255,255,0.08)',
                    fontSize: '0.86rem',
                    lineHeight: '1.5',
                    color: '#f8fafc',
                    boxShadow: m.sender === 'user' ? '0 4px 16px rgba(3,105,161,0.4)' : 'none',
                  }}
                >
                  {/* Sender + time */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: m.sender === 'user' ? '#7dd3fc' : '#38bdf8' }}>
                      {m.sender === 'user' ? (m.voiceInput ? '🎤 Voice Operator' : 'Operator') : '🤖 JARVIS AI'}
                    </span>
                    <span style={{ fontSize: '0.67rem', color: '#475569' }}>{m.timestamp}</span>
                  </div>

                  <div>{m.text}</div>

                  {/* Stats row */}
                  {m.sender === 'jarvis' && (m.memoriesRetrieved !== undefined || m.totalMs) && (
                    <div style={{ display: 'flex', gap: '0.9rem', marginTop: '0.5rem', paddingTop: '0.45rem', borderTop: '1px solid rgba(255,255,255,0.07)' }}>
                      {m.memoriesRetrieved !== undefined && m.memoriesRetrieved > 0 && (
                        <span style={{ fontSize: '0.7rem', color: '#c084fc' }}>
                          <Brain size={11} style={{ display: 'inline', marginRight: 3 }} />{m.memoriesRetrieved} memories recalled
                        </span>
                      )}
                      {m.totalMs !== undefined && m.totalMs > 0 && (
                        <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>⚡ {m.totalMs}ms</span>
                      )}
                      {m.riskLevel && (
                        <span style={{ fontSize: '0.7rem', color: m.riskLevel === 'LOW' ? '#34d399' : m.riskLevel === 'HIGH' ? '#fb7185' : '#fbbf24' }}>
                          Risk: {m.riskLevel}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Generated Code Block */}
                  {m.generatedCode && (
                    <div style={{ marginTop: '0.65rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                        <span style={{ fontSize: '0.72rem', color: '#38bdf8', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Code2 size={12} /> Synthesized Code Artifact
                        </span>
                        <button
                          onClick={() => copyCode(m.generatedCode!, m.id)}
                          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#64748b', display: 'flex', alignItems: 'center', gap: 3, fontSize: '0.7rem' }}
                          title="Copy code"
                        >
                          {copiedId === m.id ? <><Check size={13} color="#34d399" /> Copied!</> : <><Copy size={13} /> Copy</>}
                        </button>
                      </div>
                      <pre
                        style={{
                          background: 'rgba(4,7,17,0.95)',
                          padding: '0.7rem 0.85rem',
                          borderRadius: '8px',
                          border: '1px solid rgba(56,189,248,0.2)',
                          color: '#67e8f9',
                          fontSize: '0.75rem',
                          fontFamily: 'JetBrains Mono, monospace',
                          overflowX: 'auto',
                          maxHeight: '200px',
                          whiteSpace: 'pre',
                        }}
                      >
                        {m.generatedCode}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={chatBottomRef} />
          </div>

          {/* Quick Command Chips */}
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.75rem', paddingTop: '0.65rem', borderTop: '1px solid var(--border-color)' }}>
            {QUICK_COMMANDS.map((qc, i) => (
              <button
                key={i}
                onClick={() => dispatch(qc)}
                disabled={isExecuting}
                style={{
                  background: 'rgba(6,182,212,0.08)',
                  border: '1px solid rgba(56,189,248,0.2)',
                  borderRadius: '20px',
                  color: '#94a3b8',
                  fontSize: '0.72rem',
                  padding: '0.3rem 0.7rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  fontFamily: 'var(--font-family)',
                }}
                onMouseEnter={e => (e.currentTarget.style.color = '#38bdf8')}
                onMouseLeave={e => (e.currentTarget.style.color = '#94a3b8')}
              >
                {qc.length > 32 ? qc.slice(0, 32) + '…' : qc}
              </button>
            ))}
          </div>

          {/* Input Row */}
          <form
            onSubmit={e => { e.preventDefault(); dispatch(); }}
            style={{ display: 'flex', gap: '0.55rem', marginTop: '0.65rem' }}
          >
            <button
              type="button"
              onClick={toggleMic}
              className="btn-secondary"
              title={isListening ? 'Listening… (click to stop)' : 'Click to speak (Web Speech STT)'}
              style={{
                padding: '0.5rem 0.65rem',
                flexShrink: 0,
                borderColor: isListening ? '#f43f5e' : undefined,
                background: isListening ? 'rgba(244,63,94,0.15)' : undefined,
              }}
            >
              <Mic size={16} color={isListening ? '#f43f5e' : '#38bdf8'} />
            </button>

            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder={
                isListening
                  ? '🎤 Listening for speech…'
                  : isExecuting
                  ? 'JARVIS is orchestrating your task…'
                  : 'Type or speak a command for JARVIS…'
              }
              className="input-field"
              style={{ flex: 1 }}
              disabled={isExecuting || isListening}
            />

            <button
              type="submit"
              className="btn-primary"
              disabled={isExecuting || !inputText.trim()}
              style={{ flexShrink: 0 }}
            >
              {isExecuting ? <Loader2 size={15} className="spin" /> : <Send size={15} />}
              {isExecuting ? 'Running…' : 'Execute'}
            </button>
          </form>
        </div>

        {/* RIGHT: Live Execution Stream */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', height: '600px' }}>
          <div className="panel-header">
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Terminal size={17} color="#00f2fe" />
              Live Execution Stream
            </h2>
            <span className={isExecuting ? 'badge-amber' : 'badge-success'}>
              {isExecuting ? 'ORCHESTRATING…' : 'READY'}
            </span>
          </div>

          {/* Steps list */}
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {activeSteps.length > 0 ? (
              activeSteps.map(step => (
                <div
                  key={step.step_id}
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: '10px',
                    background: step.status === 'RUNNING'
                      ? 'rgba(6,182,212,0.1)'
                      : step.status === 'COMPLETED'
                      ? 'rgba(16,185,129,0.07)'
                      : 'rgba(10,14,26,0.6)',
                    border: step.status === 'COMPLETED'
                      ? '1px solid rgba(16,185,129,0.25)'
                      : '1px solid var(--border-color)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: '0.65rem',
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.45rem',
                        marginBottom: '0.25rem',
                        fontWeight: 700,
                        fontSize: '0.83rem',
                        color: agentColor[step.agent_role] ?? '#38bdf8',
                      }}
                    >
                      <StepStatusIcon status={step.status} />
                      {step.title}
                    </div>
                    <div style={{ fontSize: '0.77rem', color: '#94a3b8', lineHeight: 1.4 }}>
                      {step.message}
                    </div>
                  </div>
                  {step.latency_ms !== undefined && (
                    <span style={{ fontSize: '0.7rem', color: '#475569', flexShrink: 0 }}>
                      {step.latency_ms}ms
                    </span>
                  )}
                </div>
              ))
            ) : (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#475569', textAlign: 'center', gap: '0.75rem' }}>
                <Terminal size={36} color="#1e293b" />
                <p style={{ fontSize: '0.85rem' }}>Execute a voice or text command to observe real‑time agent orchestration events.</p>
                <p style={{ fontSize: '0.75rem', color: '#334155' }}>4 steps: Memory → Planner → Execution → Verifier</p>
              </div>
            )}
          </div>

          {/* Execution stats footer */}
          {activeSteps.length > 0 && (
            <div
              style={{
                marginTop: '0.75rem',
                paddingTop: '0.65rem',
                borderTop: '1px solid var(--border-color)',
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap',
              }}
            >
              {[
                { label: 'Steps Completed', value: `${activeSteps.filter(s => s.status === 'COMPLETED').length} / ${activeSteps.length}`, color: '#34d399' },
                { label: 'Agents Active', value: new Set(activeSteps.map(s => s.agent_role)).size.toString(), color: '#38bdf8' },
                { label: 'Total Latency', value: `${activeSteps.reduce((a, s) => a + (s.latency_ms ?? 0), 0).toFixed(0)}ms`, color: '#c084fc' },
              ].map(stat => (
                <div key={stat.label} style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                  <span style={{ fontSize: '0.68rem', color: '#475569', textTransform: 'uppercase', fontWeight: 700 }}>{stat.label}</span>
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: stat.color }}>{stat.value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── High-Risk Approval Dialog ── */}
      {pendingApproval && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(4,7,17,0.88)',
            backdropFilter: 'blur(12px)',
            zIndex: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem',
          }}
        >
          <div
            className="panel"
            style={{
              maxWidth: '500px',
              width: '100%',
              border: '1px solid rgba(244,63,94,0.5)',
              boxShadow: '0 0 50px rgba(244,63,94,0.25)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.85rem', color: '#fb7185' }}>
              <ShieldAlert size={22} />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 800 }}>Operator Authorization Required</h2>
            </div>

            <p style={{ fontSize: '0.84rem', color: '#94a3b8', marginBottom: '1rem', lineHeight: 1.5 }}>
              {pendingApproval.action_summary}
            </p>

            <div
              style={{
                background: 'rgba(4,7,17,0.7)',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                fontSize: '0.8rem',
                color: '#f8fafc',
                marginBottom: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem',
              }}
            >
              <div>Risk Level: <strong style={{ color: '#fb7185' }}>{pendingApproval.risk_level}</strong></div>
              <div>Command: <strong style={{ color: '#38bdf8' }}>{pendingApproval.command}</strong></div>
              {pendingApproval.target_tool && (
                <div>Target Tool: <strong style={{ color: '#c084fc' }}>{pendingApproval.target_tool}</strong></div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                className="btn-secondary"
                onClick={() => handleApproval(false)}
                style={{ borderColor: '#f43f5e', color: '#fb7185' }}
              >
                <AlertTriangle size={14} /> Reject
              </button>
              <button
                className="btn-primary"
                onClick={() => handleApproval(true)}
                style={{ background: 'linear-gradient(135deg,#059669,#047857)' }}
              >
                <CheckCircle2 size={14} /> Authorize Execution
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
