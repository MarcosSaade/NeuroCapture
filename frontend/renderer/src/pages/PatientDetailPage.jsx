// frontend/renderer/src/pages/PatientDetailPage.jsx
import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import PatientDetail from '../components/PatientDetail'; // Re-using the enhanced component
import { ArrowLeftIcon } from '@heroicons/react/24/solid'; // Example for a back button icon

export default function PatientDetailPage() {
  const { patientId } = useParams();
  const navigate = useNavigate();

  // The PatientDetail component now handles its own data fetching and tab logic.
  // This page becomes a simple wrapper.

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-slate-600 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 transition-colors"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Back to List
        </button>
        <h1 className="text-2xl font-semibold text-gray-800">Patient Details</h1>
        <div>{/* Placeholder for potential future actions */}</div>
      </div>
      
      <div className="bg-white shadow-xl rounded-lg p-6">
        <PatientDetail patientId={parseInt(patientId)} />
      </div>
    </div>
  );
}