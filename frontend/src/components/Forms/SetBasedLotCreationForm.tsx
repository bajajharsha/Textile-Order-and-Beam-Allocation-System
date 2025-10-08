import { AlertCircle, CheckCircle, Plus, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface BeamPiece {
  beam_color_code: string;
  beam_color_name: string;
  beam_multiplier: number;
  pieces: number;
}

interface DesignAllocation {
  order_id: number;
  order_number: string;
  party_name: string;
  quality_name: string;
  design_number: string;
  total_sets: number;
  allocated_sets: number;
  remaining_sets: number;
  beam_pieces: BeamPiece[];
}

interface DesignAllocationInput {
  order_id: number;
  design_number: string;
  allocated_sets: number;
  max_sets: number;
}

interface SetBasedLotCreationFormProps {
  onLotCreated?: () => void;
  onCancel?: () => void;
}

const SetBasedLotCreationForm: React.FC<SetBasedLotCreationFormProps> = ({
  onLotCreated,
  onCancel,
}) => {
  const [parties, setParties] = useState<any[]>([]);
  const [qualities, setQualities] = useState<any[]>([]);
  const [availableDesigns, setAvailableDesigns] = useState<DesignAllocation[]>([]);
  
  const [selectedPartyId, setSelectedPartyId] = useState<number | null>(null);
  const [selectedQualityId, setSelectedQualityId] = useState<number | null>(null);
  const [lotDate, setLotDate] = useState(new Date().toISOString().split('T')[0]);
  const [lotNumber, setLotNumber] = useState('');
  const [billNumber, setBillNumber] = useState('');
  const [actualPieces, setActualPieces] = useState<number | ''>('');
  const [deliveryDate, setDeliveryDate] = useState('');
  
  const [selectedDesigns, setSelectedDesigns] = useState<DesignAllocationInput[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchMasterData();
  }, []);

  useEffect(() => {
    if (selectedPartyId && selectedQualityId) {
      fetchAvailableDesigns();
    } else {
      setAvailableDesigns([]);
      setSelectedDesigns([]);
    }
  }, [selectedPartyId, selectedQualityId]);

  const fetchMasterData = async () => {
    try {
      const [partiesRes, qualitiesRes] = await Promise.all([
        fetch('http://localhost:8001/api/v1/parties'),
        fetch('http://localhost:8001/api/v1/master/qualities'),
      ]);

      const partiesData = await partiesRes.json();
      const qualitiesData = await qualitiesRes.json();

      // Handle both array and paginated responses
      setParties(Array.isArray(partiesData) ? partiesData : partiesData.parties || []);
      setQualities(Array.isArray(qualitiesData) ? qualitiesData : qualitiesData.qualities || []);
    } catch (err) {
      console.error('Error fetching master data:', err);
      setError('Failed to load form data');
    }
  };

  const fetchAvailableDesigns = async () => {
    try {
      const response = await fetch(
        `http://localhost:8001/api/v1/designs/allocation/design-wise?party_id=${selectedPartyId}`
      );
      
      if (!response.ok) throw new Error('Failed to fetch designs');

      const data = await response.json();
      
      console.log('🔍 Available Designs API Response:', data);
      console.log('🔍 Selected Quality:', qualities.find(q => q.id === selectedQualityId));
      
      // Filter designs that have remaining sets and match selected quality
      const filtered = data.designs.filter(
        (d: DesignAllocation) => {
          const matchesRemaining = d.remaining_sets > 0;
          const selectedQuality = qualities.find(q => q.id === selectedQualityId);
          const matchesQuality = d.quality_name === selectedQuality?.quality_name;
          
          console.log(`Design ${d.design_number}: remaining=${d.remaining_sets}, quality=${d.quality_name}, match=${matchesQuality}`);
          
          return matchesRemaining && matchesQuality;
        }
      );
      
      console.log('🔍 Filtered Designs:', filtered);
      setAvailableDesigns(filtered);
    } catch (err) {
      console.error('Error fetching available designs:', err);
      setError('Failed to load available designs');
    }
  };

  const handleAddDesign = (design: DesignAllocation) => {
    if (selectedDesigns.some(d => d.order_id === design.order_id && d.design_number === design.design_number)) {
      return; // Already added
    }

    setSelectedDesigns([
      ...selectedDesigns,
      {
        order_id: design.order_id,
        design_number: design.design_number,
        allocated_sets: Math.min(10, design.remaining_sets), // Default to 10 or remaining
        max_sets: design.remaining_sets,
      },
    ]);
  };

  const handleRemoveDesign = (orderId: number, designNumber: string) => {
    setSelectedDesigns(selectedDesigns.filter(
      d => !(d.order_id === orderId && d.design_number === designNumber)
    ));
  };

  const handleSetChange = (orderId: number, designNumber: string, value: number) => {
    setSelectedDesigns(selectedDesigns.map(d => {
      if (d.order_id === orderId && d.design_number === designNumber) {
        return { ...d, allocated_sets: Math.min(value, d.max_sets) };
      }
      return d;
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedPartyId || !selectedQualityId) {
      setError('Please select party and quality');
      return;
    }

    if (!lotNumber.trim()) {
      setError('Please enter lot number');
      return;
    }

    if (selectedDesigns.length === 0) {
      setError('Please select at least one design');
      return;
    }

    // Validate all allocations
    for (const design of selectedDesigns) {
      if (design.allocated_sets <= 0) {
        setError(`Design ${design.design_number} must have at least 1 set allocated`);
        return;
      }
      if (design.allocated_sets > design.max_sets) {
        setError(`Design ${design.design_number} exceeds available sets`);
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8001/api/v1/lots/create-from-sets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          party_id: selectedPartyId,
          quality_id: selectedQualityId,
          lot_date: lotDate,
          lot_number: lotNumber,
          bill_number: billNumber || null,
          actual_pieces: actualPieces || null,
          delivery_date: deliveryDate || null,
          design_allocations: selectedDesigns.map(d => ({
            order_id: d.order_id,
            design_number: d.design_number,
            allocated_sets: d.allocated_sets,
          })),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create lot');
      }

      const result = await response.json();
      console.log('Lot created:', result);

      setSuccess(true);
      setTimeout(() => {
        onLotCreated?.();
      }, 1500);
    } catch (err) {
      console.error('Error creating lot:', err);
      setError(err instanceof Error ? err.message : 'Failed to create lot');
    } finally {
      setLoading(false);
    }
  };

  const totalSetsAllocating = selectedDesigns.reduce((sum, d) => sum + d.allocated_sets, 0);

  if (success) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <CheckCircle className="mx-auto text-green-600 mb-4" size={64} />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Lot Created Successfully!</h3>
          <p className="text-gray-600">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Create Lot (Set-Based Allocation)</h2>
          {onCancel && (
            <button
              onClick={onCancel}
              className="text-white hover:bg-blue-800 rounded-lg p-2 transition-colors"
            >
              <X size={20} />
            </button>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle size={20} />
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Step 1: Select Party and Quality */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Party <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedPartyId || ''}
              onChange={(e) => setSelectedPartyId(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Select Party</option>
              {parties.map((party) => (
                <option key={party.id} value={party.id}>
                  {party.party_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quality <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedQualityId || ''}
              onChange={(e) => setSelectedQualityId(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Select Quality</option>
              {qualities.map((quality) => (
                <option key={quality.id} value={quality.id}>
                  {quality.quality_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Lot Date and Lot Number */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lot Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={lotDate}
              onChange={(e) => setLotDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lot Number <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={lotNumber}
              onChange={(e) => setLotNumber(e.target.value)}
              placeholder="e.g., LOT-001"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
        </div>

        {/* Optional Fields */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bill Number <span className="text-gray-400">(Optional)</span>
            </label>
            <input
              type="text"
              value={billNumber}
              onChange={(e) => setBillNumber(e.target.value)}
              placeholder="Bill #"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Actual Pieces <span className="text-gray-400">(Optional)</span>
            </label>
            <input
              type="number"
              value={actualPieces}
              onChange={(e) => setActualPieces(e.target.value ? parseInt(e.target.value) : '')}
              placeholder="Actual pieces"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Delivery Date <span className="text-gray-400">(Optional)</span>
            </label>
            <input
              type="date"
              value={deliveryDate}
              onChange={(e) => setDeliveryDate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Step 2: Available Designs */}
        {selectedPartyId && selectedQualityId && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Available Designs
            </label>
            {availableDesigns.length === 0 ? (
              <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-600">
                No designs available for allocation
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg divide-y divide-gray-200 max-h-64 overflow-y-auto">
                {availableDesigns.map((design) => {
                  const isSelected = selectedDesigns.some(
                    d => d.order_id === design.order_id && d.design_number === design.design_number
                  );

                  return (
                    <div
                      key={`${design.order_id}-${design.design_number}`}
                      className={`p-4 hover:bg-gray-50 transition-colors ${isSelected ? 'bg-blue-50' : ''}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className="font-medium text-gray-900">{design.design_number}</span>
                            <span className="text-sm text-gray-500">•</span>
                            <span className="text-sm text-gray-600">{design.order_number}</span>
                          </div>
                          <div className="flex items-center space-x-4 mt-1 text-sm">
                            <span className="text-gray-600">
                              Remaining: <span className="font-semibold text-green-600">{design.remaining_sets} sets</span>
                            </span>
                            <div className="flex items-center space-x-2">
                              {design.beam_pieces.map((beam, idx) => (
                                <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                  {beam.beam_color_code}-{beam.beam_multiplier}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => isSelected 
                            ? handleRemoveDesign(design.order_id, design.design_number)
                            : handleAddDesign(design)
                          }
                          className={`ml-4 px-4 py-2 rounded-lg font-medium transition-colors ${
                            isSelected
                              ? 'bg-red-100 text-red-700 hover:bg-red-200'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          {isSelected ? 'Remove' : 'Add'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Selected Designs with Set Allocation */}
        {selectedDesigns.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Allocate Sets to Lot ({selectedDesigns.length} designs, {totalSetsAllocating} total sets)
            </label>
            <div className="border border-gray-200 rounded-lg divide-y divide-gray-200">
              {selectedDesigns.map((design) => {
                const fullDesign = availableDesigns.find(
                  d => d.order_id === design.order_id && d.design_number === design.design_number
                );

                return (
                  <div key={`${design.order_id}-${design.design_number}`} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{design.design_number}</div>
                        <div className="text-sm text-gray-600">Max: {design.max_sets} sets</div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <label className="text-sm font-medium text-gray-700">Sets:</label>
                          <input
                            type="number"
                            min="1"
                            max={design.max_sets}
                            value={design.allocated_sets}
                            onChange={(e) => handleSetChange(
                              design.order_id,
                              design.design_number,
                              parseInt(e.target.value) || 0
                            )}
                            className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            required
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveDesign(design.order_id, design.design_number)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X size={20} />
                        </button>
                      </div>
                    </div>
                    {fullDesign && (
                      <div className="mt-2 flex items-center space-x-2">
                        <span className="text-xs text-gray-500">Beam allocation:</span>
                        {fullDesign.beam_pieces.map((beam, idx) => {
                          const calculatedPieces = design.allocated_sets * beam.beam_multiplier;
                          return (
                            <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                              {beam.beam_color_code}: {calculatedPieces} pcs
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Submit Buttons */}
        <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={loading || selectedDesigns.length === 0}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Creating Lot...</span>
              </>
            ) : (
              <>
                <Plus size={20} />
                <span>Create Lot ({totalSetsAllocating} sets)</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SetBasedLotCreationForm;
