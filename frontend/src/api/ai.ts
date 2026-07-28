import { api } from "./axios";

export interface ConversationMessage {
  role: "user" | "ai";
  content: string;
  timestamp: string;
}

export interface AgentReply {
  conversation_id: string;
  reply: string;
  is_complete: boolean;
}

export interface ConversationDetail {
  id: string;
  case_id: string | null;
  is_complete: boolean;
  messages: ConversationMessage[];
  created_at: string;
  updated_at: string;
}

export interface ConversationListItem {
  id: string;
  case_id: string | null;
  title: string;
  is_complete: boolean;
  created_at: string;
}

export const aiApi = {
  startConversation: async (
    initialMessage: string,
    caseId?: string
  ): Promise<AgentReply> => {
    const payload = {
      initial_message: initialMessage,
      case_id: caseId || null,
    };

    const response = await api.post(
      "/api/v1/agent/conversations",
      payload
    );

    return response.data.data;
  },

  sendMessage: async (
    conversationId: string,
    message: string
  ): Promise<AgentReply> => {
    const response = await api.post(
      `/api/v1/agent/conversations/${conversationId}/message`,
      { message }
    );

    return response.data.data;
  },

  getConversation: async (
    conversationId: string
  ): Promise<ConversationDetail> => {
    const response = await api.get(
      `/api/v1/agent/conversations/${conversationId}`
    );

    return response.data.data;
  },

  listConversations: async (): Promise<ConversationListItem[]> => {
    const response = await api.get(
      "/api/v1/agent/conversations"
    );

    return response.data.data;
  },
};