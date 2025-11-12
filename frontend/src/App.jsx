import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { HeroSection } from './components/layout/HeroSection';
import { HowItWorks } from './components/home/HowItWorks';
import { FAQ } from './components/home/FAQ';
import { Footer } from './components/layout/Footer';
import { WizardForm } from './components/wizard/WizardForm';
import { ResultsSection } from './components/results/ResultsSection';
import './styles/variables.css';
import './styles/animations.css';
import './App.css';

function App() {
  const [showWizard, setShowWizard] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleStartSimulation = () => {
    setShowWizard(true);
    // Scroll vers le wizard
    setTimeout(() => {
      document.querySelector('.wizard-container')?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  };

  const handleWizardComplete = async (formData) => {
    setLoading(true);
    
    try {
      const response = await fetch('https://agrisubv-backend.onrender.com/api/matching', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des aides');
      }

      const data = await response.json();
      setResults(data);
      
      // Scroll vers les résultats
      setTimeout(() => {
        document.querySelector('.results-container')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
    } catch (error) {
      console.error('Erreur:', error);
      alert('Une erreur est survenue. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      
      {!showWizard && !results && (
        <>
          <HeroSection onStart={handleStartSimulation} />
          <HowItWorks onStart={handleStartSimulation} />
          <FAQ />
        </>
      )}
      
      {showWizard && !results && (
        <WizardForm onComplete={handleWizardComplete} />
      )}
      
      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Analyse de vos critères en cours...</p>
        </div>
      )}
      
      {results && (
        <>
          <ResultsSection results={results} />
          <div className="restart-container">
            <button 
              className="btn-primary"
              onClick={() => {
                setShowWizard(false);
                setResults(null);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
            >
              🔄 Nouvelle simulation
            </button>
          </div>
        </>
      )}
      
      <Footer />
    </div>
  );
}

export default App;
