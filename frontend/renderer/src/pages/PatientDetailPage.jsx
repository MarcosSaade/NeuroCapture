// src/pages/PatientDetailPage.jsx

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useNotifications } from '../context/NotificationContext';
import PatientDetail from '../components/PatientDetail';
import DemographicForm from '../components/DemographicForm';
import Modal from '../components/Modal';

export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useNotifications();

  const [editOpen, setEditOpen] = useState(false);

  const handleEditSuccess = () => {
    setEditOpen(false);
    addToast('Patient updated', 'success');
  };

  const handleDemoSaved = () => {
    addToast('Demographics saved', 'success');
  };

  return (
    <div className="container mx-auto p-4">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="mb-4 px-3 py-1 bg-gray-200 rounded"
      >
        ← Back
      </button>

      {/* Page Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Patient Details</h2>
        <button
          onClick={() => setEditOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Edit
        </button>
      </div>

      {/* Read-only detail */}
      <PatientDetail patientId={id} readOnly />

      {/* Demographics section */}
      <div className="mt-8">
        <h3 className="text-lg font-medium mb-2">Demographics</h3>
        <DemographicForm patientId={id} onSaved={handleDemoSaved} />
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={editOpen}
        onClose={() => setEditOpen(false)}
        title="Edit Patient"
      >
        <PatientDetail patientId={id} onSuccess={handleEditSuccess} />
      </Modal>
    </div>
  );
}
