// src/App.jsx

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PatientTable from './components/PatientTable';
import NewPatientForm from './components/NewPatientForm';
import PatientDetail from './components/PatientDetail';
import Modal from './components/Modal';
import { NotificationProvider } from './context/NotificationContext';
import PatientDetailPage from './pages/PatientDetailPage';

function Header({ onAdd }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h1 className="text-2xl font-bold">NeuroCapture – Patients</h1>
      <button
        onClick={onAdd}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Add Patient
      </button>
    </div>
  );
}

export default function App() {
  const [addOpen, setAddOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);

  const handleAddSuccess = () => {
    setAddOpen(false);
    setRefreshCount((c) => c + 1);
  };

  const handleEditSuccess = () => {
    setEditId(null);
    setRefreshCount((c) => c + 1);
  };

  return (
    <NotificationProvider>
      <Router>
        <div className="container mx-auto p-4">
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <Header onAdd={() => setAddOpen(true)} />

                  <PatientTable
                    onEdit={(id) => setEditId(id)}
                    refresh={refreshCount}
                  />

                  <Modal
                    isOpen={addOpen}
                    onClose={() => setAddOpen(false)}
                    title="Add New Patient"
                  >
                    <NewPatientForm onSuccess={handleAddSuccess} />
                  </Modal>

                  <Modal
                    isOpen={editId !== null}
                    onClose={() => setEditId(null)}
                    title="Edit Patient"
                  >
                    {editId !== null && (
                      <PatientDetail
                      patientId={editId}
                      onSuccess={handleEditSuccess}
                    />
                    )}
                  </Modal>
                </>
              }
            />

            <Route
              path="/patients/:id"
              element={<PatientDetailPage />}
            />
          </Routes>
        </div>
      </Router>
    </NotificationProvider>
  );
}
