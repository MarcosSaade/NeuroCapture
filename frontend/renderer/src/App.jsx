/**
 * NeuroCapture Main Application Component
 * 
 * Root component for the NeuroCapture Electron application.
 * Manages global application state, routing, and modal interactions.
 * 
 * Features:
 * - Patient management interface
 * - Modal-based patient editing
 * - Real-time notifications
 * - Responsive navigation
 * 
 * @author NeuroCapture Development Team
 */

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PatientTable from './components/PatientTable';
import NewPatientForm from './components/NewPatientForm';
import PatientDetail from './components/PatientDetail';
import Modal from './components/Modal';
import { NotificationProvider } from './context/NotificationContext';
import { ToastContainer } from './components/Toast'; 
import PatientDetailPage from './pages/PatientDetailPage';

/**
 * Application header with navigation and primary actions
 */
function Header({ onAddPatient }) {
  return (
    <header className="bg-slate-800 text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link 
          to="/" 
          className="text-2xl font-bold hover:text-slate-300 transition-colors"
          title="Return to patient list"
        >
          NeuroCapture
        </Link>
        <button
          onClick={onAddPatient}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow transition-colors"
          title="Add new patient to study"
        >
          Add Patient
        </button>
      </div>
    </header>
  );
}

/**
 * Main application content with routing and state management
 */
function AppContent() {
  const [addPatientModalOpen, setAddPatientModalOpen] = useState(false);
  const [editingPatientId, setEditingPatientId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  /**
   * Handle successful patient creation
   */
  const handlePatientAdded = () => {
    setAddPatientModalOpen(false);
    setRefreshKey(prev => prev + 1);
  };

  /**
   * Handle patient modal closure (after edit/update)
   */
  const handlePatientModalClosed = () => {
    setEditingPatientId(null);
    setRefreshKey(prev => prev + 1);
  };
  
  /**
   * Handle patient deletion
   */
  const handlePatientDeleted = () => {
    setEditingPatientId(null);
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
            path="/patients/:patientId"
            element={<PatientDetailPage />}
          />
        </Routes>
      </main>

      {/* Add Patient Modal */}
      <Modal
        isOpen={addPatientModalOpen}
        onClose={() => setAddPatientModalOpen(false)}
        title="Add New Patient"
        size="xl"
      >
        <NewPatientForm onSuccess={handlePatientAdded} />
      </Modal>

      {/* Edit Patient Modal */}
      {editingPatientId && (
        <Modal
          isOpen={editingPatientId !== null}
          onClose={handlePatientModalClosed}
          title={`Edit Patient (ID: ${editingPatientId})`}
          size="5xl"
        >
          <PatientDetail
            patientId={editingPatientId}
            onSuccess={handlePatientModalClosed}
            onDeleted={handlePatientDeleted}
          />
        </Modal>
      )}
      
      <ToastContainer />
    </div>
  );
}

/**
 * Root application component with providers
 */
export default function App() {
  return (
    <NotificationProvider>
      <Router>
        <AppContent />
      </Router>
    </NotificationProvider>
  );
}