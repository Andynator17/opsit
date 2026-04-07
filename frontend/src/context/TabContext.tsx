import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { createTabContent } from '../components/tabContentFactory';

const STORAGE_KEY = 'opsit-tabs';

export interface Tab {
  id: string;
  title: string;
  type: 'list' | 'form' | 'dashboard';
  closable: boolean;
  content?: ReactNode;

  // Parent-child relationship for nested tabs
  parentId?: string;           // Parent tab ID (undefined for root tabs)
  subTabs?: Tab[];            // Child tabs (only for parent tabs)
  activeSubTabId?: string;    // Currently active sub-tab ID

  // For form tabs
  ticketId?: string;
  ticketType?: string;
  ticketNumber?: string;
  mode?: 'view' | 'edit' | 'create';
  // For list tabs
  listType?: string;
  // For search tabs
  initialSearch?: string;
}

/** Serializable version of a Tab (no ReactNode content) */
interface SerializableTab {
  id: string;
  title: string;
  type: 'list' | 'form' | 'dashboard';
  closable: boolean;
  parentId?: string;
  subTabs?: SerializableTab[];
  activeSubTabId?: string;
  ticketId?: string;
  ticketType?: string;
  ticketNumber?: string;
  mode?: 'view' | 'edit' | 'create';
  listType?: string;
  initialSearch?: string;
}

interface TabContextType {
  tabs: Tab[];
  activeTabId: string | null;
  addTab: (tab: Tab) => void;
  removeTab: (tabId: string) => void;
  setActiveTab: (tabId: string) => void;
  updateTab: (tabId: string, updates: Partial<Tab>) => void;
  closeAllTabs: () => void;

  // Sub-tab operations
  addSubTab: (parentId: string, subTab: Omit<Tab, 'parentId'>) => void;
  removeSubTab: (parentId: string, subTabId: string) => void;
  setActiveSubTab: (parentId: string, subTabId: string) => void;
  getSubTabs: (parentId: string) => Tab[];
  getActiveSubTab: (parentId: string) => Tab | undefined;
}

const TabContext = createContext<TabContextType | undefined>(undefined);

// ---- Serialization / Deserialization helpers ----

function serializeTab(tab: Tab): SerializableTab {
  return {
    id: tab.id,
    title: tab.title,
    type: tab.type,
    closable: tab.closable,
    parentId: tab.parentId,
    activeSubTabId: tab.activeSubTabId,
    ticketId: tab.ticketId,
    ticketType: tab.ticketType,
    ticketNumber: tab.ticketNumber,
    mode: tab.mode,
    listType: tab.listType,
    initialSearch: tab.initialSearch,
    // Recursively serialize sub-tabs, skip create-mode tabs (unsaved data)
    subTabs: tab.subTabs
      ?.filter(st => st.mode !== 'create')
      .map(serializeTab),
  };
}

function deserializeTab(st: SerializableTab, parentListType?: string): Tab {
  const content = createTabContent(st, parentListType);
  const listType = st.listType;

  return {
    ...st,
    content,
    subTabs: st.subTabs?.map(sub => deserializeTab(sub, listType)),
  };
}

function saveTabs(tabs: Tab[], activeTabId: string | null) {
  try {
    const serializable = tabs
      .filter(t => t.mode !== 'create')
      .map(serializeTab);
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ tabs: serializable, activeTabId })
    );
  } catch {
    // Silently ignore storage errors (quota, private browsing, etc.)
  }
}

function loadTabs(): { tabs: Tab[]; activeTabId: string | null } | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as {
      tabs: SerializableTab[];
      activeTabId: string | null;
    };
    if (!parsed.tabs || parsed.tabs.length === 0) return null;
    const tabs = parsed.tabs.map(st => deserializeTab(st));
    // Validate activeTabId exists in restored tabs (create-mode tabs are filtered out during save)
    const activeTabId = tabs.some(t => t.id === parsed.activeTabId)
      ? parsed.activeTabId
      : tabs[0]?.id ?? null;
    return { tabs, activeTabId };
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

// ---- Provider ----

export const TabProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Hydrate from localStorage synchronously on first render
  const initialState = useRef(loadTabs());

  const [tabs, setTabs] = useState<Tab[]>(initialState.current?.tabs ?? []);
  const [activeTabId, setActiveTabId] = useState<string | null>(
    initialState.current?.activeTabId ?? null
  );

  // Persist whenever tabs or activeTabId change (skip the initial render)
  const isFirstRender = useRef(true);
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    saveTabs(tabs, activeTabId);
  }, [tabs, activeTabId]);

  const addTab = (tab: Tab) => {
    // Check if tab already exists
    const existingTab = tabs.find(t => t.id === tab.id);
    if (existingTab) {
      // Activate the existing tab and reset to List view
      setActiveTabId(tab.id);
      if (existingTab.subTabs?.length) {
        setTabs(prev => prev.map(t =>
          t.id === tab.id ? { ...t, activeSubTabId: undefined } : t
        ));
      }
      return;
    }

    // Auto-generate content if not provided
    const tabWithContent = tab.content ? tab : { ...tab, content: createTabContent(tab) };
    setTabs(prev => [...prev, tabWithContent]);
    setActiveTabId(tab.id);
  };

  const removeTab = (tabId: string) => {
    setTabs(prev => {
      // Note: Sub-tabs are stored within parent's subTabs array,
      // so removing parent automatically removes all sub-tabs (cascade delete)
      const newTabs = prev.filter(t => t.id !== tabId);

      // If we're removing the active tab, switch to the previous tab or the first one
      if (activeTabId === tabId && newTabs.length > 0) {
        const removedIndex = prev.findIndex(t => t.id === tabId);
        const newActiveIndex = removedIndex > 0 ? removedIndex - 1 : 0;
        setActiveTabId(newTabs[newActiveIndex]?.id || null);
      } else if (newTabs.length === 0) {
        setActiveTabId(null);
      }

      return newTabs;
    });
  };

  const updateTab = (tabId: string, updates: Partial<Tab>) => {
    setTabs(prev => prev.map(tab =>
      tab.id === tabId ? { ...tab, ...updates } : tab
    ));
  };

  const closeAllTabs = () => {
    setTabs([]);
    setActiveTabId(null);
  };

  // Sub-tab operations
  const addSubTab = (parentId: string, subTab: Omit<Tab, 'parentId'>) => {
    setTabs(prev => {
      return prev.map(tab => {
        if (tab.id === parentId) {
          // Check if sub-tab already exists
          const existingSubTab = tab.subTabs?.find(st => st.id === subTab.id);
          if (existingSubTab) {
            // Just activate it
            return { ...tab, activeSubTabId: subTab.id };
          }

          // Add new sub-tab with parentId, auto-generate content if missing
          const withContent = subTab.content
            ? subTab
            : { ...subTab, content: createTabContent(subTab, tab.listType) };
          const newSubTab = { ...withContent, parentId };
          const updatedSubTabs = [...(tab.subTabs || []), newSubTab];
          return {
            ...tab,
            subTabs: updatedSubTabs,
            activeSubTabId: newSubTab.id,
          };
        }
        return tab;
      });
    });
  };

  const removeSubTab = (parentId: string, subTabId: string) => {
    setTabs(prev => {
      return prev.map(tab => {
        if (tab.id === parentId && tab.subTabs) {
          const updatedSubTabs = tab.subTabs.filter(st => st.id !== subTabId);

          // Determine new active sub-tab
          let newActiveSubTabId: string | undefined = undefined;
          if (tab.activeSubTabId === subTabId && updatedSubTabs.length > 0) {
            // Find the index of the removed sub-tab
            const removedIndex = tab.subTabs.findIndex(st => st.id === subTabId);
            const newActiveIndex = removedIndex > 0 ? removedIndex - 1 : 0;
            newActiveSubTabId = updatedSubTabs[newActiveIndex]?.id;
          }

          return {
            ...tab,
            subTabs: updatedSubTabs,
            activeSubTabId: newActiveSubTabId,
          };
        }
        return tab;
      });
    });
  };

  const setActiveSubTab = (parentId: string, subTabId: string) => {
    setTabs(prev => {
      return prev.map(tab => {
        if (tab.id === parentId) {
          return { ...tab, activeSubTabId: subTabId };
        }
        return tab;
      });
    });
  };

  const getSubTabs = (parentId: string): Tab[] => {
    const parentTab = tabs.find(t => t.id === parentId);
    return parentTab?.subTabs || [];
  };

  const getActiveSubTab = (parentId: string): Tab | undefined => {
    const parentTab = tabs.find(t => t.id === parentId);
    if (!parentTab || !parentTab.activeSubTabId) return undefined;
    return parentTab.subTabs?.find(st => st.id === parentTab.activeSubTabId);
  };

  return (
    <TabContext.Provider
      value={{
        tabs,
        activeTabId,
        addTab,
        removeTab,
        setActiveTab: setActiveTabId,
        updateTab,
        closeAllTabs,
        addSubTab,
        removeSubTab,
        setActiveSubTab,
        getSubTabs,
        getActiveSubTab,
      }}
    >
      {children}
    </TabContext.Provider>
  );
};

export const useTabs = () => {
  const context = useContext(TabContext);
  if (!context) {
    throw new Error('useTabs must be used within TabProvider');
  }
  return context;
};
