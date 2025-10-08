import { Moon, Palette, Sun } from 'lucide-react';
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header style={{ 
      backgroundColor: 'var(--color-surface)', 
      borderBottom: '1px solid var(--color-border)',
      padding: '1rem 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ 
        maxWidth: '100%', 
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Palette size={24} style={{ color: 'var(--color-primary)' }} />
          <div>
            <h1 style={{ 
              fontSize: '1.125rem', 
              fontWeight: 600, 
              color: 'var(--color-text-primary)',
              margin: 0,
              lineHeight: 1.5,
              letterSpacing: '-0.01em'
            }}>
              Textile Management System
            </h1>
            <p style={{ 
              fontSize: '0.75rem', 
              color: 'var(--color-text-secondary)',
              margin: 0,
              lineHeight: 1.5
            }}>
              Order & Beam Allocation
            </p>
          </div>
        </div>
        
        <div>
          <button
            onClick={toggleTheme}
            className="btn btn-secondary btn-sm"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? (
              <Moon size={16} />
            ) : (
              <Sun size={16} />
            )}
            {theme === 'light' ? 'Dark' : 'Light'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
