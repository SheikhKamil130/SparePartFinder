import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import StatsCard from '../Dashboard/StatsCard';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Analytics = () => {
  const chartData = {
    labels: ['Alternator', 'Battery', 'Brake Pad', 'Radiator', 'Starter', 'Muffler'],
    datasets: [
      {
        label: 'Correct Hits',
        data: [95, 91, 98, 88, 85, 92],
        backgroundColor: '#4f46e5'
      },
      {
        label: 'False Positives',
        data: [5, 9, 2, 12, 15, 8],
        backgroundColor: '#e2e8f0'
      }
    ]
  };

  const chartOptions = {
    indexAxis: 'y',
    plugins: {
      legend: { position: 'bottom' }
    },
    scales: {
      x: { stacked: true },
      y: { stacked: true }
    }
  };

  return (
    <section>
      <div className="stats-grid">
        <StatsCard
          label="Model Precision"
          value="87.4%"
        />
        <StatsCard
          label="Recall Rate"
          value="80.8%"
        />
        <StatsCard
          label="F1 Score"
          value="80.1%"
        />
      </div>
      <div className="chart-container">
        <h4 style={{ marginBottom: '1.5rem' }}>Confusion Matrix Distribution (Simplified)</h4>
        <Bar data={chartData} options={chartOptions} height={150} />
      </div>
    </section>
  );
};

export default Analytics;
