import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import StatsCard from './StatsCard';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = ({ history }) => {
  const [totalScans, setTotalScans] = useState(0);

  useEffect(() => {
    setTotalScans(history.length);
  }, [history]);

  const chartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Inference Success (%)',
      data: [85, 88, 82, 91, 89, 94, 92],
      borderColor: '#4f46e5',
      tension: 0.4,
      fill: true,
      backgroundColor: 'rgba(79, 70, 229, 0.05)'
    }]
  };

  const chartOptions = {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: false } }
  };

  return (
    <section>
      <div className="stats-grid">
        <StatsCard
          label="Model Precision"
          value="87.4%"
          trend="up"
          trendText="2.1% from last month"
        />
        <StatsCard
          label="Total Scans"
          value={totalScans}
          trendText="Lifetime activity"
        />
        <StatsCard
          label="Avg. Confidence"
          value="92.1%"
          trendText="Target: 95%"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div className="chart-container">
          <h4 style={{ marginBottom: '1.5rem' }}>System Identification Success Rate</h4>
          <Line data={chartData} options={chartOptions} height={250} />
        </div>
        <div
          className="stat-card"
          style={{
            boxShadow: 'none',
            borderStyle: 'dashed',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center'
          }}
        >
          <h3 style={{ marginBottom: '1rem' }}>Quick Scan</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
            Ready for industrial part recognition
          </p>
          <button
            className="btn btn-primary"
            onClick={() => window.location.href = '/analyzer'}
            style={{ width: 'auto', padding: '0.875rem 2rem' }}
          >
            Launch Analyzer
          </button>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;
