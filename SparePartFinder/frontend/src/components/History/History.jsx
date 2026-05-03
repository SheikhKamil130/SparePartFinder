import React, { useState } from 'react';

const History = ({ history, onDeleteItem, onDeleteSelected, onDeleteAll }) => {
  const [selectedItems, setSelectedItems] = useState([]);

  const toggleSelection = (index) => {
    if (selectedItems.includes(index)) {
      setSelectedItems(selectedItems.filter(i => i !== index));
    } else {
      setSelectedItems([...selectedItems, index]);
    }
  };

  const handleDeleteSelected = () => {
    if (selectedItems.length === 0) {
      alert('Please select items to delete');
      return;
    }
    
    if (confirm(`Are you sure you want to delete ${selectedItems.length} selected scan(s)?`)) {
      onDeleteSelected(selectedItems);
      setSelectedItems([]);
    }
  };

  const handleDeleteSingle = (index, e) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this scan?')) {
      onDeleteItem(index);
      setSelectedItems(selectedItems.filter(i => i !== index));
    }
  };

  const clearSelection = () => {
    setSelectedItems([]);
  };

  return (
    <section>
      <div className="stat-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3>Audit Trail & Activity</h3>
          {history.length > 0 && (
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn-outline" onClick={clearSelection}>Clear Selection</button>
              <button className="btn-danger" onClick={handleDeleteSelected}>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '16px' }}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                Delete Selected
              </button>
            </div>
          )}
        </div>

        {history.length > 0 && (
          <div className="delete-bar show" style={{ marginBottom: '1rem' }}>
            <span style={{ fontWeight: '600', color: 'var(--text-muted)' }}>
              {selectedItems.length} item(s) selected
            </span>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn-danger" onClick={() => {
                if (confirm('Are you sure you want to delete ALL scan history? This action cannot be undone.')) {
                  onDeleteAll();
                  setSelectedItems([]);
                }
              }}>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '16px' }}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                Delete All
              </button>
            </div>
          </div>
        )}

        <div id="history-list">
          {history.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
              No recent scans detected.
            </p>
          ) : (
            history.map((item, index) => (
              <div
                key={index}
                className={`history-item ${selectedItems.includes(index) ? 'selected' : ''}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '1rem',
                  background: 'var(--bg)',
                  borderRadius: '10px',
                  border: '1px solid var(--border)',
                  marginBottom: '0.75rem',
                  transition: 'all 0.2s',
                  cursor: 'pointer'
                }}
                onClick={() => toggleSelection(index)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(index)}
                    onChange={() => toggleSelection(index)}
                    onClick={(e) => e.stopPropagation()}
                    style={{
                      width: '18px',
                      height: '18px',
                      cursor: 'pointer',
                      accentColor: 'var(--primary)'
                    }}
                  />
                  <img
                    src={item.image_url}
                    alt={item.part_name}
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '8px',
                      objectFit: 'cover'
                    }}
                  />
                  <div>
                    <div style={{ fontWeight: '700' }}>{item.part_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {item.timestamp}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div
                    style={{
                      background: 'var(--primary-bg)',
                      color: 'var(--primary)',
                      fontSize: '0.75rem',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '999px',
                      fontWeight: '600'
                    }}
                  >
                    {item.confidence}
                  </div>
                  <button
                    className="btn-icon"
                    onClick={(e) => handleDeleteSingle(index, e)}
                    title="Delete"
                    style={{
                      background: 'var(--card-bg)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      padding: '0.5rem',
                      cursor: 'pointer',
                      color: 'var(--text-muted)',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '18px' }}>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
};

export default History;
