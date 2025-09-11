import React, { useEffect, useState } from 'react';
import { lotApi, LotRegisterItem } from '../../services/api';

interface LotRegisterTableProps {
  refreshTrigger?: number;
}

const LotRegisterTable: React.FC<LotRegisterTableProps> = ({ refreshTrigger = 0 }) => {
  const [data, setData] = useState<LotRegisterItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingCell, setEditingCell] = useState<{ rowIndex: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await lotApi.getLotRegister();
      setData(response.data.items || []);
    } catch (err) {
      console.error('Error fetching lot register:', err);
      setError('Failed to fetch lot register data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [refreshTrigger]);

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-GB');
  };

  const handleCellClick = (rowIndex: number, field: string, currentValue: any) => {
    // Only allow editing of manually entered fields
    const editableFields = ['bill_no', 'actual_pieces', 'delivery_date'];
    if (!editableFields.includes(field)) return;

    setEditingCell({ rowIndex, field });
    setEditValue(currentValue?.toString() || '');
  };

  const handleCellBlur = async () => {
    if (!editingCell) return;

    const { rowIndex, field } = editingCell;
    const item = data[rowIndex];
    
    try {
      // If lot_no is being entered and there's no lot_id, create a new lot
      if (field === 'lot_no' && !item.lot_id && editValue.trim()) {
        // Create lot from order
        const lotData = {
          order_id: item.order_id,
          lot_number: editValue.trim(),
          lot_date: new Date().toISOString().split('T')[0], // Today's date
          party_id: item.party_id,
          quality_id: item.quality_id
        };
        
        await lotApi.createLotFromRegister(lotData);
        
        // Refresh data to show the new lot
        await fetchData();
      } else if (item.lot_id) {
        // Update existing lot field
        await lotApi.updateLotField(item.lot_id, field, editValue);
        
        // Update local state
        const newData = [...data];
        newData[rowIndex] = {
          ...newData[rowIndex],
          [field]: field === 'actual_pieces' ? (editValue ? parseInt(editValue) : null) : editValue
        };
        setData(newData);
      }
      
      setEditingCell(null);
      setEditValue('');
    } catch (err) {
      console.error('Error updating field:', err);
      setError('Failed to update field');
      setEditingCell(null);
      setEditValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCellBlur();
    } else if (e.key === 'Escape') {
      setEditingCell(null);
      setEditValue('');
    }
  };

  const renderCell = (item: LotRegisterItem, rowIndex: number, field: string) => {
    const isEditing = editingCell?.rowIndex === rowIndex && editingCell?.field === field;
    const value = item[field as keyof LotRegisterItem];
    
    if (isEditing) {
      return (
        <input
          type={field === 'actual_pieces' ? 'number' : field === 'delivery_date' ? 'date' : 'text'}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={handleCellBlur}
          onKeyDown={handleKeyPress}
          className="inline-edit-input"
          autoFocus
        />
      );
    }

    const displayValue = field === 'lot_date' || field === 'delivery_date' 
      ? formatDate(value as string)
      : value?.toString() || '-';

    const isEditable = ['bill_no', 'actual_pieces', 'delivery_date'].includes(field);
    
    return (
      <span 
        className={isEditable ? 'editable-cell' : ''}
        onClick={() => handleCellClick(rowIndex, field, value)}
      >
        {displayValue}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="table-container">
        <div className="table-loading">
          <div className="loading-spinner"></div>
          <p>Loading lot register data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="table-container">
        <div className="table-error">
          <p>{error}</p>
          <button onClick={fetchData} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="table-container">
        <div className="table-empty">
          <p>No lot register data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-container">
      <div className="table-header">
        <h3 className="table-title">Lot Register</h3>
        <div className="table-actions">
          <button onClick={fetchData} className="btn btn-secondary">
            Refresh
          </button>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Lot No. Date</th>
              <th>Lot No.</th>
              <th>Party Name</th>
              <th>Design No.</th>
              <th>Quality</th>
              <th>Total Pieces</th>
              <th>Bill No.</th>
              <th>Actual Pieces</th>
              <th>Delivery Date</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={`${item.lot_id}-${item.allocation_id}-${item.design_no}`} className="data-row">
                <td>{renderCell(item, index, 'lot_date')}</td>
                <td>{renderCell(item, index, 'lot_no')}</td>
                <td>{renderCell(item, index, 'party_name')}</td>
                <td>{renderCell(item, index, 'design_no')}</td>
                <td>{renderCell(item, index, 'quality')}</td>
                <td>{renderCell(item, index, 'total_pieces')}</td>
                <td>{renderCell(item, index, 'bill_no')}</td>
                <td>{renderCell(item, index, 'actual_pieces')}</td>
                <td>{renderCell(item, index, 'delivery_date')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Section */}
      <div className="table-summary">
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Total Lots:</span>
            <span className="stat-value">
              {new Set(data.map(item => item.lot_id)).size}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Designs:</span>
            <span className="stat-value">{data.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Pieces:</span>
            <span className="stat-value">
              {data.reduce((sum, item) => sum + item.total_pieces, 0)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LotRegisterTable;
