import React, { useState } from 'react';
import { ProgressBar } from './ProgressBar';
import { Step1Localisation } from './steps/Step1Localisation';
import { Step2Profil } from './steps/Step2Profil';
import { Step3Exploitation } from './steps/Step3Exploitation';
import { Step4Productions } from './steps/Step4Productions';
import { Step5Financier } from './steps/Step5Financier';
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
    const updatedData = { ...formData, ...stepData };
    setFormData(updatedData);
    
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
      // Scroll vers le haut
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      // Dernière étape - soumission
      onComplete(updatedData);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const renderStep = () => {
    const stepProps = {
      initialData: formData,
      onNext: handleNext,
      onBack: handleBack
    };

    switch (currentStep) {
      case 1:
        return <Step1Localisation {...stepProps} />;
      case 2:
        return <Step2Profil {...stepProps} />;
      case 3:
        return <Step3Exploitation {...stepProps} />;
      case 4:
        return <Step4Productions {...stepProps} />;
      case 5:
        return <Step5Financier {...stepProps} />;
      default:
        return <Step1Localisation {...stepProps} />;
    }
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
