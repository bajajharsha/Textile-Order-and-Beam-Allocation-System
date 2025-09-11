import React, { useEffect, useState } from 'react';
import { OrderItemStatusResponse, OrderResponse, lotApi, orderApi } from '../../services/api';

interface AllocationStatusTableProps {
  className?: string;
}

const AllocationStatusTable: React.FC<AllocationStatusTableProps> = ({ className = '' }) => {
  const [statusData, setStatusData] = useState<OrderItemStatusResponse[]>([]);
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [selectedOrderId, setSelectedOrderId] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadStatusData();
  }, [selectedOrderId]);

  const loadInitialData = async () => {
    try {
      const ordersRes = await orderApi.getAll(1, 100);
      setOrders(ordersRes.data.orders);
    } catch (error) {
      console.error('Error loading orders:', error);
    }
  };

  const loadStatusData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await lotApi.getOrderAllocationStatus(selectedOrderId);
      setStatusData(response.data);
    } catch (error) {
      console.error('Error loading allocation status:', error);
      setError('Failed to load allocation status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const getProgressColor = (allocated: number, total: number) => {
    const percentage = (allocated / total) * 100;
    if (percentage === 0) return 'bg-gray-200';
    if (percentage < 50) return 'bg-red-500';
    if (percentage < 100) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const exportToCSV = () => {
    if (!statusData.length) return;

    const csvData = [];
    csvData.push([
      'Order Number',
      'Party Name',
      'Quality',
      'Design Number',
      'Ground Color',
      'Beam Color Code',
      'Beam Color Name',
      'Total Pieces',
      'Allocated Pieces',
      'Remaining Pieces',
      'Allocation %',
      'Rate per Piece'
    ]);

    statusData.forEach(item => {
      const allocationPercentage = ((item.allocated_pieces / item.total_pieces) * 100).toFixed(1);
      csvData.push([
        item.order_number || '',
        item.party_name || '',
        item.quality_name || '',
        item.design_number,
        item.ground_color_name,
        item.beam_color_code || '',
        item.beam_color_name || '',
        item.total_pieces.toString(),
        item.allocated_pieces.toString(),
        item.remaining_pieces.toString(),
        allocationPercentage + '%',
        item.rate_per_piece?.toString() || ''
      ]);
    });

    const csvContent = csvData.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `allocation_status_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Calculate summary statistics
  const summary = statusData.reduce(
    (acc, item) => ({
      totalPieces: acc.totalPieces + item.total_pieces,
      allocatedPieces: acc.allocatedPieces + item.allocated_pieces,
      remainingPieces: acc.remainingPieces + item.remaining_pieces,
      totalValue: acc.totalValue + (item.total_pieces * (item.rate_per_piece || 0))
    }),
    { totalPieces: 0, allocatedPieces: 0, remainingPieces: 0, totalValue: 0 }
  );

  const overallAllocationPercentage = summary.totalPieces > 0 
    ? (summary.allocatedPieces / summary.totalPieces) * 100 
    : 0;

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
            onClick={loadStatusData}
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
              Order Allocation Status
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Track allocated vs remaining pieces for each order item
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedOrderId || ''}
              onChange={(e) => setSelectedOrderId(e.target.value ? parseInt(e.target.value) : undefined)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Orders</option>
              {orders.map(order => (
                <option key={order.id} value={order.id}>
                  {order.order_number} - {order.party_name}
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
      {statusData.length > 0 && (
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Total Pieces</h4>
              <p className="text-2xl font-semibold text-gray-900">{summary.totalPieces.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Allocated Pieces</h4>
              <p className="text-2xl font-semibold text-green-600">{summary.allocatedPieces.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Remaining Pieces</h4>
              <p className="text-2xl font-semibold text-orange-600">{summary.remainingPieces.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <h4 className="text-sm font-medium text-gray-500">Overall Allocation</h4>
              <p className="text-2xl font-semibold text-blue-600">{overallAllocationPercentage.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Table Content */}
      <div className="overflow-hidden">
        {statusData.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No allocation data found for the selected criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Party
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quality
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Design
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ground Color
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Beam Color
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Allocated
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Remaining
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {statusData.map((item, index) => {
                  const allocationPercentage = (item.allocated_pieces / item.total_pieces) * 100;
                  const itemValue = item.total_pieces * (item.rate_per_piece || 0);
                  
                  return (
                    <tr key={`${item.id}-${index}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.order_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.party_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.quality_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.design_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.ground_color_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center space-x-1">
                          <span className="font-medium">{item.beam_color_code}</span>
                          <span className="text-gray-500">-</span>
                          <span>{item.beam_color_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.total_pieces.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                        {item.allocated_pieces.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600 font-medium">
                        {item.remaining_pieces.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(item.allocated_pieces, item.total_pieces)}`}
                              style={{ width: `${allocationPercentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-600 w-12">
                            {allocationPercentage.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.rate_per_piece ? formatCurrency(itemValue) : '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-2 bg-gray-200 rounded"></div>
            <span className="text-gray-600">Not Allocated</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-2 bg-red-500 rounded"></div>
            <span className="text-gray-600">{'< 50% Allocated'}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-2 bg-yellow-500 rounded"></div>
            <span className="text-gray-600">50-99% Allocated</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-2 bg-green-500 rounded"></div>
            <span className="text-gray-600">Fully Allocated</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AllocationStatusTable;
