import React from 'react';
import { Network } from 'lucide-react';

export function Header({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'ingest', label: '1. Find Papers', icon: '🔍' },
    { id: 'abstract', label: '2. View AI Highlights', icon: '📄' },
    { id: 'relation', label: '3. Medical Links', icon: '🔗' },
    { id: 'database', label: '4. Data Search', icon: '📊' },
    { id: 'review', label: "5. Check AI's Work", icon: '✅' },
    { id: 'eval', label: '6. AI Accuracy', icon: '📈' },
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
