import api from './api';

export interface AuditChangedBy {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface AuditLogEntry {
  id: string;
  tenant_id: string;
  table_name: string;
  record_id: string;
  action: string;
  field_name?: string;
  old_value?: string;
  new_value?: string;
  changed_by_id: string;
  changed_by?: AuditChangedBy;
  changed_at: string;
}

export interface AuditLogListResponse {
  total: number;
  audit_logs: AuditLogEntry[];
}

const auditService = {
  async getAuditLogs(taskId: string): Promise<AuditLogEntry[]> {
    const response = await api.get<AuditLogListResponse>(
      `/tasks/${taskId}/audit-logs/`
    );
    return response.data.audit_logs;
  },
};

export default auditService;
