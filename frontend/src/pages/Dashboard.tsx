import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { casesApi, Case } from "../api/cases";
import { Button } from "../components/ui/Button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "../components/ui/Card";
import { StatusBadge } from "../components/ui/StatusBadge";
import {
  PlusCircle,
  FileText,
  ChevronRight,
  Clock,
  Tag
} from "lucide-react";
import { toast } from "react-toastify";
import { motion } from "framer-motion";

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const data = await casesApi.listCases();
        setCases(data.items as unknown as Case[]);
      } catch (err) {
        toast.error("Failed to load your cases.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCases();
  }, []);



  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4 } }
  };

  return (
    <div className="space-y-8">
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 border-b border-gray-200 pb-6"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Dashboard
          </h1>
          <p className="mt-2 text-gray-500 max-w-2xl">
            Welcome back, <span className="font-medium text-gray-700">{user?.full_name}</span>. 
            Here is an overview of your consumer cases and their current status.
          </p>
        </div>

        <Button onClick={() => navigate("/cases/new")} className="flex items-center w-full md:w-auto shadow-sm hover:shadow-md transition-all">
          <PlusCircle className="mr-2 h-4 w-4" />
          New Case
        </Button>
      </motion.div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse border-gray-100 shadow-sm rounded-xl overflow-hidden">
              <CardHeader className="h-16 bg-gray-50 border-b border-gray-100" />
              <CardContent className="h-32 bg-white" />
              <CardFooter className="h-14 bg-gray-50 border-t border-gray-100" />
            </Card>
          ))}
        </div>
      ) : cases.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="text-center py-16 glass-panel rounded-2xl border-dashed border-2 border-gray-200">
            <CardContent className="flex flex-col items-center justify-center">
              <div className="h-16 w-16 text-blue-500 mb-6 bg-blue-50 rounded-2xl flex items-center justify-center shadow-sm">
                <FileText className="h-8 w-8" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No active cases
              </h3>
              <p className="text-gray-500 max-w-sm mb-8">
                You haven't reported any consumer issues yet. Start by describing your situation and our AI will guide you.
              </p>
              <Button onClick={() => navigate("/cases/new")} className="shadow-md">
                <PlusCircle className="mr-2 h-5 w-5" />
                Report New Issue
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
        >
          {cases.map((c) => (
            <motion.div key={c.id} variants={itemVariants}>
              <Card className="h-full hover:shadow-lg transition-all duration-300 flex flex-col group rounded-xl border-gray-200 bg-white overflow-hidden">
                <CardHeader className="flex flex-row justify-between items-start bg-gray-50/50 border-b border-gray-100 pb-4">
                  <div className="flex-1 pr-4">
                    <CardTitle className="text-lg font-semibold text-gray-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                      {c.title}
                    </CardTitle>
                  </div>
                  <StatusBadge status={c.status} className="flex-shrink-0" />
                </CardHeader>

                <CardContent className="flex-1 pt-5">
                  <p className="text-sm text-gray-600 mb-6 line-clamp-3 leading-relaxed">
                    {c.description}
                  </p>

                  <div className="flex flex-col space-y-3 mt-auto">
                    <div className="flex items-center text-xs text-gray-500 bg-gray-50 p-2 rounded-lg">
                      <Tag className="w-3.5 h-3.5 mr-2 text-gray-400" />
                      <span className="font-medium text-gray-700 truncate">{c.product_or_service}</span>
                    </div>
                    <div className="flex items-center text-xs text-gray-500">
                      <Clock className="w-3.5 h-3.5 mr-2 text-gray-400" />
                      Reported: <span className="font-medium text-gray-700 ml-1">{new Date(c.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                    </div>
                  </div>
                </CardContent>

                <CardFooter className="pt-4 pb-4 border-t border-gray-100 bg-gray-50/30 flex justify-end">
                  <Link
                    to={`/cases/${c.id}`}
                    className="text-sm text-blue-600 hover:text-blue-800 font-semibold flex items-center group/btn"
                  >
                    View Details
                    <ChevronRight className="ml-1 w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                  </Link>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};