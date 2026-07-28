import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, Link, useSearchParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Send, Bot, User, Loader2, Plus, MessageSquare, Menu,
  Scale, ArrowRight,
} from "lucide-react";
import { toast } from "react-toastify";

import { useAuth } from "../../context/AuthContext";
import {
  aiApi as apiService,
  ConversationMessage as Msg,
  AgentReply,
  ConversationListItem,
} from "../../api/ai";
import { motion, AnimatePresence } from "framer-motion";

const SUGGESTED_PROMPTS = [
  "I received a defective product. What are my rights?",
  "The seller is refusing to issue a refund.",
  "I was charged incorrectly on my bill.",
  "My online order never arrived.",
];

export const ChatInterface: React.FC = () => {
  const { conversationId } = useParams<{ conversationId?: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const caseId = searchParams.get("caseId");
  const { user } = useAuth();

  const [messages, setMessages] = useState<Msg[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [recentChats, setRecentChats] = useState<ConversationListItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadRecentChats = async () => {
    try {
      const chats = await apiService.listConversations();
      setRecentChats(chats);
    } catch (err) {
      console.error("Failed to load conversations", err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => { scrollToBottom(); }, [messages, isTyping]);
  useEffect(() => { loadRecentChats(); }, []);

  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    } else {
      setMessages([{
        role: "ai",
        content: "Hello! I am **MIKE**, your AI consumer rights assistant. Please describe your consumer issue in detail so I can analyze your rights and guide you to resolution.",
        timestamp: new Date().toISOString(),
      }]);
    }
  }, [conversationId]);

  const loadConversation = async (id: string) => {
    setIsLoading(true);
    try {
      const data = await apiService.getConversation(id);
      setMessages(data.messages);
    } catch (err) {
      toast.error("Failed to load conversation history.");
      navigate("/chat");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent | string) => {
    if (typeof e !== "string") e.preventDefault();
    const content = typeof e === "string" ? e : inputMessage;
    if (!content.trim()) return;

    const userMsg: Msg = { role: "user", content, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "56px";
    }
    setIsTyping(true);

    try {
      let replyData: AgentReply;
      if (conversationId) {
        replyData = await apiService.sendMessage(conversationId, userMsg.content);
      } else {
        replyData = await apiService.startConversation(userMsg.content, caseId ?? undefined);
        await loadRecentChats();
        navigate(`/chat/${replyData.conversation_id}`, { replace: true });
      }
      const aiMsg: Msg = { role: "ai", content: replyData.reply, timestamp: new Date().toISOString() };
      setMessages((prev) => [...prev, aiMsg]);
      if (replyData.is_complete) {
        toast.info("Consultation completed. Your resolution roadmap is being generated.");
      }
    } catch (err: any) {
      let errorMsg = "Failed to communicate with AI Agent.";
      if (err.response?.data?.message) errorMsg = err.response.data.message;
      if (Array.isArray(err.response?.data?.errors) && err.response.data.errors.length > 0) {
        errorMsg += ` (${err.response.data.errors[0].message})`;
      }
      toast.error(errorMsg);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as unknown as React.FormEvent);
    }
  };

  const isNewChat = !conversationId && messages.length <= 1;

  return (
    <div className="flex h-[calc(100dvh-6rem)] md:h-[calc(100dvh-4rem)] bg-[#1A1A1A] border border-[#2A2A2A] rounded-2xl overflow-hidden relative shadow-xl">

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Chat Sidebar */}
      <motion.div
        className={`w-72 bg-[#0A0A0A] border-r border-[#2A2A2A] flex flex-col absolute inset-y-0 left-0 z-50 transform md:relative md:translate-x-0 transition-transform duration-300 ease-in-out ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="p-4 border-b border-[#2A2A2A]">
          <button
            onClick={() => { navigate("/chat"); setIsSidebarOpen(false); }}
            className="w-full h-10 flex items-center justify-center gap-2 bg-[#D4AF37] hover:bg-[#F4C542] text-black text-sm font-semibold rounded-xl transition-all duration-200 shadow-md shadow-[#D4AF37]/20"
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          <p className="text-xs font-bold text-[#B3B3B3] uppercase tracking-widest mb-3 px-2">
            Recent
          </p>
          {isLoadingHistory ? (
            <div className="space-y-2 px-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="skeleton h-10 rounded-xl" />
              ))}
            </div>
          ) : recentChats.length === 0 ? (
            <div className="px-2 py-8 text-center">
              <MessageSquare className="h-8 w-8 text-[#2A2A2A] mx-auto mb-2" />
              <p className="text-xs text-[#B3B3B3]">No conversations yet</p>
            </div>
          ) : (
            <div className="space-y-1">
              {recentChats.map((chat) => (
                <Link
                  key={chat.id}
                  to={`/chat/${chat.id}`}
                  onClick={() => setIsSidebarOpen(false)}
                  className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm transition-all duration-200 ${
                    conversationId === chat.id
                      ? "bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/20"
                      : "text-[#B3B3B3] hover:bg-[#1A1A1A] hover:text-white"
                  }`}
                >
                  <MessageSquare className={`h-3.5 w-3.5 flex-shrink-0 ${conversationId === chat.id ? "text-[#D4AF37]" : "text-[#B3B3B3]"}`} />
                  <span className="truncate font-medium">{chat.title}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </motion.div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative w-full min-w-0">
        {/* Header */}
        <div className="bg-[#1A1A1A]/90 backdrop-blur-md border-b border-[#2A2A2A] px-4 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="md:hidden p-2 rounded-lg text-[#B3B3B3] hover:text-white hover:bg-[#2A2A2A] transition-all"
              aria-label="Open chat history"
            >
              <Menu size={18} />
            </button>
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[#D4AF37] to-[#F4C542] flex items-center justify-center shadow-md shadow-[#D4AF37]/20 hidden sm:flex flex-shrink-0">
              <Bot className="h-5 w-5 text-black" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white leading-none">MIKE</h2>
              <p className="text-xs text-[#D4AF37] mt-0.5">AI Legal Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 text-xs text-[#B3B3B3] bg-[#0A0A0A] border border-[#2A2A2A] rounded-full px-3 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-[#D4AF37] animate-pulse" />
              Online
            </span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 bg-[#1A1A1A]">
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-[#D4AF37]" />
                <p className="text-sm text-[#B3B3B3]">Loading conversation...</p>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6 pb-36">
              {/* Suggested prompts on new chat */}
              {isNewChat && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.4 }}
                  className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2"
                >
                  {SUGGESTED_PROMPTS.map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(prompt)}
                      disabled={isTyping}
                      className="flex items-center justify-between gap-3 p-4 bg-[#111111] border border-[#2A2A2A] rounded-xl text-left text-sm text-[#B3B3B3] hover:text-white hover:border-[#D4AF37]/40 hover:bg-[#1A1A1A] transition-all duration-200 group disabled:opacity-50"
                    >
                      <span className="line-clamp-2 leading-relaxed">{prompt}</span>
                      <ArrowRight className="h-4 w-4 flex-shrink-0 text-[#D4AF37] opacity-0 group-hover:opacity-100 transition-opacity" />
                    </button>
                  ))}
                </motion.div>
              )}

              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex max-w-[88%] sm:max-w-[82%] gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    {/* Avatar */}
                    <div className="flex-shrink-0 mt-1">
                      {msg.role === "user" ? (
                        <div className="h-8 w-8 rounded-full bg-[#D4AF37] text-black flex items-center justify-center font-bold text-sm shadow-sm">
                          {user?.full_name?.charAt(0).toUpperCase() || <User size={14} />}
                        </div>
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F4C542] flex items-center justify-center shadow-sm">
                          <Scale className="h-4 w-4 text-black" />
                        </div>
                      )}
                    </div>

                    {/* Bubble */}
                    <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      msg.role === "user"
                        ? "bg-[#D4AF37] text-black rounded-tr-sm font-medium"
                        : "bg-[#0A0A0A] border border-[#2A2A2A] text-white rounded-tl-sm prose prose-sm prose-invert max-w-none"
                    }`}>
                      {msg.role === "user" ? (
                        <p className="whitespace-pre-wrap m-0">{msg.content}</p>
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex gap-3">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F4C542] flex items-center justify-center mt-1 flex-shrink-0">
                      <Scale className="h-4 w-4 text-black" />
                    </div>
                    <div className="px-4 py-3.5 bg-[#0A0A0A] border border-[#2A2A2A] rounded-2xl rounded-tl-sm flex items-center gap-1.5">
                      {[0, 0.15, 0.3].map((delay, i) => (
                        <div
                          key={i}
                          className="w-2 h-2 bg-[#D4AF37] rounded-full animate-bounce"
                          style={{ animationDelay: `${delay}s` }}
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#1A1A1A] via-[#1A1A1A]/95 to-transparent pt-8">
          <form
            onSubmit={handleSendMessage}
            className="max-w-3xl mx-auto relative"
          >
            <textarea
              ref={textareaRef}
              className="w-full px-5 py-4 pr-14 bg-[#0A0A0A] border border-[#2A2A2A] rounded-2xl shadow-lg focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40 focus:border-[#D4AF37] transition-all resize-none text-white placeholder:text-[#B3B3B3] text-sm"
              placeholder="Describe your consumer issue... (Shift+Enter for new line)"
              value={inputMessage}
              onChange={(e) => {
                setInputMessage(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
              }}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              rows={1}
              style={{ minHeight: "56px", maxHeight: "120px" }}
            />
            <button
              type="submit"
              disabled={isTyping || !inputMessage.trim()}
              className="absolute right-2 bottom-2 h-10 w-10 rounded-xl bg-[#D4AF37] hover:bg-[#F4C542] text-black flex items-center justify-center transition-all duration-200 shadow-md disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40"
              aria-label="Send message"
            >
              {isTyping ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4 ml-0.5" />}
            </button>
          </form>
          <p className="text-center text-[10px] text-[#B3B3B3] mt-2">
            MIKE can make mistakes. Always verify important legal information with a qualified professional.
          </p>
        </div>
      </div>
    </div>
  );
};
