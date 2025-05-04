import React from 'react';
import { useNotifications } from '../context/NotificationContext';

export const ToastContainer = () => {
  const { toasts, removeToast } = useNotifications();
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`max-w-xs p-3 rounded shadow-md text-white ${
            t.type === 'success' ? 'bg-green-500' : t.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
          }`}
          onClick={() => removeToast(t.id)}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
};
