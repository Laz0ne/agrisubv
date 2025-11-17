import { useState, useEffect } from 'react';
import QuestionSelect from './QuestionSelect';
import QuestionMultiSelect from './QuestionMultiSelect';
import QuestionNumber from './QuestionNumber';
import QuestionRadio from './QuestionRadio';
import QuestionText from './QuestionText';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://agrisubv-backend.onrender.com/api';

export default function DynamicQuestionnaire({ onComplete }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Charger la configuration du questionnaire
  useEffect(() => {
    fetch(`${API_BASE_URL}/questionnaire/config`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setConfig(data.config);
        } else {
          console.error('Erreur chargement config:', data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Erreur fetch config:', err);
        setLoading(false);
      });
  }, []);

  // Mettre à jour une réponse
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
    
    // Effacer l'erreur si elle existe
    if (errors[questionId]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  };

  // Vérifier si une question doit être visible (logique conditionnelle)
  const isQuestionVisible = (question) => {
    if (!question.visible_if) return true;

    const { question_id, operator, value, values } = question.visible_if;
    const triggerValue = answers[question_id];

    if (triggerValue === undefined || triggerValue === null) return false;

    switch (operator) {
      case '<':
        return triggerValue < value;
      case '>':
        return triggerValue > value;
      case '==':
        return triggerValue === value;
      case '!=':
        return triggerValue !== value;
      case 'in':
        return values.includes(triggerValue);
      default:
        return true;
    }
  };

  // Valider une section
  const validateSection = (section) => {
    const newErrors = {};
    
    section.questions.forEach(question => {
      if (!isQuestionVisible(question)) return;
      
      const answer = answers[question.id];
      
      // Vérifier si requis
      if (question.required && (answer === undefined || answer === null || answer === '')) {
        newErrors[question.id] = 'Ce champ est requis';
        return;
      }

      // Validation spécifique selon le type
      if (answer !== undefined && answer !== null && answer !== '') {
        // Validation pour les nombres
        if (question.type === 'number' && question.validation) {
          const numValue = parseFloat(answer);
          if (question.validation.min !== undefined && numValue < question.validation.min) {
            newErrors[question.id] = `La valeur doit être supérieure ou égale à ${question.validation.min}`;
          }
          if (question.validation.max !== undefined && numValue > question.validation.max) {
            newErrors[question.id] = `La valeur doit être inférieure ou égale à ${question.validation.max}`;
          }
        }

        // Validation pour les textes (regex)
        if (question.type === 'text' && question.validation?.pattern) {
          const regex = new RegExp(question.validation.pattern);
          if (!regex.test(answer)) {
            newErrors[question.id] = question.validation.error_message || 'Format invalide';
          }
        }

        // Validation pour les multiselect
        if (question.type === 'multiselect') {
          if (question.min_selections && answer.length < question.min_selections) {
            newErrors[question.id] = `Sélectionnez au moins ${question.min_selections} option(s)`;
          }
          if (question.max_selections && answer.length > question.max_selections) {
            newErrors[question.id] = `Sélectionnez au maximum ${question.max_selections} option(s)`;
          }
        }
      }
    });

    // Validation croisée (ex: sau_bio <= sau_totale)
    if (config.validation_rules?.cross_field) {
      config.validation_rules.cross_field.forEach(rule => {
        if (rule.rule === 'sau_bio <= sau_totale') {
          const sauBio = parseFloat(answers.sau_bio);
          const sauTotale = parseFloat(answers.sau_totale);
          if (sauBio && sauTotale && sauBio > sauTotale) {
            newErrors.sau_bio = rule.error_message;
          }
        }
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Passer à la section suivante
  const handleNext = () => {
    const currentSection = config.sections[currentSectionIndex];
    
    if (validateSection(currentSection)) {
      if (currentSectionIndex < config.sections.length - 1) {
        setCurrentSectionIndex(prev => prev + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        handleSubmit();
      }
    }
  };

  // Retour à la section précédente
  const handlePrevious = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Soumettre le profil au backend
  const handleSubmit = async () => {
    setSubmitting(true);

    try {
      // Construire le profil selon le mapping
      const mapping = config.mapping_to_profil_v2;
      const profil = {};

      Object.keys(mapping).forEach(questionId => {
        const backendField = mapping[questionId];
        const value = answers[questionId];
        
        if (value !== undefined && value !== null) {
          profil[backendField] = value;
        }
      });

      // Ajouter les champs calculés
      profil.profil_id = `profil_${Date.now()}`;
      profil.created_at = new Date().toISOString();
      
      // Convertir label_bio en boolean
      if (answers.label_bio === 'certifie' || answers.label_bio === 'conversion') {
        profil.label_bio = true;
      } else {
        profil.label_bio = false;
      }

      // Envoyer au backend pour matching
      const response = await fetch(`${API_BASE_URL}/matching`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profil)
      });

      const result = await response.json();

      if (response.ok) {
        onComplete(result, profil);
      } else {
        console.error('Erreur matching:', result);
        alert('Une erreur est survenue lors du calcul des aides. Veuillez réessayer.');
      }
    } catch (error) {
      console.error('Erreur soumission:', error);
      alert('Erreur de connexion au serveur. Veuillez réessayer.');
    } finally {
      setSubmitting(false);
    }
  };

  // Rendu du composant de question selon son type
  const renderQuestion = (question) => {
    if (!isQuestionVisible(question)) return null;

    const commonProps = {
      question,
      value: answers[question.id],
      onChange: (value) => handleAnswerChange(question.id, value),
      error: errors[question.id]
    };

    switch (question.type) {
      case 'select':
        return <QuestionSelect key={question.id} {...commonProps} />;
      case 'multiselect':
        return <QuestionMultiSelect key={question.id} {...commonProps} />;
      case 'number':
        return <QuestionNumber key={question.id} {...commonProps} />;
      case 'radio':
        return <QuestionRadio key={question.id} {...commonProps} />;
      case 'text':
        return <QuestionText key={question.id} {...commonProps} />;
      default:
        return <div key={question.id}>Type de question non supporté: {question.type}</div>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement du questionnaire...</p>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <p>Erreur de chargement du questionnaire.</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  const currentSection = config.sections[currentSectionIndex];
  const progress = ((currentSectionIndex + 1) / config.sections.length) * 100;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* En-tête avec progression */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-2xl font-bold text-gray-900">
            Trouvez vos aides agricoles
          </h1>
          <span className="text-sm text-gray-500">
            Section {currentSectionIndex + 1} / {config.sections.length}
          </span>
        </div>
        
        {/* Barre de progression */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        
        <p className="mt-2 text-sm text-gray-600">
          ⏱️ Temps estimé : {config.metadata.estimated_time_minutes} minutes
        </p>
      </div>

      {/* Section actuelle */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            {currentSection.titre}
            {currentSection.importance === 'CRITIQUE' && (
              <span className="ml-2 px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                ⭐ IMPORTANT
              </span>
            )}
          </h2>
          {currentSection.description && (
            <p className="mt-2 text-gray-600">{currentSection.description}</p>
          )}
        </div>

        {/* Questions de la section */}
        <div className="space-y-6">
          {currentSection.questions.map(question => renderQuestion(question))}
        </div>
      </div>

      {/* Boutons de navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrevious}
          disabled={currentSectionIndex === 0}
          className={`px-6 py-3 rounded-lg font-medium transition-colors ${
            currentSectionIndex === 0
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          ← Précédent
        </button>

        <button
          onClick={handleNext}
          disabled={submitting}
          className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
        >
          {submitting ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Calcul en cours...
            </>
          ) : currentSectionIndex === config.sections.length - 1 ? (
            'Voir mes aides 🚀'
          ) : (
            'Suivant →'
          )}
        </button>
      </div>

      {/* Indicateur d'erreurs */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">
            ⚠️ Veuillez corriger les erreurs ci-dessus avant de continuer.
          </p>
        </div>
      )}
    </div>
  );
}
