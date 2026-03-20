import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-green-50 via-white to-emerald-50 px-4">
      <div className="text-center max-w-md">
        <div className="text-8xl font-bold text-green-600 mb-4">404</div>
        <h1 className="text-2xl font-semibold text-gray-800 mb-3">Page introuvable</h1>
        <p className="text-gray-500 mb-8">
          La page que vous cherchez n&apos;existe pas ou a été déplacée.
        </p>
        <button
          onClick={() => navigate('/')}
          className="btn btn-primary"
        >
          ← Retour à l&apos;accueil
        </button>
      </div>
    </div>
  );
}
