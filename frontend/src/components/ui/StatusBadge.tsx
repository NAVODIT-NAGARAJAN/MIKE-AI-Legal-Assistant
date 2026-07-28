import React from "react";
import { getStatusColor, formatStatus } from "../../lib/caseUtils";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = "" }) => {
  return (
    <span
      className={`px-2.5 py-1 inline-flex text-[11px] leading-4 font-semibold rounded-md border tracking-wide whitespace-nowrap ${getStatusColor(
        status
      )} ${className}`}
    >
      {formatStatus(status)}
    </span>
  );
};
