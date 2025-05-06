// src/components/PatientDetail.jsx

import React, { useState, useEffect } from 'react';
import { getPatient, updatePatient, deletePatient } from '../api/patient';
import {
  fetchAssessments,
  createAssessment,
  updateAssessment,
  deleteAssessment
} from '../api/assessment';
import { useNotifications } from '../context/NotificationContext';
import DemographicForm from './DemographicForm';
import AssessmentForm from './AssessmentForm';
import AssessmentList from './AssessmentList';

export default function PatientDetail({ patientId, onSuccess }) {
  const { addToast } = useNotifications();

  // Patient data
  const [patient, setPatient] = useState(null);
  const [studyId, setStudyId] = useState('');
  const [loadingPatient, setLoadingPatient] = useState(true);

  // Assessments data
  const [assessments, setAssessments] = useState([]);
  const [editingAssessment, setEditingAssessment] = useState(null);

  // Load patient
  useEffect(() => {
    (async () => {
      try {
        const data = await getPatient(patientId);
        setPatient(data);
        setStudyId(data.study_identifier);
      } catch {
        addToast('Failed to load patient', 'error');
      } finally {
        setLoadingPatient(false);
      }
    })();
  }, [patientId, addToast]);

  // Load assessments
  const loadAsses = async () => {
    try {
      const arr = await fetchAssessments(patientId);
      setAssessments(arr);
    } catch {
      addToast('Failed to load assessments', 'error');
    }
  };
  useEffect(() => { loadAsses(); }, [patientId]);

  // Save Study ID
  const handleSavePatient = async () => {
    setLoadingPatient(true);
    try {
      await updatePatient(patientId, { study_identifier: studyId });
      addToast('Study ID updated', 'success');
      onSuccess?.();               // closes patient modal
    } catch {
      addToast('Failed to update', 'error');
    } finally {
      setLoadingPatient(false);
    }
  };

  // Delete patient
  const handleDeletePatient = async () => {
    if (!window.confirm('Delete this patient?')) return;
    try {
      await deletePatient(patientId);
      addToast('Patient deleted', 'success');
      onSuccess?.();
    } catch {
      addToast('Delete failed', 'error');
    }
  };

  if (loadingPatient) return <div>Loading patient…</div>;
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
          disabled={loadingPatient}
          className="border px-2 py-1 w-full"
        />
        <button
          onClick={handleSavePatient}
          disabled={loadingPatient}
          className="mt-2 bg-green-600 text-white px-4 py-2 rounded"
        >
          Save Study ID
        </button>
      </div>

      {/* Demographics */}
      <div>
        <h3 className="text-lg font-semibold">Demographics</h3>
        <DemographicForm patientId={patientId} onSaved={onSuccess} />
      </div>

      {/* Cognitive Assessments */}
      <div>
        <h3 className="text-lg font-semibold">Cognitive Assessments</h3>

        <AssessmentForm
          patientId={patientId}
          // pass the assessment to edit, or null for new
          initialData={editingAssessment}
          onSaved={() => {
            setEditingAssessment(null);
            loadAsses();          // reload list
            // Note: do NOT call onSuccess here, so modal stays open
          }}
        />

        <AssessmentList
          assessments={assessments}
          onEdit={(a) => {
            // Pre-fill form for editing
            setEditingAssessment(a);
          }}
          onDelete={async (id) => {
            if (!window.confirm('Delete this assessment?')) return;
            await deleteAssessment(patientId, id);
            addToast('Assessment deleted', 'success');
            loadAsses();
          }}
        />
      </div>

      {/* Delete Patient */}
      <button
        onClick={handleDeletePatient}
        className="mt-4 bg-red-600 text-white px-4 py-2 rounded"
      >
        Delete Patient
      </button>
    </div>
  );
}
