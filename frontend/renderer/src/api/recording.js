// frontend/renderer/src/api/recording.js
import axios from 'axios';

// The backend endpoint expects FormData with fields: 'file', 'task_type', 'recording_device'
export async function uploadRecording(patientId, assessmentId, formDataToUpload) {
  const resp = await axios.post(
    `/api/v1/patients/${patientId}/assessments/${assessmentId}/recordings/`,
    formDataToUpload, // Send the pre-constructed FormData directly
    {
      headers: {
      }
    }
  );
  return resp.data;
}