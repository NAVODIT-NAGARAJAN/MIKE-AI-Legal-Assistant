import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { casesApi, CaseListItem } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import { Card, CardContent, CardHeader } from "../../components/ui/Card";
import { PlusCircle, Search, Trash2, Edit, FileText, ChevronRight } from "lucide-react";
import { toast } from "react-toastify";
import { Input } from "../../components/ui/Input";
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

export const CasesList: React.FC = () => {
  const [cases, setCases] = useState<CaseListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
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

  const filteredCases = cases.filter(c => 
    c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.product_or_service.toLowerCase().includes(searchQuery.toLowerCase())
  );



  const tableVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  };

  const rowVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0, transition: { duration: 0.3 } }
  };

  return (
    <div className="space-y-8">
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0 border-b border-gray-200 pb-6"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">My Cases</h1>
          <p className="mt-2 text-gray-500">Manage and track the progress of your consumer disputes.</p>
        </div>
        <Button onClick={() => navigate("/cases/new")} className="flex items-center shadow-sm">
          <PlusCircle className="mr-2 h-4 w-4" />
          Report New Issue
        </Button>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
        <Card className="border-gray-200 shadow-sm overflow-hidden bg-white">
          <CardHeader className="bg-gray-50/50 border-b border-gray-100 py-4 px-6">
            <div className="relative max-w-md w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                id="search"
                label=""
                placeholder="Search cases by title or product..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 h-10 bg-white border-gray-200 text-sm focus:border-blue-500 focus:ring-blue-500 transition-colors"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Case Details</th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider hidden sm:table-cell">Category</th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider hidden md:table-cell">Date Reported</th>
                    <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <motion.tbody 
                  className="bg-white divide-y divide-gray-100"
                  variants={tableVariants}
                  initial="hidden"
                  animate="show"
                >
                  {isLoading ? (
                    <tr><td colSpan={5} className="px-6 py-12 text-center text-sm text-gray-500 animate-pulse">Loading cases...</td></tr>
                  ) : filteredCases.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-16 text-center">
                        <div className="flex flex-col items-center justify-center">
                          <FileText className="h-12 w-12 text-gray-300 mb-4" />
                          <p className="text-gray-500 text-lg">No cases found.</p>
                          {searchQuery && <p className="text-gray-400 text-sm mt-1">Try adjusting your search query.</p>}
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filteredCases.map(c => (
                      <motion.tr key={c.id} variants={rowVariants} className="hover:bg-blue-50/50 transition-colors group cursor-default">
                        <td className="px-6 py-4">
                          <Link to={`/cases/${c.id}`} className="block">
                            <span className="text-sm font-semibold text-gray-900 group-hover:text-blue-700 transition-colors block mb-1">
                              {c.title}
                            </span>
                            <span className="text-xs text-gray-500 sm:hidden">
                              {formatCategory(c.category)}
                            </span>
                          </Link>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 hidden sm:table-cell">
                          {formatCategory(c.category)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <StatusBadge status={c.status} />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">
                          {new Date(c.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            <Link 
                              to={`/cases/${c.id}`} 
                              className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors sm:hidden"
                              title="View Details"
                              aria-label={`View details for ${c.title}`}
                            >
                              <ChevronRight className="h-4 w-4" />
                            </Link>
                            <Link 
                              to={`/cases/${c.id}/edit`} 
                              className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                              title="Edit Case"
                              aria-label={`Edit case ${c.title}`}
                            >
                              <Edit className="h-4 w-4" />
                            </Link>
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <button 
                                  className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                                  title="Delete Case"
                                  aria-label={`Delete case ${c.title}`}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    This action cannot be undone. This will permanently delete your case.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction onClick={(e) => handleDelete(c.id, e as any)}>Continue</AlertDialogAction>
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
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
