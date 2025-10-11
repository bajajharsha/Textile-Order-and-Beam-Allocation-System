import React, { useEffect, useState } from 'react';
import { lotApi, PartywiseDetailResponse } from '../../services/api';

interface PartywiseDetailTableProps {
  refreshTrigger?: number;
}

const PartywiseDetailTable: React.FC<PartywiseDetailTableProps> = ({ refreshTrigger = 0 }) => {
  const [data, setData] = useState<PartywiseDetailResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedParties, setExpandedParties] = useState<Set<string>>(new Set());
  const [filterText, setFilterText] = useState<string>('');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await lotApi.getPartywiseDetail();
      const parties = response.data.parties || [];
      setData(parties);
      
      // Auto-expand all parties initially
      setExpandedParties(new Set(parties.map(party => party.party_name)));
    } catch (err) {
      console.error('Error fetching partywise detail:', err);
      setError('Failed to fetch partywise detail data');
    } finally {
      setLoading(false);
    }
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

  // Filter and sort data - show recent entries on top
  const filteredData = data
    .filter(party => 
      party.party_name.toLowerCase().includes(filterText.toLowerCase())
    )
    .map(party => ({
      ...party,
      items: party.items.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    }))
    .sort((a, b) => {
      // Sort parties by their most recent item date
      const aLatestDate = Math.max(...a.items.map(item => new Date(item.date).getTime()));
      const bLatestDate = Math.max(...b.items.map(item => new Date(item.date).getTime()));
      return bLatestDate - aLatestDate;
    });

  useEffect(() => {
    fetchData();
  }, [refreshTrigger]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="table-container">
        <div className="table-loading">
          <div className="loading-spinner"></div>
          <p>Loading partywise detail data...</p>
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

  if (data.length === 0) {
    return (
      <div className="table-container">
        <div className="table-empty">
          <p>No partywise detail data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-container">
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 1.5rem',
        borderBottom: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)'
      }}>
        <h3 style={{
          fontSize: '1.125rem',
          fontWeight: 600,
          color: 'var(--color-text-primary)',
          margin: 0
        }}>
          Partywise Detail Report
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Filter by party name..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              style={{
                padding: '0.5rem 1rem',
                paddingLeft: '2.5rem',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--border-radius)',
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text-primary)',
                fontSize: '0.875rem',
                width: '250px',
                outline: 'none'
              }}
            />
            <span style={{
              position: 'absolute',
              left: '0.75rem',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--color-text-secondary)',
              fontSize: '0.875rem'
            }}>
              🔍
            </span>
          </div>
          <button onClick={fetchData} className="btn btn-secondary">
            Refresh
          </button>
        </div>
      </div>

      {/* Grouped Data by Party */}
      {filteredData.length === 0 ? (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--color-text-secondary)',
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--border-radius)'
        }}>
          <p style={{ margin: 0, fontSize: '0.875rem' }}>
            {filterText ? `No parties found matching "${filterText}"` : 'No party data available'}
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {filteredData.map((party) => (
          <div key={party.party_name} style={{ 
            border: '1px solid var(--color-border)', 
            borderRadius: 'var(--border-radius)', 
            overflow: 'hidden',
          backgroundColor: 'var(--color-surface)'
          }}>
            {/* Party Header */}
            <div 
              style={{
                backgroundColor: 'var(--color-surface-hover)',
                padding: '1rem',
                cursor: 'pointer',
                transition: 'var(--transition-fast)',
                borderBottom: expandedParties.has(party.party_name) ? '1px solid var(--color-border)' : 'none'
              }}
              onClick={() => togglePartyExpansion(party.party_name)}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--color-border)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--color-surface-hover)'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', fontWeight: 600 }}>
                  {expandedParties.has(party.party_name) ? '▼' : '▶'} {party.party_name}
                </span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                  ({party.items.length} orders)
                </span>
              </div>
                    </div>
                
                {/* Party Items */}
            {expandedParties.has(party.party_name) && (
              <div style={{ overflowX: 'auto', marginTop: '0.5rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'var(--color-surface-hover)' }}>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Date</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Des No.</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Quality</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Sets (pcs)</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Rate</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Lot No.</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Lot No. Date</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bill No.</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Actual Pcs</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Delivery Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {party.items.map((item, index) => (
                      <tr key={`${party.party_name}-${index}`} style={{ borderBottom: '1px solid var(--color-border)' }}>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{formatDate(item.date)}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.des_no}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.quality}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.sets_pcs}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{formatCurrency(item.rate)}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.lot_no || '-'}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.lot_no_date ? formatDate(item.lot_no_date) : '-'}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.bill_no || '-'}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.actual_pcs || '-'}</td>
                        <td style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{item.delivery_date ? formatDate(item.delivery_date) : '-'}</td>
                  </tr>
            ))}
          </tbody>
        </table>
      </div>
            )}
          </div>
        ))}
        </div>
      )}

       {/* Summary Section */}
       <div className="table-summary">
         <div className="summary-stats">
           <div className="stat-item">
             <span className="stat-label">Total Parties:</span>
             <span className="stat-value">{filteredData.length}</span>
           </div>
           <div className="stat-item">
             <span className="stat-label">Total Orders:</span>
             <span className="stat-value">
               {filteredData.reduce((sum, party) => sum + party.items.length, 0)}
             </span>
           </div>
         </div>
       </div>
    </div>
  );
};

export default PartywiseDetailTable;
