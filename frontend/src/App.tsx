import { Plus, X } from 'lucide-react';
import { useState } from 'react';
import OrderForm from './components/Forms/OrderForm';
import PartyForm from './components/Forms/PartyForm';
import Header from './components/Layout/Header';
import Navigation from './components/Layout/Navigation';
import BeamAllocationTable from './components/Tables/BeamAllocationTable';
import OrderTable from './components/Tables/OrderTable';
import PartyTable from './components/Tables/PartyTable';
import { ThemeProvider } from './contexts/ThemeContext';
import { BeamColorSummary, OrderResponse, Party } from './services/api';
import './styles/globals.css';

function App() {
  const [activeTab, setActiveTab] = useState('parties');
  const [beamSummary, setBeamSummary] = useState<BeamColorSummary[]>([]);
  const [showPartyForm, setShowPartyForm] = useState(false);
  const [editingParty, setEditingParty] = useState<Party | undefined>();
  const [partyRefreshTrigger, setPartyRefreshTrigger] = useState(0);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [editingOrder, setEditingOrder] = useState<OrderResponse | undefined>();
  const [orderRefreshTrigger, setOrderRefreshTrigger] = useState(0);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleBeamCalculated = (summary: BeamColorSummary[]) => {
    setBeamSummary(summary);
    setActiveTab('beam'); // Auto-switch to beam tab to show results
  };


  const handleAddParty = () => {
    setEditingParty(undefined);
    setShowPartyForm(true);
  };

  const handleEditParty = (party: Party) => {
    setEditingParty(party);
    setShowPartyForm(true);
  };

  const handleClosePartyForm = () => {
    setShowPartyForm(false);
    setEditingParty(undefined);
  };

  const handlePartyCreated = (party: Party) => {
    console.log('Party saved:', party);
    setPartyRefreshTrigger(prev => prev + 1);
    setShowPartyForm(false);
    setEditingParty(undefined);
  };

  const handleAddOrder = () => {
    setEditingOrder(undefined);
    setShowOrderForm(true);
  };

  const handleEditOrder = (order: OrderResponse) => {
    setEditingOrder(order);
    setShowOrderForm(true);
  };

  const handleCloseOrderForm = () => {
    setShowOrderForm(false);
    setEditingOrder(undefined);
  };

  const handleOrderCreated = (order: any) => {
    console.log('Order created:', order);
    setOrderRefreshTrigger(prev => prev + 1);
    setShowOrderForm(false);
    setEditingOrder(undefined);
    if (order.beam_summary) {
      setBeamSummary(order.beam_summary);
      setActiveTab('beam');
    }
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'parties':
        return (
          <div className="space-y-6">
            <div className="container">
              <div className="page-header">
                <div className="flex justify-between items-center">
                  <div>
                    <h1 className="page-title">Party Management</h1>
                    <p className="page-subtitle">
                      Add and manage party details for your textile orders
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {showPartyForm && (
                      <button
                        onClick={handleClosePartyForm}
                        className="btn btn-secondary"
                      >
                        <X size={16} />
                        Cancel
                      </button>
                    )}
                    <button
                      onClick={handleAddParty}
                      className="btn btn-primary"
                      disabled={showPartyForm && !editingParty}
                    >
                      <Plus size={16} />
                      Add Party
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="container">
              <div className="table-section">
                <PartyTable 
                  onEditParty={handleEditParty}
                  refreshTrigger={partyRefreshTrigger}
                />
              </div>
            </div>
            
            {/* Form Overlay */}
            {showPartyForm && (
              <div className="form-overlay">
                <div className="form-overlay-backdrop" onClick={handleClosePartyForm}></div>
                <div className="form-overlay-content">
                  <PartyForm 
                    onPartyCreated={handlePartyCreated}
                    editParty={editingParty}
                    onCancel={handleClosePartyForm}
                  />
                </div>
              </div>
            )}
          </div>
        );
      
      case 'orders':
        return (
          <div className="space-y-6">
            <div className="container">
              <div className="page-header">
                <div className="flex justify-between items-center">
                  <div>
                    <h1 className="page-title">Order Management</h1>
                    <p className="page-subtitle">
                      Create and manage orders with automatic beam allocation calculation
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {showOrderForm && (
                      <button
                        onClick={handleCloseOrderForm}
                        className="btn btn-secondary"
                      >
                        <X size={16} />
                        Cancel
                      </button>
                    )}
                    <button
                      onClick={handleAddOrder}
                      className="btn btn-primary"
                      disabled={showOrderForm && !editingOrder}
                    >
                      <Plus size={16} />
                      Add Order
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="container">
              <div className="table-section">
                <OrderTable 
                  onEditOrder={handleEditOrder}
                  refreshTrigger={orderRefreshTrigger}
                />
              </div>
            </div>
            
            {/* Form Overlay */}
            {showOrderForm && (
              <div className="form-overlay">
                <div className="form-overlay-backdrop" onClick={handleCloseOrderForm}></div>
                <div className="form-overlay-content">
                  <OrderForm 
                    onOrderCreated={handleOrderCreated}
                    onBeamCalculated={handleBeamCalculated}
                    editOrder={editingOrder}
                    onCancel={handleCloseOrderForm}
                  />
                </div>
              </div>
            )}
          </div>
        );
      
      case 'beam':
        return (
          <div>
            <div className="container">
              <div className="page-header">
                <h1 className="page-title">Beam Allocation</h1>
                <p className="page-subtitle">
                  View automatic beam allocation calculations based on your orders
                </p>
              </div>
            </div>
            <div className="container">
              <BeamAllocationTable 
                title="Beam Detail & Summary"
                refreshTrigger={orderRefreshTrigger}
              />
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background flex">
        <Navigation 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
          onSidebarToggle={setIsSidebarCollapsed}
        />
        <div className={`main-content flex-1 flex flex-col ${isSidebarCollapsed ? 'main-content-collapsed' : ''}`}>
          <Header />
          <main className="flex-1">
            {renderActiveTab()}
          </main>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
