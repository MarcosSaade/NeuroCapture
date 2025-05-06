// src/components/AssessmentForm.jsx

import React, { useState, useEffect } from 'react';
import {
  fetchAssessments,
  createAssessment,
  updateAssessment,
} from '../api/assessment';
import { useNotifications } from '../context/NotificationContext';

const TEST_TYPES = [
  { label: 'MMSE', max: 30 },
  { label: 'MoCA', max: 30 },
  { label: 'Other', max: null },
];

export default function AssessmentForm({
  patientId,
  initialData = null,   // the assessment to prefill for editing
  onSaved,              // called after create/update
}) {
  const { addToast } = useNotifications();

  const [existing, setExisting] = useState([]);
  const [form, setForm] = useState({
    assessment_type: 'MMSE',
    score: '',
    max_possible_score: 30,
    assessment_date: new Date().toISOString().slice(0, 16),
    diagnosis: '',
    notes: '',
  });
  const [editId, setEditId] = useState(null);
  const [loading, setLoading] = useState(true);

  // load existing assessments (for potential refetch/use by parent)
  const load = async () => {
    try {
      const arr = await fetchAssessments(patientId);
      setExisting(arr);
    } catch {
      addToast('Failed to load assessments', 'error');
    }
  };

  // initialize on mount and when patientId or initialData changes
  useEffect(() => {
    setLoading(true);
    load()
      .catch(() => {})
      .finally(() => setLoading(false));

    if (initialData) {
      // editing: prefill
      setEditId(initialData.assessment_id);
      setForm({
        assessment_type: initialData.assessment_type,
        score: initialData.score,
        max_possible_score: initialData.max_possible_score,
        assessment_date: initialData.assessment_date.slice(0, 16),
        diagnosis: initialData.diagnosis || '',
        notes: initialData.notes || '',
      });
    } else {
      // creating new: reset form
      setEditId(null);
      setForm((f) => ({
        ...f,
        score: '',
        diagnosis: '',
        notes: '',
      }));
    }
  }, [patientId, initialData]);

  // update max_possible_score when type changes
  useEffect(() => {
    const typeObj = TEST_TYPES.find((t) => t.label === form.assessment_type);
    setForm((f) => ({
      ...f,
      max_possible_score: typeObj.max,
    }));
  }, [form.assessment_type]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editId) {
        await updateAssessment(patientId, editId, form);
        addToast('Assessment updated', 'success');
      } else {
        await createAssessment(patientId, form);
        addToast('Assessment created', 'success');
      }
      onSaved?.();
    } catch {
      addToast('Save failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading assessments…</div>;
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 border p-4 rounded bg-white"
    >
      <div className="grid grid-cols-2 gap-4">
        {/* Type */}
        <div>
          <label className="block mb-1 font-medium">Type</label>
          <select
            name="assessment_type"
            value={form.assessment_type}
            onChange={handleChange}
            className="border px-2 py-1 w-full"
          >
            {TEST_TYPES.map((t) => (
              <option key={t.label} value={t.label}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        {/* Score / Max */}
        <div>
          <label className="block mb-1 font-medium">Score / Max</label>
          <div className="flex items-center space-x-2">
            <input
              name="score"
              type="number"
              min="0"
              max={form.max_possible_score ?? undefined}
              value={form.score}
              onChange={handleChange}
              required
              className="border px-2 py-1 w-1/2"
            />
            <span>/ {form.max_possible_score ?? '–'}</span>
          </div>
        </div>

        {/* Date & Time */}
        <div className="col-span-2">
          <label className="block mb-1 font-medium">Date &amp; Time</label>
          <input
            name="assessment_date"
            type="datetime-local"
            value={form.assessment_date}
            onChange={handleChange}
            required
            className="border px-2 py-1 w-full"
          />
        </div>
      </div>

      {/* Diagnosis */}
      <div>
        <label className="block mb-1 font-medium">Diagnosis</label>
        <input
          name="diagnosis"
          type="text"
          value={form.diagnosis}
          onChange={handleChange}
          className="border px-2 py-1 w-full"
        />
      </div>

      {/* Notes */}
      <div>
        <label className="block mb-1 font-medium">Notes</label>
        <textarea
          name="notes"
          rows="3"
          value={form.notes}
          onChange={handleChange}
          className="border px-2 py-1 w-full"
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        {editId ? 'Update' : 'Add'} Assessment
      </button>
    </form>
  );
}
