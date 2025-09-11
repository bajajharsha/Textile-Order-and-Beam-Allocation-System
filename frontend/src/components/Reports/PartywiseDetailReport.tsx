import React, { useEffect, useState } from 'react';
import { Party, PartywiseDetailResponse, lotApi, partyApi } from '../../services/api';

interface PartywiseDetailReportProps {
  className?: string;
}

const PartywiseDetailReport: React.FC<PartywiseDetailReportProps> = ({ className = '' }) => {
  const [reportData, setReportData] = useState<{
    parties: PartywiseDetailResponse[];
    total_parties: number;
    grand_total_pieces: number;
  } | null>(null);
  const [parties, setParties] = useState<Party[]>([]);
  const [selectedPartyId, setSelectedPartyId] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedParties, setExpandedParties] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadReportData();
  }, [selectedPartyId]);

  const loadInitialData = async () => {
    try {
      const partiesRes = await partyApi.getAll(1, 100);
      setParties(partiesRes.data.parties);
    } catch (error) {
      console.error('Error loading parties:', error);
    }
  };

  const loadReportData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await lotApi.getPartywiseDetail(selectedPartyId);
      setReportData(response.data);
    } catch (error) {
      console.error('Error loading partywise detail:', error);
      setError('Failed to load partywise detail report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const togglePartyExpansion = (partyName: string) => {
    setExpandedParties(prev => {
      const newSet = new Set(prev);
      if (newSet.has(partyName)) {
        newSet.delete(partyName);
      } else {
        newSet.add(partyName);
      }
      return newSet;
    });
  };

  const exportToCSV = () => {
    if (!reportData) return;

    const csvData = [];
    csvData.push([
      'Party Name',
      'Date',
      'Design No.',
      'Quality',
      'Units (pcs)',
      'Rate',
      'Lot No.',
      'Lot Date',
      'Bill No.',
      'Actual pcs',
      'Delivery Date',
      'Ground Color',
      'Beam Color'
    ]);

    reportData.parties.forEach(party => {
      party.items.forEach(item => {
        csvData.push([
          party.party_name,
          item.date,
          item.des_no,
          item.quality,
          item.units_pcs.toString(),
          item.rate.toString(),
          item.lot_no || '',
          item.lot_no_date || '',
          item.bill_no || '',
          item.actual_pcs?.toString() || '',
          item.delivery_date || '',
          item.ground_color_name,
          item.beam_color_name || ''
        ]);
      });
    });

    const csvContent = csvData.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `partywise_detail_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️</div>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={loadReportData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">
              Partywise Detail Report (Red Book)
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Detailed allocation and remaining inventory by party
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedPartyId || ''}
              onChange={(e) => setSelectedPartyId(e.target.value ? parseInt(e.target.value) : undefined)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Parties</option>
              {parties.map(party => (
                <option key={party.id} value={party.id}>
                  {party.party_name}
                </option>
              ))}
            </select>
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              📊 Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {reportData && (
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Total Parties</h4>
              <p className="text-2xl font-semibold text-gray-900">{reportData.total_parties}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Grand Total Pieces</h4>
              <p className="text-2xl font-semibold text-gray-900">{reportData.grand_total_pieces.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Total Value</h4>
              <p className="text-2xl font-semibold text-gray-900">
                {formatCurrency(reportData.parties.reduce((sum, party) => sum + party.total_value, 0))}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Report Content */}
      <div className="p-6">
        {!reportData || reportData.parties.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No data found for the selected criteria.
          </div>
        ) : (
          <div className="space-y-6">
            {reportData.parties.map((party) => (
              <div key={party.party_name} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Party Header */}
                <div 
                  className="bg-gray-50 px-4 py-3 cursor-pointer hover:bg-gray-100"
                  onClick={() => togglePartyExpansion(party.party_name)}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-semibold text-gray-800">
                        {expandedParties.has(party.party_name) ? '▼' : '▶'} {party.party_name}
                      </span>
                      <span className="text-sm text-gray-600">
                        ({party.items.length} items)
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">
                        Remaining: {party.total_remaining_pieces.toLocaleString()} pcs
                      </div>
                      <div className="text-sm font-medium text-gray-800">
                        Value: {formatCurrency(party.total_value)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Party Items */}
                {expandedParties.has(party.party_name) && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Des No.</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Quality</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Units (pcs)</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rate</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Lot No.</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Lot Date</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Bill No.</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actual pcs</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Delivery Date</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {party.items.map((item, index) => (
                          <tr key={index} className={item.lot_no ? 'bg-green-50' : 'bg-yellow-50'}>
                            <td className="px-4 py-2 text-sm text-gray-900">{formatDate(item.date)}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.des_no}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.quality}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.units_pcs.toLocaleString()}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{formatCurrency(item.rate)}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.lot_no || '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">
                              {item.lot_no_date ? formatDate(item.lot_no_date) : '-'}
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.bill_no || '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.actual_pcs || '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">
                              {item.delivery_date ? formatDate(item.delivery_date) : '-'}
                            </td>
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
      </div>

      {/* Legend */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-50 border border-green-200 rounded"></div>
            <span className="text-gray-600">Allocated to Lot</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-50 border border-yellow-200 rounded"></div>
            <span className="text-gray-600">Pending Allocation</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PartywiseDetailReport;
