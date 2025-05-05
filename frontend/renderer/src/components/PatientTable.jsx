// src/components/PatientTable.jsx

import React, { useState, useEffect, useMemo } from 'react';
import { fetchPatients, deletePatient } from '../api/patient';
import { useNotifications } from '../context/NotificationContext';

const statusColors = {
  complete: 'bg-green-100 text-green-800',
  incomplete: 'bg-yellow-100 text-yellow-800',
  pending: 'bg-gray-100 text-gray-800',
  error: 'bg-red-100 text-red-800'
};

export default function PatientTable({ onEdit, refresh }) {
  const [patients, setPatients] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState('patient_id');
  const [sortAsc, setSortAsc] = useState(true);
  const { addToast } = useNotifications();

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchPatients(skip, limit);
      setPatients(data);
    } catch {
      setError('Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [skip, refresh]);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this patient?')) return;
    try {
      await deletePatient(id);
      addToast('Patient deleted', 'success');
      load();
    } catch {
      addToast('Failed to delete patient', 'error');
    }
  };

  const displayed = useMemo(() => {
    let arr = patients.filter((p) =>
      p.study_identifier.toLowerCase().includes(search.toLowerCase())
    );
    arr.sort((a, b) => {
      const va = a[sortField], vb = b[sortField];
      if (va < vb) return sortAsc ? -1 : 1;
      if (va > vb) return sortAsc ? 1 : -1;
      return 0;
    });
    return arr;
  }, [patients, search, sortField, sortAsc]);

  const exportCSV = () => {
    const headers = ['ID','Study ID','Status','Created At','Updated At'];
    const rows = displayed.map(p => [
      p.patient_id,
      p.study_identifier,
      p.status ?? 'pending',
      p.created_at,
      p.updated_at
    ]);
    const csv = [headers, ...rows]
      .map(r => r.map(String).map(s => `"${s.replace(/"/g,'""')}"`).join(','))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'patients.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const onSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(true); }
  };

  if (loading) return <div>Loading patients…</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <>
      <div className="flex items-center justify-between mb-2">
        <input
          type="text"
          placeholder="Search Study ID…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border px-2 py-1 rounded w-1/3"
        />
        <button
          onClick={exportCSV}
          className="bg-green-600 text-white px-3 py-1 rounded"
        >
          Export CSV
        </button>
      </div>
      <table className="table-auto w-full mb-4 border-collapse">
        <thead>
          <tr>
            {[
              ['patient_id','ID'],
              ['study_identifier','Study ID'],
              ['status','Status'],
              ['created_at','Created At'],
              ['updated_at','Updated At'],
            ].map(([field,label]) => (
              <th
                key={field}
                onClick={() => onSort(field)}
                className="cursor-pointer px-2 py-1 border-b"
              >
                {label}
                {sortField===field ? (sortAsc?' ▲':' ▼') : ''}
              </th>
            ))}
            <th className="px-2 py-1 border-b">Actions</th>
          </tr>
        </thead>
        <tbody>
          {displayed.map((p) => {
            const status = p.status ?? 'pending';
            return (
              <tr key={p.patient_id} className="hover:bg-gray-50">
                <td className="px-2 py-1">{p.patient_id}</td>
                <td className="px-2 py-1">{p.study_identifier}</td>
                <td className="px-2 py-1">
                  <span
                    className={`px-2 py-1 rounded-full text-sm font-medium ${
                      statusColors[status] ?? statusColors.pending
                    }`}
                  >
                    {status}
                  </span>
                </td>
                <td className="px-2 py-1">
                  {new Date(p.created_at).toLocaleString()}
                </td>
                <td className="px-2 py-1">
                  {new Date(p.updated_at).toLocaleString()}
                </td>
                <td className="px-2 py-1 space-x-2">
                  <button
                    onClick={() => onEdit(p.patient_id)}
                    className="text-blue-600"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(p.patient_id)}
                    className="text-red-600"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
          {displayed.length === 0 && (
            <tr>
              <td colSpan={6} className="text-center py-4 text-gray-500">
                No patients found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
      <div className="flex justify-between">
        <button
          onClick={() => setSkip((s) => Math.max(0, s - limit))}
          disabled={skip === 0}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Prev
        </button>
        <button
          onClick={() => setSkip((s) => s + limit)}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Next
        </button>
      </div>
    </>
  );
}
