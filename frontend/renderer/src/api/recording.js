// frontend/renderer/src/api/recording.js
import api from './patient';

// The backend endpoint expects FormData with fields: 'file', 'task_type', 'recording_device'
export async function uploadRecording(patientId, assessmentId, formDataToUpload) {
  const resp = await api.post(
    `/patients/${patientId}/assessments/${assessmentId}/recordings/`,
    formDataToUpload, // Send the pre-constructed FormData directly
    {
      headers: {
      }
    }
  );
  return resp.data;
}