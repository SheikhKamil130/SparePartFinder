import React from 'react';

const StatsCard = ({ label, value, trend, trendText }) => {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {trend && (
        <div className={`stat-trend ${trend === 'up' ? 'trend-up' : ''}`}>
          {trend === 'up' && '↑ '}{trendText}
        </div>
      )}
    </div>
  );
};

export default StatsCard;
