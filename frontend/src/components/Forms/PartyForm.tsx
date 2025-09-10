import { Save, User, X } from 'lucide-react';
import React, { useState } from 'react';
import { Party, partyApi } from '../../services/api';

interface PartyFormProps {
  onPartyCreated?: (party: Party) => void;
  editParty?: Party;
  onCancel?: () => void;
}

const PartyForm: React.FC<PartyFormProps> = ({ onPartyCreated, editParty, onCancel }) => {
  const [formData, setFormData] = useState({
    party_name: editParty?.party_name || '',
    contact_number: editParty?.contact_number || '',
    broker_name: editParty?.broker_name || '',
    gst: editParty?.gst || '',
    address: editParty?.address || ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.party_name.trim()) {
      newErrors.party_name = 'Party name is required';
    }

    if (!formData.contact_number.trim()) {
      newErrors.contact_number = 'Contact number is required';
    } else if (!/^\d{10}$/.test(formData.contact_number)) {
      newErrors.contact_number = 'Contact number must be exactly 10 digits';
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
      let response;
      if (editParty) {
        // Update existing party
        response = await partyApi.update(editParty.id!, formData);
        console.log('Party updated:', response.data);
        alert('Party updated successfully!');
      } else {
        // Create new party
        response = await partyApi.create(formData);
        console.log('Party created:', response.data);
        alert('Party created successfully!');
        
        // Reset form only when creating
        setFormData({
          party_name: '',
          contact_number: '',
          broker_name: '',
          gst: '',
          address: ''
        });
      }
      
      if (onPartyCreated) {
        onPartyCreated(response.data);
      }
      
    } catch (error: any) {
      console.error(`Error ${editParty ? 'updating' : 'creating'} party:`, error);
      alert(`Failed to ${editParty ? 'update' : 'create'} party. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      party_name: '',
      contact_number: '',
      broker_name: '',
      gst: '',
      address: ''
    });
    setErrors({});
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="text-primary" size={20} />
            <h2 className="card-title">{editParty ? 'Edit Party' : 'Add New Party'}</h2>
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
          {editParty ? 'Update party details' : 'Enter party details to add them to your system'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="form-group">
            <label htmlFor="party_name" className="form-label">
              Party Name *
            </label>
            <input
              type="text"
              id="party_name"
              name="party_name"
              value={formData.party_name}
              onChange={handleInputChange}
              className={`form-input ${errors.party_name ? 'border-error' : ''}`}
              placeholder="Enter party name"
              disabled={loading}
            />
            {errors.party_name && (
              <p className="text-error text-sm mt-1">{errors.party_name}</p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="contact_number" className="form-label">
              Contact Number *
            </label>
            <input
              type="tel"
              id="contact_number"
              name="contact_number"
              value={formData.contact_number}
              onChange={handleInputChange}
              className={`form-input ${errors.contact_number ? 'border-error' : ''}`}
              placeholder="10-digit contact number"
              maxLength={10}
              disabled={loading}
            />
            {errors.contact_number && (
              <p className="text-error text-sm mt-1">{errors.contact_number}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="form-group">
            <label htmlFor="broker_name" className="form-label">
              Broker Name
            </label>
            <input
              type="text"
              id="broker_name"
              name="broker_name"
              value={formData.broker_name}
              onChange={handleInputChange}
              className="form-input"
              placeholder="Enter broker name (optional)"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="gst" className="form-label">
              GST Number
            </label>
            <input
              type="text"
              id="gst"
              name="gst"
              value={formData.gst}
              onChange={handleInputChange}
              className="form-input"
              placeholder="Enter GST number (optional)"
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="address" className="form-label">
            Address
          </label>
          <textarea
            id="address"
            name="address"
            value={formData.address}
            onChange={handleInputChange}
            className="form-textarea"
            placeholder="Enter complete address (optional)"
            rows={3}
            disabled={loading}
          />
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={handleReset}
            className="btn btn-secondary"
            disabled={loading}
          >
            Reset
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="loading"></div>
                {editParty ? 'Updating...' : 'Saving...'}
              </>
            ) : (
              <>
                <Save size={16} />
                {editParty ? 'Update Party' : 'Save Party'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PartyForm;
