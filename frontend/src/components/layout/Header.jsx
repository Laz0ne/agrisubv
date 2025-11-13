import React from 'react';
import './Header.css';

export const Header = () => {
  const scrollToTop = () => {
    window.location.href = '/';
  };

  const navigateToSection = (sectionId) => {
    const isOnHomepage = !window.location.hash && 
                         !document.querySelector('.wizard-container') &&
                         !document.querySelector('.results-container');
    
    if (!isOnHomepage) {
      window.location.href = `/#${sectionId}`;
    } else {
      const element = document.getElementById(sectionId);
      if (element) {
        const yOffset = -100;
        const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
    }
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-logo" onClick={scrollToTop}>
          <span className="logo-icon">🌾</span>
          <span className="logo-text">AgriSubv</span>
        </div>
        
        <nav className="header-nav">
          <button 
            className="nav-link"
            onClick={scrollToTop}
          >
            Accueil
          </button>
          <button 
            className="nav-link"
            onClick={() => navigateToSection('comment-ca-marche')}
          >
            Comment ça marche
          </button>
          <button 
            className="nav-link"
            onClick={() => navigateToSection('faq')}
          >
            FAQ
          </button>
        </nav>
        
        <button className="btn-account">Mon compte</button>
      </div>
    </header>
  );
};
