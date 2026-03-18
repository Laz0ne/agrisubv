import { useState, useEffect } from 'react';
import QuestionSelect from './QuestionSelect';
import QuestionMultiSelect from './QuestionMultiSelect';
import QuestionNumber from './QuestionNumber';
import QuestionRadio from './QuestionRadio';
import QuestionText from './QuestionText';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://agrisubv-backend.onrender.com/api';

const CONFIG_FETCH_TIMEOUT_MS = 8000;
const MAX_ADAPTIVE_QUESTIONS = 12;
const QUASI_ELIGIBLE_SCORE_THRESHOLD = 40;

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
  // mode: null = initializing, 'adaptive' = adaptive engine, 'static' = static sections
  const [mode, setMode] = useState(null);
  const [loading, setLoading] = useState(true);

  // ── Static mode state ────────────────────────────────────────────────────
  const [config, setConfig] = useState(FALLBACK_CONFIG);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [errors, setErrors] = useState({});

  // ── Adaptive mode state ──────────────────────────────────────────────────
  const [adaptiveState, setAdaptiveState] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [adaptiveAnswer, setAdaptiveAnswer] = useState(null);
  const [adaptiveError, setAdaptiveError] = useState(null);
  const [adaptiveDone, setAdaptiveDone] = useState(false);

  const [submitting, setSubmitting] = useState(false);

  // ── Initialization ───────────────────────────────────────────────────────
  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG_FETCH_TIMEOUT_MS);

    const init = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/questionnaire/config`, {
          signal: controller.signal,
        });
        const data = await res.json();

        if (data.status === 'success' && data.config?.engine === 'dynamic') {
          // Adaptive engine available — reconstruct initial state from config response
          const initialState = {
            session_id: data.config.session_id,
            answers: {},
            remaining_aids_count: data.config.total_aids,
            total_aids_count: data.config.total_aids,
            questions_asked: [],
            is_complete: false,
          };
          setAdaptiveState(initialState);
          setCurrentQuestion(data.config.first_question || null);
          setMode('adaptive');
        } else if (data.status === 'success' && data.config?.sections) {
          // Static config with sections
          setConfig(data.config);
          setMode('static');
        } else {
          // Unknown format or error — use FALLBACK_CONFIG
          setMode('static');
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          // Network error: fall back to static FALLBACK_CONFIG
          console.warn('Questionnaire init failed, using fallback:', err);
        }
        setMode('static');
      } finally {
        clearTimeout(timeoutId);
        setLoading(false);
      }
    };

    init();
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
      case 'in': return Array.isArray(values) && values.includes(triggerValue);
      default: return true;
    }
  };

  const validateSection = (section) => {
    const newErrors = {};
    (section.questions || []).filter(q => q != null).forEach(question => {
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

  // ── Adaptive mode handlers ───────────────────────────────────────────────

  const handleAdaptiveNext = async () => {
    const isAnswerEmpty =
      adaptiveAnswer === null ||
      adaptiveAnswer === undefined ||
      adaptiveAnswer === '' ||
      (Array.isArray(adaptiveAnswer) && adaptiveAnswer.length === 0);

    if (isAnswerEmpty && currentQuestion?.is_blocking) {
      setAdaptiveError('Ce champ est requis');
      return;
    }

    setSubmitting(true);
    setAdaptiveError(null);

    try {
      // Submit the answer
      const answerRes = await fetch(`${API_BASE_URL}/questionnaire/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          state: adaptiveState,
          criterion_id: currentQuestion.criterion_id,
          value: isAnswerEmpty ? null : adaptiveAnswer,
        }),
      });
      const answerData = await answerRes.json();

      if (answerData.status !== 'success') throw new Error('Erreur soumission réponse');

      const newState = answerData.state;
      setAdaptiveState(newState);

      if (newState.is_complete) {
        setAdaptiveDone(true);
        setCurrentQuestion(null);
        return;
      }

      // Get next question
      const nextRes = await fetch(`${API_BASE_URL}/questionnaire/next`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: newState }),
      });
      const nextData = await nextRes.json();

      if (nextData.status !== 'success') throw new Error('Erreur récupération question');

      const nextQ = nextData.question;
      if (!nextQ || nextQ.is_complete) {
        setAdaptiveDone(true);
        setCurrentQuestion(null);
      } else {
        setCurrentQuestion(nextQ);
        setAdaptiveAnswer(null);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err) {
      console.error('Erreur adaptive:', err);
      setAdaptiveError('Erreur de connexion. Veuillez réessayer.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAdaptiveResults = async () => {
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/questionnaire/results`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: adaptiveState }),
      });
      const data = await res.json();

      if (res.ok && data.status === 'success') {
        // Normalize to the format expected by ResultsPage
        const results = {
          ...data,
          total_aides: data.stats?.total_evaluated || 0,
          aides_eligibles: data.stats?.eligible_count || 0,
          aides_quasi_eligibles:
            (data.resultats || []).filter(r => !r.eligible && r.score >= QUASI_ELIGIBLE_SCORE_THRESHOLD).length,
          montant_total_estime_min: 0,
          montant_total_estime_max: 0,
        };
        onComplete(results, data.profil);
      } else {
        alert('Erreur lors du calcul. Veuillez réessayer.');
      }
    } catch (err) {
      console.error('Erreur résultats:', err);
      alert('Erreur de connexion. Veuillez réessayer.');
    } finally {
      setSubmitting(false);
    }
  };

  // ── Render: loading ──────────────────────────────────────────────────────

  if (loading || mode === null) {
    return <QuestionnaireSkeleton />;
  }

  // ── Render: adaptive mode ────────────────────────────────────────────────

  if (mode === 'adaptive') {
    const questionsAnswered = adaptiveState?.questions_asked?.length || 0;
    const remainingAids = adaptiveState?.remaining_aids_count || 0;
    const totalAids = adaptiveState?.total_aids_count || 0;
    const progress = Math.max(5, Math.min((questionsAnswered / MAX_ADAPTIVE_QUESTIONS) * 100, 100));

    // Normalize adaptive question to the format expected by question components
    const normalizeAdaptiveQuestion = (q) => {
      if (!q) return null;
      let type = q.question_type === 'boolean' ? 'radio' : q.question_type;
      let options =
        q.question_type === 'boolean'
          ? [{ value: true, label: 'Oui' }, { value: false, label: 'Non' }]
          : q.options || [];
      // Fall back to text input when select/multiselect has no options
      if ((type === 'select' || type === 'multiselect') && options.length === 0) {
        type = 'text';
        options = [];
      }
      return {
        id: q.criterion_id,
        type,
        label: q.label,
        required: q.is_blocking || false,
        help_text: q.help_text || null,
        options,
      };
    };

    const normalizedQuestion = currentQuestion
      ? normalizeAdaptiveQuestion(currentQuestion)
      : null;

    const renderAdaptiveQuestion = (q) => {
      if (!q) return null;
      const props = {
        question: q,
        value: adaptiveAnswer,
        onChange: (val) => {
          setAdaptiveAnswer(val);
          setAdaptiveError(null);
        },
        error: adaptiveError,
      };
      switch (q.type) {
        case 'select':     return <QuestionSelect     key={q.id} {...props} />;
        case 'multiselect':return <QuestionMultiSelect key={q.id} {...props} />;
        case 'number':     return <QuestionNumber      key={q.id} {...props} />;
        case 'radio':      return <QuestionRadio       key={q.id} {...props} />;
        case 'text':       return <QuestionText        key={q.id} {...props} />;
        default:           return null;
      }
    };

    // "Done" screen
    if (adaptiveDone) {
      return (
        <div className="max-w-3xl mx-auto px-4 py-8 animate-fade-in">
          <div className="card p-8 text-center">
            <div className="text-5xl mb-4" aria-hidden="true">🎯</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Analyse terminée !
            </h2>
            <p className="text-gray-600 mb-1">
              {questionsAnswered} question(s) répondue(s)
            </p>
            <p className="text-gray-600 mb-6">
              {remainingAids} aide(s) potentielle(s) identifiée(s) sur {totalAids}
            </p>
            <button
              onClick={handleAdaptiveResults}
              disabled={submitting}
              aria-disabled={submitting}
              className="btn btn-primary flex items-center gap-2 mx-auto"
            >
              {submitting ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Calcul en cours…
                </>
              ) : (
                <>
                  Voir mes aides
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      );
    }

    // Question screen
    return (
      <div className="max-w-3xl mx-auto px-4 py-8 animate-fade-in">
        {/* Header with progress */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-3">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <svg width="24" height="24" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" className="text-green-600">
                <line x1="14" y1="26" x2="14" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <ellipse cx="14" cy="5" rx="3" ry="4.5" fill="currentColor" opacity="0.9"/>
                <ellipse cx="11" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(-20 11 10)"/>
                <ellipse cx="10" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(-25 10 16)"/>
                <ellipse cx="17" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(20 17 10)"/>
                <ellipse cx="18" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(25 18 16)"/>
              </svg>
              Trouvez vos aides
            </h1>
            <span className="badge badge-info" aria-label={`${questionsAnswered} réponse(s) sur ${MAX_ADAPTIVE_QUESTIONS} maximum`}>
              {questionsAnswered} / {MAX_ADAPTIVE_QUESTIONS}
            </span>
          </div>

          <div className="progress-container" role="progressbar" aria-valuenow={Math.round(progress)} aria-valuemin={0} aria-valuemax={100} aria-label="Progression du questionnaire">
            <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          </div>

          <div className="mt-2 flex items-center justify-between text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
              {remainingAids} aide(s) restante(s) sur {totalAids}
            </span>
            <span className="flex items-center gap-1">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
              Environ 3 minutes
            </span>
          </div>
        </div>

        {/* Current question */}
        {normalizedQuestion && (
          <div className="card p-6 mb-6 animate-fade-in" key={currentQuestion.criterion_id}>
            {renderAdaptiveQuestion(normalizedQuestion)}
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-end">
          <button
            onClick={handleAdaptiveNext}
            disabled={submitting}
            aria-disabled={submitting}
            className="btn btn-primary flex items-center gap-2"
          >
            {submitting ? (
              <>
                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Traitement…
              </>
            ) : (
              <>
                Suivant
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                </svg>
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // ── Render: static mode ──────────────────────────────────────────────────

  if (!config || !config.sections) {
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
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" className="text-green-600">
              <line x1="14" y1="26" x2="14" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <ellipse cx="14" cy="5" rx="3" ry="4.5" fill="currentColor" opacity="0.9"/>
              <ellipse cx="11" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(-20 11 10)"/>
              <ellipse cx="10" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(-25 10 16)"/>
              <ellipse cx="17" cy="10" rx="2.5" ry="3.5" fill="currentColor" opacity="0.85" transform="rotate(20 17 10)"/>
              <ellipse cx="18" cy="16" rx="2.5" ry="3.5" fill="currentColor" opacity="0.75" transform="rotate(25 18 16)"/>
            </svg>
            Trouvez vos aides
          </h1>
          <span className="badge badge-info" aria-label={`Étape ${currentSectionIndex + 1} sur ${config.sections.length}`}>
            {currentSectionIndex + 1} / {config.sections.length}
          </span>
        </div>

        {/* Shimmer progress bar */}
        <div className="progress-container" role="progressbar" aria-valuenow={Math.round(progress)} aria-valuemin={0} aria-valuemax={100} aria-label="Progression du questionnaire">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        </div>

        <p className="mt-2 text-sm text-gray-500 flex items-center gap-1">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          Environ {config.metadata?.estimated_time_minutes || 5} minutes
        </p>
      </div>

      {/* Section courante */}
      <div className="card p-6 mb-6 animate-fade-in" key={currentSection.id}>
        <div className="mb-6 pb-5 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            {currentSection.titre}
            {currentSection.importance === 'CRITIQUE' && (
              <span className="badge badge-danger">⭐ Important</span>
            )}
          </h2>
          {currentSection.description && (
            <p className="mt-1 text-sm text-gray-500">{currentSection.description}</p>
          )}
        </div>

        <div className="space-y-6">
          {(currentSection.questions || []).filter(q => q != null).map(question => renderQuestion(question))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrevious}
          disabled={currentSectionIndex === 0}
          aria-disabled={currentSectionIndex === 0}
          className={`btn flex items-center gap-2 ${
            currentSectionIndex === 0
              ? 'opacity-40 cursor-not-allowed bg-gray-100 text-gray-400'
              : 'btn-secondary'
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
          </svg>
          Précédent
        </button>

        <button
          onClick={handleNext}
          disabled={submitting}
          aria-disabled={submitting}
          className="btn btn-primary flex items-center gap-2"
        >
          {submitting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Calcul en cours…
            </>
          ) : currentSectionIndex === config.sections.length - 1 ? (
            <>
              Voir mes aides
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            </>
          ) : (
            <>
              Suivant
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
              </svg>
            </>
          )}
        </button>
      </div>

      {/* Erreurs */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl animate-fade-in" role="alert">
          <p className="text-red-800 font-medium flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Veuillez corriger les erreurs avant de continuer.
          </p>
        </div>
      )}
    </div>
  );
}

