import React, { useState } from 'react';
import LotRegisterTable from '../components/Tables/LotRegisterTable';

interface LotRegisterProps {
  onLotUpdated?: () => void;
}

const LotRegister: React.FC<LotRegisterProps> = ({ onLotUpdated }) => {
  const [activeTab, setActiveTab] = useState<'High Speed' | 'Slow Speed' | 'K1K2'>('High Speed');

  const tabs = [
    { 
      id: 'High Speed', 
      label: 'High Speed', 
      color: 'bg-green-500',
      description: 'Fast production line'
    },
    { 
      id: 'Slow Speed', 
      label: 'Slow Speed', 
      color: 'bg-blue-500',
      description: 'Standard production line'
    },
    { 
      id: 'K1K2', 
      label: 'K1K2', 
      color: 'bg-purple-500',
      description: 'Specialized production line'
    }
  ] as const;

  return (
    <div className="space-y-6">
      <div className="container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Lot Register</h1>
            <p className="page-subtitle">
              View and manage lot register with inline editing for bill numbers, actual pieces, and delivery dates
            </p>
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="container">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-1 px-6" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`relative py-4 px-6 font-medium text-sm transition-all duration-200 rounded-t-lg group ${
                    activeTab === tab.id
                      ? 'bg-white text-gray-900 border-b-2 border-blue-500 shadow-sm'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                  title={tab.description}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full transition-colors duration-200 ${
                      activeTab === tab.id 
                        ? tab.color 
                        : 'bg-gray-300 group-hover:bg-gray-400'
                    }`}></div>
                    <span className="font-semibold">{tab.label}</span>
                    {activeTab === tab.id && (
                      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-full"></div>
                    )}
                  </div>
                </button>
              ))}
            </nav>
          </div>
          
          {/* Tab Content */}
          <div className="p-6 bg-gray-50">
            <div className="mb-6">
              <div className="flex items-center space-x-3 mb-2">
                <div className={`w-4 h-4 rounded-full ${
                  activeTab === 'High Speed' ? 'bg-green-500' :
                  activeTab === 'Slow Speed' ? 'bg-blue-500' : 'bg-purple-500'
                }`}></div>
                <h2 className="text-xl font-bold text-gray-900">
                  {activeTab} Lot Register
                </h2>
              </div>
              <p className="text-sm text-gray-600 ml-7">
                Orders and lots for {activeTab} production line
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 transition-all duration-300">
              <LotRegisterTable 
                key={activeTab} // Force re-render when tab changes
                onLotUpdated={onLotUpdated} 
                lotRegisterType={activeTab}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LotRegister;
