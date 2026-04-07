import api from './api';
import type { ClientScript } from '../types';

export interface ClientScriptListResponse {
  total: number;
  items: ClientScript[];
  page: number;
  page_size: number;
}

export interface ClientScriptCreateData {
  name: string;
  description?: string;
  table_name?: string;
  sys_class_name?: string;
  event: string;
  trigger_field?: string;
  execution_order?: number;
  condition_logic?: string;
  conditions: any[];
  ui_actions: any[];
  is_active?: boolean;
}

export interface ClientScriptUpdateData {
  name?: string;
  description?: string;
  table_name?: string;
  sys_class_name?: string;
  event?: string;
  trigger_field?: string;
  execution_order?: number;
  condition_logic?: string;
  conditions?: any[];
  ui_actions?: any[];
  is_active?: boolean;
}

export const clientScriptService = {
  async list(params?: {
    page?: number;
    page_size?: number;
    table_name?: string;
    event?: string;
    search?: string;
  }): Promise<ClientScriptListResponse> {
    const response = await api.get<ClientScriptListResponse>('/client-scripts/', { params });
    return response.data;
  },

  async get(id: string): Promise<ClientScript> {
    const response = await api.get<ClientScript>(`/client-scripts/${id}`);
    return response.data;
  },

  async create(data: ClientScriptCreateData): Promise<ClientScript> {
    const response = await api.post<ClientScript>('/client-scripts/', data);
    return response.data;
  },

  async update(id: string, data: ClientScriptUpdateData): Promise<ClientScript> {
    const response = await api.put<ClientScript>(`/client-scripts/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/client-scripts/${id}`);
  },

  async toggle(id: string): Promise<ClientScript> {
    const response = await api.post<ClientScript>(`/client-scripts/${id}/toggle`);
    return response.data;
  },

  async getApplicable(tableName: string, sysClassName?: string): Promise<ClientScript[]> {
    const params: Record<string, string> = { table_name: tableName };
    if (sysClassName) params.sys_class_name = sysClassName;
    const response = await api.get<ClientScript[]>('/client-scripts/applicable', { params });
    return response.data;
  },
};

export default clientScriptService;
