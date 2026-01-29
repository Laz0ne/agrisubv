import { useState, useEffect } from 'react';
import QuestionSelect from './QuestionSelect';
import QuestionMultiSelect from './QuestionMultiSelect';
import QuestionNumber from './QuestionNumber';
import QuestionRadio from './QuestionRadio';
import QuestionText from './QuestionText';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://agrisubv-backend.onrender.com/api';

// Skeleton loader component
function QuestionnaireSkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8 animate-fade-in">
      <div className="mb-8">
        <div className="skeleton h-8 w-64 mb-4"></div>
        <div className="skeleton h-2 w-full mb-2"></div>
        <div className="skeleton h-4 w-32"></div>
      </div>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="skeleton h-6 w-48 mb-4"></div>
        <div className="skeleton h-4 w-full mb-6"></div>
        
        <div className="space-y-6">
          {[1, 2, 3].map(i => (
            <div key={i}>
              <div className="skeleton h-4 w-3/4 mb-2"></div>
              <div className="skeleton h-12 w-full"></div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="flex justify-between">
        <div className="skeleton h-12 w-32"></div>
        <div className="skeleton h-12 w-32"></div>
      </div>
    </div>
  );
}

// Config questionnaire en fallback (intégré pour éviter l'attente réseau)
const FALLBACK_CONFIG = {
  version: "1.0",
  metadata: {
    estimated_time_minutes: 5
  },
  sections: [
    {
      id: "identite",
      titre: "Votre exploitation",
      description: "Informations générales sur votre exploitation agricole",
      ordre: 1,
      questions: [
        {
          id: "region",
          type: "select",
          label: "Dans quelle région est située votre exploitation ?",
          placeholder: "Sélectionnez votre région",
          required: true,
          options: [
            {value: "Auvergne-Rhône-Alpes", label: "Auvergne-Rhône-Alpes"},
            {value: "Bourgogne-Franche-Comté", label: "Bourgogne-Franche-Comté"},
            {value: "Bretagne", label: "Bretagne"},
            {value: "Centre-Val de Loire", label: "Centre-Val de Loire"},
            {value: "Corse", label: "Corse"},
            {value: "Grand Est", label: "Grand Est"},
            {value: "Hauts-de-France", label: "Hauts-de-France"},
            {value: "Île-de-France", label: "Île-de-France"},
            {value: "Normandie", label: "Normandie"},
            {value: "Nouvelle-Aquitaine", label: "Nouvelle-Aquitaine"},
            {value: "Occitanie", label: "Occitanie"},
            {value: "Pays de la Loire", label: "Pays de la Loire"},
            {value: "Provence-Alpes-Côte d'Azur", label: "Provence-Alpes-Côte d'Azur"}
          ]
        },
        {
          id: "departement",
          type: "text",
          label: "Quel est votre département ?",
          placeholder: "Ex: 35, 44, 56...",
          required: true,
          validation: { pattern: "^[0-9]{2,3}$" }
        },
        {
          id: "statut_juridique",
          type: "select",
          label: "Quel est le statut juridique de votre exploitation ?",
          required: true,
          options: [
            {value: "Exploitation individuelle", label: "Exploitation individuelle"},
            {value: "EARL", label: "EARL"},
            {value: "GAEC", label: "GAEC"},
            {value: "SCEA", label: "SCEA"},
            {value: "SA", label: "SA"},
            {value: "CUMA", label: "CUMA"},
            {value: "Coopérative", label: "Coopérative"},
            {value: "Autre", label: "Autre"}
          ]
        }
      ]
    },
    {
      id: "exploitation",
      titre: "Caractéristiques",
      description: "Surface et productions",
      ordre: 2,
      questions: [
        {
          id: "sau_totale",
          type: "number",
          label: "Surface Agricole Utile (SAU) totale ?",
          placeholder: "En hectares",
          unite: "ha",
          required: true,
          validation: { min: 0, max: 10000 }
        },
        {
          id: "productions",
          type: "multiselect",
          label: "Quelles sont vos productions principales ?",
          required: true,
          min_selections: 1,
          options: [
            {value: "Céréales", label: "Céréales"},
            {value: "Grandes cultures", label: "Grandes cultures"},
            {value: "Élevage bovin", label: "Élevage bovin"},
            {value: "Élevage ovin", label: "Élevage ovin"},
            {value: "Élevage porcin", label: "Élevage porcin"},
            {value: "Élevage avicole", label: "Élevage avicole"},
            {value: "Élevage laitier", label: "Élevage laitier"},
            {value: "Viticulture", label: "Viticulture"},
            {value: "Maraîchage", label: "Maraîchage"},
            {value: "Arboriculture", label: "Arboriculture"},
            {value: "Horticulture", label: "Horticulture"},
            {value: "Apiculture", label: "Apiculture"}
          ]
        }
      ]
    },
    {
      id: "profil",
      titre: "Votre profil",
      description: "Informations sur vous",
      ordre: 3,
      questions: [
        {
          id: "age",
          type: "number",
          label: "Quel est votre âge ?",
          required: false,
          validation: { min: 18, max: 99 }
        },
        {
          id: "jeune_agriculteur",
          type: "radio",
          label: "Êtes-vous reconnu Jeune Agriculteur ?",
          required: false,
          visible_if: { question_id: "age", operator: "<", value: 45 },
          options: [
            {value: true, label: "Oui"},
            {value: false, label: "Non"}
          ]
        }
      ]
    },
    {
      id: "labels",
      titre: "Labels et certifications",
      description: "Vos engagements",
      ordre: 4,
      importance: "CRITIQUE",
      questions: [
        {
          id: "label_bio",
          type: "select",
          label: "Êtes-vous en agriculture biologique ?",
          required: true,
          help_text: "⭐ 80% des aides concernent le bio !",
          options: [
            {value: "certifie", label: "Oui, certifié AB"},
            {value: "conversion", label: "En conversion"},
            {value: "non", label: "Non, conventionnel"}
          ]
        },
        {
          id: "autres_labels",
          type: "multiselect",
          label: "Autres labels (optionnel)",
          required: false,
          options: [
            {value: "HVE", label: "HVE"},
            {value: "Label Rouge", label: "Label Rouge"},
            {value: "AOC", label: "AOC/AOP"},
            {value: "IGP", label: "IGP"}
          ]
        }
      ]
    },
    {
      id: "projets",
      titre: "Vos projets",
      description: "Projets actuels ou à venir",
      ordre: 5,
      questions: [
        {
          id: "types_projets",
          type: "multiselect",
          label: "Quels sont vos projets ?",
          required: true,
          min_selections: 1,
          options: [
            {value: "Installation", label: "🌱 Installation"},
            {value: "Modernisation", label: "🔧 Modernisation"},
            {value: "Diversification", label: "🌈 Diversification"},
            {value: "Conversion bio", label: "🌿 Conversion bio"},
            {value: "Énergie", label: "⚡ Transition énergétique"},
            {value: "Matériel", label: "🚜 Investissement matériel"},
            {value: "Bâtiment", label: "🏗️ Construction/rénovation"},
            {value: "Irrigation", label: "💧 Irrigation"},
            {value: "Bien-être animal", label: "🐄 Bien-être animal"},
            {value: "Commercialisation", label: "🛒 Circuits courts"},
            {value: "Numérique", label: "💻 Numérique"},
            {value: "Formation", label: "📚 Formation"}
          ]
        }
      ]
    }
  ],
  mapping_to_profil_v2: {
    region: "region",
    departement: "departement",
    statut_juridique: "statut_juridique",
    sau_totale: "sau_totale",
    productions: "productions",
    age: "age",
    jeune_agriculteur: "jeune_agriculteur",
    label_bio: "label_bio",
    autres_labels: "labels",
    types_projets: "projets_en_cours"
  }
};

export default function DynamicQuestionnaire({ onComplete }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Charger la config avec fallback immédiat
  useEffect(() => {
    // Utiliser le fallback immédiatement pour affichage rapide
    setConfig(FALLBACK_CONFIG);
    setLoading(false);
    
    // Puis essayer de charger la config du serveur en arrière-plan
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // Timeout 5s
    
    fetch(`${API_BASE_URL}/questionnaire/config`, { signal: controller.signal })
      .then(res => res.json())
      .then(data => {
        clearTimeout(timeoutId);
        if (data.status === 'success' && data.config) {
          setConfig(data.config);
        }
      })
      .catch(() => {
        // Garder le fallback en cas d'erreur
        clearTimeout(timeoutId);
      });
    
    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, []);

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
    if (errors[questionId]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  };

  const isQuestionVisible = (question) => {
    if (!question.visible_if) return true;
    const { question_id, operator, value, values } = question.visible_if;
    const triggerValue = answers[question_id];
    if (triggerValue === undefined || triggerValue === null) return false;
    switch (operator) {
      case '<': return triggerValue < value;
      case '>': return triggerValue > value;
      case '==': return triggerValue === value;
      case '!=': return triggerValue !== value;
      case 'in': return values?.includes(triggerValue);
      default: return true;
    }
  };

  const validateSection = (section) => {
    const newErrors = {};
    section.questions.forEach(question => {
      if (!isQuestionVisible(question)) return;
      const answer = answers[question.id];
      
      // Check if required
      if (question.required && (answer === undefined || answer === null || answer === '' || (Array.isArray(answer) && answer.length === 0))) {
        newErrors[question.id] = 'Ce champ est requis';
        return;
      }
      
      // Validation specific to type
      if (answer !== undefined && answer !== null && answer !== '') {
        // Number validation
        if (question.type === 'number' && question.validation) {
          const numValue = parseFloat(answer);
          if (question.validation.min !== undefined && numValue < question.validation.min) {
            newErrors[question.id] = `La valeur doit être supérieure ou égale à ${question.validation.min}`;
          }
          if (question.validation.max !== undefined && numValue > question.validation.max) {
            newErrors[question.id] = `La valeur doit être inférieure ou égale à ${question.validation.max}`;
          }
        }
        
        // Text validation (regex)
        if (question.type === 'text' && question.validation?.pattern) {
          const regex = new RegExp(question.validation.pattern);
          if (!regex.test(answer)) {
            newErrors[question.id] = question.validation.error_message || 'Format invalide';
          }
        }
        
        // Multiselect validation
        if (question.type === 'multiselect' && Array.isArray(answer)) {
          if (question.min_selections && answer.length < question.min_selections) {
            newErrors[question.id] = `Sélectionnez au moins ${question.min_selections} option(s)`;
          }
          if (question.max_selections && answer.length > question.max_selections) {
            newErrors[question.id] = `Sélectionnez au maximum ${question.max_selections} option(s)`;
          }
        }
      }
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

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

  const handlePrevious = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const mapping = config.mapping_to_profil_v2 || {};
      const profil = { profil_id: `profil_${Date.now()}` };
      
      Object.keys(mapping).forEach(questionId => {
        const backendField = mapping[questionId];
        const value = answers[questionId];
        if (value !== undefined && value !== null) {
          profil[backendField] = value;
        }
      });
      
      // Gérer label_bio
      if (answers.label_bio === 'certifie' || answers.label_bio === 'conversion') {
        profil.label_bio = true;
        if (!profil.labels) profil.labels = [];
        // Avoid duplicates
        if (!profil.labels.includes('Agriculture Biologique')) {
          profil.labels.push('Agriculture Biologique');
        }
      } else {
        profil.label_bio = false;
      }

      const response = await fetch(`${API_BASE_URL}/matching`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profil)
      });

      const result = await response.json();
      if (response.ok) {
        onComplete(result, profil);
      } else {
        alert('Erreur lors du calcul. Veuillez réessayer.');
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur de connexion. Veuillez réessayer.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderQuestion = (question) => {
    if (!isQuestionVisible(question)) return null;
    const commonProps = {
      question,
      value: answers[question.id],
      onChange: (value) => handleAnswerChange(question.id, value),
      error: errors[question.id]
    };
    switch (question.type) {
      case 'select': return <QuestionSelect key={question.id} {...commonProps} />;
      case 'multiselect': return <QuestionMultiSelect key={question.id} {...commonProps} />;
      case 'number': return <QuestionNumber key={question.id} {...commonProps} />;
      case 'radio': return <QuestionRadio key={question.id} {...commonProps} />;
      case 'text': return <QuestionText key={question.id} {...commonProps} />;
      default: return null;
    }
  };

  if (loading) {
    return <QuestionnaireSkeleton />;
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Erreur de chargement</p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  const currentSection = config.sections[currentSectionIndex];
  const progress = ((currentSectionIndex + 1) / config.sections.length) * 100;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 animate-fade-in">
      {/* Header avec progression */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-3">
          <h1 className="text-2xl font-bold text-gray-900">
            🌾 Trouvez vos aides
          </h1>
          <span className="badge badge-info">
            {currentSectionIndex + 1} / {config.sections.length}
          </span>
        </div>
        
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
        </div>
        
        <p className="mt-2 text-sm text-gray-500">
          ⏱️ Environ {config.metadata?.estimated_time_minutes || 5} minutes
        </p>
      </div>

      {/* Section courante */}
      <div className="card p-6 mb-6 animate-slide-in" key={currentSection.id}>
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            {currentSection.titre}
            {currentSection.importance === 'CRITIQUE' && (
              <span className="badge badge-danger">⭐ Important</span>
            )}
          </h2>
          {currentSection.description && (
            <p className="mt-1 text-gray-600">{currentSection.description}</p>
          )}
        </div>

        <div className="space-y-6">
          {currentSection.questions.map(question => renderQuestion(question))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrevious}
          disabled={currentSectionIndex === 0}
          className={`btn ${currentSectionIndex === 0 ? 'opacity-50 cursor-not-allowed bg-gray-200' : 'btn-secondary'}`}
        >
          ← Précédent
        </button>

        <button
          onClick={handleNext}
          disabled={submitting}
          className="btn btn-primary"
        >
          {submitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Calcul...
            </>
          ) : currentSectionIndex === config.sections.length - 1 ? (
            'Voir mes aides 🚀'
          ) : (
            'Suivant →'
          )}
        </button>
      </div>

      {/* Erreurs */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
          <p className="text-red-800 font-medium">
            ⚠️ Veuillez corriger les erreurs avant de continuer.
          </p>
        </div>
      )}
    </div>
  );
}
