import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Eye, Camera, Layers, Box, Sparkles, Database, CheckCircle } from 'lucide-react';

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
  const [taskGoal, setTaskGoal] = useState<string>('Identify all buttons and input fields for form automation');
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleRunAnalysis = async () => {
    setIsLoading(true);
    try {
      const resp = await api.post<VisionAnalysisResponse>('/vision/analyze', {
        task_goal: taskGoal,
      });
      setAnalysis(resp.data);
      setStatusMsg(`✓ Computer Vision pipeline executed! Detected ${resp.data.elements.length} elements across ${resp.data.segments.length} regions.`);
    } catch (err: any) {
      setStatusMsg(`❌ Vision analysis error: ${err.response?.data?.detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleRunAnalysis();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Eye color="#06b6d4" />
            <span>Computer Vision Subsystem Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Screenshot Understanding, OCR, Object Detection, Button Recognition, Bounding Boxes, Screen Segmentation & Multi-Modal Reasoning.
          </p>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      {/* Goal Prompt & Trigger Form */}
      <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="text"
            value={taskGoal}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTaskGoal(e.target.value)}
            placeholder="Vision Reasoning Goal Prompt..."
            style={{ flex: 1, padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
          />
          <button onClick={handleRunAnalysis} disabled={isLoading} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.75rem 1.5rem' }}>
            <Camera size={16} />
            <span>Run Vision Analysis</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Screenshot Overlay Canvas */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Box size={18} color="#06b6d4" />
            <span>UI Element Bounding Box Canvas</span>
          </h2>

          <div style={{ position: 'relative', width: '100%', height: '320px', background: '#0f172a', borderRadius: '8px', border: '1px solid var(--border-color)', overflow: 'hidden' }}>
            {/* Mock Screenshot Content */}
            <div style={{ padding: '1.5rem' }}>
              <div style={{ color: '#fff', fontSize: '1.1rem', fontWeight: 700 }}>JARVIS Vision Perception Engine</div>
              <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: '0.5rem' }}>Active Window Desktop Preview</div>
            </div>

            {/* Render Bounding Boxes */}
            {analysis?.elements.map((elem: DetectedUIElement) => (
              <div
                key={elem.element_id}
                style={{
                  position: 'absolute',
                  left: `${(elem.bounding_box.x_min / 1920) * 100}%`,
                  top: `${(elem.bounding_box.y_min / 1080) * 100}%`,
                  width: `${(elem.bounding_box.width / 1920) * 100}%`,
                  height: `${(elem.bounding_box.height / 1080) * 100}%`,
                  border: elem.element_type === 'BUTTON' ? '2px solid #10b981' : '2px solid #06b6d4',
                  background: elem.element_type === 'BUTTON' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <span style={{ fontSize: '0.65rem', color: '#fff', fontWeight: 700, background: '#000', padding: '1px 4px', borderRadius: '3px' }}>
                  {elem.label}
                </span>
              </div>
            ))}
          </div>

          {analysis && (
            <div style={{ marginTop: '1rem', background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.85rem', color: '#38bdf8' }}>
              <strong>Extracted OCR Text:</strong> {analysis.ocr_text}
            </div>
          )}
        </div>

        {/* Visual Scene Reasoning & Detection Table */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="#a78bfa" />
            <span>Multi-Modal Scene Reasoning & Action Targets</span>
          </h2>

          {analysis?.reasoning && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1rem' }}>
              <div style={{ color: '#fff', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.4rem' }}>
                {analysis.reasoning.active_window_title}
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                {analysis.reasoning.scene_description}
              </p>
            </div>
          )}

          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem' }}>Detected Elements ({analysis?.elements.length || 0})</h3>
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '250px' }}>
            {analysis?.elements.map((elem: DetectedUIElement) => (
              <div key={elem.element_id} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.6rem 0.85rem', borderRadius: '6px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontSize: '0.8rem', color: '#fff', fontWeight: 600 }}>{elem.label}</span>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    Type: {elem.element_type} | Bounds: ({elem.bounding_box.x_min},{elem.bounding_box.y_min})
                  </div>
                </div>
                <span className="badge-success">{(elem.confidence * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
