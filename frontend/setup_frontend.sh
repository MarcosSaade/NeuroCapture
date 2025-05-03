#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Setting up Patient Management frontend..."

# 1. Ensure we're in the correct directory
if [[ ! -f package.json ]]; then
  echo "Error: package.json not found. Run this script from your React project root."
  exit 1
fi

# 2. Create directories
echo "📁 Creating src/api and src/components..."
mkdir -p src/api src/components

# 3. Write src/api/patient.js
cat > src/api/patient.js << 'EOF'
// src/api/patient.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export async function fetchPatients(skip = 0, limit = 20) {
  const resp = await api.get('/patients/', { params: { skip, limit } });
  return resp.data;
}

export async function createPatient(data) {
  const resp = await api.post('/patients/', data);
  return resp.data;
}

export async function getPatient(id) {
  const resp = await api.get(`/patients/${id}`);
  return resp.data;
}

export async function updatePatient(id, data) {
  const resp = await api.put(`/patients/${id}`, data);
  return resp.data;
}

export async function deletePatient(id) {
  await api.delete(`/patients/${id}`);
}
EOF

# 4. Write src/components/PatientTable.jsx
cat > src/components/PatientTable.jsx << 'EOF'
import React, { useEffect, useState } from 'react';
import { fetchPatients, deletePatient } from '../api/patient';

export default function PatientTable() {
  const [patients, setPatients] = useState([]);
  const [skip, setSkip] = useState(0);
  const limit = 20;

  const load = async () => {
    const data = await fetchPatients(skip, limit);
    setPatients(data);
  };

  useEffect(() => { load(); }, [skip]);

  const onDelete = async (id) => {
    if (window.confirm('Delete patient?')) {
      await deletePatient(id);
      load();
    }
  };

  return (
    <div className="p-4">
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th>ID</th><th>Study ID</th><th>Created</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map(p => (
            <tr key={p.patient_id} className="border-t">
              <td>{p.patient_id}</td>
              <td>{p.study_identifier}</td>
              <td>{new Date(p.created_at).toLocaleString()}</td>
              <td>
                <button onClick={() => {/* navigate to detail */}} className="mr-2">View</button>
                <button onClick={() => onDelete(p.patient_id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4">
        <button disabled={skip === 0} onClick={() => setSkip(skip - limit)}>Prev</button>
        <button onClick={() => setSkip(skip + limit)}>Next</button>
      </div>
    </div>
  );
}
EOF

# 5. Write src/components/NewPatientForm.jsx
cat > src/components/NewPatientForm.jsx << 'EOF'
import React, { useState } from 'react';
import { createPatient } from '../api/patient';

export default function NewPatientForm({ onCreated }) {
  const [studyId, setStudyId] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const p = await createPatient({ study_identifier: studyId });
      setStudyId('');
      onCreated(p);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-gray-50 rounded">
      <label className="block">
        Study Identifier
        <input
          className="mt-1 block w-full border rounded p-1"
          value={studyId}
          onChange={e => setStudyId(e.target.value)}
          required
        />
      </label>
      {error && <div className="text-red-600 mt-1">{error}</div>}
      <button type="submit" className="mt-2 px-4 py-2 bg-blue-600 text-white rounded">
        Create Patient
      </button>
    </form>
  );
}
EOF

# 6. Write src/components/PatientDetail.jsx
cat > src/components/PatientDetail.jsx << 'EOF'
import React, { useEffect, useState } from 'react';
import { getPatient, updatePatient } from '../api/patient';
import { useParams, useNavigate } from 'react-router-dom';

export default function PatientDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [patient, setPatient] = useState(null);
  const [studyId, setStudyId] = useState('');

  useEffect(() => {
    (async () => {
      const p = await getPatient(id);
      setPatient(p);
      setStudyId(p.study_identifier);
    })();
  }, [id]);

  const handleUpdate = async () => {
    await updatePatient(id, { study_identifier: studyId });
    nav('/');
  };

  if (!patient) return <div>Loading…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl">Patient {patient.patient_id}</h2>
      <label className="block mt-2">
        Study Identifier
        <input
          className="mt-1 block w-full border rounded p-1"
          value={studyId}
          onChange={e => setStudyId(e.target.value)}
        />
      </label>
      <div className="mt-4">
        <button onClick={handleUpdate} className="px-4 py-2 bg-green-600 text-white rounded mr-2">
          Save
        </button>
        <button onClick={() => nav('/')} className="px-4 py-2 bg-gray-400 text-white rounded">
          Cancel
        </button>
      </div>
    </div>
  );
}
EOF

# 7. Overwrite src/App.jsx
cat > src/App.jsx << 'EOF'
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PatientTable from './components/PatientTable';
import NewPatientForm from './components/NewPatientForm';
import PatientDetail from './components/PatientDetail';

export default function App() {
  return (
    <BrowserRouter>
      <div className="container mx-auto">
        <h1 className="text-2xl my-4">Patient Management</h1>
        <NewPatientForm onCreated={() => window.location.reload()} />
        <Routes>
          <Route path="/" element={<PatientTable />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
EOF

# 8. Install required packages
echo "📦 Installing Axios and React Router..."
npm install axios react-router-dom

echo "✅ Frontend setup complete! You can now run 'npm start'."
