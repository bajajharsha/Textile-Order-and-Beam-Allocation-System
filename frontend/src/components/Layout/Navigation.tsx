import { BarChart3, ShoppingCart, Users } from 'lucide-react';
import React from 'react';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    {
      id: 'parties',
      label: 'Party Details',
      icon: Users,
      description: 'Manage party information'
    },
    {
      id: 'orders',
      label: 'Order Entry',
      icon: ShoppingCart,
      description: 'Create and manage orders'
    },
    {
      id: 'beam',
      label: 'Beam Allocation',
      icon: BarChart3,
      description: 'View beam calculations'
    }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Navigation</h2>
      </div>
      <nav className="sidebar-nav">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`sidebar-item ${isActive ? 'sidebar-item-active' : ''}`}
            >
              <div className="sidebar-item-icon">
                <Icon size={20} />
              </div>
              <div className="sidebar-item-content">
                <div className="sidebar-item-label">{tab.label}</div>
                <div className="sidebar-item-description">{tab.description}</div>
              </div>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};

export default Navigation;
