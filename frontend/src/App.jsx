const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'https://agrisubv-backend.onrender.com';

const REGIONS = ["Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Bretagne", "Centre-Val de Loire", "Corse", "Grand Est", "Hauts-de-France", "Île-de-France", "Normandie", "Nouvelle-Aquitaine", "Occitanie", "PACA", "Pays de la Loire"];
const STATUTS_JURIDIQUES = ["Exploitation individuelle", "EARL", "GAEC", "SCEA", "Autre"];

// [...] previous lines of code

// comment for line 73
{REGIONS.map((region) => (<option key={region} value={region}>{region}</option>))}

// comment for line 101
{STATUTS_JURIDIQUES.map((statut) => (<option key={statut} value={statut}>{statut}</option>))}

axios.post(`\${API_BASE_URL}/api/eligibilite\`