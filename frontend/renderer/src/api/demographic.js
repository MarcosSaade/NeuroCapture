import api from './patient';

export async function fetchDemographics(patientId) {
  const resp = await api.get(`/patients/${patientId}/demographics/`);
  return resp.data;
}
export async function createDemographic(patientId, data) {
  const resp = await api.post(`/patients/${patientId}/demographics/`, data);
  return resp.data;
}
export async function updateDemographic(patientId, id, data) {
  const resp = await api.put(`/patients/${patientId}/demographics/${id}`, data);
  return resp.data;
}
