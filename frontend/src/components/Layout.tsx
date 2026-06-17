import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, Tractor, BrainCircuit, Menu, X } from 'lucide-react';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Log Activity', path: '/log', icon: PlusCircle },
    { name: 'Equipment', path: '/equipment', icon: Tractor },
    { name: 'DSS Predict', path: '/dss', icon: BrainCircuit },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Sidebar for desktop */}
      <aside className="hidden md:flex flex-col w-64 bg-primary-800 text-white">
        <div className="p-6">
          <h1 className="text-2xl font-bold tracking-tight">AgriProfit</h1>
          <p className="text-primary-200 text-xs">Farm Management System</p>
        </div>
        <nav className="flex-1 px-4 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                location.pathname === item.path
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-100 hover:bg-primary-700'
              }`}
            >
              <item.icon size={20} />
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Mobile header */}
      <header className="md:hidden bg-primary-800 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">AgriProfit</h1>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-primary-800 text-white absolute top-14 left-0 right-0 z-50 p-4 border-t border-primary-700">
          <nav className="space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center space-x-3 p-3 rounded-lg ${
                  location.pathname === item.path ? 'bg-primary-700' : ''
                }`}
              >
                <item.icon size={20} />
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        </div>
      )}

      {/* Main content */}
      <main className="flex-1 p-4 md:p-8 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;
