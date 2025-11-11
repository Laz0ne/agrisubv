import React, { useState } from 'react';

const STATUTS = [
  "Exploitation individuelle",
  "EARL",
  "GAEC",
  "SCEA",
  "SAS",
  "Autre"
];

export const Step2Profil = ({ initialData, onNext, onBack }) => {
  const [formData, setFormData] = useState({
    statut_juridique: initialData?.statut_juridique || '',
    age: initialData?.age || '',
    jeune_agriculteur: initialData?.jeune_agriculteur || false,
    nouvel_installe: initialData?.nouvel_installe || false,
    genre: initialData?.genre || '',
    formation_agricole: initialData?.formation_agricole || false,
    experience_agricole: initialData?.experience_agricole || ''
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
      <h2 className="step-title">👨‍🌾 Votre profil</h2>
      <p className="step-description">
        Certaines aides sont réservées aux jeunes agriculteurs ou nouveaux installés
      </p>

      <form onSubmit={handleSubmit} className="wizard-form">
        <div className="form-group">
          <label className="form-label required">Statut juridique</label>
          <select
            name="statut_juridique"
            value={formData.statut_juridique}
            onChange={handleChange}
            className="form-select"
            required
          >
            <option value="">Sélectionnez votre statut</option>
            {STATUTS.map(statut => (
              <option key={statut} value={statut}>{statut}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Âge</label>
          <input
            type="number"
            name="age"
            value={formData.age}
            onChange={handleChange}
            placeholder="Ex: 35"
            min="18"
            max="100"
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Genre</label>
          <select
            name="genre"
            value={formData.genre}
            onChange={handleChange}
            className="form-select"
          >
            <option value="">Non précisé</option>
            <option value="homme">Homme</option>
            <option value="femme">Femme</option>
            <option value="autre">Autre</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-checkbox">
            <input
              type="checkbox"
              name="jeune_agriculteur"
              checked={formData.jeune_agriculteur}
              onChange={handleChange}
            />
            <span>Jeune agriculteur (moins de 40 ans à l'installation)</span>
          </label>
        </div>

        <div className="form-group">
          <label className="form-checkbox">
            <input
              type="checkbox"
              name="nouvel_installe"
              checked={formData.nouvel_installe}
              onChange={handleChange}
            />
            <span>Nouvel installé (moins de 5 ans)</span>
          </label>
        </div>

        <div className="form-group">
          <label className="form-checkbox">
            <input
              type="checkbox"
              name="formation_agricole"
              checked={formData.formation_agricole}
              onChange={handleChange}
            />
            <span>Formation agricole (diplôme ou capacité professionnelle)</span>
          </label>
        </div>

        <div className="form-group">
          <label className="form-label">Années d'expérience</label>
          <input
            type="number"
            name="experience_agricole"
            value={formData.experience_agricole}
            onChange={handleChange}
            placeholder="Ex: 10"
            min="0"
            className="form-input"
          />
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
