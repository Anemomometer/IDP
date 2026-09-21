import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export function EvidenceDatabase() {
  const [filters, setFilters] = useState({
    drug: '',
    disease: '',
    relation_type: '',
    assertion_type: '',
    min_confidence: 0.0,
    review_status: '',
  });

  const [page, setPage] = useState(1);
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);

  const fetchEvidence = async () => {
    setLoading(true);
    try {
      const params = { ...filters, page, page_size: 15 };
      Object.keys(params).forEach((key) => {
        if (!params[key] && params[key] !== 0) delete params[key];
      });
      const res = await api.search(params);
      setData(res);
    } catch (err) {
      console.error('Failed to search evidence database:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [filters, page]);

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
    setPage(1); // Reset page on filter change
  };

  const removeFilter = (key) => {
    handleFilterChange(key, key === 'min_confidence' ? 0.0 : '');
  };

  const activeChips = Object.entries(filters).filter(([k, v]) => {
    if (k === 'min_confidence') return v > 0;
    return Boolean(v);
  });

  const handleExport = (format) => {
    const url = api.exportUrl(filters, format);
    window.open(url, '_blank');
  };

  return (
    <div>
      <div className="screen-header">
        <div>
          <h1 className="screen-title">Step 4: Search All Extracted Data</h1>
          <p className="screen-subtitle">
            Filter and search through all the medical facts the AI has ever found.
          </p>
          <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--accent-teal)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            <strong>How it works:</strong> Use this page like a search engine for medical facts. You can filter by a specific drug to see every disease it was tested against in our database.
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn" onClick={() => handleExport('csv')}>
            📥 Export CSV
          </button>
          <button className="btn btn-secondary" onClick={() => handleExport('json')}>
            📥 Export JSON
          </button>
        </div>
      </div>

      {/* Filter Panel Card */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Multi-Filter Panel (AND Logic)</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Drug Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. pembrolizumab..."
              value={filters.drug}
              onChange={(e) => handleFilterChange('drug', e.target.value)}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Disease Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. melanoma..."
              value={filters.disease}
              onChange={(e) => handleFilterChange('disease', e.target.value)}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Relation Type</label>
            <select
              className="form-input"
              value={filters.relation_type}
              onChange={(e) => handleFilterChange('relation_type', e.target.value)}
            >
              <option value="">All Relation Types</option>
              <option value="TREATS">TREATS</option>
              <option value="TESTED_IN">TESTED_IN</option>
              <option value="MEASURED_BY">MEASURED_BY</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Assertion Status</label>
            <select
              className="form-input"
              value={filters.assertion_type}
              onChange={(e) => handleFilterChange('assertion_type', e.target.value)}
            >
              <option value="">All Assertions</option>
              <option value="PRESENT_POSITIVE">PRESENT_POSITIVE</option>
              <option value="ABSENT_NEGATED">ABSENT_NEGATED</option>
              <option value="CONDITIONAL">CONDITIONAL</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
              Min Confidence: {(filters.min_confidence * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="0.95"
              step="0.05"
              value={filters.min_confidence}
              onChange={(e) => handleFilterChange('min_confidence', parseFloat(e.target.value))}
              style={{ width: '100%', marginTop: '8px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Review Status</label>
            <select
              className="form-input"
              value={filters.review_status}
              onChange={(e) => handleFilterChange('review_status', e.target.value)}
            >
              <option value="">All Review Statuses</option>
              <option value="unreviewed">Unreviewed</option>
              <option value="approved">Approved</option>
              <option value="corrected">Corrected</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        {/* Active Filter Chips */}
        {activeChips.length > 0 && (
          <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Active Filters:</span>
            {activeChips.map(([k, v]) => (
              <span
                key={k}
                style={{
                  background: 'var(--accent-teal-glow)',
                  border: '1px solid var(--accent-teal)',
                  color: 'var(--accent-teal)',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.78rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span>{k}: {k === 'min_confidence' ? `${(v * 100).toFixed(0)}%` : v}</span>
                <span style={{ cursor: 'pointer', fontWeight: 700 }} onClick={() => removeFilter(k)}>✕</span>
              </span>
            ))}
            <button
              className="btn btn-secondary"
              style={{ padding: '2px 8px', fontSize: '0.75rem' }}
              onClick={() =>
                setFilters({ drug: '', disease: '', relation_type: '', assertion_type: '', min_confidence: 0.0, review_status: '' })
              }
            >
              Clear All
            </button>
          </div>
        )}
      </div>

      {/* Results Count Summary */}
      <div style={{ margin: '1rem 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Showing <strong>{data.items.length}</strong> of <strong>{data.total}</strong> matching evidence records
      </div>

      {/* Results Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Subject Entity</th>
                <th>Relation Type</th>
                <th>Object Entity</th>
                <th>Assertion Status</th>
                <th>Confidence</th>
                <th>Method</th>
                <th>Review Status</th>
                <th>PMID</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem' }}>⏳ Searching evidence database...</td>
                </tr>
              ) : data.items.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No evidence records matched your active filter criteria. Try loosening filters.
                  </td>
                </tr>
              ) : (
                data.items.map((item) => (
                  <tr key={item.relation_id}>
                    <td>#{item.relation_id}</td>
                    <td>
                      <strong style={{ color: 'var(--entity-drug-text)' }}>{item.subject_text}</strong>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{item.subject_type}</div>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>{item.relation_type}</td>
                    <td>
                      <strong style={{ color: 'var(--entity-disease-text)' }}>{item.object_text}</strong>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{item.object_type}</div>
                    </td>
                    <td>
                      <span
                        style={{
                          color:
                            item.assertion_type === 'ABSENT_NEGATED'
                              ? '#ef4444'
                              : item.assertion_type === 'CONDITIONAL'
                              ? '#f59e0b'
                              : '#10b981',
                          fontWeight: 600,
                        }}
                      >
                        {item.assertion_type}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>{(item.confidence_score * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`badge ${item.extraction_method === 'model' ? 'badge-model' : 'badge-rule'}`}>
                        {item.extraction_method}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.78rem', textTransform: 'capitalize' }}>{item.review_status}</span>
                    </td>
                    <td>{item.abstract_id}</td>
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
