import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { casesApi, Case } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../components/ui/Card";
import {
  ArrowLeft,
  Edit,
  Trash2,
  Bot,
  Calendar,
  Store,
  Tag,
  Clock,
  Sparkles,
  FileText
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

export const CaseDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (id) {
      casesApi
        .getCase(id)
        .then(setCaseData)
        .catch(() => {
          toast.error("Failed to load case details.");
          navigate("/cases");
        })
        .finally(() => setIsLoading(false));
    }
  }, [id, navigate]);

  const handleDelete = async () => {
    try {
      await casesApi.deleteCase(id!);
      toast.success("Case deleted successfully");
      navigate("/cases");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to delete case.");
    }
  };

  const handleConsultAI = () => {
    navigate(`/chat?caseId=${id}`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-12 w-12 bg-blue-100 rounded-full mb-4"></div>
          <div className="h-4 w-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return null;
  }



  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4 } }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col md:flex-row md:justify-between md:items-center gap-4"
      >
        <Button
          variant="ghost"
          onClick={() => navigate("/cases")}
          className="px-0 hover:bg-transparent text-gray-500 hover:text-gray-900 w-fit"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Cases
        </Button>

        <div className="flex flex-wrap gap-3">
          <Button
            variant="outline"
            onClick={() => navigate(`/cases/${id}/edit`)}
            className="bg-white"
            aria-label="Edit Case"
          >
            <Edit className="mr-2 h-4 w-4 text-gray-500" />
            Edit Case
          </Button>

          <Button
            onClick={handleConsultAI}
            className="bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-200 transition-all"
          >
            <Bot className="mr-2 h-4 w-4" />
            Consult AI
          </Button>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" className="text-red-600 hover:bg-red-50 hover:text-red-700 hover:border-red-200" aria-label="Delete Case">
                <Trash2 className="h-4 w-4 md:mr-2" />
                <span className="hidden md:inline">Delete</span>
              </Button>
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
                <AlertDialogAction onClick={handleDelete}>Continue</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </motion.div>

      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Main Case Info */}
        <motion.div variants={itemVariants} className="lg:col-span-2 space-y-6">
          <Card className="border-gray-200 shadow-sm bg-white overflow-hidden h-full">
            <CardHeader className="bg-gray-50/50 border-b border-gray-100 pb-5 pt-6">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
                <div className="space-y-1">
                  <span className="text-xs font-semibold text-blue-600 tracking-wider uppercase">Issue Details</span>
                  <CardTitle className="text-2xl font-bold text-gray-900 leading-tight">
                    {caseData.title}
                  </CardTitle>
                </div>
                <StatusBadge status={caseData.status} />
              </div>
            </CardHeader>

            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2 border-b border-gray-100 pb-2">
                  <FileText className="w-4 h-4 text-gray-400" />
                  <span>Description</span>
                </div>
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed text-sm bg-gray-50/50 p-5 rounded-xl border border-gray-100">
                  {caseData.description}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Sidebar Metadata */}
        <motion.div variants={itemVariants} className="space-y-6">
          <Card className="border-gray-200 shadow-sm bg-white">
            <CardHeader className="pb-3 border-b border-gray-100">
              <CardTitle className="text-sm font-semibold text-gray-900 uppercase tracking-wider flex items-center">
                <Tag className="w-4 h-4 mr-2 text-gray-400" />
                Metadata
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-5 space-y-5">
              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Category</dt>
                <dd className="text-sm font-medium text-gray-900 bg-gray-50 px-3 py-2 rounded-lg border border-gray-100 inline-block">
                  {formatCategory(caseData.category)}
                </dd>
              </div>

              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1 flex items-center">
                  <Store className="w-3.5 h-3.5 mr-1.5" /> Product / Service
                </dt>
                <dd className="text-sm text-gray-900">
                  {caseData.product_or_service}
                </dd>
              </div>

              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1 flex items-center">
                  <Store className="w-3.5 h-3.5 mr-1.5" /> Seller / Provider
                </dt>
                <dd className="text-sm text-gray-900">
                  {caseData.seller_name || <span className="text-gray-400 italic">Not specified</span>}
                </dd>
              </div>

              <div>
                <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1 flex items-center">
                  <Calendar className="w-3.5 h-3.5 mr-1.5" /> Purchase Date
                </dt>
                <dd className="text-sm text-gray-900">
                  {caseData.purchase_date || <span className="text-gray-400 italic">Not specified</span>}
                </dd>
              </div>
              
              <div className="pt-4 border-t border-gray-100">
                <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1 flex items-center">
                  <Clock className="w-3.5 h-3.5 mr-1.5" /> Timeline
                </dt>
                <dd className="text-sm text-gray-600 space-y-1">
                  <div>Reported: <span className="font-medium text-gray-900">{new Date(caseData.created_at).toLocaleDateString()}</span></div>
                  <div>Updated: <span className="font-medium text-gray-900">{new Date(caseData.updated_at).toLocaleDateString()}</span></div>
                </dd>
              </div>
            </CardContent>
          </Card>

          {/* AI Action Card */}
          <Card className="border-blue-200 shadow-md bg-gradient-to-br from-blue-50 via-white to-blue-50 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Sparkles className="w-24 h-24 text-blue-600" />
            </div>
            <CardContent className="p-6 relative z-10">
              <h4 className="text-base font-bold text-blue-900 mb-2 flex items-center">
                <Bot className="w-5 h-5 mr-2 text-blue-600" />
                AI Agent Status
              </h4>
              <p className="text-sm text-blue-700/80 mb-6 leading-relaxed">
                {caseData.status === "OPEN"
                  ? "The AI is ready to consult with you on this case to determine your rights and options."
                  : "Consultation data is actively being managed by the AI."}
              </p>
              
              {caseData.status === "REPORT_GENERATED" ? (
                <Button 
                  onClick={() => navigate(`/cases/${id}/roadmap`)}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                >
                  View Resolution Roadmap
                </Button>
              ) : (
                <Button 
                  onClick={handleConsultAI}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                >
                  Start Consultation
                </Button>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
};