import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Space, Typography, Switch, Tooltip, Input, Badge, message } from 'antd';
import './DashboardLayout.css';
import { useTabs } from '../context/TabContext';
import TabManager from './TabManager';
import { createTabContent } from './tabContentFactory';
import { recordService } from '../services/record.service';
import { TABLE_REGISTRY } from '../config/tableRegistry';
import {
  DashboardOutlined,
  AlertOutlined,
  FileTextOutlined,
  TeamOutlined,
  BankOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ExclamationCircleOutlined,
  SyncOutlined,
  BugOutlined,
  CheckSquareOutlined,
  CustomerServiceOutlined,
  CalendarOutlined,
  DatabaseOutlined,
  ToolOutlined,
  ClockCircleOutlined,
  SolutionOutlined,
  ProjectOutlined,
  EnvironmentOutlined,
  ApartmentOutlined,
  ShoppingOutlined,
  ContainerOutlined,
  FileProtectOutlined,
  CodeOutlined,
  ApiOutlined,
  BellOutlined,
  SafetyOutlined,
  LockOutlined,
  FileSearchOutlined,
  ControlOutlined,
  BarChartOutlined,
  BulbOutlined,
  BulbFilled,
  SearchOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const DashboardLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const { addTab, addSubTab, setActiveTab } = useTabs();
  const initialized = useRef(false);
  const [searchValue, setSearchValue] = useState('');

  // Ticket number patterns
  const TICKET_PATTERN = /^(INC|REQ|CHG|PRB|TSK|APR)\d+$/i;
  const TICKET_TYPE_MAP: Record<string, 'incident' | 'request' | 'change' | 'problem' | 'task' | 'approval'> = {
    INC: 'incident', REQ: 'request', CHG: 'change', PRB: 'problem', TSK: 'task', APR: 'approval',
  };

  // Helper: open a list tab via registry
  const openList = (id: string, listType: string) => {
    const meta = {
      id,
      title: TABLE_REGISTRY[listType]?.pluralLabel ?? listType,
      type: 'list' as const,
      closable: true,
      listType,
    };
    addTab({ ...meta, content: createTabContent(meta) });
  };

  const handleSearch = async (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) return;

    if (TICKET_PATTERN.test(trimmed)) {
      try {
        const result = await recordService.getRecords('task', { search: trimmed, page: 1, page_size: 1 });
        if (result.items.length > 0) {
          const task = result.items[0];
          const ticketType = TICKET_TYPE_MAP[trimmed.substring(0, 3).toUpperCase()] || 'incident';
          const meta = {
            id: String(task.id),
            title: String(task.number || trimmed),
            type: 'form' as const,
            closable: true,
            ticketType,
            listType: ticketType,
            mode: 'view' as const,
          };
          addTab({ ...meta, content: createTabContent(meta) });
          setSearchValue('');
          return;
        }
      } catch {
        // Fall through to search results
      }
    }

    // Open search results as filtered task list (all ticket types)
    const searchTabId = `search-${Date.now()}`;
    const meta = {
      id: searchTabId,
      title: `Search: ${trimmed}`,
      type: 'list' as const,
      closable: true,
      listType: 'search',
      initialSearch: trimmed,
    };
    addTab({ ...meta, content: createTabContent(meta) });
    setSearchValue('');
  };

  // Sidebar width settings
  const SIDEBAR_WIDTH = 260;
  const SIDEBAR_COLLAPSED_WIDTH = 80;

  // Create permanent Dashboard tab on mount
  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      const meta = { id: 'dashboard-main', title: 'Dashboard', type: 'dashboard' as const, closable: false };
      addTab({ ...meta, content: createTabContent(meta) });
    }
  }, [addTab]);

  const menuItems: MenuProps['items'] = [
    // SECTION 1: Fulfillment
    {
      type: 'group',
      label: 'Fulfillment',
      children: [
        { key: '/dashboard', icon: <DashboardOutlined />, label: 'Dashboard', onClick: () => setActiveTab('dashboard-main') },
        { key: '/incident-management', icon: <ExclamationCircleOutlined />, label: 'Incident Management', onClick: () => openList('incidents-list', 'incident') },
        { key: '/request-management', icon: <FileTextOutlined />, label: 'Request Management', onClick: () => openList('requests-list', 'request') },
        { key: '/change-management', icon: <SyncOutlined />, label: 'Change Management', onClick: () => openList('changes-list', 'change') },
        { key: '/problem-management', icon: <BugOutlined />, label: 'Problem Management', onClick: () => openList('problems-list', 'problem') },
        { key: '/task-management', icon: <CheckSquareOutlined />, label: 'Task Management', onClick: () => openList('tasks-list', 'task') },
        { key: '/approval-management', icon: <SafetyOutlined />, label: 'Approval Management', onClick: () => openList('approvals-list', 'approval') },
        { key: '/services', icon: <CustomerServiceOutlined />, label: 'Service Management', onClick: () => navigate('/services') },
        { key: '/events', icon: <CalendarOutlined />, label: 'Event Management', onClick: () => navigate('/events') },
        { key: '/assets', icon: <DatabaseOutlined />, label: 'Asset Management', onClick: () => navigate('/assets') },
        { key: '/configuration', icon: <ToolOutlined />, label: 'Config Management', onClick: () => navigate('/configuration') },
        { key: '/cmdb', icon: <DatabaseOutlined />, label: 'CMDB', onClick: () => navigate('/cmdb') },
        { key: '/sla', icon: <ClockCircleOutlined />, label: 'SLA', onClick: () => navigate('/sla') },
        { key: '/hr', icon: <SolutionOutlined />, label: 'HR Management', onClick: () => navigate('/hr') },
        { key: '/business-cases', icon: <ProjectOutlined />, label: 'Business Case', onClick: () => navigate('/business-cases') },
        { key: '/reporting', icon: <BarChartOutlined />, label: 'Reporting', onClick: () => navigate('/reporting') },
      ],
    },

    // SECTION 2: Foundation
    {
      type: 'group',
      label: 'Foundation',
      children: [
        { key: '/companies', icon: <BankOutlined />, label: 'Companies', onClick: () => openList('companies-list', 'company') },
        { key: '/departments', icon: <ApartmentOutlined />, label: 'Departments', onClick: () => openList('departments-list', 'department') },
        { key: '/locations', icon: <EnvironmentOutlined />, label: 'Locations', onClick: () => openList('locations-list', 'location') },
        { key: '/users', icon: <TeamOutlined />, label: 'User', onClick: () => openList('users-list', 'user') },
        { key: '/support-groups', icon: <TeamOutlined />, label: 'Support Groups', onClick: () => openList('support-groups-list', 'support-group') },
        { key: '/catalog', icon: <ShoppingOutlined />, label: 'Services', onClick: () => navigate('/catalog') },
        { key: '/products', icon: <ShoppingOutlined />, label: 'Sold Products', onClick: () => navigate('/products') },
        { key: '/install-bases', icon: <ContainerOutlined />, label: 'Install Bases', onClick: () => navigate('/install-bases') },
        { key: '/contracts', icon: <FileProtectOutlined />, label: 'Contracts', onClick: () => navigate('/contracts') },
      ],
    },

    // SECTION 3: System
    {
      type: 'group',
      label: 'System',
      children: [
        { key: '/server-scripts', icon: <CodeOutlined />, label: 'Server Scripts', onClick: () => openList('server-scripts-list', 'server-script') },
        { key: '/client-scripts', icon: <CodeOutlined />, label: 'Client Scripts', onClick: () => openList('client-scripts-list', 'client-script') },
        { key: '/workflows', icon: <ProjectOutlined />, label: 'Workflow Editor', onClick: () => navigate('/workflows') },
        { key: '/custom-apps', icon: <ApiOutlined />, label: 'Custom Apps', onClick: () => navigate('/custom-apps') },
        { key: '/notifications', icon: <BellOutlined />, label: 'Notifications', onClick: () => navigate('/notifications') },
        { key: '/api-explorer', icon: <ApiOutlined />, label: 'Rest API Explorer', onClick: () => navigate('/api-explorer') },
        { key: '/permission-groups', icon: <SafetyOutlined />, label: 'Permission Groups', onClick: () => openList('permission-groups-list', 'permission-group') },
        { key: '/roles', icon: <LockOutlined />, label: 'Roles', onClick: () => openList('roles-list', 'role') },
        { key: '/acl', icon: <SafetyOutlined />, label: 'ACL', onClick: () => navigate('/acl') },
        { key: '/logs', icon: <FileSearchOutlined />, label: 'Logs', onClick: () => navigate('/logs') },
        { key: '/system-properties', icon: <ControlOutlined />, label: 'System Properties', onClick: () => navigate('/system-properties') },
      ],
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/app/profile'),
    },
    {
      key: 'portal',
      icon: <CustomerServiceOutlined />,
      label: 'Open Portal',
      onClick: () => navigate('/portal'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
      onClick: () => {
        logout();
        navigate('/login');
      },
    },
  ];

  // Get current selected key from pathname
  const selectedKey = location.pathname;

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={SIDEBAR_WIDTH}
        collapsedWidth={SIDEBAR_COLLAPSED_WIDTH}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
        className="custom-scrollbar"
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0 16px',
          }}
        >
          {collapsed ? (
            <div
              style={{
                color: 'white',
                fontSize: 24,
                fontWeight: 'bold',
              }}
            >
              O
            </div>
          ) : (
            <img
              src="/opsit_logo_v2.png"
              alt="OpsIT"
              style={{ height: 45, width: 'auto' }}
            />
          )}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
        />
      </Sider>

      <Layout style={{ marginLeft: collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH, transition: 'all 0.2s' }}>
        <Header
          style={{
            padding: '0 24px',
            background: isDarkMode ? '#141414' : '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: isDarkMode ? '0 1px 4px rgba(0,0,0,.3)' : '0 1px 4px rgba(0,21,41,.08)',
            borderBottom: isDarkMode ? '1px solid #303030' : 'none',
          }}
        >
          <div>
            {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              style: { fontSize: 18, cursor: 'pointer', color: isDarkMode ? '#fff' : '#000' },
              onClick: () => setCollapsed(!collapsed),
            })}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <Input.Search
              placeholder="Search tickets (e.g. INC0000001)..."
              allowClear
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 300 }}
              enterButton={<SearchOutlined />}
            />

            <Tooltip title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
              <div
                onClick={toggleTheme}
                style={{
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: 20,
                  color: isDarkMode ? '#ffd700' : '#667eea',
                  transition: 'all 0.3s',
                }}
              >
                {isDarkMode ? <BulbFilled /> : <BulbOutlined />}
              </div>
            </Tooltip>

            <Tooltip title="Notifications">
              <Badge count={0} showZero={false}>
                <BellOutlined
                  style={{
                    fontSize: 20,
                    cursor: 'pointer',
                    color: isDarkMode ? '#fff' : '#595959',
                  }}
                  onClick={() => message.info('No notifications')}
                />
              </Badge>
            </Tooltip>

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div
              className="user-profile-dropdown"
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '8px 20px',
                borderRadius: '8px',
                transition: 'background 0.2s',
              }}
            >
              <Avatar
                icon={<UserOutlined />}
                size={42}
                style={{ backgroundColor: '#667eea' }}
              />
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', minWidth: 0 }}>
                <Text strong style={{ fontSize: 14, lineHeight: '20px', margin: 0 }}>
                  {user ? `${user.first_name} ${user.last_name}` : ''}
                </Text>
                <Text type="secondary" style={{ fontSize: 12, lineHeight: '16px', margin: 0 }}>
                  {user?.is_admin ? 'Administrator' : user?.is_support_agent ? 'Support Agent' : 'User'}
                </Text>
              </div>
            </div>
          </Dropdown>
          </div>
        </Header>

        <Content
          style={{
            margin: '24px',
            padding: 24,
            minHeight: 280,
            background: isDarkMode ? '#1f1f1f' : '#fff',
            borderRadius: 8,
          }}
        >
          <TabManager />
        </Content>
      </Layout>
    </Layout>
  );
};

export default DashboardLayout;
