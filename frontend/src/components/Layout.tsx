import React, { useState } from "react";
import { Outlet, Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogOut, LayoutDashboard, FileText, MessageCircle, Menu, X, Scale } from "lucide-react";
import { motion } from "framer-motion";

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const navItems = [
    { name: "Dashboard", path: "/", icon: <LayoutDashboard className="h-5 w-5" /> },
    { name: "My Cases", path: "/cases", icon: <FileText className="h-5 w-5" /> },
    { name: "AI Chat", path: "/chat", icon: <MessageCircle className="h-5 w-5" /> },
  ];

  return (
    <div className="min-h-screen flex bg-gray-50/50">
      {/* Sidebar */}
      <motion.aside
        initial={{ width: 260 }}
        animate={{ width: isSidebarOpen ? 260 : 72 }}
        className="hidden md:flex flex-col bg-white border-r border-gray-200 z-10 sticky top-0 h-screen transition-all duration-300 shadow-sm"
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-100">
          <Link to="/" className={`flex items-center space-x-3 overflow-hidden ${!isSidebarOpen && 'justify-center'}`}>
            <div className="bg-blue-600 text-white p-1.5 rounded-lg flex-shrink-0">
              <Scale size={20} />
            </div>
            {isSidebarOpen && (
              <span className="font-semibold text-lg text-gray-900 tracking-tight whitespace-nowrap">
                LegalEase AI
              </span>
            )}
          </Link>
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="text-gray-400 hover:text-gray-600 transition-colors hidden md:block"
          >
            {isSidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-6 flex flex-col gap-2 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                } ${!isSidebarOpen && 'justify-center'}`
              }
              title={!isSidebarOpen ? item.name : undefined}
            >
              <div className={`${isSidebarOpen ? 'mr-3' : 'mr-0'} flex-shrink-0`}>
                {item.icon}
              </div>
              {isSidebarOpen && <span>{item.name}</span>}
            </NavLink>
          ))}
        </div>

        <div className="p-4 border-t border-gray-100">
          <div className={`flex items-center ${isSidebarOpen ? 'justify-between' : 'justify-center'}`}>
            {isSidebarOpen && (
              <div className="flex items-center min-w-0">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-semibold flex-shrink-0">
                  {user?.full_name?.charAt(0) || 'U'}
                </div>
                <div className="ml-3 truncate">
                  <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
                </div>
              </div>
            )}
            <button
              onClick={logout}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b border-gray-200 sticky top-0 z-20">
          <div className="flex items-center justify-between h-16 px-4">
            <Link to="/" className="flex items-center space-x-2">
              <Scale className="text-blue-600" size={24} />
              <span className="font-semibold text-lg text-gray-900">LegalEase AI</span>
            </Link>
            <button
              onClick={logout}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              <LogOut size={20} />
            </button>
          </div>
          {/* Mobile Navigation (Simple Horizontal Scroll) */}
          <nav className="flex overflow-x-auto py-2 px-4 gap-2 no-scrollbar bg-gray-50 border-t border-gray-100">
             {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                    isActive
                      ? "bg-blue-600 text-white shadow-sm"
                      : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
                  }`
                }
              >
                {item.icon}
                <span className="ml-2">{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </header>

        {/* Content */}
        <main className="flex-1 p-4 md:p-8 lg:p-10 max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
