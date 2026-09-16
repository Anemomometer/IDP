import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export function IngestSearch({ onSelectAbstract }) {
  const [query, setQuery] = useState('pembrolizumab melanoma clinical trial');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [ingestStats, setIngestStats] = useState(null);
  const [recentAbstracts, setRecentAbstracts] = useState([]);
  const [recentQueries, setRecentQueries] = useState([
    'pembrolizumab melanoma clinical trial',
    'nivolumab lung cancer OS PFS',
    'metformin type 2 diabetes cohort'
  ]);

  const fetchRecent = async () => {
    try {
      const data = await api.listAbstracts(12);
      setRecentAbstracts(data);
    } catch (err) {
      console.error('Failed to fetch recent abstracts:', err);
    }
  };

  useEffect(() => {
    fetchRecent();
  }, []);

  const handleIngest = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    setIngestStats(null);

    try {
      const result = await api.ingest(q, 10);
      setIngestStats(result);
      if (!recentQueries.includes(q)) {
        setRecentQueries([q, ...recentQueries.slice(0, 4)]);
      }
      await fetchRecent();
    } catch (err) {
      setError(err.message || 'Failed to fetch PubMed abstracts.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="screen-header">
        <div>
          <h1 className="screen-title">Screen 1: Ingest & Search PubMed</h1>
          <p className="screen-subtitle">
            Pull live clinical trial abstracts directly from NCBI E-utilities API and execute joint multi-task extraction.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-box">
          <span style={{ fontSize: '1.2rem' }}>⚠️</span>
          <div>
            <strong>Ingestion Error / Rate Limit:</strong>
            <div>{error}</div>
            <button
              className="btn btn-secondary"
              style={{ marginTop: '0.5rem', padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              onClick={() => handleIngest()}
            >
              🔄 Retry Fetch
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>NCBI E-utilities Live Query</h3>
        <div className="input-group">
          <input
            type="text"
            className="form-input"
            placeholder="e.g. pembrolizumab melanoma, nivolumab lung cancer..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleIngest()}
          />
          <button className="btn" disabled={loading} onClick={() => handleIngest()}>
            {loading ? '⏳ Fetching NCBI...' : '🚀 Fetch Abstracts'}
          </button>
        </div>

        {recentQueries.length > 0 && (
          <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Recent Queries:</span>
            {recentQueries.map((rq, idx) => (
              <button
                key={idx}
                className="btn btn-secondary"
                style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem' }}
                onClick={() => {
                  setQuery(rq);
                  handleIngest(rq);
                }}
              >
                {rq}
              </button>
            ))}
          </div>
        )}

        {ingestStats && (
          <div style={{ marginTop: '1.25rem', padding: '1rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--accent-teal)' }}>
            <div style={{ fontWeight: 700, color: 'var(--accent-teal)', marginBottom: '0.25rem' }}>
              ✓ Ingestion Complete for query: "{ingestStats.query}"
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              {ingestStats.message} ({ingestStats.total_fetched} total processed).
            </div>
          </div>
        )}
      </div>

      <h2 style={{ fontSize: '1.2rem', margin: '1.5rem 0 1rem', color: 'var(--text-primary)' }}>
        Processed Abstracts in Database ({recentAbstracts.length})
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '1.25rem' }}>
        {recentAbstracts.map((item) => (
          <div key={item.abstract_id} className="card" style={{ marginBottom: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <span className="badge badge-model">PMID: {item.abstract_id}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {item.retrieved_at ? new Date(item.retrieved_at).toLocaleDateString() : 'Recent'}
              </span>
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', lineHeight: 1.4 }}>
              {item.title}
            </h3>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              <span>🏷️ {item.entity_count} Entities</span>
              <span>🔗 {item.relation_count} Relations</span>
            </div>
            <button
              className="btn btn-secondary"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={() => onSelectAbstract(item.abstract_id)}
            >
              Inspect & Highlight Extractions →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
