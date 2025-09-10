import { BarChart3, Package } from 'lucide-react';
import React from 'react';
import { BeamColorSummary } from '../../services/api';

interface BeamAllocationTableProps {
  beamSummary: BeamColorSummary[];
  title?: string;
  showEmpty?: boolean;
}

const BeamAllocationTable: React.FC<BeamAllocationTableProps> = ({ 
  beamSummary, 
  title = "Beam Allocation Summary",
  showEmpty = true 
}) => {
  const totalPieces = beamSummary.reduce((sum, beam) => sum + beam.total_pieces, 0);

  if (!beamSummary.length && !showEmpty) {
    return null;
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-2">
          <BarChart3 className="text-primary" size={20} />
          <h2 className="card-title">{title}</h2>
        </div>
        <p className="card-description">
          Automatic calculation based on ground colors, beam colors, and design count
        </p>
      </div>

      {beamSummary.length === 0 ? (
        <div className="text-center py-8 text-secondary">
          <Package size={48} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg mb-2">No beam allocation calculated yet</p>
          <p className="text-sm">
            Fill in the order form and click "Preview Beam Allocation" to see the calculation
          </p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Beam Color</th>
                  <th className="text-center">Total Pieces</th>
                  <th className="text-center">Percentage</th>
                  <th className="text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {beamSummary.map((beam, index) => {
                  const percentage = totalPieces > 0 ? ((beam.total_pieces / totalPieces) * 100).toFixed(1) : '0.0';
                  
                  return (
                    <tr key={beam.beam_color_id || index}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-4 h-4 rounded-full border-2 border-border"
                            style={{ 
                              backgroundColor: getColorForBeam(beam.beam_color_name),
                            }}
                          />
                          <span className="font-medium">{beam.beam_color_name}</span>
                        </div>
                      </td>
                      <td className="text-center">
                        <span className="font-semibold text-lg">{beam.total_pieces.toLocaleString()}</span>
                      </td>
                      <td className="text-center">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-16 bg-border rounded-full h-2 overflow-hidden">
                            <div 
                              className="h-full bg-primary transition-all duration-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{percentage}%</span>
                        </div>
                      </td>
                      <td className="text-center">
                        <span className={`status-badge ${beam.total_pieces > 0 ? 'status-active' : 'status-inactive'}`}>
                          {beam.total_pieces > 0 ? 'Active' : 'No Pieces'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Summary Footer */}
          <div className="mt-6 p-4 bg-surface-hover rounded-lg border border-border">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">{beamSummary.length}</div>
                <div className="text-sm text-secondary">Beam Colors</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-success">{totalPieces.toLocaleString()}</div>
                <div className="text-sm text-secondary">Total Pieces</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-warning">
                  {beamSummary.filter(b => b.total_pieces > 0).length}
                </div>
                <div className="text-sm text-secondary">Active Beams</div>
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
                  Total Pieces = (Pieces per Color × Number of Designs × Beam Color Count)
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Helper function to generate colors for beam visualization
const getColorForBeam = (colorName: string): string => {
  const colorMap: Record<string, string> = {
    'Red': '#ef4444',
    'Blue': '#3b82f6',
    'Green': '#10b981',
    'Yellow': '#f59e0b',
    'Purple': '#8b5cf6',
    'Pink': '#ec4899',
    'Orange': '#f97316',
    'Teal': '#14b8a6',
    'Indigo': '#6366f1',
    'Gray': '#6b7280',
    'Black': '#1f2937',
    'White': '#f9fafb',
    'Brown': '#a3a3a3',
    'Cyan': '#06b6d4',
    'Lime': '#84cc16',
    'Amber': '#f59e0b',
    'Emerald': '#059669',
    'Rose': '#f43f5e',
    'Violet': '#7c3aed',
    'Sky': '#0ea5e9',
    'Firozi': '#0ea5e9',
    'Gold': '#f59e0b',
    'Royal Blue': '#1e40af'
  };

  // Try to find exact match first
  const exactMatch = Object.keys(colorMap).find(key => 
    key.toLowerCase() === colorName.toLowerCase()
  );
  
  if (exactMatch) {
    return colorMap[exactMatch];
  }

  // Try partial match
  const partialMatch = Object.keys(colorMap).find(key => 
    colorName.toLowerCase().includes(key.toLowerCase()) || 
    key.toLowerCase().includes(colorName.toLowerCase())
  );
  
  if (partialMatch) {
    return colorMap[partialMatch];
  }

  // Generate a color based on string hash
  let hash = 0;
  for (let i = 0; i < colorName.length; i++) {
    hash = colorName.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 50%)`;
};

export default BeamAllocationTable;
