import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Users, Play, Activity, MessageSquare, Database, CheckCircle2, ShieldCheck, Zap, Network } from 'lucide-react';

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

export const MultiAgentConsolePage: React.FC = () => {
  const [telemetry, setTelemetry] = useState<AgentTaskTelemetry[]>([]);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [sharedMem, setSharedMem] = useState<Record<string, any>>({});
  const [swarmGoal, setSwarmGoal] = useState<string>('Research microservice architecture, generate API code, test and verify quality');
  const [currentPlan, setCurrentPlan] = useState<SwarmExecutionPlan | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchSwarmData = async () => {
    try {
      const [tRes, mRes, memRes] = await Promise.all([
        api.get<AgentTaskTelemetry[]>('/multi-agent/telemetry'),
        api.get<any>('/multi-agent/messages'),
        api.get<Record<string, any>>('/multi-agent/shared-memory'),
      ]);
      setTelemetry(Array.isArray(tRes.data) ? tRes.data : []);
      const msgList = Array.isArray(mRes.data) ? mRes.data : (mRes.data?.messages || []);
      setMessages(msgList);
      setSharedMem(memRes.data || {});
    } catch (err) {
      console.error('Error fetching swarm data', err);
    }
  };

  useEffect(() => {
    fetchSwarmData();
  }, []);

  const handleDispatchSwarm = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const resp = await api.post<SwarmExecutionPlan>('/multi-agent/dispatch', null, {
        params: { goal: swarmGoal }
      });
      setCurrentPlan(resp.data);
      setStatusMsg(`✓ Swarm goal dispatched! Status: ${resp.data.status}`);
      await fetchSwarmData();
    } catch (err: any) {
      setStatusMsg(`❌ Dispatch error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users color="#06b6d4" />
            <span>Multi-Agent Swarm Execution Dashboard</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            10 Specialized Agents (Coordinator, Planner, Research, Browser, Desktop, Coding, Memory, Vision, Voice, Verifier) with Inter-Agent Messaging & Verifier Approval.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      {/* Swarm Goal Dispatcher Form */}
      <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <form onSubmit={handleDispatchSwarm} style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="text"
            value={swarmGoal}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSwarmGoal(e.target.value)}
            placeholder="Enter multi-agent goal prompt..."
            style={{ flex: 1, padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
          />
          <button type="submit" className="btn-primary" disabled={isLoading} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.75rem 1.5rem' }}>
            <Play size={16} />
            <span>Dispatch Swarm</span>
          </button>
        </form>
      </div>

      {/* 10 Agent Swarm Topology Node Grid */}
      <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Network size={18} color="#a78bfa" />
        <span>10 Specialized Agent Topology Swarm</span>
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {telemetry.map((agent: AgentTaskTelemetry) => (
          <div key={agent.agent_id} className="glass-panel" style={{ padding: '1rem', border: '1px solid var(--border-color)', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <strong style={{ color: '#fff', fontSize: '0.85rem' }}>{agent.role}</strong>
              <span className="badge-success" style={{ fontSize: '0.7rem' }}>ONLINE</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Completed: <span style={{ color: '#38bdf8', fontWeight: 600 }}>{agent.completed_count}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Failed: <span style={{ color: '#f87171', fontWeight: 600 }}>{agent.failed_count}</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Inter-Agent Message Stream Bus */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <MessageSquare size={18} color="#06b6d4" />
            <span>Inter-Agent Communication Bus Log</span>
          </h2>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px' }}>
            {messages.map((m: AgentMessage) => (
              <div key={m.message_id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <span style={{ fontSize: '0.75rem', color: '#a78bfa', fontWeight: 700 }}>
                    {m.sender_role} ➔ {m.recipient_role}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{new Date(m.timestamp).toLocaleTimeString()}</span>
                </div>
                <div style={{ color: '#fff', fontSize: '0.85rem' }}>{m.content}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Current Execution Plan & Verifier Audit Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={18} color="#10b981" />
            <span>Subtask Timeline & Verifier Audit</span>
          </h2>

          {currentPlan ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <span style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600 }}>Plan ID: {currentPlan.plan_id}</span>
                <span className="badge-success">{currentPlan.status}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {currentPlan.tasks.map((task: SubTaskSpec) => (
                  <div key={task.subtask_id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ color: '#fff', fontSize: '0.85rem', fontWeight: 600 }}>[{task.assigned_agent}] {task.goal}</div>
                    </div>
                    <span className="badge-success">{task.status}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '3rem', fontSize: '0.85rem' }}>
              Dispatch a goal to visualize parallel subtask timeline and Verifier approval.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
