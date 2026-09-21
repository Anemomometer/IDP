import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export function RelationView({ onJumpToAbstract }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [relFilter, setRelFilter] = useState('');
  const [assFilter, setAssFilter] = useState('');
  const [minConf, setMinConf] = useState(0.0);

  const loadRelations = async () => {
    setLoading(true);
    try {
      const params = {};
      if (relFilter) params.relation_type = relFilter;
      if (assFilter) params.assertion_type = assFilter;
      if (minConf > 0) params.min_confidence = minConf;
      params.page_size = 50;

      const res = await api.search(params);
      setItems(res.items || []);
    } catch (err) {
      console.error('Failed to load relations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRelations();
  }, [relFilter, assFilter, minConf]);

  return (
    <div>
      <div className="screen-header">
        <div>
          <h1 className="screen-title">Step 3: Medical Links (Relationships)</h1>
          <p className="screen-subtitle">
            A quick summary of how drugs, diseases, and outcomes are connected across the papers.
          </p>
          <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--accent-teal)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            <strong>How it works:</strong> Instead of reading full paragraphs, you can look at this table. It shows the direct medical relationships the AI found. For example, it shows if a Drug TREATS a Disease, or if it was NEGATED (meaning it didn't work).
          </div>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="card" style={{ padding: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Quick Filters:</span>

          <select
            className="form-input"
            style={{ width: 'auto', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            value={relFilter}
            onChange={(e) => setRelFilter(e.target.value)}
          >
            <option value="">All Relation Types</option>
            <option value="TREATS">TREATS</option>
            <option value="TESTED_IN">TESTED_IN</option>
            <option value="MEASURED_BY">MEASURED_BY</option>
          </select>

          <select
            className="form-input"
            style={{ width: 'auto', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            value={assFilter}
            onChange={(e) => setAssFilter(e.target.value)}
          >
            <option value="">All Assertions</option>
            <option value="PRESENT_POSITIVE">PRESENT_POSITIVE</option>
            <option value="ABSENT_NEGATED">ABSENT_NEGATED</option>
            <option value="CONDITIONAL">CONDITIONAL</option>
          </select>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <span>Min Confidence: {(minConf * 100).toFixed(0)}%</span>
            <input
              type="range"
              min="0"
              max="0.95"
              step="0.05"
              value={minConf}
              onChange={(e) => setMinConf(parseFloat(e.target.value))}
            />
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Subject Entity</th>
                <th>Relation Type</th>
                <th>Object Entity</th>
                <th>Assertion Status</th>
                <th>Confidence</th>
                <th>Method</th>
                <th>Source Abstract</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>⏳ Loading relations...</td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No extracted relations match your filters.
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr
                    key={item.relation_id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => onJumpToAbstract(item.abstract_id)}
                  >
                    <td>
                      <strong style={{ color: 'var(--entity-drug-text)' }}>{item.subject_text}</strong>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{item.subject_type}</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>{item.relation_type}</span>
                    </td>
                    <td>
                      <strong style={{ color: 'var(--entity-disease-text)' }}>{item.object_text}</strong>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{item.object_type}</div>
                    </td>
                    <td>
                      <span
                        style={{
                          fontWeight: 600,
                          color:
                            item.assertion_type === 'ABSENT_NEGATED'
                              ? '#ef4444'
                              : item.assertion_type === 'CONDITIONAL'
                              ? '#f59e0b'
                              : '#10b981',
                        }}
                      >
                        {item.assertion_type === 'ABSENT_NEGATED' ? '✗ ' : item.assertion_type === 'CONDITIONAL' ? '? ' : '✓ '}
                        {item.assertion_type}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>
                      {(item.confidence_score * 100).toFixed(1)}%
                    </td>
                    <td>
                      <span className={`badge ${item.extraction_method === 'model' ? 'badge-model' : 'badge-rule'}`}>
                        {item.extraction_method}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontSize: '0.82rem', fontWeight: 500 }}>PMID: {item.abstract_id}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '200px' }}>
                        {item.abstract_title}
                      </div>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onJumpToAbstract(item.abstract_id);
                        }}
                      >
                        Inspect Span →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
