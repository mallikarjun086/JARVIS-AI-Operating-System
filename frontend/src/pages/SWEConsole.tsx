import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Code, Terminal, GitCommit, CheckSquare, ShieldCheck, RotateCcw, FileText, Activity, Layers, Play } from 'lucide-react';

interface CodeModificationLog {
  log_id: string;
  file_path: string;
  action_type: string;
  diff_summary: string;
  backup_id?: string;
  timestamp: string;
}

interface CodeReviewIssue {
  line_number: number;
  severity: string;
  category: string;
  message: string;
  suggestion: string;
}

interface CodeReviewResult {
  file_path: string;
  quality_score: number;
  issues: CodeReviewIssue[];
  summary: string;
}

export const SWEConsolePage: React.FC = () => {
  const [logs, setLogs] = useState<CodeModificationLog[]>([]);
  const [targetFile, setTargetFile] = useState<string>('backend/app/main.py');
  const [fileContent, setFileContent] = useState<string>('# Modified code content');
  const [reviewResult, setReviewResult] = useState<CodeReviewResult | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchLogs = async () => {
    try {
      const resp = await api.get<CodeModificationLog[]>('/swe-agent/logs');
      setLogs(resp.data);
    } catch (err) {
      console.error('Error fetching logs', err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const handleModifyFile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const resp = await api.post('/swe-agent/execute', {
        action_type: 'MODIFY_FILE',
        file_path: targetFile,
        content: fileContent,
      });
      setStatusMsg(`✓ File '${targetFile}' modified. Mandatory backup created & logged.`);
      await fetchLogs();
    } catch (err: any) {
      setStatusMsg(`❌ Modification error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunCodeReview = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post<CodeReviewResult>('/swe-agent/code-review', null, {
        params: { file_path: targetFile }
      });
      setReviewResult(resp.data);
      setStatusMsg(`✓ Code review complete for ${targetFile}. Score: ${resp.data.quality_score}/10`);
    } catch (err: any) {
      setStatusMsg(`❌ Code review error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestoreBackup = async (backupId: string) => {
    try {
      await api.post(`/swe-agent/restore/${backupId}`);
      setStatusMsg(`✓ File restored successfully from backup snapshot '${backupId}'.`);
      await fetchLogs();
    } catch (err: any) {
      setStatusMsg(`❌ Restore error: ${err.response?.data?.detail}`);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Code color="#06b6d4" />
            <span>Autonomous Software Engineering Agent Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Repo Reader, Safe File Edits with Mandatory Pre-Edit Backup Snapshots, Automated Code Reviews & AST Analysis.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Safe File Modification Form */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck color="#10b981" size={18} />
            <span>Safe Code Modification (Mandatory Pre-Edit Backup)</span>
          </h2>

          <form onSubmit={handleModifyFile} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Target Relative File Path</label>
              <input
                type="text"
                value={targetFile}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTargetFile(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Code Content</label>
              <textarea
                rows={6}
                value={fileContent}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFileContent(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff', fontFamily: 'monospace', fontSize: '0.85rem' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="submit" className="btn-primary" disabled={isLoading} style={{ flex: 1 }}>
                Safe Save & Modify
              </button>
              <button type="button" onClick={handleRunCodeReview} disabled={isLoading} className="btn-primary" style={{ flex: 1, background: 'linear-gradient(135deg, #8b5cf6, #ec4899)' }}>
                Run Code Review
              </button>
            </div>
          </form>

          {reviewResult && (
            <div style={{ marginTop: '1.25rem', background: 'rgba(15, 23, 42, 0.8)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <strong style={{ color: '#fff', fontSize: '0.9rem' }}>Code Review Findings</strong>
                <span className="badge-success">Score: {reviewResult.quality_score}/10</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{reviewResult.summary}</div>
              {reviewResult.issues.map((iss: CodeReviewIssue, idx: number) => (
                <div key={idx} style={{ fontSize: '0.75rem', color: '#fca5a5', marginTop: '0.3rem' }}>
                  Line {iss.line_number} [{iss.category}]: {iss.message}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Mandatory Modification Audit Trail & Backup Restoration */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText color="#a78bfa" size={18} />
            <span>Modification Audit Log & Backup Restores</span>
          </h2>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '450px' }}>
            {logs.map((log: CodeModificationLog) => (
              <div key={log.log_id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                  <strong style={{ color: '#38bdf8', fontSize: '0.85rem' }}>{log.file_path.split('\\').pop()?.split('/').pop()}</strong>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(log.timestamp).toLocaleTimeString()}</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#fff', marginBottom: '0.4rem' }}>{log.diff_summary}</div>
                {log.backup_id && (
                  <button onClick={() => handleRestoreBackup(log.backup_id!)} className="btn-primary" style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem', background: 'rgba(245, 158, 11, 0.2)', border: '1px solid #f59e0b', color: '#fcd34d', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <RotateCcw size={12} />
                    <span>Restore Pre-Edit Backup ({log.backup_id})</span>
                  </button>
                )}
              </div>
            ))}
            {logs.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem', fontSize: '0.85rem' }}>
                No modifications logged yet. File edits will create backups and audit entries.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
