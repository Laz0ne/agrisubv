import React from 'react';
import './HowItWorks.css';

export const HowItWorks = ({ onStart }) => {
  const steps = [
    {
      number: "1",
      icon: "📝",
      title: "Répondez au questionnaire",
      description: "5 minutes pour décrire votre exploitation et vos projets",
      time: "5 min"
    },
    {
      number: "2",
      icon: "🎯",
      title: "Découvrez vos aides",
      description: "Notre algorithme analyse 1000+ aides et trouve celles faites pour vous",
      time: "Instantané"
    },
    {
      number: "3",
      icon: "🚀",
      title: "Faites-vous accompagner",
      description: "Nos experts vous aident à monter vos dossiers (optionnel)",
      time: "Sur mesure"
    }
  ];

  return (
    <section className="how-it-works" id="comment-ca-marche">
      <div className="container">
        <h2 className="section-title">Comment ça marche ?</h2>
        <p className="section-subtitle">
          Trouvez vos aides en 3 étapes simples
        </p>

        <div className="steps-grid">
          {steps.map((step, index) => (
            <div key={index} className="step-card animate-fadeIn" style={{ animationDelay: `${index * 0.2}s` }}>
              <div className="step-number">{step.number}</div>
              <div className="step-icon">{step.icon}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
              <span className="step-time">⏱️ {step.time}</span>
            </div>
          ))}
        </div>

        <div className="cta-container">
          <button onClick={onStart} className="btn-primary btn-large">
            Commencer maintenant →
          </button>
        </div>
      </div>
    </section>
  );
};
