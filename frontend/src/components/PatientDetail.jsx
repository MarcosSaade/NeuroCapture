import React, { useEffect, useState } from 'react';
import { getPatient, updatePatient } from '../api/patient';
import { useParams, useNavigate } from 'react-router-dom';

export default function PatientDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [patient, setPatient] = useState(null);
  const [studyId, setStudyId] = useState('');

  useEffect(() => {
    (async () => {
      const p = await getPatient(id);
      setPatient(p);
      setStudyId(p.study_identifier);
    })();
  }, [id]);

  const handleUpdate = async () => {
    await updatePatient(id, { study_identifier: studyId });
    nav('/');
  };

  if (!patient) return <div>Loading…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl">Patient {patient.patient_id}</h2>
      <label className="block mt-2">
        Study Identifier
        <input
          className="mt-1 block w-full border rounded p-1"
          value={studyId}
          onChange={e => setStudyId(e.target.value)}
        />
      </label>
      <div className="mt-4">
        <button onClick={handleUpdate} className="px-4 py-2 bg-green-600 text-white rounded mr-2">
          Save
        </button>
        <button onClick={() => nav('/')} className="px-4 py-2 bg-gray-400 text-white rounded">
          Cancel
        </button>
      </div>
    </div>
  );
}
