"""Database models"""
from app.models.tenant import Tenant
from app.models.company import Company
from app.models.user import User
from app.models.task import Task  # Central ticket table (ServiceNow pattern)
from app.models.incident import Incident  # Deprecated - use Task
from app.models.request import Request
from app.models.category import Category
from app.models.support_group import SupportGroup
from app.models.role import Role
from app.models.permission_group import PermissionGroup
from app.models.attachment import Attachment
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.department import Department
from app.models.location import Location
from app.models.portal import Portal
from app.models.server_script import ServerScript
from app.models.client_script import ClientScript
from app.models.sys_db_object import SysDbObject
from app.models.sys_dictionary import SysDictionary
from app.models.sys_choice import SysChoice
from app.models.sys_ui_view import SysUiView
from app.models.sys_ui_section import SysUiSection
from app.models.sys_ui_element import SysUiElement
from app.models.sys_ui_list import SysUiList
from app.models.sys_relationship import SysRelationship
from app.models.sys_ui_related_list import SysUiRelatedList

__all__ = [
    "Tenant",
    "Company",
    "User",
    "Task",
    "Incident",  # Deprecated
    "Request",
    "Category",
    "SupportGroup",
    "Role",
    "PermissionGroup",
    "Attachment",
    "AuditLog",
    "Notification",
    "Department",
    "Location",
    "Portal",
    "ServerScript",
    "ClientScript",
    "SysDbObject",
    "SysDictionary",
    "SysChoice",
    "SysUiView",
    "SysUiSection",
    "SysUiElement",
    "SysUiList",
    "SysRelationship",
    "SysUiRelatedList",
]
