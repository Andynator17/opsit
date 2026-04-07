import React, { useState } from 'react';
import { Button, Space, Modal, Form, Input, Select, message } from 'antd';
import {
  UserAddOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  LockOutlined,
} from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../services/api';
import ReferenceField from '../fields/ReferenceField';

const { TextArea } = Input;

interface StatusWorkflowProps {
  taskId: string;
  status: string;
  registryKey: string;
}

const RESOLUTION_REASONS = [
  { value: 'fixed', label: 'Fixed' },
  { value: 'workaround', label: 'Workaround' },
  { value: 'duplicate', label: 'Duplicate' },
  { value: 'user_error', label: 'User Error' },
  { value: 'cannot_reproduce', label: 'Cannot Reproduce' },
  { value: 'not_a_bug', label: 'Not a Bug' },
  { value: 'by_design', label: 'By Design' },
];

const StatusWorkflow: React.FC<StatusWorkflowProps> = ({ taskId, status, registryKey }) => {
  const queryClient = useQueryClient();
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [resolveModalOpen, setResolveModalOpen] = useState(false);
  const [closeModalOpen, setCloseModalOpen] = useState(false);
  const [assignForm] = Form.useForm();
  const [resolveForm] = Form.useForm();
  const [closeForm] = Form.useForm();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['record', 'task', taskId] });
    queryClient.invalidateQueries({ queryKey: ['records', 'task'] });
    queryClient.invalidateQueries({ queryKey: ['audit-logs', taskId] });
  };

  const assignMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => api.post(`/tasks/${taskId}/assign`, data).then(r => r.data),
    onSuccess: (updated) => {
      message.success('Task assigned');
      queryClient.setQueryData(['record', 'task', taskId], updated);
      invalidate();
      setAssignModalOpen(false);
      assignForm.resetFields();
    },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Assign failed'),
  });

  const startWorkMutation = useMutation({
    mutationFn: () => api.put(`/tasks/${taskId}`, { status: 'in_progress' }).then(r => r.data),
    onSuccess: (updated) => {
      message.success('Work started');
      queryClient.setQueryData(['record', 'task', taskId], updated);
      invalidate();
    },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed'),
  });

  const resolveMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => api.post(`/tasks/${taskId}/resolve`, data).then(r => r.data),
    onSuccess: (updated) => {
      message.success('Task resolved');
      queryClient.setQueryData(['record', 'task', taskId], updated);
      invalidate();
      setResolveModalOpen(false);
      resolveForm.resetFields();
    },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Resolve failed'),
  });

  const closeMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => api.post(`/tasks/${taskId}/close`, data).then(r => r.data),
    onSuccess: (updated) => {
      message.success('Task closed');
      queryClient.setQueryData(['record', 'task', taskId], updated);
      invalidate();
      setCloseModalOpen(false);
      closeForm.resetFields();
    },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Close failed'),
  });

  const s = status?.toLowerCase();

  return (
    <>
      <Space wrap style={{ marginBottom: 16 }}>
        {(s === 'new' || s === 'assigned' || s === 'in_progress') && (
          <Button icon={<UserAddOutlined />} onClick={() => setAssignModalOpen(true)}>
            Assign
          </Button>
        )}
        {(s === 'assigned') && (
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={() => startWorkMutation.mutate()}
            loading={startWorkMutation.isPending}
          >
            Start Work
          </Button>
        )}
        {(s === 'in_progress' || s === 'assigned') && (
          <Button icon={<CheckCircleOutlined />} onClick={() => setResolveModalOpen(true)}>
            Resolve
          </Button>
        )}
        {(s === 'resolved' || s === 'fulfilled' || s === 'complete') && (
          <Button icon={<LockOutlined />} onClick={() => setCloseModalOpen(true)}>
            Close
          </Button>
        )}
      </Space>

      {/* Assign Modal */}
      <Modal
        title="Assign Task"
        open={assignModalOpen}
        onCancel={() => setAssignModalOpen(false)}
        onOk={() => assignForm.submit()}
        confirmLoading={assignMutation.isPending}
      >
        <Form form={assignForm} layout="vertical" onFinish={(v) => assignMutation.mutate(v)}>
          <Form.Item name="assignment_group_id" label="Support Group">
            <ReferenceField referenceTable="support_group" displayField="name" />
          </Form.Item>
          <Form.Item name="assigned_to_id" label="Assigned To">
            <ReferenceField referenceTable="user" displayField="full_name" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Resolve Modal */}
      <Modal
        title="Resolve Task"
        open={resolveModalOpen}
        onCancel={() => setResolveModalOpen(false)}
        onOk={() => resolveForm.submit()}
        confirmLoading={resolveMutation.isPending}
      >
        <Form form={resolveForm} layout="vertical" onFinish={(v) => resolveMutation.mutate(v)}>
          <Form.Item name="resolution_reason" label="Resolution Reason" rules={[{ required: true }]}>
            <Select options={RESOLUTION_REASONS} placeholder="Select reason" />
          </Form.Item>
          <Form.Item name="resolution" label="Resolution" rules={[{ required: true, min: 10, message: 'Min 10 characters' }]}>
            <TextArea rows={4} placeholder="Describe the resolution..." />
          </Form.Item>
          <Form.Item name="root_cause" label="Root Cause">
            <TextArea rows={2} />
          </Form.Item>
          <Form.Item name="workaround" label="Workaround">
            <TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Close Modal */}
      <Modal
        title="Close Task"
        open={closeModalOpen}
        onCancel={() => setCloseModalOpen(false)}
        onOk={() => closeForm.submit()}
        confirmLoading={closeMutation.isPending}
      >
        <Form form={closeForm} layout="vertical" onFinish={(v) => closeMutation.mutate(v)}>
          <Form.Item name="close_notes" label="Close Notes">
            <TextArea rows={3} placeholder="Optional closing notes..." />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default StatusWorkflow;
