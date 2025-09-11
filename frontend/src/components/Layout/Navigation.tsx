import { BarChart3, BookOpen, ChevronLeft, ChevronRight, FileText, ShoppingCart, Users } from 'lucide-react';
import React, { useState } from 'react';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onSidebarToggle?: (isCollapsed: boolean) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange, onSidebarToggle }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  const handleToggle = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    onSidebarToggle?.(newState);
  };
  
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
    },
    {
      id: 'partywise-detail',
      label: 'Partywise Detail',
      icon: FileText,
      description: 'View order details by party'
    },
    {
      id: 'lot-register',
      label: 'Lot Register',
      icon: BookOpen,
      description: 'View and manage lot register'
    }
  ];

  return (
    <aside className={`sidebar ${isCollapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        {!isCollapsed && <h2 className="sidebar-title">Navigation</h2>}
        <button
          onClick={handleToggle}
          className="sidebar-toggle"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
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
              title={isCollapsed ? tab.label : undefined}
            >
              <div className="sidebar-item-icon">
                <Icon size={20} />
              </div>
              {!isCollapsed && (
                <div className="sidebar-item-content">
                  <div className="sidebar-item-label">{tab.label}</div>
                  <div className="sidebar-item-description">{tab.description}</div>
                </div>
              )}
            </button>
          );
        })}
      </nav>
    </aside>
  );
};

export default Navigation;
