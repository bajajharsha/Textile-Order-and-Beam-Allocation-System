import { BarChart3, Package, RefreshCw } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { BeamDetailByQuality, orderApi } from '../../services/api';

interface BeamAllocationTableProps {
  title?: string;
  showEmpty?: boolean;
  refreshTrigger?: number;
}

const BeamAllocationTable: React.FC<BeamAllocationTableProps> = ({ 
  title = "Beam Detail & Summary",
  showEmpty = true,
  refreshTrigger = 0
}) => {
  const [beamDetails, setBeamDetails] = useState<BeamDetailByQuality[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load beam details from all orders
  const loadBeamDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await orderApi.getBeamDetails();
      setBeamDetails(response.data);
    } catch (err) {
      setError('Failed to load beam details');
      console.error('Error loading beam details:', err);
      // Show empty state instead of mock data
      setBeamDetails([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBeamDetails();
  }, [refreshTrigger]);

  const totalOrders = beamDetails.reduce((sum, quality) => sum + quality.items.length, 0);
  const totalPieces = beamDetails.reduce((sum, quality) => 
    sum + quality.items.reduce((itemSum, item) => itemSum + item.total, 0), 0
  );

  if (!beamDetails.length && !showEmpty) {
    return null;
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="text-primary" size={20} />
            <h2 className="card-title">{title}</h2>
          </div>
          <button
            onClick={loadBeamDetails}
            disabled={loading}
            className="btn btn-sm btn-secondary"
            title="Refresh beam details"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
        <p className="card-description">
          Beam allocation details grouped by quality for all orders
        </p>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="loading"></div>
          <span className="ml-2">Loading beam details...</span>
        </div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">
          <Package size={48} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg mb-2">{error}</p>
          <button onClick={loadBeamDetails} className="btn btn-sm btn-primary">
            Try Again
          </button>
        </div>
      ) : beamDetails.length === 0 ? (
        <div className="text-center py-8 text-secondary">
          <Package size={48} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg mb-2">No beam details available</p>
          <p className="text-sm">
            Create orders to see beam allocation calculations here
          </p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left">Party Name</th>
                  <th className="text-left">Quality</th>
                  <th className="text-left">Color Per Beam</th>
                  <th className="text-center">Red</th>
                  <th className="text-center">Firozi</th>
                  <th className="text-center">Gold</th>
                  <th className="text-center">Royal Blue</th>
                  <th className="text-center">Black</th>
                  <th className="text-center">White</th>
                  <th className="text-center">Yellow</th>
                  <th className="text-center">Green</th>
                  <th className="text-center">Purple</th>
                  <th className="text-center">Orange</th>
                  <th className="text-center">Total</th>
                </tr>
              </thead>
              <tbody>
                {beamDetails.map((qualityGroup, groupIndex) => (
                  <React.Fragment key={qualityGroup.quality_name}>
                    {/* Quality Section Header */}
                    <tr className="quality-section-header">
                      <td colSpan={14} className="py-3 px-4 font-semibold text-primary bg-primary/5">
                        {qualityGroup.quality_name}
                      </td>
                    </tr>
                    {/* Quality Items */}
                    {qualityGroup.items.map((item, itemIndex) => (
                      <tr key={`${groupIndex}-${itemIndex}`} className="border-b border-border/50">
                        <td className="py-3 px-4">
                          <div className="font-medium">{item.party_name}</div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="text-sm text-secondary">{item.quality_name}</div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="font-mono text-sm bg-surface-hover px-2 py-1 rounded">
                            {item.color_per_beam}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.red} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.firozi} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.gold} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.royal_blue} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.black} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.white} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.yellow} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.green} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.purple} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <ColorCell value={item.colors.orange} />
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="font-semibold text-primary">
                            {item.total.toLocaleString()}
                          </div>
                        </td>
                      </tr>
                    ))}
                    {/* Quality Subtotal */}
                    {qualityGroup.items.length > 1 && (
                      <tr className="quality-subtotal bg-surface-hover/50">
                        <td colSpan={3} className="py-2 px-4 font-medium text-right">
                          {qualityGroup.quality_name} Subtotal:
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.red, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.firozi, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.gold, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.royal_blue, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.black, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.white, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.yellow, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.green, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.purple, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-medium">
                          {qualityGroup.items.reduce((sum, item) => sum + item.colors.orange, 0).toLocaleString()}
                        </td>
                        <td className="py-2 px-4 text-center font-semibold text-primary">
                          {qualityGroup.items.reduce((sum, item) => sum + item.total, 0).toLocaleString()}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>

          {/* Summary Footer */}
          <div className="mt-6 p-4 bg-surface-hover rounded-lg border border-border">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">{beamDetails.length}</div>
                <div className="text-sm text-secondary">Qualities</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-success">{totalOrders}</div>
                <div className="text-sm text-secondary">Orders</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-warning">{totalPieces.toLocaleString()}</div>
                <div className="text-sm text-secondary">Total Pieces</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-info">
                  {beamDetails.reduce((sum, quality) => 
                    sum + quality.items.reduce((itemSum, item) => 
                      itemSum + Object.values(item.colors).filter(v => v > 0).length, 0
                    ), 0
                  )}
                </div>
                <div className="text-sm text-secondary">Active Colors</div>
              </div>
            </div>
          </div>

          {/* Calculation Formula Info */}
          <div className="mt-4 p-3 bg-primary/5 border border-primary/20 rounded-lg">
            <div className="flex items-start gap-2">
              <div className="text-primary mt-0.5">
                <Package size={16} />
              </div>
              <div className="text-sm">
                <div className="font-medium text-primary mb-1">Calculation Formula:</div>
                <div className="text-secondary">
                  (No.of Sets/pcs) × (no of designs on respective beam) × (no of designs)
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Helper component to display color values
const ColorCell: React.FC<{ value: number }> = ({ value }) => {
  if (value === 0) {
    return <div className="text-gray-400">-</div>;
  }
  
  return (
    <div className="font-medium">
      {value.toLocaleString()}
    </div>
  );
};


export default BeamAllocationTable;
