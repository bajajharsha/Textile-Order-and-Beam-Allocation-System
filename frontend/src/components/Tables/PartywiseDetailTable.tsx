import React, { useEffect, useState } from 'react';
import { lotApi, PartywiseDetailResponse } from '../../services/api';

interface PartywiseDetailTableProps {
  refreshTrigger?: number;
}

const PartywiseDetailTable: React.FC<PartywiseDetailTableProps> = ({ refreshTrigger = 0 }) => {
  const [data, setData] = useState<PartywiseDetailResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await lotApi.getPartywiseDetail();
      setData(response.data.parties || []);
    } catch (err) {
      console.error('Error fetching partywise detail:', err);
      setError('Failed to fetch partywise detail data');
    } finally {
      setLoading(false);
    }
  };

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
        padding: '1.5rem',
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
          <button onClick={fetchData} className="btn btn-secondary">
            Refresh
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          backgroundColor: 'var(--color-surface)'
        }}>
          <thead style={{
            backgroundColor: 'var(--color-surface-hover)',
            borderBottom: '1px solid var(--color-border)'
          }}>
            <tr>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Date</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Des No.</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Quality</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Sets (pcs)</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Rate</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Lot No.</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Lot No. Date</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Bill No.</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Actual Pcs</th>
              <th style={{
                padding: '0.875rem 1rem',
                textAlign: 'left',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>Delivery Date</th>
            </tr>
          </thead>
          <tbody>
            {data.map((party, partyIndex) => (
              <React.Fragment key={partyIndex}>
                {/* Party Header Row */}
                <tr className="party-header-row">
                  <td colSpan={10} className="party-header">
                    <strong>{party.party_name}</strong>
                    <div className="party-summary">
                      <span>Total Remaining: {party.total_remaining_pieces} pcs</span>
                      <span>Total Allocated: {party.total_allocated_pieces} pcs</span>
                      <span>Total Value: {formatCurrency(party.total_value)}</span>
                    </div>
                  </td>
                </tr>
                
                {/* Party Items */}
                {party.items.map((item, itemIndex) => (
                  <tr key={`${partyIndex}-${itemIndex}`} className="data-row">
                    <td>{formatDate(item.date)}</td>
                    <td>{item.des_no}</td>
                    <td>{item.quality}</td>
                    <td>{item.sets_pcs}</td>
                    <td>{formatCurrency(item.rate)}</td>
                    <td>{item.lot_no || '-'}</td>
                    <td>{item.lot_no_date ? formatDate(item.lot_no_date) : '-'}</td>
                    <td>{item.bill_no || '-'}</td>
                    <td>{item.actual_pcs || '-'}</td>
                    <td>{item.delivery_date ? formatDate(item.delivery_date) : '-'}</td>
                  </tr>
                ))}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Section */}
      <div className="table-summary">
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Total Parties:</span>
            <span className="stat-value">{data.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Orders:</span>
            <span className="stat-value">
              {data.reduce((sum, party) => sum + party.items.length, 0)}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Value:</span>
            <span className="stat-value">
              {formatCurrency(data.reduce((sum, party) => sum + party.total_value, 0))}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PartywiseDetailTable;
