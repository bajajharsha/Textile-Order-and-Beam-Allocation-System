import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types
export interface Party {
  id?: number;
  party_name: string;
  contact_number: string;
  broker_name?: string;
  gst?: string;
  address?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Color {
  id: number;
  color_code: string;
  color_name: string;
  is_active: boolean;
}

export interface Quality {
  id: number;
  quality_name: string;
  feeder_count: number;
  specification?: string;
  is_active: boolean;
}

export interface Cut {
  id: number;
  cut_value: string;
  description?: string;
  is_active: boolean;
}

export interface GroundColorItem {
  ground_color_name: string;
  beam_color_id: number;
}

export interface OrderCreate {
  party_id: number;
  quality_id: number;
  units: number;
  cuts: string[];
  design_numbers: string[];
  ground_colors: GroundColorItem[];
  rate_per_piece: number;
  notes?: string;
}

export interface BeamColorSummary {
  beam_color_id: number;
  beam_color_name: string;
  total_pieces: number;
}

export interface BeamDetailItem {
  party_name: string;
  quality_name: string;
  color_per_beam: string;
  colors: {
    red: number;
    firozi: number;
    gold: number;
    royal_blue: number;
    black: number;
    white: number;
    yellow: number;
    green: number;
    purple: number;
    orange: number;
  };
  total: number;
}

export interface BeamDetailByQuality {
  quality_name: string;
  items: BeamDetailItem[];
}

export interface OrderResponse {
  id: number;
  order_number: string;
  party_id: number;
  quality_id: number;
  units: number;
  order_date: string;
  rate_per_piece: number;
  total_designs: number;
  total_pieces: number;
  total_value: number;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  
  // Related data
  party_name?: string;
  quality_name?: string;
  cuts: string[];
  design_numbers: string[];
  ground_colors: GroundColorItem[];
  beam_summary: { [key: string]: number }; // {"R": 1, "B": 2}
  beam_colors: BeamColorSummary[];
}

export interface DropdownData {
  parties: Array<{ id: number; name: string }>;
  colors: Color[];
  qualities: Quality[];
  cuts: Cut[];
}

// API Functions
export const partyApi = {
  getAll: (page = 1, pageSize = 20) => 
    api.get<{ parties: Party[]; total: number; page: number; page_size: number }>(`/parties?page=${page}&page_size=${pageSize}`),
  
  getById: (id: number) => 
    api.get<Party>(`/parties/${id}`),
  
  create: (data: Omit<Party, 'id'>) => 
    api.post<Party>('/parties', data),
  
  update: (id: number, data: Partial<Party>) => 
    api.put<Party>(`/parties/${id}`, data),
  
  delete: (id: number) => 
    api.delete(`/parties/${id}`),
  
  search: (query: string, limit = 20) => 
    api.get<{ parties: Party[]; total: number }>(`/parties/search?q=${encodeURIComponent(query)}&limit=${limit}`)
};

export const masterApi = {
  getDropdownData: () => 
    api.get<DropdownData>('/master/dropdown-data'),
  
  // Colors
  createColor: (data: { color_code: string; color_name: string }) => 
    api.post<Color>('/master/colors', data),
  
  // Qualities  
  createQuality: (data: { quality_name: string; feeder_count: number; specification?: string }) => 
    api.post<Quality>('/master/qualities', data),
  
  // Cuts
  createCut: (data: { cut_value: string; description?: string }) => 
    api.post<Cut>('/master/cuts', data)
};

export const orderApi = {
  getAll: (page = 1, pageSize = 20) => 
    api.get<{ orders: OrderResponse[]; total: number; page: number; page_size: number }>(`/orders?page=${page}&page_size=${pageSize}`),
  
  getById: (id: number) => 
    api.get<OrderResponse>(`/orders/${id}`),
  
  create: (data: OrderCreate) => 
    api.post<OrderResponse>('/orders', data),
  
  calculateBeamPreview: (data: {
    units: number;
    ground_colors: GroundColorItem[];
    design_numbers: string[];
  }) => 
    api.post<{ beam_summary: BeamColorSummary[] }>('/orders/preview', data),
  
  getBeamDetails: () => 
    api.get<BeamDetailByQuality[]>('/orders/beam-details'),
  
  update: (id: number, data: Partial<OrderCreate>) => 
    api.put<OrderResponse>(`/orders/${id}`, data),
  
  delete: (id: number) => 
    api.delete(`/orders/${id}`),
  
  search: (query: string, limit = 20) => 
    api.get<{ orders: OrderResponse[]; total: number }>(`/orders/search?q=${encodeURIComponent(query)}&limit=${limit}`)
};

export default api;
