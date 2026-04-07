import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Tag, Spin, Avatar, Tabs, Breadcrumb, Empty, Input, Button, message } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  DownOutlined,
  UpOutlined,
  PaperClipOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { portalService } from '../../services/portal.service';
import { useTheme } from '../../context/ThemeContext';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

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

const priorityLabel: Record<string, string> = {
  critical: '1 - Critical',
  high: '2 - High',
  medium: '3 - Medium',
  low: '4 - Low',
};

const typeLabel: Record<string, string> = {
  incident: 'Incident',
  request: 'Request',
  change: 'Change',
  problem: 'Problem',
  task: 'Task',
};

const PortalTicketDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const queryClient = useQueryClient();
  const [showMore, setShowMore] = useState(false);
  const [commentText, setCommentText] = useState('');

  const { data: ticket, isLoading } = useQuery({
    queryKey: ['portal', 'ticket', id],
    queryFn: () => portalService.getMyTicket(id!),
    enabled: !!id,
  });

  const commentMutation = useMutation({
    mutationFn: (text: string) => portalService.addComment(id!, text),
    onSuccess: () => {
      setCommentText('');
      queryClient.invalidateQueries({ queryKey: ['portal', 'ticket', id] });
      message.success('Comment added');
    },
    onError: () => {
      message.error('Failed to add comment');
    },
  });

  const handleAddComment = () => {
    const trimmed = commentText.trim();
    if (!trimmed) return;
    commentMutation.mutate(trimmed);
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 48 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!ticket) {
    return <Empty description="Ticket not found" />;
  }

  const callerName = ticket.caller
    ? `${ticket.caller.first_name} ${ticket.caller.last_name}`
    : '-';
  const callerInitials = ticket.caller
    ? `${ticket.caller.first_name?.[0] || ''}${ticket.caller.last_name?.[0] || ''}`.toUpperCase()
    : '?';
  const affectedName = ticket.affected_user
    ? `${ticket.affected_user.first_name} ${ticket.affected_user.last_name}`
    : '-';
  const affectedInitials = ticket.affected_user
    ? `${ticket.affected_user.first_name?.[0] || ''}${ticket.affected_user.last_name?.[0] || ''}`.toUpperCase()
    : '?';
  const companyName = ticket.company?.name || '-';
  const categoryDisplay = [ticket.category, ticket.subcategory].filter(Boolean).join(' / ') || '-';

  // Merge and sort activity (comments + work_notes)
  const activities: Array<{
    type: 'comment' | 'work_note';
    user_name: string;
    initials: string;
    text: string;
    created_at: string;
  }> = [];

  // Comments use agent format: { author, date, comment } — portal also adds "source"
  if (ticket.comments && Array.isArray(ticket.comments)) {
    ticket.comments.forEach((c: any) => {
      const name = c.author || c.user_name || 'System';
      activities.push({
        type: 'comment',
        user_name: name,
        initials: name.substring(0, 2).toUpperCase(),
        text: c.comment || c.text || '',
        created_at: c.date || c.created_at || '',
      });
    });
  }

  // Work notes use same agent format: { author, date, comment }
  if (ticket.work_notes && Array.isArray(ticket.work_notes)) {
    ticket.work_notes.forEach((w: any) => {
      const name = w.author || w.user_name || 'System';
      activities.push({
        type: 'work_note',
        user_name: name,
        initials: name.substring(0, 2).toUpperCase(),
        text: w.comment || w.text || '',
        created_at: w.date || w.created_at || '',
      });
    });
  }

  activities.sort((a, b) => {
    if (!a.created_at || !b.created_at) return 0;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  const cardBg = isDarkMode ? '#1f1f1f' : '#fff';
  const borderColor = isDarkMode ? '#303030' : '#f0f0f0';
  const metaLabelColor = isDarkMode ? '#8c8c8c' : '#00695c';
  const titleBannerBg = isDarkMode ? '#1a2332' : '#e8f4f8';
  const titleBannerBorder = isDarkMode ? '#1e3a5f' : '#b2dfdb';

  return (
    <div>
      {/* Breadcrumb */}
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          {
            title: (
              <span style={{ cursor: 'pointer' }} onClick={() => navigate('/portal')}>
                <HomeOutlined /> Home
              </span>
            ),
          },
          {
            title: (
              <span style={{ cursor: 'pointer' }} onClick={() => navigate('/portal/tickets')}>
                My Tickets
              </span>
            ),
          },
          { title: `${ticket.number}` },
        ]}
      />

      {/* Header: Number + Created/Updated/State */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
          flexWrap: 'wrap',
          gap: 8,
        }}
      >
        <div>
          <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Number</Text>
          <Text strong style={{ fontSize: 16 }}>{ticket.number}</Text>
        </div>
        <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Created</Text>
            <Text>{dayjs(ticket.sys_created_on).fromNow()}</Text>
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>Updated</Text>
            <Text>{dayjs(ticket.sys_updated_on).fromNow()}</Text>
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>State</Text>
            <Tag color={statusColor[ticket.status] || 'default'} style={{ margin: 0 }}>
              {ticket.status?.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
            </Tag>
          </div>
        </div>
      </div>

      {/* Title Banner */}
      <div
        style={{
          background: titleBannerBg,
          borderLeft: `4px solid ${titleBannerBorder}`,
          padding: '16px 20px',
          borderRadius: 4,
          marginBottom: 4,
        }}
      >
        <Title level={4} style={{ margin: 0 }}>{ticket.short_description}</Title>
        {ticket.description && (
          <div
            style={{ cursor: 'pointer', marginTop: 8, color: '#667eea', fontSize: 13 }}
            onClick={() => setShowMore(!showMore)}
          >
            {showMore ? <UpOutlined /> : <DownOutlined />} Show {showMore ? 'less' : 'more'}
          </div>
        )}
      </div>

      {/* Expandable description */}
      {showMore && ticket.description && (
        <div
          style={{
            background: cardBg,
            border: `1px solid ${borderColor}`,
            borderTop: 'none',
            padding: '16px 20px',
            borderRadius: '0 0 4px 4px',
            marginBottom: 0,
          }}
        >
          <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{ticket.description}</Paragraph>
        </div>
      )}

      {/* Metadata Row */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 32,
          padding: '16px 0',
          borderBottom: `1px solid ${borderColor}`,
          marginBottom: 24,
        }}
      >
        <div>
          <Text style={{ fontSize: 12, color: metaLabelColor, display: 'block' }}>Category</Text>
          <Text>{categoryDisplay}</Text>
        </div>
        <div>
          <Text style={{ fontSize: 12, color: metaLabelColor, display: 'block' }}>Priority</Text>
          <Text>{priorityLabel[ticket.priority] || ticket.priority}</Text>
        </div>
        <div>
          <Text style={{ fontSize: 12, color: metaLabelColor, display: 'block' }}>Account</Text>
          <Text>{companyName}</Text>
        </div>
        <div>
          <Text style={{ fontSize: 12, color: metaLabelColor, display: 'block' }}>Caller</Text>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
            <Avatar size={24} style={{ backgroundColor: '#667eea', fontSize: 11 }}>
              {callerInitials}
            </Avatar>
            <Text>{callerName}</Text>
          </div>
        </div>
        <div>
          <Text style={{ fontSize: 12, color: metaLabelColor, display: 'block' }}>Affected User</Text>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
            <Avatar size={24} style={{ backgroundColor: '#667eea', fontSize: 11 }}>
              {affectedInitials}
            </Avatar>
            <Text>{affectedName}</Text>
          </div>
        </div>
      </div>

      {/* Resolution info */}
      {ticket.resolution && (
        <div
          style={{
            background: isDarkMode ? '#1a2e1a' : '#f6ffed',
            border: `1px solid ${isDarkMode ? '#274916' : '#b7eb8f'}`,
            padding: '12px 20px',
            borderRadius: 4,
            marginBottom: 24,
          }}
        >
          <Text strong style={{ display: 'block', marginBottom: 4 }}>Resolution</Text>
          <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{ticket.resolution}</Paragraph>
        </div>
      )}

      {/* Tabs: Activity | Attachments */}
      <Tabs
        defaultActiveKey="activity"
        items={[
          {
            key: 'activity',
            label: 'Activity',
            children: (
              <div>
                {/* Comment input */}
                {ticket.status !== 'closed' && ticket.status !== 'cancelled' && (
                  <div
                    style={{
                      display: 'flex',
                      gap: 12,
                      marginBottom: 20,
                      padding: 16,
                      background: cardBg,
                      border: `1px solid ${borderColor}`,
                      borderRadius: 8,
                    }}
                  >
                    <Input.TextArea
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      placeholder="Add a comment..."
                      autoSize={{ minRows: 2, maxRows: 6 }}
                      style={{ flex: 1 }}
                      onPressEnter={(e) => {
                        if (e.ctrlKey || e.metaKey) {
                          handleAddComment();
                        }
                      }}
                    />
                    <Button
                      type="primary"
                      icon={<SendOutlined />}
                      onClick={handleAddComment}
                      loading={commentMutation.isPending}
                      disabled={!commentText.trim()}
                      style={{ alignSelf: 'flex-end' }}
                    >
                      Send
                    </Button>
                  </div>
                )}

                {activities.length === 0 ? (
                  <div style={{ padding: '24px 0', textAlign: 'center' }}>
                    <Text type="secondary">No activity yet.</Text>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {activities.map((activity, idx) => (
                      <div
                        key={idx}
                        style={{
                          display: 'flex',
                          gap: 12,
                          padding: '16px',
                          borderRadius: 8,
                          background: cardBg,
                          borderLeft: `4px solid ${activity.type === 'work_note' ? '#d4a017' : '#667eea'}`,
                          border: `1px solid ${borderColor}`,
                          borderLeftWidth: 4,
                          borderLeftColor: activity.type === 'work_note' ? '#d4a017' : '#667eea',
                        }}
                      >
                        <Avatar
                          size={36}
                          style={{
                            backgroundColor: activity.type === 'work_note' ? '#d4a017' : '#667eea',
                            flexShrink: 0,
                            fontSize: 13,
                          }}
                        >
                          {activity.initials}
                        </Avatar>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 4 }}>
                            <Text strong>{activity.user_name}</Text>
                            <div>
                              <Text type="secondary" style={{ fontSize: 12, marginRight: 8 }}>
                                {activity.created_at ? dayjs(activity.created_at).fromNow() : ''}
                              </Text>
                              <Tag
                                color={activity.type === 'work_note' ? 'gold' : 'blue'}
                                style={{ fontSize: 11 }}
                              >
                                {activity.type === 'work_note' ? 'Work notes' : 'Additional comments'}
                              </Tag>
                            </div>
                          </div>
                          <Paragraph
                            style={{ margin: '8px 0 0', whiteSpace: 'pre-wrap' }}
                          >
                            {activity.text}
                          </Paragraph>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ),
          },
          {
            key: 'attachments',
            label: (
              <span>
                <PaperClipOutlined /> Attachments
              </span>
            ),
            children: (
              <div style={{ padding: '24px 0', textAlign: 'center' }}>
                <Text type="secondary">No attachments.</Text>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
};

export default PortalTicketDetail;
