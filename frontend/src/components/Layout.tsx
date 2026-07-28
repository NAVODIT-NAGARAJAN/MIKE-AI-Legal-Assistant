import React, { useState } from "react";
import { Outlet, Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogOut, LayoutDashboard, FileText, MessageCircle, Menu, X } from "lucide-react";
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
    <div className="min-h-screen flex bg-[#0A0A0A]/50">
      {/* Sidebar */}
      <motion.aside
        initial={{ width: 260 }}
        animate={{ width: isSidebarOpen ? 260 : 72 }}
        className="hidden md:flex flex-col bg-[#111111] border-r border-[#2A2A2A] z-10 sticky top-0 h-screen transition-all duration-300 shadow-sm"
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-[#2A2A2A]">
          <Link to="/" className={`flex items-center space-x-3 overflow-hidden ${!isSidebarOpen && 'justify-center'}`}>
            <img src="/mike-logo.png" alt="MIKE Logo" className="h-9 w-9 object-contain flex-shrink-0" />
            {isSidebarOpen && (
              <div className="flex flex-col">
                <span className="font-bold text-lg text-white tracking-wider leading-none">
                  MIKE
                </span>
                <span className="text-[10px] text-[#D4AF37] font-medium tracking-wide mt-0.5">
                  AI Legal Assistant
                </span>
              </div>
            )}
          </Link>
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="flex-shrink-0 p-1 rounded-lg text-[#B3B3B3] hover:text-white hover:bg-[#2A2A2A] transition-all duration-200 hidden md:flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40"
            aria-label={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isSidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-6 flex flex-col gap-2 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `relative flex items-center px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40 ${
                  isActive
                    ? 'bg-[#D4AF37]/10 text-[#D4AF37] shadow-sm'
                    : 'text-[#B3B3B3] hover:bg-[#1A1A1A] hover:text-white'
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

        <div className="p-4 border-t border-[#2A2A2A]">
          <div className={`flex items-center ${isSidebarOpen ? 'justify-between' : 'justify-center'}`}>
            {isSidebarOpen && (
              <div className="flex items-center min-w-0 flex-1">
                <div className="h-9 w-9 rounded-full bg-[#D4AF37] flex items-center justify-center text-black font-bold text-sm flex-shrink-0 shadow-sm">
                  {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="ml-3 truncate">
                  <p className="text-sm font-semibold text-white truncate leading-tight">{user?.full_name}</p>
                  <p className="text-xs text-[#B3B3B3] truncate mt-0.5">{user?.email || 'Consumer'}</p>
                </div>
              </div>
            )}
            <button
              onClick={logout}
              className="p-2 rounded-lg text-[#B3B3B3] hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              title="Logout"
              aria-label="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <header className="md:hidden bg-[#1A1A1A] border-b border-[#2A2A2A] sticky top-0 z-20">
          <div className="flex items-center justify-between h-16 px-4">
            <Link to="/" className="flex items-center space-x-3">
              <img src="/mike-logo.png" alt="MIKE Logo" className="h-8 w-8 object-contain flex-shrink-0" />
              <div className="flex flex-col">
                <span className="font-bold text-base text-white tracking-wider leading-none">MIKE</span>
                <span className="text-[9px] text-[#D4AF37] font-medium tracking-wide mt-0.5">AI Legal Assistant</span>
              </div>
            </Link>
            <button
              onClick={logout}
              className="p-2 rounded-lg text-[#B3B3B3] hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
              aria-label="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
          {/* Mobile Navigation (Simple Horizontal Scroll) */}
          <nav className="flex overflow-x-auto py-2 px-4 gap-2 no-scrollbar bg-[#0A0A0A] border-t border-[#2A2A2A]">
             {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                    isActive
                      ? "bg-[#D4AF37] text-black shadow-sm"
                      : "bg-[#1A1A1A] text-[#B3B3B3] border border-[#2A2A2A] hover:bg-[#0A0A0A]"
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
