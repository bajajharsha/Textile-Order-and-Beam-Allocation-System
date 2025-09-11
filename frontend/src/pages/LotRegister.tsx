import React from 'react';
import LotRegisterTable from '../components/Tables/LotRegisterTable';

const LotRegister: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Lot Register</h1>
            <p className="page-subtitle">
              View and manage lot register with inline editing for bill numbers, actual pieces, and delivery dates
            </p>
          </div>
        </div>
      </div>
      
      <div className="container">
        <div className="table-section">
          <LotRegisterTable />
        </div>
      </div>
    </div>
  );
};

export default LotRegister;
