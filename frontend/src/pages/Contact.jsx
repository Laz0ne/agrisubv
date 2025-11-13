import React, { useState } from 'react';
import './Contact.css';

export const Contact = () => {
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    sujet: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Formulaire soumis:', formData);
    setSubmitted(true);
    
    setTimeout(() => {
      setSubmitted(false);
      setFormData({ nom: '', email: '', sujet: '', message: '' });
    }, 3000);
  };

  return (
    <div className="contact-page">
      <div className="contact-container">
        <div className="contact-header">
          <h1>📧 Contactez-nous</h1>
          <p>Une question ? Une suggestion ? Nous sommes là pour vous aider !</p>
        </div>

        <div className="contact-content">
          <div className="contact-form-section">
            <form onSubmit={handleSubmit} className="contact-form">
              <div className="form-group">
                <label htmlFor="nom">Nom complet *</label>
                <input
                  type="text"
                  id="nom"
                  name="nom"
                  value={formData.nom}
                  onChange={handleChange}
                  required
                  placeholder="Jean Dupont"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="jean.dupont@example.com"
                />
              </div>

              <div className="form-group">
                <label htmlFor="sujet">Sujet *</label>
                <select
                  id="sujet"
                  name="sujet"
                  value={formData.sujet}
                  onChange={handleChange}
                  required
                >
                  <option value="">Sélectionnez un sujet</option>
                  <option value="question">Question générale</option>
                  <option value="aide">Aide sur une aide spécifique</option>
                  <option value="bug">Signaler un bug</option>
                  <option value="suggestion">Suggestion d'amélioration</option>
                  <option value="partenariat">Partenariat</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="message">Message *</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="6"
                  placeholder="Décrivez votre demande..."
                />
              </div>

              <button type="submit" className="btn-submit">
                {submitted ? '✅ Message envoyé !' : '📤 Envoyer le message'}
              </button>

              {submitted && (
                <div className="success-message">
                  <p>✅ Merci ! Votre message a été envoyé. Nous vous répondrons dans les 48h.</p>
                </div>
              )}
            </form>
          </div>

          <div className="contact-info-section">
            <div className="contact-info-card">
              <h3>📍 Autres moyens de contact</h3>
              
              <div className="contact-item">
                <span className="contact-icon">📧</span>
                <div>
                  <strong>Email</strong>
                  <p>contact@agrisubv.fr</p>
                </div>
              </div>

              <div className="contact-item">
                <span className="contact-icon">📞</span>
                <div>
                  <strong>Téléphone</strong>
                  <p>01 23 45 67 89</p>
                  <small>Lun-Ven : 9h-18h</small>
                </div>
              </div>

              <div className="contact-item">
                <span className="contact-icon">💬</span>
                <div>
                  <strong>Chat en ligne</strong>
                  <p>Disponible sur notre site</p>
                  <small>Lun-Ven : 9h-18h</small>
                </div>
              </div>
            </div>

            <div className="contact-info-card">
              <h3>⏱️ Temps de réponse</h3>
              <ul>
                <li>Email : 24-48h</li>
                <li>Téléphone : immédiat</li>
                <li>Chat : immédiat</li>
              </ul>
            </div>

            <div className="contact-info-card">
              <h3>🔗 Suivez-nous</h3>
              <div className="social-links">
                <a href="#" className="social-link">🐦 Twitter</a>
                <a href="#" className="social-link">📘 Facebook</a>
                <a href="#" className="social-link">💼 LinkedIn</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
