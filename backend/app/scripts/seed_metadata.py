"""Seed metadata — sys_db_object, sys_dictionary, sys_choice, sys_relationship, sys_ui_view/section/element/list

Idempotent: checks if sys_db_object has any records before seeding.
All records are tenant_id=None (system-global).

Usage:
    cd backend
    .venv/Scripts/python.exe -m app.scripts.seed_metadata
    .venv/Scripts/python.exe -m app.scripts.seed_metadata --force   # re-seed from scratch
"""
import sys
import asyncio
from sqlalchemy import select, delete

from app.core.database import AsyncSessionLocal
from app.models.sys_db_object import SysDbObject
from app.models.sys_dictionary import SysDictionary
from app.models.sys_choice import SysChoice
from app.models.sys_relationship import SysRelationship
from app.models.sys_ui_view import SysUiView
from app.models.sys_ui_section import SysUiSection
from app.models.sys_ui_element import SysUiElement
from app.models.sys_ui_list import SysUiList


# ===========================================================================
# 1. TABLE REGISTRY (sys_db_object)
# ===========================================================================
TABLES = [
    {"name": "task", "label": "Task", "plural_label": "Tasks", "super_class": None, "display_field": "number", "number_prefix": "TASK", "module": "fulfillment"},
    {"name": "incident", "label": "Incident", "plural_label": "Incidents", "super_class": "task", "display_field": "number", "number_prefix": "INC", "module": "fulfillment"},
    {"name": "request", "label": "Request", "plural_label": "Requests", "super_class": "task", "display_field": "number", "number_prefix": "REQ", "module": "fulfillment"},
    {"name": "change", "label": "Change", "plural_label": "Changes", "super_class": "task", "display_field": "number", "number_prefix": "CHG", "module": "fulfillment"},
    {"name": "problem", "label": "Problem", "plural_label": "Problems", "super_class": "task", "display_field": "number", "number_prefix": "PRB", "module": "fulfillment"},
    {"name": "approval", "label": "Approval", "plural_label": "Approvals", "super_class": "task", "display_field": "number", "number_prefix": "APPR", "module": "fulfillment"},
    {"name": "company", "label": "Company", "plural_label": "Companies", "super_class": None, "display_field": "name", "number_prefix": None, "module": "foundation"},
    {"name": "user", "label": "User", "plural_label": "Users", "super_class": None, "display_field": "full_name", "number_prefix": None, "module": "foundation"},
    {"name": "support_group", "label": "Support Group", "plural_label": "Support Groups", "super_class": None, "display_field": "name", "number_prefix": None, "module": "foundation"},
    {"name": "department", "label": "Department", "plural_label": "Departments", "super_class": None, "display_field": "name", "number_prefix": None, "module": "foundation"},
    {"name": "location", "label": "Location", "plural_label": "Locations", "super_class": None, "display_field": "name", "number_prefix": None, "module": "foundation"},
    {"name": "category", "label": "Category", "plural_label": "Categories", "super_class": None, "display_field": "name", "number_prefix": None, "module": "foundation"},
    {"name": "role", "label": "Role", "plural_label": "Roles", "super_class": None, "display_field": "name", "number_prefix": None, "module": "system"},
    {"name": "permission_group", "label": "Permission Group", "plural_label": "Permission Groups", "super_class": None, "display_field": "name", "number_prefix": None, "module": "system"},
    {"name": "server_script", "label": "Server Script", "plural_label": "Server Scripts", "super_class": None, "display_field": "name", "number_prefix": None, "module": "system"},
    {"name": "client_script", "label": "Client Script", "plural_label": "Client Scripts", "super_class": None, "display_field": "name", "number_prefix": None, "module": "system"},
]

# ===========================================================================
# 2. FIELD DICTIONARY (sys_dictionary) — matches actual SQLAlchemy models
# ===========================================================================
TASK_FIELDS = [
    {"column_name": "number", "label": "Number", "field_type": "string", "max_length": 40, "is_mandatory": True, "is_read_only": True, "is_display": True, "is_system": True, "sort_order": 1},
    {"column_name": "sys_class_name", "label": "Class", "field_type": "string", "max_length": 50, "is_mandatory": True, "is_read_only": True, "is_system": True, "sort_order": 2},
    {"column_name": "sys_id", "label": "Sys ID", "field_type": "uuid", "is_read_only": True, "is_system": True, "sort_order": 3},
    {"column_name": "sys_created_on", "label": "Created", "field_type": "datetime", "is_read_only": True, "is_system": True, "sort_order": 4},
    {"column_name": "sys_updated_on", "label": "Updated", "field_type": "datetime", "is_read_only": True, "is_system": True, "sort_order": 5},
    {"column_name": "short_description", "label": "Short Description", "field_type": "string", "max_length": 255, "is_mandatory": True, "hint": "Brief summary", "sort_order": 10},
    {"column_name": "description", "label": "Description", "field_type": "text", "hint": "Detailed description", "sort_order": 11},
    {"column_name": "opened_by_id", "label": "Opened By", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "is_mandatory": True, "is_read_only": True, "is_system": True, "sort_order": 20},
    {"column_name": "caller_id", "label": "Caller", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "sort_order": 21},
    {"column_name": "affected_user_id", "label": "Affected User", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "sort_order": 22},
    {"column_name": "company_id", "label": "Company", "field_type": "reference", "reference_table": "company", "is_mandatory": True, "sort_order": 23},
    {"column_name": "caller_company_id", "label": "Caller Company", "field_type": "reference", "reference_table": "company", "sort_order": 24},
    {"column_name": "affected_user_company_id", "label": "Affected User Company", "field_type": "reference", "reference_table": "company", "sort_order": 25},
    {"column_name": "assignment_group_id", "label": "Assignment Group", "field_type": "reference", "reference_table": "support_group", "sort_order": 30},
    {"column_name": "assigned_to_id", "label": "Assigned To", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "sort_order": 31},
    {"column_name": "reassignment_count", "label": "Reassignment Count", "field_type": "integer", "is_read_only": True, "default_value": "0", "sort_order": 32},
    {"column_name": "category", "label": "Category", "field_type": "choice", "sort_order": 40},
    {"column_name": "subcategory", "label": "Subcategory", "field_type": "choice", "sort_order": 41},
    {"column_name": "channel", "label": "Channel", "field_type": "choice", "default_value": "web", "sort_order": 42},
    {"column_name": "contact_type", "label": "Contact Type", "field_type": "choice", "default_value": "email", "sort_order": 43},
    {"column_name": "impact", "label": "Impact", "field_type": "choice", "is_mandatory": True, "sort_order": 50},
    {"column_name": "urgency", "label": "Urgency", "field_type": "choice", "is_mandatory": True, "sort_order": 51},
    {"column_name": "priority", "label": "Priority", "field_type": "choice", "is_mandatory": True, "is_read_only": True, "sort_order": 52},
    {"column_name": "status", "label": "Status", "field_type": "choice", "is_mandatory": True, "sort_order": 60},
    {"column_name": "status_reason", "label": "Status Reason", "field_type": "string", "max_length": 100, "sort_order": 61},
    {"column_name": "resolved_by_id", "label": "Resolved By", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "is_read_only": True, "sort_order": 70},
    {"column_name": "resolved_at", "label": "Resolved At", "field_type": "datetime", "is_read_only": True, "sort_order": 71},
    {"column_name": "resolution", "label": "Resolution", "field_type": "text", "sort_order": 72},
    {"column_name": "resolution_reason", "label": "Resolution Reason", "field_type": "choice", "sort_order": 73},
    {"column_name": "close_notes", "label": "Close Notes", "field_type": "text", "sort_order": 74},
    {"column_name": "closed_by_id", "label": "Closed By", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "is_read_only": True, "sort_order": 75},
    {"column_name": "closed_at", "label": "Closed At", "field_type": "datetime", "is_read_only": True, "sort_order": 76},
    {"column_name": "root_cause", "label": "Root Cause", "field_type": "text", "sort_order": 80},
    {"column_name": "workaround", "label": "Workaround", "field_type": "text", "sort_order": 81},
    {"column_name": "sla_target_respond", "label": "SLA Response Target", "field_type": "datetime", "is_read_only": True, "sort_order": 90},
    {"column_name": "sla_target_resolve", "label": "SLA Resolve Target", "field_type": "datetime", "is_read_only": True, "sort_order": 91},
    {"column_name": "sla_breach", "label": "SLA Breached", "field_type": "boolean", "is_read_only": True, "default_value": "false", "sort_order": 92},
    {"column_name": "parent_task_id", "label": "Parent Task", "field_type": "reference", "reference_table": "task", "reference_display_field": "number", "sort_order": 100},
    {"column_name": "related_task_id", "label": "Related Task", "field_type": "uuid", "sort_order": 101},
    {"column_name": "external_ticket_id", "label": "External Ticket ID", "field_type": "string", "max_length": 100, "sort_order": 102},
    {"column_name": "work_notes", "label": "Work Notes", "field_type": "json", "sort_order": 110},
    {"column_name": "comments", "label": "Comments", "field_type": "json", "sort_order": 111},
    {"column_name": "custom_fields", "label": "Custom Fields", "field_type": "json", "is_system": True, "sort_order": 200},
]

COMPANY_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 255, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "legal_name", "label": "Legal Name", "field_type": "string", "max_length": 255, "sort_order": 2},
    {"column_name": "company_code", "label": "Company Code", "field_type": "string", "max_length": 50, "sort_order": 3},
    {"column_name": "company_type", "label": "Type", "field_type": "choice", "default_value": "internal", "sort_order": 4},
    {"column_name": "status", "label": "Status", "field_type": "choice", "default_value": "active", "sort_order": 5},
    {"column_name": "parent_company_id", "label": "Parent Company", "field_type": "reference", "reference_table": "company", "sort_order": 6},
    {"column_name": "industry", "label": "Industry", "field_type": "string", "max_length": 100, "sort_order": 10},
    {"column_name": "employee_count", "label": "Employee Count", "field_type": "integer", "sort_order": 11},
    {"column_name": "primary_email", "label": "Email", "field_type": "email", "max_length": 255, "sort_order": 20},
    {"column_name": "primary_phone", "label": "Phone", "field_type": "phone", "max_length": 50, "sort_order": 21},
    {"column_name": "website", "label": "Website", "field_type": "url", "max_length": 255, "sort_order": 22},
    {"column_name": "address_line1", "label": "Address", "field_type": "string", "max_length": 255, "sort_order": 30},
    {"column_name": "city", "label": "City", "field_type": "string", "max_length": 100, "sort_order": 31},
    {"column_name": "country", "label": "Country", "field_type": "string", "max_length": 100, "sort_order": 32},
    {"column_name": "support_tier", "label": "Support Tier", "field_type": "string", "max_length": 50, "sort_order": 40},
    {"column_name": "contract_start_date", "label": "Contract Start", "field_type": "date", "sort_order": 50},
    {"column_name": "contract_end_date", "label": "Contract End", "field_type": "date", "sort_order": 51},
    {"column_name": "is_main_it_company", "label": "Main IT Company", "field_type": "boolean", "default_value": "false", "sort_order": 60},
]

USER_FIELDS = [
    {"column_name": "user_id", "label": "User ID", "field_type": "string", "max_length": 100, "is_mandatory": True, "sort_order": 1},
    {"column_name": "email", "label": "Email", "field_type": "email", "max_length": 255, "is_mandatory": True, "sort_order": 2},
    {"column_name": "first_name", "label": "First Name", "field_type": "string", "max_length": 100, "is_mandatory": True, "sort_order": 3},
    {"column_name": "last_name", "label": "Last Name", "field_type": "string", "max_length": 100, "is_mandatory": True, "sort_order": 4},
    {"column_name": "full_name", "label": "Full Name", "field_type": "string", "max_length": 255, "is_display": True, "is_read_only": True, "sort_order": 5},
    {"column_name": "job_title", "label": "Job Title", "field_type": "string", "max_length": 100, "sort_order": 10},
    {"column_name": "phone", "label": "Phone", "field_type": "phone", "max_length": 50, "sort_order": 11},
    {"column_name": "mobile", "label": "Mobile", "field_type": "phone", "max_length": 50, "sort_order": 12},
    {"column_name": "primary_company_id", "label": "Company", "field_type": "reference", "reference_table": "company", "is_mandatory": True, "sort_order": 20},
    {"column_name": "department_id", "label": "Department", "field_type": "reference", "reference_table": "department", "sort_order": 21},
    {"column_name": "location_id", "label": "Location", "field_type": "reference", "reference_table": "location", "sort_order": 22},
    {"column_name": "user_type", "label": "User Type", "field_type": "choice", "default_value": "employee", "sort_order": 30},
    {"column_name": "is_vip", "label": "VIP", "field_type": "boolean", "default_value": "false", "sort_order": 31},
    {"column_name": "is_support_agent", "label": "Support Agent", "field_type": "boolean", "default_value": "false", "sort_order": 32},
    {"column_name": "is_admin", "label": "Admin", "field_type": "boolean", "default_value": "false", "sort_order": 33},
    {"column_name": "language", "label": "Language", "field_type": "string", "max_length": 10, "default_value": "en", "sort_order": 40},
    {"column_name": "timezone", "label": "Timezone", "field_type": "string", "max_length": 50, "default_value": "UTC", "sort_order": 41},
]

DEPARTMENT_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 255, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "description", "label": "Description", "field_type": "text", "sort_order": 2},
    {"column_name": "company_id", "label": "Company", "field_type": "reference", "reference_table": "company", "is_mandatory": True, "sort_order": 10},
    {"column_name": "manager_id", "label": "Manager", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "sort_order": 11},
    {"column_name": "parent_department_id", "label": "Parent Department", "field_type": "reference", "reference_table": "department", "sort_order": 12},
]

LOCATION_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 255, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "company_id", "label": "Company", "field_type": "reference", "reference_table": "company", "is_mandatory": True, "sort_order": 2},
    {"column_name": "address", "label": "Address", "field_type": "string", "max_length": 255, "sort_order": 10},
    {"column_name": "city", "label": "City", "field_type": "string", "max_length": 100, "sort_order": 11},
    {"column_name": "state", "label": "State", "field_type": "string", "max_length": 100, "sort_order": 12},
    {"column_name": "country", "label": "Country", "field_type": "string", "max_length": 100, "sort_order": 13},
    {"column_name": "postal_code", "label": "Postal Code", "field_type": "string", "max_length": 20, "sort_order": 14},
]

SUPPORT_GROUP_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 100, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "description", "label": "Description", "field_type": "text", "sort_order": 2},
    {"column_name": "email", "label": "Email", "field_type": "email", "max_length": 255, "sort_order": 10},
    {"column_name": "group_type", "label": "Group Type", "field_type": "choice", "default_value": "support", "sort_order": 11},
    {"column_name": "assignment_method", "label": "Assignment Method", "field_type": "choice", "default_value": "manual", "sort_order": 12},
    {"column_name": "manager_id", "label": "Manager", "field_type": "reference", "reference_table": "user", "reference_display_field": "full_name", "sort_order": 20},
]

PERMISSION_GROUP_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 255, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "description", "label": "Description", "field_type": "text", "sort_order": 2},
]

ROLE_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 100, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "code", "label": "Code", "field_type": "string", "max_length": 100, "is_mandatory": True, "sort_order": 2},
    {"column_name": "description", "label": "Description", "field_type": "text", "sort_order": 3},
    {"column_name": "module", "label": "Module", "field_type": "choice", "is_mandatory": True, "sort_order": 10},
    {"column_name": "level", "label": "Level", "field_type": "choice", "is_mandatory": True, "sort_order": 11},
    {"column_name": "permissions", "label": "Permissions", "field_type": "json", "sort_order": 20},
    {"column_name": "is_system_role", "label": "System Role", "field_type": "boolean", "default_value": "false", "sort_order": 30},
]

SERVER_SCRIPT_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 255, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "description", "label": "Description", "field_type": "text", "sort_order": 2},
    {"column_name": "is_active", "label": "Active", "field_type": "boolean", "default_value": "true", "sort_order": 3},
    {"column_name": "table_name", "label": "Table", "field_type": "reference", "max_length": 50, "is_mandatory": True, "default_value": "tasks", "reference_table": "sys_db_object", "reference_display_field": "name", "sort_order": 10},
    {"column_name": "sys_class_name", "label": "Class Name", "field_type": "choice", "max_length": 50, "sort_order": 11, "hint": "Leave empty for all types"},
    {"column_name": "timing", "label": "Timing", "field_type": "choice", "is_mandatory": True, "sort_order": 12},
    {"column_name": "execution_order", "label": "Execution Order", "field_type": "integer", "default_value": "100", "sort_order": 13},
    {"column_name": "condition_logic", "label": "Condition Logic", "field_type": "choice", "default_value": "and", "sort_order": 20},
    {"column_name": "conditions", "label": "Conditions", "field_type": "json", "sort_order": 21},
    {"column_name": "actions", "label": "Actions", "field_type": "json", "sort_order": 22},
]

CLIENT_SCRIPT_FIELDS = [
    {"column_name": "name", "label": "Name", "field_type": "string", "max_length": 255, "is_mandatory": True, "is_display": True, "sort_order": 1},
    {"column_name": "description", "label": "Description", "field_type": "text", "sort_order": 2},
    {"column_name": "is_active", "label": "Active", "field_type": "boolean", "default_value": "true", "sort_order": 3},
    {"column_name": "table_name", "label": "Table", "field_type": "reference", "max_length": 50, "is_mandatory": True, "default_value": "tasks", "reference_table": "sys_db_object", "reference_display_field": "name", "sort_order": 10},
    {"column_name": "sys_class_name", "label": "Class Name", "field_type": "choice", "max_length": 50, "sort_order": 11, "hint": "Leave empty for all types"},
    {"column_name": "event", "label": "Event", "field_type": "choice", "is_mandatory": True, "sort_order": 12},
    {"column_name": "trigger_field", "label": "Trigger Field", "field_type": "string", "max_length": 100, "sort_order": 13},
    {"column_name": "execution_order", "label": "Execution Order", "field_type": "integer", "default_value": "100", "sort_order": 14},
    {"column_name": "condition_logic", "label": "Condition Logic", "field_type": "choice", "default_value": "and", "sort_order": 20},
    {"column_name": "conditions", "label": "Conditions", "field_type": "json", "sort_order": 21},
    {"column_name": "ui_actions", "label": "UI Actions", "field_type": "json", "sort_order": 22},
]

# Master list
ALL_DICTIONARY_FIELDS = [
    ("task", TASK_FIELDS),
    ("company", COMPANY_FIELDS),
    ("user", USER_FIELDS),
    ("department", DEPARTMENT_FIELDS),
    ("location", LOCATION_FIELDS),
    ("support_group", SUPPORT_GROUP_FIELDS),
    ("permission_group", PERMISSION_GROUP_FIELDS),
    ("role", ROLE_FIELDS),
    ("server_script", SERVER_SCRIPT_FIELDS),
    ("client_script", CLIENT_SCRIPT_FIELDS),
]

# ===========================================================================
# 3. CHOICES (sys_choice)
# ===========================================================================

# --- Task status choices (per ticket type) ---
STATUS_CHOICES = {
    "incident": [
        ("new", "New", "blue", 10),
        ("assigned", "Assigned", "cyan", 20),
        ("in_progress", "In Progress", "orange", 30),
        ("pending", "Pending", "gold", 40),
        ("resolved", "Resolved", "green", 50),
        ("closed", "Closed", None, 60),
        ("cancelled", "Cancelled", "red", 70),
    ],
    "request": [
        ("submitted", "Submitted", "blue", 10),
        ("pending_approval", "Pending Approval", "gold", 20),
        ("approved", "Approved", "cyan", 30),
        ("rejected", "Rejected", "red", 35),
        ("in_progress", "In Progress", "orange", 40),
        ("fulfilled", "Fulfilled", "green", 50),
        ("closed", "Closed", None, 60),
        ("cancelled", "Cancelled", "red", 70),
    ],
    "change": [
        ("draft", "Draft", "default", 10),
        ("assessment", "Assessment", "blue", 20),
        ("approval", "Approval", "gold", 30),
        ("scheduled", "Scheduled", "cyan", 40),
        ("implementation", "Implementation", "orange", 50),
        ("review", "Review", "purple", 60),
        ("closed", "Closed", None, 70),
        ("cancelled", "Cancelled", "red", 80),
    ],
    "problem": [
        ("new", "New", "blue", 10),
        ("investigation", "Investigation", "orange", 20),
        ("root_cause_analysis", "Root Cause Analysis", "purple", 30),
        ("resolved", "Resolved", "green", 40),
        ("closed", "Closed", None, 50),
    ],
    "task": [
        ("pending", "Pending", "gold", 10),
        ("open", "Open", "blue", 20),
        ("work_in_progress", "Work In Progress", "orange", 30),
        ("complete", "Complete", "green", 40),
        ("closed", "Closed", None, 50),
    ],
    "approval": [
        ("pending", "Pending", "gold", 10),
        ("approved", "Approved", "green", 20),
        ("rejected", "Rejected", "red", 30),
        ("cancelled", "Cancelled", None, 40),
    ],
}

# --- Shared task choices (sys_class_name=None) ---
SHARED_TASK_CHOICES = [
    ("priority", [("critical", "Critical", "red", 10), ("high", "High", "orange", 20), ("medium", "Medium", "gold", 30), ("low", "Low", "blue", 40)]),
    ("urgency", [("critical", "Critical", "red", 10), ("high", "High", "orange", 20), ("medium", "Medium", "gold", 30), ("low", "Low", "blue", 40)]),
    ("impact", [("critical", "Critical", "red", 10), ("high", "High", "orange", 20), ("medium", "Medium", "gold", 30), ("low", "Low", "blue", 40)]),
    ("channel", [("web", "Web", None, 10), ("phone", "Phone", None, 20), ("email", "Email", None, 30), ("walk_in", "Walk-In", None, 40), ("portal", "Portal", None, 50), ("chat", "Chat", None, 60)]),
    ("contact_type", [("email", "Email", None, 10), ("phone", "Phone", None, 20), ("walk_in", "Walk-In", None, 30), ("portal", "Portal", None, 40)]),
    ("resolution_reason", [("fixed", "Fixed", "green", 10), ("workaround", "Workaround", "orange", 20), ("duplicate", "Duplicate", "gold", 30), ("user_error", "User Error", "cyan", 40), ("cannot_reproduce", "Cannot Reproduce", "purple", 50), ("not_a_bug", "Not a Bug", None, 60)]),
    ("category", [("hardware", "Hardware", None, 10), ("software", "Software", None, 20), ("network", "Network", None, 30), ("service", "Service", None, 40), ("other", "Other", None, 50)]),
    ("subcategory", [("desktop", "Desktop", None, 10), ("laptop", "Laptop", None, 20), ("server", "Server", None, 30), ("printer", "Printer", None, 40)]),
]

# --- Non-task table choices: (table_name, field_name, choices) ---
NON_TASK_CHOICES = [
    ("company", "company_type", [("internal", "Internal", "blue", 10), ("customer", "Customer", "green", 20), ("partner", "Partner", "cyan", 30), ("vendor", "Vendor", "purple", 40)]),
    ("company", "status", [("active", "Active", "green", 10), ("inactive", "Inactive", "default", 20), ("prospect", "Prospect", "blue", 30)]),
    ("user", "user_type", [("employee", "Employee", "blue", 10), ("contractor", "Contractor", "cyan", 20), ("customer", "Customer", "green", 30), ("partner", "Partner", "purple", 40)]),
    ("support_group", "group_type", [("support", "Support", "blue", 10), ("operations", "Operations", "green", 20), ("development", "Development", "purple", 30)]),
    ("support_group", "assignment_method", [("manual", "Manual", None, 10), ("round_robin", "Round Robin", None, 20), ("least_busy", "Least Busy", None, 30)]),
    ("role", "module", [("fulfillment", "Fulfillment", "blue", 10), ("foundation", "Foundation", "green", 20), ("system", "System", "purple", 30), ("custom", "Custom", "orange", 40)]),
    ("role", "level", [("basic", "Basic", "default", 10), ("standard", "Standard", "blue", 20), ("admin", "Admin", "red", 30)]),
    ("server_script", "timing", [("before_create", "Before Create", "orange", 10), ("after_create", "After Create", "green", 20), ("before_update", "Before Update", "orange", 30), ("after_update", "After Update", "green", 40), ("before_submit", "Before Submit", "purple", 50), ("after_submit", "After Submit", "cyan", 60)]),
    ("server_script", "condition_logic", [("and", "AND", None, 10), ("or", "OR", None, 20)]),
    ("server_script", "sys_class_name", [("incident", "Incident", "blue", 10), ("request", "Request", "green", 20), ("change", "Change", "purple", 30), ("problem", "Problem", "orange", 40), ("task", "Task", "cyan", 50), ("approval", "Approval", "gold", 60)]),
    ("client_script", "event", [("on_load", "On Load", "blue", 10), ("on_change", "On Change", "orange", 20), ("on_submit", "On Submit", "green", 30)]),
    ("client_script", "condition_logic", [("and", "AND", None, 10), ("or", "OR", None, 20)]),
    ("client_script", "sys_class_name", [("incident", "Incident", "blue", 10), ("request", "Request", "green", 20), ("change", "Change", "purple", 30), ("problem", "Problem", "orange", 40), ("task", "Task", "cyan", 50), ("approval", "Approval", "gold", 60)]),
]

# ===========================================================================
# 4. RELATIONSHIPS (sys_relationship)
# ===========================================================================
RELATIONSHIPS = [
    {"name": "Company → Users", "parent_table": "company", "child_table": "user", "relationship_type": "one_to_many", "foreign_key_field": "primary_company_id"},
    {"name": "Company → Departments", "parent_table": "company", "child_table": "department", "relationship_type": "one_to_many", "foreign_key_field": "company_id"},
    {"name": "Company → Locations", "parent_table": "company", "child_table": "location", "relationship_type": "one_to_many", "foreign_key_field": "company_id"},
    {"name": "Task → Attachments", "parent_table": "task", "child_table": "attachment", "relationship_type": "one_to_many", "foreign_key_field": "task_id"},
    {"name": "Task → Child Tasks", "parent_table": "task", "child_table": "task", "relationship_type": "one_to_many", "foreign_key_field": "parent_task_id"},
    {"name": "Support Group → Members", "parent_table": "support_group", "child_table": "user", "relationship_type": "many_to_many", "join_table": "group_members", "join_parent_field": "group_id", "join_child_field": "user_id"},
    {"name": "Permission Group → Members", "parent_table": "permission_group", "child_table": "user", "relationship_type": "many_to_many", "join_table": "permission_group_members", "join_parent_field": "permission_group_id", "join_child_field": "user_id"},
    {"name": "Permission Group → Roles", "parent_table": "permission_group", "child_table": "role", "relationship_type": "many_to_many", "join_table": "permission_group_roles", "join_parent_field": "permission_group_id", "join_child_field": "role_id"},
]

# ===========================================================================
# 5. FORM LAYOUTS — task view (kept separate for historical reasons)
# ===========================================================================
TASK_VIEW_SECTIONS = [
    {
        "title": "Requester Information", "position": "left", "sequence": 100, "is_expanded": True,
        "section_type": "fields", "columns": 2,
        "elements": [("caller_id", 10, 1, 1), ("affected_user_id", 20, 1, 1), ("company_id", 30, 1, 1)],
    },
    {
        "title": "Assignment", "position": "left", "sequence": 200, "is_expanded": True,
        "section_type": "fields", "columns": 2,
        "elements": [("assignment_group_id", 10, 1, 1), ("assigned_to_id", 20, 1, 1)],
    },
    {
        "title": "Details", "position": "right", "sequence": 100, "is_expanded": True,
        "section_type": "fields", "columns": 2,
        "elements": [
            ("short_description", 10, 1, 2), ("description", 20, 1, 2),
            ("urgency", 30, 1, 1), ("impact", 40, 2, 1), ("priority", 50, 1, 1),
            ("category", 60, 1, 1), ("subcategory", 70, 2, 1),
            ("channel", 80, 1, 1), ("contact_type", 90, 2, 1), ("status_reason", 100, 1, 1),
        ],
    },
    {
        "title": "Resolution", "position": "right", "sequence": 200, "is_expanded": False,
        "section_type": "fields", "columns": 2,
        "elements": [
            ("resolution", 10, 1, 2), ("resolution_reason", 20, 1, 1),
            ("close_notes", 30, 1, 2), ("root_cause", 40, 1, 2), ("workaround", 50, 1, 2),
        ],
    },
]

TASK_LIST_COLUMNS = [
    ("number", 10, 140, "desc", 1), ("short_description", 20, 300, None, None),
    ("caller_id", 30, 150, None, None), ("assignment_group_id", 40, 180, None, None),
    ("assigned_to_id", 50, 150, None, None), ("priority", 60, 100, None, None),
    ("status", 70, 120, None, None), ("sys_created_on", 80, 160, None, None),
]

# ===========================================================================
# 6. FORM + LIST LAYOUTS for non-task tables
# ===========================================================================
TABLE_LAYOUTS = {
    "company": {
        "sections": [
            {"title": "Basic Information", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 1), ("legal_name", 20, 2, 1), ("company_code", 30, 1, 1), ("company_type", 40, 2, 1), ("status", 50, 1, 1), ("parent_company_id", 60, 2, 1), ("industry", 70, 1, 1), ("employee_count", 80, 2, 1)]},
            {"title": "Contact & Address", "sequence": 200, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("primary_email", 10, 1, 1), ("primary_phone", 20, 2, 1), ("website", 30, 1, 2), ("address_line1", 40, 1, 2), ("city", 50, 1, 1), ("country", 60, 2, 1)]},
            {"title": "Contract", "sequence": 300, "is_expanded": False, "section_type": "fields", "columns": 2,
             "elements": [("support_tier", 10, 1, 1), ("is_main_it_company", 20, 2, 1), ("contract_start_date", 30, 1, 1), ("contract_end_date", 40, 2, 1)]},
        ],
        "list_columns": [("name", 10, 200, None, None), ("company_code", 20, 120, None, None), ("company_type", 30, 120, None, None), ("status", 40, 100, None, None), ("city", 50, 120, None, None), ("country", 60, 120, None, None)],
    },
    "user": {
        "sections": [
            {"title": "Personal Information", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("first_name", 10, 1, 1), ("last_name", 20, 2, 1), ("email", 30, 1, 1), ("user_id", 40, 2, 1), ("job_title", 50, 1, 1), ("phone", 60, 2, 1), ("mobile", 70, 1, 1)]},
            {"title": "Organization", "sequence": 200, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("primary_company_id", 10, 1, 1), ("department_id", 20, 2, 1), ("location_id", 30, 1, 1), ("user_type", 40, 2, 1)]},
            {"title": "Access & Settings", "sequence": 300, "is_expanded": False, "section_type": "fields", "columns": 2,
             "elements": [("is_vip", 10, 1, 1), ("is_support_agent", 20, 2, 1), ("is_admin", 30, 1, 1), ("language", 40, 2, 1), ("timezone", 50, 1, 1)]},
        ],
        "list_columns": [("user_id", 10, 120, None, None), ("email", 20, 200, None, None), ("first_name", 30, 120, None, None), ("last_name", 40, 120, None, None), ("primary_company_id", 50, 160, None, None), ("is_support_agent", 60, 100, None, None)],
    },
    "department": {
        "sections": [
            {"title": "Department Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 1), ("company_id", 20, 2, 1), ("manager_id", 30, 1, 1), ("parent_department_id", 40, 2, 1), ("description", 50, 1, 2)]},
        ],
        "list_columns": [("name", 10, 200, None, None), ("company_id", 20, 180, None, None), ("manager_id", 30, 180, None, None)],
    },
    "location": {
        "sections": [
            {"title": "Location Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 1), ("company_id", 20, 2, 1), ("address", 30, 1, 2), ("city", 40, 1, 1), ("state", 50, 2, 1), ("country", 60, 1, 1), ("postal_code", 70, 2, 1)]},
        ],
        "list_columns": [("name", 10, 200, None, None), ("company_id", 20, 180, None, None), ("city", 30, 120, None, None), ("country", 40, 120, None, None)],
    },
    "support_group": {
        "sections": [
            {"title": "Group Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 1), ("email", 20, 2, 1), ("group_type", 30, 1, 1), ("assignment_method", 40, 2, 1), ("manager_id", 50, 1, 1), ("description", 60, 1, 2)]},
        ],
        "list_columns": [("name", 10, 200, None, None), ("email", 20, 200, None, None), ("group_type", 30, 120, None, None), ("manager_id", 40, 180, None, None)],
    },
    "permission_group": {
        "sections": [
            {"title": "Group Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 1,
             "elements": [("name", 10, 1, 1), ("description", 20, 1, 1)]},
        ],
        "list_columns": [("name", 10, 300, None, None), ("description", 20, 400, None, None)],
    },
    "role": {
        "sections": [
            {"title": "Role Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 1), ("code", 20, 2, 1), ("module", 30, 1, 1), ("level", 40, 2, 1), ("is_system_role", 50, 1, 1), ("description", 60, 1, 2)]},
        ],
        "list_columns": [("name", 10, 180, None, None), ("code", 20, 150, None, None), ("module", 30, 120, None, None), ("level", 40, 120, None, None), ("is_system_role", 50, 100, None, None)],
    },
    "server_script": {
        "sections": [
            {"title": "Script Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 2), ("is_active", 15, 1, 1), ("table_name", 20, 1, 1), ("sys_class_name", 30, 2, 1), ("timing", 40, 1, 1), ("execution_order", 50, 2, 1), ("description", 60, 1, 2)]},
            {"title": "Logic", "sequence": 200, "is_expanded": True, "section_type": "fields", "columns": 1,
             "elements": [("condition_logic", 10, 1, 1), ("conditions", 20, 1, 1), ("actions", 30, 1, 1)]},
        ],
        "list_columns": [("name", 10, 200, None, None), ("table_name", 20, 120, None, None), ("timing", 30, 100, None, None), ("is_active", 35, 80, None, None), ("execution_order", 40, 100, None, None)],
    },
    "client_script": {
        "sections": [
            {"title": "Script Details", "sequence": 100, "is_expanded": True, "section_type": "fields", "columns": 2,
             "elements": [("name", 10, 1, 2), ("is_active", 15, 1, 1), ("table_name", 20, 1, 1), ("sys_class_name", 30, 2, 1), ("event", 40, 1, 1), ("trigger_field", 50, 2, 1), ("execution_order", 60, 1, 1), ("description", 70, 1, 2)]},
            {"title": "Logic", "sequence": 200, "is_expanded": True, "section_type": "fields", "columns": 1,
             "elements": [("condition_logic", 10, 1, 1), ("conditions", 20, 1, 1), ("ui_actions", 30, 1, 1)]},
        ],
        "list_columns": [("name", 10, 200, None, None), ("table_name", 20, 120, None, None), ("event", 30, 100, None, None), ("is_active", 35, 80, None, None), ("execution_order", 40, 100, None, None)],
    },
}


# ===========================================================================
# Helpers
# ===========================================================================

def _make_dict_entry(table_name: str, field: dict) -> SysDictionary:
    return SysDictionary(
        tenant_id=None,
        table_name=table_name,
        column_name=field["column_name"],
        label=field["label"],
        field_type=field["field_type"],
        max_length=field.get("max_length"),
        is_mandatory=field.get("is_mandatory", False),
        is_read_only=field.get("is_read_only", False),
        is_display=field.get("is_display", False),
        default_value=field.get("default_value"),
        reference_table=field.get("reference_table"),
        reference_display_field=field.get("reference_display_field"),
        hint=field.get("hint"),
        sort_order=field.get("sort_order", 100),
        sys_class_name=None,
        is_system=field.get("is_system", False),
    )


def _make_choice(table_name: str, field_name: str, value: str, label: str,
                 color: str | None, sequence: int,
                 sys_class_name: str | None = None) -> SysChoice:
    return SysChoice(
        tenant_id=None,
        table_name=table_name,
        field_name=field_name,
        value=value,
        label=label,
        sequence=sequence,
        sys_class_name=sys_class_name,
        color=color,
    )


# ===========================================================================
# MAIN SEED FUNCTION
# ===========================================================================
async def seed_metadata():
    force = "--force" in sys.argv

    async with AsyncSessionLocal() as db:
        try:
            if force:
                print("Force mode: clearing all metadata...")
                await db.execute(delete(SysUiList))
                await db.execute(delete(SysUiElement))
                await db.execute(delete(SysUiSection))
                await db.execute(delete(SysUiView))
                await db.execute(delete(SysRelationship))
                await db.execute(delete(SysChoice))
                await db.execute(delete(SysDictionary))
                await db.execute(delete(SysDbObject))
                await db.commit()
                print("  Cleared.")

            # Idempotency check
            result = await db.execute(select(SysDbObject))
            if result.scalar_one_or_none():
                print("Metadata already seeded! Use --force to re-seed.")
                return

            print("Seeding metadata...")

            # ----------------------------------------------------------
            # 1. Tables (sys_db_object)
            # ----------------------------------------------------------
            print("  [1/6] sys_db_object ...")
            for t in TABLES:
                db.add(SysDbObject(
                    tenant_id=None, name=t["name"], label=t["label"],
                    plural_label=t["plural_label"], super_class=t["super_class"],
                    display_field=t["display_field"], number_prefix=t["number_prefix"],
                    module=t["module"],
                ))
            await db.flush()
            print(f"        {len(TABLES)} tables registered.")

            # ----------------------------------------------------------
            # 2. Dictionary fields (sys_dictionary)
            # ----------------------------------------------------------
            print("  [2/6] sys_dictionary ...")
            field_count = 0
            for table_name, fields in ALL_DICTIONARY_FIELDS:
                for field in fields:
                    db.add(_make_dict_entry(table_name, field))
                    field_count += 1
            await db.flush()
            print(f"        {field_count} fields registered.")

            # ----------------------------------------------------------
            # 3. Choices (sys_choice)
            # ----------------------------------------------------------
            print("  [3/6] sys_choice ...")
            choice_count = 0

            # Task status choices per ticket type
            for sys_class_name, statuses in STATUS_CHOICES.items():
                for value, label, color, seq in statuses:
                    db.add(_make_choice("task", "status", value, label, color, seq,
                                        sys_class_name=sys_class_name))
                    choice_count += 1

            # Shared task choices (sys_class_name=None)
            for field_name, choices in SHARED_TASK_CHOICES:
                for value, label, color, seq in choices:
                    db.add(_make_choice("task", field_name, value, label, color, seq))
                    choice_count += 1

            # Non-task table choices
            for table_name, field_name, choices in NON_TASK_CHOICES:
                for value, label, color, seq in choices:
                    db.add(_make_choice(table_name, field_name, value, label, color, seq))
                    choice_count += 1

            await db.flush()
            print(f"        {choice_count} choices registered.")

            # ----------------------------------------------------------
            # 4. Relationships (sys_relationship)
            # ----------------------------------------------------------
            print("  [4/6] sys_relationship ...")
            for rel in RELATIONSHIPS:
                db.add(SysRelationship(
                    tenant_id=None, name=rel["name"],
                    parent_table=rel["parent_table"], child_table=rel["child_table"],
                    relationship_type=rel["relationship_type"],
                    foreign_key_field=rel.get("foreign_key_field"),
                    join_table=rel.get("join_table"),
                    join_parent_field=rel.get("join_parent_field"),
                    join_child_field=rel.get("join_child_field"),
                ))
            await db.flush()
            print(f"        {len(RELATIONSHIPS)} relationships registered.")

            # ----------------------------------------------------------
            # 5. Task view + sections + elements + list columns
            # ----------------------------------------------------------
            print("  [5/6] Task view ...")
            task_view = SysUiView(
                tenant_id=None, name="default", title="Default",
                table_name="task", sys_class_name=None, is_default=True,
            )
            db.add(task_view)
            await db.flush()

            element_count = 0
            for sec_def in TASK_VIEW_SECTIONS:
                section = SysUiSection(
                    tenant_id=None, view_id=task_view.id, title=sec_def["title"],
                    section_type=sec_def["section_type"], columns=sec_def.get("columns", 2),
                    sequence=sec_def["sequence"], is_expanded=sec_def["is_expanded"],
                    position=sec_def.get("position"), sys_class_name=None,
                )
                db.add(section)
                await db.flush()
                for field_name, seq, col_idx, span in sec_def["elements"]:
                    db.add(SysUiElement(
                        tenant_id=None, section_id=section.id,
                        field_name=field_name, element_type="field",
                        sequence=seq, column_index=col_idx, span=span,
                    ))
                    element_count += 1

            for field_name, seq, width, sort_dir, sort_pri in TASK_LIST_COLUMNS:
                db.add(SysUiList(
                    tenant_id=None, view_id=task_view.id,
                    field_name=field_name, sequence=seq, width=width,
                    sort_direction=sort_dir, sort_priority=sort_pri,
                ))

            await db.flush()
            print(f"        1 view, {len(TASK_VIEW_SECTIONS)} sections, {element_count} elements, {len(TASK_LIST_COLUMNS)} list columns.")

            # ----------------------------------------------------------
            # 6. Non-task table views + sections + elements + list columns
            # ----------------------------------------------------------
            print("  [6/6] Non-task table views ...")
            view_count = 0
            total_sections = 0
            total_elements = 0
            total_list_cols = 0

            for table_name, layout in TABLE_LAYOUTS.items():
                view = SysUiView(
                    tenant_id=None, name="default", title="Default",
                    table_name=table_name, sys_class_name=None, is_default=True,
                )
                db.add(view)
                await db.flush()
                view_count += 1

                for sec_def in layout["sections"]:
                    section = SysUiSection(
                        tenant_id=None, view_id=view.id, title=sec_def["title"],
                        section_type=sec_def["section_type"], columns=sec_def.get("columns", 2),
                        sequence=sec_def["sequence"], is_expanded=sec_def["is_expanded"],
                        position=None, sys_class_name=None,
                    )
                    db.add(section)
                    await db.flush()
                    total_sections += 1
                    for field_name, seq, col_idx, span in sec_def["elements"]:
                        db.add(SysUiElement(
                            tenant_id=None, section_id=section.id,
                            field_name=field_name, element_type="field",
                            sequence=seq, column_index=col_idx, span=span,
                        ))
                        total_elements += 1

                for field_name, seq, width, sort_dir, sort_pri in layout["list_columns"]:
                    db.add(SysUiList(
                        tenant_id=None, view_id=view.id,
                        field_name=field_name, sequence=seq, width=width,
                        sort_direction=sort_dir, sort_priority=sort_pri,
                    ))
                    total_list_cols += 1

            await db.flush()
            print(f"        {view_count} views, {total_sections} sections, {total_elements} elements, {total_list_cols} list columns.")

            # ----------------------------------------------------------
            # Commit
            # ----------------------------------------------------------
            await db.commit()
            print("\nMetadata seeded successfully!")

        except Exception as e:
            print(f"Error seeding metadata: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    print("Starting metadata seed script...")
    asyncio.run(seed_metadata())
