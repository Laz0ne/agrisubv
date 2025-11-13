import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

export const Header = () => {
  const navigate = useNavigate();

  const scrollToSection = (sectionId) => {
    if (window.location.pathname !== '/') {
      navigate('/');
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          const yOffset = -100;
          const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }, 100);
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
        <Link to="/" className="header-logo">
          <span className="logo-icon">🌾</span>
          <span className="logo-text">AgriSubv</span>
        </Link>
        
        <nav className="header-nav">
          <Link to="/" className="nav-link">
            Accueil
          </Link>
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
          <Link to="/contact" className="nav-link">
            Contact
          </Link>
        </nav>
        
        <Link to="/compte" className="btn-account">
          Mon compte
        </Link>
      </div>
    </header>
  );
};
