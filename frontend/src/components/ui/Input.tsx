import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  id: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, id, className = "", ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-[#B3B3B3] mb-2">
            {label}
            {props.required && <span className="text-red-500 ml-0.5">*</span>}
          </label>
        )}
        <div className="relative">
          <input
            id={id}
            ref={ref}
            className={`
              block w-full px-4 py-2.5 border rounded-xl shadow-sm 
              focus:outline-none focus:ring-2 focus:ring-offset-0 sm:text-sm transition-colors duration-200
              ${
                error
                  ? "border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500"
                  : "border-[#2A2A2A] bg-[#0A0A0A]/50 placeholder-gray-400 focus:ring-[#D4AF37] focus:border-[#D4AF37] focus:bg-[#1A1A1A]"
              }
              ${className}
            `}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-red-600" id={`${id}-error`}>
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

