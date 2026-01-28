/**
 * @deprecated This component is deprecated and should not be used in new code.
 * Please use ResultsPage instead for displaying matching results.
 * This file is kept for reference only.
 */
import React, { useState } from 'react';
import './ResultsSection.css';

export const ResultsSection = ({ results }) => {
  const [expandedAide, setExpandedAide] = useState(null);

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

  const aidesFiltered = resultats.filter(aide => aide.eligible || aide.score >= 40);

  const toggleExpand = (aideId) => {
    setExpandedAide(expandedAide === aideId ? null : aideId);
  };

  return (
    <div className="results-container animate-fadeIn">
      {/* Header avec animation */}
      <div className="results-header">
        <div className="success-badge">
          🎉 Résultats trouvés !
        </div>
        <h2 className="results-title">
          Nous avons trouvé <span className="highlight-number">{aides_eligibles}</span> aide{aides_eligibles > 1 ? 's' : ''} pour vous !
        </h2>
        <p className="results-subtitle">
          Sur {total_aides} aides analysées dans notre base de données
        </p>
      </div>

      {/* Stats Grid améliorée */}
      <div className="stats-grid">
        <div className="stat-card green">
          <div className="stat-icon-wrapper green-bg">
            <span className="stat-icon">✅</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">{aides_eligibles}</div>
            <div className="stat-label">Aides éligibles</div>
            <div className="stat-sublabel">Vous correspondez aux critères</div>
          </div>
        </div>

        <div className="stat-card yellow">
          <div className="stat-icon-wrapper yellow-bg">
            <span className="stat-icon">⚠️</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">{aides_quasi_eligibles}</div>
            <div className="stat-label">Quasi-éligibles</div>
            <div className="stat-sublabel">Critères presque remplis</div>
          </div>
        </div>

        <div className="stat-card blue">
          <div className="stat-icon-wrapper blue-bg">
            <span className="stat-icon">💰</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">
              {montant_total_estime_min > 0 
                ? `${montant_total_estime_min.toLocaleString('fr-FR')}€ - ${montant_total_estime_max.toLocaleString('fr-FR')}€`
                : 'Non estimé'
              }
            </div>
            <div className="stat-label">Montant total estimé</div>
            <div className="stat-sublabel">Cumul des aides éligibles</div>
          </div>
        </div>
      </div>

      {/* Liste des aides améliorée */}
      <div className="aides-section">
        <div className="aides-header-bar">
          <h3 className="aides-section-title">
            📋 Vos aides détaillées ({aidesFiltered.length})
          </h3>
          <button className="btn-export" onClick={() => window.print()}>
            📥 Exporter en PDF
          </button>
        </div>

        <div className="aides-list">
          {aidesFiltered.map((aide, index) => {
            // Récupérer les données de l'aide de manière sécurisée
            const aideData = aide.aide || aide;
            const titre = aideData.titre || aide.titre || 'Aide sans titre';
            const organisme = aideData.organisme || aide.organisme;
            const score = aide.score || 0;
            const eligible = aide.eligible || false;
            const montantMin = aide.montant_estime_min || aideData.montant_min_eur || 0;
            const montantMax = aide.montant_estime_max || aideData.montant_max_eur || 0;
            const description = aide.description || aideData.description || '';
            const resume = aide.resume || '';
            const recommandations = aide.recommandations || [];
            const aideId = aide.aide_id || aideData.aid_id || index;

            return (
              <div 
                key={aideId} 
                className={`aide-card-enhanced ${expandedAide === aideId ? 'expanded' : ''}`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {/* Header de la carte */}
                <div className="aide-card-header">
                  <div className="aide-header-left">
                    <div className="aide-rank">#{index + 1}</div>
                    <div className={`aide-badge ${eligible ? 'green' : 'yellow'}`}>
                      {eligible ? '✅ Éligible' : '⚠️ Quasi-éligible'}
                    </div>
                    <div className="aide-score-badge">
                      {Math.round(score)}% match
                    </div>
                  </div>
                  <button 
                    className="aide-expand-btn"
                    onClick={() => toggleExpand(aideId)}
                    aria-label={expandedAide === aideId ? "Réduire" : "Développer"}
                  >
                    {expandedAide === aideId ? '▼' : '▶'}
                  </button>
                </div>
                
                {/* Titre et organisme */}
                <h3 className="aide-title">{titre}</h3>
                
                {organisme && (
                  <div className="aide-organisme">
                    🏢 {organisme}
                  </div>
                )}
                
                {/* Barre de score */}
                <div className="aide-score-section">
                  <div className="score-bar-container">
                    <div className="score-bar-bg">
                      <div 
                        className={`score-bar-fill ${score >= 80 ? 'excellent' : score >= 60 ? 'good' : 'average'}`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <div className="score-labels">
                      <span className="score-label-left">Correspondance</span>
                      <span className="score-label-right">{Math.round(score)}%</span>
                    </div>
                  </div>
                </div>

                {/* Montant */}
                {(montantMin > 0 || montantMax > 0) && (
                  <div className="aide-montant-section">
                    <div className="montant-icon">💰</div>
                    <div className="montant-details">
                      <div className="montant-label">Montant estimé</div>
                      <div className="montant-value">
                        {montantMin > 0 && montantMax > 0 
                          ? `${montantMin.toLocaleString('fr-FR')}€ - ${montantMax.toLocaleString('fr-FR')}€`
                          : montantMin > 0 
                            ? `À partir de ${montantMin.toLocaleString('fr-FR')}€`
                            : `Jusqu'à ${montantMax.toLocaleString('fr-FR')}€`
                        }
                      </div>
                    </div>
                  </div>
                )}

                {/* Description (si développé) */}
                {expandedAide === aideId && (
                  <div className="aide-details-expanded">
                    {description && (
                      <div className="detail-section">
                        <h4>📝 Description</h4>
                        <p>{description}</p>
                      </div>
                    )}
                    
                    {resume && (
                      <div className="detail-section">
                        <h4>💡 Résumé</h4>
                        <p>{resume}</p>
                      </div>
                    )}

                    {recommandations && recommandations.length > 0 && (
                      <div className="detail-section">
                        <h4>🎯 Recommandations</h4>
                        <ul className="recommendations-list">
                          {recommandations.map((rec, i) => (
                            <li key={i}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Boutons d'action */}
                <div className="aide-actions">
                  <button 
                    className="btn-details-primary"
                    onClick={() => toggleExpand(aideId)}
                  >
                    {expandedAide === aideId ? 'Réduire' : 'Voir les détails'} →
                  </button>
                  <button className="btn-favorite" title="Ajouter aux favoris">
                    ⭐
                  </button>
                  <button className="btn-share" title="Partager">
                    📤
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Message si aucune aide */}
      {aidesFiltered.length === 0 && (
        <div className="no-results">
          <span className="no-results-icon">😔</span>
          <h3>Aucune aide éligible trouvée</h3>
          <p>Essayez de modifier vos critères de recherche</p>
          <button className="btn-retry" onClick={() => window.location.reload()}>
            🔄 Nouvelle simulation
          </button>
        </div>
      )}
    </div>
  );
};
