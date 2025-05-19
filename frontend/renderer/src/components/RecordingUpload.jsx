// src/components/RecordingUpload.jsx

import React, { useState } from 'react';
import Modal from './Modal';
import { uploadRecording } from '../api/recording';

export default function RecordingUpload({ patientId, assessmentId, onUploaded }) {
  const [isOpen, setIsOpen] = useState(false);
  const [taskType, setTaskType] = useState('');
  const [device, setDevice] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const form = new FormData();
    form.append('file', file);
    form.append('task_type', taskType);
    form.append('recording_device', device);

    try {
      const rec = await uploadRecording(patientId, assessmentId, form);
      onUploaded(rec);
      setIsOpen(false);
      setTaskType('');
      setDevice('');
      setFile(null);
    } catch (err) {
      console.error(err);
      alert('Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="px-4 py-2 bg-green-600 text-white rounded"
        disabled={!assessmentId}
        title={assessmentId ? 'Add a new recording' : 'Please select an assessment first'}
      >
        Add Recording
      </button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Upload Audio Recording"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Task Type</label>
            <input
              type="text"
              value={taskType}
              onChange={e => setTaskType(e.target.value)}
              required
              className="border px-2 py-1 w-full"
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Recording Device</label>
            <input
              type="text"
              value={device}
              onChange={e => setDevice(e.target.value)}
              required
              className="border px-2 py-1 w-full"
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Audio File</label>
            <input
              type="file"
              accept="audio/*"
              onChange={e => setFile(e.target.files[0] || null)}
              required
              className="w-full"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            {loading ? 'Uploading…' : 'Upload'}
          </button>
        </form>
      </Modal>
    </>
  );
}
