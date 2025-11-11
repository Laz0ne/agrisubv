import React, { useState } from 'react';

export const Step5Financier = ({ initialData, onNext, onBack }) => {
  const [formData, setFormData] = useState({
    montant_projet: initialData?.montant_projet || '',
    budget_disponible: initialData?.budget_disponible || '',
    cofinancement_obtenu: initialData?.cofinancement_obtenu || false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(formData);
  };

  return (
    <div className="wizard-step animate-fadeIn">
      <h2 className="step-title">💰 Informations financières</h2>
      <p className="step-description">
        Ces informations nous aident à évaluer les montants d'aides potentiels
      </p>

      <form onSubmit={handleSubmit} className="wizard-form">
        <div className="form-group">
          <label className="form-label">Montant du projet principal</label>
          <input
            type="number"
            name="montant_projet"
            value={formData.montant_projet}
            onChange={handleChange}
            placeholder="Ex: 50000"
            min="0"
            step="1000"
            className="form-input"
          />
          <small className="form-hint">En euros (si vous avez un projet d'investissement en cours)</small>
        </div>

        <div className="form-group">
          <label className="form-label">Budget disponible (autofinancement)</label>
          <input
            type="number"
            name="budget_disponible"
            value={formData.budget_disponible}
            onChange={handleChange}
            placeholder="Ex: 20000"
            min="0"
            step="1000"
            className="form-input"
          />
          <small className="form-hint">En euros</small>
        </div>

        <div className="form-group">
          <label className="form-checkbox">
            <input
              type="checkbox"
              name="cofinancement_obtenu"
              checked={formData.cofinancement_obtenu}
              onChange={handleChange}
            />
            <span>J'ai déjà obtenu un cofinancement (banque, autre organisme)</span>
          </label>
        </div>

        <div className="info-box">
          <span className="info-icon">💡</span>
          <div>
            <strong>Information importante</strong>
            <p>Ces informations sont optionnelles mais nous permettent d'affiner les résultats et de calculer les montants estimés d'aides.</p>
          </div>
        </div>

        <div className="wizard-actions">
          <button type="button" className="btn-secondary" onClick={onBack}>
            ← Retour
          </button>
          <button type="submit" className="btn-primary">
            Voir les résultats 🎉
          </button>
        </div>
      </form>
    </div>
  );
};
