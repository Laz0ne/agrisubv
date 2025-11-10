import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'https://agrisubv-backend.onrender.com';

const REGIONS = [
    "Auvergne-Rhône-Alpes",
    "Bourgogne-Franche-Comté",
    "Bretagne",
    "Centre-Val de Loire",
    "Corse",
    "Grand Est",
    "Hauts-de-France",
    "Île-de-France",
    "Normandie",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "PACA",
    "Pays de la Loire"
];

const STATUTS_JURIDIQUES = [
    "Exploitation individuelle",
    "EARL",
    "GAEC",
    "SCEA",
    "Autre"
];

function App() {
    const [formData, setFormData] = useState({
        region: '',
        departement: '',
        statut_juridique: '',
        superficie_ha: '',
        age_exploitant: '',
        jeune_agriculteur: false,
    });
    
    const [results, setResults] = useState({
        aidesEligibles: [],
        loading: false,
        error: '',
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setResults({ aidesEligibles: [], loading: true, error: '' });
        
        try {
            const response = await axios.post(`${API_BASE_URL}/api/eligibilite`, formData);
            console.log('Backend response:', response.data);
            
            // Le backend retourne un objet avec { aides_eligibles: [...] }
            const aides = response.data.aides_eligibles || [];
            setResults({ aidesEligibles: aides, loading: false, error: '' });
        } catch (error) {
            console.error('Error:', error);
            setResults({ aidesEligibles: [], loading: false, error: error.message });
        }
    };

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <h1 className="app-title">🌾 AgriSubv</h1>
                    <p className="app-subtitle">Plateforme d'aide aux subventions agricoles</p>
                </div>
            </header>

            {/* Main Content */}
            <main className="app-main">
                <div className="content-wrapper">
                    
                    {/* Form Card */}
                    <section className="card form-card">
                        <h2 className="section-title">Informations sur votre exploitation</h2>
                        
                        <form onSubmit={handleSubmit} className="form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Région *</label>
                                    <select 
                                        name="region" 
                                        value={formData.region}
                                        onChange={handleChange}
                                        className="form-input"
                                        required
                                    >
                                        <option value="">Sélectionnez votre région</option>
                                        {REGIONS.map((region) => (
                                            <option key={region} value={region}>{region}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Département</label>
                                    <input 
                                        type="text" 
                                        name="departement"
                                        value={formData.departement}
                                        onChange={handleChange}
                                        placeholder="Ex: 01, 75, 69..."
                                        className="form-input"
                                    />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Statut juridique *</label>
                                    <select 
                                        name="statut_juridique"
                                        value={formData.statut_juridique}
                                        onChange={handleChange}
                                        className="form-input"
                                        required
                                    >
                                        <option value="">Sélectionnez votre statut</option>
                                        {STATUTS_JURIDIQUES.map((statut) => (
                                            <option key={statut} value={statut}>{statut}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Superficie (hectares) *</label>
                                    <input 
                                        type="number" 
                                        name="superficie_ha"
                                        value={formData.superficie_ha}
                                        onChange={handleChange}
                                        placeholder="Ex: 50"
                                        min="0"
                                        className="form-input"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Âge de l'exploitant</label>
                                    <input 
                                        type="number" 
                                        name="age_exploitant"
                                        value={formData.age_exploitant}
                                        onChange={handleChange}
                                        placeholder="Ex: 35"
                                        min="18"
                                        max="100"
                                        className="form-input"
                                    />
                                </div>

                                <div className="form-group checkbox-wrapper">
                                    <label className="checkbox-label">
                                        <input 
                                            type="checkbox" 
                                            name="jeune_agriculteur"
                                            checked={formData.jeune_agriculteur}
                                            onChange={handleChange}
                                            className="checkbox-input"
                                        />
                                        <span>Jeune agriculteur (première installation)</span>
                                    </label>
                                </div>
                            </div>

                            <button 
                                type="submit" 
                                className="btn btn-primary"
                                disabled={results.loading}
                            >
                                {results.loading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Recherche en cours...
                                    </>
                                ) : (
                                    '🔍 Rechercher les aides disponibles'
                                )}
                            </button>
                        </form>
                    </section>

                    {/* Loading State */}
                    {results.loading && (
                        <div className="loading-state">
                            <div className="loading-spinner"></div>
                            <p>Analyse de votre profil en cours...</p>
                        </div>
                    )}

                    {/* Error State */}
                    {results.error && (
                        <div className="alert alert-error">
                            <span className="alert-icon">⚠️</span>
                            <div>
                                <strong>Erreur</strong>
                                <p>{results.error}</p>
                            </div>
                        </div>
                    )}

                    {/* Results Section */}
                    {results.aidesEligibles.length > 0 && (
                        <section className="results-section">
                            <h2 className="section-title">
                                Résultats ({results.aidesEligibles.length} aide(s) trouvée(s))
                            </h2>
                            
                            <div className="results-grid">
                                {results.aidesEligibles.map((aide, index) => (
                                    <article key={index} className="card aide-card">
                                        <div className="aide-header">
                                            <h3 className="aide-title">{aide.aide?.titre || 'Aide agricole'}</h3>
                                            {aide.score_pertinence && (
                                                <span className="badge badge-score">
                                                    {Math.round(aide.score_pertinence)}%
                                                </span>
                                            )}
                                        </div>
                                        
                                        <div className="aide-body">
                                            {aide.aide?.organisme && (
                                                <p className="aide-info">
                                                    <strong>Organisme:</strong> {aide.aide.organisme}
                                                </p>
                                            )}
                                            {aide.aide?.montant_max && (
                                                <p className="aide-info">
                                                    <strong>Montant max:</strong> {aide.aide.montant_max}€
                                                </p>
                                            )}
                                            {aide.aide?.conditions_clefs && (
                                                <p className="aide-info">
                                                    <strong>Conditions:</strong> {aide.aide.conditions_clefs}
                                                </p>
                                            )}
                                            {aide.resume_ia && (
                                                <p className="aide-info">
                                                    <strong>Résumé:</strong> {aide.resume_ia}
                                                </p>
                                            )}
                                        </div>
                                        
                                        {aide.eligible !== undefined && (
                                            <div className="aide-footer">
                                                <span className={`badge ${aide.eligible ? 'badge-success' : 'badge-error'}`}> 
                                                    {aide.eligible ? '✓ Éligible' : '✗ Non éligible'}
                                                </span>
                                            </div>
                                        )}
                                    </article>
                                ))}
                            </div>
                        </section>
                    )}
                </div>
            </main>

            {/* Footer */}
            <footer className="app-footer">
                <p>© 2025 AgriSubv - Plateforme d'aide aux subventions agricoles</p>
            </footer>
        </div>
    );
}

export default App;
