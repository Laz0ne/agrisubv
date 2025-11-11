import React, { useState } from 'react';

const TYPES_PRODUCTIONS = [
  "Grandes cultures (céréales, oléagineux)",
  "Élevage bovin viande",
  "Élevage bovin lait",
  "Élevage ovin/caprin",
  "Élevage porcin",
  "Élevage volailles",
  "Viticulture",
  "Arboriculture",
  "Maraîchage",
  "Horticulture",
  "Apiculture",
  "Autre"
];

const TYPES_PROJETS = [
  "Transition bio",
  "Installation équipements",
  "Modernisation bâtiments",
  "Diversification activité",
  "Irrigation/eau",
  "Agroforesterie",
  "Méthanisation",
  "Photovoltaïque",
  "Stockage",
  "Transformation produits",
  "Autre"
];

export const Step4Productions = ({ initialData, onNext, onBack }) => {
  const [formData, setFormData] = useState({
    productions: initialData?.productions || [],
    projets_en_cours: initialData?.projets_en_cours || []
  });

  const handleProductionChange = (prod) => {
    setFormData(prev => {
      const productions = prev.productions.includes(prod)
        ? prev.productions.filter(p => p !== prod)
        : [...prev.productions, prod];
      return { ...prev, productions };
    });
  };

  const handleProjetChange = (projet) => {
    setFormData(prev => {
      const projets_en_cours = prev.projets_en_cours.includes(projet)
        ? prev.projets_en_cours.filter(p => p !== projet)
        : [...prev.projets_en_cours, projet];
      return { ...prev, projets_en_cours };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.productions.length === 0) {
      alert('Veuillez sélectionner au moins un type de production');
      return;
    }
    onNext(formData);
  };

  return (
    <div className="wizard-step animate-fadeIn">
      <h2 className="step-title">🐄 Productions et projets</h2>
      <p className="step-description">
        Sélectionnez vos productions actuelles et vos projets en cours
      </p>

      <form onSubmit={handleSubmit} className="wizard-form">
        <div className="form-group">
          <label className="form-label required">Types de production</label>
          <div className="checkbox-grid">
            {TYPES_PRODUCTIONS.map(prod => (
              <label key={prod} className="form-checkbox">
                <input
                  type="checkbox"
                  checked={formData.productions.includes(prod)}
                  onChange={() => handleProductionChange(prod)}
                />
                <span>{prod}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Projets en cours ou envisagés</label>
          <div className="checkbox-grid">
            {TYPES_PROJETS.map(projet => (
              <label key={projet} className="form-checkbox">
                <input
                  type="checkbox"
                  checked={formData.projets_en_cours.includes(projet)}
                  onChange={() => handleProjetChange(projet)}
                />
                <span>{projet}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="wizard-actions">
          <button type="button" className="btn-secondary" onClick={onBack}>
            ← Retour
          </button>
          <button type="submit" className="btn-primary">
            Suivant →
          </button>
        </div>
      </form>
    </div>
  );
};
