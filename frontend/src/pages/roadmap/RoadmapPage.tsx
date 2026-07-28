import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { reportsApi, Report } from "../../api/reports";
import { casesApi, Case } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import { toast } from "react-toastify";
import { 
  ArrowLeft, Download, Printer, CheckCircle, Circle, AlertCircle, 
  BookOpen, FileText, Scale, Loader2, ChevronDown, ChevronUp, Clock
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const RoadmapPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [report, setReport] = useState<Report | null>(null);
  const [caseInfo, setCaseInfo] = useState<Case | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedStep, setExpandedStep] = useState<number | null>(0);

  useEffect(() => {
    if (!id) return;
    
    setIsLoading(true);
    Promise.all([
      casesApi.getCase(id),
      reportsApi.getReport(id)
    ])
    .then(([caseData, reportData]) => {
      setCaseInfo(caseData);
      setReport(reportData);
    })
    .catch((err) => {
      if (err.response?.status === 404) {
        toast.info("Report not generated yet for this case.");
      } else {
        toast.error("Failed to load roadmap data.");
      }
    })
    .finally(() => {
      setIsLoading(false);
    });
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    if (!id) return;
    window.open(reportsApi.downloadPdfUrl(id), "_blank");
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="relative">
          <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        </div>
        <p className="text-gray-500 text-sm">Loading your personalized resolution roadmap...</p>
      </div>
    );
  }

  if (!report || !caseInfo) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl mx-auto py-16 text-center"
      >
        <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-6">
          <AlertCircle className="h-8 w-8 text-yellow-500" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-3">Roadmap Not Available</h2>
        <p className="text-gray-500 mb-8 leading-relaxed">
          A resolution roadmap has not been generated for this case yet. Please complete the AI consultation first.
        </p>
        <Button onClick={() => navigate(`/cases/${id}`)} className="shadow-sm">
          Return to Case Details
        </Button>
      </motion.div>
    );
  }

  const completedStepsCount = report.roadmap_steps.filter(s => s.is_done).length;
  const totalSteps = report.roadmap_steps.length;
  const progressPercentage = totalSteps === 0 ? 0 : Math.round((completedStepsCount / totalSteps) * 100);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.12 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 24 },
    show: { opacity: 1, y: 0, transition: { duration: 0.45 } }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      {/* Header / Actions */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0 print:hidden"
      >
        <Button variant="ghost" onClick={() => navigate(`/cases/${id}`)} className="px-0 text-gray-500 hover:text-gray-900 hover:bg-transparent w-fit">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Case Details
        </Button>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={handlePrint} className="bg-white shadow-sm">
            <Printer className="mr-2 h-4 w-4" />
            Print
          </Button>
          <Button onClick={handleDownload} className="shadow-sm">
            <Download className="mr-2 h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </motion.div>

      {/* Main Report Container */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="bg-white rounded-2xl shadow-md border border-gray-200 overflow-hidden print:shadow-none print:border-none"
      >
        {/* Gradient Hero Cover */}
        <div className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-blue-700 text-white p-10 sm:p-14 text-center overflow-hidden">
          <div className="absolute inset-0 opacity-10"
            style={{ backgroundImage: 'radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 20%, white 1px, transparent 1px)', backgroundSize: '40px 40px' }}
          />
          <div className="relative z-10">
            <div className="inline-flex items-center justify-center p-4 bg-white/15 rounded-2xl mb-5 backdrop-blur-sm">
              <Scale className="h-9 w-9 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold mb-3">Resolution Roadmap</h1>
            <p className="text-blue-100 max-w-xl mx-auto text-base leading-relaxed">
              Personalized legal guidance and step-by-step action plan for your consumer issue.
            </p>
            <div className="mt-6 inline-flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-full text-sm font-medium border border-white/20">
              <span className="text-white/80">Generated for:</span>
              <span className="text-white font-semibold">{caseInfo.title}</span>
            </div>
          </div>
        </div>

        <div className="p-6 sm:p-10 space-y-14">

          {/* Section 1: Case Overview */}
          <motion.section variants={itemVariants}>
            <div className="flex items-center mb-5">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Case Overview</h2>
            </div>
            <div className="bg-gray-50/70 rounded-2xl p-6 border border-gray-100">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                <div className="col-span-2 md:col-span-1">
                  <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Case ID</span>
                  <span className="block text-sm text-gray-800 font-mono bg-gray-200 px-2 py-1 rounded inline-block">{caseInfo.id.split("-")[0]}...</span>
                </div>
                <div className="col-span-2 md:col-span-1">
                  <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Product / Service</span>
                  <span className="block text-sm font-medium text-gray-900">{caseInfo.product_or_service}</span>
                </div>
                <div className="col-span-2 md:col-span-1">
                  <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Target Authority</span>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200 mt-1">
                    {report.recommended_authority}
                  </span>
                </div>
                <div className="col-span-2 md:col-span-1">
                  <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Generated On</span>
                  <span className="block text-sm font-medium text-gray-900">{new Date(report.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                </div>
              </div>
              <div className="pt-5 border-t border-gray-200">
                <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">AI Analysis Summary</span>
                <p className="text-gray-700 text-sm leading-relaxed">{report.case_summary}</p>
              </div>
            </div>
          </motion.section>

          {/* Section 2: Consumer Rights */}
          <motion.section variants={itemVariants}>
            <div className="flex items-center mb-5">
              <div className="p-2 bg-indigo-100 rounded-lg mr-3">
                <BookOpen className="h-5 w-5 text-indigo-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Your Consumer Rights</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.consumer_rights.map((right, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.07, duration: 0.35 }}
                  className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all group"
                >
                  <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-indigo-700 transition-colors">{right.right}</h3>
                  <p className="text-sm text-gray-600 mb-4 leading-relaxed">{right.description}</p>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono bg-indigo-50 text-indigo-700 py-1 px-2.5 rounded-md border border-indigo-100 inline-block">
                      {right.legal_citation}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Section 3: Resolution Roadmap */}
          <motion.section variants={itemVariants}>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg mr-3">
                  <Clock className="h-5 w-5 text-green-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Action Plan Timeline</h2>
              </div>
              <div className="flex items-center space-x-2 bg-blue-50 px-4 py-1.5 rounded-full border border-blue-100">
                <span className="text-sm font-bold text-blue-800">{progressPercentage}%</span>
                <span className="text-sm text-blue-600 hidden sm:inline">Complete</span>
              </div>
            </div>

            {/* Animated Progress Bar */}
            <div className="w-full bg-gray-100 rounded-full h-2.5 mb-8 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progressPercentage}%` }}
                transition={{ duration: 1.2, ease: "easeOut", delay: 0.4 }}
                className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2.5 rounded-full"
              />
            </div>

            <div className="space-y-3">
              {report.roadmap_steps.map((step, idx) => {
                const isExpanded = expandedStep === idx;
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.06, duration: 0.35 }}
                    className={`border rounded-xl overflow-hidden transition-all duration-200 ${step.is_done ? "border-green-200 bg-green-50/40" : "border-gray-200 bg-white hover:border-gray-300"}`}
                  >
                    <button
                      onClick={() => setExpandedStep(isExpanded ? null : idx)}
                      className="w-full flex items-center justify-between p-4 sm:p-5 text-left focus:outline-none"
                      aria-expanded={isExpanded}
                      aria-controls={`step-content-${idx}`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`flex-shrink-0 flex items-center justify-center h-9 w-9 rounded-full text-sm font-bold transition-all ${step.is_done ? "bg-green-500 text-white border-2 border-green-500" : "bg-white border-2 border-gray-300 text-gray-500"}`}>
                          {step.is_done ? <CheckCircle className="h-5 w-5" /> : <span>{step.step_number}</span>}
                        </div>
                        <div className="text-left">
                          <h3 className={`font-semibold text-base ${step.is_done ? "text-green-800" : "text-gray-900"}`}>
                            {step.title}
                          </h3>
                          {!isExpanded && (
                            <p className="text-xs text-gray-400 mt-0.5 hidden sm:block">Click to expand</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-400 flex-shrink-0 ml-4">
                        {step.is_done && <span className="text-xs font-bold text-green-600 uppercase tracking-wider hidden sm:inline-block">Done</span>}
                        <div className={`p-1 rounded-md transition-colors ${isExpanded ? 'bg-gray-100' : 'hover:bg-gray-100'}`}>
                          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </div>
                      </div>
                    </button>
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.25 }}
                          className="overflow-hidden"
                          id={`step-content-${idx}`}
                          role="region"
                        >
                          <div className="px-5 pb-5 pt-1 pl-[4.25rem] border-t border-gray-100">
                            <p className="text-gray-600 text-sm leading-relaxed">{step.description}</p>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          </motion.section>

          {/* Section 4: Evidence Checklist */}
          <motion.section variants={itemVariants}>
            <div className="flex items-center mb-4">
              <div className="p-2 bg-orange-100 rounded-lg mr-3">
                <CheckCircle className="h-5 w-5 text-orange-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Evidence Checklist</h2>
            </div>
            <p className="text-sm text-gray-500 mb-6 leading-relaxed">
              Gather these documents to strengthen your consumer case. Uploaded documents can be managed in the case details page.
            </p>
            
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
              <ul className="divide-y divide-gray-100">
                {report.evidence_items.map((item, idx) => (
                  <motion.li
                    key={idx}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="p-4 sm:px-6 sm:py-4 hover:bg-gray-50 transition-colors flex items-start space-x-4"
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      {item.is_required ? (
                        <div className="h-5 w-5 rounded-full border-2 border-orange-400 bg-orange-50" />
                      ) : (
                        <Circle className="h-5 w-5 text-gray-300" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                        <h4 className="text-sm font-semibold text-gray-900">{item.item}</h4>
                        {item.is_required ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold bg-red-50 text-red-700 border border-red-100 whitespace-nowrap w-fit">
                            Required
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold bg-gray-100 text-gray-600 border border-gray-200 whitespace-nowrap w-fit">
                            Optional
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-gray-500 leading-relaxed">{item.description}</p>
                    </div>
                  </motion.li>
                ))}
              </ul>
            </div>
          </motion.section>

          {/* Section 5: Immediate Next Steps CTA */}
          <motion.section
            variants={itemVariants}
            className="relative bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-8 sm:p-10 text-center overflow-hidden"
          >
            <div className="absolute inset-0 opacity-10"
              style={{ backgroundImage: 'radial-gradient(circle at 80% 20%, white 1px, transparent 1px)', backgroundSize: '30px 30px' }}
            />
            <div className="relative z-10">
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-3">Immediate Next Actions</h2>
              <p className="text-blue-100 max-w-2xl mx-auto mb-8 leading-relaxed text-sm sm:text-base">
                {report.next_steps}
              </p>
              <Button
                onClick={() => navigate(`/cases/${id}`)}
                className="bg-white text-blue-700 hover:bg-blue-50 font-semibold shadow-lg shadow-blue-900/20"
              >
                Manage Case &amp; Evidence
              </Button>
            </div>
          </motion.section>

        </div>
      </motion.div>
    </div>
  );
};

