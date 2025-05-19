// frontend/renderer/src/components/Toast.jsx
import React from 'react';
import { XCircleIcon, CheckCircleIcon, InformationCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/solid';
import { useNotifications } from '../context/NotificationContext';

const icons = {
  success: <CheckCircleIcon className="h-6 w-6 text-green-100 mr-3" />,
  error: <XCircleIcon className="h-6 w-6 text-red-100 mr-3" />,
  info: <InformationCircleIcon className="h-6 w-6 text-blue-100 mr-3" />,
  warning: <ExclamationTriangleIcon className="h-6 w-6 text-yellow-100 mr-3" />,
};

const bgColors = {
  success: 'bg-green-500',
  error: 'bg-red-500',
  info: 'bg-blue-500',
  warning: 'bg-yellow-500',
};

export const ToastContainer = () => {
  const { toasts, removeToast } = useNotifications();
  
  if (!toasts.length) return null;

  return (
    <div className="fixed top-6 right-6 z-[100] w-full max-w-xs sm:max-w-sm space-y-3">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-center p-4 rounded-lg shadow-2xl text-white ${
            bgColors[t.type] || bgColors.info
          } cursor-pointer transition-all duration-300 ease-in-out transform hover:scale-105`}
          onClick={() => removeToast(t.id)}
          role="alert"
          aria-live="assertive"
        >
          {icons[t.type] || icons.info}
          <span className="flex-1 text-sm font-medium">{t.message}</span>
        </div>
      ))}
    </div>
  );
};