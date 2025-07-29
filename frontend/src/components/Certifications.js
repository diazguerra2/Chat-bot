import React from 'react';
import LoadingSpinner from './LoadingSpinner';

const Certifications = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ISTQB Certifications
        </h1>
        <p className="text-gray-600">
          Explore all available ISTQB certifications and find the right path for your career.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
        <LoadingSpinner text="Loading certifications..." />
        <div className="text-center mt-4">
          <p className="text-gray-600">This feature is being implemented...</p>
        </div>
      </div>
    </div>
  );
};

export default Certifications;
