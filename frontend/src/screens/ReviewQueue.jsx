import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export function ReviewQueue() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [bulkThresh, setBulkThresh] = useState(0.85);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const items = await api.getReviewQueue(50);
      setQueue(items);
    } catch (err) {
      console.error('Failed to load review queue:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleAction = async (relationId, status, correctedValue = null) => {
    try {
      await api.submitReview('relations', relationId, status, correctedValue);
      setReviewedCount((prev) => prev + 1);
      setQueue((prev) => prev.filter((item) => item.relation_id !== relationId));
    } catch (err) {
      alert(`Action failed: ${err.message}`);
    }
  };

  const handleBulkApprove = async () => {
    try {
      const res = await api.bulkApprove(bulkThresh);
      alert(res.message);
      fetchQueue();
    } catch (err) {
      alert(`Bulk approve failed: ${err.message}`);
    }
  };

  return (
    <div>
      <div className="screen-header">
        <div>
          <h1 className="screen-title">Step 5: Check the AI's Work</h1>
          <p className="screen-subtitle">
            Review facts that the AI isn't completely sure about.
          </p>
          <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--accent-teal)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            <strong>How it works:</strong> Sometimes the AI gets confused by complex sentences. This page shows the lowest-confidence guesses. You act as the human supervisor to Approve, Correct, or Reject the AI's work to keep the database accurate.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Session Progress: <strong style={{ color: 'var(--accent-teal)' }}>{reviewedCount}</strong> reviewed
          </span>
          <button className="btn" onClick={handleBulkApprove}>
            ⚡ Bulk Approve (&ge; {(bulkThresh * 100).toFixed(0)}%)
          </button>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p>⏳ Loading unreviewed extractions...</p>
        </div>
      ) : queue.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h2>🎉 Review Queue Empty!</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            All extracted evidence records have been reviewed or approved.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {queue.map((item) => (
            <div key={item.relation_id} className="card" style={{ margin: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div>
                  <span className="badge badge-model" style={{ marginRight: '8px' }}>PMID: {item.abstract_id}</span>
                  <strong style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>{item.abstract_title}</strong>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Confidence Score</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-teal)' }}>
                    {(item.confidence_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Text Snippet Context */}
              <div style={{ background: 'var(--bg-primary)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.88rem', color: '#cbd5e1', marginBottom: '1rem' }}>
                "...{item.raw_text_snippet}..."
              </div>

              {/* Relation Extraction Card Details */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span className="entity-highlight entity-DRUG">{item.subject_text}</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-teal)' }}>→ {item.relation_type} →</span>
                  <span className="entity-highlight entity-DISEASE">{item.object_text}</span>
                  <span className="badge badge-rule" style={{ marginLeft: '6px' }}>
                    Assertion: {item.assertion_type}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="btn"
                    style={{ padding: '0.4rem 0.85rem', fontSize: '0.82rem' }}
                    onClick={() => handleAction(item.relation_id, 'approved')}
                  >
                    ✓ Approve
                  </button>
                  <button
                    className="btn btn-secondary"
                    style={{ padding: '0.4rem 0.85rem', fontSize: '0.82rem' }}
                    onClick={() => {
                      const newType = prompt('Enter corrected Relation Type (TREATS, TESTED_IN, MEASURED_BY):', item.relation_type);
                      if (newType) handleAction(item.relation_id, 'corrected', newType);
                    }}
                  >
                    ✏️ Correct
                  </button>
                  <button
                    className="btn btn-danger"
                    style={{ padding: '0.4rem 0.85rem', fontSize: '0.82rem' }}
                    onClick={() => handleAction(item.relation_id, 'rejected')}
                  >
                    ✗ Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
