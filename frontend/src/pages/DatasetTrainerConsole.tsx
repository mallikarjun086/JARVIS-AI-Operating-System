import React, { useState } from 'react';
import { api } from '../services/api';
import { Database, Sparkles, Download, Cpu, CheckCircle2, FileText } from 'lucide-react';

interface FewShotSample {
  id: string;
  prompt: string;
  completion: string;
  formatted_pair: string;
}

export const DatasetTrainerConsolePage: React.FC = () => {
  const [ingestText, setIngestText] = useState<string>('');
  const [category, setCategory] = useState<string>('LONG_TERM_EPISODIC');
  const [importance, setImportance] = useState<number>(0.9);
  const [ingestStatus, setIngestStatus] = useState<string>('');
  const [isIngesting, setIsIngesting] = useState<boolean>(false);

  const [topic, setTopic] = useState<string>('JARVIS Swarm Mesh Architecture');
  const [sampleCount, setSampleCount] = useState<number>(5);
  const [fewshots, setFewshots] = useState<FewShotSample[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportMsg, setExportMsg] = useState<string>('');

  const handleIngestDataset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestText.trim()) return;

    setIsIngesting(true);
    setIngestStatus('');

    try {
      // Split text into paragraphs or JSON items
      let items: any[] = [];
      if (ingestText.trim().startsWith('[') || ingestText.trim().startsWith('{')) {
        try {
          const parsed = JSON.parse(ingestText);
          items = Array.isArray(parsed) ? parsed : [parsed];
        } catch {
          items = [{ content: ingestText }];
        }
      } else {
        const paragraphs = ingestText.split('\n\n').filter((p) => p.trim().length > 10);
        items = paragraphs.map((p, idx) => ({
          title: `Ingested Document Chunk #${idx + 1}`,
          content: p.trim(),
        }));
      }

      const res = await api.post('/memory/train-dataset', {
        items,
        category,
        importance_score: Number(importance),
      });

      setIngestStatus(`✓ ${res.data.message || 'Dataset batch successfully trained into vector store.'}`);
      setIngestText('');
    } catch (err: any) {
      setIngestStatus(`❌ Ingestion Error: ${err.response?.data?.detail || 'Failed to ingest dataset.'}`);
    } finally {
      setIsIngesting(false);
    }
  };

  const handleGenerateFewShot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsGenerating(true);
    try {
      const res = await api.post('/memory/generate-fewshot', {
        topic,
        count: Number(sampleCount),
      });

      if (res.data.samples) {
        setFewshots(res.data.samples);
      }
    } catch (err: any) {
      alert(`Few-Shot Generation Error: ${err.response?.data?.detail || 'Failed to generate few-shots.'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportJSONL = async () => {
    setIsExporting(true);
    setExportMsg('');

    try {
      const res = await api.get('/memory/export-fine-tune?limit=50');
      const content = res.data.jsonl_content || '';
      const filename = res.data.filename || 'jarvis_finetune_dataset.jsonl';

      const blob = new Blob([content], { type: 'application/x-jsonlines' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setExportMsg(`✓ Downloaded ${res.data.total_records || 0} fine-tuning records as ${filename}`);
    } catch (err: any) {
      setExportMsg(`❌ Export Error: ${err.response?.data?.detail || 'Failed to export fine-tuning JSONL.'}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Cpu size={26} color="#00f2fe" /> Dataset Training & Knowledge Synthesizer
          </h1>
          <p className="page-subtitle">
            Ingest raw documents into vector memory, generate synthetic few-shot QA prompt pairs, and export JSONL fine-tuning datasets.
          </p>
        </div>
        <button onClick={handleExportJSONL} disabled={isExporting} className="btn-primary" style={{ background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)' }}>
          <Download size={16} /> {isExporting ? 'Exporting...' : 'Export Fine-Tuning JSONL'}
        </button>
      </div>

      {exportMsg && <div className="alert-banner info">{exportMsg}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Ingest Dataset Batch */}
        <div className="panel">
          <div className="panel-header">
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Database size={18} color="#00f2fe" /> Train & Ingest Dataset Batch
            </h2>
          </div>

          <form onSubmit={handleIngestDataset} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.3rem', display: 'block' }}>
                Memory Category
              </label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="input-field">
                <option value="LONG_TERM_EPISODIC">LONG_TERM_EPISODIC (Episodic Knowledge)</option>
                <option value="SEMANTIC_FACT">SEMANTIC_FACT (Factual Knowledge)</option>
                <option value="PROJECT_SPECIFIC">PROJECT_SPECIFIC (Project Docs)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.3rem', display: 'block' }}>
                Importance Weight (0.0 to 1.0)
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="1.0"
                value={importance}
                onChange={(e) => setImportance(Number(e.target.value))}
                className="input-field"
              />
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.3rem', display: 'block' }}>
                Dataset Text or JSON Array
              </label>
              <textarea
                value={ingestText}
                onChange={(e) => setIngestText(e.target.value)}
                placeholder="Paste raw documentation text, articles, or JSON array format..."
                rows={7}
                className="input-field"
                style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
                required
              />
            </div>

            {ingestStatus && <div className={`alert-banner ${ingestStatus.startsWith('✓') ? 'success' : 'error'}`}>{ingestStatus}</div>}

            <button type="submit" disabled={isIngesting} className="btn-primary">
              <CheckCircle2 size={16} /> {isIngesting ? 'Computing Embeddings & Ingesting...' : 'Train Dataset Batch into Vector Store'}
            </button>
          </form>
        </div>

        {/* Generate Synthetic Few-Shot Prompt Pairs */}
        <div className="panel">
          <div className="panel-header">
            <h2 className="panel-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={18} color="#a855f7" /> Synthetic Few-Shot QA Generator
            </h2>
          </div>

          <form onSubmit={handleGenerateFewShot} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.3rem', display: 'block' }}>
                Target Topic / Subsystem
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Swarm Mesh Architecture, Tool Execution Safety..."
                className="input-field"
                required
              />
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '0.3rem', display: 'block' }}>
                Sample Pair Count (1-20)
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={sampleCount}
                onChange={(e) => setSampleCount(Number(e.target.value))}
                className="input-field"
              />
            </div>

            <button type="submit" disabled={isGenerating} className="btn-primary" style={{ background: 'linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)' }}>
              <Sparkles size={16} /> {isGenerating ? 'Synthesizing Prompt Pairs...' : 'Synthesize Synthetic Few-Shot QA Dataset'}
            </button>
          </form>

          {fewshots.length > 0 && (
            <div style={{ marginTop: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-dim)' }}>Synthesized Few-Shot Pairs ({fewshots.length}):</div>
              <div style={{ maxHeight: '250px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {fewshots.map((item) => (
                  <div key={item.id} style={{ background: 'var(--bg-card)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                    <div style={{ color: '#38bdf8', fontWeight: 600, marginBottom: '0.2rem' }}>Q: {item.prompt}</div>
                    <div style={{ color: '#f8fafc' }}>A: {item.completion}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
