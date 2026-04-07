import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Card, Typography, Statistic, Button, List, Tag, Space, Spin } from 'antd';
import {
  WarningOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  BookOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../context/AuthContext';
import { portalService } from '../../services/portal.service';

const { Title, Text, Paragraph } = Typography;

const statusColor: Record<string, string> = {
  new: 'blue',
  assigned: 'cyan',
  in_progress: 'processing',
  pending: 'warning',
  resolved: 'success',
  closed: 'default',
  submitted: 'blue',
  pending_approval: 'warning',
  approved: 'green',
  fulfilled: 'success',
};

const PortalOverview: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['portal', 'stats'],
    queryFn: () => portalService.getMyStats(),
  });

  const { data: ticketData, isLoading: ticketsLoading } = useQuery({
    queryKey: ['portal', 'tickets', 'recent'],
    queryFn: () => portalService.getMyTickets({ page: 1, page_size: 5 }),
  });

  const quickActions = [
    {
      title: 'Report an Issue',
      description: 'Something broken? Let us know.',
      icon: <WarningOutlined style={{ fontSize: 28, color: '#ff4d4f' }} />,
      onClick: () => navigate('/portal/tickets/new?type=incident'),
    },
    {
      title: 'Request a Service',
      description: 'Need access, software, or hardware?',
      icon: <AppstoreOutlined style={{ fontSize: 28, color: '#667eea' }} />,
      onClick: () => navigate('/portal/tickets/new?type=request'),
    },
    {
      title: 'Knowledge Base',
      description: 'Find answers and guides.',
      icon: <BookOutlined style={{ fontSize: 28, color: '#52c41a' }} />,
      onClick: () => navigate('/portal/knowledge'),
    },
  ];

  return (
    <div>
      {/* Welcome */}
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>
          Welcome back, {user?.first_name}!
        </Title>
        <Paragraph type="secondary">
          Your IT Self-Service Hub — report issues, request services, and track your tickets.
        </Paragraph>
      </div>

      {/* Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Open Incidents"
              value={stats?.open_incidents ?? 0}
              loading={statsLoading}
              prefix={<WarningOutlined />}
              valueStyle={{ color: (stats?.open_incidents ?? 0) > 0 ? '#ff4d4f' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Open Requests"
              value={stats?.open_requests ?? 0}
              loading={statsLoading}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: (stats?.open_requests ?? 0) > 0 ? '#667eea' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Pending Approvals"
              value={stats?.pending_approvals ?? 0}
              loading={statsLoading}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: (stats?.pending_approvals ?? 0) > 0 ? '#faad14' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            <Statistic
              title="Resolved (30d)"
              value={stats?.resolved_last_30_days ?? 0}
              loading={statsLoading}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Title level={5} style={{ marginBottom: 12 }}>Quick Actions</Title>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {quickActions.map((action) => (
          <Col xs={24} sm={8} key={action.title}>
            <Card
              hoverable
              onClick={action.onClick}
              style={{ textAlign: 'center', height: '100%' }}
              bodyStyle={{ padding: '24px 16px' }}
            >
              <div style={{ marginBottom: 12 }}>{action.icon}</div>
              <Text strong style={{ display: 'block', marginBottom: 4 }}>{action.title}</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>{action.description}</Text>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Recent Tickets */}
      <Card
        title="Recent Tickets"
        extra={
          <Space>
            <Button type="link" onClick={() => navigate('/portal/tickets')}>View all</Button>
            <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => navigate('/portal/tickets/new')}>
              New Ticket
            </Button>
          </Space>
        }
      >
        {ticketsLoading ? (
          <div style={{ textAlign: 'center', padding: 24 }}><Spin /></div>
        ) : (ticketData?.tasks?.length ?? 0) === 0 ? (
          <div style={{ textAlign: 'center', padding: 24 }}>
            <Text type="secondary">No tickets yet. Use the quick actions above to get started!</Text>
          </div>
        ) : (
          <List
            dataSource={ticketData?.tasks ?? []}
            renderItem={(ticket: any) => (
              <List.Item
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/portal/tickets/${ticket.id}`)}
                actions={[
                  <Tag color={statusColor[ticket.status] || 'default'} key="status">
                    {ticket.status?.replace(/_/g, ' ')}
                  </Tag>,
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text style={{ fontSize: 12, color: '#667eea', fontWeight: 600 }}>{ticket.number}</Text>
                      <Text>{ticket.short_description}</Text>
                    </Space>
                  }
                  description={
                    <Space size="small">
                      <Tag style={{ textTransform: 'capitalize' }}>{ticket.sys_class_name}</Tag>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {new Date(ticket.sys_created_on).toLocaleDateString()}
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default PortalOverview;
