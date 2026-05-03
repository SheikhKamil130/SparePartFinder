import React from 'react';

const Results = ({ data, onCopy }) => {
  if (!data) return null;

  return (
    <div className="result-container" style={{ display: 'block' }}>
      <div className="result-card">
        <div className="result-banner">
          <div>
            <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: '600', opacity: '0.9' }}>
              Identified Object
            </p>
            <h2 style={{ fontSize: '2rem', fontWeight: '700', letterSpacing: '-0.025em' }}>
              {data.part_name}
            </h2>
          </div>
          <div className="part-id-badge">{data.confidence} Match</div>
        </div>
        <div className="result-body">
          <div className="section-header">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '18px' }}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Technical Specifications
          </div>
          <div className="specs-grid">
            {Object.entries(data.details).map(([key, value]) => (
              <div key={key} className="spec-item">
                <div className="spec-label">{key}</div>
                <div className="spec-value">{value}</div>
              </div>
            ))}
          </div>

          <div className="section-header">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '18px' }}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            Unified Market Comparison
          </div>
          <div className="price-list">
            {data.prices.map((price, index) => {
              const isInternal = price.retailer === 'Internal Inventory';
              return (
                <div key={index} className={`price-row ${isInternal ? 'internal' : ''}`}>
                  <div className="retailer-info">
                    <div className="retailer-logo">{price.name.charAt(0)}</div>
                    <div>
                      <div style={{ fontWeight: '700' }}>{price.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {isInternal ? 'Warehouse Location: In Stock' : 'Online Provider'}
                      </div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div className="price-val">${price.price}</div>
                    <span className={`availability-badge ${price.availability.includes('In') || price.availability.includes('available') ? 'badge-success' : 'badge-warning'}`}>
                      {price.availability}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <button className="btn btn-secondary" onClick={onCopy} style={{ marginTop: '2rem' }}>
            Export Identification Report (Copy)
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results;
