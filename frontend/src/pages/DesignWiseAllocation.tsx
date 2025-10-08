import React from 'react';
import DesignWiseBeamAllocationTable from '../components/Tables/DesignWiseBeamAllocationTable';

interface DesignWiseAllocationProps {
  refreshTrigger?: number;
}

const DesignWiseAllocation: React.FC<DesignWiseAllocationProps> = ({ refreshTrigger = 0 }) => {
  return (
    <div className="space-y-6">
      <div className="container">
        <DesignWiseBeamAllocationTable refreshTrigger={refreshTrigger} />
      </div>
    </div>
  );
};

export default DesignWiseAllocation;
