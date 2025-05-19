// src/components/RecordingList.jsx
import React from 'react';
import api from '../api/patient';

export default function RecordingList({
  recordings,
  patientId,
  assessmentId,
  onDeleted,
  onExtractFeatures
}) {
  if (!recordings.length) {
    return <div className="text-gray-500">No recordings yet.</div>;
  }

  const handleDelete = async id => {
    if (!window.confirm('Delete this recording?')) return;
    try {
      await api.delete(
        `/patients/${patientId}/assessments/${assessmentId}/recordings/${id}`
      );
      onDeleted(id);
    } catch {
      alert('Delete failed');
    }
  };

  return (
    <ul className="space-y-4">
      {recordings.map(r => (
        <li key={r.recording_id} className="border p-2 rounded">
          <div className="flex items-center space-x-4">
            <audio controls src={r.file_path} className="flex-1" />
            <span className="text-sm text-gray-600">
              {new Date(r.recording_date).toLocaleString()}
            </span>
            <button
              onClick={() => handleDelete(r.recording_id)}
              className="text-red-600 hover:underline"
            >
              Delete
            </button>
            <button
              onClick={() => onExtractFeatures(r)}
              className="text-green-600 hover:underline"
            >
              Extract Features
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
