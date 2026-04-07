import api from './api';

// Per-table API configuration to handle backend route inconsistencies
interface TableApiConfig {
  basePath: string;
  updateMethod: 'put' | 'patch';
  listResponseKey?: string; // key in response holding the array; undefined = plain array
}

const TABLE_API_CONFIG: Record<string, TableApiConfig> = {
  task:             { basePath: '/tasks',             updateMethod: 'put',   listResponseKey: 'tasks' },
  company:          { basePath: '/companies',         updateMethod: 'patch' },
  user:             { basePath: '/users',             updateMethod: 'put' },
  department:       { basePath: '/departments',       updateMethod: 'patch', listResponseKey: 'departments' },
  location:         { basePath: '/locations',          updateMethod: 'patch', listResponseKey: 'locations' },
  support_group:    { basePath: '/support-groups',    updateMethod: 'patch', listResponseKey: 'groups' },
  permission_group: { basePath: '/permission-groups', updateMethod: 'patch', listResponseKey: 'permission_groups' },
  role:             { basePath: '/roles',             updateMethod: 'patch', listResponseKey: 'roles' },
  server_script:    { basePath: '/server-scripts',    updateMethod: 'put',   listResponseKey: 'items' },
  client_script:    { basePath: '/client-scripts',    updateMethod: 'put',   listResponseKey: 'items' },
  sys_db_object:    { basePath: '/sys/tables',        updateMethod: 'put',   listResponseKey: 'items' },
};

function getConfig(tableName: string): TableApiConfig {
  const config = TABLE_API_CONFIG[tableName];
  if (!config) throw new Error(`No API config for table: ${tableName}`);
  return config;
}

export interface RecordListResult {
  items: Record<string, unknown>[];
  total: number;
}

export const recordService = {
  async getRecords(tableName: string, params?: Record<string, unknown>): Promise<RecordListResult> {
    const config = getConfig(tableName);
    const response = await api.get(config.basePath + '/', { params });
    const data = response.data;

    if (config.listResponseKey) {
      // Paginated/keyed response: { total, [key]: [...] }
      return {
        items: data[config.listResponseKey] ?? data.items ?? [],
        total: data.total ?? 0,
      };
    }

    // Plain array response
    const items = Array.isArray(data) ? data : [];
    return { items, total: items.length };
  },

  async getRecord(tableName: string, id: string): Promise<Record<string, unknown>> {
    const config = getConfig(tableName);
    return (await api.get(`${config.basePath}/${id}`)).data;
  },

  async createRecord(tableName: string, data: Record<string, unknown>): Promise<Record<string, unknown>> {
    const config = getConfig(tableName);
    return (await api.post(config.basePath + '/', data)).data;
  },

  async updateRecord(tableName: string, id: string, data: Record<string, unknown>): Promise<Record<string, unknown>> {
    const config = getConfig(tableName);
    if (config.updateMethod === 'put') {
      return (await api.put(`${config.basePath}/${id}`, data)).data;
    }
    return (await api.patch(`${config.basePath}/${id}`, data)).data;
  },

  async deleteRecord(tableName: string, id: string): Promise<void> {
    const config = getConfig(tableName);
    await api.delete(`${config.basePath}/${id}`);
  },
};
