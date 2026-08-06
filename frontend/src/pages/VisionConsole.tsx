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
      setStatusMsg(`✓ Computer Vision Perception Engine: Segmented ${resp.data.elements.length} target elements across ${resp.data.segments.length} visual regions.`);
    } catch (err: any) {
      setStatusMsg(`❌ Vision analysis error: ${err.response?.data?.detail || err.message}`);
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

  // Clean, sleek radar coordinates layout for target elements
  const targetPresets: Record<string, { left: string; top: string; width: string; height: string; color: string; badge: string }> = {
    'System Status: Online': { left: '10%', top: '25%', width: '36%', height: '55px', color: '#10b981', badge: 'STATUS BADGE' },
    'Settings Cog Icon': { left: '54%', top: '25%', width: '36%', height: '55px', color: '#a78bfa', badge: 'SETTINGS ICON' },
    'User Email Input': { left: '10%', top: '55%', width: '36%', height: '55px', color: '#38bdf8', badge: 'EMAIL INPUT' },
    'Submit Request': { left: '54%', top: '55%', width: '36%', height: '55px', color: '#f59e0b', badge: 'SUBMIT BUTTON' },
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', paddingBottom: '2.5rem' }}>
      
      {/* Top Header */}
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
              Visual OCR, Precision GUI Element Target Detection & Perception Engine
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

      {/* Status Notification */}
      {statusMsg && (
        <div style={{ background: 'rgba(6, 182, 212, 0.12)', border: '1px solid rgba(6, 182, 212, 0.3)', color: '#67e8f9', padding: '0.85rem 1.25rem', borderRadius: '10px', marginBottom: '1.25rem', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={16} color="#38bdf8" />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* Goal Input & Trigger Bar */}
      <div className="glass-panel" style={{ padding: '1.15rem 1.35rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              value={taskGoal}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTaskGoal(e.target.value)}
              placeholder="Enter vision reasoning goal prompt..."
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

      {/* Grid Layout: High-Tech Radar Canvas + Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* Left Column: High-Tech Vision Radar Target Display */}
        <div className="glass-panel" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Box size={18} color="#38bdf8" />
              <span style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>Vision Target Perception Radar</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(15, 23, 42, 0.8)', padding: '0.25rem 0.65rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              Resolution: 1920 × 1080
            </span>
          </div>

          {/* High-Tech Radar Canvas Display */}
          <div style={{
            position: 'relative',
            width: '100%',
            height: '320px',
            background: 'radial-gradient(circle at 50% 50%, #0d1527 0%, #050811 100%)',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            overflow: 'hidden',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)'
          }}>
            {/* Window Header */}
            <div style={{
              height: '36px',
              background: '#0f172a',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              padding: '0 0.85rem',
              justifyContent: 'space-between'
            }}>
              <div style={{ display: 'flex', gap: '6px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#eab308' }} />
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#22c55e' }} />
              </div>
              <span style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>
                JARVIS Vision Target Detection Display
              </span>
              <span className="badge-success" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>● LIVE TARGET SCAN</span>
            </div>

            {/* Subtle High-Tech Blueprint Grid Lines */}
            <div style={{
              position: 'absolute',
              top: '36px',
              left: 0,
              right: 0,
              bottom: 0,
              backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
              backgroundSize: '40px 40px',
              pointerEvents: 'none'
            }} />

            {/* Target Detection Cards */}
            <div style={{ position: 'relative', height: 'calc(100% - 36px)', padding: '1rem' }}>
              {analysis?.elements.map((elem: DetectedUIElement, idx: number) => {
                const isSelected = selectedElemId === elem.element_id;
                const preset = targetPresets[elem.label] || {
                  left: `${10 + (idx % 2) * 44}%`,
                  top: `${25 + Math.floor(idx / 2) * 30}%`,
                  width: '38%',
                  height: '55px',
                  color: '#38bdf8',
                  badge: elem.element_type
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
                      background: isSelected ? 'rgba(56, 189, 248, 0.18)' : 'rgba(15, 23, 42, 0.75)',
                      border: isSelected ? `2px solid ${preset.color}` : '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '10px',
                      padding: '0.65rem 0.85rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: isSelected ? `0 0 20px ${preset.color}` : '0 4px 15px rgba(0,0,0,0.3)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '0.8rem', color: '#fff', fontWeight: 700 }}>{elem.label}</div>
                      <div style={{ fontSize: '0.675rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                        {elem.element_type} • ID: {elem.element_id}
                      </div>
                    </div>

                    <span style={{
                      fontSize: '0.65rem',
                      background: `${preset.color}25`,
                      color: preset.color,
                      border: `1px solid ${preset.color}50`,
                      padding: '0.2rem 0.5rem',
                      borderRadius: '5px',
                      fontWeight: 700
                    }}>
                      {(elem.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* OCR Extracted Text Box */}
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

        {/* Right Column: Multi-Modal Scene Reasoning & Target Elements Table */}
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
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>{elem.label}</span>
                        <span style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.08)', color: '#cbd5e1', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
                          {elem.element_type}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        ID: {elem.element_id} | Bounds: ({elem.bounding_box.width}×{elem.bounding_box.height})
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
