import React from 'react';
import './ResultsSection.css';

export const ResultsSection = ({ results }) => {
  if (!results) {
    return (
      <div className="results-container">
        <div className="results-empty">
          <span className="empty-icon">🔍</span>
          <h2>Aucun résultat</h2>
          <p>Complétez le formulaire pour trouver vos aides</p>
        </div>
      </div>
    );
  }

  const { 
    total_aides = 0, 
    aides_eligibles = 0, 
    aides_quasi_eligibles = 0,
    montant_total_estime_min = 0,
    montant_total_estime_max = 0,
    resultats = [] 
  } = results;

  return (
    <div className="results-container animate-fadeIn">
      <div className="results-header">
        <h2 className="results-title">
          🎉 Nous avons trouvé {aides_eligibles} aide{aides_eligibles > 1 ? 's' : ''} pour vous !
        </h2>
        <p className="results-subtitle">
          Sur {total_aides} aides analysées
        </p>
      </div>

      <div className="stats-grid">
        <div className="stat-card green">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{aides_eligibles}</div>
            <div className="stat-label">Aides éligibles</div>
          </div>
        </div>

        <div className="stat-card yellow">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-value">{aides_quasi_eligibles}</div>
            <div className="stat-label">Quasi-éligibles</div>
          </div>
        </div>

        <div className="stat-card blue">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-value">
              {montant_total_estime_min.toLocaleString()}€ - {montant_total_estime_max.toLocaleString()}€
            </div>
            <div className="stat-label">Montant estimé</div>
          </div>
        </div>
      </div>

      <div className="aides-list">
        {resultats
          .filter(aide => aide.eligible || aide.quasi_eligible)
          .map((aide, index) => (
            <div key={aide.aide_id} className="aide-card animate-slideInLeft" style={{ animationDelay: `${index * 0.1}s` }}>
              <div className="aide-header">
                <div className="aide-rank">#{index + 1}</div>
                <div className={`aide-badge ${aide.eligible ? 'green' : 'yellow'}`}>
                  {aide.eligible ? '✅ Éligible' : '⚠️ Quasi-éligible'}
                </div>
              </div>
              
              <h3 className="aide-title">{aide.titre}</h3>
              
              <div className="aide-score">
                <div className="score-bar-bg">
                  <div 
                    className="score-bar-fill"
                    style={{ width: `${aide.score}%` }}
                  />
                </div>
                <span className="score-value">{Math.round(aide.score)}% de correspondance</span>
              </div>

              {aide.montant_min && aide.montant_max && (
                <div className="aide-montant">
                  💰 {aide.montant_min.toLocaleString()}€ - {aide.montant_max.toLocaleString()}€
                </div>
              )}

              <button className="btn-details">
                Voir les détails →
              </button>
            </div>
          ))}
      </div>

      {resultats.filter(aide => aide.eligible || aide.quasi_eligible).length === 0 && (
        <div className="no-results">
          <span className="no-results-icon">😔</span>
          <h3>Aucune aide éligible trouvée</h3>
          <p>Essayez de modifier vos critères de recherche</p>
        </div>
      )}
    </div>
  );
};
