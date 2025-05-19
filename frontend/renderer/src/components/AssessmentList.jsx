// frontend/renderer/src/components/AssessmentList.jsx
import React from 'react';
import { PencilSquareIcon, TrashIcon } from '@heroicons/react/24/outline';

export default function AssessmentList({ assessments, onEdit, onDelete }) {
  if (!assessments || assessments.length === 0) {
    return <p className="text-center text-gray-500 py-4">No assessments recorded yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Diagnosis</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subscores</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {assessments.map(a => (
            <tr key={a.assessment_id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{a.assessment_type}</td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {a.score} / {a.max_possible_score ?? 'N/A'}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {new Date(a.assessment_date).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{a.diagnosis || <span className="italic text-gray-400">None</span>}</td>
              <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate" title={a.subscores?.map(s => `${s.name}: ${s.score}/${s.max_score || 'N/A'}`).join('; ') || ''}>
                {a.subscores && a.subscores.length > 0
                  ? `${a.subscores.length} subscore(s)`
                  : <span className="italic text-gray-400">None</span>}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm font-medium space-x-2">
                <button
                  onClick={() => onEdit(a)}
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                  title="Edit Assessment"
                >
                  <PencilSquareIcon className="h-5 w-5 inline-block" />
                </button>
                <button
                  onClick={() => onDelete(a.assessment_id)}
                  className="text-red-600 hover:text-red-800 transition-colors"
                  title="Delete Assessment"
                >
                  <TrashIcon className="h-5 w-5 inline-block" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}