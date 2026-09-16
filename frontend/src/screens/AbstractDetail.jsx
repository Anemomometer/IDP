import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Legend } from '../components/Legend';

export function AbstractDetail({ abstractId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePopover, setActivePopover] = useState(null);
  const [reviewMsg, setReviewMsg] = useState(null);

  const loadData = async (id) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.getAbstractDetail(id);
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load abstract details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (abstractId) {
      loadData(abstractId);
    }
  }, [abstractId]);

  const handleReview = async (targetTable, targetId, status, correctedValue = null) => {
    try {
      await api.submitReview(targetTable, targetId, status, correctedValue);
      setReviewMsg(`Updated ${targetTable} #${targetId} to '${status}'.`);
      setActivePopover(null);
      await loadData(abstractId); // Refresh data
      setTimeout(() => setReviewMsg(null), 3000);
    } catch (err) {
      alert(`Review action failed: ${err.message}`);
    }
  };

  if (!abstractId) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h2>No Abstract Selected</h2>
        <p style={{ color: 'var(--text-muted)', margin: '1rem 0' }}>
          Please go to Screen 1 (Ingest & Search) and select an abstract to inspect.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p>⏳ Loading abstract extractions for PMID: {abstractId}...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-box">
        <strong>Error loading abstract:</strong> {error}
      </div>
    );
  }

  // Render character-accurate entity highlights over normalized text
  const renderHighlightedText = () => {
    if (!data || !data.normalized_text) return null;
    const text = data.normalized_text;
    const entities = [...(data.entities || [])].sort((a, b) => a.char_start - b.char_start);

    if (entities.length === 0) return text;

    const elements = [];
    let lastOffset = 0;

    entities.forEach((ent, idx) => {
      // Un-highlighted preceding text
      if (ent.char_start > lastOffset) {
        elements.push(text.substring(lastOffset, ent.char_start));
      }

      // Map entity type to CSS class
      let typeClass = 'entity-disease';
      if (ent.entity_type === 'Drug') typeClass = 'entity-drug';
      else if (ent.entity_type === 'Sample Size') typeClass = 'entity-sample';
      else if (ent.entity_type === 'Endpoint') typeClass = 'entity-endpoint';

      // Find relations & assertions linked to this entity
      const linkedRel = data.relations.find(
        (r) => r.subject_entity_id === ent.entity_id || r.object_entity_id === ent.entity_id
      );
      const linkedAssertion = linkedRel && linkedRel.assertions ? linkedRel.assertions[0] : null;

      let assertionClass = 'assertion-overlay-positive';
      if (linkedAssertion) {
        if (linkedAssertion.assertion_type === 'Negated') assertionClass = 'assertion-overlay-negated';
        else if (linkedAssertion.assertion_type === 'Conditional') assertionClass = 'assertion-overlay-conditional';
      }

      const isPopoverOpen = activePopover === ent.entity_id;

      elements.push(
        <span
          key={`ent-${ent.entity_id}-${idx}`}
          className={`entity-highlight ${typeClass} ${assertionClass}`}
          onClick={(e) => {
            e.stopPropagation();
            setActivePopover(isPopoverOpen ? null : ent.entity_id);
          }}
        >
          <span>{ent.text_span}</span>
          <span style={{ fontSize: '0.68rem', opacity: 0.85, fontWeight: 700 }}>
            ({ent.entity_type[0]})
          </span>

          {isPopoverOpen && (
            <div className="popover" onClick={(e) => e.stopPropagation()}>
              <div className="popover-header">
                <span>{ent.entity_type} Mention</span>
                <span className={`badge ${ent.extraction_method === 'model' ? 'badge-model' : 'badge-rule'}`}>
                  {ent.extraction_method}
                </span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Confidence Score: <strong style={{ color: 'var(--accent-teal)' }}>{(ent.confidence_score * 100).toFixed(1)}%</strong>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Status: {ent.review_status}
              </div>

              <div className="popover-actions">
                <button
                  className="popover-btn"
                  onClick={() => handleReview('entities', ent.entity_id, 'approved')}
                >
                  ✓ Approve
                </button>
                <button
                  className="popover-btn"
                  onClick={() => {
                    const newType = prompt('Enter corrected Entity Type (Disease, Drug, Sample Size, Endpoint):', ent.entity_type);
                    if (newType) handleReview('entities', ent.entity_id, 'corrected', newType);
                  }}
                >
                  ✏️ Correct
                </button>
                <button
                  className="popover-btn"
                  style={{ color: '#fca5a5' }}
                  onClick={() => handleReview('entities', ent.entity_id, 'rejected')}
                >
                  ✗ Reject
                </button>
              </div>
            </div>
          )}
        </span>
      );

      lastOffset = Math.max(lastOffset, ent.char_end);
    });

    if (lastOffset < text.length) {
      elements.push(text.substring(lastOffset));
    }

    return elements;
  };

  return (
    <div onClick={() => setActivePopover(null)}>
      <div className="screen-header">
        <div>
          <h1 className="screen-title">Screen 2: Abstract Detail & Inline Highlighting</h1>
          <p className="screen-subtitle">PMID: {data.abstract_id} — {data.title}</p>
        </div>
      </div>

      {reviewMsg && (
        <div style={{ padding: '0.75rem 1rem', background: 'var(--accent-teal-glow)', border: '1px solid var(--accent-teal)', color: 'var(--accent-teal)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
          ✓ {reviewMsg}
        </div>
      )}

      <Legend />

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        {/* Abstract Prose Card */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Annotated Abstract Text</h3>
          <div className="abstract-body">{renderHighlightedText()}</div>
        </div>

        {/* Sidebar Extractions List */}
        <div>
          <div className="card">
            <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Extracted Entities ({data.entities.length})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
              {data.entities.map((e) => (
                <div key={e.entity_id} style={{ padding: '0.5rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>{e.text_span}</strong>
                    <span className={`badge ${e.extraction_method === 'model' ? 'badge-model' : 'badge-rule'}`}>
                      {e.extraction_method}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>{e.entity_type}</span>
                    <span>Conf: {(e.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Extracted Relations ({data.relations.length})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
              {data.relations.map((r) => {
                const ass = r.assertions && r.assertions[0] ? r.assertions[0] : null;
                return (
                  <div key={r.relation_id} style={{ padding: '0.6rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
                    <div style={{ fontWeight: 600, color: 'var(--accent-teal)' }}>
                      {r.subject_entity ? r.subject_entity.text_span : 'Subj'} → {r.relation_type} → {r.object_entity ? r.object_entity.text_span : 'Obj'}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', fontSize: '0.75rem' }}>
                      <span style={{ color: ass?.assertion_type === 'Negated' ? '#ef4444' : ass?.assertion_type === 'Conditional' ? '#f59e0b' : '#10b981' }}>
                        Assertion: {ass ? ass.assertion_type : 'Positive'}
                      </span>
                      <span>{(r.confidence_score * 100).toFixed(0)}%</span>
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
}
