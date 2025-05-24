// frontend/renderer/src/components/PatientDetail.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { getPatient, updatePatient as apiUpdatePatient, deletePatient as apiDeletePatient } from '../api/patient';
import {
  fetchAssessments,
  createAssessment,
  updateAssessment,
  deleteAssessment,
} from '../api/assessment';
import { uploadRecording } from '../api/recording';
import api from '../api/patient'; // For direct recording deletion
import { useNotifications } from '../context/NotificationContext';
import DemographicForm from './DemographicForm';
import AssessmentForm from './AssessmentForm';
import AssessmentList from './AssessmentList';
import RecordingList from './RecordingList';
import RecordingUpload from './RecordingUpload'; // We'll use this for specific assessments

const TABS = [
  { id: 'info', label: 'Info & Demographics' },
  { id: 'cognitive', label: 'Cognitive Assessments' },
  { id: 'audio', label: 'Audio Data' },
];

const API_BASE_URL = 'http://localhost:8000';


export default function PatientDetail({ patientId, onSuccess, onDeleted }) {
  const { addToast } = useNotifications();

  const [activeTab, setActiveTab] = useState(TABS[0].id);
  const [patient, setPatient] = useState(null);
  const [studyId, setStudyId] = useState('');
  const [loadingPatient, setLoadingPatient] = useState(true);

  const [assessments, setAssessments] = useState([]);
  const [loadingAssessments, setLoadingAssessments] = useState(true);
  const [editingAssessment, setEditingAssessment] = useState(null); // For AssessmentForm

  // For "Upload New Audio Test" (creates new assessment)
  const [audioTestTaskType, setAudioTestTaskType] = useState('');
  const [audioTestDevice, setAudioTestDevice] = useState('');
  const [audioTestFile, setAudioTestFile] = useState(null);
  const [uploadingAudioTest, setUploadingAudioTest] = useState(false);

  // For managing recordings of a selected existing assessment
  const [selectedAssessmentForAudio, setSelectedAssessmentForAudio] = useState(null);
  const [selectedAssessmentRecordings, setSelectedAssessmentRecordings] = useState([]);
  const [loadingSelectedRecordings, setLoadingSelectedRecordings] = useState(false);


  const loadPatientData = useCallback(async () => {
    setLoadingPatient(true);
    try {
      const data = await getPatient(patientId);
      setPatient(data);
      setStudyId(data.study_identifier);
    } catch (err) {
      addToast(`Failed to load patient: ${err.message}`, 'error');
    } finally {
      setLoadingPatient(false);
    }
  }, [patientId, addToast]);

  const loadAssessmentsData = useCallback(async () => {
    setLoadingAssessments(true);
    try {
      const data = await fetchAssessments(patientId);
      setAssessments(data);
    } catch (err) {
      addToast(`Failed to load assessments: ${err.message}`, 'error');
    } finally {
      setLoadingAssessments(false);
    }
  }, [patientId, addToast]);

  // Auto-select first assessment that has audio recordings when assessments load
  useEffect(() => {
    const selectFirstAssessmentWithAudio = async () => {
      if (assessments.length > 0 && !selectedAssessmentForAudio && !loadingAssessments) {
        // Check each assessment for audio recordings, starting from the first
        for (const assessment of assessments) {
          try {
            const recordingsData = await api.get(
              `/patients/${patientId}/assessments/${assessment.assessment_id}/recordings/`
            );
            if (recordingsData.data && recordingsData.data.length > 0) {
              // Found an assessment with audio recordings, select it
              setSelectedAssessmentForAudio(assessment);
              setSelectedAssessmentRecordings(recordingsData.data);
              break;
            }
          } catch (err) {
            console.error('Error checking recordings for assessment:', err);
          }
        }
      }
    };

    selectFirstAssessmentWithAudio();
  }, [assessments, selectedAssessmentForAudio, loadingAssessments, patientId]);

  useEffect(() => {
    loadPatientData();
    loadAssessmentsData();
  }, [loadPatientData, loadAssessmentsData]);
  
  const handleSavePatientStudyId = async () => {
    setLoadingPatient(true);
    try {
      await apiUpdatePatient(patientId, { study_identifier: studyId });
      addToast('Study ID updated', 'success');
      loadPatientData(); // Re-fetch to confirm
      onSuccess?.(); // Might close modal or refresh list
    } catch (err) {
      addToast(`Failed to update Study ID: ${err.message}`, 'error');
    } finally {
      setLoadingPatient(false);
    }
  };

  const handleDeletePatient = async () => {
    if (!window.confirm('Are you sure you want to delete this patient and all associated data? This cannot be undone.')) return;
    try {
      await apiDeletePatient(patientId);
      addToast('Patient deleted successfully', 'success');
      onDeleted?.(patientId); // Notify parent to remove from list/close modal
    } catch (err) {
      addToast(`Failed to delete patient: ${err.message}`, 'error');
    }
  };

  const handleAssessmentSaved = async (payload, assessmentId) => {
    try {
      if (assessmentId) {
        // This is an update
        await updateAssessment(patientId, assessmentId, payload);
        addToast('Assessment updated successfully', 'success');
      } else {
        // This is a new assessment
        await createAssessment(patientId, payload);
        addToast('Assessment created successfully', 'success');
      }
      setEditingAssessment(null); // Clear edit form
      loadAssessmentsData();    // Reload list
    } catch (err) {
      addToast(`Failed to save assessment: ${err.message}`, 'error');
      // Optionally, you might not want to clear the form or reload data if save failed
    }
  };

  const handleEditAssessment = (assessment) => {
    setEditingAssessment(assessment);
    // Smooth scroll to the form if it's far or not visible
    const formElement = document.getElementById('assessment-form-section');
    if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };
  
  const handleDeleteAssessment = async (assessmentIdToDel) => {
    if (!window.confirm('Delete this assessment?')) return;
    try {
      await deleteAssessment(patientId, assessmentIdToDel);
      addToast('Assessment deleted', 'success');
      loadAssessmentsData();
      if (editingAssessment?.assessment_id === assessmentIdToDel) {
        setEditingAssessment(null);
      }
      if(selectedAssessmentForAudio?.assessment_id === assessmentIdToDel){
        setSelectedAssessmentForAudio(null);
        setSelectedAssessmentRecordings([]);
      }
    } catch (err) {
      addToast(`Assessment delete failed: ${err.message}`, 'error');
    }
  };

  const handleUploadNewAudioTest = async (e) => {
    e.preventDefault();
    if (!audioTestTaskType || !audioTestFile) {
      addToast('Task Type and Audio File are required.', 'error');
      return;
    }
    setUploadingAudioTest(true);
    try {
      const newAssessmentPayload = {
        assessment_type: audioTestTaskType,
        score: 0, // Default score for an audio test
        max_possible_score: null,
        assessment_date: new Date().toISOString(),
        notes: `Audio test: ${audioTestTaskType}`,
        subscores: [],
      };
      const newAsm = await createAssessment(patientId, newAssessmentPayload);
      
      const formData = new FormData();
      formData.append('file', audioTestFile);
      formData.append('task_type', audioTestTaskType);
      formData.append('recording_device', audioTestDevice || 'Unknown');
      
      await uploadRecording(patientId, newAsm.assessment_id, formData);
      
      addToast('New audio test uploaded successfully', 'success');
      setAudioTestTaskType('');
      setAudioTestDevice('');
      setAudioTestFile(null);
      loadAssessmentsData(); // Refresh assessment list to show the new one
    } catch (err) {
      addToast(`Failed to upload new audio test: ${err.message}`, 'error');
    } finally {
      setUploadingAudioTest(false);
    }
  };

  const handleSelectAssessmentForAudio = async (assessment) => {
    setSelectedAssessmentForAudio(assessment);
    if (assessment) {
      setLoadingSelectedRecordings(true);
      try {
        const recordingsData = await api.get(
          `/patients/${patientId}/assessments/${assessment.assessment_id}/recordings/`
        );
        setSelectedAssessmentRecordings(recordingsData.data);
      } catch (err) {
        addToast(`Failed to load recordings for assessment: ${err.message}`, 'error');
        setSelectedAssessmentRecordings([]);
      } finally {
        setLoadingSelectedRecordings(false);
      }
    } else {
      setSelectedAssessmentRecordings([]);
    }
  };
  
  const handleRecordingUploadedToSelected = (newRecording) => {
    setSelectedAssessmentRecordings(prev => [...prev, newRecording]);
    addToast('Recording uploaded to assessment.', 'success');
  };

  const handleRecordingDeletedFromSelected = (deletedRecordingId) => {
    setSelectedAssessmentRecordings(prev => prev.filter(r => r.recording_id !== deletedRecordingId));
    addToast('Recording deleted.', 'success');
  };


  if (loadingPatient) return <div className="p-4 text-center">Loading patient data...</div>;
  if (!patient) return <div className="p-4 text-center text-red-500">Patient not found.</div>;

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-4" aria-label="Tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm transition-colors duration-150`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="pt-2">
        {/* Tab 1: Info & Demographics */}
        {activeTab === 'info' && (
          <div className="space-y-6">
            <div className="p-4 border rounded-md bg-slate-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Patient Identifier</h3>
              <div className="flex items-center space-x-3">
                <input
                  type="text"
                  value={studyId}
                  onChange={(e) => setStudyId(e.target.value)}
                  disabled={loadingPatient}
                  className="flex-grow border border-gray-300 px-3 py-2 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="e.g., P001_SITE_A"
                />
                <button
                  onClick={handleSavePatientStudyId}
                  disabled={loadingPatient || studyId === patient.study_identifier}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors duration-150"
                >
                  {loadingPatient ? 'Saving...' : 'Save ID'}
                </button>
              </div>
            </div>

            <div className="p-4 border rounded-md bg-slate-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Demographics</h3>
              <DemographicForm patientId={patientId} onSaved={loadPatientData} />
            </div>
             <div className="mt-8 pt-6 border-t border-gray-300">
                <h3 className="text-lg font-semibold text-red-600 mb-2">Danger Zone</h3>
                <button
                    onClick={handleDeletePatient}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors duration-150"
                >
                    Delete This Patient
                </button>
                <p className="text-sm text-gray-500 mt-2">This action is permanent and will remove all data associated with this patient.</p>
            </div>
          </div>
        )}

        {/* Tab 2: Cognitive Assessments */}
        {activeTab === 'cognitive' && (
          <div className="space-y-6">
            <div id="assessment-form-section" className="p-4 border rounded-md bg-slate-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                {editingAssessment ? 'Edit Cognitive Assessment' : 'Add New Cognitive Assessment'}
              </h3>
              <AssessmentForm
                patientId={patientId}
                initialData={editingAssessment}
                onSaved={handleAssessmentSaved}
                onCancel={() => setEditingAssessment(null)}
              />
            </div>
            <div className="p-4 border rounded-md bg-slate-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Existing Assessments</h3>
              {loadingAssessments ? (
                <p>Loading assessments...</p>
              ) : (
                <AssessmentList
                  assessments={assessments}
                  onEdit={handleEditAssessment}
                  onDelete={handleDeleteAssessment}
                />
              )}
            </div>
          </div>
        )}

        {/* Tab 3: Audio Data */}
        {activeTab === 'audio' && (
          <div className="space-y-8">
            <div className="p-4 border rounded-md bg-slate-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Upload New Audio Test</h3>
              <p className="text-sm text-gray-600 mb-3">This will create a new assessment entry specifically for this audio recording.</p>
              <form onSubmit={handleUploadNewAudioTest} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Task Type / Test Name</label>
                  <input
                    type="text"
                    value={audioTestTaskType}
                    onChange={e => setAudioTestTaskType(e.target.value)}
                    required
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Cookie Theft Description, Verbal Fluency - Animals"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Recording Device (Optional)</label>
                  <input
                    type="text"
                    value={audioTestDevice}
                    onChange={e => setAudioTestDevice(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    placeholder="e.g., Zoom H4n, Smartphone"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Audio File</label>
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={e => setAudioTestFile(e.target.files[0] || null)}
                    required
                    className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
                <button
                  type="submit"
                  disabled={uploadingAudioTest}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors duration-150"
                >
                  {uploadingAudioTest ? 'Uploading...' : 'Upload Audio Test'}
                </button>
              </form>
            </div>
            
            <div className="p-4 border rounded-md bg-slate-50">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Manage Recordings for Existing Assessments</h3>
                {loadingAssessments ? <p>Loading assessments...</p> : (
                    assessments.length > 0 ? (
                        <div className="space-y-2 mb-4">
                            <label htmlFor="assessment-select-for-audio" className="block text-sm font-medium text-gray-700">Select an assessment to manage its audio:</label>
                            <select
                                id="assessment-select-for-audio"
                                value={selectedAssessmentForAudio?.assessment_id || ''}
                                onChange={e => {
                                    const selectedId = parseInt(e.target.value);
                                    const foundAssessment = assessments.find(a => a.assessment_id === selectedId);
                                    handleSelectAssessmentForAudio(foundAssessment || null);
                                }}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                            >
                                <option value="">-- Select Assessment --</option>
                                {assessments.map(asm => (
                                    <option key={asm.assessment_id} value={asm.assessment_id}>
                                        {asm.assessment_type} ({new Date(asm.assessment_date).toLocaleDateString()}) - Score: {asm.score}
                                    </option>
                                ))}
                            </select>
                        </div>
                    ) : <p className="text-gray-600">No cognitive assessments found. Add one in the 'Cognitive Assessments' tab to manage its audio recordings.</p>
                )}

                {selectedAssessmentForAudio && (
                    <div className="mt-4 pt-4 border-t">
                        <h4 className="text-md font-semibold text-gray-700 mb-2">
                            Recordings for: {selectedAssessmentForAudio.assessment_type} ({new Date(selectedAssessmentForAudio.assessment_date).toLocaleDateString()})
                        </h4>
                        {loadingSelectedRecordings ? <p>Loading recordings...</p> : (
                            <>
                                <RecordingList
                                    recordings={selectedAssessmentRecordings}
                                    patientId={patientId}
                                    assessmentId={selectedAssessmentForAudio.assessment_id}
                                    onDeleted={handleRecordingDeletedFromSelected}
                                    // onExtractFeatures could be implemented later
                                />
                                <div className="mt-4">
                                  <h5 className="text-sm font-medium text-gray-700 mb-1">Upload new recording to this assessment:</h5>
                                  <RecordingUpload 
                                      patientId={patientId}
                                      assessmentId={selectedAssessmentForAudio.assessment_id}
                                      onUploaded={handleRecordingUploadedToSelected}
                                  />
                                </div>
                            </>
                        )}
                    </div>
                )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}