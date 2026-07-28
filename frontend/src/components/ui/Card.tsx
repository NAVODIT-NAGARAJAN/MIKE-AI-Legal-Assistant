import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Card: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div
      className={`bg-[#1A1A1A] rounded-xl border border-[#2A2A2A] shadow-sm overflow-hidden ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`px-6 py-5 border-b border-[#2A2A2A] bg-[#0A0A0A]/50 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className = "", children, ...props }) => {
  return (
    <h3 className={`text-lg font-semibold text-white ${className}`} {...props}>
      {children}
    </h3>
  );
};

export const CardContent: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`p-6 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`px-6 py-4 bg-[#0A0A0A] border-t border-[#2A2A2A] ${className}`} {...props}>
      {children}
    </div>
  );
};
