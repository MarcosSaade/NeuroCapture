// frontend/renderer/src/components/ProgressBar.jsx
import React from 'react';

export default function ProgressBar({ progress, className = "", animated = true }) {
  const percentage = Math.round(progress * 100);
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
      <div 
        className={`bg-blue-600 h-2.5 rounded-full transition-all duration-300 ${
          animated ? 'animate-pulse' : ''
        }`}
        style={{ width: `${percentage}%` }}
      ></div>
      <div className="text-xs text-gray-600 mt-1 text-center">
        {percentage}%
      </div>
    </div>
  );
}
