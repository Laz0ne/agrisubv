import React, { useState } from 'react';
import './FAQ.css';

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
    <section className="faq-section" id="faq">
      <div className="container">
        <h2 className="section-title">Questions fréquentes</h2>
        <p className="section-subtitle">
          Tout ce que vous devez savoir sur AgriSubv
        </p>

        <div className="faq-container">
          {faqs.map((faq, index) => (
            <div 
              key={index} 
              className={`faq-item ${openIndex === index ? 'open' : ''}`}
            >
              <button 
                className="faq-question"
                onClick={() => toggleFAQ(index)}
              >
                <span className="faq-icon">❓</span>
                <span className="faq-question-text">{faq.question}</span>
                <span className={`faq-toggle ${openIndex === index ? 'open' : ''}`}>
                  {openIndex === index ? '−' : '+'}
                </span>
              </button>
              
              <div className={`faq-answer ${openIndex === index ? 'open' : ''}`}>
                <p>{faq.answer}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="faq-cta">
          <p className="faq-cta-text">
            Vous avez une autre question ?
          </p>
          <button className="btn-secondary">
            📧 Contactez-nous
          </button>
        </div>
      </div>
    </section>
  );
};
