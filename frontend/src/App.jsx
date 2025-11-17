import { useState } from 'react';
import DynamicQuestionnaire from './components/DynamicQuestionnaire';
import ResultsPage from './components/ResultsPage';
import './App.css';

function App() {
  const [step, setStep] = useState('welcome'); // 'welcome', 'questionnaire', 'results'
  const [results, setResults] = useState(null);
  const [profil, setProfil] = useState(null);

  const handleStart = () => {
    setStep('questionnaire');
  };

  const handleComplete = (matchingResults, userProfil) => {
    setResults(matchingResults);
    setProfil(userProfil);
    setStep('results');
  };

  const handleRestart = () => {
    setResults(null);
    setProfil(null);
    setStep('welcome');
  };

  if (step === 'welcome') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-2xl text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            🌾 AgriSubv
          </h1>
          <p className="text-xl text-gray-700 mb-8">
            Trouvez toutes les aides agricoles auxquelles vous êtes éligible en 5 minutes
          </p>
          <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="text-4xl mb-2">📋</div>
                <div className="font-semibold">15 questions</div>
                <div className="text-sm text-gray-600">Questionnaire simple</div>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">🎯</div>
                <div className="font-semibold">507 aides</div>
                <div className="text-sm text-gray-600">Base complète</div>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">⏱️</div>
                <div className="font-semibold">5 minutes</div>
                <div className="text-sm text-gray-600">Résultats rapides</div>
              </div>
            </div>
            <button
              onClick={handleStart}
              className="w-full bg-green-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-green-700 transition-colors shadow-lg"
            >
              Commencer le questionnaire 🚀
            </button>
          </div>
          <p className="text-sm text-gray-600">
            ⭐ Basé sur l'analyse de 507 aides agricoles • 80% des aides concernent le bio
          </p>
        </div>
      </div>
    );
  }

  if (step === 'questionnaire') {
    return <DynamicQuestionnaire onComplete={handleComplete} />;
  }

  if (step === 'results') {
    return <ResultsPage results={results} profil={profil} onRestart={handleRestart} />;
  }

  return null;
}

export default App;
