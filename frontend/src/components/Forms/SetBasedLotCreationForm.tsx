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
    <div className="card overflow-hidden" style={{ maxWidth: 'none', width: '100%' }}>
      <div className="card-header" style={{ 
        background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%)',
        margin: 0,
        padding: '1.5rem',
        borderBottom: '1px solid var(--color-border)'
      }}>
        <div className="flex items-center justify-between">
          <h2 className="card-title" style={{ color: 'white', margin: 0, fontSize: '1.25rem' }}>
            Create Lot (Set-Based Allocation)
          </h2>
          {onCancel && (
            <button
              onClick={onCancel}
              className="btn btn-secondary"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: 'white',
                padding: '0.5rem',
                borderRadius: 'var(--border-radius)'
              }}
            >
              <X size={20} />
            </button>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6" style={{ padding: '1.5rem' }}>
        {/* Error Message */}
        {error && (
          <div style={{
            backgroundColor: 'var(--color-error)',
            color: 'white',
            border: '1px solid var(--color-error)',
            borderRadius: 'var(--border-radius)',
            padding: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div className="flex items-center space-x-2">
              <AlertCircle size={20} />
              <span className="font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Step 1: Select Party and Quality */}
        <div className="grid grid-cols-2 gap-4" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">
              Party <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <select
              value={selectedPartyId || ''}
              onChange={(e) => setSelectedPartyId(Number(e.target.value))}
              className="form-select"
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

          <div className="form-group">
            <label className="form-label">
              Quality <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <select
              value={selectedQualityId || ''}
              onChange={(e) => setSelectedQualityId(Number(e.target.value))}
              className="form-select"
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
        <div className="grid grid-cols-2 gap-4" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">
              Lot Date <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <input
              type="date"
              value={lotDate}
              onChange={(e) => setLotDate(e.target.value)}
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Lot Number <span style={{ color: 'var(--color-error)' }}>*</span>
            </label>
            <input
              type="text"
              value={lotNumber}
              onChange={(e) => setLotNumber(e.target.value)}
              placeholder="e.g., LOT-001"
              className="form-input"
              required
            />
          </div>
        </div>

        {/* Optional Fields */}
        <div className="grid grid-cols-3 gap-4" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label">
              Bill Number <span style={{ color: 'var(--color-text-muted)' }}>(Optional)</span>
            </label>
            <input
              type="text"
              value={billNumber}
              onChange={(e) => setBillNumber(e.target.value)}
              placeholder="Bill #"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Actual Pieces <span style={{ color: 'var(--color-text-muted)' }}>(Optional)</span>
            </label>
            <input
              type="number"
              value={actualPieces}
              onChange={(e) => setActualPieces(e.target.value ? parseInt(e.target.value) : '')}
              placeholder="Actual pieces"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Delivery Date <span style={{ color: 'var(--color-text-muted)' }}>(Optional)</span>
            </label>
            <input
              type="date"
              value={deliveryDate}
              onChange={(e) => setDeliveryDate(e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        {/* Step 2: Available Designs */}
        {selectedPartyId && selectedQualityId && (
          <div style={{ marginBottom: '1.5rem' }}>
            <label className="form-label" style={{ marginBottom: '1rem' }}>
              Available Designs
            </label>
            {availableDesigns.length === 0 ? (
              <div style={{
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--border-radius)',
                padding: '1.5rem',
                textAlign: 'center',
                color: 'var(--color-text-secondary)'
              }}>
                No designs available for allocation
              </div>
            ) : (
              <div style={{
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--border-radius)',
                maxHeight: '16rem',
                overflowY: 'auto',
                backgroundColor: 'var(--color-surface)'
              }}>
                {availableDesigns.map((design) => {
                  const isSelected = selectedDesigns.some(
                    d => d.order_id === design.order_id && d.design_number === design.design_number
                  );

                  return (
                    <div
                      key={`${design.order_id}-${design.design_number}`}
                      style={{
                        padding: '1rem',
                        borderBottom: '1px solid var(--color-border)',
                        backgroundColor: isSelected ? 'var(--color-primary-light)' : 'transparent',
                        transition: 'var(--transition-fast)'
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                              {design.design_number}
                            </span>
                            <span style={{ color: 'var(--color-text-muted)' }}>•</span>
                            <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                              {design.order_number}
                            </span>
                          </div>
                          <div className="flex items-center space-x-4 mt-1" style={{ fontSize: '0.875rem' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>
                              Remaining: <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>
                                {design.remaining_sets} sets
                              </span>
                            </span>
                            <div className="flex items-center space-x-2">
                              {design.beam_pieces.map((beam, idx) => (
                                <span 
                                  key={idx} 
                                  style={{
                                    fontSize: '0.75rem',
                                    backgroundColor: 'var(--color-primary-light)',
                                    color: 'var(--color-primary)',
                                    padding: '0.25rem 0.5rem',
                                    borderRadius: 'var(--border-radius)',
                                    fontWeight: 500
                                  }}
                                >
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
                          className={`btn ${isSelected ? 'btn-danger' : 'btn-primary'}`}
                          style={{ marginLeft: '1rem' }}
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
          <div style={{ marginBottom: '1.5rem' }}>
            <label className="form-label" style={{ marginBottom: '1rem' }}>
              Allocate Sets to Lot ({selectedDesigns.length} designs, {totalSetsAllocating} total sets)
            </label>
            <div style={{
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--border-radius)',
              backgroundColor: 'var(--color-surface)'
            }}>
              {selectedDesigns.map((design) => {
                const fullDesign = availableDesigns.find(
                  d => d.order_id === design.order_id && d.design_number === design.design_number
                );

                return (
                  <div 
                    key={`${design.order_id}-${design.design_number}`} 
                    style={{
                      padding: '1rem',
                      borderBottom: '1px solid var(--color-border)'
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                          {design.design_number}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                          Max: {design.max_sets} sets
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <label style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                            Sets:
                          </label>
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
                            className="form-input"
                            style={{ width: '6rem' }}
                            required
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveDesign(design.order_id, design.design_number)}
                          style={{ 
                            color: 'var(--color-error)',
                            padding: '0.5rem',
                            borderRadius: 'var(--border-radius)',
                            transition: 'var(--transition-fast)'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = 'var(--color-error)';
                            e.currentTarget.style.color = 'white';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = 'transparent';
                            e.currentTarget.style.color = 'var(--color-error)';
                          }}
                        >
                          <X size={20} />
                        </button>
                      </div>
                    </div>
                    {fullDesign && (
                      <div className="mt-2 flex items-center space-x-2">
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                          Beam allocation:
                        </span>
                        {fullDesign.beam_pieces.map((beam, idx) => {
                          const calculatedPieces = design.allocated_sets * beam.beam_multiplier;
                          return (
                            <span 
                              key={idx} 
                              style={{
                                fontSize: '0.75rem',
                                backgroundColor: 'var(--color-surface-hover)',
                                color: 'var(--color-text-secondary)',
                                padding: '0.25rem 0.5rem',
                                borderRadius: 'var(--border-radius)',
                                fontWeight: 500
                              }}
                            >
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
        <div 
          className="flex items-center justify-end space-x-4"
          style={{
            paddingTop: '1.5rem',
            borderTop: '1px solid var(--color-border)',
            marginTop: '1.5rem'
          }}
        >
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={loading || selectedDesigns.length === 0}
            className="btn btn-primary flex items-center space-x-2"
            style={{
              opacity: (loading || selectedDesigns.length === 0) ? 0.5 : 1,
              cursor: (loading || selectedDesigns.length === 0) ? 'not-allowed' : 'pointer'
            }}
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
