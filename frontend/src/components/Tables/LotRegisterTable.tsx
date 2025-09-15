import React, { useEffect, useState } from 'react';
import { lotApi, LotRegisterItem } from '../../services/api';

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

  const fetchData = async () => {
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
  };

  useEffect(() => {
    fetchData();
  }, [refreshTrigger, lotRegisterType]);

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

      {/* Summary Section */}
      <div className="table-summary">
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Total Parties:</span>
            <span className="stat-value">{Object.keys(groupedData).length}</span>
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

      {/* Grouped Data by Party */}
      <div className="space-y-4">
        {Object.entries(groupedData).map(([partyName, items]) => (
          <div key={partyName} className="border border-gray-200 rounded-lg overflow-hidden">
            {/* Party Header */}
            <div 
              className="bg-gray-50 px-4 py-3 cursor-pointer hover:bg-gray-100"
              onClick={() => togglePartyExpansion(partyName)}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-semibold text-gray-800">
                    {expandedParties.has(partyName) ? '▼' : '▶'} {partyName}
                  </span>
                  <span className="text-sm text-gray-600">
                    ({items.length} designs)
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">
                    Total Pieces: {items.reduce((sum, item) => sum + item.total_pieces, 0).toLocaleString()}
                  </div>
                  <div className="text-sm font-medium text-gray-800">
                    Lots: {new Set(items.map(item => item.lot_id).filter(id => id)).size}
                  </div>
                </div>
              </div>
            </div>

            {/* Party Items */}
            {expandedParties.has(partyName) && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Lot No. Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Lot No.</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Design No.</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Quality</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total Pieces</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Bill No.</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actual Pieces</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Delivery Date</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {items.map((item, index) => (
                      <tr key={`${item.lot_id}-${item.allocation_id}-${item.design_no}`} className={item.lot_no ? 'bg-green-50' : 'bg-yellow-50'}>
                        <td className="px-4 py-2 text-sm text-gray-900">{renderCell(item, partyName, index, 'lot_date')}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{renderCell(item, partyName, index, 'lot_no')}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{item.design_no}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{item.quality}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{item.total_pieces.toLocaleString()}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{renderCell(item, partyName, index, 'bill_no')}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{renderCell(item, partyName, index, 'actual_pieces')}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{renderCell(item, partyName, index, 'delivery_date')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>


    </div>
  );
};

export default LotRegisterTable;
