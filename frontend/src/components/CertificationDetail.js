import React from 'react';
import { useParams } from 'react-router-dom';
import LoadingSpinner from './LoadingSpinner';

const CertificationDetail = () => {
  const { certId } = useParams();

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Certification Details: {certId}
        </h1>
        <p className="text-gray-600">
          Detailed information about the {certId} certification.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
        <LoadingSpinner text="Loading certification details..." />
        <div className="text-center mt-4">
          <p className="text-gray-600">This feature is being implemented...</p>
        </div>
      </div>
    </div>
  );
};

export default CertificationDetail;
