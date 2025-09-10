import { X } from 'lucide-react';
import React from 'react';
import { Party } from '../../services/api';
import PartyForm from './PartyForm';

interface PartyFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPartyCreated: (party: Party) => void;
  editParty?: Party;
}

const PartyFormModal: React.FC<PartyFormModalProps> = ({ 
  isOpen, 
  onClose, 
  onPartyCreated,
  editParty 
}) => {
  if (!isOpen) return null;

  const handlePartyCreated = (party: Party) => {
    onPartyCreated(party);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-background rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-semibold">
            {editParty ? 'Edit Party' : 'Add New Party'}
          </h2>
          <button
            onClick={onClose}
            className="btn btn-secondary btn-sm"
            title="Close"
          >
            <X size={16} />
          </button>
        </div>
        
        <div className="p-6">
          <PartyForm 
            onPartyCreated={handlePartyCreated}
            editParty={editParty}
          />
        </div>
      </div>
    </div>
  );
};

export default PartyFormModal;
