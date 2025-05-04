// src/components/NewPatientForm.jsx

import React, { useState } from 'react';
import { createPatient } from '../api/patient';
import { useNotifications } from '../context/NotificationContext';

export default function NewPatientForm({ onSuccess }) {
  const [studyId, setStudyId] = useState('');
  const [loading, setLoading] = useState(false);
  const { addToast } = useNotifications();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createPatient({ study_identifier: studyId });
      addToast('Patient created', 'success');
      setStudyId('');
      onSuccess?.();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to create', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        placeholder="Study Identifier"
        value={studyId}
        onChange={(e) => setStudyId(e.target.value)}
        disabled={loading}
        className="border px-2 py-1 w-full"
        required
      />
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? 'Creating…' : 'Create Patient'}
      </button>
    </form>
  );
}
