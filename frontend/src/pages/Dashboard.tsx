import React, { useState } from 'react';
import { Card, Typography, Space, Spin, Alert, Table, Tag, Select, Row, Col } from 'antd';
import {
  AlertOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  UserOutlined,
  TeamOutlined,
  SyncOutlined,
  WarningOutlined,
  BellOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import dayjs from 'dayjs';
import { useTabs } from '../context/TabContext';
import { createTabContent } from '../components/tabContentFactory';

const { Title } = Typography;
const { Option } = Select;

interface AgentDashboardStats {
  new_unassigned_incidents: number;
  my_approvals_open: number;
  my_requests_open: number;
  sla_breach: number;
  support_group_incidents: number;
  support_group_changes: number;
  support_group_tasks: number;
  my_incidents: number;
  my_changes: number;
  my_tasks: number;
}

interface TicketSummary {
  id: string;
  ticket_number: string;
  ticket_type: string;
  title: string;
  priority: string;
  status: string;
  assigned_to_name: string | null;
  support_group_name: string | null;
  created_at: string;
  due_date: string | null;
  sla_breach: boolean;
}

interface OverviewConsoleResponse {
  total: number;
  tickets: TicketSummary[];
}

const DashboardContent: React.FC = () => {
  const { addTab } = useTabs();
  const [ticketTypeFilter, setTicketTypeFilter] = useState<string | undefined>(undefined);
  const [priorityFilter, setPriorityFilter] = useState<string | undefined>(undefined);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);

  // Fetch agent dashboard stats
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery<AgentDashboardStats>({
    queryKey: ['agentDashboardStats'],
    queryFn: async () => {
      const response = await api.get<AgentDashboardStats>('/dashboard/stats/agent');
      return response.data;
    },
    refetchInterval: 30000,
  });

  // Fetch overview console tickets
  const { data: overview, isLoading: overviewLoading, error: overviewError } = useQuery<OverviewConsoleResponse>({
    queryKey: ['overviewConsole', ticketTypeFilter, priorityFilter, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (ticketTypeFilter) params.append('ticket_type', ticketTypeFilter);
      if (priorityFilter) params.append('priority', priorityFilter);
      if (statusFilter) params.append('status', statusFilter);
      params.append('limit', '100');

      const response = await api.get<OverviewConsoleResponse>(`/dashboard/overview?${params.toString()}`);
      return response.data;
    },
    refetchInterval: 30000,
  });

  if (statsLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (statsError) {
    return (
      <Alert
        message="Error Loading Dashboard"
        description="Failed to load dashboard statistics. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: 'red',
      high: 'orange',
      medium: 'blue',
      low: 'green',
    };
    return colors[priority.toLowerCase()] || 'default';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'blue',
      assigned: 'cyan',
      in_progress: 'processing',
      pending_approval: 'warning',
      resolved: 'success',
      closed: 'default',
    };
    return colors[status.toLowerCase()] || 'default';
  };

  // Handle ticket click - open in tab
  const handleTicketClick = (record: TicketSummary) => {
    const meta = {
      id: record.id,
      title: record.ticket_number,
      type: 'form' as const,
      closable: true,
      ticketType: record.ticket_type,
      mode: 'view' as const,
    };
    addTab({ ...meta, content: createTabContent(meta) });
  };

  const columns = [
    {
      title: 'Ticket #',
      dataIndex: 'ticket_number',
      key: 'ticket_number',
      width: 160,
      render: (text: string) => <span style={{ fontWeight: 600 }}>{text}</span>,
    },
    {
      title: 'Type',
      dataIndex: 'ticket_type',
      key: 'ticket_type',
      width: 100,
      render: (type: string) => (
        <Tag icon={type === 'incident' ? <AlertOutlined /> : <FileTextOutlined />}>
          {type.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => (
        <Tag color={getPriorityColor(priority)}>{priority.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 140,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status.replace('_', ' ').toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Assigned To',
      dataIndex: 'assigned_to_name',
      key: 'assigned_to_name',
      width: 150,
      render: (name: string | null) => name || <Tag>Unassigned</Tag>,
    },
    {
      title: 'Support Group',
      dataIndex: 'support_group_name',
      key: 'support_group_name',
      width: 150,
    },
    {
      title: 'Created Date',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
  ];

  const statCards = [
    { title: 'New/Unassigned', value: stats?.new_unassigned_incidents || 0, icon: <ExclamationCircleOutlined />, color: '#cf1322' },
    { title: 'My Approvals', value: stats?.my_approvals_open || 0, icon: <CheckCircleOutlined />, color: '#faad14' },
    { title: 'My Requests', value: stats?.my_requests_open || 0, icon: <FileTextOutlined />, color: '#1890ff' },
    { title: 'SLA Breach', value: stats?.sla_breach || 0, icon: <WarningOutlined />, color: '#ff4d4f' },
    { title: 'SG Incidents', value: stats?.support_group_incidents || 0, icon: <TeamOutlined />, color: '#722ed1' },
    { title: 'SG Changes', value: stats?.support_group_changes || 0, icon: <SyncOutlined />, color: '#13c2c2' },
    { title: 'My Incidents', value: stats?.my_incidents || 0, icon: <UserOutlined />, color: '#eb2f96' },
    { title: 'My Changes', value: stats?.my_changes || 0, icon: <SyncOutlined />, color: '#52c41a' },
    { title: 'My Tasks', value: stats?.my_tasks || 0, icon: <BellOutlined />, color: '#faad14' },
    { title: 'SG Tasks', value: stats?.support_group_tasks || 0, icon: <TeamOutlined />, color: '#13c2c2' },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Title level={2}>Agent Dashboard</Title>

      {/* Statistics Cards - Simple Grid */}
      <Row gutter={[12, 12]}>
        {statCards.map((card, index) => (
          <Col xs={24} sm={12} md={8} lg={6} xl={6} key={index}>
            <Card hoverable bodyStyle={{ padding: '12px 16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                <span style={{ fontSize: 12, opacity: 0.65, fontWeight: 500 }}>{card.title}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: 20, color: card.color }}>{card.icon}</span>
                <span style={{ fontSize: 28, fontWeight: 600, color: card.color }}>{card.value}</span>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Overview Console */}
      <Card
        title={
          <Space>
            <TeamOutlined />
            <span>Overview Console - My Support Group Tickets</span>
          </Space>
        }
        extra={
          <Space>
            <Select
              placeholder="Ticket Type"
              style={{ width: 120 }}
              allowClear
              onChange={setTicketTypeFilter}
            >
              <Option value="incident">Incident</Option>
              <Option value="request">Request</Option>
              <Option value="change">Change</Option>
              <Option value="problem">Problem</Option>
              <Option value="task">Task</Option>
            </Select>
            <Select
              placeholder="Priority"
              style={{ width: 120 }}
              allowClear
              onChange={setPriorityFilter}
            >
              <Option value="critical">Critical</Option>
              <Option value="high">High</Option>
              <Option value="medium">Medium</Option>
              <Option value="low">Low</Option>
            </Select>
            <Select
              placeholder="Status"
              style={{ width: 150 }}
              allowClear
              onChange={setStatusFilter}
            >
              <Option value="new">New</Option>
              <Option value="assigned">Assigned</Option>
              <Option value="in_progress">In Progress</Option>
              <Option value="pending_approval">Pending Approval</Option>
            </Select>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={overview?.tickets || []}
          loading={overviewLoading}
          rowKey="id"
          onRow={(record) => ({
            onClick: () => handleTicketClick(record),
            style: { cursor: 'pointer' },
          })}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} tickets`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </Space>
  );
};

// Export DashboardContent as the default Dashboard component
const Dashboard: React.FC = DashboardContent;

export default Dashboard;
