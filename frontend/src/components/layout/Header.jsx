import React from 'react';
import './Header.css';

export const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🌾</span>
            <span className="logo-text">AgriSubv</span>
          </div>
          <nav className="nav">
            <a href="#accueil" className="nav-link">Accueil</a>
            <a href="#comment-ca-marche" className="nav-link">Comment ça marche</a>
            <a href="#faq" className="nav-link">FAQ</a>
          </nav>
          <button className="btn-account">Mon compte</button>
        </div>
      </div>
    </header>
  );
};