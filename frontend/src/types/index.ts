// API Response Types

export interface User {
  id: string;
  user_id: string;
  tenant_id: string;
  primary_company_id: string;

  // Authentication
  email: string;
  email_secondary?: string;

  // Personal Information
  employee_id?: string;
  salutation?: string;
  title?: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  full_name?: string;
  gender?: string;

  // Contact Information
  phone?: string;
  phone_secondary?: string;
  mobile?: string;

  // Work Information
  job_title?: string;
  department?: string;
  location?: string;
  department_id?: string;
  location_id?: string;

  // User Type & Roles
  user_type: string;
  is_vip: boolean;
  is_admin: boolean;
  is_support_agent: boolean;
  is_active: boolean;

  // Preferences
  language: string;
  timezone: string;
  avatar_url?: string;

  // Security
  locked_until?: string;
  failed_login_attempts?: number;

  // Timestamps
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

// Auth Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

// Portal Types
export interface Portal {
  id: string;
  name: string;
  slug: string;
  description?: string;
  audience_type: 'internal' | 'company' | 'external';
  company_id?: string;
  logo_url?: string;
  primary_color: string;
  accent_color: string;
  welcome_title?: string;
  welcome_message?: string;
  enabled_modules: string[];
  default_ticket_type: string;
}

export interface PortalStats {
  open_incidents: number;
  open_requests: number;
  pending_approvals: number;
  resolved_last_30_days: number;
  total_tickets: number;
}

// Client Scripts (Browser-Side UI Rules)
export interface ClientScriptCondition {
  field: string;
  operator: string;
  value?: any;
}

export interface ClientScriptUIAction {
  type: string; // set_hidden, set_readonly, set_mandatory, set_value
  field: string;
  value?: any;
}

export interface ClientScript {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  table_name: string;
  sys_class_name?: string;
  event: string; // on_load, on_change, on_submit
  trigger_field?: string;
  execution_order: number;
  condition_logic: string;
  conditions: ClientScriptCondition[];
  ui_actions: ClientScriptUIAction[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
