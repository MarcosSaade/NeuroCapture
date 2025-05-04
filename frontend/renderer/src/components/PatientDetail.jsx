import React, { useState, useEffect } from 'react';
import { getPatient, updatePatient, deletePatient } from '../api/patient';
import { useParams, useNavigate } from 'react-router-dom';
import { useNotifications } from '../context/NotificationContext';

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useNotifications();

  const [patient, setPatient] = useState(null);
  const [studyId, setStudyId] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getPatient(id);
        setPatient(data);
        setStudyId(data.study_identifier);
      } catch {
        addToast('Failed to load patient', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const handleSave = async () => {
    setLoading(true);
    try {
      await updatePatient(id, { study_identifier: studyId });
      addToast('Updated successfully', 'success');
      navigate('/');
    } catch {
      addToast('Failed to update', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this patient?')) return;
    try {
      await deletePatient(id);
      addToast('Patient deleted', 'success');
      navigate('/');
    } catch {
      addToast('Delete failed', 'error');
    }
  };

  if (loading) return <div>Loading patient…</div>;
  if (!patient) return <div className="text-red-500">No patient found.</div>;

  return (
    <div className="space-y-4">
      <div>
        <label className="block">Study Identifier:</label>
        <input
          type="text"
          value={studyId}
          onChange={(e) => setStudyId(e.target.value)}
          disabled={loading}
          className="border px-2 py-1 w-full"
        />
      </div>
      <div className="space-x-2">
        <button onClick={handleSave} disabled={loading} className="bg-green-600 text-white px-4 py-1 rounded">
          {loading ? 'Saving…' : 'Save'}
        </button>
        <button onClick={handleDelete} className="bg-red-600 text-white px-4 py-1 rounded">
          Delete
        </button>
        <button onClick={() => navigate('/')} className="bg-gray-400 text-white px-4 py-1 rounded">
          Cancel
        </button>
      </div>
    </div>
  );
}
