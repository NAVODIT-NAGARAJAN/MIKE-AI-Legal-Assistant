import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { casesApi, Case } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card";
import {
  ArrowLeft, Edit, Trash2, Bot, Calendar, Store, Tag,
  Clock, Sparkles, FileText, MapPin,
} from "lucide-react";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader,
  AlertDialogTitle, AlertDialogTrigger,
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
      casesApi.getCase(id)
        .then(setCaseData)
        .catch(() => { toast.error("Failed to load case details."); navigate("/cases"); })
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

  const handleConsultAI = () => navigate(`/chat?caseId=${id}`);

  if (isLoading) {
    return (
      <div className="space-y-8 max-w-5xl mx-auto">
        <div className="skeleton h-9 w-32 rounded-xl" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 skeleton h-80 rounded-2xl" />
          <div className="space-y-6">
            <div className="skeleton h-56 rounded-2xl" />
            <div className="skeleton h-40 rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  if (!caseData) return null;

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  const metaItems = [
    { icon: <Tag className="w-4 h-4 text-[#D4AF37]" />, label: "Category", value: formatCategory(caseData.category) },
    { icon: <Store className="w-4 h-4 text-[#D4AF37]" />, label: "Product / Service", value: caseData.product_or_service },
    { icon: <MapPin className="w-4 h-4 text-[#D4AF37]" />, label: "Seller / Provider", value: caseData.seller_name || "Not specified", muted: !caseData.seller_name },
    { icon: <Calendar className="w-4 h-4 text-[#D4AF37]" />, label: "Purchase Date", value: caseData.purchase_date || "Not specified", muted: !caseData.purchase_date },
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Topbar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4"
      >
        <Button
          variant="ghost"
          onClick={() => navigate("/cases")}
          className="px-0 hover:bg-transparent text-[#B3B3B3] hover:text-white w-fit gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Cases
        </Button>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={() => navigate(`/cases/${id}/edit`)}
            className="bg-[#1A1A1A] gap-2 h-10"
            aria-label="Edit Case"
          >
            <Edit className="h-4 w-4 text-[#B3B3B3]" />
            Edit
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="outline"
                className="gap-2 h-10 border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300 hover:border-red-500/50"
                aria-label="Delete Case"
              >
                <Trash2 className="h-4 w-4" />
                <span className="hidden sm:inline">Delete</span>
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this case?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. The case and all associated AI consultation data will be permanently deleted.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
          <Button
            onClick={handleConsultAI}
            className="gap-2 h-10 px-5 shadow-md shadow-[#D4AF37]/15"
          >
            <Bot className="h-4 w-4" />
            Consult AI
          </Button>
        </div>
      </motion.div>

      {/* Content Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Main Card */}
        <motion.div variants={itemVariants} className="lg:col-span-2 space-y-6">
          <Card className="border border-[#2A2A2A] bg-[#1A1A1A] rounded-2xl overflow-hidden shadow-sm">
            <CardHeader className="bg-[#0A0A0A]/60 border-b border-[#2A2A2A] px-6 pt-6 pb-5">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
                <div className="space-y-1.5">
                  <span className="text-xs font-bold text-[#D4AF37] tracking-widest uppercase">
                    Issue Details
                  </span>
                  <CardTitle className="text-2xl font-bold text-white leading-tight">
                    {caseData.title}
                  </CardTitle>
                </div>
                <StatusBadge status={caseData.status} />
              </div>
            </CardHeader>
            <CardContent className="px-6 pt-6 pb-6">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-[#B3B3B3] pb-3 border-b border-[#2A2A2A]">
                  <FileText className="w-4 h-4 text-[#D4AF37]" />
                  Description
                </div>
                <p className="text-[#B3B3B3] whitespace-pre-wrap leading-relaxed text-sm bg-[#0A0A0A]/50 p-5 rounded-xl border border-[#2A2A2A]">
                  {caseData.description}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Right Column */}
        <motion.div variants={itemVariants} className="space-y-5">
          {/* Metadata */}
          <Card className="border border-[#2A2A2A] bg-[#1A1A1A] rounded-2xl overflow-hidden shadow-sm">
            <CardHeader className="px-5 pt-5 pb-4 border-b border-[#2A2A2A]">
              <CardTitle className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Tag className="w-4 h-4 text-[#D4AF37]" />
                Metadata
              </CardTitle>
            </CardHeader>
            <CardContent className="px-5 pt-4 pb-5 space-y-4">
              {metaItems.map((item, i) => (
                <div key={i} className="space-y-1">
                  <dt className="flex items-center gap-1.5 text-xs font-semibold text-[#B3B3B3] uppercase tracking-wider">
                    {item.icon}
                    {item.label}
                  </dt>
                  <dd className={`text-sm pl-5 ${item.muted ? "text-[#B3B3B3] italic" : "text-white font-medium"}`}>
                    {item.value}
                  </dd>
                </div>
              ))}
              <div className="pt-4 border-t border-[#2A2A2A] space-y-1">
                <dt className="flex items-center gap-1.5 text-xs font-semibold text-[#B3B3B3] uppercase tracking-wider">
                  <Clock className="w-4 h-4 text-[#D4AF37]" />
                  Timeline
                </dt>
                <dd className="text-sm pl-5 space-y-1">
                  <div className="text-[#B3B3B3]">
                    Reported:{" "}
                    <span className="font-medium text-white">
                      {new Date(caseData.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
                    </span>
                  </div>
                  <div className="text-[#B3B3B3]">
                    Updated:{" "}
                    <span className="font-medium text-white">
                      {new Date(caseData.updated_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
                    </span>
                  </div>
                </dd>
              </div>
            </CardContent>
          </Card>

          {/* AI Action Card */}
          <Card className="border border-[#D4AF37]/30 bg-gradient-to-br from-[#1A1A1A] via-[#111111] to-[#0A0A0A] rounded-2xl overflow-hidden relative shadow-md shadow-[#D4AF37]/5">
            <div className="absolute top-0 right-0 p-5 opacity-10 pointer-events-none">
              <Sparkles className="w-20 h-20 text-[#D4AF37]" />
            </div>
            <CardContent className="px-5 pt-5 pb-5 relative z-10">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-8 w-8 rounded-lg bg-[#D4AF37]/15 border border-[#D4AF37]/20 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-[#D4AF37]" />
                </div>
                <h4 className="text-base font-bold text-white">AI Agent</h4>
              </div>
              <p className="text-sm text-[#B3B3B3] mb-5 leading-relaxed">
                {caseData.status === "REPORT_GENERATED"
                  ? "Your personalized resolution roadmap has been generated and is ready to view."
                  : "MIKE is ready to analyze your case, identify your legal rights, and create a personalized resolution roadmap."}
              </p>
              {caseData.status === "REPORT_GENERATED" ? (
                <Button
                  onClick={() => navigate(`/cases/${id}/roadmap`)}
                  className="w-full h-10 shadow-sm gap-2"
                >
                  <FileText className="h-4 w-4" />
                  View Roadmap
                </Button>
              ) : (
                <Button
                  onClick={handleConsultAI}
                  className="w-full h-10 shadow-sm gap-2"
                >
                  <Bot className="h-4 w-4" />
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