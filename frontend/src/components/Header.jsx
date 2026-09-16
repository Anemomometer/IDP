import React from 'react';
import { Network } from 'lucide-react';

export function Header({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'ingest', label: 'Ingest & Search', icon: '🔍' },
    { id: 'abstract', label: 'Abstract Detail', icon: '📄' },
    { id: 'relation', label: 'Relation View', icon: '🔗' },
    { id: 'database', label: 'Evidence DB', icon: '📊' },
    { id: 'review', label: 'Review Queue', icon: '✅' },
    { id: 'eval', label: 'Evaluation', icon: '📈' },
  ];

  return (
    <header className="header">
      <div className="brand">
        <div className="brand-logo">
          <Network size={22} strokeWidth={2.5} />
        </div>
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
            <span style={{ fontSize: '1rem', opacity: activeTab === tab.id ? 1 : 0.6 }}>
              {tab.icon}
            </span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </header>
  );
}
