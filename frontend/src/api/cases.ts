import { api } from "./axios";

export interface Case {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category: string;
  product_or_service: string;
  seller_name: string | null;
  purchase_date: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CaseListItem {
  id: string;
  title: string;
  category: string;
  status: string;
  product_or_service: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCaseRequest {
  title: string;
  description: string;
  category: string;
  product_or_service: string;
  seller_name?: string | null;
  purchase_date?: string | null;
}

export interface UpdateCaseRequest {
  title?: string;
  description?: string;
  product_or_service?: string;
  seller_name?: string | null;
  purchase_date?: string | null;
}

export const casesApi = {
  listCases: async (skip: number = 0, limit: number = 20): Promise<{items: CaseListItem[], total: number}> => {
    // The backend returns a dict in data, e.g. { items: [...], total: X }
    const response = await api.get("/api/v1/cases", { params: { skip, limit } });
    return response.data.data;
  },

  getCase: async (id: string): Promise<Case> => {
    const response = await api.get(`/api/v1/cases/${id}`);
    return response.data.data;
  },

  createCase: async (data: CreateCaseRequest): Promise<Case> => {
    const response = await api.post("/api/v1/cases", data);
    return response.data.data;
  },

  updateCase: async (id: string, data: UpdateCaseRequest): Promise<Case> => {
    const response = await api.put(`/api/v1/cases/${id}`, data);
    return response.data.data;
  },

  deleteCase: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/cases/${id}`);
  }
};
