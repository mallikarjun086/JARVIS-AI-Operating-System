import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Network, Play, ShieldAlert, RotateCcw, CheckCircle, Clock, FileText, Database, ArrowRight } from 'lucide-react';

interface WorkflowDefinition {
  definition_id: string;
  name: string;
  description: string;
  nodes: any[];
}

interface WorkflowInstance {
  instance_id: string;
  definition_id: string;
  name: string;
  status: string;
  current_node_id?: string;
  variables: Record<string, any>;
  execution_history: any[];
  pending_approval_id?: string;
}

export const WorkflowConsolePage: React.FC = () => {
  const [definitions, setDefinitions] = useState<WorkflowDefinition[]>([]);
  const [instances, setInstances] = useState<WorkflowInstance[]>([]);
  const [currentInstance, setCurrentInstance] = useState<WorkflowInstance | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchWorkflows = async () => {
    try {
      const [dRes, iRes] = await Promise.all([
        api.get<WorkflowDefinition[]>('/workflow/definitions'),
        api.get<WorkflowInstance[]>('/workflow/instances'),
      ]);
      setDefinitions(dRes.data);
      setInstances(iRes.data);
      if (iRes.data.length > 0) setCurrentInstance(iRes.data[0]);
    } catch (err) {
      console.error('Error fetching workflows', err);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleExecuteWorkflow = async (defId: string) => {
    setIsLoading(true);
    try {
      const resp = await api.post<WorkflowInstance>(`/workflow/execute/${defId}`);
      setCurrentInstance(resp.data);
      setStatusMsg(`✓ Workflow triggered! Status: ${resp.data.status}`);
      await fetchWorkflows();
    } catch (err: any) {
      setStatusMsg(`❌ Execution error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRespondApproval = async (instanceId: string, approved: boolean) => {
    try {
      const resp = await api.post<WorkflowInstance>(`/workflow/instances/${instanceId}/approve`, null, {
        params: { approved }
      });
      setCurrentInstance(resp.data);
      setStatusMsg(approved ? '✓ Human Approval granted! Pipeline completed.' : '🛑 Approval rejected. Workflow rolled back.');
      await fetchWorkflows();
    } catch (err: any) {
      setStatusMsg(`❌ Response error: ${err.response?.data?.detail}`);
    }
  };

  const handleRollback = async (instanceId: string) => {
    try {
      const resp = await api.post<WorkflowInstance>(`/workflow/instances/${instanceId}/rollback`);
      setCurrentInstance(resp.data);
      setStatusMsg('🛑 Workflow manually rolled back to pre-execution state.');
      await fetchWorkflows();
    } catch (err: any) {
      setStatusMsg(`❌ Rollback error: ${err.response?.data?.detail}`);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Network color="#06b6d4" />
            <span>Workflow Automation Subsystem Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            DAG Workflows, Conditional Branching, Loops, Human Approval Interception, Scheduling, Retries, Rollback & Persistence.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      {/* Human Approval Pending Interception Banner */}
      {currentInstance?.status === 'PAUSED_FOR_APPROVAL' && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#fca5a5', padding: '1rem 1.25rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldAlert color="#ef4444" size={20} />
              <span>Human Approval Interception: Review Application Package</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Resume tailored and cover letter generated. Operator authorization required before submitting application.
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button onClick={() => handleRespondApproval(currentInstance.instance_id, true)} className="btn-primary" style={{ background: '#10b981' }}>
              Approve & Submit
            </button>
            <button onClick={() => handleRespondApproval(currentInstance.instance_id, false)} className="btn-primary" style={{ background: '#ef4444' }}>
              Reject & Rollback
            </button>
          </div>
        </div>
      )}

      {/* Registered Templates Section */}
      <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <FileText size={18} color="#a78bfa" />
        <span>Workflow Pipeline Templates</span>
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        {definitions.map((def: WorkflowDefinition) => (
          <div key={def.definition_id} className="glass-panel" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div>
                <h3 style={{ color: '#fff', fontSize: '1rem', fontWeight: 700 }}>{def.name}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.2rem' }}>{def.description}</p>
              </div>
              <button onClick={() => handleExecuteWorkflow(def.definition_id)} disabled={isLoading} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Play size={16} />
                <span>Execute Pipeline</span>
              </button>
            </div>

            {/* Pipeline Step Visualizer */}
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', overflowX: 'auto', paddingTop: '0.5rem' }}>
              {def.nodes.map((node: any, idx: number) => (
                <React.Fragment key={node.node_id}>
                  <div style={{ background: node.node_type === 'HUMAN_APPROVAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(15, 23, 42, 0.7)', border: node.node_type === 'HUMAN_APPROVAL' ? '1px solid #ef4444' : '1px solid var(--border-color)', padding: '0.5rem 0.85rem', borderRadius: '6px', fontSize: '0.75rem', color: '#fff', whiteSpace: 'nowrap' }}>
                    {node.name}
                  </div>
                  {idx < def.nodes.length - 1 && <ArrowRight size={14} color="var(--text-muted)" />}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Current Execution State Inspector */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Clock size={18} color="#06b6d4" />
              <span>Live Instance Execution State</span>
            </h2>
            {currentInstance && (
              <button onClick={() => handleRollback(currentInstance.instance_id)} className="btn-primary" style={{ background: '#f59e0b', color: '#000', fontWeight: 700, padding: '0.35rem 0.75rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <RotateCcw size={12} />
                <span>Rollback</span>
              </button>
            )}
          </div>

          {currentInstance ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div>
                  <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600 }}>{currentInstance.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Instance ID: {currentInstance.instance_id}</div>
                </div>
                <span className="badge-success">{currentInstance.status}</span>
              </div>

              <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>Execution History Nodes</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '250px', overflowY: 'auto' }}>
                {currentInstance.execution_history.map((hist: any, idx: number) => (
                  <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.5rem 0.85rem', borderRadius: '6px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                    <span style={{ color: '#fff' }}>{hist.name || hist.action}</span>
                    <span className="badge-success">{hist.status || 'DONE'}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem', fontSize: '0.85rem' }}>
              No workflow instance active. Click Execute Pipeline above.
            </div>
          )}
        </div>

        {/* Variable Scope Inspector */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={18} color="#10b981" />
            <span>Workflow Variable Scope & Output Context</span>
          </h2>

          {currentInstance ? (
            <pre style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', color: '#38bdf8', fontSize: '0.85rem', maxHeight: '350px', overflowY: 'auto' }}>
              {JSON.stringify(currentInstance.variables, null, 2)}
            </pre>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem', fontSize: '0.85rem' }}>
              Variable scope will populate upon workflow execution.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
