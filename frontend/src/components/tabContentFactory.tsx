import React from 'react';
import Dashboard from '../pages/Dashboard';
import DynamicList from './dynamic/DynamicList';
import DynamicForm from './dynamic/DynamicForm';
import { TABLE_REGISTRY, isTicketType } from '../config/tableRegistry';
import type { ReactNode } from 'react';

/**
 * Reconstructs a React component for a tab based on its serializable metadata.
 * Used when restoring tabs from localStorage and as the single source of truth
 * for DashboardLayout menu items.
 */
export function createTabContent(
  tabMeta: {
    id: string;
    type: 'list' | 'form' | 'dashboard';
    listType?: string;
    ticketType?: string;
    mode?: 'view' | 'edit' | 'create';
    parentId?: string;
    initialSearch?: string;
  },
  parentListType?: string
): ReactNode {
  if (tabMeta.type === 'dashboard') {
    return <Dashboard />;
  }

  if (tabMeta.type === 'list') {
    const registryKey = tabMeta.listType || 'incident';
    const entry = TABLE_REGISTRY[registryKey];
    if (!entry) return <div>Unknown list type: {registryKey}</div>;

    const isSearch = registryKey === 'search';
    return (
      <DynamicList
        registryKey={registryKey}
        parentTabId={tabMeta.id}
        initialSearch={tabMeta.initialSearch}
        title={isSearch ? `Search Results: "${tabMeta.initialSearch || ''}"` : undefined}
        createButtonText={isSearch ? '' : undefined}
        showMyGroupsFilter={isTicketType(registryKey)}
      />
    );
  }

  if (tabMeta.type === 'form') {
    const registryKey = tabMeta.ticketType || parentListType || tabMeta.listType || 'incident';
    const mode = tabMeta.mode || 'view';

    return (
      <DynamicForm
        registryKey={registryKey}
        recordId={mode !== 'create' ? tabMeta.id : undefined}
        mode={mode}
        parentTabId={tabMeta.parentId}
        currentTabId={tabMeta.id}
      />
    );
  }

  return <div>Unknown tab type</div>;
}
