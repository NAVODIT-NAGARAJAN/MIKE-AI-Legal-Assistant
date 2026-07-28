import { api } from "./axios";

export interface RoadmapStep {
  step_number: number;
  title: string;
  description: string;
  is_done: boolean;
}

export interface ConsumerRight {
  right: string;
  description: string;
  legal_citation: string;
}

export interface EvidenceItem {
  item: string;
  is_required: boolean;
  description: string;
}

export interface Report {
  id: string;
  case_id: string;
  case_summary: string;
  consumer_rights: ConsumerRight[];
  roadmap_steps: RoadmapStep[];
  evidence_items: EvidenceItem[];
  next_steps: string;
  recommended_authority: string;
  created_at: string;
}

export const reportsApi = {
  generateReport: async (conversationId: string): Promise<Report> => {
    const response = await api.post(`/api/v1/reports/generate/${conversationId}`);
    return response.data.data;
  },

  getReport: async (caseId: string): Promise<Report> => {
    const response = await api.get(`/api/v1/reports/${caseId}`);
    return response.data.data;
  },

  downloadPdfUrl: (caseId: string): string => {
    return `${api.defaults.baseURL}/api/v1/reports/${caseId}/download`;
  }
};
