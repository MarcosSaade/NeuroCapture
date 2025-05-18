// src/components/AssessmentList.jsx

import React from 'react';

export default function AssessmentList({
  assessments,
  onEdit,
  onDelete
}) {
  if (!assessments.length) {
    return <div className="text-gray-500">No assessments yet.</div>;
  }

  return (
    <table className="table-auto w-full mt-4 border-collapse">
      <thead>
        <tr>
          <th className="px-2 py-1 border-b">Type</th>
          <th className="px-2 py-1 border-b">Score</th>
          <th className="px-2 py-1 border-b">Date</th>
          <th className="px-2 py-1 border-b">Diagnosis</th>
          <th className="px-2 py-1 border-b">Notes</th>
          <th className="px-2 py-1 border-b">Subscores</th>
          <th className="px-2 py-1 border-b">Actions</th>
        </tr>
      </thead>
      <tbody>
        {assessments.map(a => (
          <tr key={a.assessment_id} className="hover:bg-gray-50">
            <td className="px-2 py-1">{a.assessment_type}</td>
            <td className="px-2 py-1">
              {a.score} / {a.max_possible_score ?? '–'}
            </td>
            <td className="px-2 py-1">
              {new Date(a.assessment_date).toLocaleString()}
            </td>
            <td className="px-2 py-1">{a.diagnosis || '-'}</td>
            <td className="px-2 py-1">{a.notes || '-'}</td>
            <td className="px-2 py-1">
              {a.subscores && a.subscores.length > 0
                ? a.subscores
                    .map(
                      s => `${s.name}: ${s.score}/${s.max_score}`
                    )
                    .join(', ')
                : '-'}
            </td>
            <td className="px-2 py-1 space-x-2">
              <button
                onClick={() => onEdit(a)}
                className="text-blue-600"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(a.assessment_id)}
                className="text-red-600"
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
