import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './Header.css';

// SVG Wheat Logo
const WheatIcon = () => (
  <svg
    width="28"
    height="28"
    viewBox="0 0 28 28"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    className="logo-svg"
  >
    {/* Stem */}
    <line x1="14" y1="26" x2="14" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    {/* Top grain */}
    <ellipse cx="14" cy="5" rx="3" ry="4.5" fill="currentColor" opacity="0.9"/>
    {/* Left grains */}
    <ellipse cx="11" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(-20 11 10)"/>
    <ellipse cx="10" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(-25 10 16)"/>
    {/* Right grains */}
    <ellipse cx="17" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(20 17 10)"/>
    <ellipse cx="18" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(25 18 16)"/>
  </svg>
);

// SVG User Icon
const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

export const Header = () => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menu on route change
  useEffect(() => {
    setMenuOpen(false);
  }, [location]);

  const scrollToTop = () => {
    window.location.href = '/';
  };

  const navigateToSection = (sectionId) => {
    setMenuOpen(false);
    const isOnHomepage = !document.querySelector('.wizard-container') &&
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

  const isActive = (path) => location.pathname === path;

  return (
    <header className={`header${scrolled ? ' scrolled' : ''}`} role="banner">
      <div className="header-container">
        {/* Logo */}
        <button
          className="header-logo"
          onClick={scrollToTop}
          aria-label="AgriSubv — Retour à l'accueil"
        >
          <WheatIcon />
          <span className="logo-text">AgriSubv</span>
        </button>

        {/* Desktop Nav */}
        <nav className="header-nav" aria-label="Navigation principale">
          <button
            className={`nav-link${isActive('/') ? ' active' : ''}`}
            onClick={scrollToTop}
            aria-current={isActive('/') ? 'page' : undefined}
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

        {/* Account Button */}
        <button className="btn-account" aria-label="Accéder à mon compte">
          <UserIcon />
          <span>Mon compte</span>
        </button>

        {/* Hamburger Toggle */}
        <button
          className={`menu-toggle${menuOpen ? ' open' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label={menuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
        >
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>
      </div>

      {/* Mobile Drawer */}
      {menuOpen && (
        <div
          id="mobile-menu"
          className="mobile-menu"
          role="dialog"
          aria-label="Menu de navigation mobile"
        >
          <nav aria-label="Navigation mobile">
            <button
              className={`mobile-nav-link${isActive('/') ? ' active' : ''}`}
              onClick={scrollToTop}
              aria-current={isActive('/') ? 'page' : undefined}
            >
              🏠 Accueil
            </button>
            <button
              className="mobile-nav-link"
              onClick={() => navigateToSection('comment-ca-marche')}
            >
              ❓ Comment ça marche
            </button>
            <button
              className="mobile-nav-link"
              onClick={() => navigateToSection('faq')}
            >
              💬 FAQ
            </button>
            <button className="mobile-nav-link mobile-account">
              <UserIcon />
              Mon compte
            </button>
          </nav>
        </div>
      )}
    </header>
  );
};
