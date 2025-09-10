import { Edit, Eye, Search, Trash2 } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { orderApi, OrderResponse } from '../../services/api';

interface OrderTableProps {
  onEditOrder?: (order: OrderResponse) => void;
  onViewOrder?: (order: OrderResponse) => void;
  refreshTrigger?: number;
}

const OrderTable: React.FC<OrderTableProps> = ({ onEditOrder, onViewOrder, refreshTrigger }) => {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredOrders, setFilteredOrders] = useState<OrderResponse[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 10;

  // Load orders
  const loadOrders = async (page = 1, search = '') => {
    setLoading(true);
    try {
      if (search.trim()) {
        // Use search API when there's a search query
        const response = await orderApi.search(search.trim(), pageSize);
        setOrders(response.data.orders);
        setFilteredOrders(response.data.orders);
        setTotalCount(response.data.total);
        setTotalPages(Math.ceil(response.data.total / pageSize));
      } else {
        // Use regular pagination when no search
        const response = await orderApi.getAll(page, pageSize);
        setOrders(response.data.orders);
        setFilteredOrders(response.data.orders);
        setTotalCount(response.data.total);
        setTotalPages(Math.ceil(response.data.total / pageSize));
      }
      setCurrentPage(page);
    } catch (error) {
      console.error('Error loading orders:', error);
      setOrders([]);
      setFilteredOrders([]);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and refresh trigger
  useEffect(() => {
    loadOrders(1, searchQuery);
  }, [refreshTrigger]);

  // Search functionality
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    loadOrders(1, query);
  };

  // Pagination
  const handlePageChange = (page: number) => {
    loadOrders(page, searchQuery);
  };

  // Delete order
  const handleDelete = async (orderId: number, orderName: string) => {
    if (window.confirm(`Are you sure you want to delete order "${orderName}"?`)) {
      try {
        await orderApi.delete(orderId);
        loadOrders(currentPage, searchQuery);
      } catch (error) {
        console.error('Error deleting order:', error);
        alert('Failed to delete order. Please try again.');
      }
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
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
              placeholder="Search orders by party name or order number..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="form-input search-input"
            />
          </div>
          <div className="search-results-badge">
            {totalCount} {totalCount === 1 ? 'order' : 'orders'} found
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th>Order #</th>
                <th>Party ID</th>
                <th>Quality ID</th>
                <th>Rate/Piece</th>
                <th>Designs</th>
                <th>Total Pieces</th>
                <th>Total Value</th>
                <th>Order Date</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={10} className="text-center py-8">
                    <div className="loading"></div>
                    <span className="ml-2">Loading orders...</span>
                  </td>
                </tr>
              ) : filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={10} className="text-center py-8 text-gray-500">
                    No orders found
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => (
                  <tr key={order.id}>
                    <td className="py-3 px-4">
                      <div className="font-medium">#{order.order_number}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium">Party #{order.party_id || 'N/A'}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div>Quality #{order.quality_id || 'N/A'}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div>{formatCurrency(order.rate_per_piece || 0)}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium">{order.total_designs}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium">{order.total_pieces}</div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-green-600">
                        {formatCurrency(order.total_value)}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm text-gray-500">
                        {order.order_date ? formatDate(order.order_date) : 'N/A'}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-sm text-gray-500">
                        {formatDate(order.created_at)}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {onViewOrder && (
                          <button
                            onClick={() => onViewOrder(order)}
                            className="btn btn-sm btn-secondary"
                            title="View Details"
                          >
                            <Eye size={14} />
                          </button>
                        )}
                        {onEditOrder && (
                          <button
                            onClick={() => onEditOrder(order)}
                            className="btn btn-sm btn-primary"
                            title="Edit Order"
                          >
                            <Edit size={14} />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(order.id, `Order #${order.order_number}`)}
                          className="btn btn-sm btn-danger"
                          title="Delete Order"
                        >
                          <Trash2 size={14} />
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
          <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} orders
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="btn btn-sm btn-secondary"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="btn btn-sm btn-secondary"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTable;
