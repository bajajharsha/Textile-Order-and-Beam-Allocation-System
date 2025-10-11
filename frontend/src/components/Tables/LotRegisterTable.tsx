import React, { useCallback, useEffect, useState } from 'react';
import { lotApi, LotRegisterItem } from '../../services/api';
import SetBasedLotCreationForm from '../Forms/SetBasedLotCreationForm';

interface LotRegisterTableProps {
  refreshTrigger?: number;
  onLotUpdated?: () => void;
  lotRegisterType?: string;
}

interface GroupedData {
  [partyName: string]: LotRegisterItem[];
}

const LotRegisterTable: React.FC<LotRegisterTableProps> = ({ refreshTrigger = 0, onLotUpdated, lotRegisterType }) => {
  const [data, setData] = useState<LotRegisterItem[]>([]);
  const [groupedData, setGroupedData] = useState<GroupedData>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingCell, setEditingCell] = useState<{ partyName: string; rowIndex: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [expandedParties, setExpandedParties] = useState<Set<string>>(new Set());
  const [showSetBasedLotForm, setShowSetBasedLotForm] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching lot register data for type:', lotRegisterType);
      const response = await lotApi.getLotRegister(1, 100, lotRegisterType || undefined);
      const items = response.data.items || [];
      console.log('Received lot register items:', items.length);
      setData(items);
      
      // Group data by party name
      const grouped: GroupedData = {};
      items.forEach(item => {
        if (!grouped[item.party_name]) {
          grouped[item.party_name] = [];
        }
        grouped[item.party_name].push(item);
      });
      setGroupedData(grouped);
      
      // Auto-expand all parties initially
      setExpandedParties(new Set(Object.keys(grouped)));
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

  const togglePartyExpansion = (partyName: string) => {
    const newExpanded = new Set(expandedParties);
    if (newExpanded.has(partyName)) {
      newExpanded.delete(partyName);
    } else {
      newExpanded.add(partyName);
    }
    setExpandedParties(newExpanded);
  };

  const handleCellClick = (partyName: string, rowIndex: number, field: string, currentValue: any) => {
    // Only allow editing of manually entered fields
    const editableFields = ['lot_date', 'lot_no', 'bill_no', 'actual_pieces', 'delivery_date'];
    if (!editableFields.includes(field)) return;

    setEditingCell({ partyName, rowIndex, field });
    setEditValue(currentValue?.toString() || '');
  };

  const handleCellBlur = async () => {
    if (!editingCell) return;

    const { partyName, rowIndex, field } = editingCell;
    const item = groupedData[partyName][rowIndex];
    
    
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
        const newGroupedData = { ...groupedData };
        newGroupedData[partyName][rowIndex] = {
          ...newGroupedData[partyName][rowIndex],
          [field]: field === 'actual_pieces' ? (editValue ? parseInt(editValue) : null) : editValue
        };
        setGroupedData(newGroupedData);
        
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

  const renderCell = (item: LotRegisterItem, partyName: string, rowIndex: number, field: string) => {
    const isEditing = editingCell?.partyName === partyName && editingCell?.rowIndex === rowIndex && editingCell?.field === field;
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
        onClick={() => handleCellClick(partyName, rowIndex, field, value)}
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

  if (Object.keys(groupedData).length === 0) {
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
            {Object.keys(groupedData).length}
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

      {/* Grouped Data by Party */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {Object.entries(groupedData).map(([partyName, items]) => (
          <div key={partyName} style={{ 
            border: '1px solid var(--color-border)', 
            borderRadius: 'var(--border-radius)', 
            overflow: 'hidden',
            backgroundColor: 'var(--color-surface)'
          }}>
            {/* Party Header */}
            <div 
              style={{
                backgroundColor: 'var(--color-surface-hover)',
                padding: '1rem',
                cursor: 'pointer',
                transition: 'var(--transition-fast)',
                borderBottom: expandedParties.has(partyName) ? '1px solid var(--color-border)' : 'none'
              }}
              onClick={() => togglePartyExpansion(partyName)}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--color-border)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)'}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', fontWeight: 600 }}>
                    {expandedParties.has(partyName) ? '▼' : '▶'} {partyName}
                  </span>
                  <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                    ({items.length} designs)
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                      Total Pieces: {items.reduce((sum, item) => sum + item.total_pieces, 0).toLocaleString()}
                    </div>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                      Lots: {new Set(items.map(item => item.lot_id).filter(id => id)).size}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Party Items */}
            {expandedParties.has(partyName) && (
              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Lot No. Date</th>
                      <th>Lot No.</th>
                      <th>Design No.</th>
                      <th>Quality</th>
                      <th>
                        Total Pieces<br/>
                        <span style={{ fontSize: '0.6875rem', fontWeight: 400, textTransform: 'none', color: 'var(--color-text-muted)' }}>(Sets × designs)</span>
                      </th>
                      <th>Bill No.</th>
                      <th>Actual Pieces</th>
                      <th>Delivery Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item, index) => (
                      <tr key={`${item.lot_id}-${item.allocation_id}-${item.design_no}`}>
                        <td>{renderCell(item, partyName, index, 'lot_date')}</td>
                        <td>{renderCell(item, partyName, index, 'lot_no')}</td>
                        <td>{item.design_no}</td>
                        <td>{item.quality}</td>
                        <td>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontWeight: 500 }}>{item.total_pieces.toLocaleString()}</span>
                            {item.sets && item.ground_colors_count && (
                              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                                ({item.sets} × {item.ground_colors_count})
                              </span>
                            )}
                          </div>
                        </td>
                        <td>{renderCell(item, partyName, index, 'bill_no')}</td>
                        <td>{renderCell(item, partyName, index, 'actual_pieces')}</td>
                        <td>{renderCell(item, partyName, index, 'delivery_date')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
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
