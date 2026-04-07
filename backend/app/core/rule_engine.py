"""
Declarative Rule Engine for Server Scripts (Business Rules).

Evaluates JSON-based conditions and executes actions on Task objects.
NO eval/exec — only whitelisted fields and operators.
"""
import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.server_script import ServerScript

logger = logging.getLogger(__name__)

# ── Security whitelists ──────────────────────────────────────────────────────

SETTABLE_FIELDS = {
    "assignment_group_id", "assigned_to_id", "status", "priority",
    "urgency", "impact", "category", "subcategory", "channel",
    "caller_id", "affected_user_id", "company_id", "contact_type",
    "status_reason", "short_description", "description",
    "resolution", "resolution_reason", "close_notes",
    "root_cause", "workaround",
}

VALID_OPERATORS = {
    "is_empty", "is_not_empty", "equals", "not_equals",
    "in", "not_in", "contains",
    "changed", "changed_to", "changed_from",
}


def _get_queryable_models() -> dict:
    """Lazy import to avoid circular imports."""
    from app.models.support_group import SupportGroup
    from app.models.user import User
    from app.models.company import Company
    from app.models.category import Category
    return {
        "SupportGroup": SupportGroup,
        "User": User,
        "Company": Company,
        "Category": Category,
    }


# ── Condition evaluation ─────────────────────────────────────────────────────

def _evaluate_condition(
    condition: dict,
    task: Any,
    old_values: dict,
) -> bool:
    """Evaluate a single condition against a task. Returns True if condition passes."""
    field = condition.get("field")
    operator = condition.get("operator")
    expected = condition.get("value")

    if not field or operator not in VALID_OPERATORS:
        logger.warning("Invalid condition: field=%s operator=%s", field, operator)
        return False

    current_value = getattr(task, field, None)

    if operator == "is_empty":
        return current_value is None or current_value == "" or current_value == []

    if operator == "is_not_empty":
        return current_value is not None and current_value != "" and current_value != []

    if operator == "equals":
        return str(current_value) == str(expected) if current_value is not None else expected is None

    if operator == "not_equals":
        return str(current_value) != str(expected) if current_value is not None else expected is not None

    if operator == "in":
        if not isinstance(expected, list):
            return False
        return str(current_value) in [str(v) for v in expected]

    if operator == "not_in":
        if not isinstance(expected, list):
            return True
        return str(current_value) not in [str(v) for v in expected]

    if operator == "contains":
        if current_value is None:
            return False
        return str(expected) in str(current_value)

    if operator == "changed":
        if field not in old_values:
            return False
        return str(old_values[field]) != str(current_value)

    if operator == "changed_to":
        if field not in old_values:
            return False
        return str(old_values[field]) != str(current_value) and str(current_value) == str(expected)

    if operator == "changed_from":
        if field not in old_values:
            return False
        return str(old_values[field]) == str(expected) and str(old_values[field]) != str(current_value)

    return False


def _evaluate_conditions(conditions: list, task: Any, old_values: dict, logic: str = "and") -> bool:
    """Evaluate conditions with AND or OR logic. Empty conditions = always true."""
    if not conditions:
        return True
    results = (_evaluate_condition(c, task, old_values) for c in conditions)
    if logic == "or":
        return any(results)
    return all(results)


# ── Action execution ─────────────────────────────────────────────────────────

async def _execute_action(
    action: dict,
    task: Any,
    db: AsyncSession,
    tenant_id: UUID,
) -> None:
    """Execute a single action on a task."""
    action_type = action.get("type")

    # ── add_work_note / add_comment — append to JSON array ──
    if action_type in ("add_work_note", "add_comment"):
        text = action.get("value", "")
        if not text:
            logger.warning("Empty text for %s action — skipping", action_type)
            return
        target = "work_notes" if action_type == "add_work_note" else "comments"
        from datetime import datetime, timezone
        entry = {
            "author": "System (Rule Engine)",
            "date": datetime.now(timezone.utc).isoformat(),
            "comment": str(text),
        }
        existing = getattr(task, target, None) or []
        setattr(task, target, existing + [entry])
        logger.info("Rule appended %s entry: %s", target, text[:80])
        return

    # ── set_value / set_value_from_query — require a valid target field ──
    field = action.get("field")
    if not field or field not in SETTABLE_FIELDS:
        logger.warning("Blocked action: field '%s' not in SETTABLE_FIELDS", field)
        return

    if action_type == "set_value":
        value = action.get("value")
        setattr(task, field, value)
        logger.info("Rule set %s = %s", field, value)

    elif action_type == "set_value_from_query":
        query_model_name = action.get("query_model")
        query_filters = action.get("query_filters", {})
        query_field = action.get("query_field", "id")

        queryable = _get_queryable_models()
        model_cls = queryable.get(query_model_name)
        if not model_cls:
            logger.warning("Blocked query: model '%s' not in QUERYABLE_MODELS", query_model_name)
            return

        target_col = getattr(model_cls, query_field, None)
        if target_col is None:
            logger.warning("Field '%s' not found on model '%s'", query_field, query_model_name)
            return

        query = select(target_col)

        if hasattr(model_cls, "tenant_id"):
            query = query.where(model_cls.tenant_id == tenant_id)

        for filter_field, filter_value in query_filters.items():
            col = getattr(model_cls, filter_field, None)
            if col is not None:
                query = query.where(col == filter_value)

        query = query.limit(1)
        result = await db.execute(query)
        row_value = result.scalar_one_or_none()

        if row_value is not None:
            setattr(task, field, row_value)
            logger.info("Rule set %s = %s (from query %s.%s)", field, row_value, query_model_name, query_field)
        else:
            logger.info("Rule query returned no result for %s.%s", query_model_name, query_field)
    else:
        logger.warning("Unknown action type: %s", action_type)


# ── Main entry point ─────────────────────────────────────────────────────────

async def execute_rules(
    timing: str,
    task: Any,
    old_values: dict,
    db: AsyncSession,
    tenant_id: UUID,
) -> None:
    """
    Execute all matching server scripts for the given timing.

    Args:
        timing: "before_create", "after_create", "before_update", "after_update"
        task: The Task object being created/updated
        old_values: Dict of {field: old_value} for update operations (empty for create)
        db: Database session
        tenant_id: Current tenant
    """
    task_class_name = getattr(task, "sys_class_name", None)

    # Fetch matching rules: same timing, same table, matching class or NULL class
    query = (
        select(ServerScript)
        .where(
            ServerScript.tenant_id == tenant_id,
            ServerScript.table_name == "tasks",
            ServerScript.timing == timing,
            ServerScript.is_active == True,
            ServerScript.is_deleted == False,
            or_(
                ServerScript.sys_class_name == task_class_name,
                ServerScript.sys_class_name == None,
            ),
        )
        .order_by(ServerScript.execution_order)
    )

    result = await db.execute(query)
    rules = result.scalars().all()

    if not rules:
        return

    logger.debug("Found %d rules for timing=%s class=%s", len(rules), timing, task_class_name)

    for rule in rules:
        conditions = rule.conditions or []
        actions = rule.actions or []
        logic = getattr(rule, "condition_logic", "and") or "and"

        if _evaluate_conditions(conditions, task, old_values, logic):
            logger.info("Rule '%s' matched — executing %d action(s)", rule.name, len(actions))
            for action in actions:
                await _execute_action(action, task, db, tenant_id)
        else:
            logger.debug("Rule '%s' conditions not met — skipping", rule.name)
