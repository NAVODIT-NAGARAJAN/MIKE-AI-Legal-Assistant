import React from "react";
import { Loader2 } from "lucide-react";

type ButtonVariant = "default" | "outline" | "ghost" | "danger";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: "default" | "sm" | "lg" | "icon" | string;
  asChild?: boolean;
  isLoading?: boolean;
  children?: React.ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  default:
    "bg-[#D4AF37] text-black border border-transparent hover:bg-[#F4C542] focus:ring-[#D4AF37] shadow-sm",
  outline:
    "bg-[#1A1A1A] text-white border border-[#D4AF37] hover:bg-[#D4AF37]/10 focus:ring-[#D4AF37]",
  ghost:
    "bg-transparent text-[#B3B3B3] border border-transparent hover:bg-[#111111] hover:text-white focus:ring-gray-400",
  danger:
    "bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 focus:ring-red-500",
};

export const Button: React.FC<ButtonProps> = ({
  variant = "default",
  size,
  asChild,
  isLoading = false,
  disabled,
  className = "",
  children,
  ...props
}) => {
  const base =
    "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

  return (
    <button
      disabled={disabled || isLoading}
      className={`${base} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
};

export { Button as default };
