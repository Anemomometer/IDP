import React from 'react';

export function Header({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'ingest', label: '1. Ingest & Search', icon: '🔍' },
    { id: 'abstract', label: '2. Abstract Detail', icon: '📄' },
    { id: 'relation', label: '3. Relation View', icon: '🔗' },
    { id: 'database', label: '4. Evidence DB', icon: '📊' },
    { id: 'review', label: '5. Review Queue', icon: '✅' },
    { id: 'eval', label: '6. Evaluation', icon: '📈' },
  ];

  return (
    <header className="header">
      <div className="brand">
        <div className="brand-logo">CT</div>
        <div>
          <div className="brand-title">Clinical Trial NLP</div>
          <div className="brand-patent">US20250252261A1</div>
        </div>
      </div>

      <nav className="nav-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </header>
  );
}
