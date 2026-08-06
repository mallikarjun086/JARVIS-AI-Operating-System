import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Monitor, MousePointer, Keyboard, ShieldAlert, RotateCcw, Camera, Eye, Zap } from 'lucide-react';

interface WindowInfo {
  hwnd: number;
  title: string;
  process_name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  is_active: bool;
}

interface AutomationResponse {
  action_id: string;
  action_type: string;
  status: string;
  result?: any;
  error_message?: string;
  is_reversible: bool;
  undo_action_id?: string;
}

export const AutomationConsolePage: React.FC = () => {
  const [windows, setWindows] = useState<WindowInfo[]>([]);
  const [screenCaptureB64, setScreenCaptureB64] = useState<string>('');
  const [ocrText, setOcrText] = useState<string>('');
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: 500, y: 300 });
  const [keyInput, setKeyInput] = useState<string>('Hello JARVIS Automation');
  const [isEmergencyStopped, setIsEmergencyStopped] = useState<boolean>(false);
  const [lastAction, setLastAction] = useState<AutomationResponse | null>(null);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchWindows = async () => {
    try {
      const resp = await api.get<WindowInfo[]>('/automation/windows');
      setWindows(resp.data);
    } catch (err) {
      console.error('Error listing windows', err);
    }
  };

  useEffect(() => {
    fetchWindows();
  }, []);

  const handleScreenCapture = async () => {
    try {
      const resp = await api.post<{ image_base64: string }>('/automation/screen-capture');
      setScreenCaptureB64(resp.data.image_base64);
      setStatusMsg('✓ Screen capture buffer updated.');
    } catch (err: any) {
      setStatusMsg(`❌ Capture error: ${err.response?.data?.detail}`);
    }
  };

  const handleOCR = async () => {
    try {
      const resp = await api.post<{ extracted_text: string }>('/automation/ocr');
      setOcrText(resp.data.extracted_text);
      setStatusMsg('✓ OCR text extraction complete.');
    } catch (err: any) {
      setStatusMsg(`❌ OCR error: ${err.response?.data?.detail}`);
    }
  };

  const handleMouseMove = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post<AutomationResponse>('/automation/execute', {
        action_type: 'MOUSE_MOVE',
        parameters: { x: Number(mousePos.x), y: Number(mousePos.y) },
      });
      setLastAction(resp.data);
      setStatusMsg(`✓ Mouse cursor moved to (${mousePos.x}, ${mousePos.y}). Action is reversible.`);
    } catch (err: any) {
      setStatusMsg(`❌ Action error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTypeKey = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post<AutomationResponse>('/automation/execute', {
        action_type: 'KEY_TYPE',
        parameters: { text: keyInput },
      });
      setLastAction(resp.data);
      setStatusMsg(`✓ Typed string "${keyInput}".`);
    } catch (err: any) {
      setStatusMsg(`❌ Typing error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUndo = async (undoId: string) => {
    try {
      await api.post(`/automation/undo/${undoId}`);
      setStatusMsg(`✓ Reverted action '${undoId}' back to pre-execution state.`);
      setLastAction(null);
    } catch (err: any) {
      setStatusMsg(`❌ Undo error: ${err.response?.data?.detail}`);
    }
  };

  const handleEmergencyStop = async () => {
    try {
      const resp = await api.post<{ is_emergency_stopped: boolean }>('/automation/emergency-stop', null, {
        params: { reason: 'User Panic Button Pressed in UI' }
      });
      setIsEmergencyStopped(resp.data.is_emergency_stopped);
      setStatusMsg('🚨 EMERGENCY STOP ACTIVATED. All automation actions halted.');
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleResume = async () => {
    try {
      const resp = await api.post<{ is_emergency_stopped: boolean }>('/automation/resume');
      setIsEmergencyStopped(resp.data.is_emergency_stopped);
      setStatusMsg('✓ System automation operation resumed.');
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Monitor color="#06b6d4" />
            <span>Windows Desktop Automation Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Mouse, Keyboard, Window Management, Screen Capture, OCR, Emergency Stop & Reversible Undo.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          {isEmergencyStopped ? (
            <button onClick={handleResume} className="btn-primary" style={{ background: '#10b981' }}>
              Resume Operation
            </button>
          ) : (
            <button onClick={handleEmergencyStop} className="btn-primary" style={{ background: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
              <ShieldAlert size={18} />
              <span>EMERGENCY STOP</span>
            </button>
          )}
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: isEmergencyStopped ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.15)', border: isEmergencyStopped ? '1px solid #ef4444' : '1px solid rgba(56, 189, 248, 0.3)', color: isEmergencyStopped ? '#fca5a5' : '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      {/* Undo Alert Banner */}
      {lastAction && lastAction.is_reversible && lastAction.undo_action_id && (
        <div style={{ background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.3)', color: '#fcd34d', padding: '0.85rem 1.25rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Previous action '{lastAction.action_type}' recorded in reversibility log. Pre-execution state captured.</span>
          <button onClick={() => handleUndo(lastAction.undo_action_id!)} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: '#f59e0b', color: '#000', fontWeight: 700, padding: '0.4rem 0.85rem' }}>
            <RotateCcw size={15} />
            <span>Revert / Undo Action</span>
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Hardware Interaction Control Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <MousePointer size={18} color="#06b6d4" />
            <span>Hardware & OS Controls</span>
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Mouse Move */}
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <label style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>Mouse Cursor Movement (Reversible)</label>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <input
                  type="number"
                  value={mousePos.x}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMousePos({ ...mousePos, x: Number(e.target.value) })}
                  placeholder="X"
                  style={{ width: '100px', padding: '0.5rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
                />
                <input
                  type="number"
                  value={mousePos.y}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMousePos({ ...mousePos, y: Number(e.target.value) })}
                  placeholder="Y"
                  style={{ width: '100px', padding: '0.5rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
                />
                <button onClick={handleMouseMove} disabled={isLoading || isEmergencyStopped} className="btn-primary" style={{ padding: '0.5rem 1rem' }}>
                  Move Mouse
                </button>
              </div>
            </div>

            {/* Keyboard Typing */}
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <label style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>Keyboard Text Synthesizer</label>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <input
                  type="text"
                  value={keyInput}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setKeyInput(e.target.value)}
                  style={{ flex: 1, padding: '0.5rem 0.75rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
                />
                <button onClick={handleTypeKey} disabled={isLoading || isEmergencyStopped} className="btn-primary" style={{ padding: '0.5rem 1rem' }}>
                  Type Text
                </button>
              </div>
            </div>

            {/* Perception Controls */}
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
              <button onClick={handleScreenCapture} className="btn-primary" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
                <Camera size={16} />
                <span>Screen Capture</span>
              </button>
              <button onClick={handleOCR} className="btn-primary" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', background: 'linear-gradient(135deg, #8b5cf6, #ec4899)' }}>
                <Eye size={16} />
                <span>Run OCR Text</span>
              </button>
            </div>

            {ocrText && (
              <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid var(--border-color)', color: '#38bdf8', fontSize: '0.85rem' }}>
                <strong>Extracted OCR Text:</strong> {ocrText}
              </div>
            )}
          </div>
        </div>

        {/* Active Desktop Windows List */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Monitor size={18} color="#a78bfa" />
            <span>Active Desktop Windows Detection</span>
          </h2>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px' }}>
            {windows.map((w: WindowInfo) => (
              <div key={w.hwnd} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600 }}>{w.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    HWND: {w.hwnd} | Process: {w.process_name} | Bounds: {w.width}x{w.height} at ({w.x},{w.y})
                  </div>
                </div>
                {w.is_active && <span className="badge-success">ACTIVE FOCUS</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
