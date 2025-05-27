// frontend/renderer/src/api/export.js
import api from './patient';

export async function exportFeaturesCSV() {
  try {
    const response = await api.get('/export/features/csv', {
      responseType: 'blob', // Important for file downloads
    });
    
    // Create blob and download
    const blob = new Blob([response.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'neurocapture_features_export.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return { success: true };
  } catch (error) {
    console.error('Export error:', error);
    throw new Error(error.response?.data?.detail || 'Failed to export features');
  }
}
