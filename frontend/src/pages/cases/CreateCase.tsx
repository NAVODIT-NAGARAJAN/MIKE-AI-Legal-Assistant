import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { casesApi, CreateCaseRequest } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import { Package, Info, FileText, ChevronRight, ArrowLeft } from "lucide-react";
import { formatCategory } from "../../lib/caseUtils";

const CATEGORIES = [
  "DEFECTIVE_PRODUCT", "REFUND_ISSUE", "WARRANTY_CLAIM", "BILLING_DISPUTE",
  "DELIVERY_PROBLEM", "SERVICE_DEFICIENCY", "MISLEADING_ADVERTISEMENT", "ECOMMERCE_COMPLAINT",
];

export const CreateCase: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState<CreateCaseRequest>({
    title: "", description: "", category: "DEFECTIVE_PRODUCT",
    product_or_service: "", seller_name: "", purchase_date: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isEditing && id) {
      setIsLoading(true);
      casesApi.getCase(id)
        .then((data) => {
          setFormData({
            title: data.title, description: data.description, category: data.category,
            product_or_service: data.product_or_service,
            seller_name: data.seller_name || "", purchase_date: data.purchase_date || "",
          });
        })
        .catch(() => toast.error("Failed to load case details."))
        .finally(() => setIsLoading(false));
    }
  }, [id, isEditing]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const payload = {
        ...formData,
        seller_name: formData.seller_name || null,
        purchase_date: formData.purchase_date || null,
      };
      if (isEditing && id) {
        await casesApi.updateCase(id, payload);
        toast.success("Case updated successfully.");
      } else {
        await casesApi.createCase(payload);
        toast.success("Case created successfully.");
      }
      navigate("/cases");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to save case.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const formVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };
  const itemVariants = {
    hidden: { opacity: 0, y: 14 },
    show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
  };

  const inputClass = "block w-full px-4 py-3 bg-[#0A0A0A]/60 border border-[#2A2A2A] rounded-xl text-white placeholder:text-[#B3B3B3] text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/30 focus:border-[#D4AF37] transition-all duration-200";
  const labelClass = "block text-sm font-semibold text-[#B3B3B3] mb-2";

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        className="space-y-1 border-b border-[#2A2A2A] pb-7"
      >
        <button
          onClick={() => navigate("/cases")}
          className="flex items-center gap-1.5 text-sm text-[#B3B3B3] hover:text-white mb-4 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Cases
        </button>
        <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
          {isEditing ? "Edit Case" : "Report an Issue"}
        </h1>
        <p className="text-[#B3B3B3] text-base leading-relaxed">
          {isEditing
            ? "Update the details of your consumer case."
            : "Provide detailed information so MIKE can accurately analyze your rights and build your resolution roadmap."}
        </p>
      </motion.div>

      {/* Progress steps (visual only) */}
      {!isEditing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-2 text-xs text-[#B3B3B3]"
        >
          {["Issue Info", "Product Details", "Submit"].map((step, i) => (
            <React.Fragment key={step}>
              <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${
                i === 0 ? "border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]" : "border-[#2A2A2A] text-[#B3B3B3]"
              }`}>
                <span className="font-semibold">{i + 1}</span>
                <span>{step}</span>
              </div>
              {i < 2 && <ChevronRight className="h-3 w-3 text-[#2A2A2A]" />}
            </React.Fragment>
          ))}
        </motion.div>
      )}

      {/* Form */}
      <motion.form
        onSubmit={handleSubmit}
        variants={formVariants}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        {/* Card 1: Basic Info */}
        <motion.div variants={itemVariants}>
          <Card className="border border-[#2A2A2A] bg-[#1A1A1A] rounded-2xl overflow-hidden shadow-sm">
            <CardHeader className="bg-[#0A0A0A]/50 border-b border-[#2A2A2A] px-6 py-4">
              <CardTitle className="text-base font-bold text-white flex items-center gap-2.5">
                <div className="h-7 w-7 rounded-lg bg-[#D4AF37]/15 border border-[#D4AF37]/20 flex items-center justify-center">
                  <FileText className="w-4 h-4 text-[#D4AF37]" />
                </div>
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent className="px-6 py-6 space-y-6">
              <div className="max-w-2xl">
                <label htmlFor="title" className={labelClass}>
                  Issue Title <span className="text-red-400">*</span>
                </label>
                <Input
                  id="title"
                  name="title"
                  label=""
                  required
                  minLength={5}
                  maxLength={255}
                  placeholder="e.g. Defective smartphone received from Amazon"
                  value={formData.title}
                  onChange={handleChange}
                  className="bg-[#0A0A0A]/60"
                />
              </div>
              <div>
                <label htmlFor="description" className={labelClass}>
                  Detailed Description <span className="text-red-400">*</span>
                </label>
                <textarea
                  id="description"
                  name="description"
                  required
                  minLength={20}
                  rows={7}
                  className={inputClass + " resize-y"}
                  placeholder="Describe exactly what happened in chronological order. Include dates, amounts, and what resolution you expect..."
                  value={formData.description}
                  onChange={handleChange}
                />
                <p className="mt-2 text-xs text-[#B3B3B3] flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-[#D4AF37] flex-shrink-0" />
                  Include all communication with customer service and any evidence you have.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Card 2: Product & Seller */}
        <motion.div variants={itemVariants}>
          <Card className="border border-[#2A2A2A] bg-[#1A1A1A] rounded-2xl overflow-hidden shadow-sm">
            <CardHeader className="bg-[#0A0A0A]/50 border-b border-[#2A2A2A] px-6 py-4">
              <CardTitle className="text-base font-bold text-white flex items-center gap-2.5">
                <div className="h-7 w-7 rounded-lg bg-[#D4AF37]/15 border border-[#D4AF37]/20 flex items-center justify-center">
                  <Package className="w-4 h-4 text-[#D4AF37]" />
                </div>
                Product & Seller Details
              </CardTitle>
            </CardHeader>
            <CardContent className="px-6 py-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="category" className={labelClass}>
                    Issue Category <span className="text-red-400">*</span>
                  </label>
                  <select
                    id="category"
                    name="category"
                    required
                    className={inputClass + " cursor-pointer appearance-none"}
                    value={formData.category}
                    onChange={handleChange}
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23D4AF37' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: "right 0.75rem center",
                      backgroundRepeat: "no-repeat",
                      backgroundSize: "1.25em 1.25em",
                      paddingRight: "2.75rem",
                    }}
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat} className="bg-[#1A1A1A]">
                        {formatCategory(cat)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="product_or_service" className={labelClass}>
                    Product / Service Name <span className="text-red-400">*</span>
                  </label>
                  <Input
                    id="product_or_service"
                    name="product_or_service"
                    label=""
                    required
                    placeholder="e.g. iPhone 15 Pro Max"
                    value={formData.product_or_service}
                    onChange={handleChange}
                    className="bg-[#0A0A0A]/60"
                  />
                </div>
                <div>
                  <label htmlFor="seller_name" className={labelClass}>
                    Seller / Provider Name{" "}
                    <span className="text-[#B3B3B3] font-normal">(optional)</span>
                  </label>
                  <Input
                    id="seller_name"
                    name="seller_name"
                    label=""
                    placeholder="e.g. Amazon India"
                    value={formData.seller_name || ""}
                    onChange={handleChange}
                    className="bg-[#0A0A0A]/60"
                  />
                </div>
                <div>
                  <label htmlFor="purchase_date" className={labelClass}>
                    Purchase Date{" "}
                    <span className="text-[#B3B3B3] font-normal">(optional)</span>
                  </label>
                  <input
                    id="purchase_date"
                    type="date"
                    name="purchase_date"
                    max={new Date().toISOString().split("T")[0]}
                    value={formData.purchase_date || ""}
                    onChange={handleChange}
                    className={inputClass + " [color-scheme:dark]"}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Actions */}
        <motion.div variants={itemVariants} className="flex justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="ghost"
            onClick={() => navigate("/cases")}
            disabled={isLoading}
            className="h-11 px-6"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={isLoading}
            className="h-11 px-8 shadow-md shadow-[#D4AF37]/15 gap-2"
          >
            {isEditing ? "Save Changes" : "Submit Case"}
          </Button>
        </motion.div>
      </motion.form>
    </div>
  );
};
