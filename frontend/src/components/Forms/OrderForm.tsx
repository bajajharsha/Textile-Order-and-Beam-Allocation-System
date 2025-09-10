import { Calculator, Plus, ShoppingCart, Trash2, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import {
  BeamColorSummary,
  DropdownData,
  GroundColorItem,
  masterApi,
  orderApi,
  OrderCreate
} from '../../services/api';

interface OrderFormProps {
  onOrderCreated?: (order: any) => void;
  onBeamCalculated?: (beamSummary: BeamColorSummary[]) => void;
  editOrder?: any;
  onCancel?: () => void;
}

const OrderForm: React.FC<OrderFormProps> = ({ onOrderCreated, onBeamCalculated, editOrder, onCancel }) => {
  const [dropdownData, setDropdownData] = useState<DropdownData | null>(null);
  const [loading, setLoading] = useState(false);
  const [calculatingBeam, setCalculatingBeam] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState({
    party_id: '',
    quality_id: '',
    cuts: [] as string[],
    design_numbers: [''],
    rate_per_piece: '',
    notes: ''
  });

  const [groundColors, setGroundColors] = useState<GroundColorItem[]>([
    { ground_color_id: 0, beam_color_id: 0, pieces_per_color: 0 }
  ]);

  const [beamPreview, setBeamPreview] = useState<BeamColorSummary[]>([]);

  // Load dropdown data on component mount
  useEffect(() => {
    loadDropdownData();
  }, []);

   const loadDropdownData = async () => {
     try {
       const response = await masterApi.getDropdownData();
       setDropdownData(response.data);
     } catch (error) {
       console.error('Error loading dropdown data:', error);
       // Set empty data structure to prevent map errors
       setDropdownData({
         parties: [],
         colors: [],
         qualities: [],
         cuts: []
       });
       alert('Failed to load dropdown data. Please make sure the backend server is running.');
     }
   };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleCutChange = (cutValue: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      cuts: checked 
        ? [...prev.cuts, cutValue]
        : prev.cuts.filter(c => c !== cutValue)
    }));
  };

  const handleDesignNumberChange = (index: number, value: string) => {
    const newDesignNumbers = [...formData.design_numbers];
    newDesignNumbers[index] = value;
    setFormData(prev => ({ ...prev, design_numbers: newDesignNumbers }));
  };

  const addDesignNumber = () => {
    setFormData(prev => ({
      ...prev,
      design_numbers: [...prev.design_numbers, '']
    }));
  };

  const removeDesignNumber = (index: number) => {
    if (formData.design_numbers.length > 1) {
      const newDesignNumbers = formData.design_numbers.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, design_numbers: newDesignNumbers }));
    }
  };

  const handleGroundColorChange = (index: number, field: keyof GroundColorItem, value: number) => {
    const newGroundColors = [...groundColors];
    newGroundColors[index] = { ...newGroundColors[index], [field]: value };
    setGroundColors(newGroundColors);
  };

  const addGroundColor = () => {
    setGroundColors(prev => [
      ...prev,
      { ground_color_id: 0, beam_color_id: 0, pieces_per_color: 0 }
    ]);
  };

  const removeGroundColor = (index: number) => {
    if (groundColors.length > 1) {
      setGroundColors(prev => prev.filter((_, i) => i !== index));
    }
  };

  const calculateBeamPreview = async () => {
    if (!formData.design_numbers.some(d => d.trim()) || !groundColors.some(g => g.pieces_per_color > 0)) {
      alert('Please enter design numbers and ground color details');
      return;
    }

    setCalculatingBeam(true);
    try {
      const validGroundColors = groundColors.filter(g => g.ground_color_id > 0 && g.beam_color_id > 0);
      const validDesignNumbers = formData.design_numbers.filter(d => d.trim());
      
      if (validGroundColors.length === 0) {
        alert('Please select valid ground colors and beam colors');
        return;
      }

      const response = await orderApi.calculateBeamPreview({
        ground_colors: validGroundColors,
        design_numbers: validDesignNumbers
      });

      setBeamPreview(response.data.beam_summary);
      if (onBeamCalculated) {
        onBeamCalculated(response.data.beam_summary);
      }
    } catch (error) {
      console.error('Error calculating beam preview:', error);
      alert('Failed to calculate beam preview');
    } finally {
      setCalculatingBeam(false);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.party_id) newErrors.party_id = 'Please select a party';
    if (!formData.quality_id) newErrors.quality_id = 'Please select a quality';
    if (formData.cuts.length === 0) newErrors.cuts = 'Please select at least one cut';
    if (!formData.design_numbers.some(d => d.trim())) newErrors.design_numbers = 'Please enter at least one design number';
    if (!formData.rate_per_piece || parseFloat(formData.rate_per_piece) <= 0) {
      newErrors.rate_per_piece = 'Please enter a valid rate per piece';
    }
    if (!groundColors.some(g => g.ground_color_id > 0 && g.beam_color_id > 0 && g.pieces_per_color > 0)) {
      newErrors.ground_colors = 'Please add at least one valid ground color entry';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      const validGroundColors = groundColors.filter(g => g.ground_color_id > 0 && g.beam_color_id > 0);
      const validDesignNumbers = formData.design_numbers.filter(d => d.trim());

      const orderData: OrderCreate = {
        party_id: parseInt(formData.party_id),
        quality_id: parseInt(formData.quality_id),
        cuts: formData.cuts,
        design_numbers: validDesignNumbers,
        ground_colors: validGroundColors,
        rate_per_piece: parseFloat(formData.rate_per_piece),
        notes: formData.notes || undefined
      };

      const response = await orderApi.create(orderData);
      console.log('Order created:', response.data);
      
      if (onOrderCreated) {
        onOrderCreated(response.data);
      }
      
      alert('Order created successfully!');
      
      // Reset form
      setFormData({
        party_id: '',
        quality_id: '',
        cuts: [],
        design_numbers: [''],
        rate_per_piece: '',
        notes: ''
      });
      setGroundColors([{ ground_color_id: 0, beam_color_id: 0, pieces_per_color: 0 }]);
      setBeamPreview([]);
      
    } catch (error: any) {
      console.error('Error creating order:', error);
      alert('Failed to create order. Please try again.');
    } finally {
      setLoading(false);
    }
  };

   if (!dropdownData || 
       !dropdownData.parties?.length || 
       !dropdownData.colors?.length || 
       !dropdownData.qualities?.length || 
       !dropdownData.cuts?.length) {
     return (
       <div className="card">
         <div className="flex items-center justify-center py-8">
           <div className="loading"></div>
           <span className="ml-2">Loading form data...</span>
         </div>
       </div>
     );
   }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingCart className="text-primary" size={20} />
            <h2 className="card-title">{editOrder ? 'Edit Order' : 'Create New Order'}</h2>
          </div>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-secondary btn-sm"
              title="Close"
            >
              <X size={16} />
            </button>
          )}
        </div>
        <p className="card-description">
          {editOrder ? 'Update order details and recalculate beam allocation' : 'Enter order details and calculate beam allocation'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Order Info */}
        <div className="grid grid-cols-2 gap-4">
          <div className="form-group">
            <label htmlFor="party_id" className="form-label">
              Party Name *
            </label>
            <select
              id="party_id"
              name="party_id"
              value={formData.party_id}
              onChange={handleInputChange}
              className={`form-select ${errors.party_id ? 'border-error' : ''}`}
              disabled={loading}
            >
               <option value="">Select Party</option>
               {(dropdownData.parties || []).map(party => (
                 <option key={party.id} value={party.id}>
                   {party.name}
                 </option>
               ))}
            </select>
            {errors.party_id && <p className="text-error text-sm mt-1">{errors.party_id}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="quality_id" className="form-label">
              Quality *
            </label>
            <select
              id="quality_id"
              name="quality_id"
              value={formData.quality_id}
              onChange={handleInputChange}
              className={`form-select ${errors.quality_id ? 'border-error' : ''}`}
              disabled={loading}
            >
               <option value="">Select Quality</option>
               {(dropdownData.qualities || []).map(quality => (
                 <option key={quality.id} value={quality.id}>
                   {quality.quality_name} ({quality.feeder_count} feeder)
                 </option>
               ))}
            </select>
            {errors.quality_id && <p className="text-error text-sm mt-1">{errors.quality_id}</p>}
          </div>
        </div>

        {/* Cuts Selection */}
        <div className="form-group">
          <label className="form-label">
            Cuts (Quality) *
          </label>
             <div className="flex flex-wrap gap-3">
             {(dropdownData.cuts || []).map(cut => (
               <label key={cut.id} className="flex items-center gap-2 cursor-pointer">
                 <input
                   type="checkbox"
                   checked={formData.cuts.includes(cut.cut_value)}
                   onChange={(e) => handleCutChange(cut.cut_value, e.target.checked)}
                   className="rounded border-border"
                   disabled={loading}
                 />
                 <span className="text-sm">{cut.cut_value}</span>
               </label>
             ))}
          </div>
          {errors.cuts && <p className="text-error text-sm mt-1">{errors.cuts}</p>}
        </div>

        {/* Design Numbers */}
        <div className="form-group">
          <div className="flex items-center justify-between mb-2">
            <label className="form-label">Design Numbers *</label>
            <button
              type="button"
              onClick={addDesignNumber}
              className="btn btn-secondary btn-sm"
              disabled={loading}
            >
              <Plus size={14} />
              Add Design
            </button>
          </div>
          <div className="space-y-2">
            {formData.design_numbers.map((design, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="text"
                  value={design}
                  onChange={(e) => handleDesignNumberChange(index, e.target.value)}
                  className="form-input"
                  placeholder={`Design number ${index + 1}`}
                  disabled={loading}
                />
                {formData.design_numbers.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeDesignNumber(index)}
                    className="btn btn-secondary btn-sm"
                    disabled={loading}
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            ))}
          </div>
          {errors.design_numbers && <p className="text-error text-sm mt-1">{errors.design_numbers}</p>}
        </div>

        {/* Ground Colors */}
        <div className="form-group">
          <div className="flex items-center justify-between mb-2">
            <label className="form-label">Ground Colors & Beam Colors *</label>
            <button
              type="button"
              onClick={addGroundColor}
              className="btn btn-secondary btn-sm"
              disabled={loading}
            >
              <Plus size={14} />
              Add Color
            </button>
          </div>
          <div className="space-y-3">
            {groundColors.map((groundColor, index) => (
              <div key={index} className="grid grid-cols-4 gap-2 items-end">
                <div>
                  <label className="form-label text-sm">Ground Color</label>
                  <select
                    value={groundColor.ground_color_id}
                    onChange={(e) => handleGroundColorChange(index, 'ground_color_id', parseInt(e.target.value))}
                    className="form-select"
                    disabled={loading}
                  >
                     <option value={0}>Select Ground Color</option>
                     {(dropdownData.colors || []).map(color => (
                       <option key={color.id} value={color.id}>
                         {color.color_name} ({color.color_code})
                       </option>
                     ))}
                  </select>
                </div>
                <div>
                  <label className="form-label text-sm">Beam Color</label>
                  <select
                    value={groundColor.beam_color_id}
                    onChange={(e) => handleGroundColorChange(index, 'beam_color_id', parseInt(e.target.value))}
                    className="form-select"
                    disabled={loading}
                  >
                     <option value={0}>Select Beam Color</option>
                     {(dropdownData.colors || []).map(color => (
                       <option key={color.id} value={color.id}>
                         {color.color_name} ({color.color_code})
                       </option>
                     ))}
                  </select>
                </div>
                <div>
                  <label className="form-label text-sm">Pieces per Color</label>
                  <input
                    type="number"
                    value={groundColor.pieces_per_color}
                    onChange={(e) => handleGroundColorChange(index, 'pieces_per_color', parseInt(e.target.value) || 0)}
                    className="form-input"
                    min="0"
                    disabled={loading}
                  />
                </div>
                <div>
                  {groundColors.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeGroundColor(index)}
                      className="btn btn-secondary btn-sm w-full"
                      disabled={loading}
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          {errors.ground_colors && <p className="text-error text-sm mt-1">{errors.ground_colors}</p>}
        </div>

        {/* Rate */}
        <div className="form-group">
          <label htmlFor="rate_per_piece" className="form-label">
            Rate per Piece *
          </label>
          <input
            type="number"
            id="rate_per_piece"
            name="rate_per_piece"
            value={formData.rate_per_piece}
            onChange={handleInputChange}
            className={`form-input ${errors.rate_per_piece ? 'border-error' : ''}`}
            placeholder="Enter rate per piece"
            min="0"
            step="0.01"
            disabled={loading}
          />
          {errors.rate_per_piece && <p className="text-error text-sm mt-1">{errors.rate_per_piece}</p>}
        </div>

        {/* Notes */}
        <div className="form-group">
          <label htmlFor="notes" className="form-label">
            Notes
          </label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleInputChange}
            className="form-textarea"
            placeholder="Enter any additional notes (optional)"
            rows={3}
            disabled={loading}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            type="button"
            onClick={calculateBeamPreview}
            className="btn btn-secondary"
            disabled={loading || calculatingBeam}
          >
            {calculatingBeam ? (
              <>
                <div className="loading"></div>
                Calculating...
              </>
            ) : (
              <>
                <Calculator size={16} />
                Preview Beam Allocation
              </>
            )}
          </button>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="loading"></div>
                Creating Order...
              </>
            ) : (
              <>
                <ShoppingCart size={16} />
                Create Order
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OrderForm;
