import React, { useState } from 'react';
import { Header } from './components/Header';
import { IngestSearch } from './screens/IngestSearch';
import { AbstractDetail } from './screens/AbstractDetail';
import { RelationView } from './screens/RelationView';
import { EvidenceDatabase } from './screens/EvidenceDatabase';
import { ReviewQueue } from './screens/ReviewQueue';
import { EvaluationDashboard } from './screens/EvaluationDashboard';

export function App() {
  const [activeTab, setActiveTab] = useState('ingest'); // ingest | abstract | relation | database | review | eval
  const [selectedAbstractId, setSelectedAbstractId] = useState(null);

  const handleSelectAbstract = (abstractId) => {
    setSelectedAbstractId(abstractId);
    setActiveTab('abstract');
  };

  return (
    <div className="app-container">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'ingest' && (
          <IngestSearch onSelectAbstract={handleSelectAbstract} />
        )}

        {activeTab === 'abstract' && (
          <AbstractDetail abstractId={selectedAbstractId} />
        )}

        {activeTab === 'relation' && (
          <RelationView onJumpToAbstract={handleSelectAbstract} />
        )}

        {activeTab === 'database' && (
          <EvidenceDatabase />
        )}

        {activeTab === 'review' && (
          <ReviewQueue />
        )}

        {activeTab === 'eval' && (
          <EvaluationDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
