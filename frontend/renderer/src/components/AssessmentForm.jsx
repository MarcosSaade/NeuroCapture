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

// Preset subscores for MMSE and MoCA:
const SUBSCORES_PRESETS = {
  MMSE: [
    ['Orientation – Time', 5],
    ['Orientation – Place', 5],
    ['Registration', 3],
    ['Attention & Calculation', 5],
    ['Recall', 3],
    ['Language – Naming', 2],
    ['Language – Repetition', 1],
    ['Language – Comprehension', 3],
    ['Reading', 1],
    ['Writing', 1],
    ['Visuoconstruction', 1],
  ],
  MoCA: [
    ['Visuospatial/Executive', 5],
    ['Naming', 3],
    ['Attention', 6],
    ['Language', 3],
    ['Abstraction', 2],
    ['Delayed Recall', 5],
    ['Orientation', 6],
  ],
};

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
    subscores: [],      // will hold { name, score, max_score }
  });
  const [editId, setEditId] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load existing assessments
  const load = async () => {
    try {
      const arr = await fetchAssessments(patientId);
      setExisting(arr);
    } catch {
      addToast('Failed to load assessments', 'error');
    }
  };

  // Initialize on mount / patientId / initialData
  useEffect(() => {
    setLoading(true);
    load()
      .catch(() => {})
      .finally(() => setLoading(false));

    if (initialData) {
      // Editing existing assessment
      setEditId(initialData.assessment_id);
      setForm({
        assessment_type: initialData.assessment_type,
        score: initialData.score,
        max_possible_score: initialData.max_possible_score,
        assessment_date: initialData.assessment_date.slice(0, 16),
        diagnosis: initialData.diagnosis || '',
        notes: initialData.notes || '',
        subscores: initialData.subscores?.map(s => ({
          name: s.name,
          score: s.score,
          max_score: s.max_score,
        })) || [],
      });
    } else {
      // New assessment: reset fields
      setEditId(null);
      setForm(f => ({
        ...f,
        score: '',
        diagnosis: '',
        notes: '',
      }));
    }
  }, [patientId, initialData]);

  // Update max & preset subscores when type changes
  useEffect(() => {
    const typeObj = TEST_TYPES.find(t => t.label === form.assessment_type);
    const presets = SUBSCORES_PRESETS[form.assessment_type] || [];
    setForm(f => ({
      ...f,
      max_possible_score: typeObj?.max ?? null,
      subscores: presets.map(([name, max]) => ({
        name,
        score: f.subscores.find(s => s.name === name)?.score ?? '',
        max_score: max,
      })),
    }));
  }, [form.assessment_type]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubscoreChange = (idx, value) => {
    setForm(f => {
      const subs = [...f.subscores];
      subs[idx] = { ...subs[idx], score: value };
      return { ...f, subscores: subs };
    });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = { ...form };
      if (editId) {
        await updateAssessment(patientId, editId, payload);
        addToast('Assessment updated', 'success');
      } else {
        await createAssessment(patientId, payload);
        addToast('Assessment created', 'success');
      }
      onSaved?.();
    } catch {
      addToast('Save failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading assessments…</div>;

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 border p-6 rounded bg-white"
    >
      {/* Basic Fields */}
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
            {TEST_TYPES.map(t => (
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

      {/* Subscores Grid (MMSE/MoCA only) */}
      {(form.assessment_type === 'MMSE' || form.assessment_type === 'MoCA') && (
        <div>
          <h4 className="font-semibold mb-2">Subscores</h4>
          <div className="grid grid-cols-2 gap-4">
            {form.subscores.map((s, idx) => (
              <div key={s.name} className="flex items-center space-x-2">
                <label className="w-48">{s.name}:</label>
                <input
                  type="number"
                  min="0"
                  max={s.max_score}
                  value={s.score}
                  onChange={e => handleSubscoreChange(idx, e.target.value)}
                  required
                  className="border px-2 py-1 w-20"
                />
                <span>/ {s.max_score}</span>
              </div>
            ))}
          </div>
        </div>
      )}

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
