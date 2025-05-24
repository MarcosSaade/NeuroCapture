// frontend/renderer/src/components/RecordingList.jsx
import React, { useState, useEffect } from 'react';
import api from '../api/patient'; // Assuming this is your configured axios instance
import { TrashIcon, MusicalNoteIcon, BeakerIcon, EyeIcon } from '@heroicons/react/24/outline';
import { useNotifications } from '../context/NotificationContext';
import { startAudioProcessing, getProcessingStatus, getRecordingFeatures } from '../api/audioProcessing';
import ProgressBar from './ProgressBar';

const API_BASE_URL = 'http://localhost:8000'; // Define this if not globally available

export default function RecordingList({
  recordings,
  patientId,
  assessmentId,
  onDeleted,
  // onExtractFeatures // Placeholder for future use
}) {
  const { addToast } = useNotifications();
  const [processingTasks, setProcessingTasks] = useState({}); // Track processing status per recording
  const [features, setFeatures] = useState({}); // Track extracted features per recording

  // Load features for all recordings on mount
  useEffect(() => {
    if (recordings && recordings.length > 0) {
      recordings.forEach(recording => {
        loadFeatures(recording.recording_id);
      });
    }
  }, [recordings]);

  // Cleanup intervals when component unmounts
  useEffect(() => {
    return () => {
      Object.values(processingTasks).forEach(task => {
        if (task.intervalId) {
          clearInterval(task.intervalId);
        }
      });
    };
  }, [processingTasks]);

  if (!recordings || recordings.length === 0) {
    return <p className="text-center text-gray-500 py-3">No recordings for this assessment yet.</p>;
  }

  const startFeatureExtraction = async (recordingId) => {
    try {
      const response = await startAudioProcessing(patientId, assessmentId, recordingId);
      const taskId = response.task_id;
      
      addToast('Audio processing started. This may take a few minutes...', 'info');
      
      // Start tracking this task
      const intervalId = setInterval(async () => {
        try {
          const status = await getProcessingStatus(patientId, assessmentId, recordingId, taskId);
          
          setProcessingTasks(prev => ({
            ...prev,
            [recordingId]: {
              ...status,
              intervalId
            }
          }));
          
          if (status.status === 'completed') {
            clearInterval(intervalId);
            addToast(`Audio processing completed! Extracted ${status.result?.features_extracted || 0} features.`, 'success');
            
            // Load features for this recording
            loadFeatures(recordingId);
            
            // Clean up processing task
            setProcessingTasks(prev => {
              const newTasks = { ...prev };
              delete newTasks[recordingId];
              return newTasks;
            });
          } else if (status.status === 'failed') {
            clearInterval(intervalId);
            addToast(`Audio processing failed: ${status.error}`, 'error');
            
            // Clean up processing task
            setProcessingTasks(prev => {
              const newTasks = { ...prev };
              delete newTasks[recordingId];
              return newTasks;
            });
          }
        } catch (err) {
          console.error('Error checking processing status:', err);
        }
      }, 2000); // Check every 2 seconds
      
      setProcessingTasks(prev => ({
        ...prev,
        [recordingId]: {
          status: 'pending',
          progress: 0,
          intervalId
        }
      }));
      
    } catch (err) {
      addToast(`Failed to start audio processing: ${err.message || 'Unknown error'}`, 'error');
    }
  };

  const loadFeatures = async (recordingId) => {
    try {
      const featuresData = await getRecordingFeatures(patientId, assessmentId, recordingId);
      setFeatures(prev => ({
        ...prev,
        [recordingId]: featuresData
      }));
    } catch (err) {
      console.error('Error loading features:', err);
    }
  };

  const viewFeatures = (recordingId) => {
    const recordingFeatures = features[recordingId];
    if (!recordingFeatures || recordingFeatures.length === 0) {
      addToast('No features available for this recording', 'warning');
      return;
    }

    // Create a simple modal/alert showing feature count
    const featureCount = recordingFeatures.length;
    const featureNames = recordingFeatures.slice(0, 5).map(f => f.feature_name).join(', ');
    const message = `${featureCount} features extracted:\n${featureNames}${featureCount > 5 ? '...' : ''}`;
    
    alert(message); // Simple implementation - could be enhanced with a proper modal
  };

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
      {recordings.map(r => {
        const processingTask = processingTasks[r.recording_id];
        const recordingFeatures = features[r.recording_id];
        const isProcessing = processingTask && ['pending', 'running'].includes(processingTask.status);
        
        return (
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
                
                {/* Processing Progress */}
                {isProcessing && (
                  <div className="mt-2">
                    <p className="text-xs text-blue-600 mb-1">
                      Processing audio... ({processingTask.status})
                    </p>
                    <ProgressBar 
                      progress={processingTask.progress || 0} 
                      animated={processingTask.status === 'running'}
                    />
                  </div>
                )}
                
                {/* Feature Status */}
                {recordingFeatures && recordingFeatures.length > 0 && (
                  <p className="text-xs text-green-600 mt-1">
                    ✓ {recordingFeatures.length} features extracted
                  </p>
                )}
              </div>
              <div className="flex-shrink-0 flex space-x-2 sm:ml-auto">
                {/* Feature Extraction Button */}
                <button
                  onClick={() => startFeatureExtraction(r.recording_id)}
                  disabled={isProcessing}
                  className={`p-1 transition-colors ${
                    isProcessing 
                      ? 'text-gray-400 cursor-not-allowed' 
                      : 'text-green-600 hover:text-green-800'
                  }`}
                  title={isProcessing ? 'Processing...' : 'Extract Audio Features'}
                >
                  <BeakerIcon className="h-5 w-5" />
                </button>
                
                {/* View Features Button */}
                {recordingFeatures && recordingFeatures.length > 0 && (
                  <button
                    onClick={() => viewFeatures(r.recording_id)}
                    className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
                    title="View Extracted Features"
                  >
                    <EyeIcon className="h-5 w-5" />
                  </button>
                )}
                
                {/* Delete Button */}
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
        );
      })}
    </ul>
  );
}