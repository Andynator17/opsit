import api from './api';
import type { Portal, PortalStats } from '../types';

export interface PortalTicketListResponse {
  total: number;
  tasks: any[];
  page: number;
  page_size: number;
}

export interface PortalCreateTicketData {
  sys_class_name?: string;
  short_description: string;
  description?: string;
  category?: string;
  subcategory?: string;
  urgency?: string;
  impact?: string;
}

export interface PortalCategory {
  id: string;
  name: string;
  description?: string;
  category_type: string;
  parent_category_id?: string;
  level: number;
  icon?: string;
  color?: string;
}

export const portalService = {
  // Portal config
  async getMyPortals(): Promise<Portal[]> {
    const response = await api.get<Portal[]>('/portals/my');
    return response.data;
  },

  async getPortalBySlug(slug: string): Promise<Portal> {
    const response = await api.get<Portal>(`/portals/by-slug/${slug}`);
    return response.data;
  },

  // My stats
  async getMyStats(): Promise<PortalStats> {
    const response = await api.get<PortalStats>('/portal/me/stats');
    return response.data;
  },

  // My tickets
  async getMyTickets(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    type?: string;
  }): Promise<PortalTicketListResponse> {
    const response = await api.get<PortalTicketListResponse>('/portal/me/tickets', { params });
    return response.data;
  },

  async getMyTicket(id: string): Promise<any> {
    const response = await api.get(`/portal/me/ticket/${id}`);
    return response.data;
  },

  async createTicket(data: PortalCreateTicketData): Promise<any> {
    const response = await api.post('/portal/me/tickets', data);
    return response.data;
  },

  // Comments
  async addComment(ticketId: string, text: string): Promise<any> {
    const response = await api.post(`/portal/me/ticket/${ticketId}/comments`, { text });
    return response.data;
  },

  // Categories
  async getCategories(categoryType?: string): Promise<PortalCategory[]> {
    const params = categoryType ? { category_type: categoryType } : {};
    const response = await api.get<PortalCategory[]>('/portal/me/categories', { params });
    return response.data;
  },
};

export default portalService;
