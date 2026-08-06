import React, { useState } from 'react';
import { api } from '../services/api';
import { Brain, Database, Layers, Search, Trash2 } from 'lucide-react';

interface MemoryEntry {
  id: string;
  category: string;
  content: string;
  importance_score: number;
  access_count: number;
  created_at: string;
  expires_at?: string;
}

interface MemorySearchResult {
  entry: MemoryEntry;
  vector_similarity: number;
  importance_score: number;
  recency_score: number;
  access_frequency_score: number;
  ranked_score: number;
}

export const MemoryConsolePage: React.FC = () => {
  const [content, setContent] = useState<string>('');
  const [category, setCategory] = useState<string>('LONG_TERM_EPISODIC');
  const [importance, setImportance] = useState<number>(0.8);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<MemorySearchResult[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string>('');

  const handleCreateMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    setStatusMsg('');

    try {
      await api.post('/memory', {
        content,
        category,
        importance_score: Number(importance),
      });
      setContent('');
      setStatusMsg('✓ Memory record indexed in vector store & SQLite metadata.');
    } catch (err: any) {
      setStatusMsg(`❌ Error: ${err.response?.data?.detail || 'Memory creation failed.'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const resp = await api.post<MemorySearchResult[]>('/memory/query', {
        query: searchQuery,
        top_k: 5,
      });
      setSearchResults(resp.data);
    } catch (err: any) {
      console.error('Memory search failed', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCompress = async () => {
    setIsSubmitting(true);
    try {
      await api.post('/memory/compress', {
        conversation_turns: [
          'User: How do we achieve Clean Architecture in AI OS?',
          'Assistant: Separate Domain Entities, Application Use Cases, and Infrastructure Adapters.',
        ],
        importance_score: 0.9,
      });
      setStatusMsg('✓ Conversation turns compressed into long-term semantic memory.');
    } catch (err: any) {
      setStatusMsg(`❌ Error compressing memory: ${err.response?.data?.detail}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCleanup = async () => {
    try {
      const resp = await api.post<{ message: string }>('/memory/cleanup');
      setStatusMsg(`✓ ${resp.data.message}`);
    } catch (err: any) {
      setStatusMsg(`❌ Cleanup error: ${err.response?.data?.detail}`);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Brain color="#38bdf8" />
            <span>Long-Term Memory Subsystem Console</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Multi-Tier Memory (Short-Term, Conversation, Long-Term Episodic, Semantic) with Multi-Factor Ranking.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button onClick={handleCompress} disabled={isSubmitting} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'linear-gradient(135deg, #8b5cf6, #ec4899)' }}>
            <Layers size={16} />
            <span>Compress Turns</span>
          </button>
          <button onClick={handleCleanup} className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#fca5a5' }}>
            <Trash2 size={16} />
            <span>TTL Cleanup</span>
          </button>
        </div>
      </div>

      {statusMsg && (
        <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#7dd3fc', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
          {statusMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Memory Creation Form */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={18} color="#06b6d4" />
            <span>Store New Memory Record</span>
          </h2>

          <form onSubmit={handleCreateMemory} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Memory Category</label>
              <select
                value={category}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setCategory(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
              >
                <option value="SHORT_TERM">SHORT_TERM (Transient Working Buffer)</option>
                <option value="CONVERSATION">CONVERSATION (Session Turn History)</option>
                <option value="LONG_TERM_EPISODIC">LONG_TERM_EPISODIC (Event History)</option>
                <option value="SEMANTIC">SEMANTIC (Persistent Factual Knowledge)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Importance Weight (0.0 to 1.0)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={importance}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setImportance(Number(e.target.value))}
                style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Memory Content Text</label>
              <textarea
                rows={4}
                required
                value={content}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setContent(e.target.value)}
                placeholder="Enter facts, observations, or event records to store in long-term vector & SQLite memory..."
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff', fontFamily: 'inherit' }}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Indexing...' : 'Index Memory Record'}
            </button>
          </form>
        </div>

        {/* Semantic Search & Multi-Factor Ranking */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Search size={18} color="#a78bfa" />
            <span>Ranked Semantic Retrieval</span>
          </h2>

          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
              placeholder="Search query for vector similarity..."
              style={{ flex: 1, padding: '0.6rem 0.85rem', borderRadius: '6px', background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--border-color)', color: '#fff' }}
            />
            <button type="submit" className="btn-primary" disabled={isSearching}>
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </form>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {searchResults.map((res: MemorySearchResult, idx: number) => (
              <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span className="badge-success">{res.entry.category}</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#38bdf8' }}>Rank Score: {res.ranked_score}</span>
                </div>
                <div style={{ fontSize: '0.9rem', color: '#fff', marginBottom: '0.5rem' }}>{res.entry.content}</div>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <span>Similarity: {res.vector_similarity}</span>
                  <span>Importance: {res.importance_score}</span>
                  <span>Recency: {res.recency_score}</span>
                </div>
              </div>
            ))}
            {searchResults.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem', fontSize: '0.85rem' }}>
                Enter a query string above to perform semantic vector search and multi-factor ranking.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
