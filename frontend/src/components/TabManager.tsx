import React from 'react';
import { Tabs } from 'antd';
import { useTabs } from '../context/TabContext';
import type { Tab } from '../context/TabContext';

const TabManager: React.FC = () => {
  const {
    tabs,
    activeTabId,
    setActiveTab,
    removeTab,
    getSubTabs,
    getActiveSubTab,
    setActiveSubTab,
    removeSubTab,
  } = useTabs();

  // Filter to get only root tabs (no parentId)
  const rootTabs = tabs.filter(t => !t.parentId);

  const handleMainTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  const handleMainTabEdit = (
    targetKey: React.MouseEvent | React.KeyboardEvent | string,
    action: 'add' | 'remove'
  ) => {
    if (action === 'remove' && typeof targetKey === 'string') {
      removeTab(targetKey);
    }
  };

  const handleSubTabChange = (parentId: string, subTabId: string) => {
    setActiveSubTab(parentId, subTabId);
  };

  const handleSubTabEdit = (
    parentId: string,
    targetKey: React.MouseEvent | React.KeyboardEvent | string,
    action: 'add' | 'remove'
  ) => {
    if (action === 'remove' && typeof targetKey === 'string') {
      removeSubTab(parentId, targetKey);
    }
  };

  // Render content for a tab (either its content or sub-tabs)
  const renderTabContent = (tab: Tab) => {
    const subTabs = getSubTabs(tab.id);
    const activeSubTab = getActiveSubTab(tab.id);

    // If no sub-tabs, show the main content
    if (subTabs.length === 0) {
      return tab.content || <div>Loading...</div>;
    }

    // Has sub-tabs, render sub-tab bar
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {renderSubTabs(tab.id, subTabs, activeSubTab)}
      </div>
    );
  };

  // Render sub-tabs for a parent tab
  const renderSubTabs = (parentId: string, subTabs: Tab[], activeSubTab: Tab | undefined) => {
    const parentTab = rootTabs.find(t => t.id === parentId);

    // Create a special "List" tab to show the parent's content
    const listTabItem = {
      key: `${parentId}-list`,
      label: 'List',
      closable: false,  // Can't close the list tab
      children: parentTab?.content || <div>Loading...</div>,
    };

    // Add sub-tab items
    const subTabItems = subTabs.map((subTab: Tab) => ({
      key: subTab.id,
      label: subTab.title,
      closable: true,
      children: subTab.content || <div>Loading...</div>,
    }));

    // Combine list tab with sub-tabs
    const allItems = [listTabItem, ...subTabItems];

    // Determine active key (default to list if no active sub-tab)
    const activeKey = activeSubTab?.id || `${parentId}-list`;

    return (
      <Tabs
        type="editable-card"  // Changed from "card" to show close buttons
        size="small"
        activeKey={activeKey}
        onChange={(key) => {
          if (key === `${parentId}-list`) {
            // Clicked on List tab, deactivate any sub-tab
            setActiveSubTab(parentId, '');
          } else {
            handleSubTabChange(parentId, key);
          }
        }}
        onEdit={(key, action) => handleSubTabEdit(parentId, key, action)}
        items={allItems}
        hideAdd  // Hide the + button
        style={{ flex: 1 }}
        tabBarStyle={{
          marginBottom: 8,
          paddingLeft: 16,
          paddingRight: 16,
          backgroundColor: 'rgba(0, 0, 0, 0.02)',
        }}
      />
    );
  };

  // Convert root tabs to Ant Design format
  const mainItems = rootTabs.map((tab: Tab) => {
    const subTabs = getSubTabs(tab.id);
    const hasSubTabs = subTabs.length > 0;

    return {
      key: tab.id,
      label: tab.title + (hasSubTabs ? ' ▼' : ''),  // Add indicator for tabs with sub-tabs
      closable: tab.closable,
      children: renderTabContent(tab),
    };
  });

  if (rootTabs.length === 0) {
    return null;
  }

  return (
    <Tabs
      type="editable-card"
      activeKey={activeTabId || undefined}
      onChange={handleMainTabChange}
      onEdit={handleMainTabEdit}
      hideAdd
      items={mainItems}
      style={{ height: '100%' }}
      tabBarStyle={{ marginBottom: 0 }}
    />
  );
};

export default TabManager;
