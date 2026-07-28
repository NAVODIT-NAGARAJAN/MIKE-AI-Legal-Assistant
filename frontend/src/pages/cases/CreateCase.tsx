import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { casesApi, CreateCaseRequest } from "../../api/cases";
import { Button } from "../../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { toast } from "react-toastify";
import { motion } from "framer-motion";
import { Package, Info, FileText } from "lucide-react";

const CATEGORIES = [
  "DEFECTIVE_PRODUCT",
  "REFUND_ISSUE",
  "WARRANTY_CLAIM",
  "BILLING_DISPUTE",
  "DELIVERY_PROBLEM",
  "SERVICE_DEFICIENCY",
  "MISLEADING_ADVERTISEMENT",
  "ECOMMERCE_COMPLAINT"
];

export const CreateCase: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState<CreateCaseRequest>({
    title: "",
    description: "",
    category: "DEFECTIVE_PRODUCT",
    product_or_service: "",
    seller_name: "",
    purchase_date: "",
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isEditing && id) {
      setIsLoading(true);
      casesApi.getCase(id)
        .then(data => {
          setFormData({
            title: data.title,
            description: data.description,
            category: data.category,
            product_or_service: data.product_or_service,
            seller_name: data.seller_name || "",
            purchase_date: data.purchase_date || "",
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
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4 } }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="pb-4 border-b border-gray-200"
      >
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
          {isEditing ? "Edit Consumer Case" : "Report a Consumer Issue"}
        </h1>
        <p className="mt-2 text-gray-500">
          Provide as much detail as possible so our AI can accurately analyze your rights.
        </p>
      </motion.div>

      <motion.form 
        onSubmit={handleSubmit}
        variants={formVariants}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        <motion.div variants={itemVariants}>
          <Card className="border-gray-200 shadow-sm overflow-hidden bg-white">
            <CardHeader className="bg-gray-50/50 border-b border-gray-100 py-4 px-6 flex flex-row items-center space-x-2">
              <FileText className="w-5 h-5 text-blue-500" />
              <CardTitle className="text-lg">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="max-w-2xl">
                <Input
                  id="title"
                  name="title"
                  label="Issue Title"
                  required
                  minLength={5}
                  maxLength={255}
                  placeholder="e.g. Defective smartphone from Amazon"
                  value={formData.title}
                  onChange={handleChange}
                  className="bg-gray-50/50"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Detailed Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="description"
                  name="description"
                  required
                  minLength={20}
                  rows={6}
                  className="block w-full px-4 py-3 bg-gray-50/50 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors resize-y"
                  placeholder="Please describe exactly what happened in chronological order..."
                  value={formData.description}
                  onChange={handleChange}
                />
                <p className="mt-2 text-xs text-gray-500 flex items-center">
                  <Info className="w-3.5 h-3.5 mr-1" />
                  Include dates, communication with customer service, and the outcome you want.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="border-gray-200 shadow-sm overflow-hidden bg-white">
            <CardHeader className="bg-gray-50/50 border-b border-gray-100 py-4 px-6 flex flex-row items-center space-x-2">
              <Package className="w-5 h-5 text-indigo-500" />
              <CardTitle className="text-lg">Product & Seller Details</CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
                <div>
                  <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                    Category <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="category"
                    name="category"
                    required
                    className="block w-full px-4 py-3 bg-gray-50/50 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors cursor-pointer appearance-none"
                    value={formData.category}
                    onChange={handleChange}
                    style={{ backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`, backgroundPosition: `right 0.5rem center`, backgroundRepeat: `no-repeat`, backgroundSize: `1.5em 1.5em`, paddingRight: `2.5rem` }}
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat.replace(/_/g, " ")}</option>
                    ))}
                  </select>
                </div>
                <Input
                  id="product_or_service"
                  name="product_or_service"
                  label="Product/Service Name"
                  required
                  value={formData.product_or_service}
                  onChange={handleChange}
                  className="bg-gray-50/50"
                  placeholder="e.g. iPhone 14 Pro Max"
                />
                <Input
                  id="seller_name"
                  name="seller_name"
                  label="Seller / Provider Name"
                  value={formData.seller_name || ""}
                  onChange={handleChange}
                  className="bg-gray-50/50"
                  placeholder="e.g. Amazon India"
                />
                <Input
                  id="purchase_date"
                  name="purchase_date"
                  type="date"
                  label="Purchase Date"
                  max={new Date().toISOString().split("T")[0]}
                  value={formData.purchase_date || ""}
                  onChange={handleChange}
                  className="bg-gray-50/50"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants} className="flex justify-end space-x-4 pt-4">
          <Button type="button" variant="ghost" onClick={() => navigate("/cases")} disabled={isLoading} className="h-11 px-6">
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading} className="h-11 px-8 shadow-md">
            {isEditing ? "Save Changes" : "Submit Case"}
          </Button>
        </motion.div>
      </motion.form>
    </div>
  );
};
