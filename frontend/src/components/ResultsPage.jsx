import { useState } from 'react';
import DOMPurify from 'dompurify';
import ScoreIndicator from './ScoreIndicator';

export default function ResultsPage({ results, profil, onRestart }) {
  const [expandedAide, setExpandedAide] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'eligible', 'quasi'
  
  if (!results) return null;

  const aidesEligibles = results.resultats?.filter(r => r.eligible) || [];
  const aidesQuasiEligibles = results.resultats?.filter(r => !r.eligible && r.score >= 40) || [];
  
  // Filtrage
  const displayedAides = filter === 'eligible' 
    ? aidesEligibles 
    : filter === 'quasi' 
      ? aidesQuasiEligibles 
      : [...aidesEligibles, ...aidesQuasiEligibles];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* En-tête des résultats */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg p-8 mb-8">
        <h1 className="text-3xl font-bold mb-4">
          🎉 Vos résultats sont prêts !
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-4xl font-bold">{results.total_aides || 0}</div>
            <div className="text-sm">Aides analysées</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4 cursor-pointer hover:bg-white/20" onClick={() => setFilter('eligible')}>
            <div className="text-4xl font-bold text-green-200">{results.aides_eligibles || 0}</div>
            <div className="text-sm">✅ Éligibles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4 cursor-pointer hover:bg-white/20" onClick={() => setFilter('quasi')}>
            <div className="text-4xl font-bold text-yellow-200">{results.aides_quasi_eligibles || 0}</div>
            <div className="text-sm">⚠️ Presque éligibles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">
              {results.montant_total_estime_min > 0 
                ? `${(results.montant_total_estime_min || 0).toLocaleString('fr-FR')} €`
                : 'À estimer'}
            </div>
            <div className="text-sm">💰 Montant potentiel</div>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex gap-2 mb-6">
        <button 
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Toutes ({aidesEligibles.length + aidesQuasiEligibles.length})
        </button>
        <button 
          onClick={() => setFilter('eligible')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'eligible' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          ✅ Éligibles ({aidesEligibles.length})
        </button>
        <button 
          onClick={() => setFilter('quasi')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'quasi' ? 'bg-yellow-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          ⚠️ Presque ({aidesQuasiEligibles.length})
        </button>
      </div>

      {/* Liste des aides */}
      <div className="space-y-4">
        {displayedAides.map((resultat, index) => (
          <AideFlashcard 
            key={resultat.aide_id || index} 
            resultat={resultat}
            isExpanded={expandedAide === resultat.aide_id}
            onToggle={() => setExpandedAide(expandedAide === resultat.aide_id ? null : resultat.aide_id)}
          />
        ))}
      </div>

      {/* Aucune aide */}
      {displayedAides.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-lg text-yellow-800">
            😔 Aucune aide trouvée pour ce filtre
          </p>
        </div>
      )}

      {/* Bouton recommencer */}
      <div className="text-center mt-8">
        <button onClick={onRestart} className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
          🔄 Refaire le questionnaire
        </button>
      </div>
    </div>
  );
}

// Composant Flashcard enrichi
function AideFlashcard({ resultat, isExpanded, onToggle }) {
  const aide = resultat.aide || {};
  const isEligible = resultat.eligible;
  const borderColor = isEligible ? 'border-green-500' : 'border-yellow-500';
  const badgeColor = isEligible ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';

  // Formatter la date limite
  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Formatter le montant
  const formatMontant = () => {
    const montant = aide.montant;
    if (!montant) return null;
    
    const parts = [];
    
    if (montant.taux_min || montant.taux_max) {
      if (montant.taux_min && montant.taux_max && montant.taux_min !== montant.taux_max) {
        parts.push(`${montant.taux_min}% à ${montant.taux_max}%`);
      } else {
        parts.push(`${montant.taux_max || montant.taux_min}%`);
      }
    }
    
    if (montant.min || montant.max) {
      if (montant.min && montant.max && montant.min !== montant.max) {
        parts.push(`${montant.min.toLocaleString('fr-FR')}€ à ${montant.max.toLocaleString('fr-FR')}€`);
      } else {
        parts.push(`jusqu'à ${(montant.max || montant.min).toLocaleString('fr-FR')}€`);
      }
    }
    
    if (montant.plafond) {
      parts.push(`(plafond: ${montant.plafond.toLocaleString('fr-FR')}€)`);
    }
    
    return parts.length > 0 ? parts.join(' • ') : null;
  };

  return (
    <div className={`card ${isEligible ? 'card-eligible' : 'card-quasi'} card-interactive animate-fade-in`}>
      {/* En-tête cliquable */}
      <div 
        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {aide.titre || `Aide ${resultat.aide_id}`}
            </h3>
            {aide.organisme && (
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span>🏛️</span>
                <span>{aide.organisme}</span>
                {aide.programme && <span className="text-gray-400">• {aide.programme}</span>}
              </p>
            )}
          </div>
          
          {/* Score Indicator */}
          <div className="flex flex-col items-end gap-2">
            <ScoreIndicator 
              score={resultat.score || 0}
              size={70}
              eligible={isEligible}
            />
            <span className="text-gray-400 text-2xl transform transition-transform" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
              ▼
            </span>
          </div>
        </div>
        
        {/* Résumé rapide */}
        <div className="flex flex-wrap gap-2 mt-4">
          {/* Date limite */}
          {aide.date_limite_depot && (
            <span className="badge badge-danger">
              📅 Limite: {formatDate(aide.date_limite_depot)}
            </span>
          )}
          
          {/* Montant */}
          {formatMontant() && (
            <span className="badge badge-success">
              💰 {formatMontant()}
            </span>
          )}
          
          {/* Type d'aide */}
          {aide.montant?.type && (
            <span className="badge badge-info">
              {aide.montant.type}
            </span>
          )}
          
          {/* Tags */}
          {aide.tags?.slice(0, 3).map((tag, i) => (
            <span key={i} className="badge badge-neutral">
              {tag}
            </span>
          ))}
        </div>

        {/* Critères bloquants si non éligible */}
        {!isEligible && resultat.criteres_bloquants_ko?.length > 0 && (
          <div className="mt-4 p-3 bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-xl">
            <p className="text-orange-800 text-sm font-medium flex items-start gap-2">
              <span className="text-lg">⚠️</span>
              <span>
                <strong>Critères non remplis:</strong>
                <span className="block mt-1">
                  {resultat.criteres_bloquants_ko.join(', ')}
                </span>
              </span>
            </p>
          </div>
        )}
      </div>

      {/* Détails expandables */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-6 bg-gradient-to-br from-gray-50 to-white animate-fade-in">
          {/* Description */}
          {aide.description && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">📝</span>
                <span>Description</span>
              </h4>
              <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                {aide.description}
              </p>
            </div>
          )}
          
          {/* Conditions d'éligibilité */}
          {aide.conditions_eligibilite && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">✅</span>
                <span>Conditions d'éligibilité</span>
              </h4>
              <div 
                className="text-gray-700 prose prose-sm max-w-none leading-relaxed"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(aide.conditions_eligibilite) }}
              />
            </div>
          )}
          
          {/* Critères détectés */}
          {aide.criteres && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">🎯</span>
                <span>Critères détectés</span>
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                {aide.criteres.regions?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="font-semibold text-gray-900">Régions:</span>
                    <span className="ml-2 text-gray-600">{aide.criteres.regions.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.types_production?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="font-semibold text-gray-900">Productions:</span>
                    <span className="ml-2 text-gray-600">{aide.criteres.types_production.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.types_projets?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="font-semibold text-gray-900">Projets:</span>
                    <span className="ml-2 text-gray-600">{aide.criteres.types_projets.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.labels_requis?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="font-semibold text-gray-900">Labels requis:</span>
                    <span className="ml-2 text-gray-600">{aide.criteres.labels_requis.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.jeune_agriculteur && (
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                    <span className="font-semibold text-blue-900">👨‍🌾 Réservé aux Jeunes Agriculteurs</span>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Démarches */}
          {aide.demarche && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">📋</span>
                <span>Démarches</span>
              </h4>
              <p className="text-gray-700 leading-relaxed">{aide.demarche}</p>
            </div>
          )}
          
          {/* Détails du score */}
          {resultat.details_criteres?.length > 0 && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">📊</span>
                <span>Détail du score</span>
              </h4>
              <div className="space-y-2">
                {resultat.details_criteres.map((critere, i) => (
                  <div 
                    key={i} 
                    className={`flex justify-between items-center p-3 rounded-lg ${
                      critere.valide 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-red-50 border border-red-200'
                    }`}
                  >
                    <span className={`font-medium ${critere.valide ? 'text-green-700' : 'text-red-700'}`}>
                      <span className="text-lg mr-2">{critere.valide ? '✓' : '✗'}</span>
                      {critere.nom}
                    </span>
                    <span className={`font-semibold ${critere.valide ? 'text-green-600' : 'text-red-600'}`}>
                      {critere.points}/{critere.points_max} pts
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Liens */}
          <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
            {(aide.lien_officiel || aide.source_url) && (
              <a
                href={aide.lien_officiel || aide.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                <span className="mr-2">🔗</span>
                Voir l'aide officielle
              </a>
            )}
            {aide.lien_dossier && (
              <a
                href={aide.lien_dossier}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary"
              >
                <span className="mr-2">📄</span>
                Déposer un dossier
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
