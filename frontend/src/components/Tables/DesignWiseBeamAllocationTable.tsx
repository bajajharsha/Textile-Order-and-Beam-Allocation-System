import { AlertCircle, ChevronDown, ChevronRight, Package, Plus, RefreshCw } from 'lucide-react';
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
  design_number: string;
  total_sets: number;
  allocated_sets: number;
  remaining_sets: number;
  beam_pieces: BeamPiece[];
}

interface DesignWiseBeamAllocationTableProps {
  refreshTrigger?: number;
}

// Standard beam colors in order
const BEAM_COLORS = [
  { code: 'R', name: 'Red' },
  { code: 'F', name: 'Firozi' },
  { code: 'G', name: 'Gold' },
  { code: 'RB', name: 'Royal Blue' },
  { code: 'B', name: 'Black' },
  { code: 'W', name: 'White' },
  { code: 'Y', name: 'Yellow' },
  { code: 'GR', name: 'Green' },
  { code: 'P', name: 'Purple' },
  { code: 'O', name: 'Orange' },
];

const DesignWiseBeamAllocationTable: React.FC<DesignWiseBeamAllocationTableProps> = ({
  refreshTrigger = 0
}) => {
  const [designs, setDesigns] = useState<DesignAllocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedOrders, setExpandedOrders] = useState<Set<number>>(new Set());
  const [showLotForm, setShowLotForm] = useState(false);

  useEffect(() => {
    fetchDesignAllocations();
  }, [refreshTrigger]);

  const fetchDesignAllocations = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8001/api/v1/designs/allocation/design-wise');
      
      if (!response.ok) throw new Error('Failed to fetch design allocations');

      const data = await response.json();
      setDesigns(data.designs || []);

      // Auto-expand all orders initially
      const orderIds = new Set<number>(data.designs.map((d: DesignAllocation) => d.order_id));
      setExpandedOrders(orderIds);
    } catch (err) {
      console.error('Error fetching design allocations:', err);
      setError('Failed to load design allocation data');
    } finally {
      setLoading(false);
    }
  };

  const toggleOrder = (orderId: number) => {
    const newExpanded = new Set(expandedOrders);
    if (newExpanded.has(orderId)) {
      newExpanded.delete(orderId);
    } else {
      newExpanded.add(orderId);
    }
    setExpandedOrders(newExpanded);
  };

  const getBeamPiecesForColor = (design: DesignAllocation, colorCode: string): number => {
    const beam = design.beam_pieces.find(b => b.beam_color_code === colorCode);
    return beam ? beam.pieces : 0;
  };

  const getTotalBeamPieces = (design: DesignAllocation): number => {
    return design.beam_pieces.reduce((sum, b) => sum + b.pieces, 0);
  };

  // Group designs by order
  const groupedByOrder = designs.reduce((acc, design) => {
    if (!acc[design.order_id]) {
      acc[design.order_id] = {
        order_number: design.order_number,
        party_name: design.party_name,
        quality_name: design.quality_name,
        designs: []
      };
    }
    acc[design.order_id].designs.push(design);
    return acc;
  }, {} as Record<number, { order_number: string; party_name: string; quality_name: string; designs: DesignAllocation[] }>);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center space-y-4">
          <RefreshCw className="animate-spin text-blue-600" size={48} />
          <p className="text-gray-600">Loading design allocations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <AlertCircle className="text-red-600" size={24} />
          <div>
            <h3 className="font-semibold text-red-900">Error Loading Data</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
        <button
          onClick={fetchDesignAllocations}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (designs.length === 0) {
    return (
      <div style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--border-radius)',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <Package className="mx-auto mb-4" size={48} style={{ color: 'var(--color-text-muted)' }} />
        <h3 className="mb-2" style={{ 
          fontSize: '1.125rem', 
          fontWeight: 600, 
          color: 'var(--color-text-primary)' 
        }}>
          No Design Allocations
        </h3>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          Create an order to see design-wise beam allocation details
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div style={{
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--border-radius)',
        boxShadow: 'var(--shadow-sm)',
        padding: '1.5rem'
      }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Package size={32} style={{ color: 'var(--color-primary)' }} />
            <div>
              <h2 style={{ 
                fontSize: '1.25rem', 
                fontWeight: 700, 
                color: 'var(--color-text-primary)',
                marginBottom: '0.25rem'
              }}>
                Design-Wise Beam Allocation
              </h2>
              <p style={{ 
                fontSize: '0.875rem', 
                color: 'var(--color-text-secondary)' 
              }}>
                Track sets and beam pieces per design with reduction
              </p>
            </div>
          </div>
          <div className="flex items-center" style={{ gap: '1rem' }}>
            <button
              onClick={fetchDesignAllocations}
              className="btn btn-secondary flex items-center space-x-2"
            >
              <RefreshCw size={16} />
              <span>Refresh</span>
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

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4" style={{ marginTop: '1.5rem' }}>
          <div style={{
            backgroundColor: 'var(--color-primary-light)',
            border: '1px solid var(--color-primary)',
            borderRadius: 'var(--border-radius)',
            padding: '1rem'
          }}>
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--color-primary)', 
              fontWeight: 500,
              marginBottom: '0.25rem'
            }}>
              Total Designs
            </div>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: 700, 
              color: 'var(--color-text-primary)' 
            }}>
              {designs.length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-success)',
            borderRadius: 'var(--border-radius)',
            padding: '1rem'
          }}>
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--color-success)', 
              fontWeight: 500,
              marginBottom: '0.25rem'
            }}>
              Total Remaining Sets
            </div>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: 700, 
              color: 'var(--color-text-primary)' 
            }}>
              {designs.reduce((sum, d) => sum + d.remaining_sets, 0)}
            </div>
          </div>
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-warning)',
            borderRadius: 'var(--border-radius)',
            padding: '1rem'
          }}>
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--color-warning)', 
              fontWeight: 500,
              marginBottom: '0.25rem'
            }}>
              Total Allocated Sets
            </div>
            <div style={{ 
              fontSize: '1.5rem', 
              fontWeight: 700, 
              color: 'var(--color-text-primary)' 
            }}>
              {designs.reduce((sum, d) => sum + d.allocated_sets, 0)}
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div style={{
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--border-radius)',
        boxShadow: 'var(--shadow-sm)',
        overflow: 'hidden'
      }}>
        <div className="overflow-x-auto">
          <table className="w-full">
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
                  letterSpacing: '0.05em',
                  position: 'sticky',
                  left: 0,
                  backgroundColor: 'var(--color-surface-hover)',
                  zIndex: 10
                }}>
                  Order / Design
                </th>
                <th style={{
                  padding: '0.875rem 1rem',
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Total<br/>Sets
                </th>
                <th style={{
                  padding: '0.875rem 1rem',
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Allocated<br/>Sets
                </th>
                <th style={{
                  padding: '0.875rem 1rem',
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Remaining<br/>Sets
                </th>
                {BEAM_COLORS.map((color) => (
                  <th
                    key={color.code}
                    style={{
                      padding: '0.875rem 0.75rem',
                      textAlign: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--color-text-primary)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}
                    title={color.name}
                  >
                    {color.code}
                  </th>
                ))}
                <th style={{
                  padding: '0.875rem 1rem',
                  textAlign: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Total<br/>Pieces
                </th>
              </tr>
            </thead>
            <tbody style={{
              backgroundColor: 'var(--color-surface)',
              borderTop: '1px solid var(--color-border)'
            }}>
              {Object.entries(groupedByOrder).map(([orderId, orderData]) => {
                const isExpanded = expandedOrders.has(Number(orderId));
                
                return (
                  <React.Fragment key={orderId}>
                    {/* Order Header Row */}
                    <tr className="bg-blue-50 hover:bg-blue-100 cursor-pointer transition-colors">
                      <td
                        className="px-4 py-3 sticky left-0 bg-blue-50 z-10"
                        onClick={() => toggleOrder(Number(orderId))}
                      >
                        <div className="flex items-center space-x-2">
                          {isExpanded ? (
                            <ChevronDown size={18} className="text-blue-600" />
                          ) : (
                            <ChevronRight size={18} className="text-blue-600" />
                          )}
                          <div>
                            <div className="font-semibold text-gray-900">{orderData.order_number}</div>
                            <div className="text-xs text-gray-600">
                              {orderData.party_name} • {orderData.quality_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td colSpan={14} className="px-4 py-3 text-sm text-gray-600">
                        {orderData.designs.length} design{orderData.designs.length !== 1 ? 's' : ''}
                      </td>
                    </tr>

                    {/* Design Rows (Expandable) */}
                    {isExpanded && orderData.designs.map((design) => (
                      <tr key={`${orderId}-${design.design_number}`} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 pl-12 sticky left-0 bg-white z-10">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                            <span className="font-medium text-gray-900">{design.design_number}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center text-sm text-gray-900 font-medium">
                          {design.total_sets}
                        </td>
                        <td className="px-4 py-3 text-center text-sm">
                          <span className="inline-block px-2 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">
                            {design.allocated_sets}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center text-sm">
                          <span className={`inline-block px-2 py-1 rounded-full font-medium ${
                            design.remaining_sets > 0 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-500'
                          }`}>
                            {design.remaining_sets}
                          </span>
                        </td>
                        {BEAM_COLORS.map((color) => {
                          const pieces = getBeamPiecesForColor(design, color.code);
                          return (
                            <td key={color.code} className="px-3 py-3 text-center text-sm">
                              {pieces > 0 ? (
                                <span className="font-medium text-gray-900">{pieces}</span>
                              ) : (
                                <span className="text-gray-300">-</span>
                              )}
                            </td>
                          );
                        })}
                        <td className="px-4 py-3 text-center text-sm font-bold text-gray-900">
                          {getTotalBeamPieces(design)}
                        </td>
                      </tr>
                    ))}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

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

export default DesignWiseBeamAllocationTable;

