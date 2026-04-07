import React from 'react';
import { Card, Descriptions, Typography, Tag, Avatar, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';

const { Title } = Typography;

const PortalProfile: React.FC = () => {
  const { user } = useAuth();

  if (!user) return null;

  const initials = `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase();

  return (
    <div>
      <Title level={4} style={{ marginBottom: 16 }}>My Profile</Title>

      <Card>
        <Space align="start" size={24} style={{ marginBottom: 24 }}>
          <Avatar size={72} style={{ backgroundColor: '#667eea', fontSize: 28 }}>
            {initials}
          </Avatar>
          <div>
            <Title level={4} style={{ margin: 0 }}>
              {user.first_name} {user.last_name}
            </Title>
            <div style={{ marginTop: 4 }}>
              {user.job_title && <Tag>{user.job_title}</Tag>}
              {user.is_vip && <Tag color="gold">VIP</Tag>}
            </div>
          </div>
        </Space>

        <Descriptions bordered column={{ xs: 1, sm: 2 }} size="small">
          <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
          <Descriptions.Item label="Employee ID">{user.employee_id || '-'}</Descriptions.Item>
          <Descriptions.Item label="Phone">{user.phone || '-'}</Descriptions.Item>
          <Descriptions.Item label="Mobile">{user.mobile || '-'}</Descriptions.Item>
          <Descriptions.Item label="Department">{user.department || '-'}</Descriptions.Item>
          <Descriptions.Item label="Location">{user.location || '-'}</Descriptions.Item>
          <Descriptions.Item label="Language">{user.language}</Descriptions.Item>
          <Descriptions.Item label="Timezone">{user.timezone}</Descriptions.Item>
          <Descriptions.Item label="Account Status">
            <Tag color={user.is_active ? 'green' : 'red'}>
              {user.is_active ? 'Active' : 'Inactive'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Last Login">
            {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default PortalProfile;
