import React from 'react';

export function Legend() {
  return (
    <div className="legend-box">
      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
        LEGEND & ENCODING:
      </span>

      <div className="legend-item">
        <span className="entity-highlight entity-disease">
          🏷️ Disease
        </span>
      </div>

      <div className="legend-item">
        <span className="entity-highlight entity-drug">
          💊 Drug
        </span>
      </div>

      <div className="legend-item">
        <span className="entity-highlight entity-sample">
          👥 Sample Size
        </span>
      </div>

      <div className="legend-item">
        <span className="entity-highlight entity-endpoint">
          🎯 Endpoint
        </span>
      </div>

      <div style={{ height: '16px', width: '1px', background: 'var(--border-color)', margin: '0 4px' }} />

      <div className="legend-item">
        <span style={{ borderBottom: '2px solid var(--assertion-positive-color)', paddingBottom: '1px' }}>
          ✓ Positive (Solid)
        </span>
      </div>

      <div className="legend-item">
        <span style={{ textDecoration: 'line-through', textDecorationColor: 'var(--assertion-negated-color)' }}>
          ✗ Negated (Strikethrough)
        </span>
      </div>

      <div className="legend-item">
        <span style={{ borderBottom: '2px dashed var(--assertion-conditional-color)', paddingBottom: '1px' }}>
          ? Conditional (Dashed)
        </span>
      </div>

      <div style={{ height: '16px', width: '1px', background: 'var(--border-color)', margin: '0 4px' }} />

      <div className="legend-item">
        <span className="badge badge-model">AI Model</span>
        <span className="badge badge-rule">Rule Refined</span>
      </div>
    </div>
  );
}
