import { apiService } from './api';
import { User } from '../types';

export const authService = {
  async login(email: string, password: string) {
    const response = await apiService.login(email, password);
    return response;
  },

  async register(userData: any) {
    const response = await apiService.register(userData);
    return response;
  },

  async getCurrentUser(token?: string): Promise<User | null> {
    const response = await apiService.getCurrentUser();
    return response.data || null;
  },

  async refreshToken() {
    const response = await apiService.refreshToken();
    return response;
  },

  async logout() {
    await apiService.logout();
  }
};
