export default function ResultsPage({ results, profil, onRestart }) {
  if (!results) return null;

  const aidesEligibles = results.resultats?.filter(r => r.eligible) || [];
  const aidesQuasiEligibles = results.resultats?.filter(r => !r.eligible && r.score >= 40) || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* En-tête des résultats */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg p-8 mb-8">
        <h1 className="text-3xl font-bold mb-4">
          🎉 Vos résultats sont prêts !
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-4xl font-bold">{results.aides_eligibles || 0}</div>
            <div className="text-sm">Aides éligibles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-4xl font-bold">{results.aides_quasi_eligibles || 0}</div>
            <div className="text-sm">Aides quasi-éligibles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">
              {(results.montant_total_estime_min || 0).toLocaleString('fr-FR')} €
            </div>
            <div className="text-sm">Montant estimé minimum</div>
          </div>
        </div>
      </div>

      {/* Aides éligibles */}
      {aidesEligibles.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ✅ Aides auxquelles vous êtes éligible ({aidesEligibles.length})
          </h2>
          <div className="space-y-4">
            {aidesEligibles.map((resultat, index) => (
              <AideCard key={resultat.aide_id || index} resultat={resultat} type="eligible" />
            ))}
          </div>
        </div>
      )}

      {/* Aides quasi-éligibles */}
      {aidesQuasiEligibles.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ⚠️ Aides presque accessibles ({aidesQuasiEligibles.length})
          </h2>
          <div className="space-y-4">
            {aidesQuasiEligibles.slice(0, 10).map((resultat, index) => (
              <AideCard key={resultat.aide_id || index} resultat={resultat} type="quasi" />
            ))}
          </div>
        </div>
      )}

      {/* Aucune aide */}
      {aidesEligibles.length === 0 && aidesQuasiEligibles.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-lg text-yellow-800">
            😔 Aucune aide trouvée pour votre profil
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

// Composant carte d'aide
function AideCard({ resultat, type }) {
  const aide = resultat.aide || {};
  const borderColor = type === 'eligible' ? 'border-green-500' : 'border-yellow-500';
  const badgeColor = type === 'eligible' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';

  return (
    <div className={`bg-white border-l-4 ${borderColor} rounded-lg shadow p-6`}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold text-gray-900">
          {aide.titre || `Aide ${resultat.aide_id}`}
        </h3>
        <span className={`${badgeColor} px-3 py-1 rounded-full text-sm font-medium`}>
          Score: {Math.round(resultat.score || 0)}/100
        </span>
      </div>
      
      {aide.organisme && (
        <p className="text-sm text-gray-500 mb-2">📍 {aide.organisme}</p>
      )}
      
      {aide.description && (
        <p className="text-gray-600 text-sm mb-3">
          {aide.description.length > 300 ? aide.description.substring(0, 300) + '...' : aide.description}
        </p>
      )}
      
      {aide.tags?.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {aide.tags.slice(0, 5).map((tag, i) => (
            <span key={i} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
              {tag}
            </span>
          ))}
        </div>
      )}
      
      {(resultat.montant_estime_min || resultat.montant_estime_max) && (
        <p className="text-green-700 font-semibold mb-3">
          💰 Montant estimé : {(resultat.montant_estime_min || 0).toLocaleString('fr-FR')} €
          {resultat.montant_estime_max && resultat.montant_estime_max !== resultat.montant_estime_min && 
            ` - ${resultat.montant_estime_max.toLocaleString('fr-FR')} €`}
        </p>
      )}
      
      {/* Critères bloquants si non éligible */}
      {!resultat.eligible && resultat.criteres_bloquants_ko && resultat.criteres_bloquants_ko.length > 0 && (
        <p className="text-orange-600 text-sm mb-3">
          ⚠️ Critères non remplis : {resultat.criteres_bloquants_ko.join(', ')}
        </p>
      )}
      
      {(aide.lien_officiel || aide.source_url) && (
        <a
          href={aide.lien_officiel || aide.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-green-600 hover:text-green-700 font-medium"
        >
          En savoir plus →
        </a>
      )}
    </div>
  );
}
