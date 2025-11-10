import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'https://agrisubv-backend.onrender.com';

const REGIONS = [
  'Auvergne-Rhône-Alpes',
  'Bourgogne-Franche-Comté',
  'Bretagne',
  'Centre-Val de Loire',
  'Grand Est',
  'Hauts-de-France',
  'Ile-de-France',
  'Normandie',
  'Nouvelle-Aquitaine',
  'Occitanie',
  'Pays de la Loire',
  'Provence-Alpes-Côte d’Azur',
  'Corse'
];

const STATUTS_JURIDIQUES = [
  'Société',
  'Individuel',
  'Réseau',
  'Coopérative',
  'Autre'
];

function App() {
  const [formData, setFormData] = useState({
    region: '',
    departement: '',
    statut_juridique: '',
    superficie_ha: '',
    age_exploitant: '',
    jeune_agriculteur: false
  });

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/eligibilite`, formData);
      setResults(response.data);
    } catch (err) {
      setError('An error occurred while fetching data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Agricultural Eligibility App</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="region">Select Region:</label>
        <select name="region" onChange={handleChange} value={formData.region}>
          {REGIONS.map((region, index) => (
            <option key={index} value={region}>{region}</option>
          ))}
        </select>
        <label htmlFor="departement">Département:</label>
        <input type="text" name="departement" onChange={handleChange} value={formData.departement} />
        <label htmlFor="statut_juridique">Statut Juridique:</label>
        <select name="statut_juridique" onChange={handleChange} value={formData.statut_juridique}>
          {STATUTS_JURIDIQUES.map((statut, index) => (
            <option key={index} value={statut}>{statut}</option>
          ))}
        </select>
        <label htmlFor="superficie_ha">Superficie en Ha:</label>
        <input type="number" name="superficie_ha" onChange={handleChange} value={formData.superficie_ha} />
        <label htmlFor="age_exploitant">Âge de l’Exploitant:</label>
        <input type="number" name="age_exploitant" onChange={handleChange} value={formData.age_exploitant} />
        <label>
          <input type="checkbox" name="jeune_agriculteur" onChange={handleChange} checked={formData.jeune_agriculteur} /> Jeune Agriculteur
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Loading...' : 'Submit'}</button>
      </form>
      {error && <p>{error}</p>}
      <div>
        {results.length > 0 && <h2>Results:</h2>}
        {results.map((result, index) => (
          <div key={index} className="result-card">
            {/* Card component for displaying result information */}
          </div>
        ))}
      </div>
      <footer>
        <p>© 2025 Your Company. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;