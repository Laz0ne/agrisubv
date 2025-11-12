import React from 'react';
import './Header.css';

export const Header = () => {
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-logo">
          <span className="logo-icon">🌾</span>
          <span className="logo-text">AgriSubv</span>
        </div>
        
        <nav className="header-nav">
          <button 
            className="nav-link"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Accueil
          </button>
          <button 
            className="nav-link"
            onClick={() => scrollToSection('comment-ca-marche')}
          >
            Comment ça marche
          </button>
          <button 
            className="nav-link"
            onClick={() => scrollToSection('faq')}
          >
            FAQ
          </button>
        </nav>
        
        <button className="btn-account">Mon compte</button>
      </div>
    </header>
  );
};
