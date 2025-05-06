// src/components/PatientDetail.jsx

import React, { useState, useEffect } from 'react';
import { getPatient, updatePatient, deletePatient } from '../api/patient';
import { useNotifications } from '../context/NotificationContext';
import DemographicForm from './DemographicForm';

export default function PatientDetail({ patientId, onSuccess }) {
  const { addToast } = useNotifications();
  const [patient, setPatient] = useState(null);
  const [studyId, setStudyId] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getPatient(patientId);
        setPatient(data);
        setStudyId(data.study_identifier);
      } catch {
        addToast('Failed to load patient', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [patientId, addToast]);

  const handleSave = async () => {
    setLoading(true);
    try {
      await updatePatient(patientId, { study_identifier: studyId });
      addToast('Updated successfully', 'success');
      onSuccess?.();
    } catch {
      addToast('Failed to update', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this patient?')) return;
    try {
      await deletePatient(patientId);
      addToast('Patient deleted', 'success');
      onSuccess?.();
    } catch {
      addToast('Delete failed', 'error');
    }
  };

  if (loading) return <div>Loading patient…</div>;
  if (!patient) return <div className="text-red-500">No patient found.</div>;

  return (
    <div className="space-y-6">
      {/* Study Identifier */}
      <div className="space-y-1">
        <label className="block font-medium">Study Identifier:</label>
        <input
          type="text"
          value={studyId}
          onChange={(e) => setStudyId(e.target.value)}
          disabled={loading}
          className="border px-2 py-1 w-full"
        />
        <button
          onClick={handleSave}
          disabled={loading}
          className="mt-2 bg-green-600 text-white px-4 py-2 rounded"
        >
          {loading ? 'Saving…' : 'Save Study ID'}
        </button>
      </div>

      {/* Demographics Section */}
      <div>
        <h3 className="text-lg font-semibold">Demographics</h3>
        <DemographicForm patientId={patientId} onSaved={onSuccess} />
      </div>

      {/* Delete Patient */}
      <button
        onClick={handleDelete}
        className="mt-4 bg-red-600 text-white px-4 py-2 rounded"
      >
        Delete Patient
      </button>
    </div>
  );
}