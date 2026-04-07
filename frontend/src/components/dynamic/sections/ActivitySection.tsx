import React, { useState, useCallback } from 'react';
import { Card, Tabs, List, Input, Button, Tag, Typography, Space, Timeline, Empty, message } from 'antd';
import { SendOutlined, HistoryOutlined, MessageOutlined, FileTextOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import auditService from '../../../services/audit.service';
import type { AuditLogEntry } from '../../../services/audit.service';
import { recordService } from '../../../services/record.service';
import { useAuth } from '../../../context/AuthContext';

dayjs.extend(relativeTime);

const { TextArea } = Input;
const { Text } = Typography;

interface ActivitySectionProps {
  taskId: string;
  record: Record<string, unknown>;
  showWorkNotes?: boolean;
  showComments?: boolean;
  readOnly?: boolean;
}

interface NoteEntry {
  author: string;
  date: string;
  comment: string;
  source?: string;
}

const ActivitySection: React.FC<ActivitySectionProps> = ({
  taskId,
  record,
  showWorkNotes = true,
  showComments = true,
  readOnly = false,
}) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [workNoteText, setWorkNoteText] = useState('');
  const [commentText, setCommentText] = useState('');

  const workNotes = (record.work_notes as NoteEntry[] | null) ?? [];
  const comments = (record.comments as NoteEntry[] | null) ?? [];

  // Fetch audit trail
  const { data: auditLogs = [], isLoading: auditLoading } = useQuery({
    queryKey: ['audit-logs', taskId],
    queryFn: () => auditService.getAuditLogs(taskId),
    enabled: !!taskId,
  });

  // Mutation to add work note / comment
  const addEntryMutation = useMutation({
    mutationFn: (payload: { field: 'work_notes' | 'comments'; entries: NoteEntry[] }) =>
      recordService.updateRecord('task', taskId, { [payload.field]: payload.entries }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['record', 'task', taskId], updated);
      queryClient.invalidateQueries({ queryKey: ['audit-logs', taskId] });
    },
    onError: () => message.error('Failed to save'),
  });

  const handleAddWorkNote = useCallback(() => {
    if (!workNoteText.trim()) return;
    const newEntry: NoteEntry = {
      author: user ? `${user.first_name} ${user.last_name}` : 'Unknown',
      date: new Date().toLocaleString(),
      comment: workNoteText.trim(),
      source: 'agent',
    };
    addEntryMutation.mutate({ field: 'work_notes', entries: [...workNotes, newEntry] });
    setWorkNoteText('');
  }, [workNoteText, workNotes, user, addEntryMutation]);

  const handleAddComment = useCallback(() => {
    if (!commentText.trim()) return;
    const newEntry: NoteEntry = {
      author: user ? `${user.first_name} ${user.last_name}` : 'Unknown',
      date: new Date().toLocaleString(),
      comment: commentText.trim(),
      source: 'agent',
    };
    addEntryMutation.mutate({ field: 'comments', entries: [...comments, newEntry] });
    setCommentText('');
  }, [commentText, comments, user, addEntryMutation]);

  const renderNoteList = (notes: NoteEntry[]) => {
    if (!notes.length) return <Empty description="No entries yet" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    return (
      <List
        dataSource={[...notes].reverse()}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              title={
                <Space>
                  <Text strong>{item.author}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>{item.date}</Text>
                  {item.source && <Tag>{item.source}</Tag>}
                </Space>
              }
              description={<Text style={{ whiteSpace: 'pre-wrap' }}>{item.comment}</Text>}
            />
          </List.Item>
        )}
      />
    );
  };

  const renderAuditTrail = () => {
    if (auditLoading) return <Text type="secondary">Loading...</Text>;
    if (!auditLogs.length) return <Empty description="No audit history" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    return (
      <Timeline
        items={auditLogs.map((log: AuditLogEntry) => ({
          key: log.id,
          children: (
            <div>
              <Text strong>
                {log.changed_by
                  ? `${log.changed_by.first_name} ${log.changed_by.last_name}`
                  : 'System'}
              </Text>
              <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                {dayjs(log.changed_at).fromNow()}
              </Text>
              <div>
                {log.action === 'create' ? (
                  <Text>Created this record</Text>
                ) : log.field_name ? (
                  <Text>
                    Changed <Tag>{log.field_name}</Tag>
                    {log.old_value && <>{` from "${log.old_value}"`}</>}
                    {log.new_value && <>{` to "${log.new_value}"`}</>}
                  </Text>
                ) : (
                  <Text>Updated record</Text>
                )}
              </div>
            </div>
          ),
        }))}
      />
    );
  };

  const tabItems = [];

  if (showWorkNotes) {
    tabItems.push({
      key: 'work_notes',
      label: <><FileTextOutlined /> Work Notes ({workNotes.length})</>,
      children: (
        <>
          {!readOnly && (
            <div style={{ marginBottom: 16 }}>
              <TextArea
                rows={3}
                placeholder="Add a work note (internal)..."
                value={workNoteText}
                onChange={(e) => setWorkNoteText(e.target.value)}
                onPressEnter={(e) => { if (e.ctrlKey) handleAddWorkNote(); }}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleAddWorkNote}
                loading={addEntryMutation.isPending}
                style={{ marginTop: 8 }}
                disabled={!workNoteText.trim()}
              >
                Add Work Note
              </Button>
            </div>
          )}
          {renderNoteList(workNotes)}
        </>
      ),
    });
  }

  if (showComments) {
    tabItems.push({
      key: 'comments',
      label: <><MessageOutlined /> Comments ({comments.length})</>,
      children: (
        <>
          {!readOnly && (
            <div style={{ marginBottom: 16 }}>
              <TextArea
                rows={3}
                placeholder="Add a comment (visible to customer)..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                onPressEnter={(e) => { if (e.ctrlKey) handleAddComment(); }}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleAddComment}
                loading={addEntryMutation.isPending}
                style={{ marginTop: 8 }}
                disabled={!commentText.trim()}
              >
                Add Comment
              </Button>
            </div>
          )}
          {renderNoteList(comments)}
        </>
      ),
    });
  }

  tabItems.push({
    key: 'audit',
    label: <><HistoryOutlined /> Audit Trail</>,
    children: renderAuditTrail(),
  });

  return (
    <Card title="Activity" size="small" style={{ marginBottom: 16 }}>
      <Tabs items={tabItems} defaultActiveKey={showWorkNotes ? 'work_notes' : 'comments'} />
    </Card>
  );
};

export default ActivitySection;
