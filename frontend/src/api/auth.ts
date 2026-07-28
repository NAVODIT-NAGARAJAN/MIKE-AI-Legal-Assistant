import { api } from "./axios";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  register: async (data: { full_name: string; email: string; password: string }) => {
    const response = await api.post("/api/v1/auth/register", data);
    return response.data;
  },

  login: async (data: { email: string; password: string }): Promise<LoginResponse> => {
    const response = await api.post("/api/v1/auth/login", data);
    return response.data.data;
  },

  logout: async () => {
    const response = await api.post("/api/v1/auth/logout");
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get("/api/v1/users/profile");
    return response.data.data;
  }
};
