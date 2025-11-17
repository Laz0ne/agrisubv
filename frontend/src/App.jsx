import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { HeroSection } from './components/layout/HeroSection';
import { HowItWorks } from './components/home/HowItWorks';
import { FAQ } from './components/home/FAQ';
import { Footer } from './components/layout/Footer';
import { WizardForm } from './components/wizard/WizardForm';
import { ResultsSection } from './components/results/ResultsSection';
import DynamicQuestionnaire from './components/DynamicQuestionnaire';
import ResultsPage from './components/ResultsPage';
import './styles/variables.css';
import './styles/animations.css';
import './App.css';

// Page d'accueil avec l'ancien visuel
function HomePage() {
  const navigate = useNavigate();
  const [showWizard, setShowWizard] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleStartSimulation = () => {
    setShowWizard(true);
    setTimeout(() => {
      const wizardElement = document.querySelector('.wizard-container');
      if (wizardElement) {
        const yOffset = -100;
        const y = wizardElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
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
      
      setTimeout(() => {
        const resultsElement = document.querySelector('.results-container');
        if (resultsElement) {
          const yOffset = -100;
          const y = resultsElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
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
      <div className="decorative-band"></div>
      <Header />
      
      {!showWizard && !results && (
        <>
          <HeroSection onStart={handleStartSimulation} />
          <HowItWorks onStart={handleStartSimulation} />
          
          {/* Nouveau bouton pour accéder au questionnaire dynamique */}
          <div className="dynamic-questionnaire-section" style={{ padding: '4rem 2rem', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', textAlign: 'center' }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🆕 Nouveau : Questionnaire Intelligent</h2>
            <p style={{ fontSize: '1.25rem', marginBottom: '2rem', opacity: 0.9 }}>
              Basé sur l'analyse de 507 aides agricoles • 80% des aides concernent le bio
            </p>
            <button 
              onClick={() => navigate('/questionnaire')}
              className="btn-primary"
              style={{ background: 'white', color: '#667eea', padding: '1rem 2rem', fontSize: '1.125rem', fontWeight: 'bold', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
            >
              Essayer le nouveau questionnaire 🚀
            </button>
          </div>
          
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

// Page du questionnaire dynamique
function QuestionnairePage() {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [profil, setProfil] = useState(null);

  const handleComplete = (matchingResults, userProfil) => {
    setResults(matchingResults);
    setProfil(userProfil);
  };

  const handleRestart = () => {
    setResults(null);
    setProfil(null);
  };

  const handleBackHome = () => {
    navigate('/');
  };

  if (results) {
    return (
      <>
        <div style={{ padding: '1rem', background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
          <button 
            onClick={handleBackHome}
            style={{ padding: '0.5rem 1rem', background: '#6b7280', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}
          >
            ← Retour à l'accueil
          </button>
        </div>
        <ResultsPage results={results} profil={profil} onRestart={handleRestart} />
      </>
    );
  }

  return (
    <>
      <div style={{ padding: '1rem', background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
        <button 
          onClick={handleBackHome}
          style={{ padding: '0.5rem 1rem', background: '#6b7280', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' }}
        >
          ← Retour à l'accueil
        </button>
      </div>
      <DynamicQuestionnaire onComplete={handleComplete} />
    </>
  );
}

// App principal avec routing
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/questionnaire" element={<QuestionnairePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
