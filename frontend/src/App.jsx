import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import DynamicQuestionnaire from './components/DynamicQuestionnaire';
import ResultsPage from './components/ResultsPage';
import './styles/variables.css';
import './styles/animations.css';
import './App.css';

// Page d'accueil simplifiée
function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
          🌾 Trouvez vos aides agricoles
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Répondez à quelques questions et découvrez les aides auxquelles vous êtes éligible parmi plus de 400 dispositifs.
        </p>
        <button
          onClick={() => navigate('/questionnaire')}
          className="px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-lg hover:bg-green-700 transition-colors shadow-lg"
        >
          Commencer le questionnaire →
        </button>
        <p className="mt-4 text-sm text-gray-500">
          ⏱️ Environ 5 minutes • 🔒 Données non conservées
        </p>
      </div>
    </div>
  );
}

// Page questionnaire
function QuestionnairePage() {
  const navigate = useNavigate();
  
  const handleComplete = (results, profil) => {
    // Stocker les résultats et naviguer
    sessionStorage.setItem('matching_results', JSON.stringify(results));
    sessionStorage.setItem('user_profil', JSON.stringify(profil));
    navigate('/resultats');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <DynamicQuestionnaire onComplete={handleComplete} />
    </div>
  );
}

// Page résultats
function ResultatsPage() {
  const navigate = useNavigate();
  const results = JSON.parse(sessionStorage.getItem('matching_results') || 'null');
  const profil = JSON.parse(sessionStorage.getItem('user_profil') || 'null');

  if (!results) {
    navigate('/questionnaire');
    return null;
  }

  return (
    <ResultsPage 
      results={results} 
      profil={profil}
      onRestart={() => {
        sessionStorage.clear();
        navigate('/questionnaire');
      }}
    />
  );
}

// App principale
function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/questionnaire" element={<QuestionnairePage />} />
            <Route path="/resultats" element={<ResultatsPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
