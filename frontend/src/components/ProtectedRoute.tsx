import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#0A0A0A] space-y-8">
        {/* Logo */}
        <div className="flex flex-col items-center space-y-3">
          <img
            src="/mike-logo.png"
            alt="MIKE Logo"
            className="h-20 w-20 object-contain animate-pulse"
          />
          <div className="flex flex-col items-center">
            <span className="text-white text-2xl font-extrabold tracking-widest leading-tight">MIKE</span>
            <span className="text-xs text-[#D4AF37] font-semibold tracking-widest mt-0.5">AI Legal Assistant</span>
          </div>
        </div>
        {/* Spinner */}
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[#D4AF37]"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
