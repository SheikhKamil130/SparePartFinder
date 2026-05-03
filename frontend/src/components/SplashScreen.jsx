import React, { useState, useEffect } from 'react';

const SplashScreen = ({ onLoadComplete }) => {
  const [visible, setVisible] = useState(true);
  const [status, setStatus] = useState('Initializing system...');

  useEffect(() => {
    const loadingSteps = [
      'Initializing system...',
      'Loading AI models...',
      'Preparing interface...',
      'Almost ready...'
    ];

    let currentStep = 0;
    const loadingInterval = setInterval(() => {
      if (currentStep < loadingSteps.length) {
        setStatus(loadingSteps[currentStep]);
        currentStep++;
      }
    }, 500);

    const timer = setTimeout(() => {
      clearInterval(loadingInterval);
      setVisible(false);
      setTimeout(() => {
        onLoadComplete();
      }, 500);
    }, 2000);

    return () => {
      clearTimeout(timer);
      clearInterval(loadingInterval);
    };
  }, [onLoadComplete]);

  if (!visible) return null;

  return (
    <div className="splash-screen">
      <div className="splash-logo">S</div>
      <div className="splash-title">SparePartFinder Pro</div>
      <div className="splash-subtitle">Industrial AI Identification Tool</div>
      <div className="splash-loader">
        <div className="splash-loader-bar"></div>
      </div>
      <div className="splash-status">{status}</div>
    </div>
  );
};

export default SplashScreen;
