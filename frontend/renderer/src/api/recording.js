// src/api/recording.js
import axios from 'axios';

export async function uploadRecording(patientId, assessmentId, file, metadata) {
  const form = new FormData();
  form.append('file', file);
  form.append('task_type', metadata.testName);           // matches Form(...) name
  form.append('recording_device', metadata.deviceType);  // matches Form(...) name

  const resp = await axios.post(
    `/api/v1/patients/${patientId}/assessments/${assessmentId}/recordings/`,
    form,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  return resp.data;
}
