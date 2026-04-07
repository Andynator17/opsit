export interface TableRegistryEntry {
  tableName: string;          // sys_db_object.name — used for metadata API
  sysClassName?: string;      // for polymorphic tables (task subtypes)
  label: string;
  pluralLabel: string;
  displayField: string;       // field shown as tab title: "number" or "name"

  // Feature flags for task-specific sections
  hasWorkNotes?: boolean;
  hasComments?: boolean;
  hasAttachments?: boolean;
  hasStatusWorkflow?: boolean;

  // Fixed filters applied to list queries
  defaultFilters?: Record<string, unknown>;
}

// Helper to create ticket type entries (all share the task table)
function ticketEntry(
  sysClassName: string,
  label: string,
  pluralLabel: string,
): TableRegistryEntry {
  return {
    tableName: 'task',
    sysClassName,
    label,
    pluralLabel,
    displayField: 'number',
    hasWorkNotes: true,
    hasComments: true,
    hasAttachments: true,
    hasStatusWorkflow: true,
    defaultFilters: { sys_class_name: sysClassName },
  };
}

export const TABLE_REGISTRY: Record<string, TableRegistryEntry> = {
  // Ticket types (all use unified task table)
  incident:  ticketEntry('incident',  'Incident',  'Incidents'),
  request:   ticketEntry('request',   'Request',   'Requests'),
  change:    ticketEntry('change',    'Change',    'Changes'),
  problem:   ticketEntry('problem',   'Problem',   'Problems'),
  task:      ticketEntry('task',      'Task',      'Tasks'),
  approval:  ticketEntry('approval',  'Approval',  'Approvals'),

  // Foundation tables
  company: {
    tableName: 'company',
    label: 'Company',
    pluralLabel: 'Companies',
    displayField: 'name',
  },
  user: {
    tableName: 'user',
    label: 'User',
    pluralLabel: 'Users',
    displayField: 'email',
  },
  department: {
    tableName: 'department',
    label: 'Department',
    pluralLabel: 'Departments',
    displayField: 'name',
  },
  location: {
    tableName: 'location',
    label: 'Location',
    pluralLabel: 'Locations',
    displayField: 'name',
  },
  'support-group': {
    tableName: 'support_group',
    label: 'Support Group',
    pluralLabel: 'Support Groups',
    displayField: 'name',
  },
  'permission-group': {
    tableName: 'permission_group',
    label: 'Permission Group',
    pluralLabel: 'Permission Groups',
    displayField: 'name',
  },
  role: {
    tableName: 'role',
    label: 'Role',
    pluralLabel: 'Roles',
    displayField: 'name',
  },

  // Cross-type search (no sys_class_name filter)
  search: {
    tableName: 'task',
    label: 'Task',
    pluralLabel: 'Search Results',
    displayField: 'number',
  },

  // System tables
  'server-script': {
    tableName: 'server_script',
    label: 'Server Script',
    pluralLabel: 'Server Scripts',
    displayField: 'name',
  },
  'client-script': {
    tableName: 'client_script',
    label: 'Client Script',
    pluralLabel: 'Client Scripts',
    displayField: 'name',
  },
};

// Ticket type list for quick checks
export const TICKET_TYPES = ['incident', 'request', 'change', 'problem', 'task', 'approval'];

export function isTicketType(key: string): boolean {
  return TICKET_TYPES.includes(key);
}
