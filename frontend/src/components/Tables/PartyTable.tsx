import { Edit, Search, Trash2 } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { Party, partyApi } from '../../services/api';

interface PartyTableProps {
  onEditParty?: (party: Party) => void;
  refreshTrigger?: number;
}

const PartyTable: React.FC<PartyTableProps> = ({ onEditParty, refreshTrigger }) => {
  const [parties, setParties] = useState<Party[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredParties, setFilteredParties] = useState<Party[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 10;

  // Load parties
  const loadParties = async (page = 1, search = '') => {
    setLoading(true);
    try {
      if (search.trim()) {
        // Use search API when there's a search query
        const response = await partyApi.search(search.trim(), pageSize);
        setParties(response.data.parties);
        setFilteredParties(response.data.parties);
        setTotalCount(response.data.total);
        setTotalPages(Math.ceil(response.data.total / pageSize));
      } else {
        // Use regular pagination when no search
        const response = await partyApi.getAll(page, pageSize);
        setParties(response.data.parties);
        setFilteredParties(response.data.parties);
        setTotalCount(response.data.total);
        setTotalPages(Math.ceil(response.data.total / pageSize));
      }
      setCurrentPage(page);
    } catch (error) {
      console.error('Error loading parties:', error);
      setParties([]);
      setFilteredParties([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and refresh trigger
  useEffect(() => {
    loadParties(1, searchQuery);
  }, [refreshTrigger]);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    loadParties(1, query);
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    loadParties(page, searchQuery);
  };

  // Handle delete
  const handleDelete = async (partyId: number, partyName: string) => {
    if (window.confirm(`Are you sure you want to delete party "${partyName}"?`)) {
      try {
        await partyApi.delete(partyId);
        loadParties(currentPage, searchQuery);
        alert('Party deleted successfully!');
      } catch (error) {
        console.error('Error deleting party:', error);
        alert('Failed to delete party. Please try again.');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="search-bar">
        <div className="flex items-center gap-6">
          <div className="flex-1 search-input-container">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search parties by name..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="form-input search-input"
            />
          </div>
          <div className="search-results-badge">
            {totalCount} {totalCount === 1 ? 'party' : 'parties'} found
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-medium text-secondary">Name</th>
                <th className="text-left py-3 px-4 font-medium text-secondary">Contact</th>
                <th className="text-left py-3 px-4 font-medium text-secondary">Broker</th>
                <th className="text-left py-3 px-4 font-medium text-secondary">GST</th>
                <th className="text-left py-3 px-4 font-medium text-secondary">Address</th>
                <th className="text-left py-3 px-4 font-medium text-secondary">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center">
                    <div className="flex items-center justify-center">
                      <div className="loading"></div>
                      <span className="ml-2">Loading parties...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredParties.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-secondary">
                    {searchQuery ? 'No parties found matching your search.' : 'No parties found.'}
                  </td>
                </tr>
              ) : (
                filteredParties.map((party) => (
                  <tr key={party.id} className="border-b border-border hover:bg-surface">
                    <td className="py-3 px-4">
                      <div className="font-medium">{party.party_name}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm">{party.contact_number}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm">{party.broker_name || '-'}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm">{party.gst || '-'}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm max-w-xs truncate" title={party.address}>
                        {party.address || '-'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => onEditParty?.(party)}
                          className="btn btn-secondary btn-sm hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300"
                          title="Edit party"
                        >
                          <Edit size={14} />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(party.id!, party.party_name)}
                          className="btn btn-danger btn-sm hover:bg-red-50 hover:text-red-600 hover:border-red-300"
                          title="Delete party"
                        >
                          <Trash2 size={14} />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-slate-800 dark:to-slate-700 border-t border-border">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="text-sm text-secondary font-medium">
                Showing <span className="font-semibold text-primary">{((currentPage - 1) * pageSize) + 1}</span> to{' '}
                <span className="font-semibold text-primary">{Math.min(currentPage * pageSize, totalCount)}</span> of{' '}
                <span className="font-semibold text-primary">{totalCount}</span> parties
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="btn btn-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <div className="flex items-center gap-1">
                  <span className="text-sm text-secondary">Page</span>
                  <span className="px-3 py-1 bg-primary text-white rounded-md font-semibold text-sm">
                    {currentPage}
                  </span>
                  <span className="text-sm text-secondary">of {totalPages}</span>
                </div>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="btn btn-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PartyTable;
