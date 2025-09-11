import React, { useEffect, useState } from 'react';
import {
    LotAllocationItem,
    LotCreate,
    OrderItemStatusResponse,
    Party,
    Quality,
    lotApi,
    masterApi,
    partyApi
} from '../../services/api';

interface LotFormProps {
  onSubmit: (data: LotCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const LotForm: React.FC<LotFormProps> = ({ onSubmit, onCancel, isLoading = false }) => {
  // Form state
  const [formData, setFormData] = useState<LotCreate>({
    party_id: 0,
    quality_id: 0,
    lot_date: new Date().toISOString().split('T')[0],
    bill_number: '',
    actual_pieces: undefined,
    delivery_date: '',
    notes: '',
    allocations: []
  });

  // Dropdown data
  const [parties, setParties] = useState<Party[]>([]);
  const [qualities, setQualities] = useState<Quality[]>([]);
  const [availableAllocations, setAvailableAllocations] = useState<OrderItemStatusResponse[]>([]);
  const [filteredAllocations, setFilteredAllocations] = useState<OrderItemStatusResponse[]>([]);
  
  // UI state
  const [loadingData, setLoadingData] = useState(true);
  const [selectedAllocations, setSelectedAllocations] = useState<{ [key: string]: number }>({});

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (formData.party_id && formData.quality_id) {
      loadAvailableAllocations();
    }
  }, [formData.party_id, formData.quality_id]);

  const loadInitialData = async () => {
    try {
      setLoadingData(true);
      const [partiesRes, masterRes] = await Promise.all([
        partyApi.getAll(1, 100),
        masterApi.getDropdownData()
      ]);

      setParties(partiesRes.data.parties);
      setQualities(masterRes.data.qualities);
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const loadAvailableAllocations = async () => {
    try {
      const response = await lotApi.getAvailableAllocations(
        formData.party_id || undefined, 
        formData.quality_id || undefined
      );
      setAvailableAllocations(response.data);
      filterAllocations(response.data);
    } catch (error) {
      console.error('Error loading available allocations:', error);
    }
  };

  const filterAllocations = (allocations: OrderItemStatusResponse[]) => {
    let filtered = allocations;
    
    if (formData.party_id) {
      filtered = filtered.filter(item => 
        item.party_name?.toLowerCase().includes(parties.find(p => p.id === formData.party_id)?.party_name.toLowerCase() || '')
      );
    }
    
    if (formData.quality_id) {
      filtered = filtered.filter(item => 
        item.quality_name?.toLowerCase().includes(qualities.find(q => q.id === formData.quality_id)?.quality_name.toLowerCase() || '')
      );
    }

    setFilteredAllocations(filtered);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'party_id' || name === 'quality_id' || name === 'actual_pieces' 
        ? (value ? parseInt(value) : 0) 
        : value
    }));
  };

  const handleAllocationChange = (itemKey: string, pieces: number) => {
    setSelectedAllocations(prev => ({
      ...prev,
      [itemKey]: pieces
    }));
  };

  const getItemKey = (item: OrderItemStatusResponse) => 
    `${item.order_id}-${item.design_number}-${item.ground_color_name}`;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Build allocations from selected items
    const allocations: LotAllocationItem[] = [];
    
    Object.entries(selectedAllocations).forEach(([itemKey, pieces]) => {
      if (pieces > 0) {
        const item = filteredAllocations.find(alloc => getItemKey(alloc) === itemKey);
        if (item) {
          allocations.push({
            order_id: item.order_id,
            design_number: item.design_number,
            ground_color_name: item.ground_color_name,
            beam_color_id: item.beam_color_id,
            allocated_pieces: pieces
          });
        }
      }
    });

    if (allocations.length === 0) {
      alert('Please select at least one allocation');
      return;
    }

    const submitData: LotCreate = {
      ...formData,
      allocations,
      actual_pieces: formData.actual_pieces || undefined,
      lot_date: formData.lot_date || undefined,
      delivery_date: formData.delivery_date || undefined
    };

    onSubmit(submitData);
  };

  if (loadingData) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading form data...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Create New Lot</h2>
        <button
          onClick={onCancel}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Lot Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Party *
            </label>
            <select
              name="party_id"
              value={formData.party_id}
              onChange={handleInputChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Party</option>
              {parties.map(party => (
                <option key={party.id} value={party.id}>
                  {party.party_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quality *
            </label>
            <select
              name="quality_id"
              value={formData.quality_id}
              onChange={handleInputChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Quality</option>
              {qualities.map(quality => (
                <option key={quality.id} value={quality.id}>
                  {quality.quality_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lot Date
            </label>
            <input
              type="date"
              name="lot_date"
              value={formData.lot_date}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bill Number
            </label>
            <input
              type="text"
              name="bill_number"
              value={formData.bill_number}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter bill number"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Actual Pieces
            </label>
            <input
              type="number"
              name="actual_pieces"
              value={formData.actual_pieces || ''}
              onChange={handleInputChange}
              min="0"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter actual pieces produced"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Delivery Date
            </label>
            <input
              type="date"
              name="delivery_date"
              value={formData.delivery_date}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notes
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleInputChange}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter any additional notes"
          />
        </div>

        {/* Allocation Selection */}
        {formData.party_id && formData.quality_id && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Select Items to Allocate
            </h3>
            
            {filteredAllocations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No available items found for the selected party and quality.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Order
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Design
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ground Color
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Beam Color
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Available
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Allocate
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredAllocations.map((item) => {
                      const itemKey = getItemKey(item);
                      return (
                        <tr key={itemKey}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.order_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.design_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.ground_color_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.beam_color_code} - {item.beam_color_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.remaining_pieces}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <input
                              type="number"
                              min="0"
                              max={item.remaining_pieces}
                              value={selectedAllocations[itemKey] || ''}
                              onChange={(e) => handleAllocationChange(itemKey, parseInt(e.target.value) || 0)}
                              className="w-20 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="0"
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !formData.party_id || !formData.quality_id}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                Creating...
              </>
            ) : (
              'Create Lot'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LotForm;
