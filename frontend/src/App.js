import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'https://your-api-url/api'; // Replace with your actual API URL

function App() {
    const [formData, setFormData] = useState({
        region: '',
        departement: '',
        statut_juridique: '',
        superficie_ha: '',
        productions: [],
        labels: [],
        projets: [],
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
        setResults({ ...results, loading: true, error: '' });
        try {
            const response = await axios.post(`${API_BASE_URL}/eligibilite`, formData);
            setResults({ ...results, aidesEligibles: response.data, loading: false });
        } catch (error) {
            setResults({ ...results, loading: false, error: error.message });
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">AgriSubv Application</h1>
            <form onSubmit={handleSubmit} className="mb-4">
                <select name="region" onChange={handleChange} className="mb-2">
                    <option value="">Select Region</option>
                    {/* Add options here */}
                </select>
                <input type="number" name="superficie_ha" value={formData.superficie_ha} onChange={handleChange} placeholder="Superficie (ha)" className="mb-2" />
                {/* Other input fields for departement, statut_juridique, etc. */}
                <button type="submit" className="btn bg-blue-500 text-white px-4 py-2">Check Aides</button>
            </form>
            <div>
                {results.loading && <p>Loading...</p>}
                {results.error && <p className="text-red-500">Error: {results.error}</p>}
                <ul className="results-list">
                    {results.aidesEligibles.map((aide, index) => (
                        <li key={index} className="mb-2">
                            <h2 className="font-semibold">{aide.title} (Score: {aide.score})</h2>
                            <p>Organisme: {aide.organisme}</p>
                            <p>Montant: {aide.montant}</p>
                            <p>Conditions: {aide.conditions}</p>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default App;