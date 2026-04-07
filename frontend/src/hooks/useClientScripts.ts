/**
 * useClientScripts — evaluates declarative client scripts against form values
 * and returns per-field UI states (hidden, readonly, mandatory, set_value).
 */
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { clientScriptService } from '../services/clientScript.service';
import type { ClientScript, ClientScriptCondition } from '../types';

export interface FieldState {
  hidden?: boolean;
  readonly?: boolean;
  mandatory?: boolean;
  value?: any;
  hasValue?: boolean; // true when a set_value action was triggered
}

interface UseClientScriptsOptions {
  tableName: string;
  sysClassName: string;
  formValues: Record<string, any>;
  mode: 'view' | 'edit' | 'create';
  enabled?: boolean;
}

// ── Condition evaluation (pure, no eval/exec) ──────────────────────────────

function evaluateCondition(
  condition: ClientScriptCondition,
  formValues: Record<string, any>,
): boolean {
  const { field, operator, value: expected } = condition;
  if (!field || !operator) return false;

  const current = formValues[field];

  switch (operator) {
    case 'is_empty':
      return current === null || current === undefined || current === '';
    case 'is_not_empty':
      return current !== null && current !== undefined && current !== '';
    case 'equals':
      return String(current ?? '') === String(expected ?? '');
    case 'not_equals':
      return String(current ?? '') !== String(expected ?? '');
    case 'in':
      if (!Array.isArray(expected)) return false;
      return expected.map(String).includes(String(current ?? ''));
    case 'not_in':
      if (!Array.isArray(expected)) return true;
      return !expected.map(String).includes(String(current ?? ''));
    case 'contains':
      if (current === null || current === undefined) return false;
      return String(current).includes(String(expected ?? ''));
    default:
      return false;
  }
}

function evaluateConditions(
  conditions: ClientScriptCondition[],
  formValues: Record<string, any>,
  logic: string,
): boolean {
  if (!conditions || conditions.length === 0) return true;
  if (logic === 'or') {
    return conditions.some((c) => evaluateCondition(c, formValues));
  }
  return conditions.every((c) => evaluateCondition(c, formValues));
}

// ── Hook ────────────────────────────────────────────────────────────────────

export function useClientScripts({
  tableName,
  sysClassName,
  formValues,
  mode,
  enabled = true,
}: UseClientScriptsOptions) {
  // Fetch applicable scripts (cached 5 min)
  const { data: scripts, isLoading } = useQuery({
    queryKey: ['client-scripts-applicable', tableName, sysClassName],
    queryFn: () => clientScriptService.getApplicable(tableName, sysClassName),
    enabled: enabled && mode !== 'create' ? true : enabled, // always fetch
    staleTime: 5 * 60 * 1000,
  });

  // Evaluate all scripts and compute field states
  const fieldStates = useMemo<Record<string, FieldState>>(() => {
    if (!scripts || scripts.length === 0) return {};

    const states: Record<string, FieldState> = {};

    const applyAction = (field: string, type: string, value: any) => {
      if (!states[field]) states[field] = {};
      switch (type) {
        case 'set_hidden':
          states[field].hidden = Boolean(value);
          break;
        case 'set_readonly':
          states[field].readonly = Boolean(value);
          break;
        case 'set_mandatory':
          states[field].mandatory = Boolean(value);
          break;
        case 'set_value':
          states[field].value = value;
          states[field].hasValue = true;
          break;
      }
    };

    for (const script of scripts) {
      // on_load: always evaluate
      // on_change: always evaluate (conditions check current values)
      // on_submit: skip (handled separately at submit time)
      if (script.event === 'on_submit') continue;

      const conditions = script.conditions || [];
      const logic = script.condition_logic || 'and';
      const actions = script.ui_actions || [];

      if (evaluateConditions(conditions, formValues, logic)) {
        for (const action of actions) {
          applyAction(action.field, action.type, action.value);
        }
      }
    }

    return states;
  }, [scripts, formValues]);

  return { fieldStates, loading: isLoading };
}

export default useClientScripts;
