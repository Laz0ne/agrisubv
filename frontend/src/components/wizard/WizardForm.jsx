import React, { useState } from 'react';
import { ProgressBar } from './ProgressBar';
import './WizardForm.css';

export const WizardForm = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Localisation
    region: '',
    departement: '',
    epci: '',
    commune: '',
    
    // Profil
    statut_juridique: '',
    age: null,
    jeune_agriculteur: false,
    nouvel_installe: false,
    genre: '',
    formation_agricole: false,
    experience_agricole: null,
    
    // Exploitation
    sau_totale: 0,
    sau_irrigable: null,
    certifications: [],
    signes_qualite: [],
    mode_commercialisation: '',
    nombre_uth: null,
    
    // Productions & Projets
    productions: [],
    projets_en_cours: [],
    
    // Financier
    montant_projet: null,
    budget_disponible: null,
    cofinancement_obtenu: false
  });

  const totalSteps = 5;

  const handleNext = (stepData) => {
    setFormData({ ...formData, ...stepData });
    
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      // Dernière étape - soumission
      onComplete({ ...formData, ...stepData });
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep = () => {
    // Pour l'instant, affiche juste un message simple
    // Les composants Step1, Step2, etc. seront créés après
    return (
      <div className="wizard-step animate-fadeIn">
        <h2 className="step-title">Étape {currentStep}/5</h2>
        <p className="step-description">
          Cette étape sera complétée avec les composants Step1Localisation.jsx, etc.
        </p>
        
        <div className="wizard-actions">
          {currentStep > 1 && (
            <button 
              type="button" 
              className="btn-secondary"
              onClick={handleBack}
            >
              ← Retour
            </button>
          )}
          <button 
            type="button" 
            className="btn-primary"
            onClick={() => handleNext({})}
          >
            {currentStep < totalSteps ? 'Suivant →' : 'Voir les résultats 🎉'}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="wizard-container">
      <div className="wizard-card">
        <ProgressBar currentStep={currentStep} totalSteps={totalSteps} />
        <div className="wizard-content">
          {renderStep()}
        </div>
      </div>
    </div>
  );
};
