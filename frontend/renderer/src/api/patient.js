// src/api/patient.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export async function fetchPatients(skip = 0, limit = 20) {
  const resp = await api.get('/patients/', { params: { skip, limit } });
  return resp.data;
}

export async function createPatient(data) {
  const resp = await api.post('/patients/', data);
  return resp.data;
}

export async function getPatient(id) {
  const resp = await api.get(`/patients/${id}`);
  return resp.data;
}

export async function updatePatient(id, data) {
  const resp = await api.put(`/patients/${id}`, data);
  return resp.data;
}

export async function deletePatient(id) {
  await api.delete(`/patients/${id}`);
}

export async function fetchPatient(patientId) {
  const { data } = await axios.get(`/api/v1/patients/${patientId}`)
  return data
}

export async function fetchDemographics(patientId) {
  const { data } = await axios.get(
    `/api/v1/patients/${patientId}/demographics/`
  )
  return data
}

export async function fetchAssessments(patientId) {
  const { data } = await axios.get(
    `/api/v1/patients/${patientId}/assessments/`
  )
  return data
}

export default api;