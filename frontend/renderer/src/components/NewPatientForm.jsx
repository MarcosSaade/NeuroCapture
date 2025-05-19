// frontend/renderer/src/components/NewPatientForm.jsx
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
    if (studyId.trim().length < 1 || studyId.trim().length > 50) {
      setError('Study ID must be between 1 and 50 characters.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await createPatient({ study_identifier: studyId.trim() });
      addToast('Patient created successfully!', 'success');
      setStudyId(''); // Reset form
      onSuccess?.(); // Callback for parent component
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to create patient. Please try again.';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="studyId" className="block text-sm font-medium text-gray-700 mb-1">
          Study Identifier
        </label>
        <input
          id="studyId"
          type="text"
          placeholder="e.g., P001_SITE_A (1-50 chars)"
          value={studyId}
          onChange={(e) => setStudyId(e.target.value)}
          disabled={loading}
          className={`w-full px-3 py-2 border ${
            error ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
          } rounded-md shadow-sm sm:text-sm`}
          required
          aria-describedby={error ? "studyId-error" : undefined}
        />
        {error && <p id="studyId-error" className="mt-1 text-xs text-red-600">{error}</p>}
      </div>
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60 transition-colors"
        >
          {loading ? 'Creating…' : 'Create Patient'}
        </button>
      </div>
    </form>
  );
}