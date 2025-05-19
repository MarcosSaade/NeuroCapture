// frontend/renderer/src/components/PatientTable.jsx
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { fetchPatients, deletePatient } from '../api/patient';
import { useNotifications } from '../context/NotificationContext';
import { TableCellsIcon, PencilSquareIcon, TrashIcon, ArrowUpIcon, ArrowDownIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline'; // Using outline icons

const statusColors = {
  complete: 'bg-green-100 text-green-700',
  incomplete: 'bg-yellow-100 text-yellow-700',
  pending: 'bg-slate-100 text-slate-700',
  error: 'bg-red-100 text-red-700'
};

const SortableHeader = ({ children, field, currentSort, onSort }) => {
  const isActive = currentSort.field === field;
  const Icon = isActive ? (currentSort.asc ? ArrowUpIcon : ArrowDownIcon) : TableCellsIcon;
  return (
    <th
      scope="col"
      onClick={() => onSort(field)}
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
    >
      <div className="flex items-center">
        {children}
        <Icon className={`ml-1 h-4 w-4 ${isActive ? 'text-gray-700' : 'text-gray-400'}`} />
      </div>
    </th>
  );
};

export default function PatientTable({ onEdit, refresh }) {
  const [patients, setPatients] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(10); // Reduced for better pagination demo
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  // const [statusFilter, setStatusFilter] = useState('all'); // Status field not on patient model yet
  const [sortConfig, setSortConfig] = useState({ field: 'patient_id', asc: true });
  const { addToast } = useNotifications();

  const loadPatients = useCallback(async (currentSkip, currentLimit) => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchPatients(currentSkip, currentLimit);
      setPatients(data); // Assuming API returns an array
    } catch (err) {
      setError('Failed to load patients. Please try again.');
      addToast('Failed to load patients.', 'error');
      setPatients([]); // Clear patients on error
    } finally {
      setLoading(false);
    }
  }, [addToast]);


  useEffect(() => {
    loadPatients(skip, limit);
  }, [skip, limit, refresh, loadPatients]);

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this patient? This action cannot be undone.')) return;
    try {
      await deletePatient(id);
      addToast('Patient deleted successfully!', 'success');
      // Refresh data: if on last page with one item, might need to go to prev page
      if (patients.length === 1 && skip > 0) {
        setSkip(s => Math.max(0, s - limit));
      } else {
        loadPatients(skip, limit); // Or simply trigger refresh via key
      }
    } catch {
      addToast('Failed to delete patient.', 'error');
    }
  };

  const filteredAndSortedPatients = useMemo(() => {
    let processedPatients = [...patients];

    if (search) {
      processedPatients = processedPatients.filter(p =>
        p.study_identifier.toLowerCase().includes(search.toLowerCase())
      );
    }

    // Sorting
    processedPatients.sort((a, b) => {
      const valA = a[sortConfig.field];
      const valB = b[sortConfig.field];
      if (valA < valB) return sortConfig.asc ? -1 : 1;
      if (valA > valB) return sortConfig.asc ? 1 : -1;
      return 0;
    });

    return processedPatients;
  }, [patients, search, sortConfig]);

  const handleSort = (field) => {
    setSortConfig(prevConfig => ({
      field,
      asc: prevConfig.field === field ? !prevConfig.asc : true,
    }));
  };
  
  const exportCSV = () => {
    const headers = ['Patient ID','Study ID','Created At','Updated At']; // Adjusted to actual fields
    const rows = filteredAndSortedPatients.map(p => [
      p.patient_id,
      p.study_identifier,
      new Date(p.created_at).toLocaleString(),
      new Date(p.updated_at).toLocaleString()
    ]);
    const csvContent = [headers, ...rows]
      .map(r => r.map(String).map(s => `"${s.replace(/"/g,'""')}"`).join(','))
      .join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'patients_export.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
    addToast('CSV export initiated.', 'info');
  };


  return (
    <div className="bg-white shadow-lg rounded-lg p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row items-center justify-between mb-4 gap-4">
        <input
          type="text"
          placeholder="Search by Study ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <button
          onClick={exportCSV}
          disabled={filteredAndSortedPatients.length === 0}
          className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 transition-colors"
        >
          <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
          Export CSV
        </button>
      </div>

      {loading && <p className="text-center py-4 text-gray-500">Loading patients...</p>}
      {error && <p className="text-center py-4 text-red-500 bg-red-50 p-3 rounded-md">{error}</p>}
      
      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <SortableHeader field="patient_id" currentSort={sortConfig} onSort={handleSort}>ID</SortableHeader>
                <SortableHeader field="study_identifier" currentSort={sortConfig} onSort={handleSort}>Study ID</SortableHeader>
                <SortableHeader field="created_at" currentSort={sortConfig} onSort={handleSort}>Created At</SortableHeader>
                <SortableHeader field="updated_at" currentSort={sortConfig} onSort={handleSort}>Updated At</SortableHeader>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAndSortedPatients.map((p) => (
                <tr key={p.patient_id} className="hover:bg-slate-50 transition-colors duration-150">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{p.patient_id}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-blue-600 hover:text-blue-800">
                    <Link to={`/patients/${p.patient_id}`}>{p.study_identifier}</Link>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{new Date(p.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{new Date(p.updated_at).toLocaleString()}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => onEdit(p.patient_id)}
                      className="text-blue-600 hover:text-blue-800 transition-colors"
                      title="Edit Patient"
                    >
                      <PencilSquareIcon className="h-5 w-5 inline-block" />
                    </button>
                    <button
                      onClick={() => handleDelete(p.patient_id)}
                      className="text-red-600 hover:text-red-800 transition-colors"
                      title="Delete Patient"
                    >
                      <TrashIcon className="h-5 w-5 inline-block" />
                    </button>
                  </td>
                </tr>
              ))}
              {filteredAndSortedPatients.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-10 text-gray-500">
                    No patients found matching your criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && patients.length > 0 && (
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => setSkip(s => Math.max(0, s - limit))}
            disabled={skip === 0 || loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            Previous
          </button>
          <span className="text-sm text-gray-700">
            Page {Math.floor(skip / limit) + 1}
            {/* You might want to add total count from API for "of X pages" */}
          </span>
          <button
            onClick={() => setSkip(s => s + limit)}
            disabled={patients.length < limit || loading} // Disable if current page is not full
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}