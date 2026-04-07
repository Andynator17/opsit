import api from './api';
import type { TableMetadataResponse, FormLayoutResponse, ListLayoutResponse } from '../types/metadata';

export const metadataService = {
  async getTableMetadata(tableName: string, sysClassName?: string): Promise<TableMetadataResponse> {
    const params: Record<string, string> = {};
    if (sysClassName) params.sys_class_name = sysClassName;
    return (await api.get(`/sys/metadata/${tableName}`, { params })).data;
  },

  async getFormLayout(tableName: string, viewName = 'default', sysClassName?: string): Promise<FormLayoutResponse> {
    const params: Record<string, string> = { view_name: viewName };
    if (sysClassName) params.sys_class_name = sysClassName;
    return (await api.get(`/sys/form-layout/${tableName}`, { params })).data;
  },

  async getListLayout(tableName: string, viewName = 'default', sysClassName?: string): Promise<ListLayoutResponse> {
    const params: Record<string, string> = { view_name: viewName };
    if (sysClassName) params.sys_class_name = sysClassName;
    return (await api.get(`/sys/list-layout/${tableName}`, { params })).data;
  },
};
