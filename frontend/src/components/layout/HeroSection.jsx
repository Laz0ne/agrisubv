import React from 'react';
import './HeroSection.css';

export const HeroSection = ({ onStart }) => {
  return (
    <section className="hero">
      <div className="container">
        <div className="hero-content">
          <h1 className="hero-title animate-fadeIn">
            🌾 Trouvez toutes vos aides agricoles
            <br />
            en quelques clics
          </h1>
          <p className="hero-subtitle animate-fadeIn">
            Simulateur intelligent • 1000+ aides • Gratuit
          </p>
          <button className="btn-primary btn-hero animate-fadeIn" onClick={onStart}>
            Commencer ma simulation
            <span className="arrow">→</span>
          </button>
        </div>
      </div>
      <div className="scroll-indicator animate-bounce">
        <span>↓</span>
      </div>
    </section>
  );
};
