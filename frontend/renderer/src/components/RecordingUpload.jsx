// frontend/renderer/src/components/RecordingUpload.jsx
import React, { useState } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { uploadRecording as apiUploadRecording } from '../api/recording'; // Ensure this points to your API call

export default function RecordingUpload({ patientId, assessmentId, onUploaded, compact = false }) {
  const { addToast } = useNotifications();
  const [taskType, setTaskType] = useState('');
  const [device, setDevice] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      addToast('Please select an audio file.', 'error');
      return;
    }
    if (!taskType && !compact) { // Task type might not be needed for compact mode if context is clear
        addToast('Please provide a task type.', 'error');
        return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    // Use a default task type if in compact mode and not provided, or make it required
    formData.append('task_type', taskType || (compact ? "Assessment Recording" : "")); 
    formData.append('recording_device', device || 'Unknown');

    try {
      const newRecording = await apiUploadRecording(patientId, assessmentId, formData);
      addToast('Recording uploaded successfully!', 'success');
      onUploaded?.(newRecording); // Callback to parent
      // Reset form
      setTaskType('');
      setDevice('');
      setFile(null);
      if (e.target.elements.fileInput) e.target.elements.fileInput.value = null; // Clear file input
    } catch (err) {
      addToast(`Upload failed: ${err.message || 'Unknown error'}`, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  if (compact) {
    return (
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <div className="flex-grow">
          <label htmlFor={`fileInput-${assessmentId}`} className="sr-only">Audio File</label>
          <input
            id={`fileInput-${assessmentId}`}
            name="fileInput"
            type="file"
            accept="audio/*"
            onChange={e => setFile(e.target.files[0] || null)}
            required
            className="block w-full text-sm text-gray-500 file:mr-2 file:py-1 file:px-2 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !file}
          className="px-3 py-1.5 bg-blue-500 text-white text-sm rounded-md shadow-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
        >
          {loading ? '...' : 'Upload'}
        </button>
      </form>
    );
  }


  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-1 bg-slate-50 rounded-md">
      <div>
        <label htmlFor="taskType" className="block text-sm font-medium text-gray-700">Task Type / Name</label>
        <input
          id="taskType"
          type="text"
          value={taskType}
          onChange={e => setTaskType(e.target.value)}
          required
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="e.g., Story Recall, Picture Description"
        />
      </div>

      <div>
        <label htmlFor="device" className="block text-sm font-medium text-gray-700">Recording Device (Optional)</label>
        <input
          id="device"
          type="text"
          value={device}
          onChange={e => setDevice(e.target.value)}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="e.g., Smartphone, Zoom H2n"
        />
      </div>

      <div>
        <label htmlFor="fileInput" className="block text-sm font-medium text-gray-700">Audio File</label>
        <input
          id="fileInput"
          name="fileInput" // Add name to allow reset via form.elements
          type="file"
          accept="audio/*" // Suggests audio files to the browser
          onChange={e => setFile(e.target.files[0] || null)}
          required
          className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading || !file}
          className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Uploading...' : 'Upload Recording'}
        </button>
      </div>
    </form>
  );
}