import React from 'react';
import './Footer.css';

export const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="logo-icon">🌾</span>
            <span className="logo-text">AgriSubv</span>
          </div>
          <div className="footer-links">
            <a href="#mentions">Mentions légales</a>
            <a href="#contact">Contact</a>
            <a href="#cgu">CGU</a>
          </div>
          <div className="footer-copyright">
            © 2025 AgriSubv • Fait avec ❤️ pour les agriculteurs français
          </div>
        </div>
      </div>
    </footer>
  );
};
