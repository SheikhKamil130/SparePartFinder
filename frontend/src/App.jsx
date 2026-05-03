import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useLocalStorage } from './hooks/useLocalStorage';
import { addToHistory, deleteHistoryItem, deleteMultipleHistoryItems } from './utils/storage';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './components/Dashboard/Dashboard';
import Analyzer from './components/Analyzer/Analyzer';
import History from './components/History/History';
import Analytics from './components/Analytics/Analytics';
import SplashScreen from './components/SplashScreen';
import './App.css';

function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  const [history, setHistory] = useLocalStorage('pro_history', []);
  const [currentView, setCurrentView] = useState('dashboard');
  const [showSplash, setShowSplash] = useState(true);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const handleAddToHistory = (newEntry) => {
    const updatedHistory = addToHistory(history, newEntry);
    setHistory(updatedHistory);
  };

  const handleDeleteItem = (index) => {
    const updatedHistory = deleteHistoryItem(history, index);
    setHistory(updatedHistory);
  };

  const handleDeleteSelected = (indexes) => {
    const updatedHistory = deleteMultipleHistoryItems(history, indexes);
    setHistory(updatedHistory);
  };

  const handleDeleteAll = () => {
    setHistory([]);
  };

  const handleSplashComplete = () => {
    setShowSplash(false);
  };

  if (showSplash) {
    return <SplashScreen onLoadComplete={handleSplashComplete} />;
  }

  return (
    <Router>
      <div id="root">
        <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
        <div className="main-content">
          <Header theme={theme} setTheme={setTheme} currentView={currentView} />
          <div className="content-area">
            <Routes>
              <Route path="/" element={<Dashboard history={history} />} />
              <Route
                path="/analyzer"
                element={<Analyzer onAddToHistory={handleAddToHistory} />}
              />
              <Route
                path="/history"
                element={
                  <History
                    history={history}
                    onDeleteItem={handleDeleteItem}
                    onDeleteSelected={handleDeleteSelected}
                    onDeleteAll={handleDeleteAll}
                  />
                }
              />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
