import React, { useEffect, useState } from 'react';
import { fetchPatients, deletePatient } from '../api/patient';

export default function PatientTable() {
  const [patients, setPatients] = useState([]);
  const [skip, setSkip] = useState(0);
  const limit = 20;

  const load = async () => {
    const data = await fetchPatients(skip, limit);
    setPatients(data);
  };

  useEffect(() => { load(); }, [skip]);

  const onDelete = async (id) => {
    if (window.confirm('Delete patient?')) {
      await deletePatient(id);
      load();
    }
  };

  return (
    <div className="p-4">
      <table className="min-w-full bg-white">
        <thead>
          <tr>
            <th>ID</th><th>Study ID</th><th>Created</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map(p => (
            <tr key={p.patient_id} className="border-t">
              <td>{p.patient_id}</td>
              <td>{p.study_identifier}</td>
              <td>{new Date(p.created_at).toLocaleString()}</td>
              <td>
                <button onClick={() => {/* navigate to detail */}} className="mr-2">View</button>
                <button onClick={() => onDelete(p.patient_id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4">
        <button disabled={skip === 0} onClick={() => setSkip(skip - limit)}>Prev</button>
        <button onClick={() => setSkip(skip + limit)}>Next</button>
      </div>
    </div>
  );
}
