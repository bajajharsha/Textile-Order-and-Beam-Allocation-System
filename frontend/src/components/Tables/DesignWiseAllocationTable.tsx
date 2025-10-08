import { AlertCircle, ChevronDown, ChevronRight, Package, Plus } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import SetBasedLotCreationForm from '../Forms/SetBasedLotCreationForm';

interface BeamPiece {
  beam_color_code: string;
  beam_color_name: string;
  beam_multiplier: number;
  pieces: number;
}

interface DesignAllocation {
  order_id: number;
  order_number: string;
  party_name: string;
  quality_name: string;
  lot_register_type: string;
  design_number: string;
  total_sets: number;
  allocated_sets: number;
  remaining_sets: number;
  beam_pieces: BeamPiece[];
}

interface DesignWiseAllocationTableProps {
  refreshTrigger?: number;
}

const DesignWiseAllocationTable: React.FC<DesignWiseAllocationTableProps> = ({ 
  refreshTrigger = 0 
}) => {
  const [designs, setDesigns] = useState<DesignAllocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedOrders, setExpandedOrders] = useState<Set<number>>(new Set());
  const [selectedLotType, setSelectedLotType] = useState<string>('all');
  const [showLotForm, setShowLotForm] = useState(false);

  useEffect(() => {
    fetchDesignAllocations();
  }, [refreshTrigger]);

  const fetchDesignAllocations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8001/api/v1/designs/allocation/design-wise');
      
      if (!response.ok) {
        throw new Error('Failed to fetch design allocations');
      }

      const data = await response.json();
      setDesigns(data.designs || []);
      
      // Auto-expand all orders initially
      const orderIds = new Set<number>(data.designs.map((d: DesignAllocation) => d.order_id));
      setExpandedOrders(orderIds);
    } catch (err) {
      console.error('Error fetching design allocations:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const toggleOrderExpansion = (orderId: number) => {
    const newExpanded = new Set(expandedOrders);
    if (newExpanded.has(orderId)) {
      newExpanded.delete(orderId);
    } else {
      newExpanded.add(orderId);
    }
    setExpandedOrders(newExpanded);
  };

  // Group designs by order
  const groupedByOrder = designs.reduce((acc, design) => {
    if (!acc[design.order_id]) {
      acc[design.order_id] = {
        order_id: design.order_id,
        order_number: design.order_number,
        party_name: design.party_name,
        quality_name: design.quality_name,
        lot_register_type: design.lot_register_type,
        designs: []
      };
    }
    acc[design.order_id].designs.push(design);
    return acc;
  }, {} as Record<number, any>);

  const orders = Object.values(groupedByOrder);

  // Filter by lot register type
  const filteredOrders = selectedLotType === 'all' 
    ? orders 
    : orders.filter(order => order.lot_register_type === selectedLotType);

  // Calculate totals
  const totalRemainingSetsAll = designs.reduce((sum, d) => sum + d.remaining_sets, 0);
  const totalAllocatedSetsAll = designs.reduce((sum, d) => sum + d.allocated_sets, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-red-800">
          <AlertCircle size={20} />
          <span className="font-medium">Error: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Package className="text-blue-600" size={24} />
            <div>
              <h2 className="text-xl font-bold text-gray-900">Design-Wise Beam Allocation</h2>
              <p className="text-sm text-gray-600">Track remaining sets and beam requirements per design</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchDesignAllocations}
              className="btn btn-secondary"
            >
              Refresh
            </button>
            <button
              onClick={() => setShowLotForm(true)}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Plus size={16} />
              <span>Create Lot</span>
            </button>
          </div>
        </div>

        {/* Lot Type Filter */}
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Filter by Type:</label>
          <div className="flex space-x-2">
            {['all', 'High Speed', 'Slow Speed', 'K1K2'].map((type) => (
              <button
                key={type}
                onClick={() => setSelectedLotType(type)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedLotType === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type === 'all' ? 'All Types' : type}
              </button>
            ))}
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-sm text-blue-600 font-medium">Total Designs</div>
            <div className="text-2xl font-bold text-blue-900">{designs.length}</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-sm text-green-600 font-medium">Remaining Sets</div>
            <div className="text-2xl font-bold text-green-900">{totalRemainingSetsAll}</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-sm text-purple-600 font-medium">Allocated Sets</div>
            <div className="text-2xl font-bold text-purple-900">{totalAllocatedSetsAll}</div>
          </div>
        </div>
      </div>

      {/* Orders List */}
      {filteredOrders.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <Package className="mx-auto text-gray-400 mb-3" size={48} />
          <p className="text-gray-600">No designs found for selected filter</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredOrders.map((order) => {
            const isExpanded = expandedOrders.has(order.order_id);
            const orderTotalRemaining = order.designs.reduce((sum: number, d: DesignAllocation) => sum + d.remaining_sets, 0);
            const orderTotalAllocated = order.designs.reduce((sum: number, d: DesignAllocation) => sum + d.allocated_sets, 0);

            return (
              <div key={order.order_id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                {/* Order Header */}
                <div
                  className="bg-gray-50 px-6 py-4 cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => toggleOrderExpansion(order.order_id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                      <div>
                        <div className="flex items-center space-x-3">
                          <span className="font-semibold text-gray-900">{order.order_number}</span>
                          <span className="text-sm text-gray-600">•</span>
                          <span className="text-sm font-medium text-gray-700">{order.party_name}</span>
                          <span className="text-sm text-gray-600">•</span>
                          <span className="text-sm text-gray-600">{order.quality_name}</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            order.lot_register_type === 'High Speed' ? 'bg-green-100 text-green-800' :
                            order.lot_register_type === 'Slow Speed' ? 'bg-blue-100 text-blue-800' :
                            'bg-purple-100 text-purple-800'
                          }`}>
                            {order.lot_register_type}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="text-right">
                        <div className="text-gray-500">Designs</div>
                        <div className="font-semibold text-gray-900">{order.designs.length}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-gray-500">Remaining Sets</div>
                        <div className="font-semibold text-green-600">{orderTotalRemaining}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-gray-500">Allocated Sets</div>
                        <div className="font-semibold text-purple-600">{orderTotalAllocated}</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Designs Table */}
                {isExpanded && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Design
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Total Sets
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Allocated
                          </th>
                          <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Remaining
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Beam Allocation
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {order.designs.map((design: DesignAllocation) => (
                          <tr key={`${design.order_id}-${design.design_number}`} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="font-medium text-gray-900">{design.design_number}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="text-gray-900">{design.total_sets}</span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="text-purple-600 font-medium">{design.allocated_sets}</span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className={`font-semibold ${
                                design.remaining_sets === 0 ? 'text-gray-400' :
                                design.remaining_sets < 10 ? 'text-orange-600' :
                                'text-green-600'
                              }`}>
                                {design.remaining_sets}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex flex-wrap gap-2">
                                {design.beam_pieces.map((beam, idx) => (
                                  <div
                                    key={idx}
                                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-50 border border-blue-200"
                                  >
                                    <span className="font-medium text-blue-900">
                                      {beam.beam_color_code}-{beam.beam_multiplier}
                                    </span>
                                    <span className="mx-2 text-blue-400">→</span>
                                    <span className="text-blue-700 font-semibold">
                                      {beam.pieces} pcs
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Lot Creation Form Modal */}
      {showLotForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <SetBasedLotCreationForm
              onLotCreated={() => {
                setShowLotForm(false);
                fetchDesignAllocations(); // Refresh data
              }}
              onCancel={() => setShowLotForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default DesignWiseAllocationTable;
