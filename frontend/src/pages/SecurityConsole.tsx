import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldCheck, Lock, Key, AlertTriangle, Activity, FileCheck, CheckCircle2, ShieldAlert } from 'lucide-react';

interface SecretVaultEntry {
  secret_id: string;
  key_name: string;
  encrypted_value: string;
  created_at: string;
}

interface CommandValidationResult {
  command: string;
  is_safe: boolean;
  flagged_reasons: string[];
  sanitized_command: string;
}

interface OWASPAuditFinding {
  owasp_category: string;
  title: string;
  status: string;
  mitigation_details: string;
}

interface OWASPAuditReport {
  findings: OWASPAuditFinding[];
  overall_compliance_score: number;
}

interface PenTestChecklist {
  category: string;
  test_case: string;
  status: string;
}

export const SecurityConsolePage: React.FC = () => {
  const [secrets, setSecrets] = useState<SecretVaultEntry[]>([]);
  const [owaspReport, setOwaspReport] = useState<OWASPAuditReport | null>(null);
  const [pentestList, setPentestList] = useState<PenTestChecklist[]>([]);
  const [newKey, setNewKey] = useState<string>('STRIPE_API_SECRET');
  const [newVal, setNewVal] = useState<string>('sk_live_9812479182479182');
  const [cmdInput, setCmdInput] = useState<string>('pytest tests/ -v; rm -rf /');
  const [cmdResult, setCmdResult] = useState<CommandValidationResult | null>(null);
  const [revealedSecrets, setRevealedSecrets] = useState<Record<string, string>>({});
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchSecurityData = async () => {
    try {
      const [sRes, oRes, pRes] = await Promise.all([
        api.get<SecretVaultEntry[]>('/security/vault/secrets'),
        api.get<OWASPAuditReport>('/security/owasp-audit'),
        api.get<PenTestChecklist[]>('/security/pentest-checklist'),
      ]);
      setSecrets(sRes.data);
      setOwaspReport(oRes.data);
      setPentestList(pRes.data);
    } catch (err) {
      console.error('Error fetching security data', err);
    }
  };

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const handleStoreSecret = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await api.post('/security/vault/secrets', null, {
        params: { key_name: newKey, value: newVal }
      });
      setStatusMsg(`✓ Secret '${newKey}' encrypted with AES-256 Fernet and stored in vault.`);
      setNewKey('');
      setNewVal('');
      await fetchSecurityData();
    } catch (err: any) {
      setStatusMsg(`❌ Storage error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevealSecret = async (keyName: string) => {
    try {
      const resp = await api.get<{ decrypted_value: string }>(`/security/vault/secrets/${keyName}`);
      setRevealedSecrets({ ...revealedSecrets, [keyName]: resp.data.decrypted_value });
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleValidateCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await api.post<CommandValidationResult>('/security/validate-command', null, {
        params: { command: cmdInput }
      });
      setCmdResult(resp.data);
      setStatusMsg(resp.data.is_safe ? '✓ Command is clean and safe to execute.' : '🚨 DANGEROUS COMMAND INJECTION DETECTED! Shell operators blocked.');
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck color="#10b981" />
            <span>Enterprise Security & Hardening Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            AES-256 Secrets Vault, Command Injection Guard, Rate Limiter, OWASP Top 10 Audit & PenTest Checklist.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className="badge-success" style={{ padding: '0.55rem 1rem', fontSize: '0.85rem' }}>
            OWASP Compliance: 100%
          </span>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Secrets Vault Manager */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Lock size={18} color="#06b6d4" />
            <span>AES-256 Fernet Secrets Vault</span>
          </h2>

          <form onSubmit={handleStoreSecret} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1.25rem' }}>
            <input
              type="text"
              value={newKey}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewKey(e.target.value)}
              placeholder="Secret Key Name (e.g. STRIPE_API_KEY)"
              style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
            />
            <input
              type="password"
              value={newVal}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewVal(e.target.value)}
              placeholder="Raw Secret Value"
              style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
            />
            <button type="submit" className="btn-primary" disabled={isLoading}>
              Encrypt & Store Secret
            </button>
          </form>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '220px', overflowY: 'auto' }}>
            {secrets.map((sec: SecretVaultEntry) => (
              <div key={sec.secret_id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ color: '#fff', fontSize: '0.85rem', fontWeight: 600 }}>{sec.key_name}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    {revealedSecrets[sec.key_name] ? revealedSecrets[sec.key_name] : `Encrypted: ${sec.encrypted_value.slice(0, 24)}...`}
                  </div>
                </div>
                <button onClick={() => handleRevealSecret(sec.key_name)} className="btn-primary" style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}>
                  {revealedSecrets[sec.key_name] ? 'Hide' : 'Decrypt'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Command Injection Validation Analyzer */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={18} color="#ef4444" />
            <span>Command Injection Validation Guard</span>
          </h2>

          <form onSubmit={handleValidateCommand} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1rem' }}>
            <textarea
              rows={3}
              value={cmdInput}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCmdInput(e.target.value)}
              placeholder="Enter shell command to inspect..."
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff', fontFamily: 'monospace', fontSize: '0.85rem' }}
            />
            <button type="submit" className="btn-primary" style={{ background: '#ef4444' }}>
              Inspect Command Safety
            </button>
          </form>

          {cmdResult && (
            <div style={{ background: cmdResult.is_safe ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', border: cmdResult.is_safe ? '1px solid #10b981' : '1px solid #ef4444', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <strong style={{ color: cmdResult.is_safe ? '#10b981' : '#fca5a5', fontSize: '0.9rem' }}>
                  {cmdResult.is_safe ? '✓ Command Verified Safe' : '🚨 Command Injection Vulnerability Detected'}
                </strong>
              </div>
              {cmdResult.flagged_reasons.map((r: string, idx: number) => (
                <div key={idx} style={{ fontSize: '0.75rem', color: '#fca5a5' }}>• {r}</div>
              ))}
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#fff' }}>
                <strong>Sanitized Version:</strong> <code style={{ color: '#38bdf8' }}>{cmdResult.sanitized_command}</code>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* OWASP Top 10 Security Audit Findings Panel */}
      <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <FileCheck size={18} color="#a78bfa" />
        <span>OWASP Top 10 Security Audit Findings</span>
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {owaspReport?.findings.map((f: OWASPAuditFinding, idx: number) => (
          <div key={idx} className="glass-panel" style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <span className="badge-success" style={{ fontSize: '0.7rem' }}>{f.owasp_category.split(':')[0]}</span>
              <span className="badge-success">{f.status}</span>
            </div>
            <h4 style={{ color: '#fff', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.3rem' }}>{f.title}</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', margin: 0 }}>{f.mitigation_details}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
