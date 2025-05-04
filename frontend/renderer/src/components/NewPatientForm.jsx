// src/components/NewPatientForm.jsx

import React, { useState } from 'react';
import { createPatient } from '../api/patient';
import { useNotifications } from '../context/NotificationContext';

export default function NewPatientForm({ onSuccess }) {
  const [studyId, setStudyId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { addToast } = useNotifications();

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Client-side validation
    if (studyId.length < 3 || studyId.length > 50) {
      setError('Study ID must be 3–50 characters');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await createPatient({ study_identifier: studyId });
      addToast('Patient created', 'success');
      setStudyId('');
      onSuccess?.();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to create patient';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div>
        <input
          type="text"
          placeholder="Study Identifier (3–50 chars)"
          value={studyId}
          onChange={(e) => setStudyId(e.target.value)}
          disabled={loading}
          className={`border px-2 py-1 w-full ${
            error ? 'border-red-500' : 'border-gray-300'
          } rounded`}
          required
        />
        {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
      </div>
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Creating…' : 'Create Patient'}
      </button>
    </form>
  );
}
