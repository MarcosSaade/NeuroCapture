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
