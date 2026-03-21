import { useState, useEffect, useCallback } from 'react';
import { Header } from './layout/Header';
import { Footer } from './layout/Footer';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://agrisubv-backend.onrender.com/api';
const ADMIN_KEY = import.meta.env.VITE_ADMIN_KEY || '';

// ── Auth Gate ─────────────────────────────────────────────────────────────────

function AuthGate({ children }) {
  const [unlocked, setUnlocked] = useState(() => {
    if (!ADMIN_KEY) return true; // dev mode
    const params = new URLSearchParams(window.location.search);
    if (params.get('key') === ADMIN_KEY) {
      // Remove the key from URL to avoid it appearing in browser history/logs
      const cleanUrl = window.location.pathname + (params.toString().replace(/key=[^&]*&?/, '').replace(/&$/, '') ? `?${params.toString().replace(/key=[^&]*&?/, '').replace(/&$/, '')}` : '');
      window.history.replaceState(null, '', cleanUrl);
      return true;
    }
    return localStorage.getItem('admin_key') === ADMIN_KEY;
  });
  const [input, setInput] = useState('');
  const [error, setError] = useState(false);

  if (unlocked) return children;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input === ADMIN_KEY) {
      localStorage.setItem('admin_key', input);
      setUnlocked(true);
    } else {
      setError(true);
      setInput('');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-sm">
        <div className="text-center mb-6">
          <span className="text-4xl">🔒</span>
          <h1 className="text-xl font-bold text-gray-900 mt-2">Accès Admin</h1>
          <p className="text-sm text-gray-500 mt-1">Entrez le mot de passe administrateur</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="password"
            value={input}
            onChange={(e) => { setInput(e.target.value); setError(false); }}
            placeholder="Mot de passe"
            className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500"
            autoFocus
          />
          {error && <p className="text-red-500 text-sm">Mot de passe incorrect</p>}
          <button
            type="submit"
            className="w-full py-2 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 transition-colors"
          >
            Accéder
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Stat Card ─────────────────────────────────────────────────────────────────

function StatCard({ label, value, icon, color = 'from-green-500 to-emerald-500' }) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center text-2xl flex-shrink-0`}>
        {icon}
      </div>
      <div>
        <p className="text-2xl font-extrabold text-gray-900 leading-none">{value ?? '—'}</p>
        <p className="text-sm text-gray-500 mt-0.5">{label}</p>
      </div>
    </div>
  );
}

// ── Section wrapper ───────────────────────────────────────────────────────────

function Section({ title, children }) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">{title}</h2>
      {children}
    </div>
  );
}

// ── Sync Button ───────────────────────────────────────────────────────────────

function SyncButton({ label, onAction, paramLabel, paramKey, paramDefault }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [paramValue, setParamValue] = useState(paramDefault ?? '');

  const handleClick = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await onAction(paramKey ? Number(paramValue) || undefined : undefined);
      setResult({ ok: true, data: res });
    } catch (err) {
      setResult({ ok: false, message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        {paramLabel && (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600 whitespace-nowrap">{paramLabel}</label>
            <input
              type="number"
              value={paramValue}
              onChange={(e) => setParamValue(e.target.value)}
              className="w-20 px-2 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              min={1}
            />
          </div>
        )}
        <button
          onClick={handleClick}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-xl hover:bg-green-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '🔄 En cours…' : label}
        </button>
      </div>
      {result && (
        <div className={`text-sm rounded-lg px-3 py-2 ${result.ok ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-700'}`}>
          {result.ok ? '✅ ' : '❌ '}
          {result.ok
            ? (result.data?.message || result.data?.status || JSON.stringify(result.data).slice(0, 200))
            : result.message}
        </div>
      )}
    </div>
  );
}

// ── Status Badge ──────────────────────────────────────────────────────────────

function StatusBadge({ status }) {
  const ok = status === 'ok' || status === 'healthy';
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`}></span>
      {status}
    </span>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState(null);
  const [health, setHealth] = useState(null);
  const [migrationStatus, setMigrationStatus] = useState(null);
  const [matchingTest, setMatchingTest] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    const headers = { 'Content-Type': 'application/json' };

    const safe = async (fn) => { try { return await fn(); } catch { return null; } };

    const [statsRes, healthRes, migRes, matchRes] = await Promise.all([
      safe(() => fetch(`${API_BASE_URL}/stats/aides`, { headers }).then((r) => r.json())),
      safe(() => fetch(`${API_BASE_URL}/health`, { headers }).then((r) => r.json())),
      safe(() => fetch(`${API_BASE_URL}/admin/migration-status`, { headers }).then((r) => r.json())),
      safe(() => fetch(`${API_BASE_URL}/matching/test`, { headers }).then((r) => r.json())),
    ]);

    if (!statsRes || statsRes.detail) setStatsError(statsRes?.detail || 'Erreur de chargement des statistiques');
    else setStats(statsRes);
    setHealth(healthRes);
    setMigrationStatus(migRes);
    setMatchingTest(matchRes);
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // Noindex for admin page
  useEffect(() => {
    const meta = document.createElement('meta');
    meta.name = 'robots';
    meta.content = 'noindex, nofollow';
    document.head.appendChild(meta);
    return () => {
      if (document.head.contains(meta)) {
        document.head.removeChild(meta);
      }
    };
  }, []);

  const callSync = async (endpoint, body) => {
    const headers = { 'Content-Type': 'application/json' };
    if (ADMIN_KEY) headers['X-Admin-Key'] = ADMIN_KEY;
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50">
      <div className="max-w-6xl mx-auto px-4 py-10 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">📊 Dashboard Admin</h1>
            <p className="text-gray-500 text-sm mt-1">AgriSubv — Panneau d'administration</p>
          </div>
          <button
            onClick={fetchAll}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl hover:bg-gray-50 disabled:opacity-60 transition-colors shadow-sm"
          >
            🔄 {loading ? 'Chargement…' : 'Actualiser'}
          </button>
        </div>

        {/* ── 1. Stats Overview ── */}
        <Section title="📈 Vue d'ensemble des aides">
          {statsError ? (
            <p className="text-red-600 text-sm">❌ {statsError}</p>
          ) : loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 animate-pulse">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-20 bg-gray-100 rounded-xl"></div>
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <StatCard label="Total aides" value={stats?.total_aides} icon="📋" color="from-green-500 to-emerald-500" />
                <StatCard label="Aides actives" value={stats?.aides_actives} icon="✅" color="from-blue-500 to-cyan-500" />
                <StatCard label="Aides expirées" value={stats?.aides_expirees} icon="⏰" color="from-amber-500 to-orange-500" />
              </div>

              {stats?.par_source && Object.keys(stats.par_source).length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Répartition par source</p>
                  <div className="space-y-2">
                    {Object.entries(stats.par_source).map(([source, count]) => {
                      const pct = stats.total_aides ? Math.round((count / stats.total_aides) * 100) : 0;
                      return (
                        <div key={source} className="flex items-center gap-3">
                          <span className="text-xs text-gray-600 w-40 truncate">{source}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
                              style={{ width: `${pct}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-gray-700 w-16 text-right">{count} ({pct}%)</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {stats?.par_region && Object.keys(stats.par_region).length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-2">Top régions</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(stats.par_region).slice(0, 10).map(([region, count]) => (
                      <span key={region} className="px-2 py-1 bg-green-50 text-green-800 text-xs rounded-full font-medium">
                        {region} ({count})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </Section>

        {/* ── 2. Sync Panel ── */}
        <Section title="🔄 Gestion des synchronisations">
          <div className="space-y-3">
            <SyncButton
              label="▶ Sync Aides-Territoires V2"
              paramLabel="max_pages"
              paramKey="max_pages"
              paramDefault="5"
              onAction={(maxPages) => callSync('/sync/aides-territoires-v2', maxPages ? { max_pages: maxPages } : {})}
            />
            <SyncButton
              label="▶ Sync DataGouv PAC"
              paramLabel="limit"
              paramKey="limit"
              paramDefault="100"
              onAction={(limit) => callSync('/sync/datagouv-pac', limit ? { limit } : {})}
            />
            <SyncButton
              label="▶ Run Migration V2"
              onAction={() => callSync('/admin/run-migration', {})}
            />
          </div>

          {migrationStatus && (
            <div className="mt-4 p-4 bg-gray-50 rounded-xl text-sm">
              <p className="font-semibold text-gray-700 mb-2">Statut migration</p>
              <div className="grid grid-cols-2 gap-2 text-gray-600">
                <span>Aides V2 total :</span>
                <span className="font-medium">{migrationStatus?.aides_v2_collection?.total ?? '—'}</span>
                <span>Aides actives V2 :</span>
                <span className="font-medium">{migrationStatus?.aides_v2_collection?.active ?? '—'}</span>
                {migrationStatus.status && (
                  <>
                    <span>Statut :</span>
                    <StatusBadge status={migrationStatus.status} />
                  </>
                )}
              </div>
            </div>
          )}
        </Section>

        {/* ── 3. Health & System Status ── */}
        <Section title="💚 Santé du système">
          {loading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(3)].map((_, i) => <div key={i} className="h-8 bg-gray-100 rounded-xl"></div>)}
            </div>
          ) : (
            <div className="space-y-4">
              {health ? (
                <div className="flex flex-wrap gap-4 items-center">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">API :</span>
                    <StatusBadge status={health.status} />
                  </div>
                  {health.version && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">Version :</span>
                      <span className="text-sm font-medium text-gray-800">{health.version}</span>
                    </div>
                  )}
                  {health.timestamp && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">Timestamp :</span>
                      <span className="text-sm font-mono text-gray-700">{health.timestamp}</span>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-red-600 text-sm">❌ Impossible de joindre l'API health</p>
              )}

              {matchingTest !== null && (
                <div className="p-3 bg-gray-50 rounded-xl">
                  <p className="text-sm font-semibold text-gray-700 mb-1">Test moteur de matching</p>
                  <pre className="text-xs text-gray-600 overflow-auto max-h-40 whitespace-pre-wrap">
                    {JSON.stringify(matchingTest, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </Section>
      </div>
    </div>
  );
}

// ── Exported Component ────────────────────────────────────────────────────────

export default function AdminDashboard() {
  return (
    <AuthGate>
      <div className="app">
        <Header />
        <main className="flex-1">
          <Dashboard />
        </main>
        <Footer />
      </div>
    </AuthGate>
  );
}
