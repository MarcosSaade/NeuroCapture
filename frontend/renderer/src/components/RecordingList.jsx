// frontend/renderer/src/components/RecordingList.jsx
import React from 'react';
import api from '../api/patient'; // Assuming this is your configured axios instance
import { TrashIcon, MusicalNoteIcon } from '@heroicons/react/24/outline';
import { useNotifications } from '../context/NotificationContext';

const API_BASE_URL = 'http://localhost:8000'; // Define this if not globally available

export default function RecordingList({
  recordings,
  patientId,
  assessmentId,
  onDeleted,
  // onExtractFeatures // Placeholder for future use
}) {
  const { addToast } = useNotifications();

  if (!recordings || recordings.length === 0) {
    return <p className="text-center text-gray-500 py-3">No recordings for this assessment yet.</p>;
  }

  const handleDelete = async (recordingId) => {
    if (!window.confirm('Are you sure you want to delete this recording?')) return;
    try {
      await api.delete(
        `/patients/${patientId}/assessments/${assessmentId}/recordings/${recordingId}`
      );
      addToast('Recording deleted successfully!', 'success');
      onDeleted?.(recordingId); // Notify parent to update list
    } catch (err) {
      addToast(`Failed to delete recording: ${err.message || 'Unknown error'}`, 'error');
    }
  };

  return (
    <ul className="space-y-3">
      {recordings.map(r => (
        <li key={r.recording_id} className="p-3 border border-gray-200 rounded-md shadow-sm bg-white hover:shadow-md transition-shadow">
          <div className="flex flex-col sm:flex-row items-start sm:items-center sm:space-x-4 space-y-2 sm:space-y-0">
            <div className="flex-shrink-0">
              <MusicalNoteIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="flex-grow min-w-0"> {/* Added min-w-0 for proper truncation */}
              <p className="text-sm font-medium text-gray-700 truncate" title={r.filename}>
                File: {r.filename}
              </p>
              <p className="text-xs text-gray-500">
                Task: {r.task_type || 'N/A'} | Device: {r.recording_device || 'N/A'}
              </p>
              <p className="text-xs text-gray-500">
                Recorded: {new Date(r.recording_date).toLocaleString()}
              </p>
              <audio
                controls
                src={`${API_BASE_URL}${r.file_path}`} // Ensure full URL for audio source
                className="w-full mt-1 h-10" // Basic styling for audio player
              />
            </div>
            <div className="flex-shrink-0 flex space-x-2 sm:ml-auto">
              {/* <button
                onClick={() => onExtractFeatures?.(r)}
                className="p-1 text-green-600 hover:text-green-800 transition-colors"
                title="Extract Features (Not Implemented)"
              >
                <BeakerIcon className="h-5 w-5" />
              </button> */}
              <button
                onClick={() => handleDelete(r.recording_id)}
                className="p-1 text-red-500 hover:text-red-700 transition-colors"
                title="Delete Recording"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}