import React, { useState, useEffect, useRef } from "react";
import {
  useParams,
  useNavigate,
  Link,
  useSearchParams,
} from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Bot, User, Loader2, Plus, MessageSquare, Menu, Scale } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "../../components/ui/Button";
import { useAuth } from "../../context/AuthContext";
import {
  aiApi as apiService,
  ConversationMessage as Msg,
  AgentReply,
  ConversationListItem,
} from "../../api/ai";
import { motion, AnimatePresence } from "framer-motion";

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

  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Load history for sidebar
  useEffect(() => {
    loadRecentChats();
  }, []);

  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    } else {
      setMessages([
        {
          role: "ai",
          content: "Hello! I am LegalEase AI, your consumer rights assistant. Please describe your consumer issue in detail so I can analyze it and guide you on your rights.",
          timestamp: new Date().toISOString(),
        }
      ]);
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

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMsg: Msg = {
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInputMessage("");
    setIsTyping(true);

    try {
      let replyData: AgentReply;
      
      if (conversationId) {
        replyData = await apiService.sendMessage(conversationId, userMsg.content);
      } else {
        replyData = await apiService.startConversation(
          userMsg.content,
          caseId ?? undefined
        );

        await loadRecentChats();

        navigate(`/chat/${replyData.conversation_id}`, {
          replace: true,
        });
      }

      const aiMsg: Msg = {
        role: "ai",
        content: replyData.reply,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMsg]);
      
      if (replyData.is_complete) {
        toast.info("Consultation completed. The report is being generated.");
      }
    } catch (err: any) {
      let errorMsg = "Failed to communicate with AI Agent.";
      if (err.response?.data) {
        if (err.response.data.message) {
          errorMsg = err.response.data.message;
        }
        if (Array.isArray(err.response.data.errors) && err.response.data.errors.length > 0) {
          // Append the first specific field error if available
          errorMsg += ` (${err.response.data.errors[0].message})`;
        }
      }
      toast.error(errorMsg);
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="flex h-[calc(100dvh-6rem)] md:h-[calc(100dvh-4rem)] bg-white border border-gray-200 rounded-2xl shadow-lg overflow-hidden relative">
      
      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 z-40 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div 
        className={`w-72 bg-gray-50 border-r border-gray-200 flex flex-col absolute inset-y-0 left-0 z-50 transform md:relative md:translate-x-0 transition-transform duration-300 ease-in-out ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="p-4 border-b border-gray-200 bg-white">
          <Button onClick={() => { navigate("/chat"); setIsSidebarOpen(false); }} className="w-full flex items-center justify-center shadow-sm">
            <Plus className="mr-2 h-4 w-4" /> New Chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">
            Recent Chats
          </h3>
          {isLoadingHistory ? (
            <div className="text-center py-4 text-sm text-gray-400">Loading history...</div>
          ) : recentChats.length === 0 ? (
            <div className="text-center py-4 text-sm text-gray-400">
                No recent chats
            </div>
          ) : (
            recentChats.map(chat => (
              <Link
                key={chat.id}
                to={`/chat/${chat.id}`}
                onClick={() => setIsSidebarOpen(false)}
                className={`flex items-start space-x-2 p-2.5 rounded-xl transition-colors duration-200 ${conversationId === chat.id ? 'bg-blue-100 text-blue-900' : 'hover:bg-gray-200 text-gray-700'}`}
              >
                <MessageSquare className={`h-4 w-4 mt-0.5 ${conversationId === chat.id ? 'text-blue-600' : 'text-gray-400'}`} />
                <div className="text-sm font-medium truncate">
                  {chat.title}
                </div>
              </Link>
            ))
          )}
        </div>
      </motion.div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative w-full">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-md border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center space-x-3">
            <button 
              className="md:hidden p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu size={20} />
            </button>
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-xl shadow-sm hidden sm:block">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-semibold text-gray-900">LegalEase AI</h2>
              <p className="text-xs sm:text-sm text-gray-500">Consumer Rights Expert</p>
            </div>
          </div>
        </div>

        {/* Chat Feed */}
        <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 space-y-6 bg-white scroll-smooth pb-32">
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-8">
              {messages.map((msg, idx) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  key={idx} 
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex max-w-[90%] sm:max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    
                    {/* Avatar */}
                    <div className="flex-shrink-0">
                      {msg.role === "user" ? (
                        <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-medium text-sm ml-3 shadow-sm">
                          {user?.full_name?.charAt(0).toUpperCase() || <User size={16} />}
                        </div>
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mr-3 shadow-sm">
                          <Scale className="h-4 w-4 text-white" />
                        </div>
                      )}
                    </div>

                    {/* Message Bubble */}
                    <div className={`
                      px-5 py-3.5 rounded-2xl
                      ${msg.role === "user" 
                        ? "bg-indigo-600 text-white rounded-tr-sm shadow-sm" 
                        : "bg-gray-50 border border-gray-200/60 text-gray-800 rounded-tl-sm prose prose-sm sm:prose-base prose-blue max-w-none shadow-sm"
                      }
                    `}>
                      {msg.role === "user" ? (
                        <p className="whitespace-pre-wrap m-0 font-medium">{msg.content}</p>
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                  <div className="flex max-w-[80%] flex-row">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mr-3 shadow-sm">
                        <Scale className="h-4 w-4 text-white" />
                      </div>
                    </div>
                    <div className="px-5 py-4 bg-gray-50 border border-gray-200/60 rounded-2xl rounded-tl-sm shadow-sm flex space-x-1.5 items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.15s" }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.3s" }}></div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area - Floating at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-white via-white to-transparent pt-10">
          <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto relative group">
            <textarea
              className="w-full px-5 py-4 pr-16 bg-white border border-gray-300 rounded-2xl shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none overflow-hidden text-gray-900"
              placeholder="Ask LegalEase AI..."
              value={inputMessage}
              onChange={(e) => {
                setInputMessage(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              rows={1}
              style={{ minHeight: '56px', maxHeight: '120px' }}
            />
            <button
              type="submit"
              disabled={isTyping || !inputMessage.trim()}
              className="absolute right-2 bottom-2 inline-flex items-center justify-center h-10 w-10 border border-transparent rounded-xl text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-40 transition-all shadow-md"
            >
              <Send className="h-4 w-4 ml-0.5" />
            </button>
          </form>
          <div className="text-center mt-2 pb-1">
            <span className="text-[10px] text-gray-400">LegalEase AI can make mistakes. Verify legal information.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
