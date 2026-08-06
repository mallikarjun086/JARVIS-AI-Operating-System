import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Globe, Plus, X, Camera, ShieldAlert, Sparkles, Code, CheckCircle, AlertTriangle, Play, Lock } from 'lucide-react';

interface TabInfo {
  tab_id: string;
  url: str;
  title: str;
  is_active: bool;
}

interface HumanApprovalRequest {
  approval_id: string;
  high_risk_type: string;
  target_details: any;
  status: string;
  requested_at: string;
}

interface BrowserActionResponse {
  action_id: string;
  action_type: string;
  status: string;
  result?: any;
  error_message?: string;
  requires_approval: bool;
  approval_id?: string;
}

export const BrowserConsolePage: React.FC = () => {
  const [tabs, setTabs] = useState<TabInfo[]>([]);
  const [activeTabUrl, setActiveTabUrl] = useState<string>('https://jarvis.ai');
  const [screenshotB64, setScreenshotB64] = useState<string>('');
  const [domTree, setDomTree] = useState<any>(null);
  const [aiPrompt, setAiPrompt] = useState<string>('Find the contact form and fill in user details');
  const [pendingApprovals, setPendingApprovals] = useState<HumanApprovalRequest[]>([]);
  const [highRiskType, setHighRiskType] = useState<string>('PAYMENT');
  const [lastAction, setLastAction] = useState<BrowserActionResponse | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchTabsAndApprovals = async () => {
    try {
      const [tRes, aRes] = await Promise.all([
        api.get<TabInfo[]>('/browser/tabs'),
        api.get<HumanApprovalRequest[]>('/browser/approvals'),
      ]);
      setTabs(tRes.data);
      setPendingApprovals(aRes.data);
    } catch (err) {
      console.error('Error fetching tabs/approvals', err);
    }
  };

  useEffect(() => {
    fetchTabsAndApprovals();
  }, []);

  const handleNavigate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const resp = await api.post<BrowserActionResponse>('/browser/execute', {
        action_type: 'NAVIGATE',
        url: activeTabUrl,
      });
      setLastAction(resp.data);
      setStatusMsg(`✓ Navigated active tab to ${activeTabUrl}.`);
      await fetchTabsAndApprovals();
    } catch (err: any) {
      setStatusMsg(`❌ Navigation error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewTab = async () => {
    try {
      await api.post('/browser/execute', { action_type: 'NEW_TAB', url: 'https://jarvis.ai/docs' });
      await fetchTabsAndApprovals();
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleCloseTab = async (tabId: string) => {
    try {
      await api.post('/browser/execute', { action_type: 'CLOSE_TAB', tab_id: tabId });
      await fetchTabsAndApprovals();
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleScreenshot = async () => {
    try {
      const resp = await api.post<{ image_base64: string }>('/browser/screenshot');
      setScreenshotB64(resp.data.image_base64);
      setStatusMsg('✓ Page screenshot captured.');
    } catch (err: any) {
      setStatusMsg(`❌ Screenshot error: ${err.response?.data?.detail}`);
    }
  };

  const handleExtractDOM = async () => {
    try {
      const resp = await api.post('/browser/extract-dom');
      setDomTree(resp.data);
      setStatusMsg('✓ DOM element tree extracted.');
    } catch (err: any) {
      setStatusMsg(`❌ DOM error: ${err.response?.data?.detail}`);
    }
  };

  const handleAINavigate = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post('/browser/ai-navigate', null, { params: { prompt: aiPrompt } });
      setLastAction({ action_id: 'ai-nav', action_type: 'AI_NAVIGATE', status: 'SUCCESS', result: resp.data, requires_approval: false });
      setStatusMsg('✓ AI-assisted navigation sequence executed.');
    } catch (err: any) {
      setStatusMsg(`❌ AI Navigation error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriggerHighRiskAction = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post<BrowserActionResponse>('/browser/execute', {
        action_type: 'CLICK',
        url: activeTabUrl,
        high_risk_type: highRiskType,
      });
      setLastAction(resp.data);
      setStatusMsg(`🛡️ Action '${highRiskType}' intercepted by Human Approval Gatekeeper!`);
      await fetchTabsAndApprovals();
    } catch (err: any) {
      setStatusMsg(`❌ Action error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRespondApproval = async (approvalId: string, approved: boolean) => {
    try {
      await api.post(`/browser/approvals/${approvalId}/respond`, null, { params: { approved } });
      setStatusMsg(approved ? '✓ High-risk operation APPROVED by operator.' : '⛔ High-risk operation REJECTED.');
      await fetchTabsAndApprovals();
    } catch (err: any) {
      setStatusMsg(`❌ Response error: ${err.response?.data?.detail}`);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Globe color="#06b6d4" />
            <span>Playwright Browser Automation Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Multi-Tab Pool, Forms, Cookies, Session Persistence, Screenshots, DOM Extraction & Human Approval Gatekeeper.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      {/* Human Approval Pending Interception Banner */}
      {pendingApprovals.length > 0 && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#fca5a5', padding: '1rem 1.25rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <ShieldAlert color="#ef4444" size={20} />
            <span>Human Approval Authorization Required ({pendingApprovals.length} Pending)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {pendingApprovals.map((appr: HumanApprovalRequest) => (
              <div key={appr.approval_id} style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '0.75rem 1rem', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong style={{ color: '#fff', fontSize: '0.9rem' }}>High-Risk Operation: {appr.high_risk_type}</strong>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Approval ID: {appr.approval_id} | Requested: {new Date(appr.requested_at).toLocaleTimeString()}</div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button onClick={() => handleRespondApproval(appr.approval_id, true)} className="btn-primary" style={{ background: '#10b981', padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}>
                    Approve Execution
                  </button>
                  <button onClick={() => handleRespondApproval(appr.approval_id, false)} className="btn-primary" style={{ background: '#ef4444', padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}>
                    Reject Action
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Browser Tab Bar */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center' }}>
        {tabs.map((t: TabInfo) => (
          <div
            key={t.tab_id}
            style={{
              padding: '0.5rem 0.85rem',
              borderRadius: '8px 8px 0 0',
              background: t.is_active ? 'rgba(30, 41, 59, 0.9)' : 'rgba(15, 23, 42, 0.5)',
              border: t.is_active ? '1px solid #06b6d4' : '1px solid var(--border-color)',
              color: t.is_active ? '#fff' : 'var(--text-muted)',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: 'pointer'
            }}
          >
            <span>{t.title}</span>
            {tabs.length > 1 && (
              <X size={14} onClick={(e) => { e.stopPropagation(); handleCloseTab(t.tab_id); }} />
            )}
          </div>
        ))}
        <button onClick={handleNewTab} className="btn-primary" style={{ padding: '0.4rem 0.75rem', borderRadius: '6px', fontSize: '0.8rem' }}>
          <Plus size={14} />
        </button>
      </div>

      {/* Navigation Address Bar */}
      <div className="glass-panel" style={{ padding: '1rem', marginBottom: '1.5rem' }}>
        <form onSubmit={handleNavigate} style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="url"
            value={activeTabUrl}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setActiveTabUrl(e.target.value)}
            placeholder="Enter web address URL (https://...)"
            style={{ flex: 1, padding: '0.6rem 1rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
          />
          <button type="submit" className="btn-primary" disabled={isLoading}>
            Navigate
          </button>
        </form>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Perception & AI Navigation Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="#06b6d4" />
            <span>AI-Assisted Autonomous Navigation</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Natural Language Navigation Goal</label>
              <textarea
                rows={3}
                value={aiPrompt}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setAiPrompt(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>

            <button onClick={handleAINavigate} disabled={isLoading} className="btn-primary" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
              <Play size={16} />
              <span>Execute Autonomous AI Navigation</span>
            </button>

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button onClick={handleScreenshot} className="btn-primary" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
                <Camera size={16} />
                <span>Screenshot</span>
              </button>
              <button onClick={handleExtractDOM} className="btn-primary" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', background: 'linear-gradient(135deg, #8b5cf6, #ec4899)' }}>
                <Code size={16} />
                <span>Extract DOM</span>
              </button>
            </div>
          </div>
        </div>

        {/* High-Risk Action Tester */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Lock size={18} color="#ef4444" />
            <span>High-Risk Action Interception Test</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Select High-Risk Action Category</label>
              <select
                value={highRiskType}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setHighRiskType(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
              >
                <option value="PAYMENT">PAYMENT (Financial Transaction)</option>
                <option value="PURCHASE">PURCHASE (Order Checkout)</option>
                <option value="EMAIL_SEND">EMAIL_SEND (Dispatch Outgoing Email)</option>
                <option value="ACCOUNT_DELETE">ACCOUNT_DELETE (Data Removal)</option>
              </select>
            </div>

            <button onClick={handleTriggerHighRiskAction} className="btn-primary" style={{ background: '#ef4444' }}>
              Trigger High-Risk Action
            </button>

            {domTree && (
              <div style={{ marginTop: '0.5rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Extracted DOM Structure</label>
                <pre style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border-color)', color: '#38bdf8', fontSize: '0.8rem', maxHeight: '180px', overflowY: 'auto' }}>
                  {JSON.stringify(domTree, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
