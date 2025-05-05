// src/components/DemographicForm.jsx

import React, { useState, useEffect } from 'react';
import {
  fetchDemographics,
  createDemographic,
  updateDemographic
} from '../api/demographic';
import { useNotifications } from '../context/NotificationContext';

export default function DemographicForm({ patientId, onSaved }) {
  const { addToast } = useNotifications();
  const [demo, setDemo] = useState(null);
  const [form, setForm] = useState({
    age: '',
    gender: 'Male',
    education_years: '',
    collection_date: new Date().toISOString().slice(0, 10),
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const arr = await fetchDemographics(patientId);
        if (arr.length) {
          const d = arr[0];
          setDemo(d);
          setForm({
            age: d.age,
            gender: d.gender,
            education_years: d.education_years ?? '',
            collection_date: d.collection_date.slice(0, 10),
          });
        }
      } catch {
        addToast('Failed to load demographics', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [patientId, addToast]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (demo) {
        // Update existing
        await updateDemographic(patientId, demo.demographic_id, form);
        addToast('Demographics updated', 'success');
      } else {
        // Create new
        await createDemographic(patientId, form);
        addToast('Demographics saved', 'success');
      }
      onSaved?.();
    } catch {
      addToast('Failed to save demographics', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading demographics…</div>;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block mb-1">Age:</label>
        <input
          name="age"
          type="number"
          min="0"
          max="120"
          value={form.age}
          onChange={handleChange}
          required
          className="border px-2 py-1 w-full"
        />
      </div>

      <div>
        <label className="block mb-1">Gender:</label>
        <select
          name="gender"
          value={form.gender}
          onChange={handleChange}
          required
          className="border px-2 py-1 w-full"
        >
          <option>Male</option>
          <option>Female</option>
          <option>Other</option>
          <option>Prefer not to say</option>
        </select>
      </div>

      <div>
        <label className="block mb-1">Education Years:</label>
        <input
          name="education_years"
          type="number"
          min="0"
          max="30"
          value={form.education_years}
          onChange={handleChange}
          className="border px-2 py-1 w-full"
        />
      </div>

      <div>
        <label className="block mb-1">Collection Date:</label>
        <input
          name="collection_date"
          type="date"
          value={form.collection_date}
          onChange={handleChange}
          required
          className="border px-2 py-1 w-full"
        />
      </div>

      {/* ENASEM fields to be added here later */}

      <div className="flex space-x-2">
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? (demo ? 'Updating…' : 'Saving…') : demo ? 'Update' : 'Save'}
        </button>
      </div>
    </form>
  );
}
