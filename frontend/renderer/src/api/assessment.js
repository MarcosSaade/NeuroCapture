import api from './patient';

export async function fetchAssessments(patientId) {
  const resp = await api.get(`/patients/${patientId}/assessments/`);
  return resp.data;
}

export async function createAssessment(patientId, data) {
  const resp = await api.post(`/patients/${patientId}/assessments/`, data);
  return resp.data;
}

export async function updateAssessment(patientId, id, data) {
  const resp = await api.put(
    `/patients/${patientId}/assessments/${id}`,
    data
  );
  return resp.data;
}

export async function deleteAssessment(patientId, id) {
  await api.delete(`/patients/${patientId}/assessments/${id}`);
}
