import React, { useEffect } from 'react';
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
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50 overflow-hidden">
      {/* Hero Section avec motif de fond */}
      <div className="relative">
        {/* Motif décoratif */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-200 rounded-full opacity-20 blur-3xl"></div>
          <div className="absolute top-60 -left-20 w-60 h-60 bg-emerald-300 rounded-full opacity-20 blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-yellow-200 rounded-full opacity-10 blur-3xl"></div>
        </div>
        
        <div className="relative max-w-6xl mx-auto px-4 py-20 lg:py-32">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium mb-8 animate-fade-in">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Plus de 800 aides disponibles
            </div>
            
            {/* Titre principal */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 mb-6 animate-fade-in">
              Trouvez vos
              <span className="block bg-gradient-to-r from-green-600 via-emerald-500 to-teal-500 bg-clip-text text-transparent">
                aides agricoles
              </span>
            </h1>
            
            {/* Sous-titre */}
            <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-10 animate-fade-in animation-delay-100">
              Répondez à quelques questions et découvrez en <strong>5 minutes</strong> toutes les subventions auxquelles vous avez droit.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in animation-delay-200">
              <button
                onClick={() => navigate('/questionnaire')}
                className="group relative px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-lg font-bold rounded-2xl shadow-xl shadow-green-500/30 hover:shadow-2xl hover:shadow-green-500/40 transform hover:-translate-y-1 transition-all duration-300"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Commencer maintenant
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-green-700 to-emerald-700 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </button>
              
              <p className="text-gray-500 text-sm flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                100% gratuit • Données non conservées
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="relative max-w-5xl mx-auto px-4 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { value: '800+', label: 'Aides analysées', icon: '📊' },
            { value: '5 min', label: 'Temps moyen', icon: '⏱️' },
            { value: '100%', label: 'Gratuit', icon: '🎁' },
            { value: '13', label: 'Régions couvertes', icon: '🗺️' },
          ].map((stat, i) => (
            <div 
              key={i}
              className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 text-center shadow-lg shadow-gray-100 hover:shadow-xl transition-shadow animate-fade-in"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="text-3xl mb-2">{stat.icon}</div>
              <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div className="relative max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Comment ça marche ?
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              step: '01',
              icon: '📝',
              title: 'Répondez au questionnaire',
              description: 'Quelques questions simples sur votre exploitation, vos productions et vos projets.',
              color: 'from-blue-500 to-cyan-500'
            },
            {
              step: '02',
              icon: '🔍',
              title: 'Analyse intelligente',
              description: 'Notre algorithme compare votre profil avec plus de 800 aides disponibles.',
              color: 'from-green-500 to-emerald-500'
            },
            {
              step: '03',
              icon: '🎯',
              title: 'Résultats personnalisés',
              description: 'Découvrez les aides auxquelles vous êtes éligible avec les montants estimés.',
              color: 'from-orange-500 to-amber-500'
            }
          ].map((feature, i) => (
            <div 
              key={i}
              className="relative bg-white rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 group animate-fade-in"
              style={{ animationDelay: `${i * 150}ms` }}
            >
              {/* Numéro de l'étape */}
              <div className={`absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center text-white font-bold shadow-lg`}>
                {feature.step}
              </div>
              
              {/* Icône */}
              <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {feature.title}
              </h3>
              
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Final */}
      <div className="relative max-w-4xl mx-auto px-4 py-20">
        <div className="relative bg-gradient-to-r from-green-600 to-emerald-600 rounded-3xl p-12 text-center text-white overflow-hidden">
          {/* Motif décoratif */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2"></div>
          
          <div className="relative">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Prêt à découvrir vos aides ?
            </h2>
            <p className="text-xl text-green-100 mb-8">
              Ne passez plus à côté des subventions qui vous sont destinées.
            </p>
            <button
              onClick={() => navigate('/questionnaire')}
              className="px-8 py-4 bg-white text-green-600 text-lg font-bold rounded-2xl shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300"
            >
              Démarrer le questionnaire →
            </button>
          </div>
        </div>
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
function ResultsRoute() {
  const navigate = useNavigate();
  
  let results = null;
  let profil = null;
  
  try {
    const resultsStr = sessionStorage.getItem('matching_results');
    const profilStr = sessionStorage.getItem('user_profil');
    results = resultsStr ? JSON.parse(resultsStr) : null;
    profil = profilStr ? JSON.parse(profilStr) : null;
  } catch (error) {
    console.error('Error parsing sessionStorage data:', error);
    results = null;
    profil = null;
  }

  useEffect(() => {
    if (!results) {
      navigate('/questionnaire');
    }
  }, [results, navigate]);

  if (!results) {
    return null;
  }

  return (
    <ResultsPage 
      results={results} 
      profil={profil}
      onRestart={() => {
        sessionStorage.removeItem('matching_results');
        sessionStorage.removeItem('user_profil');
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
            <Route path="/resultats" element={<ResultsRoute />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
