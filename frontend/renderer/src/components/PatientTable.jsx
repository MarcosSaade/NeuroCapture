// src/components/PatientTable.jsx

import React, { useState, useEffect } from 'react';
import { fetchPatients, deletePatient } from '../api/patient';
import { useNotifications } from '../context/NotificationContext';

export default function PatientTable({ onEdit, refresh }) {
  const [patients, setPatients] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { addToast } = useNotifications();

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchPatients(skip, limit);
      setPatients(data);
    } catch {
      setError('Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  // reload whenever skip or refresh changes
  useEffect(() => {
    load();
  }, [skip, refresh]);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this patient?')) return;
    try {
      await deletePatient(id);
      addToast('Patient deleted', 'success');
      load();
    } catch {
      addToast('Failed to delete patient', 'error');
    }
  };

  if (loading) return <div>Loading patients…</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <>
      <table className="table-auto w-full mb-4">
        <thead>
          <tr>
            <th>ID</th>
            <th>Study ID</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p.patient_id}>
              <td>{p.patient_id}</td>
              <td>{p.study_identifier}</td>
              <td>{new Date(p.created_at).toLocaleString()}</td>
              <td className="space-x-2">
                <button onClick={() => onEdit(p.patient_id)} className="text-blue-600">
                  Edit
                </button>
                <button onClick={() => handleDelete(p.patient_id)} className="text-red-600">
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex justify-between">
        <button
          onClick={() => setSkip((s) => Math.max(0, s - limit))}
          disabled={skip === 0}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Prev
        </button>
        <button
          onClick={() => setSkip((s) => s + limit)}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Next
        </button>
      </div>
    </>
  );
}
