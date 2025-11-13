import React, { useState } from 'react';
import './Account.css';

export const Account = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginMode, setLoginMode] = useState('login');
  
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });

  const [registerData, setRegisterData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    password: '',
    confirmPassword: ''
  });

  const handleLoginChange = (e) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value
    });
  };

  const handleRegisterChange = (e) => {
    setRegisterData({
      ...registerData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = (e) => {
    e.preventDefault();
    console.log('Connexion:', loginData);
    setIsLoggedIn(true);
  };

  const handleRegister = (e) => {
    e.preventDefault();
    if (registerData.password !== registerData.confirmPassword) {
      alert('Les mots de passe ne correspondent pas');
      return;
    }
    console.log('Inscription:', registerData);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setLoginData({ email: '', password: '' });
  };

  if (isLoggedIn) {
    return (
      <div className="account-page">
        <div className="account-container">
          <div className="account-header">
            <h1>👤 Mon Compte</h1>
            <button className="btn-logout" onClick={handleLogout}>
              🚪 Déconnexion
            </button>
          </div>

          <div className="account-grid">
            <div className="account-card">
              <h2>📋 Mon Profil</h2>
              <div className="profile-info">
                <div className="info-row">
                  <strong>Nom :</strong>
                  <span>Jean Dupont</span>
                </div>
                <div className="info-row">
                  <strong>Email :</strong>
                  <span>jean.dupont@example.com</span>
                </div>
                <div className="info-row">
                  <strong>Téléphone :</strong>
                  <span>06 12 34 56 78</span>
                </div>
                <button className="btn-edit">✏️ Modifier mes informations</button>
              </div>
            </div>

            <div className="account-card">
              <h2>📊 Mes Simulations</h2>
              <div className="simulations-list">
                <p className="empty-state">Aucune simulation enregistrée pour le moment</p>
              </div>
            </div>

            <div className="account-card">
              <h2>⭐ Mes Aides Favorites</h2>
              <div className="favorites-list">
                <p className="empty-state">Aucune aide favorite pour le moment</p>
              </div>
            </div>

            <div className="account-card">
              <h2>⚙️ Paramètres</h2>
              <div className="settings-list">
                <div className="setting-item">
                  <label>
                    <input type="checkbox" />
                    <span>Recevoir les notifications par email</span>
                  </label>
                </div>
                <div className="setting-item">
                  <label>
                    <input type="checkbox" />
                    <span>Alertes sur les nouvelles aides</span>
                  </label>
                </div>
                <div className="setting-item">
                  <label>
                    <input type="checkbox" checked readOnly />
                    <span>Newsletter mensuelle</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="account-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>👤 Mon Compte</h1>
          <p>Connectez-vous pour accéder à vos simulations et favoris</p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`auth-tab ${loginMode === 'login' ? 'active' : ''}`}
            onClick={() => setLoginMode('login')}
          >
            Connexion
          </button>
          <button 
            className={`auth-tab ${loginMode === 'register' ? 'active' : ''}`}
            onClick={() => setLoginMode('register')}
          >
            Inscription
          </button>
        </div>

        {loginMode === 'login' ? (
          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label htmlFor="login-email">Email</label>
              <input
                type="email"
                id="login-email"
                name="email"
                value={loginData.email}
                onChange={handleLoginChange}
                required
                placeholder="votre@email.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="login-password">Mot de passe</label>
              <input
                type="password"
                id="login-password"
                name="password"
                value={loginData.password}
                onChange={handleLoginChange}
                required
                placeholder="••••••••"
              />
            </div>

            <button type="submit" className="btn-submit">
              🔓 Se connecter
            </button>

            <a href="#" className="forgot-password">Mot de passe oublié ?</a>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="auth-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="register-nom">Nom</label>
                <input
                  type="text"
                  id="register-nom"
                  name="nom"
                  value={registerData.nom}
                  onChange={handleRegisterChange}
                  required
                  placeholder="Dupont"
                />
              </div>

              <div className="form-group">
                <label htmlFor="register-prenom">Prénom</label>
                <input
                  type="text"
                  id="register-prenom"
                  name="prenom"
                  value={registerData.prenom}
                  onChange={handleRegisterChange}
                  required
                  placeholder="Jean"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="register-email">Email</label>
              <input
                type="email"
                id="register-email"
                name="email"
                value={registerData.email}
                onChange={handleRegisterChange}
                required
                placeholder="votre@email.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-telephone">Téléphone</label>
              <input
                type="tel"
                id="register-telephone"
                name="telephone"
                value={registerData.telephone}
                onChange={handleRegisterChange}
                placeholder="06 12 34 56 78"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-password">Mot de passe</label>
              <input
                type="password"
                id="register-password"
                name="password"
                value={registerData.password}
                onChange={handleRegisterChange}
                required
                placeholder="••••••••"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-confirm">Confirmer le mot de passe</label>
              <input
                type="password"
                id="register-confirm"
                name="confirmPassword"
                value={registerData.confirmPassword}
                onChange={handleRegisterChange}
                required
                placeholder="••••••••"
              />
            </div>

            <button type="submit" className="btn-submit">
              ✅ Créer mon compte
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
