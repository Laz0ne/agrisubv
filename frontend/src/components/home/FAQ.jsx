import React, { useState } from 'react';
import './FAQ.css';

const ChevronIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    className="faq-chevron"
  >
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

const categoryIcons = {
  0: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
};

export const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "C'est vraiment gratuit ?",
      answer: "Oui ! La simulation et la découverte de vos aides sont 100% gratuites. Nous proposons ensuite un accompagnement optionnel payant pour vous aider à constituer vos dossiers."
    },
    {
      question: "Combien de temps prend la simulation ?",
      answer: "5 minutes seulement ! Vous répondez à un questionnaire simple sur votre exploitation, et notre algorithme analyse instantanément plus de 1000 aides pour trouver celles qui vous correspondent."
    },
    {
      question: "Quelles aides sont référencées ?",
      answer: "Nous référençons plus de 1000 aides : PAC, aides régionales, départementales, FEADER, France Relance, aides à la transition écologique, à l'installation, à l'investissement, etc."
    },
    {
      question: "Mes données sont-elles sécurisées ?",
      answer: "Absolument ! Vos données sont chiffrées et stockées de manière sécurisée. Nous ne partageons jamais vos informations personnelles avec des tiers. Vous pouvez consulter notre politique de confidentialité pour plus de détails."
    },
    {
      question: "Comment fonctionne l'accompagnement ?",
      answer: "Après votre simulation, vous pouvez choisir de vous faire accompagner par nos experts. Ils vous aident à comprendre les conditions d'éligibilité, rassembler les pièces justificatives, et constituer vos dossiers de A à Z."
    },
    {
      question: "Les résultats sont-ils fiables ?",
      answer: "Nos algorithmes analysent vos critères avec précision. Cependant, l'éligibilité finale dépend de l'étude complète de votre dossier par les organismes financeurs. Nous indiquons un score de pertinence pour chaque aide."
    },
    {
      question: "Puis-je sauvegarder mes résultats ?",
      answer: "Oui ! Vous pouvez ajouter vos aides favorites à votre liste, et exporter vos résultats en PDF. Créez un compte gratuit pour sauvegarder vos simulations et recevoir des alertes sur les nouvelles aides."
    },
    {
      question: "Que faire si je ne trouve pas d'aide ?",
      answer: "Si aucune aide ne correspond exactement à votre profil, nos experts peuvent vous conseiller sur les modifications à apporter à votre projet pour devenir éligible, ou vous orienter vers d'autres dispositifs de financement."
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="faq-section" id="faq" aria-label="Questions fréquentes">
      <div className="container">
        <h2 className="section-title">Questions fréquentes</h2>
        <p className="section-subtitle">
          Tout ce que vous devez savoir sur AgriSubv
        </p>

        <div className="faq-container" role="list">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div
                key={index}
                className={`faq-item${isOpen ? ' open' : ''}`}
                role="listitem"
              >
                <button
                  className="faq-question"
                  onClick={() => toggleFAQ(index)}
                  aria-expanded={isOpen}
                  aria-controls={`faq-answer-${index}`}
                  id={`faq-question-${index}`}
                >
                  <span className="faq-icon" aria-hidden="true">
                    {categoryIcons[0]}
                  </span>
                  <span className="faq-question-text">{faq.question}</span>
                  <span className={`faq-toggle${isOpen ? ' open' : ''}`} aria-hidden="true">
                    <ChevronIcon />
                  </span>
                </button>

                <div
                  id={`faq-answer-${index}`}
                  role="region"
                  aria-labelledby={`faq-question-${index}`}
                  className={`faq-answer${isOpen ? ' open' : ''}`}
                >
                  <p>{faq.answer}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="faq-cta">
          <p className="faq-cta-text">
            Vous avez une autre question ?
          </p>
          <a href="mailto:contact@agrisubv.fr" className="btn-secondary faq-contact-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
            </svg>
            Contactez-nous
          </a>
        </div>
      </div>
    </section>
  );
};
