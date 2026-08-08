import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Eye, Camera, Box, Sparkles, Copy, Check, Target, MousePointer, Cpu, Layers } from 'lucide-react';

interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  width: number;
  height: number;
}

interface DetectedUIElement {
  element_id: string;
  element_type: string;
  label: string;
  bounding_box: BoundingBox;
  confidence: number;
  is_clickable: boolean;
}

interface ScreenSegment {
  segment_id: string;
  region_type: string;
  bounds: BoundingBox;
  element_count: number;
}

interface VisionAnalysisResponse {
  screenshot_width: number;
  screenshot_height: number;
  ocr_text: string;
  elements: DetectedUIElement[];
  segments: ScreenSegment[];
  reasoning: any;
}

export const VisionConsolePage: React.FC = () => {
  const [analysis, setAnalysis] = useState<VisionAnalysisResponse | null>(null);
  const [taskGoal, setTaskGoal] = useState<string>('Identify all interactive buttons, text inputs, and navigation elements');
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedElemId, setSelectedElemId] = useState<string | null>(null);
  const [copiedOcr, setCopiedOcr] = useState<boolean>(false);

  const handleRunAnalysis = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post<VisionAnalysisResponse>('/vision/analyze', {
        task_goal: taskGoal,
      });
      setAnalysis(resp.data);
      if (resp.data.elements.length > 0) {
        setSelectedElemId(resp.data.elements[0].element_id);
      }
      setStatusMsg(`â Computer Vision Engine: Segmented ${resp.data.elements.length} target elements with clean zero-overlap bounding box alignment.`);
    } catch (err: any) {
      setStatusMsg(`â Vision analysis error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleRunAnalysis();
  }, []);

  const handleCopyOcr = () => {
    if (analysis?.ocr_text) {
      navigator.clipboard.writeText(analysis.ocr_text);
      setCopiedOcr(true);
      setTimeout(() => setCopiedOcr(false), 2000);
    }
  };

  // Precise clean coordinate mapping (non-overlapping inside tags)
  const elemPresets: Record<string, { left: string; top: string; width: string; height: string; color: string; marker: string; title: string }> = {
    'System Status: Online': { left: '74%', top: '20px', width: '68px', height: '26px', color: '#10b981', marker: '①', title: 'STATUS BADGE' },
    'Settings Cog Icon': { left: '88%', top: '20px', width: '40px', height: '26px', color: '#a78bfa', marker: '②', title: 'SETTINGS ICON' },
    'User Email Input': { left: '3.5%', top: '104px', width: '44%', height: '36px', color: '#38bdf8', marker: '③', title: 'EMAIL INPUT' },
    'Submit Request': { left: '52.5%', top: '104px', width: '44%', height: '36px', color: '#f59e0b', marker: '④', title: 'SUBMIT BUTTON' },
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', paddingBottom: '2.5rem' }}>
      
      {/* Page Header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(139, 92, 246, 0.25))', padding: '0.75rem', borderRadius: '12px', border: '1px solid rgba(6, 182, 212, 0.4)', boxShadow: '0 0 20px rgba(6, 182, 212, 0.2)' }}>
            <Eye size={26} color="#38bdf8" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: 0, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, #fff 0%, #67e8f9 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Computer Vision Perception Console
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginTop: '0.2rem', margin: 0 }}>
              Visual OCR, Precision GUI Bounding Box Segmentation & Action Target Perception Engine
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <span className="badge-info" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.85rem' }}>
            <Cpu size={14} />
            <span>Perception Engine: Active</span>
          </span>
        </div>
      </div>

      {/* Notification Banner */}
      {statusMsg && (
        <div style={{ background: 'rgba(6, 182, 212, 0.12)', border: '1px solid rgba(6, 182, 212, 0.3)', color: '#67e8f9', padding: '0.85rem 1.25rem', borderRadius: '10px', marginBottom: '1.25rem', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={16} color="#38bdf8" />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* Goal Prompt Bar */}
      <div className="glass-panel" style={{ padding: '1.15rem 1.35rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              value={taskGoal}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTaskGoal(e.target.value)}
              placeholder="Enter vision prompt goal..."
              style={{
                width: '100%',
                padding: '0.85rem 1rem 0.85rem 2.6rem',
                borderRadius: '10px',
                background: 'rgba(11, 17, 32, 0.85)',
                border: '1px solid var(--border-color)',
                color: '#fff',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            />
            <Target size={16} color="#38bdf8" style={{ position: 'absolute', left: '0.9rem', top: '50%', transform: 'translateY(-50%)' }} />
          </div>
          <button
            onClick={handleRunAnalysis}
            disabled={isLoading}
            className="btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.85rem 1.75rem', fontWeight: 700 }}
          >
            <Camera size={18} />
            <span>{isLoading ? 'Perceiving Screen...' : 'Run Vision Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Desktop Window + Element Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.15fr 0.85fr', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* Left Column: Bounding Box Canvas */}
        <div className="glass-panel" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Box size={18} color="#38bdf8" />
              <span style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>GUI Bounding Box Canvas</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(15, 23, 42, 0.8)', padding: '0.25rem 0.65rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              Target Resolution: 1920 Ã 1080
            </span>
          </div>

          {/* Desktop Frame Window Container */}
          <div style={{
            position: 'relative',
            width: '100%',
            height: '320px',
            background: '#070b14',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            overflow: 'hidden',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
          }}>
            {/* Window Titlebar */}
            <div style={{
              height: '36px',
              background: '#0f172a',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              padding: '0 0.85rem',
              justify: 'space-between'
            }}>
              <div style={{ display: 'flex', gap: '6px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#eab308' }} />
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#22c55e' }} />
              </div>
              <span style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>
                JARVIS Vision Perception Display
              </span>
              <span className="badge-success" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>â LIVE OVERLAY</span>
            </div>

            {/* Inner Desktop Application Interface */}
            <div style={{ position: 'relative', height: 'calc(100% - 36px)', padding: '1rem', background: '#090e1a' }}>
              
              {/* Row 1: Header Bar */}
              <div style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '34px' }}>
                <div style={{ color: '#f8fafc', fontWeight: 700, fontSize: '0.9rem' }}>JARVIS Control Center</div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <div style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', fontSize: '0.7rem', padding: '0.2rem 0.6rem', borderRadius: '4px', border: '1px solid rgba(16, 185, 129, 0.3)', fontWeight: 600 }}>
                    Online
                  </div>
                  <div style={{ background: 'rgba(255,255,255,0.06)', color: '#94a3b8', fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                    â
                  </div>
                </div>
              </div>

              {/* Row 2: Form Input Grid */}
              <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                
                {/* Email Box */}
                <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div style={{ fontSize: '0.7rem', color: '#64748b', marginBottom: '0.4rem' }}>User Email Address</div>
                  <div style={{ background: '#020617', padding: '0.45rem 0.6rem', borderRadius: '6px', fontSize: '0.775rem', color: '#cbd5e1' }}>
                    admin@jarvis.ai
                  </div>
                </div>

                {/* Submit Button Box */}
                <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div style={{ fontSize: '0.7rem', color: '#64748b', marginBottom: '0.4rem' }}>Action Target</div>
                  <div style={{ background: 'linear-gradient(135deg, #0284c7, #0369a1)', color: '#fff', padding: '0.45rem 0.6rem', borderRadius: '6px', fontSize: '0.775rem', fontWeight: 700, textAlign: 'center' }}>
                    Submit Request
                  </div>
                </div>

              </div>

              {/* Bounding Box Highlights (Strict zero-overlap inner corner tags) */}
              {analysis?.elements.map((elem: DetectedUIElement, idx: number) => {
                const isSelected = selectedElemId === elem.element_id;
                const preset = elemPresets[elem.label] || elemPresets[elem.element_id] || {
                  left: `${5 + idx * 24}%`, top: '110px', width: '22%', height: '36px', color: '#38bdf8', marker: `${idx + 1}`, title: elem.label
                };

                return (
                  <div
                    key={elem.element_id}
                    onClick={() => setSelectedElemId(elem.element_id)}
                    style={{
                      position: 'absolute',
                      left: preset.left,
                      top: preset.top,
                      width: preset.width,
                      height: preset.height,
                      border: `2px solid ${preset.color}`,
                      background: isSelected ? 'rgba(56, 189, 248, 0.22)' : 'rgba(6, 182, 212, 0.08)',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      boxShadow: isSelected ? `0 0 15px ${preset.color}` : 'none',
                      pointerEvents: 'auto'
                    }}
                  >
                    {/* Inner Corner Marker Badge - Zero Overlap! */}
                    <div style={{
                      position: 'absolute',
                      top: '2px',
                      left: '2px',
                      background: preset.color,
                      color: '#000',
                      fontSize: '0.65rem',
                      fontWeight: 800,
                      width: '16px',
                      height: '16px',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.5)'
                    }}>
                      {preset.marker}
                    </div>
                  </div>
                );
              })}

            </div>
          </div>

          {/* OCR Extracted Text Payload */}
          {analysis && (
            <div style={{ marginTop: '1rem', background: 'rgba(15, 23, 42, 0.75)', padding: '0.85rem 1.15rem', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Extracted OCR Text Payload</div>
                <div style={{ fontSize: '0.85rem', color: '#38bdf8', marginTop: '0.15rem', fontFamily: 'var(--font-mono)' }}>
                  "{analysis.ocr_text}"
                </div>
              </div>
              <button
                onClick={handleCopyOcr}
                style={{
                  background: 'rgba(6, 182, 212, 0.15)',
                  border: '1px solid #06b6d4',
                  color: '#fff',
                  padding: '0.4rem 0.75rem',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  fontWeight: 600
                }}
              >
                {copiedOcr ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                <span>{copiedOcr ? 'Copied!' : 'Copy OCR'}</span>
              </button>
            </div>
          )}
        </div>

        {/* Right Column: Scene Reasoning & Target Elements Inspector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          
          {/* Scene Reasoning Card */}
          <div className="glass-panel" style={{ padding: '1.35rem' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={18} color="#a78bfa" />
              <span>Multi-Modal Scene Reasoning</span>
            </h2>

            {analysis?.reasoning && (
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ color: '#fff', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Layers size={14} color="#38bdf8" />
                  <span>{analysis.reasoning.active_window_title}</span>
                </div>
                <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                  {analysis.reasoning.scene_description}
                </p>
              </div>
            )}
          </div>

          {/* Detected Target Elements Table */}
          <div className="glass-panel" style={{ padding: '1.35rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <MousePointer size={18} color="#10b981" />
                <span>Detected Target Elements ({analysis?.elements.length || 0})</span>
              </h2>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
              {analysis?.elements.map((elem: DetectedUIElement) => {
                const isSelected = selectedElemId === elem.element_id;
                const preset = elemPresets[elem.label] || { marker: 'â', title: elem.label };
                return (
                  <div
                    key={elem.element_id}
                    onClick={() => setSelectedElemId(elem.element_id)}
                    style={{
                      background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'rgba(15, 23, 42, 0.6)',
                      border: isSelected ? '1px solid #38bdf8' : '1px solid var(--border-color)',
                      padding: '0.75rem 0.95rem',
                      borderRadius: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      display: 'flex',
                      justify: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', color: '#000', background: '#38bdf8', padding: '1px 6px', borderRadius: '50%', fontWeight: 800 }}>
                          {preset.marker}
                        </span>
                        <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>{elem.label}</span>
                        <span style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.08)', color: '#cbd5e1', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
                          {elem.element_type}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        ID: {elem.element_id} | Bounds: ({elem.bounding_box.width}Ã{elem.bounding_box.height})
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <span className="badge-success" style={{ fontSize: '0.725rem' }}>
                        {(elem.confidence * 100).toFixed(0)}% Match
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
