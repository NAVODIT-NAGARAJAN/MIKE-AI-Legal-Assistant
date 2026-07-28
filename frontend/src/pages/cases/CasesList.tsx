import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { casesApi, CaseListItem } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import {
  PlusCircle,
  Search,
  Trash2,
  Edit,
  FileText,
  ChevronRight,
  Filter,
  X,
} from "lucide-react";
import { toast } from "react-toastify";

import { motion } from "framer-motion";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../../components/ui/alert-dialog";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { formatCategory } from "../../lib/caseUtils";

const STATUS_OPTIONS = ["ALL", "OPEN", "IN_PROGRESS", "REPORT_GENERATED"];

export const CasesList: React.FC = () => {
  const [cases, setCases] = useState<CaseListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const navigate = useNavigate();

  const fetchCases = async () => {
    try {
      setIsLoading(true);
      const data = await casesApi.listCases(0, 100);
      setCases(data.items);
    } catch (err) {
      toast.error("Failed to load cases.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await casesApi.deleteCase(id);
      toast.success("Case deleted successfully");
      fetchCases();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to delete case.");
    }
  };

  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.product_or_service.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const tableVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.04 } },
  };
  const rowVariants = {
    hidden: { opacity: 0, y: 8 },
    show: { opacity: 1, y: 0, transition: { duration: 0.25 } },
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-5 border-b border-[#2A2A2A] pb-7"
      >
        <div className="space-y-1">
          <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
            My Cases
          </h1>
          <p className="text-[#B3B3B3] text-base">
            Manage and track your consumer dispute progress.
          </p>
        </div>
        <Button
          onClick={() => navigate("/cases/new")}
          className="flex items-center gap-2 h-11 px-6 shadow-lg shadow-[#D4AF37]/10 w-full sm:w-auto"
        >
          <PlusCircle className="h-4 w-4" />
          Report New Issue
        </Button>
      </motion.div>

      {/* Search + Filter Bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-3"
      >
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#B3B3B3] h-4 w-4 pointer-events-none" />
          <input
            type="text"
            placeholder="Search by title or product..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-11 pl-10 pr-10 bg-[#1A1A1A] border border-[#2A2A2A] rounded-xl text-white placeholder:text-[#B3B3B3] text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/30 focus:border-[#D4AF37] transition-all duration-200"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#B3B3B3] hover:text-white transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-[#B3B3B3] flex-shrink-0" />
          <div className="flex gap-2 flex-wrap">
            {STATUS_OPTIONS.map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`h-9 px-3 rounded-lg text-xs font-semibold border transition-all duration-200 ${
                  statusFilter === s
                    ? "bg-[#D4AF37] text-black border-[#D4AF37]"
                    : "bg-[#1A1A1A] text-[#B3B3B3] border-[#2A2A2A] hover:border-[#D4AF37]/50 hover:text-white"
                }`}
              >
                {s === "ALL" ? "All" : s.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay: 0.15 }}
      >
        <Card className="border border-[#2A2A2A] bg-[#1A1A1A] rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-[#0A0A0A] border-b border-[#2A2A2A]">
                  <th scope="col" className="px-6 py-4 text-left text-xs font-bold text-[#B3B3B3] uppercase tracking-widest">
                    Case
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-bold text-[#B3B3B3] uppercase tracking-widest hidden sm:table-cell">
                    Category
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-bold text-[#B3B3B3] uppercase tracking-widest">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-4 text-left text-xs font-bold text-[#B3B3B3] uppercase tracking-widest hidden md:table-cell">
                    Reported
                  </th>
                  <th scope="col" className="px-6 py-4 text-right text-xs font-bold text-[#B3B3B3] uppercase tracking-widest">
                    Actions
                  </th>
                </tr>
              </thead>
              <motion.tbody
                className="divide-y divide-[#2A2A2A]"
                variants={tableVariants}
                initial="hidden"
                animate="show"
              >
                {isLoading ? (
                  [1, 2, 3, 4, 5].map((i) => (
                    <tr key={i}>
                      <td className="px-6 py-4">
                        <div className="space-y-2">
                          <div className="skeleton h-4 w-40 rounded" />
                          <div className="skeleton h-3 w-24 rounded" />
                        </div>
                      </td>
                      <td className="px-6 py-4 hidden sm:table-cell">
                        <div className="skeleton h-4 w-28 rounded" />
                      </td>
                      <td className="px-6 py-4">
                        <div className="skeleton h-6 w-20 rounded-full" />
                      </td>
                      <td className="px-6 py-4 hidden md:table-cell">
                        <div className="skeleton h-4 w-24 rounded" />
                      </td>
                      <td className="px-6 py-4" />
                    </tr>
                  ))
                ) : filteredCases.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-20 text-center">
                      <div className="flex flex-col items-center gap-4">
                        <div className="h-14 w-14 rounded-2xl bg-[#111111] border border-[#2A2A2A] flex items-center justify-center">
                          <FileText className="h-6 w-6 text-[#D4AF37]" />
                        </div>
                        <div>
                          <p className="text-white font-semibold text-base">No cases found</p>
                          <p className="text-[#B3B3B3] text-sm mt-1">
                            {searchQuery
                              ? "Try a different search term or clear the filter."
                              : "You haven't reported any issues yet."}
                          </p>
                        </div>
                        {!searchQuery && (
                          <Button
                            onClick={() => navigate("/cases/new")}
                            className="gap-2 h-10 px-6 mt-1"
                          >
                            <PlusCircle className="h-4 w-4" />
                            Report an Issue
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredCases.map((c) => (
                    <motion.tr
                      key={c.id}
                      variants={rowVariants}
                      className="hover:bg-[#111111]/60 transition-colors duration-150 group"
                    >
                      <td className="px-6 py-4">
                        <Link to={`/cases/${c.id}`} className="block">
                          <span className="text-sm font-semibold text-white group-hover:text-[#D4AF37] transition-colors block mb-0.5">
                            {c.title}
                          </span>
                          <span className="text-xs text-[#B3B3B3] sm:hidden">
                            {formatCategory(c.category)}
                          </span>
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap hidden sm:table-cell">
                        <span className="text-sm text-[#B3B3B3]">
                          {formatCategory(c.category)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={c.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap hidden md:table-cell">
                        <span className="text-sm text-[#B3B3B3]">
                          {new Date(c.created_at).toLocaleDateString(undefined, {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          })}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Link
                            to={`/cases/${c.id}`}
                            className="p-2 rounded-lg text-[#B3B3B3] hover:text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-all duration-200 sm:hidden focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40"
                            aria-label={`View details for ${c.title}`}
                          >
                            <ChevronRight className="h-4 w-4" />
                          </Link>
                          <Link
                            to={`/cases/${c.id}/edit`}
                            className="p-2 rounded-lg text-[#B3B3B3] hover:text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40"
                            aria-label={`Edit case ${c.title}`}
                          >
                            <Edit className="h-4 w-4" />
                          </Link>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <button
                                className="p-2 rounded-lg text-[#B3B3B3] hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500/30"
                                aria-label={`Delete case ${c.title}`}
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete this case?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  This action cannot be undone. The case and all associated data will be permanently deleted.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={(e) => handleDelete(c.id, e as any)}>
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </td>
                    </motion.tr>
                  ))
                )}
              </motion.tbody>
            </table>
          </div>
          {!isLoading && filteredCases.length > 0 && (
            <div className="px-6 py-3 border-t border-[#2A2A2A] bg-[#0A0A0A]/40 flex items-center justify-between">
              <span className="text-xs text-[#B3B3B3]">
                Showing <span className="font-medium text-white">{filteredCases.length}</span> of{" "}
                <span className="font-medium text-white">{cases.length}</span> cases
              </span>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
};
