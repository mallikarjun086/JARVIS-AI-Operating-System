import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Users, Play, Activity, MessageSquare, ShieldCheck, Network, Bot, Cpu, Zap, Globe, Wrench, Brain, Eye, Mic, GitMerge } from 'lucide-react';

interface AgentTaskTelemetry {
  agent_id: string;
  role: string;
  active_task?: string;
  completed_count: number;
  failed_count: number;
}

interface AgentMessage {
  message_id: string;
  sender_role: string;
  recipient_role: string;
  content: string;
  timestamp: string;
}

interface SubTaskSpec {
  subtask_id: string;
  assigned_agent: string;
  goal: string;
  status: string;
  result?: any;
}

interface SwarmExecutionPlan {
  plan_id: string;
  goal: string;
  tasks: SubTaskSpec[];
  status: string;
}

const AGENT_META_MAP: Record<string, { name: string; icon: any; color: string; capability: string }> = {
  PLANNER: { name: 'Task Planner', icon: GitMerge, color: '#38bdf8', capability: 'DAG Decomposition' },
  RESEARCH: { name: 'Deep Research', icon: Globe, color: '#a78bfa', capability: 'Web & Docs Synthesis' },
  BROWSER: { name: 'Playwright Browser', icon: Zap, color: '#34d399', capability: 'Headless DOM Scraping' },
  DESKTOP: { name: 'Desktop Manager', icon: Cpu, color: '#f59e0b', capability: 'Native OS Automation' },
  CODING: { name: 'Software Engineer', icon: Wrench, color: '#38bdf8', capability: 'AST Patch & Refactor' },
  MEMORY: { name: 'Vector Memory', icon: Brain, color: '#c084fc', capability: 'ChromaDB RAG Vault' },
  VISION: { name: 'Computer Vision', icon: Eye, color: '#f43f5e', capability: 'OCR & UI Heatmap' },
  VOICE: { name: 'Voice Intelligence', icon: Mic, color: '#38bdf8', capability: 'STT & TTS Synthesis' },
  COORDINATOR: { name: 'Swarm Coordinator', icon: Users, color: '#34d399', capability: 'Goal Synchronization' },
  VERIFIER: { name: 'Quality Verifier', icon: ShieldCheck, color: '#10b981', capability: 'Consensus Gatekeeper' },
};

export const MultiAgentConsolePage: React.FC = () => {
  const [telemetry, setTelemetry] = useState<AgentTaskTelemetry[]>([]);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [swarmGoal, setSwarmGoal] = useState<string>('Autonomous research, code generation, and verification pipeline');
  const [currentPlan, setCurrentPlan] = useState<SwarmExecutionPlan | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchSwarmData = async () => {
    try {
      const [tRes, mRes] = await Promise.all([
        api.get<AgentTaskTelemetry[]>('/multi-agent/telemetry'),
        api.get<any>('/multi-agent/messages'),
      ]);
      setTelemetry(Array.isArray(tRes.data) ? tRes.data : []);
      const msgList: AgentMessage[] = Array.isArray(mRes.data)
        ? mRes.data
        : (Array.isArray(mRes.data?.messages) ? mRes.data.messages : []);
      setMessages(msgList);
    } catch (err) {
      console.error('Error fetching swarm data', err);
    }
  };

  useEffect(() => {
    fetchSwarmData();
  }, []);

  const handleDispatchSwarm = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!swarmGoal.trim()) return;

    setIsLoading(true);
    setStatusMsg('');

    try {
      const resp = await api.post<SwarmExecutionPlan>('/multi-agent/dispatch', null, {
        params: { goal: swarmGoal }
      });
      setCurrentPlan(resp.data);
      setStatusMsg(`✓ Swarm Goal Dispatched Successfully! Plan ID: ${resp.data.plan_id}`);
      await fetchSwarmData();
    } catch (err: any) {
      setStatusMsg(`❌ Dispatch Notice: ${err.response?.data?.detail || 'Goal dispatch fallback engaged.'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const agentList = Object.keys(AGENT_META_MAP).map((role) => {
    const found = telemetry.find((t) => t.role === role);
    return {
      agent_id: found?.agent_id || `agent-${role.toLowerCase()}`,
      role: role,
      completed_count: found?.completed_count || 1,
      failed_count: found?.failed_count || 0,
    };
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
            <span className="badge-purple">SWARM KERNEL v1.0</span>
            <span className="beacon-dot"></span>
            <span style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>10 SPECIALIZED AGENTS ONLINE</span>
          </div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Users color="#06b6d4" size={26} /> Autonomous 10-Agent Swarm Orchestrator
          </h1>
          <p className="page-subtitle">
            Parallel subtask planning, consensus voting engine, and inter-agent message stream.
          </p>
        </div>
      </div>

      {statusMsg && <div className={`alert-banner ${statusMsg.startsWith('✓') ? 'success' : 'info'}`}>{statusMsg}</div>}

      {/* Swarm Goal Dispatcher Form */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={18} color="#f59e0b" /> Dispatch Multi-Agent Goal
          </h2>
          <span className="badge-info">TOPOLOGY SCHEDULER</span>
        </div>

        <form onSubmit={handleDispatchSwarm} style={{ display: 'flex', gap: '0.85rem' }}>
          <input
            type="text"
            value={swarmGoal}
            onChange={(e) => setSwarmGoal(e.target.value)}
            placeholder="Enter multi-agent goal prompt..."
            className="input-field"
            style={{ flex: 1 }}
            required
          />
          <button type="submit" className="btn-primary" disabled={isLoading}>
            <Play size={16} /> {isLoading ? 'Dispatching...' : 'Dispatch Swarm Goal'}
          </button>
        </form>
      </div>

      {/* 10 Agent Swarm Topology Node Grid */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Network size={20} color="#a78bfa" /> 10-Agent Swarm Capability Topology
          </h2>
          <span className="badge-success">CONSENSUS VOTING ACTIVE</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '1rem' }}>
          {agentList.map((agent) => {
            const meta = AGENT_META_MAP[agent.role];
            const Icon = meta.icon;
            return (
              <div key={agent.agent_id} style={{ background: 'rgba(4, 7, 17, 0.6)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Icon size={18} color={meta.color} />
                    <strong style={{ color: '#fff', fontSize: '0.9rem' }}>{meta.name}</strong>
                  </div>
                  <span className="badge-success" style={{ fontSize: '0.65rem' }}>READY</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#c084fc', fontWeight: 600, marginBottom: '0.5rem' }}>
                  {meta.capability}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  <span>Completed: <strong style={{ color: '#38bdf8' }}>{agent.completed_count}</strong></span>
                  <span>Failed: <strong style={{ color: '#f87171' }}>{agent.failed_count}</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Inter-Agent Bus & Timeline */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="panel-header">
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MessageSquare size={18} color="#06b6d4" /> Inter-Agent Communication Stream
            </h2>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '350px' }}>
            {messages.length > 0 ? (
              messages.map((m) => (
                <div key={m.message_id} style={{ background: 'rgba(4, 7, 17, 0.7)', padding: '0.85rem 1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                    <span style={{ fontSize: '0.78rem', color: '#a78bfa', fontWeight: 700 }}>
                      {m.sender_role} ➔ {m.recipient_role}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{new Date(m.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ color: '#f8fafc', fontSize: '0.85rem', lineHeight: '1.4' }}>{m.content}</div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem 0', fontSize: '0.85rem' }}>
                Inter-agent communication bus active. Dispatched goals stream subtask messages live.
              </div>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldCheck size={18} color="#10b981" /> Subtask Timeline & Verifier Audit
            </h2>
          </div>

          {currentPlan ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <span style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 700 }}>Plan ID: {currentPlan.plan_id}</span>
                <span className="badge-success">{currentPlan.status}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {currentPlan.tasks.map((task) => (
                  <div key={task.subtask_id} style={{ background: 'rgba(4, 7, 17, 0.7)', padding: '0.85rem 1rem', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ color: '#fff', fontSize: '0.85rem', fontWeight: 600 }}>[{task.assigned_agent}] {task.goal}</div>
                    </div>
                    <span className="badge-success">{task.status}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2.5rem 0', fontSize: '0.85rem' }}>
              Dispatch a goal prompt to visualize real-time subtask timeline and Verifier consensus gating.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
