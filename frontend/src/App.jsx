import React, { useEffect, useMemo } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import { FAQ } from './components/home/FAQ';
import DynamicQuestionnaire from './components/DynamicQuestionnaire';
import ResultsPage from './components/ResultsPage';
import ErrorBoundary from './components/ErrorBoundary';
import {
  ClipboardIcon,
  SearchIcon,
  TargetIcon,
  ChartIcon,
  ClockIcon,
  ShieldIcon,
  MapIcon,
  ArrowRightIcon,
  LockIcon,
} from './icons';
import './styles/variables.css';
import './styles/animations.css';
import './App.css';

// ============ HOME PAGE ============

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50 overflow-hidden">

      {/* ── Hero Section ─────────────────────────────────────── */}
      <div className="relative">
        {/* Background blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-200 rounded-full opacity-20 blur-3xl"></div>
          <div className="absolute top-60 -left-20 w-60 h-60 bg-emerald-300 rounded-full opacity-20 blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-yellow-200 rounded-full opacity-10 blur-3xl"></div>
        </div>

        <div className="relative max-w-6xl mx-auto px-4 py-20 lg:py-32">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-semibold mb-8 animate-fade-in" role="status">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" aria-hidden="true"></span>
              Plus de 800 aides disponibles
            </div>

            {/* Titre principal */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 mb-6 animate-fade-in leading-tight">
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
                className="group relative inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-lg font-bold rounded-2xl shadow-xl shadow-green-500/25 hover:shadow-2xl hover:shadow-green-500/35 hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2 transition-all duration-300"
                aria-label="Commencer le questionnaire d'aides agricoles"
              >
                Commencer maintenant
                <span className="group-hover:translate-x-1 transition-transform duration-300">
                  <ArrowRightIcon />
                </span>
              </button>

              <p className="text-gray-500 text-sm flex items-center gap-2">
                <LockIcon />
                100% gratuit · Données non conservées
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Stats Section ────────────────────────────────────── */}
      <div className="relative max-w-5xl mx-auto px-4 py-16" aria-label="Chiffres clés">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {[
            { value: '800+', label: 'Aides analysées',    icon: <ChartIcon />, color: 'from-emerald-500 to-teal-500'  },
            { value: '5 min', label: 'Temps moyen',       icon: <ClockIcon />,  color: 'from-blue-500 to-cyan-500'    },
            { value: '100%', label: 'Gratuit',            icon: <ShieldIcon />, color: 'from-violet-500 to-purple-500' },
            { value: '13',    label: 'Régions couvertes', icon: <MapIcon />,    color: 'from-amber-500 to-orange-500'  },
          ].map((stat, i) => (
            <div
              key={i}
              className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 text-center shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 animate-fade-in"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className={`w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center text-white`}>
                {stat.icon}
              </div>
              <div className="text-3xl font-extrabold text-gray-900 leading-none">{stat.value}</div>
              <div className="text-xs text-gray-500 mt-1 font-medium uppercase tracking-wide">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── How It Works ─────────────────────────────────────── */}
      <div className="relative max-w-6xl mx-auto px-4 py-16" id="comment-ca-marche">
        <h2 className="text-3xl font-extrabold text-center text-gray-900 mb-4">
          Comment ça marche ?
        </h2>
        <p className="text-center text-gray-500 mb-14 max-w-xl mx-auto">
          Un processus simple en trois étapes pour accéder à toutes vos aides.
        </p>

        <div className="relative grid md:grid-cols-3 gap-8">
          {/* Connector line (desktop) */}
          <div className="hidden md:block absolute top-10 left-1/6 right-1/6 h-0.5 bg-gradient-to-r from-blue-400 via-green-400 to-orange-400 opacity-30 z-0" style={{left:'16.67%', right:'16.67%'}} aria-hidden="true"></div>

          {[
            {
              step: '01',
              icon: <ClipboardIcon />,
              title: 'Répondez au questionnaire',
              description: 'Quelques questions simples sur votre exploitation, vos productions et vos projets.',
              color: 'from-blue-500 to-cyan-500',
              bg: 'from-blue-50 to-cyan-50',
              border: 'border-blue-100',
            },
            {
              step: '02',
              icon: <SearchIcon />,
              title: 'Analyse intelligente',
              description: 'Notre algorithme compare votre profil avec plus de 800 aides disponibles.',
              color: 'from-green-500 to-emerald-500',
              bg: 'from-green-50 to-emerald-50',
              border: 'border-green-100',
            },
            {
              step: '03',
              icon: <TargetIcon />,
              title: 'Résultats personnalisés',
              description: 'Découvrez les aides auxquelles vous êtes éligible avec les montants estimés.',
              color: 'from-orange-500 to-amber-500',
              bg: 'from-orange-50 to-amber-50',
              border: 'border-orange-100',
            },
          ].map((feature, i) => (
            <div
              key={i}
              className={`relative bg-gradient-to-br ${feature.bg} border ${feature.border} rounded-3xl p-8 shadow-md hover:shadow-xl transition-all duration-300 group animate-fade-in z-10`}
              style={{ animationDelay: `${i * 150}ms` }}
            >
              {/* Step badge */}
              <div className={`absolute -top-4 left-8 px-3 py-1 bg-gradient-to-r ${feature.color} text-white text-xs font-bold rounded-full shadow-md`}>
                Étape {feature.step}
              </div>

              {/* Icon */}
              <div className={`w-16 h-16 mb-5 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-white shadow-lg group-hover:scale-105 group-hover:rotate-2 transition-transform duration-300`}>
                {feature.icon}
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── FAQ Section ──────────────────────────────────────── */}
      <FAQ />

      {/* ── CTA Final ────────────────────────────────────────── */}
      <div className="relative max-w-4xl mx-auto px-4 py-20">
        <div className="relative bg-gradient-to-br from-green-600 via-emerald-600 to-teal-600 rounded-3xl p-12 text-center text-white overflow-hidden shadow-2xl">
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-72 h-72 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" aria-hidden="true"></div>
          <div className="absolute bottom-0 left-0 w-52 h-52 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2" aria-hidden="true"></div>
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djZoNnYtNmgtNnptNiA2djZoNnYtNmgtNnptLTEyIDBoNnY2aC02di02em0xMiAwaDZ2NmgtNnptLTYtMTJoNnY2aC02di02em0xMiAwaDZ2NmgtNnptLTEyIDZoNnY2aC02di02em0xMi02aDZ2NmgtNnYtNnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-30" aria-hidden="true"></div>

          <div className="relative z-10">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/20 rounded-full text-sm font-semibold mb-6">
              <span className="w-2 h-2 bg-yellow-300 rounded-full animate-pulse" aria-hidden="true"></span>
              Commencez en 5 minutes
            </div>
            <h2 className="text-3xl md:text-4xl font-extrabold mb-4">
              Prêt à découvrir vos aides ?
            </h2>
            <p className="text-xl text-green-100 mb-8 max-w-xl mx-auto">
              Ne passez plus à côté des subventions qui vous sont destinées.
            </p>
            <button
              onClick={() => navigate('/questionnaire')}
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-green-700 text-lg font-bold rounded-2xl shadow-xl hover:shadow-2xl hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-green-600 transition-all duration-300"
              aria-label="Démarrer le questionnaire d'aides agricoles"
            >
              Démarrer le questionnaire
              <ArrowRightIcon />
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
      <ErrorBoundary
        fallbackMessage="Le questionnaire a rencontré un problème. Veuillez réessayer."
        onReset={() => window.location.reload()}
      >
        <DynamicQuestionnaire onComplete={handleComplete} />
      </ErrorBoundary>
    </div>
  );
}

// Page résultats
function ResultsRoute() {
  const navigate = useNavigate();
  
  const { results, profil } = useMemo(() => {
    try {
      const resultsStr = sessionStorage.getItem('matching_results');
      const profilStr = sessionStorage.getItem('user_profil');
      return {
        results: resultsStr ? JSON.parse(resultsStr) : null,
        profil: profilStr ? JSON.parse(profilStr) : null,
      };
    } catch (error) {
      console.error('Error parsing sessionStorage data:', error);
      return { results: null, profil: null };
    }
  }, []); // The sessionStorage is read once on mount; no reactive dependencies needed

  useEffect(() => {
    if (!results) {
      navigate('/questionnaire');
    }
  }, [results, navigate]);

  if (!results) {
    return null;
  }

  return (
    <ErrorBoundary
      fallbackMessage="Une erreur est survenue lors de l'affichage des résultats."
      onReset={() => navigate('/questionnaire')}
    >
      <ResultsPage 
        results={results} 
        profil={profil}
        onRestart={() => {
          sessionStorage.removeItem('matching_results');
          sessionStorage.removeItem('user_profil');
          navigate('/questionnaire');
        }}
      />
    </ErrorBoundary>
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
