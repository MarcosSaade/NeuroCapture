// frontend/renderer/src/api/audioProcessing.js
import api from './patient';

export async function startAudioProcessing(patientId, assessmentId, recordingId) {
  const response = await api.post(
    `/patients/${patientId}/assessments/${assessmentId}/recordings/${recordingId}/process`
  );
  return response.data;
}

export async function getProcessingStatus(patientId, assessmentId, recordingId, taskId) {
  const response = await api.get(
    `/patients/${patientId}/assessments/${assessmentId}/recordings/${recordingId}/process/${taskId}`
  );
  return response.data;
}

export async function getRecordingFeatures(patientId, assessmentId, recordingId) {
  const response = await api.get(
    `/patients/${patientId}/assessments/${assessmentId}/recordings/${recordingId}/features/`
  );
  return response.data;
}
