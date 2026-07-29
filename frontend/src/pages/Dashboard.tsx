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
  Tag,
  Briefcase,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
  ArrowUpRight,
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

  const firstName = user?.full_name?.split(" ")[0] ?? "there";

  const totalCases = cases.length;
  const openCases = cases.filter((c) => c.status === "OPEN").length;
  const resolvedCases = cases.filter(
    (c) => c.status === "REPORT_GENERATED"
  ).length;
  const inProgressCases = cases.filter(
    (c) => c.status === "IN_PROGRESS"
  ).length;

  const stats = [
    {
      label: "Total Cases",
      value: totalCases,
      icon: <Briefcase className="h-5 w-5" />,
      sub: "All reported issues",
    },
    {
      label: "Open",
      value: openCases,
      icon: <AlertCircle className="h-5 w-5" />,
      sub: "Awaiting consultation",
    },
    {
      label: "In Progress",
      value: inProgressCases,
      icon: <Loader2 className="h-5 w-5" />,
      sub: "AI actively working",
    },
    {
      label: "Reports Ready",
      value: resolvedCases,
      icon: <CheckCircle className="h-5 w-5" />,
      sub: "Roadmap generated",
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.08 } },
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 16 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  return (
    <div className="space-y-10">
      {/* Greeting Header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col md:flex-row md:justify-between md:items-end gap-6 border-b border-[#2A2A2A] pb-8"
      >
        <div className="space-y-1">
          <p className="text-sm text-[#D4AF37] font-semibold tracking-wide uppercase mb-1">
            Overview
          </p>
          <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight flex items-center gap-2">
            Hi, {firstName} <span className="animate-wave origin-bottom-right inline-block">👋</span>
          </h1>
          <p className="text-[#B3B3B3] text-base max-w-xl leading-relaxed mt-2">
            Here's a quick look at your consumer rights cases and AI consultation status. MIKE is ready to assist you.
          </p>
        </div>
        <Button
          onClick={() => navigate("/cases/new")}
          className="flex items-center gap-2 w-full md:w-auto h-11 px-6 shadow-lg shadow-[#D4AF37]/10"
        >
          <PlusCircle className="h-4 w-4" />
          New Case
        </Button>
      </motion.div>

      {/* Stats Row */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-2 xl:grid-cols-4 gap-4"
      >
        {isLoading
          ? [1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="skeleton h-28 rounded-2xl"
              />
            ))
          : stats.map((s, i) => (
              <motion.div key={i} variants={itemVariants}>
                <Card className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-2xl hover:border-[#D4AF37]/30 hover:shadow-lg hover:shadow-[#D4AF37]/5 transition-all duration-300 overflow-hidden">
                  <CardContent className="p-5 flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <div className="h-9 w-9 rounded-xl bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37]">
                        {s.icon}
                      </div>
                      <span className="text-3xl font-bold text-white tabular-nums">
                        {s.value}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">
                        {s.label}
                      </p>
                      <p className="text-xs text-[#B3B3B3] mt-0.5">{s.sub}</p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
      </motion.div>

      {/* Cases Section */}
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white tracking-tight">
            Recent Cases
          </h2>
          {cases.length > 0 && (
            <Link
              to="/cases"
              className="flex items-center gap-1 text-sm text-[#D4AF37] hover:text-[#F4C542] font-medium transition-colors"
            >
              View all
              <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          )}
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="rounded-2xl overflow-hidden border border-[#2A2A2A] bg-[#1A1A1A]">
                <div className="skeleton h-16 rounded-none" />
                <div className="p-5 space-y-3">
                  <div className="skeleton h-4 w-3/4" />
                  <div className="skeleton h-3 w-full" />
                  <div className="skeleton h-3 w-2/3" />
                  <div className="skeleton h-9 mt-4 w-full rounded-lg" />
                </div>
              </div>
            ))}
          </div>
        ) : cases.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <Card className="text-center py-20 bg-[#1A1A1A] border-2 border-dashed border-[#2A2A2A] rounded-2xl">
              <CardContent className="flex flex-col items-center gap-5">
                <div className="relative">
                  <div className="h-20 w-20 rounded-2xl bg-[#111111] border border-[#2A2A2A] flex items-center justify-center">
                    <FileText className="h-9 w-9 text-[#D4AF37]" />
                  </div>
                  <div className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/40 flex items-center justify-center">
                    <Sparkles className="h-3 w-3 text-[#D4AF37]" />
                  </div>
                </div>
                <div className="space-y-2 max-w-sm">
                  <h3 className="text-lg font-bold text-white">
                    No cases yet
                  </h3>
                  <p className="text-sm text-[#B3B3B3] leading-relaxed">
                    Report your first consumer issue and let MIKE analyze
                    your rights and guide you to resolution.
                  </p>
                </div>
                <Button
                  onClick={() => navigate("/cases/new")}
                  className="gap-2 h-11 px-8 shadow-md shadow-[#D4AF37]/10"
                >
                  <PlusCircle className="h-4 w-4" />
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
            className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5"
          >
            {cases.slice(0, 6).map((c) => (
              <motion.div key={c.id} variants={itemVariants}>
                <Card className="h-full group flex flex-col rounded-2xl border border-[#2A2A2A] bg-[#1A1A1A] hover:border-[#D4AF37]/30 hover:shadow-xl hover:shadow-[#D4AF37]/5 transition-all duration-300 overflow-hidden">
                  <CardHeader className="bg-[#0A0A0A]/60 border-b border-[#2A2A2A] px-5 pt-5 pb-4">
                    <div className="flex items-start justify-between gap-3">
                      <CardTitle className="text-base font-semibold text-white line-clamp-2 group-hover:text-[#D4AF37] transition-colors duration-200 leading-snug">
                        {c.title}
                      </CardTitle>
                      <StatusBadge status={c.status} className="flex-shrink-0 mt-0.5" />
                    </div>
                  </CardHeader>

                  <CardContent className="flex-1 px-5 pt-4 pb-3">
                    <p className="text-sm text-[#B3B3B3] line-clamp-3 leading-relaxed mb-5">
                      {c.description}
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs text-[#B3B3B3] bg-[#0A0A0A] px-3 py-2 rounded-lg border border-[#2A2A2A]">
                        <Tag className="w-3.5 h-3.5 text-[#D4AF37] flex-shrink-0" />
                        <span className="truncate font-medium">{c.product_or_service}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-[#B3B3B3] px-3 py-1.5">
                        <Clock className="w-3.5 h-3.5 text-[#D4AF37] flex-shrink-0" />
                        <span>
                          Reported{" "}
                          <span className="text-white font-medium">
                            {new Date(c.created_at).toLocaleDateString(
                              undefined,
                              { year: "numeric", month: "short", day: "numeric" }
                            )}
                          </span>
                        </span>
                      </div>
                    </div>
                  </CardContent>

                  <CardFooter className="px-5 pt-3 pb-4 border-t border-[#2A2A2A] bg-[#0A0A0A]/30 flex justify-end">
                    <Link
                      to={`/cases/${c.id}`}
                      className="flex items-center gap-1 text-sm font-semibold text-[#D4AF37] hover:text-[#F4C542] transition-colors duration-200 group/btn"
                    >
                      View Details
                      <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform duration-200" />
                    </Link>
                  </CardFooter>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};