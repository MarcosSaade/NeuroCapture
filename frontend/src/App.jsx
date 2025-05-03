import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PatientTable from './components/PatientTable';
import NewPatientForm from './components/NewPatientForm';
import PatientDetail from './components/PatientDetail';

export default function App() {
  return (
    <BrowserRouter>
      <div className="container mx-auto">
        <h1 className="text-2xl my-4">Patient Management</h1>
        <NewPatientForm onCreated={() => window.location.reload()} />
        <Routes>
          <Route path="/" element={<PatientTable />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
