import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Footer.css';

// SVG Wheat Logo (same as Header)
const WheatIcon = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 28 28"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <line x1="14" y1="26" x2="14" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    <ellipse cx="14" cy="5" rx="3" ry="4.5" fill="currentColor" opacity="0.9"/>
    <ellipse cx="11" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(-20 11 10)"/>
    <ellipse cx="10" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(-25 10 16)"/>
    <ellipse cx="17" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(20 17 10)"/>
    <ellipse cx="18" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(25 18 16)"/>
  </svg>
);

export const Footer = () => {
  const navigate = useNavigate();

  return (
    <footer className="footer" role="contentinfo">
      {/* CTA Strip */}
      <div className="footer-cta-strip">
        <div className="footer-cta-content">
          <p className="footer-cta-text">Prêt à découvrir vos aides agricoles ?</p>
          <button
            className="footer-cta-btn"
            onClick={() => navigate('/questionnaire')}
            aria-label="Démarrer le questionnaire d'aides agricoles"
          >
            Démarrer gratuitement →
          </button>
        </div>
      </div>

      {/* Main Footer */}
      <div className="footer-main">
        <div className="footer-grid">
          {/* Brand Column */}
          <div className="footer-col footer-brand-col">
            <div className="footer-brand">
              <WheatIcon />
              <span className="footer-logo-text">AgriSubv</span>
            </div>
            <p className="footer-tagline">
              La plateforme qui simplifie l'accès aux aides et subventions agricoles pour les exploitants français.
            </p>
            <div className="footer-badges">
              <span className="footer-badge">🔒 100% sécurisé</span>
              <span className="footer-badge">🆓 Gratuit</span>
            </div>
          </div>

          {/* À propos Column */}
          <div className="footer-col">
            <h3 className="footer-col-title">À propos</h3>
            <ul className="footer-col-links">
              <li><a href="#mission">Notre mission</a></li>
              <li><a href="#equipe">L'équipe</a></li>
              <li><a href="#partenaires">Partenaires</a></li>
              <li><a href="#presse">Presse</a></li>
            </ul>
          </div>

          {/* Liens utiles Column */}
          <div className="footer-col">
            <h3 className="footer-col-title">Liens utiles</h3>
            <ul className="footer-col-links">
              <li><a href="https://agriculture.gouv.fr" target="_blank" rel="noopener noreferrer">Ministère de l'Agriculture</a></li>
              <li><a href="https://www.asp-public.fr" target="_blank" rel="noopener noreferrer">ASP — Aides PAC</a></li>
              <li><a href="https://www.chambre-agriculture.fr" target="_blank" rel="noopener noreferrer">Chambres d'Agriculture</a></li>
              <li><a href="#aides-disponibles">Catalogue des aides</a></li>
            </ul>
          </div>

          {/* Légal Column */}
          <div className="footer-col">
            <h3 className="footer-col-title">Légal &amp; Contact</h3>
            <ul className="footer-col-links">
              <li><a href="#mentions">Mentions légales</a></li>
              <li><a href="#cgu">CGU</a></li>
              <li><a href="#confidentialite">Politique de confidentialité</a></li>
              <li><a href="mailto:contact@agrisubv.fr">contact@agrisubv.fr</a></li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="footer-bottom">
        <p className="footer-copyright">
          © 2026 AgriSubv — Fait avec ❤️ pour les agriculteurs français
        </p>
        <p className="footer-disclaimer">
          Les informations présentées sont données à titre indicatif. L'éligibilité finale relève des organismes compétents.
        </p>
      </div>
    </footer>
  );
};
