import React, { useState } from 'react';
import LotRegisterTable from '../components/Tables/LotRegisterTable';

interface LotRegisterProps {
  onLotUpdated?: () => void;
}

const LotRegister: React.FC<LotRegisterProps> = ({ onLotUpdated }) => {
  const [activeTab, setActiveTab] = useState<'All' | 'High Speed' | 'Slow Speed' | 'K1K2'>('All');

  const tabs = [
    { 
      id: 'All', 
      label: 'All Lots', 
      color: 'bg-gray-500',
      description: 'All lots across all production lines'
    },
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
    <div>
      <div className="page-header">
        <div className="container">
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
        <div style={{ marginTop: '1.5rem' }}>
          <div style={{ 
            backgroundColor: 'var(--color-surface)', 
            borderRadius: 'var(--border-radius)',
            border: '1px solid var(--color-border)',
            overflow: 'hidden'
          }}>
            <div style={{ borderBottom: '1px solid var(--color-border)' }}>
              <nav style={{ display: 'flex', gap: '0.25rem', padding: '0.5rem' }} aria-label="Tabs">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      padding: '0.625rem 1rem',
                      fontSize: '0.875rem',
                      fontWeight: activeTab === tab.id ? 600 : 500,
                      color: activeTab === tab.id ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                      backgroundColor: activeTab === tab.id ? 'var(--color-surface)' : 'transparent',
                      border: 'none',
                      borderRadius: 'var(--border-radius)',
                      cursor: 'pointer',
                      transition: 'var(--transition-fast)',
                      borderBottom: activeTab === tab.id ? '2px solid var(--color-primary)' : '2px solid transparent'
                    }}
                    title={tab.description}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>
            
            {/* Tab Content */}
            <div style={{ padding: '1.5rem' }}>
              <div style={{ marginBottom: '1.5rem' }}>
                <h2 style={{ 
                  fontSize: '1rem', 
                  fontWeight: 600, 
                  color: 'var(--color-text-primary)',
                  marginBottom: '0.25rem'
                }}>
                  {activeTab === 'All' ? 'All Lots' : `${activeTab} Lot Register`}
                </h2>
                <p style={{ 
                  fontSize: '0.875rem', 
                  color: 'var(--color-text-secondary)'
                }}>
                  {activeTab === 'All' 
                    ? 'All orders and lots across all production lines' 
                    : `Orders and lots for ${activeTab} production line`}
                </p>
              </div>
              
              <LotRegisterTable 
                key={activeTab}
                onLotUpdated={onLotUpdated} 
                lotRegisterType={activeTab === 'All' ? undefined : activeTab}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LotRegister;
