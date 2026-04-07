import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Dropdown, Avatar, Space, Typography, Switch } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  BookOutlined,
  UserOutlined,
  LogoutOutlined,
  BulbOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

const PortalLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();

  const menuItems = [
    {
      key: '/portal',
      icon: <HomeOutlined />,
      label: 'Overview',
    },
    {
      key: '/portal/tickets',
      icon: <FileTextOutlined />,
      label: 'My Tickets',
    },
    {
      key: '/portal/services',
      icon: <AppstoreOutlined />,
      label: 'Services',
    },
    {
      key: '/portal/knowledge',
      icon: <BookOutlined />,
      label: 'Knowledge Base',
    },
  ];

  const getSelectedKey = () => {
    const path = location.pathname;
    if (path === '/portal' || path === '/portal/') return '/portal';
    if (path.startsWith('/portal/tickets')) return '/portal/tickets';
    if (path.startsWith('/portal/services')) return '/portal/services';
    if (path.startsWith('/portal/knowledge')) return '/portal/knowledge';
    return '/portal';
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'My Profile',
      onClick: () => navigate('/portal/profile'),
    },
    ...(user?.is_admin || user?.is_support_agent
      ? [
          {
            key: 'agent-view',
            icon: <ToolOutlined />,
            label: 'Agent View',
            onClick: () => navigate('/app/dashboard'),
          },
        ]
      : []),
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: () => {
        logout();
        navigate('/login');
      },
    },
  ];

  const initials = user
    ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    : '?';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          background: isDarkMode ? '#141414' : '#fff',
          borderBottom: isDarkMode ? '1px solid #303030' : '1px solid #f0f0f0',
          boxShadow: isDarkMode ? '0 1px 4px rgba(0,0,0,.3)' : '0 1px 4px rgba(0,21,41,.08)',
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            marginRight: 40,
          }}
          onClick={() => navigate('/portal')}
        >
          <img
            src="/opsit_logo_v2.png"
            alt="OpsIT"
            style={{ height: 36, width: 'auto' }}
          />
        </div>

        {/* Navigation */}
        <Menu
          mode="horizontal"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{
            flex: 1,
            border: 'none',
            background: 'transparent',
          }}
        />

        {/* Right side */}
        <Space size="middle" align="center">
          <Switch
            checked={isDarkMode}
            onChange={toggleTheme}
            checkedChildren={<BulbOutlined />}
            unCheckedChildren={<BulbOutlined />}
            size="small"
          />

          <Dropdown menu={{ items: userMenuItems }} trigger={['click']} placement="bottomRight">
            <Space style={{ cursor: 'pointer' }}>
              <Avatar
                size={32}
                style={{ backgroundColor: '#667eea' }}
              >
                {initials}
              </Avatar>
              <Text
                style={{
                  maxWidth: 150,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  color: isDarkMode ? '#fff' : '#595959',
                }}
              >
                {user?.first_name} {user?.last_name}
              </Text>
            </Space>
          </Dropdown>
        </Space>
      </Header>

      <Content
        style={{
          padding: '24px',
          maxWidth: 1200,
          width: '100%',
          margin: '0 auto',
        }}
      >
        <Outlet />
      </Content>

      <Footer
        style={{
          textAlign: 'center',
          background: isDarkMode ? '#141414' : '#fafafa',
          borderTop: isDarkMode ? '1px solid #303030' : '1px solid #f0f0f0',
          padding: '16px 24px',
        }}
      >
        <Text type="secondary" style={{ fontSize: 12 }}>
          OpsIT Self-Service Portal • Need help? Contact your IT department
        </Text>
      </Footer>
    </Layout>
  );
};

export default PortalLayout;
