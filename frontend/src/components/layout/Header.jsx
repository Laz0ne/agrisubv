import React from 'react';
import './Header.css';

export const Header = () => {
  const scrollToTop = () => {
    // Recharger la page pour revenir à l'accueil
    window.location.href = '/';
  };

  const navigateToSection = (sectionId) => {
    // Si on est dans le wizard/résultats, d'abord retourner à l'accueil
    const isOnHomepage = !window.location.hash && 
                         !document.querySelector('.wizard-container') &&
                         !document.querySelector('.results-container');
    
    if (!isOnHomepage) {
      // Retourner à l'accueil avec le hash de la section
      window.location.href = `/#${sectionId}`;
    } else {
      // Déjà sur la homepage, juste scroller
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
