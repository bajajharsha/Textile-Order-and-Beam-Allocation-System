import React from 'react';
import PartywiseDetailTable from '../components/Tables/PartywiseDetailTable';

interface PartywiseDetailProps {
  refreshTrigger?: number;
}

const PartywiseDetail: React.FC<PartywiseDetailProps> = ({ refreshTrigger = 0 }) => {
  return (
    <div className="space-y-6">
      <div className="container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Partywise Detail Report</h1>
            <p className="page-subtitle">
              View all orders grouped by party with lot allocation details
            </p>
          </div>
        </div>
      </div>
      
      <div className="container">
        <div className="table-section">
          <PartywiseDetailTable refreshTrigger={refreshTrigger} />
        </div>
      </div>
    </div>
  );
};

export default PartywiseDetail;
