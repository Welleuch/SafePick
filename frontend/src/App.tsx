import { useState } from 'react';
import { JuniorDashboard, SeniorPortal } from './Portal';

function App() {
  const [page, setPage] = useState<'junior' | 'senior'>('junior');

  return (
    <div>
      <header className="header">
        <h1>PESE - Pre-Engineering Standardization Engine</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn" onClick={() => setPage('junior')} style={page === 'junior' ? { background: 'var(--accent-blue)', color: 'white' } : {}}>
            Junior
          </button>
          <button className="btn" onClick={() => setPage('senior')} style={page === 'senior' ? { background: 'var(--accent-blue)', color: 'white' } : {}}>
            Senior
          </button>
        </div>
      </header>

      {page === 'junior' ? <JuniorDashboard /> : <SeniorPortal />}
    </div>
  );
}

export default App;