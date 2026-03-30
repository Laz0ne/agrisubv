import { useState, useEffect, useMemo } from 'react';
import DOMPurify from 'dompurify';
import ScoreIndicator from './ScoreIndicator';

const TYPES_PRODUCTION = [
  'Céréales', 'Maraîchage', 'Viticulture', 'Arboriculture',
  'Élevage bovin', 'Élevage ovin', 'Élevage caprin', 'Élevage porcin',
  'Élevage avicole', 'Élevage laitier', 'Grandes cultures', 'Horticulture',
  'Apiculture', 'Aquaculture',
];

const TYPES_PROJETS = [
  'Installation', 'Conversion bio', 'Modernisation', 'Diversification',
  'Irrigation', 'Bâtiment', 'Matériel', 'Énergie', 'Environnement',
  'Formation', 'Commercialisation', 'Numérique', 'Bien-être animal',
];

export default function ResultsPage({ results, profil, onRestart }) {
  const [expandedAide, setExpandedAide] = useState(null);
  const [filter, setFilter] = useState('all');
  const [visible, setVisible] = useState(false);

  // Advanced filters state
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [filterRegion, setFilterRegion] = useState('');
  const [filterTypeProduction, setFilterTypeProduction] = useState('');
  const [filterTypeProjet, setFilterTypeProjet] = useState('');
  const [filterMontantMin, setFilterMontantMin] = useState('');
  const [filterOrganisme, setFilterOrganisme] = useState('');
  const [sortBy, setSortBy] = useState('score');

  function handleExport() {
    const date = new Date().toISOString().slice(0, 10);
    const payload = {
      metadata: { date, version: '1.0', application: 'AgriSubv' },
      profil: profil || {},
      resultats: results,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agrisubv-resultats-${date}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, []);

  if (!results) return null;

  const aidesTresProbable = results.resultats?.filter(r => r.statut_matching === 'tres_probable') || [];
  const aidesProbable = results.resultats?.filter(r => r.statut_matching === 'probable') || [];
  const aidesAVerifier = results.resultats?.filter(r => r.statut_matching === 'a_verifier') || [];
  const aidesNonRetenue = results.resultats?.filter(r => r.statut_matching === 'non_retenue') || [];

  // All resultats after status filter
  const statusFilteredAides = useMemo(() => {
    if (filter === 'tres_probable') return aidesTresProbable;
    if (filter === 'probable')      return aidesProbable;
    if (filter === 'a_verifier')    return aidesAVerifier;
    if (filter === 'non_retenue')   return aidesNonRetenue;
    return [...aidesTresProbable, ...aidesProbable, ...aidesAVerifier];
  }, [filter, aidesTresProbable, aidesProbable, aidesAVerifier, aidesNonRetenue]);

  // Extract unique regions and organismes from all resultats
  const uniqueRegions = useMemo(() => {
    const allResultats = results.resultats || [];
    const regions = new Set();
    allResultats.forEach(r => {
      (r.aide?.criteres?.regions || []).forEach(reg => regions.add(reg));
    });
    return Array.from(regions).sort();
  }, [results.resultats]);

  const uniqueOrganismes = useMemo(() => {
    const allResultats = results.resultats || [];
    const organismes = new Set();
    allResultats.forEach(r => {
      if (r.aide?.organisme) organismes.add(r.aide.organisme);
    });
    return Array.from(organismes).sort();
  }, [results.resultats]);

  // Apply advanced filters + sort with useMemo
  const displayedAides = useMemo(() => {
    let aides = statusFilteredAides;

    // Text search
    if (searchText.trim()) {
      const q = searchText.trim().toLowerCase();
      aides = aides.filter(r => {
        const aide = r.aide || {};
        return (
          (aide.titre || '').toLowerCase().includes(q) ||
          (aide.organisme || '').toLowerCase().includes(q) ||
          (aide.description || '').toLowerCase().includes(q)
        );
      });
    }

    // Region filter
    if (filterRegion) {
      aides = aides.filter(r => {
        const regions = r.aide?.criteres?.regions || [];
        return regions.includes(filterRegion);
      });
    }

    // Type de production filter
    if (filterTypeProduction) {
      aides = aides.filter(r => {
        const types = r.aide?.criteres?.types_production || [];
        return types.includes(filterTypeProduction);
      });
    }

    // Type de projet filter
    if (filterTypeProjet) {
      aides = aides.filter(r => {
        const types = r.aide?.criteres?.types_projets || [];
        return types.includes(filterTypeProjet);
      });
    }

    // Montant minimum filter
    if (filterMontantMin !== '') {
      const minVal = parseFloat(filterMontantMin);
      if (!isNaN(minVal)) {
        aides = aides.filter(r => {
          const montantValue = r.montant_estime_min ?? r.aide?.montant?.montant_max ?? 0;
          return montantValue >= minVal;
        });
      }
    }

    // Organisme filter
    if (filterOrganisme) {
      aides = aides.filter(r => r.aide?.organisme === filterOrganisme);
    }

    // Sort
    aides = [...aides];
    if (sortBy === 'score') {
      aides.sort((a, b) => (b.score || 0) - (a.score || 0));
    } else if (sortBy === 'montant') {
      aides.sort((a, b) => {
        const aVal = a.montant_estime_min ?? a.aide?.montant?.montant_max ?? 0;
        const bVal = b.montant_estime_min ?? b.aide?.montant?.montant_max ?? 0;
        return bVal - aVal;
      });
    } else if (sortBy === 'titre') {
      aides.sort((a, b) => {
        const aTitle = (a.aide?.titre || '').toLowerCase();
        const bTitle = (b.aide?.titre || '').toLowerCase();
        return aTitle.localeCompare(bTitle, 'fr');
      });
    }

    return aides;
  }, [statusFilteredAides, searchText, filterRegion, filterTypeProduction, filterTypeProjet, filterMontantMin, filterOrganisme, sortBy]);

  // Count active advanced filters (excluding sort)
  const activeFilterCount = [
    searchText.trim() !== '',
    filterRegion !== '',
    filterTypeProduction !== '',
    filterTypeProjet !== '',
    filterMontantMin !== '',
    filterOrganisme !== '',
  ].filter(Boolean).length;

  function resetFilters() {
    setSearchText('');
    setFilterRegion('');
    setFilterTypeProduction('');
    setFilterTypeProjet('');
    setFilterMontantMin('');
    setFilterOrganisme('');
    setSortBy('score');
  }

  const totalStatusFiltered = statusFilteredAides.length;

  return (
    <div className={`max-w-6xl mx-auto px-4 py-8 transition-opacity duration-500 ${visible ? 'opacity-100' : 'opacity-0'}`}>

      {/* ── Dashboard Header ─────────────────────────────────── */}
      <div className="results-header mb-8 rounded-2xl overflow-hidden shadow-xl animate-fade-in">
        <div className="bg-gradient-to-br from-green-700 via-emerald-600 to-teal-600 p-8 text-white relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/3 translate-x-1/3" aria-hidden="true"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/3 -translate-x-1/4" aria-hidden="true"></div>

          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </div>
              <h1 className="text-2xl font-bold">Vos résultats sont prêts !</h1>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                value={results.total_aides || 0}
                label="Aides analysées"
                icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>}
              />
              <StatCard
                value={aidesTresProbable.length + aidesProbable.length}
                label="Éligibles"
                highlight="green"
                onClick={() => setFilter('tres_probable')}
                icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>}
              />
              <StatCard
                value={aidesAVerifier.length}
                label="À vérifier"
                highlight="yellow"
                onClick={() => setFilter('a_verifier')}
                icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>}
              />
              <StatCard
                value={results.montant_total_estime_min > 0
                  ? `${(results.montant_total_estime_min || 0).toLocaleString('fr-FR')} €`
                  : 'À estimer'}
                label="Montant potentiel"
                icon={<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ── Filter Tabs ───────────────────────────────────────── */}
      <div className="flex gap-2 mb-6 flex-wrap" role="group" aria-label="Filtrer les aides">
        {[
          { key: 'all',          label: `Actives (${aidesTresProbable.length + aidesProbable.length + aidesAVerifier.length})`, color: 'gray' },
          { key: 'tres_probable', label: `🟢 Très probable (${aidesTresProbable.length})`,  color: 'green' },
          { key: 'probable',      label: `🔵 Probable (${aidesProbable.length})`,            color: 'blue' },
          { key: 'a_verifier',    label: `🟡 À vérifier (${aidesAVerifier.length})`,         color: 'yellow' },
          { key: 'non_retenue',   label: `⚫ Non retenue (${aidesNonRetenue.length})`,       color: 'gray-dark' },
        ].map(({ key, label, color }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            aria-pressed={filter === key}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
              filter === key
                ? color === 'green'     ? 'bg-green-600 text-white shadow-md shadow-green-500/25'
                : color === 'blue'      ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25'
                : color === 'yellow'    ? 'bg-amber-500 text-white shadow-md shadow-amber-500/25'
                : color === 'gray-dark' ? 'bg-gray-500 text-white shadow-md'
                                        : 'bg-gray-700 text-white shadow-md'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Advanced Filter Toolbar ───────────────────────────── */}
      <div className="mb-4">
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={() => setFiltersOpen(prev => !prev)}
            aria-expanded={filtersOpen}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border transition-all duration-200 ${
              filtersOpen
                ? 'bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-500/25'
                : 'bg-white text-gray-700 border-gray-200 hover:border-emerald-300 hover:bg-emerald-50'
            }`}
          >
            🔧 Filtres avancés
            {activeFilterCount > 0 && (
              <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-white text-emerald-700 text-xs font-bold leading-none">
                {activeFilterCount}
              </span>
            )}
            <svg
              width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
              className={`transition-transform duration-200 ${filtersOpen ? 'rotate-180' : ''}`}
              aria-hidden="true"
            >
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>

          {activeFilterCount > 0 && (
            <button
              onClick={resetFilters}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm text-red-600 border border-red-200 bg-red-50 hover:bg-red-100 font-medium transition-all duration-200"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
              Réinitialiser les filtres
            </button>
          )}

          <span className="ml-auto text-sm text-gray-500">
            <span className="font-semibold text-gray-800">{displayedAides.length}</span> aide{displayedAides.length !== 1 ? 's' : ''} affichée{displayedAides.length !== 1 ? 's' : ''} sur <span className="font-semibold text-gray-800">{totalStatusFiltered}</span>
          </span>
        </div>

        {/* Collapsible filter panel */}
        {filtersOpen && (
          <div className="mt-3 p-5 bg-white border border-gray-200 rounded-2xl shadow-md animate-fade-in">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

              {/* Text search */}
              <div className="sm:col-span-2 lg:col-span-3">
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  🔍 Recherche textuelle
                </label>
                <input
                  type="text"
                  value={searchText}
                  onChange={e => setSearchText(e.target.value)}
                  placeholder="Titre, organisme, description…"
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent"
                />
              </div>

              {/* Région */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  📍 Région
                </label>
                <select
                  value={filterRegion}
                  onChange={e => setFilterRegion(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent bg-white"
                >
                  <option value="">Toutes les régions</option>
                  {uniqueRegions.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>

              {/* Type de production */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  🌾 Type de production
                </label>
                <select
                  value={filterTypeProduction}
                  onChange={e => setFilterTypeProduction(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent bg-white"
                >
                  <option value="">Tous les types</option>
                  {TYPES_PRODUCTION.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              {/* Type de projet */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  🎯 Type de projet
                </label>
                <select
                  value={filterTypeProjet}
                  onChange={e => setFilterTypeProjet(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent bg-white"
                >
                  <option value="">Tous les projets</option>
                  {TYPES_PROJETS.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              {/* Organisme */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  🏛️ Organisme
                </label>
                <select
                  value={filterOrganisme}
                  onChange={e => setFilterOrganisme(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent bg-white"
                >
                  <option value="">Tous les organismes</option>
                  {uniqueOrganismes.map(o => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              </div>

              {/* Montant minimum */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  💰 Montant minimum (€)
                </label>
                <input
                  type="number"
                  value={filterMontantMin}
                  onChange={e => setFilterMontantMin(e.target.value)}
                  placeholder="Ex: 5000"
                  min="0"
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent"
                />
              </div>

              {/* Tri */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wide">
                  ↕️ Trier par
                </label>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent bg-white"
                >
                  <option value="score">Score (par défaut)</option>
                  <option value="montant">Montant estimé (décroissant)</option>
                  <option value="titre">Titre (alphabétique)</option>
                </select>
              </div>

            </div>
          </div>
        )}
      </div>

      {/* ── Aide Cards ────────────────────────────────────────── */}
      <div className="space-y-4">
        {displayedAides.map((resultat, index) => (
          <AideFlashcard
            key={resultat.aide_id || index}
            resultat={resultat}
            index={index}
            isExpanded={expandedAide === resultat.aide_id}
            onToggle={() => setExpandedAide(expandedAide === resultat.aide_id ? null : resultat.aide_id)}
          />
        ))}
      </div>

      {/* ── Empty state ───────────────────────────────────────── */}
      {displayedAides.length === 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-8 text-center animate-fade-in">
          <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <p className="text-lg font-semibold text-amber-800">Aucune aide trouvée pour ce filtre</p>
          <p className="text-sm text-amber-600 mt-1">Essayez un autre filtre ou modifiez votre profil.</p>
        </div>
      )}

      {/* ── Action Buttons ────────────────────────────────────── */}
      <div className="flex justify-center gap-3 mt-10 flex-wrap">
        <button
          onClick={onRestart}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium transition-all duration-200"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/>
          </svg>
          Refaire le questionnaire
        </button>
        <button
          onClick={handleExport}
          className="inline-flex items-center gap-2 px-6 py-3 btn btn-secondary rounded-xl font-medium transition-all duration-200 bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
        >
          📥 Exporter les résultats
        </button>
      </div>
    </div>
  );
}

// Statut matching badge
function StatutMatchingBadge({ statut }) {
  const config = {
    tres_probable: { label: 'Très probable', className: 'bg-green-100 text-green-800 border border-green-200' },
    probable:      { label: 'Probable',       className: 'bg-blue-100 text-blue-800 border border-blue-200' },
    a_verifier:    { label: 'À vérifier',     className: 'bg-amber-100 text-amber-800 border border-amber-200' },
    non_retenue:   { label: 'Non retenue',    className: 'bg-gray-100 text-gray-600 border border-gray-200' },
  };
  const { label, className } = config[statut] || config.non_retenue;
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${className}`}>
      {label}
    </span>
  );
}

// Stat card inside header
function StatCard({ value, label, icon, highlight, onClick }) {
  return (
    <div
      className={`bg-white/10 backdrop-blur-sm rounded-xl p-4 ${onClick ? 'cursor-pointer hover:bg-white/20 transition-colors' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } } : undefined}
    >
      <div className="flex items-center gap-2 mb-1 opacity-80">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <div className={`text-2xl font-extrabold ${
        highlight === 'green' ? 'text-green-200'
        : highlight === 'yellow' ? 'text-yellow-200'
        : 'text-white'
      }`}>
        {value}
      </div>
    </div>
  );
}

// Aide flashcard
function AideFlashcard({ resultat, index, isExpanded, onToggle }) {
  const aide = resultat.aide || {};
  const isEligible = resultat.eligible;

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    try {
      return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const formatMontant = () => {
    const montant = aide.montant;
    if (!montant) return null;
    const parts = [];
    if (montant.taux_min || montant.taux_max) {
      parts.push(montant.taux_min && montant.taux_max && montant.taux_min !== montant.taux_max
        ? `${montant.taux_min}% à ${montant.taux_max}%`
        : `${montant.taux_max || montant.taux_min}%`);
    }
    if (montant.min || montant.max) {
      parts.push(montant.min && montant.max && montant.min !== montant.max
        ? `${montant.min.toLocaleString('fr-FR')}€ à ${montant.max.toLocaleString('fr-FR')}€`
        : `jusqu'à ${(montant.max || montant.min).toLocaleString('fr-FR')}€`);
    }
    if (montant.plafond) parts.push(`(plafond: ${montant.plafond.toLocaleString('fr-FR')}€)`);
    return parts.length > 0 ? parts.join(' • ') : null;
  };

  const formatMontantEstime = () => {
    const min = resultat.montant_estime_min;
    const max = resultat.montant_estime_max;
    if (min != null && max != null && min !== max) return `${min.toLocaleString('fr-FR')} € – ${max.toLocaleString('fr-FR')} €`;
    if (max != null) return `${max.toLocaleString('fr-FR')} €`;
    if (min != null) return `${min.toLocaleString('fr-FR')} €`;
    return 'Montant à déterminer';
  };

  return (
    <div
      className={`card ${isEligible ? 'card-eligible' : 'card-quasi'} card-interactive animate-fade-in`}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Header cliquable */}
      <div
        className="p-6 cursor-pointer hover:bg-gray-50/50 transition-colors"
        onClick={onToggle}
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onToggle(); } }}
      >
        <div className="flex justify-between items-start gap-4 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-gray-900 mb-1 leading-snug">
              {aide.titre || `Aide ${resultat.aide_id}`}
            </h3>
            <p className="text-sm text-gray-500 flex items-center gap-1.5 truncate">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              <span className="truncate">{aide.organisme || 'Organisme non précisé'}</span>
              {aide.programme && <span className="text-gray-400 truncate">• {aide.programme}</span>}
            </p>
            {resultat.resume && (
              <p className="text-xs text-gray-500 mt-1 italic truncate">{resultat.resume}</p>
            )}
          </div>

          <div className="flex flex-col items-end gap-2 flex-shrink-0">
            <ScoreIndicator score={resultat.score || 0} size={64} eligible={isEligible} />
            {resultat.statut_matching && (
              <StatutMatchingBadge statut={resultat.statut_matching} />
            )}
            <svg
              width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
              className={`text-gray-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
              aria-hidden="true"
            >
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-3">
          {aide.date_limite_depot && (
            <span className="badge badge-danger">
              📅 Limite: {formatDate(aide.date_limite_depot)}
            </span>
          )}
          {formatMontant() ? (
            <span className="badge badge-success">💰 {formatMontant()}</span>
          ) : (
            <span className="badge badge-neutral">💰 {formatMontantEstime()}</span>
          )}
          {aide.montant?.type && (
            <span className="badge badge-info">{aide.montant.type}</span>
          )}
          {(aide.lien_officiel || aide.source_url) && (
            <a
              href={aide.lien_officiel || aide.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="badge badge-info hover:opacity-80 transition-opacity"
            >
              🔗 Voir l'aide officielle
            </a>
          )}
          {aide.tags?.slice(0, 3).map((tag, i) => (
            <span key={i} className="badge badge-neutral">{tag}</span>
          ))}
        </div>

        {/* Critères bloquants */}
        {!isEligible && resultat.criteres_bloquants_ko?.length > 0 && (
          <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-xl">
            <p className="text-orange-800 text-sm font-medium flex items-start gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0 mt-0.5" aria-hidden="true">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <span>
                <strong>Critères non remplis: </strong>
                {resultat.criteres_bloquants_ko.join(', ')}
              </span>
            </p>
          </div>
        )}
      </div>

      {/* Détails expandables */}
      {isExpanded && (
        <div className="border-t border-gray-100 p-6 bg-gradient-to-br from-gray-50 to-white animate-fade-in">
          <div className="mb-6">
            <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
              </svg>
              Description
            </h4>
            {(aide.description || resultat.resume) ? (
              <div
                className="text-gray-700 prose prose-sm max-w-none leading-relaxed"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(aide.description || resultat.resume || '')
                }}
              />
            ) : aide.conditions_eligibilite ? (
              <p className="text-gray-700 leading-relaxed text-sm italic">Voir les conditions d'éligibilité ci-dessous.</p>
            ) : (
              <p className="text-gray-700 leading-relaxed text-sm italic">Aucune description disponible pour cette aide.</p>
            )}
          </div>

          {aide.conditions_eligibilite && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
                </svg>
                Conditions d'éligibilité
              </h4>
              <div
                className="text-gray-700 prose prose-sm max-w-none leading-relaxed"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(aide.conditions_eligibilite) }}
              />
            </div>
          )}

          {aide.criteres && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
                </svg>
                Critères détectés
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                {aide.criteres.regions?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-100">
                    <span className="font-semibold text-gray-900">Régions: </span>
                    <span className="text-gray-600">{aide.criteres.regions.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.types_production?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-100">
                    <span className="font-semibold text-gray-900">Productions: </span>
                    <span className="text-gray-600">{aide.criteres.types_production.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.types_projets?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-100">
                    <span className="font-semibold text-gray-900">Projets: </span>
                    <span className="text-gray-600">{aide.criteres.types_projets.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.labels_requis?.length > 0 && (
                  <div className="bg-white p-3 rounded-lg border border-gray-100">
                    <span className="font-semibold text-gray-900">Labels requis: </span>
                    <span className="text-gray-600">{aide.criteres.labels_requis.join(', ')}</span>
                  </div>
                )}
                {aide.criteres.jeune_agriculteur && (
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                    <span className="font-semibold text-blue-900">👨‍🌾 Réservé aux Jeunes Agriculteurs</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {aide.demarche && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/>
                </svg>
                Démarches
              </h4>
              <div
                className="text-gray-700 prose prose-sm max-w-none leading-relaxed"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(aide.demarche) }}
              />
            </div>
          )}

          {resultat.details_criteres?.length > 0 && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
                </svg>
                Détail du score
              </h4>
              <div className="space-y-2">
                {resultat.details_criteres.map((critere, i) => (
                  <div
                    key={i}
                    className={`flex justify-between items-center p-3 rounded-xl text-sm ${
                      critere.valide ? 'bg-green-50 border border-green-100' : 'bg-red-50 border border-red-100'
                    }`}
                  >
                    <span className={`font-medium flex items-center gap-2 ${critere.valide ? 'text-green-700' : 'text-red-700'}`}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        {critere.valide ? <polyline points="20 6 9 17 4 12"/> : <><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>}
                      </svg>
                      {critere.nom}
                    </span>
                    <span className={`font-bold ${critere.valide ? 'text-green-600' : 'text-red-600'}`}>
                      {critere.points}/{critere.points_max} pts
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {resultat.recommandations?.length > 0 && (
            <div className="mb-6">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                Recommandations
              </h4>
              <ul className="space-y-1">
                {resultat.recommandations.map((rec, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-amber-500 flex-shrink-0 mt-0.5">→</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-100">
            {(aide.lien_officiel || aide.source_url) && (
              <a
                href={aide.lien_officiel || aide.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                </svg>
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
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
                </svg>
                Déposer un dossier
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

