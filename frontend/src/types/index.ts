export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: 'patient' | 'doctor' | 'admin';
  is_active: boolean;
  specialty?: string;
  license_number?: string;
  experience_years?: number;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  emergency_contact?: string;
  created_at: string;
  updated_at: string;
}

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  patient_name?: string;
  doctor_name?: string;
  appointment_date: string;
  appointment_time: string;
  duration_minutes: number;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed' | 'no_show';
  reason?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Resource {
  id: number;
  name: string;
  resource_type: 'bed' | 'medicine' | 'equipment';
  category?: string;
  total_quantity: number;
  available_quantity: number;
  unit?: string;
  description?: string;
  location?: string;
  expiry_date?: string;
  min_threshold: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResourceTransaction {
  id: number;
  resource_id: number;
  transaction_type: 'in' | 'out' | 'adjustment';
  quantity: number;
  reason?: string;
  reference_id?: string;
  created_by?: number;
  created_at: string;
}

export interface Billing {
  id: number;
  appointment_id: number;
  patient_id: number;
  total_amount: number;
  consultation_fee: number;
  additional_charges: number;
  discount: number;
  tax_amount: number;
  status: 'pending' | 'paid' | 'cancelled' | 'refunded';
  payment_method?: 'cash' | 'card' | 'insurance' | 'online';
  payment_reference?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  appointments: {
    total: number;
    scheduled: number;
    confirmed: number;
    completed: number;
    cancelled: number;
  };
  upcoming_appointments?: Appointment[];
  resources?: {
    total_resources: number;
    total_beds: number;
    total_medicines: number;
    total_equipment: number;
    low_stock_count: number;
    expired_medicines: number;
  };
  occupancy?: {
    total_beds: number;
    occupied_beds: number;
    available_beds: number;
    occupancy_rate: number;
  };
}

export interface Notification {
  type: 'appointment_reminder' | 'low_stock' | 'expired' | 'general';
  title: string;
  message: string;
  date: string;
  priority: 'low' | 'medium' | 'high';
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  total?: number;
  pages?: number;
  current_page?: number;
  per_page?: number;
}

// Specific response types for different endpoints
export interface LoginResponse {
  user: User;
  access_token: string;
}

export interface AppointmentsResponse {
  appointments: Appointment[];
  pages: number;
  total: number;
}

export interface DoctorsResponse {
  doctors: User[];
}

export interface AvailableSlotsResponse {
  available_slots: string[];
}

export interface DashboardResponse {
  stats: DashboardStats;
  notifications: Notification[];
}

export interface NotificationsResponse {
  notifications: Notification[];
}
