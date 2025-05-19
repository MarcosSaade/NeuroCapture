// frontend/renderer/src/components/DemographicForm.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { fetchDemographics, createDemographic, updateDemographic } from '../api/demographic';
import { useNotifications } from '../context/NotificationContext';

const getDefaultFormState = () => ({
  age: '',
  gender: 'Male', // Default value
  education_years: '',
  collection_date: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
});

export default function DemographicForm({ patientId, onSaved }) {
  const { addToast } = useNotifications();
  const [demographicData, setDemographicData] = useState(null); // Stores the fetched demographic record
  const [form, setForm] = useState(getDefaultFormState());
  const [loading, setLoading] = useState(true);

  const loadDemographics = useCallback(async () => {
    setLoading(true);
    try {
      const dataArray = await fetchDemographics(patientId);
      if (dataArray && dataArray.length > 0) {
        const d = dataArray[0]; // Assuming one demographic record per patient for now
        setDemographicData(d);
        setForm({
          age: d.age.toString(),
          gender: d.gender,
          education_years: d.education_years?.toString() ?? '',
          collection_date: d.collection_date ? new Date(d.collection_date).toISOString().slice(0, 10) : new Date().toISOString().slice(0, 10),
        });
      } else {
        setDemographicData(null);
        setForm(getDefaultFormState());
      }
    } catch (err) {
      addToast(`Failed to load demographics: ${err.message}`, 'error');
      setDemographicData(null); // Reset on error
      setForm(getDefaultFormState());
    } finally {
      setLoading(false);
    }
  }, [patientId, addToast]);

  useEffect(() => {
    loadDemographics();
  }, [loadDemographics]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const payload = {
        ...form,
        age: parseInt(form.age),
        education_years: form.education_years ? parseInt(form.education_years) : null,
    };

    try {
      if (demographicData && demographicData.demographic_id) {
        await updateDemographic(patientId, demographicData.demographic_id, payload);
        addToast('Demographics updated successfully', 'success');
      } else {
        await createDemographic(patientId, payload);
        addToast('Demographics saved successfully', 'success');
      }
      loadDemographics(); // Re-fetch to update state
      onSaved?.(); // Notify parent
    } catch (err) {
      addToast(`Failed to save demographics: ${err.message || 'Unknown error'}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !demographicData && !form.age) return <div className="text-center py-4">Loading demographics…</div>;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="age" className="block text-sm font-medium text-gray-700">Age</label>
          <input
            id="age"
            name="age"
            type="number"
            min="0"
            max="120"
            value={form.age}
            onChange={handleChange}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        <div>
          <label htmlFor="gender" className="block text-sm font-medium text-gray-700">Gender</label>
          <select
            id="gender"
            name="gender"
            value={form.gender}
            onChange={handleChange}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
            <option value="Prefer not to say">Prefer not to say</option>
          </select>
        </div>
        <div>
          <label htmlFor="education_years" className="block text-sm font-medium text-gray-700">Education Years (Optional)</label>
          <input
            id="education_years"
            name="education_years"
            type="number"
            min="0"
            max="30"
            value={form.education_years}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        <div>
          <label htmlFor="collection_date" className="block text-sm font-medium text-gray-700">Collection Date</label>
          <input
            id="collection_date"
            name="collection_date"
            type="date"
            value={form.collection_date}
            onChange={handleChange}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>

      {/* ENASEM fields can be added here later, following similar pattern */}
      {/* <p className="text-sm text-gray-500">ENASEM specific fields will be added here.</p> */}

      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Saving...' : (demographicData ? 'Update Demographics' : 'Save Demographics')}
        </button>
      </div>
    </form>
  );
}