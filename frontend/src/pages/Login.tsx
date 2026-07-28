import React, { useState } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { Scale, ShieldCheck, Zap, BookOpen } from "lucide-react";
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
    { icon: <ShieldCheck className="w-5 h-5 text-blue-400" />, title: "Secure & Confidential", desc: "Your data is protected with bank-level security." },
    { icon: <Zap className="w-5 h-5 text-blue-400" />, title: "AI-Powered Insights", desc: "Instant legal analysis tailored to your specific case." },
    { icon: <BookOpen className="w-5 h-5 text-blue-400" />, title: "Comprehensive Knowledge", desc: "Built on extensive consumer rights laws and precedents." },
  ];

  return (
    <div className="min-h-screen flex bg-white">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-blue-900 relative overflow-hidden flex-col justify-between p-12">
        {/* Background Patterns */}
        <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
           <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500 blur-[100px]" />
           <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-500 blur-[100px]" />
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 flex items-center space-x-3"
        >
          <div className="bg-white/10 p-2.5 rounded-xl backdrop-blur-sm border border-white/20">
            <Scale className="text-white w-8 h-8" strokeWidth={1.5} />
          </div>
          <span className="text-white text-2xl font-bold tracking-tight">LegalEase AI</span>
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
            <p className="text-blue-200 text-lg">
              Understand your rights, evaluate your options, and take action with confidence.
            </p>
          </motion.div>

          <div className="space-y-6 pt-8 border-t border-blue-800/50">
            {features.map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 + (idx * 0.1) }}
                className="flex items-start space-x-4"
              >
                <div className="bg-blue-800/50 p-2 rounded-lg border border-blue-700/50 flex-shrink-0 mt-1">
                  {feature.icon}
                </div>
                <div>
                  <h3 className="text-white font-semibold">{feature.title}</h3>
                  <p className="text-blue-300 text-sm mt-1">{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="relative z-10 text-blue-400 text-sm">
          &copy; {new Date().getFullYear()} LegalEase AI. All rights reserved.
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 bg-gray-50/50">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md space-y-8"
        >
          {/* Mobile Branding (only shows on small screens) */}
          <div className="lg:hidden flex flex-col items-center mb-8">
             <div className="bg-blue-600 p-3 rounded-xl mb-4 shadow-lg shadow-blue-200">
               <Scale className="text-white w-8 h-8" strokeWidth={1.5} />
             </div>
             <h2 className="text-2xl font-bold text-gray-900 tracking-tight">LegalEase AI</h2>
          </div>

          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight mb-2">
              Welcome back
            </h2>
            <p className="text-gray-500 text-sm">
              Please enter your details to sign in to your account.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100">
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
                  placeholder="••••••••"
                  className="glass-input h-12"
                />
              </div>
              <Button type="submit" className="w-full h-12 text-base font-medium mt-6 shadow-md shadow-blue-200 hover:shadow-lg hover:shadow-blue-300 transition-all" isLoading={isLoading}>
                Sign in
              </Button>
            </form>
          </div>

          <p className="text-center text-sm text-gray-600 mt-8">
            Don't have an account?{" "}
            <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-700 transition-colors">
              Create an account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

