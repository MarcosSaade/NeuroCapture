// frontend/renderer/src/App.jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PatientTable from './components/PatientTable';
import NewPatientForm from './components/NewPatientForm';
import PatientDetail from './components/PatientDetail';
import Modal from './components/Modal';
import { NotificationProvider, useNotifications } from './context/NotificationContext';
import { ToastContainer } from './components/Toast'; 
import PatientDetailPage from './pages/PatientDetailPage';

function Header({ onAddPatient }) {
  return (
    <header className="bg-slate-800 text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold hover:text-slate-300 transition-colors">
          NeuroCapture
        </Link>
        <button
          onClick={onAddPatient}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow transition-colors"
        >
          Add Patient
        </button>
      </div>
    </header>
  );
}

function AppContent() {
  const [addPatientModalOpen, setAddPatientModalOpen] = useState(false);
  const [editingPatientId, setEditingPatientId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0); // Used to trigger re-fetch in PatientTable

  const handlePatientAdded = () => {
    setAddPatientModalOpen(false);
    setRefreshKey(prev => prev + 1);
  };

  const handlePatientModalClosed = () => {
    setEditingPatientId(null);
    setRefreshKey(prev => prev + 1); // Refresh table after edit modal closes
  };
  
  const handlePatientDeleted = () => {
    setEditingPatientId(null); // Close modal if patient was deleted from it
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <Header onAddPatient={() => setAddPatientModalOpen(true)} />
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <Routes>
          <Route
            path="/"
            element={
              <PatientTable
                onEdit={(id) => setEditingPatientId(id)}
                refresh={refreshKey}
              />
            }
          />
          <Route
            path="/patients/:patientId" // Changed from :id to :patientId for clarity
            element={<PatientDetailPage />}
          />
        </Routes>
      </main>

      <Modal
        isOpen={addPatientModalOpen}
        onClose={() => setAddPatientModalOpen(false)}
        title="Add New Patient"
        size="xl"
      >
        <NewPatientForm onSuccess={handlePatientAdded} />
      </Modal>

      {editingPatientId && (
        <Modal
          isOpen={editingPatientId !== null}
          onClose={handlePatientModalClosed}
          title={`Edit Patient (ID: ${editingPatientId})`}
          size="5xl" // Increased size for tabs
        >
          <PatientDetail
            patientId={editingPatientId}
            onSuccess={handlePatientModalClosed} // General success (e.g. study ID update)
            onDeleted={handlePatientDeleted} // Specifically after patient deletion
          />
        </Modal>
      )}
      <ToastContainer />
    </div>
  );
}

export default function App() {
  return (
    <NotificationProvider>
      <Router>
        <AppContent />
      </Router>
    </NotificationProvider>
  );
}