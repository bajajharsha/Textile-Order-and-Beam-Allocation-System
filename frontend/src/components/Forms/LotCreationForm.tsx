import React, { useState } from 'react';
import { lotApi } from '../../services/api';

interface LotCreationFormProps {
  orderId: number;
  orderNumber: string;
  partyName: string;
  qualityName: string;
  designs: Array<{
    design_number: string;
    remaining_pieces: number;
    original_pieces: number;
  }>;
  onLotCreated: () => void;
  onCancel: () => void;
}

const LotCreationForm: React.FC<LotCreationFormProps> = ({
  orderId,
  orderNumber,
  partyName,
  qualityName,
  designs,
  onLotCreated,
  onCancel
}) => {
  const [formData, setFormData] = useState({
    lot_number: '',
    lot_date: new Date().toISOString().split('T')[0], // Today's date
    selected_design: '',
    pieces_to_allocate: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.lot_number.trim()) {
      newErrors.lot_number = 'Lot number is required';
    }
    if (!formData.selected_design) {
      newErrors.selected_design = 'Please select a design';
    }
    if (!formData.pieces_to_allocate || parseInt(formData.pieces_to_allocate) <= 0) {
      newErrors.pieces_to_allocate = 'Please enter a valid number of pieces';
    } else {
      const selectedDesign = designs.find(d => d.design_number === formData.selected_design);
      if (selectedDesign && parseInt(formData.pieces_to_allocate) > selectedDesign.remaining_pieces) {
        newErrors.pieces_to_allocate = `Cannot allocate more than ${selectedDesign.remaining_pieces} remaining pieces`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const lotData = {
        order_id: orderId,
        lot_number: formData.lot_number,
        lot_date: formData.lot_date,
        design_number: formData.selected_design,
        pieces_allocated: parseInt(formData.pieces_to_allocate)
      };

      await lotApi.createLotFromDesign(lotData);
      
      alert('Lot created successfully!');
      onLotCreated();
      
      // Reset form
      setFormData({
        lot_number: '',
        lot_date: new Date().toISOString().split('T')[0],
        selected_design: '',
        pieces_to_allocate: ''
      });
      
    } catch (error: any) {
      console.error('Error creating lot:', error);
      alert('Failed to create lot. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const selectedDesign = designs.find(d => d.design_number === formData.selected_design);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Create New Lot
            </h2>
            <p className="text-sm text-gray-600">
              Order: {orderNumber} | Party: {partyName} | Quality: {qualityName}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Lot Number */}
            <div className="form-group">
              <label htmlFor="lot_number" className="form-label">
                Lot Number *
              </label>
              <input
                type="text"
                id="lot_number"
                name="lot_number"
                value={formData.lot_number}
                onChange={handleInputChange}
                className={`form-input ${errors.lot_number ? 'border-error' : ''}`}
                placeholder="Enter lot number"
                disabled={loading}
              />
              {errors.lot_number && (
                <p className="text-error text-sm mt-1">{errors.lot_number}</p>
              )}
            </div>

            {/* Lot Date */}
            <div className="form-group">
              <label htmlFor="lot_date" className="form-label">
                Lot Date *
              </label>
              <input
                type="date"
                id="lot_date"
                name="lot_date"
                value={formData.lot_date}
                onChange={handleInputChange}
                className="form-input"
                disabled={loading}
              />
            </div>

            {/* Design Selection */}
            <div className="form-group">
              <label htmlFor="selected_design" className="form-label">
                Select Design *
              </label>
              <select
                id="selected_design"
                name="selected_design"
                value={formData.selected_design}
                onChange={handleInputChange}
                className={`form-select ${errors.selected_design ? 'border-error' : ''}`}
                disabled={loading}
              >
                <option value="">Select a design</option>
                 {designs.map(design => (
                   <option key={design.design_number} value={design.design_number}>
                     {design.design_number} (Remaining: {design.remaining_pieces} pieces)
                   </option>
                 ))}
              </select>
              {errors.selected_design && (
                <p className="text-error text-sm mt-1">{errors.selected_design}</p>
              )}
            </div>

                   {/* Pieces to Allocate */}
                   <div className="form-group">
                     <label htmlFor="pieces_to_allocate" className="form-label">
                       Pieces to Allocate *
                     </label>
                     <input
                       type="number"
                       id="pieces_to_allocate"
                       name="pieces_to_allocate"
                       value={formData.pieces_to_allocate}
                       onChange={handleInputChange}
                       className={`form-input ${errors.pieces_to_allocate ? 'border-error' : ''}`}
                       placeholder="Enter number of pieces"
                       min="1"
                       max={selectedDesign?.remaining_pieces || undefined}
                       disabled={loading}
                     />
                     {selectedDesign && (
                       <p className="text-sm text-gray-600 mt-1">
                         Available: {selectedDesign.remaining_pieces} pieces
                       </p>
                     )}
                     {errors.pieces_to_allocate && (
                       <p className="text-error text-sm mt-1">{errors.pieces_to_allocate}</p>
                     )}
                   </div>

            {/* Design Info */}
            {selectedDesign && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Design Information</h4>
                 <div className="text-sm text-gray-600 space-y-1">
                   <p>Design: {selectedDesign.design_number}</p>
                   <p>Original Pieces: {selectedDesign.original_pieces}</p>
                   <p>Remaining Pieces: {selectedDesign.remaining_pieces}</p>
                   <p>Pieces to Allocate: {formData.pieces_to_allocate || 0}</p>
                 </div>
              </div>
            )}

            {/* Form Actions */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Create Lot'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LotCreationForm;
