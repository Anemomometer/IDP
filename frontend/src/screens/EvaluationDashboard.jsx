import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export function EvaluationDashboard() {
  const [activeTask, setActiveTask] = useState('NER'); // NER | RE | AD
  const [latestEval, setLatestEval] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchEval = async () => {
    setLoading(true);
    try {
      const data = await api.getEvaluationLatest();
      setLatestEval(data);
    } catch (err) {
      console.error('Failed to load evaluation data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEval();
  }, []);

  const handleRunEvaluation = async () => {
    setRunning(true);
    try {
      const data = await api.runEvaluation('ALL', 'v1.0-gold');
      setLatestEval(data);
    } catch (err) {
      alert(`Evaluation failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p>⏳ Loading evaluation metrics from gold-standard benchmark set...</p>
      </div>
    );
  }

  const metrics = latestEval?.metrics || {};
  const currentTaskMetrics = metrics[activeTask] || { per_class: {}, macro: {} };
  const macro = currentTaskMetrics.macro || { precision: 0, recall: 0, f1: 0 };
  const perClass = currentTaskMetrics.per_class || {};

  return (
    <div>
      <div className="screen-header">
        <div>
          <h1 className="screen-title">Step 6: AI Accuracy Report</h1>
          <p className="screen-subtitle">
            See how well the AI performs against a human-verified answer key.
          </p>
          <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--accent-teal)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            <strong>How it works:</strong> This page grades the AI. It compares the AI's answers against a 'Gold Standard' test set created by human doctors to tell you the exact accuracy (Precision and Recall) of the system.
          </div>
        </div>

        <button className="btn" disabled={running} onClick={handleRunEvaluation}>
          {running ? '⏳ Running Evaluation...' : '🔄 Execute Evaluation Run'}
        </button>
      </div>

      {latestEval && (
        <div style={{ marginBottom: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Run ID: #{latestEval.run_id} | Dataset: {latestEval.dataset_version} | Timestamp: {new Date(latestEval.run_timestamp).toLocaleString()}
        </div>
      )}

      <div className="nav-tabs" style={{ marginBottom: '1.5rem', width: 'fit-content' }}>
        <button className={`nav-btn ${activeTask === 'NER' ? 'active' : ''}`} onClick={() => setActiveTask('NER')}>
          1. Highlighted Terms (NER)
        </button>
        <button className={`nav-btn ${activeTask === 'RE' ? 'active' : ''}`} onClick={() => setActiveTask('RE')}>
          2. Medical Relationships (RE)
        </button>
        <button className={`nav-btn ${activeTask === 'AD' ? 'active' : ''}`} onClick={() => setActiveTask('AD')}>
          3. Fact Check / Modality (AD)
        </button>
      </div>

      {/* Summary Macro Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem', marginBottom: '1.5rem' }}>
        <div className="card" style={{ textAlign: 'center', margin: 0 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Macro Precision</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-teal)' }}>
            {(macro.precision * 100).toFixed(1)}%
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', margin: 0 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Macro Recall</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-teal)' }}>
            {(macro.recall * 100).toFixed(1)}%
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', margin: 0 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Macro F1 Score</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-teal)' }}>
            {(macro.f1 * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: activeTask === 'AD' ? '3fr 2fr' : '1fr', gap: '1.5rem' }}>
        {/* Per-Class Metrics Table */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <h3 style={{ padding: '1rem 1.25rem', fontSize: '1rem', borderBottom: '1px solid var(--border-color)' }}>
            Per-Class {activeTask} Performance Breakdown
          </h3>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Class / Label</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1 Score</th>
                  <th>True Positive (TP)</th>
                  <th>False Positive (FP)</th>
                  <th>False Negative (FN)</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(perClass).length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                      No evaluation metrics available for {activeTask}.
                    </td>
                  </tr>
                ) : (
                  Object.entries(perClass).map(([cls, val]) => (
                    <tr key={cls}>
                      <td><strong style={{ color: 'var(--text-primary)' }}>{cls}</strong></td>
                      <td>{(val.precision * 100).toFixed(1)}%</td>
                      <td>{(val.recall * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: 'var(--accent-teal)' }}>{(val.f1 * 100).toFixed(1)}%</td>
                      <td>{val.tp}</td>
                      <td>{val.fp}</td>
                      <td>{val.fn}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Confusion Matrix Visualization for Assertion Detection */}
        {activeTask === 'AD' && latestEval?.confusion_matrix && (
          <div className="card">
            <h3 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>Assertion Confusion Matrix</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Rows = True Gold Label, Columns = Model Prediction
            </p>

            <div className="matrix-grid">
              <div className="matrix-cell header">True \ Pred</div>
              <div className="matrix-cell header">PRESENT_POSITIVE</div>
              <div className="matrix-cell header">ABSENT_NEGATED</div>
              <div className="matrix-cell header">CONDITIONAL</div>

              {['PRESENT_POSITIVE', 'ABSENT_NEGATED', 'CONDITIONAL'].map((trueCls) => (
                <React.Fragment key={trueCls}>
                  <div className="matrix-cell header">{trueCls}</div>
                  {['PRESENT_POSITIVE', 'ABSENT_NEGATED', 'CONDITIONAL'].map((predCls) => (
                    <div key={predCls} className="matrix-cell val">
                      {latestEval.confusion_matrix[trueCls] ? latestEval.confusion_matrix[trueCls][predCls] || 0 : 0}
                    </div>
                  ))}
                </React.Fragment>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
