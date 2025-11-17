export default function ResultsPage({ results, profil, onRestart }) {
  if (!results) return null;

  const aidesEligibles = results.resultats.filter(r => r.eligible);
  const aidesQuasiEligibles = results.resultats.filter(r => !r.eligible && r.score >= 40);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* En-tête des résultats */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg p-8 mb-8">
        <h1 className="text-3xl font-bold mb-4">
          🎉 Vos résultats sont prêts !
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-4xl font-bold">{results.aides_eligibles}</div>
            <div className="text-sm">Aides éligibles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-4xl font-bold">{results.aides_quasi_eligibles}</div>
            <div className="text-sm">Aides quasi-éligibles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold">
              {results.montant_total_estime_min.toLocaleString()} €
            </div>
            <div className="text-sm">Montant total estimé</div>
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
           {aidesEligibles.map((resultat, index) => {
  const aide = resultat.aide || resultat; // Support des deux formats
  
  return (
    <div key={index} className="bg-white border-l-4 border-green-500 rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold text-gray-900">
          {aide.titre || 'Titre non disponible'}
                  </h3>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                    Score: {resultat.score}/100
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-3">
                  {resultat.aide.description.substring(0, 200)}...
                </p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {resultat.aide.type_aide?.map((type, i) => (
                    <span key={i} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                      {type}
                    </span>
                  ))}
                </div>
                {resultat.montant_estime_min && (
                  <p className="text-green-700 font-semibold">
                    💰 Montant estimé : {resultat.montant_estime_min.toLocaleString()} € - {resultat.montant_estime_max?.toLocaleString()} €
                  </p>
                )}
                {resultat.aide.url && (
                  <a
                    href={resultat.aide.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-3 text-green-600 hover:text-green-700 font-medium"
                  >
                    En savoir plus →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Aides quasi-éligibles */}
      {aidesQuasiEligibles.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ⚠️ Aides pour lesquelles vous êtes presque éligible ({aidesQuasiEligibles.length})
          </h2>
          <div className="space-y-4">
            {aidesQuasiEligibles.slice(0, 5).map((resultat, index) => (
              <div key={index} className="bg-white border-l-4 border-yellow-500 rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {resultat.aide.titre}
                  </h3>
                  <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
                    Score: {resultat.score}/100
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-3">
                  {resultat.aide.description.substring(0, 200)}...
                </p>
                <p className="text-yellow-700 text-sm">
                  ℹ️ Critères manquants : {resultat.criteres_manquants?.join(', ') || 'Voir les détails'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bouton recommencer */}
      <div className="text-center mt-8">
        <button
          onClick={onRestart}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
        >
          🔄 Refaire le questionnaire
        </button>
      </div>
    </div>
  );
}
