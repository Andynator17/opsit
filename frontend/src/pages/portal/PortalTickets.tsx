import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Card, Button, Space, Tag, Select, Typography } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { portalService } from '../../services/portal.service';

const { Title, Text } = Typography;

const statusColor: Record<string, string> = {
  new: 'blue',
  assigned: 'cyan',
  in_progress: 'processing',
  pending: 'warning',
  resolved: 'success',
  closed: 'default',
  cancelled: 'default',
  submitted: 'blue',
  pending_approval: 'warning',
  approved: 'green',
  fulfilled: 'success',
};

const priorityColor: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'blue',
  low: 'green',
};

const PortalTickets: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [typeFilter, setTypeFilter] = useState<string | undefined>();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['portal', 'tickets', page, pageSize, statusFilter, typeFilter],
    queryFn: () =>
      portalService.getMyTickets({
        page,
        page_size: pageSize,
        status: statusFilter,
        type: typeFilter,
      }),
  });

  const columns = [
    {
      title: 'Number',
      dataIndex: 'number',
      key: 'number',
      width: 130,
      render: (num: string) => <Text style={{ fontSize: 12, color: '#667eea', fontWeight: 600 }}>{num}</Text>,
    },
    {
      title: 'Type',
      dataIndex: 'sys_class_name',
      key: 'type',
      width: 100,
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: 'Subject',
      dataIndex: 'short_description',
      key: 'subject',
      ellipsis: true,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 90,
      render: (p: string) => <Tag color={priorityColor[p] || 'default'}>{p}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 130,
      render: (s: string) => (
        <Tag color={statusColor[s] || 'default'}>{s?.replace(/_/g, ' ')}</Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'sys_created_on',
      key: 'created',
      width: 110,
      render: (d: string) => new Date(d).toLocaleDateString(),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>My Tickets</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/portal/tickets/new')}>
          New Ticket
        </Button>
      </div>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="Filter by type"
            allowClear
            style={{ width: 160 }}
            value={typeFilter}
            onChange={(v) => { setTypeFilter(v); setPage(1); }}
            options={[
              { label: 'Incident', value: 'incident' },
              { label: 'Request', value: 'request' },
              { label: 'Change', value: 'change' },
            ]}
          />
          <Select
            placeholder="Filter by status"
            allowClear
            style={{ width: 160 }}
            value={statusFilter}
            onChange={(v) => { setStatusFilter(v); setPage(1); }}
            options={[
              { label: 'New', value: 'new' },
              { label: 'Assigned', value: 'assigned' },
              { label: 'In Progress', value: 'in_progress' },
              { label: 'Resolved', value: 'resolved' },
              { label: 'Closed', value: 'closed' },
              { label: 'Submitted', value: 'submitted' },
              { label: 'Pending Approval', value: 'pending_approval' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>Refresh</Button>
        </Space>
      </Card>

      <Table
        columns={columns}
        dataSource={data?.tasks ?? []}
        rowKey="id"
        loading={isLoading}
        onRow={(record) => ({
          onClick: () => navigate(`/portal/tickets/${record.id}`),
          style: { cursor: 'pointer' },
        })}
        pagination={{
          current: page,
          pageSize,
          total: data?.total ?? 0,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
          showSizeChanger: true,
          showTotal: (total) => `${total} tickets`,
        }}
      />
    </div>
  );
};

export default PortalTickets;
