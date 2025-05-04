import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PatientTable from './components/PatientTable';
import PatientDetail from './components/PatientDetail';
import NewPatientForm from './components/NewPatientForm';
import { NotificationProvider } from './context/NotificationContext';
import { ToastContainer } from './components/Toast';

export default function App() {
  return (
    <NotificationProvider>
      <Router>
        <div className="container mx-auto p-4">
          <h1 className="text-2xl font-bold mb-4">NeuroCapture – Patients</h1>
          <NewPatientForm />
          <Routes>
            <Route path="/" element={<PatientTable />} />
            <Route path="/patients/:id" element={<PatientDetail />} />
          </Routes>
        </div>
      </Router>
      <ToastContainer />
    </NotificationProvider>
  );
}
