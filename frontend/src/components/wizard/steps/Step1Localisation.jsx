import React, { useState } from 'react';

const REGIONS = [
  "Auvergne-Rhône-Alpes",
  "Bourgogne-Franche-Comté",
  "Bretagne",
  "Centre-Val de Loire",
  "Corse",
  "Grand Est",
  "Hauts-de-France",
  "Île-de-France",
  "Normandie",
  "Nouvelle-Aquitaine",
  "Occitanie",
  "Provence-Alpes-Côte d'Azur",
  "Pays de la Loire"
];

export const Step1Localisation = ({ initialData, onNext, onBack }) => {
  const [formData, setFormData] = useState({
    region: initialData?.region || '',
    departement: initialData?.departement || '',
    epci: initialData?.epci || '',
    commune: initialData?.commune || ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(formData);
  };

  return (
    <div className="wizard-step animate-fadeIn">
      <h2 className="step-title">📍 Localisation de votre exploitation</h2>
      <p className="step-description">
        Ces informations nous permettent de trouver les aides régionales et départementales
      </p>

      <form onSubmit={handleSubmit} className="wizard-form">
        <div className="form-group">
          <label className="form-label required">Région</label>
          <select
            name="region"
            value={formData.region}
            onChange={handleChange}
            className="form-select"
            required
          >
            <option value="">Sélectionnez votre région</option>
            {REGIONS.map(region => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label required">Département</label>
          <input
            type="text"
            name="departement"
            value={formData.departement}
            onChange={handleChange}
            placeholder="Ex: 75, 69, 33..."
            className="form-input"
            required
          />
          <small className="form-hint">Entrez le numéro de votre département</small>
        </div>

        <div className="form-group">
          <label className="form-label">EPCI (Intercommunalité)</label>
          <input
            type="text"
            name="epci"
            value={formData.epci}
            onChange={handleChange}
            placeholder="Ex: Métropole de Lyon"
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Commune</label>
          <input
            type="text"
            name="commune"
            value={formData.commune}
            onChange={handleChange}
            placeholder="Ex: Paris, Lyon..."
            className="form-input"
          />
        </div>

        <div className="wizard-actions">
          <button type="submit" className="btn-primary">
            Suivant →
          </button>
        </div>
      </form>
    </div>
  );
};
