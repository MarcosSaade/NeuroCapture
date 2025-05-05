// src/pages/PatientDetailPage.jsx

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PatientDetail from '../components/PatientDetail';
import { ToastContainer } from '../components/Toast';

export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="container mx-auto p-4">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 px-3 py-1 bg-gray-200 rounded"
      >
        ← Back
      </button>

      <h2 className="text-xl font-semibold mb-2">Patient Details</h2>
      {/* Reuse PatientDetail component in read-only mode */}
      <PatientDetail patientId={id} readOnly />
      <ToastContainer />
    </div>
  );
}
