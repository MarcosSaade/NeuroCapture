// frontend/renderer/src/components/AssessmentForm.jsx
import React, { useState, useEffect, useMemo } from 'react';
import { useNotifications } from '../context/NotificationContext';

// Filtered list for general cognitive assessments
const COGNITIVE_TEST_TYPES = [
  { label: 'MMSE', max: 30 },
  { label: 'MoCA', max: 30 },
  { label: 'Other', max: null }, // For custom scored tests
];

const SUBSCORES_PRESETS = {
  MMSE: [
    ['Orientation – Time', 5], ['Orientation – Place', 5], ['Registration', 3],
    ['Attention & Calculation', 5], ['Recall', 3], ['Language – Naming', 2],
    ['Language – Repetition', 1], ['Language – Comprehension', 3], ['Reading', 1],
    ['Writing', 1], ['Visuoconstruction', 1],
  ],
  MoCA: [
    ['Visuospatial/Executive', 5], ['Naming', 3], ['Attention', 6],
    ['Language', 3], ['Abstraction', 2], ['Delayed Recall', 5], ['Orientation', 6],
  ],
};

const getDefaultFormState = () => ({
  assessment_type: COGNITIVE_TEST_TYPES[0].label, // Default to MMSE
  score: '',
  max_possible_score: COGNITIVE_TEST_TYPES[0].max,
  assessment_date: new Date().toISOString().slice(0, 16), // datetime-local format
  diagnosis: '',
  notes: '',
  subscores: SUBSCORES_PRESETS.MMSE.map(([name, max]) => ({ name, score: '', max_score: max })),
});

export default function AssessmentForm({
  patientId,
  initialData = null,
  onSaved,
  onCancel, 
}) {
  const { addToast } = useNotifications();
  const [form, setForm] = useState(getDefaultFormState());
  const [loading, setLoading] = useState(false);

  const isEditing = useMemo(() => initialData !== null, [initialData]);

  useEffect(() => {
    if (initialData) {
      // Ensure the initialData.assessment_type is one of the COGNITIVE_TEST_TYPES
      // If not, it might be an audio test being mistakenly edited here, or 'Other'
      const initialTypeIsValid = COGNITIVE_TEST_TYPES.some(t => t.label === initialData.assessment_type);
      const typeToSet = initialTypeIsValid ? initialData.assessment_type : 'Other';
      
      setForm({
        assessment_type: typeToSet,
        score: initialData.score.toString(),
        max_possible_score: initialData.max_possible_score ?? COGNITIVE_TEST_TYPES.find(t => t.label === typeToSet)?.max ?? null,
        assessment_date: initialData.assessment_date ? new Date(initialData.assessment_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
        diagnosis: initialData.diagnosis || '',
        notes: initialData.notes || '',
        subscores: initialData.subscores?.map(s => ({
          name: s.name,
          score: s.score.toString(),
          max_score: s.max_score,
        })) || SUBSCORES_PRESETS[typeToSet]?.map(([name, max]) => ({ name, score: '', max_score: max })) || [],
      });
    } else {
      setForm(getDefaultFormState());
    }
  }, [initialData]);

  useEffect(() => {
    const typeObj = COGNITIVE_TEST_TYPES.find(t => t.label === form.assessment_type);
    const presets = SUBSCORES_PRESETS[form.assessment_type] || [];
    
    setForm(f => ({
      ...f,
      max_possible_score: typeObj?.max ?? null,
      subscores: presets.map(([name, max]) => {
        const existingSubscore = f.subscores?.find(s => s.name === name);
        return {
          name,
          score: existingSubscore?.score || '',
          max_score: max,
        };
      }),
    }));
  }, [form.assessment_type]);


  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubscoreChange = (idx, field, value) => {
    setForm(f => {
      const subs = [...f.subscores];
      subs[idx] = { ...subs[idx], [field]: value };
      return { ...f, subscores: subs };
    });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        score: parseFloat(form.score),
        max_possible_score: form.max_possible_score ? parseFloat(form.max_possible_score) : null,
        assessment_date: new Date(form.assessment_date).toISOString(),
        subscores: form.subscores.map(s => ({
          ...s,
          score: parseFloat(s.score),
          max_score: s.max_score ? parseFloat(s.max_score) : null,
        })).filter(s => s.score !== '' && !isNaN(s.score)), 
      };
      onSaved(payload, isEditing ? initialData.assessment_id : null);
    } catch(err) {
      addToast(`Save failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
        <div>
          <label htmlFor="assessment_type" className="block text-sm font-medium text-gray-700">Assessment Type</label>
          <select
            id="assessment_type"
            name="assessment_type"
            value={form.assessment_type}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {COGNITIVE_TEST_TYPES.map(t => (
              <option key={t.label} value={t.label}>{t.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="score" className="block text-sm font-medium text-gray-700">Overall Score / Max</label>
          <div className="mt-1 flex items-center space-x-2">
            <input
              id="score"
              name="score"
              type="number"
              step="any"
              value={form.score}
              onChange={handleChange}
              required
              className="block w-1/2 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Score"
            />
            <span className="text-gray-500">/ {form.max_possible_score ?? 'N/A'}</span>
          </div>
        </div>

        <div className="md:col-span-2">
          <label htmlFor="assessment_date" className="block text-sm font-medium text-gray-700">Date & Time</label>
          <input
            id="assessment_date"
            name="assessment_date"
            type="datetime-local"
            value={form.assessment_date}
            onChange={handleChange}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>

      {(form.assessment_type === 'MMSE' || form.assessment_type === 'MoCA') && form.subscores.length > 0 && (
        <div>
          <h4 className="text-md font-semibold text-gray-700 mb-2">Subscores</h4>
          <div className="space-y-3">
            {form.subscores.map((s, idx) => (
              <div key={idx} className="grid grid-cols-3 gap-2 items-center">
                <label htmlFor={`subscore-name-${idx}`} className="text-sm text-gray-600 col-span-1">{s.name}:</label>
                <input
                  id={`subscore-score-${idx}`}
                  type="number"
                  step="any"
                  value={s.score}
                  onChange={e => handleSubscoreChange(idx, 'score', e.target.value)}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm col-span-1"
                  placeholder="Score"
                />
                <span className="text-sm text-gray-500 col-span-1">/ {s.max_score}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <label htmlFor="diagnosis" className="block text-sm font-medium text-gray-700">Diagnosis (Optional)</label>
        <input
          id="diagnosis"
          name="diagnosis"
          type="text"
          value={form.diagnosis}
          onChange={handleChange}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="e.g., Mild Cognitive Impairment"
        />
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
        <textarea
          id="notes"
          name="notes"
          rows="3"
          value={form.notes}
          onChange={handleChange}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Any relevant observations..."
        />
      </div>

      <div className="flex items-center justify-end space-x-3 pt-3">
        {isEditing && onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Cancel Edit
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Saving...' : (isEditing ? 'Update Assessment' : 'Add Assessment')}
        </button>
      </div>
    </form>
  );
}