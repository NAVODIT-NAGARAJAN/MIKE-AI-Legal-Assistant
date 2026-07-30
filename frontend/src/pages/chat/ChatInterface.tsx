import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, Link, useSearchParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Send, Bot, User, Loader2, Plus, MessageSquare, Menu,
  Scale, MoreVertical, Edit2, Trash2, ShieldCheck, FileText, Briefcase, Search as SearchIcon
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

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../../components/ui/dropdown-menu";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../../components/ui/alert-dialog";

const QUICK_ACTIONS = [
  { icon: <ShieldCheck className="w-5 h-5 text-[#D4AF37]" />, label: "Analyze Consumer Case", prompt: "I want to analyze a consumer rights case. Where should I start?" },
  { icon: <Scale className="w-5 h-5 text-[#D4AF37]" />, label: "Consumer Rights", prompt: "What are my basic rights as a consumer in India?" },
  { icon: <FileText className="w-5 h-5 text-[#D4AF37]" />, label: "Draft Complaint", prompt: "Help me draft a formal consumer complaint letter." },
  { icon: <Briefcase className="w-5 h-5 text-[#D4AF37]" />, label: "Legal Research", prompt: "I need to do some legal research on consumer protection laws." },
];

// Helper to auto-generate title
const generateTitle = (text: string) => {
  const cleanText = text.trim();
  if (cleanText.length < 5) return "General Inquiry";
  const words = cleanText.split(" ");
  if (words.length <= 4) return cleanText;
  return words.slice(0, 5).join(" ") + "...";
};

// Helper for grouping
const groupConversations = (chats: ConversationListItem[], query: string) => {
  const filtered = chats.filter(c => c.title.toLowerCase().includes(query.toLowerCase()));
  const groups: { [key: string]: ConversationListItem[] } = {
    "Today": [],
    "Yesterday": [],
    "Previous 7 Days": [],
    "Older": []
  };

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const lastWeek = new Date(today);
  lastWeek.setDate(lastWeek.getDate() - 7);

  filtered.forEach(chat => {
    const chatDate = new Date(chat.created_at);
    if (chatDate >= today) {
      groups["Today"].push(chat);
    } else if (chatDate >= yesterday) {
      groups["Yesterday"].push(chat);
    } else if (chatDate >= lastWeek) {
      groups["Previous 7 Days"].push(chat);
    } else {
      groups["Older"].push(chat);
    }
  });

  return groups;
};

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
  
  // Sidebar state
  const [recentChats, setRecentChats] = useState<ConversationListItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  
  // Chat management state
  const [chatToDelete, setChatToDelete] = useState<string | null>(null);
  const [chatToRename, setChatToRename] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadRecentChats = async () => {
    try {
      const chats = await apiService.listConversations();
      // Auto-generate titles for generic ones locally if needed
      const polishedChats = chats.map(c => ({
        ...c,
        title: c.title.length < 3 || c.title.toLowerCase() === "hi" || c.title.toLowerCase() === "hello" 
          ? "General Inquiry" 
          : c.title
      }));
      setRecentChats(polishedChats);
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
      setMessages([]); // Empty array triggers the welcome screen
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

  const handleDeleteChat = async () => {
  if (!chatToDelete) return;

  try {
    // Delete from backend
    await apiService.deleteConversation(chatToDelete);

    // Remove from sidebar
    setRecentChats(prev =>
      prev.filter(c => c.id !== chatToDelete)
    );

    toast.success("Conversation deleted.");

    // If currently viewing this conversation,
    // navigate back to a new chat
    if (conversationId === chatToDelete) {
      navigate("/chat");
    }
  } catch (err) {
    console.error(err);
    toast.error("Failed to delete conversation.");
  } finally {
    setChatToDelete(null);
  }
};

  const handleRenameSubmit = (id: string) => {
    if (!renameValue.trim()) {
      setChatToRename(null);
      return;
    }
    setRecentChats(prev => prev.map(c => c.id === id ? { ...c, title: renameValue } : c));
    toast.success("Conversation renamed.");
    setChatToRename(null);
    setRenameValue("");
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
        const newTitle = generateTitle(userMsg.content);
        
        // Optimistically add to sidebar
        setRecentChats(prev => [{
          id: replyData.conversation_id,
          case_id: caseId ?? null,
          title: newTitle,
          is_complete: false,
          created_at: new Date().toISOString()
        }, ...prev]);

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
      setMessages((prev) => prev.filter(m => m !== userMsg)); // Revert if failed
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

  const isNewChat = !conversationId && messages.length === 0;
  const firstName = user?.full_name?.split(" ")[0] ?? "there";
  const groupedChats = groupConversations(recentChats, searchQuery);

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
        <div className="p-4 border-b border-[#2A2A2A] space-y-4">
          <button
            onClick={() => { navigate("/chat"); setIsSidebarOpen(false); }}
            className="w-full h-10 flex items-center justify-center gap-2 bg-[#D4AF37] hover:bg-[#F4C542] text-black text-sm font-semibold rounded-xl transition-all duration-200 shadow-md shadow-[#D4AF37]/20"
          >
            <Plus className="h-4 w-4" />
            New Chat
          </button>
          
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#B3B3B3]" />
            <input 
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-9 pl-9 pr-3 bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg text-sm text-white placeholder:text-[#B3B3B3] focus:outline-none focus:border-[#D4AF37]/50 focus:ring-1 focus:ring-[#D4AF37]/30 transition-all"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-5">
          {isLoadingHistory ? (
            <div className="space-y-2 px-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="skeleton h-10 rounded-xl" />
              ))}
            </div>
          ) : recentChats.length === 0 ? (
            <div className="px-2 py-8 text-center">
              <MessageSquare className="h-8 w-8 text-[#2A2A2A] mx-auto mb-2" />
              <p className="text-xs text-[#B3B3B3]">No conversations yet</p>
            </div>
          ) : (
            Object.entries(groupedChats).map(([groupName, chats]) => {
              if (chats.length === 0) return null;
              return (
                <div key={groupName} className="space-y-1">
                  <p className="text-[10px] font-bold text-[#B3B3B3] uppercase tracking-wider mb-2 px-3">
                    {groupName}
                  </p>
                  {chats.map((chat) => (
                    <div
                      key={chat.id}
                      className={`group relative flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm transition-all duration-200 ${
                        conversationId === chat.id
                          ? "bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/20"
                          : "text-[#B3B3B3] hover:bg-[#1A1A1A] hover:text-white border border-transparent"
                      }`}
                    >
                      <Link
                        to={`/chat/${chat.id}`}
                        onClick={() => setIsSidebarOpen(false)}
                        className="flex items-center gap-2.5 flex-1 min-w-0"
                      >
                        <MessageSquare className={`h-3.5 w-3.5 flex-shrink-0 ${conversationId === chat.id ? "text-[#D4AF37]" : "text-[#B3B3B3]"}`} />
                        {chatToRename === chat.id ? (
                          <input 
                            autoFocus
                            value={renameValue}
                            onChange={(e) => setRenameValue(e.target.value)}
                            onBlur={() => handleRenameSubmit(chat.id)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleRenameSubmit(chat.id);
                              if (e.key === 'Escape') setChatToRename(null);
                            }}
                            className="flex-1 bg-transparent border-b border-[#D4AF37] text-white focus:outline-none px-0 py-0 text-sm w-full"
                          />
                        ) : (
                          <span className="truncate font-medium">{chat.title}</span>
                        )}
                      </Link>
                      
                      {/* 3-dot menu */}
                      <DropdownMenu>
                        <DropdownMenuTrigger className={`p-1 rounded-md text-[#B3B3B3] hover:text-white hover:bg-[#2A2A2A] transition-colors ${conversationId === chat.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                          <MoreVertical className="h-3.5 w-3.5" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-40 bg-[#1A1A1A] border-[#2A2A2A] text-white rounded-xl shadow-xl">
                          <DropdownMenuItem 
                            onClick={(e) => { e.stopPropagation(); setChatToRename(chat.id); setRenameValue(chat.title); }}
                            className="hover:bg-[#2A2A2A] focus:bg-[#2A2A2A] cursor-pointer text-sm gap-2"
                          >
                            <Edit2 className="h-3.5 w-3.5" /> Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={(e) => { e.stopPropagation(); setChatToDelete(chat.id); }}
                            className="hover:bg-red-500/10 focus:bg-red-500/10 text-red-400 focus:text-red-300 cursor-pointer text-sm gap-2"
                          >
                            <Trash2 className="h-3.5 w-3.5" /> Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  ))}
                </div>
              );
            })
          )}
        </div>
      </motion.div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative w-full min-w-0">
        {/* Header */}
        <div className="bg-[#1A1A1A]/90 backdrop-blur-md border-b border-[#2A2A2A] px-4 py-3 flex items-center justify-between flex-shrink-0 relative z-10">
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
            <span className="flex items-center gap-1.5 text-xs text-[#B3B3B3] bg-[#0A0A0A] border border-[#2A2A2A] rounded-full px-3 py-1 shadow-inner">
              <span className="h-1.5 w-1.5 rounded-full bg-[#D4AF37] animate-pulse shadow-[0_0_8px_rgba(212,175,55,0.8)]" />
              Online
            </span>
          </div>
        </div>

        {/* Messages / Empty State */}
        <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 bg-[#1A1A1A] scroll-smooth">
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-[#D4AF37]" />
                <p className="text-sm text-[#B3B3B3]">Loading conversation...</p>
              </div>
            </div>
          ) : isNewChat ? (
            <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto text-center px-4 -mt-10">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="mb-8"
              >
                <div className="h-20 w-20 mx-auto rounded-3xl bg-gradient-to-br from-[#D4AF37] to-[#F4C542] flex items-center justify-center shadow-lg shadow-[#D4AF37]/20 mb-6 border-4 border-[#1A1A1A] ring-1 ring-[#2A2A2A]">
                  <Scale className="h-10 w-10 text-black" />
                </div>
                <h1 className="text-3xl font-bold text-white mb-3">Hi, {firstName} <span className="animate-wave origin-bottom-right inline-block">👋</span></h1>
                <p className="text-[#B3B3B3] text-lg">How can MIKE help you today?</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full"
              >
                {QUICK_ACTIONS.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendMessage(action.prompt)}
                    disabled={isTyping}
                    className="flex flex-col items-start p-4 bg-[#111111] border border-[#2A2A2A] rounded-2xl text-left hover:border-[#D4AF37]/40 hover:bg-[#1A1A1A] transition-all duration-300 group hover:shadow-lg hover:shadow-[#D4AF37]/5 disabled:opacity-50"
                  >
                    <div className="bg-[#1A1A1A] p-2 rounded-lg border border-[#2A2A2A] mb-3 group-hover:scale-110 transition-transform">
                      {action.icon}
                    </div>
                    <span className="font-semibold text-white text-sm mb-1">{action.label}</span>
                    <span className="text-xs text-[#B3B3B3] line-clamp-1">{action.prompt}</span>
                  </button>
                ))}
              </motion.div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6 pb-36">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex max-w-[88%] sm:max-w-[82%] gap-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    {/* Avatar */}
                    <div className="flex-shrink-0 mt-1">
                      {msg.role === "user" ? (
                        <div className="h-8 w-8 rounded-full bg-[#D4AF37] text-black flex items-center justify-center font-bold text-sm shadow-sm ring-2 ring-[#1A1A1A]">
                          {user?.full_name?.charAt(0).toUpperCase() || <User size={14} />}
                        </div>
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F4C542] flex items-center justify-center shadow-sm ring-2 ring-[#1A1A1A]">
                          <Scale className="h-4 w-4 text-black" />
                        </div>
                      )}
                    </div>

                    {/* Bubble */}
                    <div className={`px-5 py-4 rounded-3xl text-[15px] leading-relaxed shadow-sm ${
                      msg.role === "user"
                        ? "bg-[#D4AF37] text-black rounded-tr-sm font-medium"
                        : "bg-[#111111] border border-[#2A2A2A] text-white rounded-tl-sm prose prose-sm prose-invert max-w-none"
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

              {/* Thinking Indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex max-w-[88%] sm:max-w-[82%] gap-4 flex-row">
                    <div className="flex-shrink-0 mt-1">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F4C542] flex items-center justify-center shadow-sm ring-2 ring-[#1A1A1A]">
                        <Scale className="h-4 w-4 text-black" />
                      </div>
                    </div>
                    <div className="px-5 py-4 bg-[#111111] border border-[#2A2A2A] rounded-3xl rounded-tl-sm flex items-center gap-3 shadow-sm">
                      <span className="text-sm font-medium text-[#B3B3B3]">MIKE is thinking</span>
                      <div className="flex items-center gap-1.5 mt-1">
                        {[0, 0.15, 0.3].map((delay, i) => (
                          <div
                            key={i}
                            className="w-1.5 h-1.5 bg-[#D4AF37] rounded-full animate-bounce"
                            style={{ animationDelay: `${delay}s` }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#1A1A1A] via-[#1A1A1A]/95 to-transparent pt-10">
          <form
            onSubmit={handleSendMessage}
            className="max-w-3xl mx-auto relative group"
          >
            <div className="absolute -inset-1 bg-gradient-to-r from-[#D4AF37]/0 via-[#D4AF37]/10 to-[#D4AF37]/0 rounded-3xl blur opacity-0 group-focus-within:opacity-100 transition duration-500"></div>
            <textarea
              ref={textareaRef}
              className="w-full px-6 py-4 pr-16 bg-[#0A0A0A] border border-[#2A2A2A] rounded-2xl shadow-2xl focus:outline-none focus:ring-1 focus:ring-[#D4AF37]/30 focus:border-[#D4AF37] transition-all resize-none text-white placeholder:text-[#B3B3B3] text-[15px] relative z-10 leading-relaxed"
              placeholder="Message MIKE... (Shift+Enter for new line)"
              value={inputMessage}
              onChange={(e) => {
                setInputMessage(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 150) + "px";
              }}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              rows={1}
              style={{ minHeight: "60px", maxHeight: "150px" }}
            />
            <button
              type="submit"
              disabled={isTyping || !inputMessage.trim()}
              className="absolute right-2 bottom-2 z-20 h-11 w-11 rounded-xl bg-[#D4AF37] hover:bg-[#F4C542] text-black flex items-center justify-center transition-all duration-300 shadow-md disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/40 hover:shadow-[0_0_15px_rgba(212,175,55,0.4)]"
              aria-label="Send message"
            >
              {isTyping ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5 ml-0.5" />}
            </button>
          </form>
          <p className="text-center text-[10px] text-[#B3B3B3] mt-3">
            MIKE can make mistakes. Always verify important legal information with a qualified professional.
          </p>
        </div>
      </div>
      
      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!chatToDelete} onOpenChange={(open) => !open && setChatToDelete(null)}>
        <AlertDialogContent className="bg-[#111111] border-[#2A2A2A] text-white">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
            <AlertDialogDescription className="text-[#B3B3B3]">
              This will permanently delete this conversation and remove it from your history. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-[#1A1A1A] border-[#2A2A2A] text-white hover:bg-[#2A2A2A] hover:text-white">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteChat} className="bg-red-500/20 text-red-400 hover:bg-red-500/30 hover:text-red-300 border border-red-500/30">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
