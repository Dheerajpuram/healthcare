import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  ApiResponse, 
  LoginResponse, 
  AppointmentsResponse, 
  DoctorsResponse, 
  AvailableSlotsResponse, 
  DashboardResponse,
  NotificationsResponse,
  User,
  Appointment,
  Resource
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config: any) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: any) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic methods
  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await this.api.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.put(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.api.delete(url);
    return response.data;
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.api.post('/auth/login', { email, password });
    return response.data;
  }

  async register(userData: any): Promise<LoginResponse> {
    const response = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.get('/auth/me');
  }

  async refreshToken() {
    return this.post('/auth/refresh');
  }

  async logout() {
    return this.post('/auth/logout');
  }

  // Appointments
  async getAppointments(params?: any): Promise<AppointmentsResponse> {
    const response = await this.api.get('/appointments', { params });
    return response.data;
  }

  async createAppointment(data: any): Promise<ApiResponse<Appointment>> {
    return this.post('/appointments', data);
  }

  async getAppointment(id: number): Promise<ApiResponse<Appointment>> {
    return this.get(`/appointments/${id}`);
  }

  async updateAppointment(id: number, data: any): Promise<ApiResponse<Appointment>> {
    return this.put(`/appointments/${id}`, data);
  }

  async cancelAppointment(id: number): Promise<ApiResponse<any>> {
    return this.delete(`/appointments/${id}`);
  }

  async getDoctors(): Promise<DoctorsResponse> {
    const response = await this.api.get('/appointments/doctors');
    return response.data;
  }

  async getAvailableSlots(doctorId: number, date: string): Promise<AvailableSlotsResponse> {
    const response = await this.api.get('/appointments/available-slots', { 
      params: { doctor_id: doctorId, date } 
    });
    return response.data;
  }

  // Resources
  async getResources(params?: any) {
    return this.get('/resources', params);
  }

  async createResource(data: any) {
    return this.post('/resources', data);
  }

  async getResource(id: number) {
    return this.get(`/resources/${id}`);
  }

  async updateResource(id: number, data: any) {
    return this.put(`/resources/${id}`, data);
  }

  async deleteResource(id: number) {
    return this.delete(`/resources/${id}`);
  }

  async createResourceTransaction(resourceId: number, data: any) {
    return this.post(`/resources/${resourceId}/transactions`, data);
  }

  async getResourceTransactions(resourceId: number, params?: any) {
    return this.get(`/resources/${resourceId}/transactions`, params);
  }

  async getResourceAlerts() {
    return this.get('/resources/alerts');
  }

  // Users
  async getUsers(params?: any) {
    return this.get('/users', params);
  }

  async getUser(id: number) {
    return this.get(`/users/${id}`);
  }

  async updateUser(id: number, data: any) {
    return this.put(`/users/${id}`, data);
  }

  async deactivateUser(id: number) {
    return this.post(`/users/${id}/deactivate`);
  }

  async activateUser(id: number) {
    return this.post(`/users/${id}/activate`);
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardResponse> {
    const response = await this.api.get('/dashboard/stats');
    return response.data;
  }

  async getNotifications(): Promise<NotificationsResponse> {
    const response = await this.api.get('/dashboard/notifications');
    return response.data;
  }
}

export const apiService = new ApiService();
