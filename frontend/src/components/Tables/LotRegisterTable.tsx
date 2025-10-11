import React, { useCallback, useEffect, useState } from 'react';
import { lotApi, LotRegisterItem } from '../../services/api';
import SetBasedLotCreationForm from '../Forms/SetBasedLotCreationForm';

interface LotRegisterTableProps {
  refreshTrigger?: number;
  onLotUpdated?: () => void;
  lotRegisterType?: string;
}


const LotRegisterTable: React.FC<LotRegisterTableProps> = ({ refreshTrigger = 0, onLotUpdated, lotRegisterType }) => {
  const [data, setData] = useState<LotRegisterItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingCell, setEditingCell] = useState<{ rowIndex: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [showSetBasedLotForm, setShowSetBasedLotForm] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching lot register data for type:', lotRegisterType);
      const response = await lotApi.getLotRegister(1, 100, lotRegisterType || undefined);
      const items = response.data.items || [];
      console.log('Received lot register items:', items.length);
      
      // Sort by date (newest first)
      const sortedItems = items.sort((a, b) => {
        const dateA = new Date(a.lot_date || 0).getTime();
        const dateB = new Date(b.lot_date || 0).getTime();
        return dateB - dateA;
      });
      
      setData(sortedItems);
    } catch (err) {
      console.error('Error fetching lot register:', err);
      setError('Failed to fetch lot register data');
    } finally {
      setLoading(false);
    }
  }, [lotRegisterType]);

  useEffect(() => {
    fetchData();
  }, [refreshTrigger, fetchData]);



  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-GB');
  };


  const handleCellClick = (rowIndex: number, field: string, currentValue: any) => {
    // Only allow editing of manually entered fields
    const editableFields = ['lot_date', 'lot_no', 'bill_no', 'actual_pieces', 'delivery_date'];
    if (!editableFields.includes(field)) return;

    setEditingCell({ rowIndex, field });
    setEditValue(currentValue?.toString() || '');
  };

  const handleCellBlur = async () => {
    if (!editingCell) return;

    const { rowIndex, field } = editingCell;
    const item = data[rowIndex];
    
    
    try {
      // Map frontend field names to backend field names
      const fieldMapping: { [key: string]: string } = {
        'lot_no': 'lot_number',
        'bill_no': 'bill_number',
        'lot_date': 'lot_date',
        'actual_pieces': 'actual_pieces',
        'delivery_date': 'delivery_date'
      };
      
      const backendField = fieldMapping[field] || field;
      
      // If lot_no is being entered and there's no lot_id, create a new lot for this specific design
      if (field === 'lot_no' && !item.lot_id && editValue.trim()) {
        // Create lot for this specific design only
        const lotData = {
          order_id: item.order_id,
          design_number: item.design_no,
          lot_number: editValue.trim(),
          lot_date: new Date().toISOString().split('T')[0], // Today's date
          party_id: item.party_id,
          quality_id: item.quality_id
        };
        
        await lotApi.createLotForDesign(lotData);
        
        // Refresh data to show the new lot
        await fetchData();
        
        // Notify parent component that lot was updated
        onLotUpdated?.();
      } else if (item.lot_id) {
        // Update existing lot field
        await lotApi.updateLotField(item.lot_id, backendField, editValue);
        
        // Update local state
        const newData = [...data];
        newData[rowIndex] = {
          ...newData[rowIndex],
          [field]: field === 'actual_pieces' ? (editValue ? parseInt(editValue) : null) : editValue
        };
        setData(newData);
        
        // Notify parent component that lot was updated
        onLotUpdated?.();
      } else if (!item.lot_id && field !== 'lot_no') {
        // If trying to edit other fields without a lot, show error
        setError('Please enter a lot number first before editing other fields');
        setEditingCell(null);
        setEditValue('');
        return;
      }
      
      setEditingCell(null);
      setEditValue('');
    } catch (err: any) {
      console.error('Error updating field:', err);
      console.error('Error details:', err.response?.data || err.message);
      setError(`Failed to update field: ${err.response?.data?.detail || err.message}`);
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
          type={field === 'actual_pieces' ? 'number' : (field === 'delivery_date' || field === 'lot_date') ? 'date' : 'text'}
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

    const isEditable = ['lot_date', 'lot_no', 'bill_no', 'actual_pieces', 'delivery_date'].includes(field);
    
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
      <div>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '1.5rem',
          padding: '1rem',
          backgroundColor: 'var(--color-surface)',
          borderRadius: 'var(--border-radius)',
          border: '1px solid var(--color-border)'
        }}>
          <div className="flex gap-3">
            <button onClick={fetchData} className="btn btn-secondary">
              Refresh
            </button>
            <button 
              onClick={() => setShowSetBasedLotForm(true)} 
              className="btn btn-primary"
            >
              + Create Lot
            </button>
          </div>
        </div>

        <div className="table-container">
          <div className="table-empty">
            <p>No lot register data available</p>
          </div>
        </div>

        {/* Set-Based Lot Creation Form Modal (New System) */}
        {showSetBasedLotForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <SetBasedLotCreationForm
                onLotCreated={() => {
                  setShowSetBasedLotForm(false);
                  fetchData(); // Refresh lot register
                  if (onLotUpdated) {
                    onLotUpdated();
                  }
                }}
                onCancel={() => setShowSetBasedLotForm(false)}
              />
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1.5rem',
        padding: '1rem',
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--border-radius)',
        border: '1px solid var(--color-border)'
      }}>
        <div className="flex gap-3">
          <button onClick={fetchData} className="btn btn-secondary">
            Refresh
          </button>
          <button 
            onClick={() => setShowSetBasedLotForm(true)} 
            className="btn btn-primary"
          >
            + Create Lot
          </button>
        </div>
      </div>

      {/* Summary Section */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <div style={{ 
          padding: '1rem',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--border-radius)'
        }}>
          <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
            Total Parties:
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {new Set(data.map(item => item.party_name)).size}
          </div>
        </div>
        <div style={{ 
          padding: '1rem',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--border-radius)'
        }}>
          <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
            Total Designs:
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {data.length}
          </div>
        </div>
        <div style={{ 
          padding: '1rem',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--border-radius)'
        }}>
          <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
            Total Pieces:
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              {data.reduce((sum, item) => sum + item.total_pieces, 0)}
          </div>
        </div>
      </div>

      {/* Simple Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: 'var(--color-surface-hover)' }}>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Lot No. Date</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Party Name</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Lot No.</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Design No.</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Quality</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Pieces<br/>
                <span style={{ fontSize: '0.6875rem', fontWeight: 400, textTransform: 'none', color: 'var(--color-text-muted)' }}>(Sets × designs)</span>
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bill No.</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Actual Pieces</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Delivery Date</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={`${item.lot_id}-${item.allocation_id}-${item.design_no}`} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{renderCell(item, index, 'lot_date')}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.party_name}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{renderCell(item, index, 'lot_no')}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.design_no}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.quality}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontWeight: 500 }}>{item.total_pieces.toLocaleString()}</span>
                    {item.sets && item.ground_colors_count && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                        ({item.sets} × {item.ground_colors_count})
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{renderCell(item, index, 'bill_no')}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{renderCell(item, index, 'actual_pieces')}</td>
                <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{renderCell(item, index, 'delivery_date')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>


      {/* Set-Based Lot Creation Form Modal (New System) */}
      {showSetBasedLotForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <SetBasedLotCreationForm
              onLotCreated={() => {
                setShowSetBasedLotForm(false);
                fetchData(); // Refresh lot register
                if (onLotUpdated) {
                  onLotUpdated();
                }
              }}
              onCancel={() => setShowSetBasedLotForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default LotRegisterTable;
