import React from 'react';
import './ProgressBar.css';

export const ProgressBar = ({ currentStep, totalSteps }) => {
  const progress = (currentStep / totalSteps) * 100;
  
  const steps = [
    { number: 1, title: "Localisation", icon: "📍" },
    { number: 2, title: "Profil", icon: "👨‍🌾" },
    { number: 3, title: "Exploitation", icon: "🌾" },
    { number: 4, title: "Productions", icon: "🐄" },
    { number: 5, title: "Financier", icon: "💰" }
  ];

  return (
    <div className="progress-container">
      <div className="progress-header">
        <span className="progress-text">
          Étape {currentStep} sur {totalSteps}
        </span>
        <span className="progress-percentage">{Math.round(progress)}%</span>
      </div>
      <div className="progress-bar-bg">
        <div 
          className="progress-bar-fill" 
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="progress-steps">
        {steps.map((step) => (
          <div 
            key={step.number}
            className={`progress-step ${currentStep >= step.number ? 'active' : ''} ${currentStep === step.number ? 'current' : ''}`}
          >
            <div className="progress-step-circle">
              {currentStep > step.number ? '✓' : step.icon}
            </div>
            <span className="progress-step-title">{step.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
