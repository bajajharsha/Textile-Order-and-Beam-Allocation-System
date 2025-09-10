import { Moon, Palette, Sun } from 'lucide-react';
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="page-header">
      <div className="container">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Palette className="text-primary" size={28} />
              <div>
                <h1 className="text-xl font-bold text-primary">Textile System</h1>
                <p className="text-sm text-secondary">Order & Beam Allocation</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
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
      </div>
    </header>
  );
};

export default Header;
