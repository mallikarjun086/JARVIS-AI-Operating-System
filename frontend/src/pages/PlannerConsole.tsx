import React, { useState } from 'react';
import { api } from '../services/api';
import { Network, Play, CheckCircle2, ShieldAlert, Zap, Code, ArrowRight } from 'lucide-react';

interface SubTask {
  id: string;
  title: string;
  description: string;
  tool_required?: string;
  priority: string;
  dependencies: string[];
  max_retries: number;
}

interface ExecutionBatch {
  batch_id: number;
  parallel_task_ids: string[];
}

interface RecoveryPolicy {
  task_id: string;
  strategy: string;
  max_retries: number;
  backoff_seconds: number;
}

interface ExecutionPlan {
  plan_id: string;
  goal: string;
  intent_summary: string;
  subtasks: SubTask[];
  execution_graph: ExecutionBatch[];
  topological_order: string[];
  is_valid_dag: boolean;
  recovery_policies: RecoveryPolicy[];
}

export const PlannerConsolePage: React.FC = () => {
  const [goalInput, setGoalInput] = useState<string>('Create a Spring Boot project and push to GitHub.');
  const [plan, setPlan] = useState<ExecutionPlan | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalInput.trim()) return;

    setIsGenerating(true);
    setErrorMsg('');

    try {
      const resp = await api.post<ExecutionPlan>('/planner/plan', {
        goal: goalInput,
        allow_parallel: true,
      });
      setPlan(resp.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to generate task plan.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Network color="#06b6d4" />
            <span>Intelligent Task Planner & Execution Graph Engine</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Natural Language Decomposition, DAG Dependency Graph Validation, Parallel Batching, and Failure Recovery.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          ⚠️ {errorMsg}
        </div>
      )}

      {/* Input Form */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <form onSubmit={handleGeneratePlan} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <input
            type="text"
            value={goalInput}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGoalInput(e.target.value)}
            placeholder="Enter natural language goal (e.g. 'Create a Spring Boot project and push to GitHub.')"
            style={{ flex: 1, padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.95rem' }}
          />
          <button type="submit" className="btn-primary" disabled={isGenerating} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem' }}>
            <Play size={16} />
            <span>{isGenerating ? 'Decomposing...' : 'Generate Plan'}</span>
          </button>
        </form>
      </div>

      {plan && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Intent Summary Banner */}
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#06b6d4', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.05em' }}>Parsed Goal Intent</div>
            <div style={{ fontSize: '1.1rem', color: '#fff', marginTop: '0.25rem', fontWeight: 600 }}>{plan.intent_summary}</div>
            <div style={{ marginTop: '0.5rem', display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <span>Plan ID: {plan.plan_id}</span>
              <span>DAG Status: <strong style={{ color: plan.is_valid_dag ? '#10b981' : '#ef4444' }}>{plan.is_valid_dag ? 'Valid DAG (No Cycles)' : 'Invalid Graph'}</strong></span>
              <span>Total Subtasks: {plan.subtasks.length}</span>
              <span>Parallel Batches: {plan.execution_graph.length}</span>
            </div>
          </div>

          {/* Execution Graph Parallel Batches */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap color="#f59e0b" size={18} />
              <span>Parallel Execution Graph Batches</span>
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {plan.execution_graph.map((batch: ExecutionBatch) => (
                <div key={batch.batch_id} style={{ background: 'rgba(15, 23, 42, 0.6)', borderRadius: '8px', padding: '1rem', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.8rem', color: '#f59e0b', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span>Batch #{batch.batch_id}</span>
                    {batch.parallel_task_ids.length > 1 && <span className="badge-warning">Parallel Concurrent Execution</span>}
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                    {batch.parallel_task_ids.map((tid: string) => {
                      const st = plan.subtasks.find((t: SubTask) => t.id === tid);
                      return (
                        <div key={tid} style={{ flex: 1, minWidth: '220px', background: 'rgba(30, 41, 59, 0.8)', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                            <strong style={{ color: '#38bdf8', fontSize: '0.85rem' }}>{tid}</strong>
                            <span className={st?.priority === 'CRITICAL' ? 'badge-danger' : st?.priority === 'HIGH' ? 'badge-warning' : 'badge-success'}>{st?.priority}</span>
                          </div>
                          <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600 }}>{st?.title}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Tool: {st?.tool_required || 'internal'}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Subtask Details Table */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle2 color="#10b981" size={18} />
              <span>Decomposed Subtask Specification</span>
            </h2>

            <table className="data-table">
              <thead>
                <tr>
                  <th>Task ID</th>
                  <th>Title & Description</th>
                  <th>Priority</th>
                  <th>Dependencies</th>
                  <th>Tool Required</th>
                  <th>Max Retries</th>
                </tr>
              </thead>
              <tbody>
                {plan.subtasks.map((st: SubTask) => (
                  <tr key={st.id}>
                    <td><strong style={{ color: '#38bdf8' }}>{st.id}</strong></td>
                    <td>
                      <div style={{ color: '#fff', fontWeight: 600 }}>{st.title}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{st.description}</div>
                    </td>
                    <td><span className={st.priority === 'CRITICAL' ? 'badge-danger' : st.priority === 'HIGH' ? 'badge-warning' : 'badge-success'}>{st.priority}</span></td>
                    <td>{st.dependencies.length > 0 ? st.dependencies.join(', ') : <span style={{ color: 'var(--text-muted)' }}>None (Root)</span>}</td>
                    <td><code>{st.tool_required || 'None'}</code></td>
                    <td>{st.max_retries}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
