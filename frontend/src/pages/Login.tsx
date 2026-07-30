import React, { useState } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, Zap, BookOpen, Users, FileCheck, Clock } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { motion } from "framer-motion";

export const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await authApi.login({ email, password });
      toast.success("Successfully logged in!");
      await login(response.access_token);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    { icon: <ShieldCheck className="w-5 h-5 text-[#D4AF37]" />, title: "Secure & Confidential", desc: "Your data is protected with bank-level security." },
    { icon: <Zap className="w-5 h-5 text-[#D4AF37]" />, title: "AI-Powered Insights", desc: "Instant legal analysis tailored to your specific case." },
    { icon: <BookOpen className="w-5 h-5 text-[#D4AF37]" />, title: "Comprehensive Knowledge", desc: "Built on extensive consumer rights laws and precedents." },
  ];

  return (
    <div className="min-h-screen flex bg-[#0A0A0A]">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#111111] relative overflow-hidden flex-col justify-between p-12">
        {/* Background Patterns */}
        <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
           <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[#D4AF37] blur-[100px]" />
           <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[#D4AF37] blur-[100px]" />
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 flex flex-col items-start space-y-3"
        >
          <img src="/mike-logo.png" alt="MIKE Logo" className="h-16 w-16 object-contain" />
          <div className="flex flex-col">
            <span className="text-white text-3xl font-extrabold tracking-wider leading-tight">MIKE</span>
            <span className="text-sm text-[#D4AF37] font-semibold tracking-wider mt-0.5">AI Legal Assistant</span>
          </div>
        </motion.div>

        <div className="relative z-10 space-y-8 max-w-md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h1 className="text-4xl font-bold text-white leading-tight mb-4">
              Empowering consumers through intelligent legal guidance.
            </h1>
            <p className="text-[#B3B3B3] text-lg">
              Understand your rights, evaluate your options, and take action with confidence.
            </p>
          </motion.div>

          <div className="space-y-6 pt-8 border-t border-[#2A2A2A]">
            {features.map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 + (idx * 0.1) }}
                className="flex items-start space-x-4"
              >
                <div className="bg-[#1A1A1A] p-2 rounded-lg border border-[#2A2A2A] flex-shrink-0 mt-1">
                   {feature.icon}
                </div>
                <div>
                  <h3 className="text-white font-semibold">{feature.title}</h3>
                  <p className="text-[#B3B3B3] text-sm mt-1">{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="grid grid-cols-3 gap-4 pt-6 border-t border-[#2A2A2A]"
          >
            {[
              { icon: <Users className="h-4 w-4 text-[#D4AF37]" />, value: "10,000+", label: "Consumers Helped" },
              { icon: <FileCheck className="h-4 w-4 text-[#D4AF37]" />, value: "95%", label: "Success Rate" },
              { icon: <Clock className="h-4 w-4 text-[#D4AF37]" />, value: "< 2 min", label: "AI Analysis" },
            ].map((s, i) => (
              <div key={i} className="text-center">
                <div className="flex justify-center mb-1">{s.icon}</div>
                <p className="text-lg font-extrabold text-white leading-none">{s.value}</p>
                <p className="text-xs text-[#B3B3B3] mt-1 leading-tight">{s.label}</p>
              </div>
            ))}
          </motion.div>
        </div>

        <div className="relative z-10 text-[#B3B3B3] text-sm">
          &copy; {new Date().getFullYear()} MIKE. All rights reserved.
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 bg-[#0A0A0A]/50">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md space-y-8"
        >
          {/* Mobile Branding (only shows on small screens) */}
          <div className="lg:hidden flex flex-col items-center mb-8">
             <img src="/mike-logo.png" alt="MIKE Logo" className="h-16 w-16 object-contain mb-3" />
             <h2 className="text-2xl font-bold text-white tracking-tight">MIKE</h2>
             <span className="text-xs text-[#D4AF37] font-medium tracking-wide mt-1">AI Legal Assistant</span>
          </div>

          <div className="text-center lg:text-left">
            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              Sign in to MIKE
            </h2>
            <p className="text-[#B3B3B3] text-sm mt-1.5">
              Your AI-powered consumer rights assistant.
            </p>
          </div>

          <div className="bg-[#1A1A1A] p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-[#2A2A2A]">
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="space-y-1">
                <Input
                  id="email"
                  label="Email address"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="glass-input h-12"
                />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between items-center mb-1">
                </div>
                <Input
                  id="password"
                  label="Password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="glass-input h-12"
                />
              </div>
              <Button type="submit" className="w-full h-12 text-base font-medium mt-6 shadow-md shadow-[#D4AF37]/20 hover:shadow-lg hover:shadow-[#D4AF37]/30 transition-all" isLoading={isLoading}>
                Sign in
              </Button>
            </form>
          </div>

          <p className="text-center text-sm text-[#B3B3B3] mt-8">
            Don't have an account?{" "}
            <Link to="/register" className="font-semibold text-[#D4AF37] hover:text-[#D4AF37] transition-colors">
              Create an account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};


