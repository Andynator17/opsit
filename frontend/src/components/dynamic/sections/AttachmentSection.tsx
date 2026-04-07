import React, { useCallback } from 'react';
import { Card, Upload, Table, Button, Popconfirm, Space, Tag, message, Empty } from 'antd';
import { UploadOutlined, DownloadOutlined, DeleteOutlined, PaperClipOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import attachmentService from '../../../services/attachment.service';
import type { AttachmentInfo } from '../../../services/attachment.service';

interface AttachmentSectionProps {
  taskId: string;
  readOnly?: boolean;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const AttachmentSection: React.FC<AttachmentSectionProps> = ({ taskId, readOnly = false }) => {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['attachments', taskId],
    queryFn: () => attachmentService.getAttachments(taskId),
    enabled: !!taskId,
  });

  const attachments = data?.attachments ?? [];

  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => attachmentService.uploadFiles(taskId, files),
    onSuccess: () => {
      message.success('File(s) uploaded');
      queryClient.invalidateQueries({ queryKey: ['attachments', taskId] });
    },
    onError: () => message.error('Upload failed'),
  });

  const deleteMutation = useMutation({
    mutationFn: (attachmentId: string) => attachmentService.deleteAttachment(taskId, attachmentId),
    onSuccess: () => {
      message.success('Attachment deleted');
      queryClient.invalidateQueries({ queryKey: ['attachments', taskId] });
    },
    onError: () => message.error('Delete failed'),
  });

  const handleDownload = useCallback((att: AttachmentInfo) => {
    attachmentService.downloadFile(taskId, att.id, att.file_name);
  }, [taskId]);

  const columns = [
    {
      title: 'File',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (name: string, record: AttachmentInfo) => (
        <Button type="link" onClick={() => handleDownload(record)} style={{ padding: 0 }}>
          <PaperClipOutlined /> {name}
        </Button>
      ),
    },
    {
      title: 'Size',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: 'Type',
      dataIndex: 'content_type',
      key: 'content_type',
      width: 120,
      render: (type: string) => <Tag>{type.split('/').pop()}</Tag>,
    },
    {
      title: 'Uploaded By',
      key: 'uploaded_by',
      width: 150,
      render: (_: unknown, record: AttachmentInfo) =>
        record.uploaded_by
          ? `${record.uploaded_by.first_name} ${record.uploaded_by.last_name}`
          : '-',
    },
    {
      title: 'Date',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    ...(!readOnly
      ? [
          {
            title: '',
            key: '_actions',
            width: 80,
            render: (_: unknown, record: AttachmentInfo) => (
              <Space>
                <Button type="link" size="small" icon={<DownloadOutlined />} onClick={() => handleDownload(record)} />
                <Popconfirm title="Delete attachment?" onConfirm={() => deleteMutation.mutate(record.id)}>
                  <Button type="link" size="small" danger icon={<DeleteOutlined />} />
                </Popconfirm>
              </Space>
            ),
          },
        ]
      : []),
  ];

  return (
    <Card
      title={`Attachments (${attachments.length})`}
      size="small"
      style={{ marginBottom: 16 }}
      extra={
        !readOnly && (
          <Upload
            multiple
            showUploadList={false}
            beforeUpload={(_, fileList) => {
              uploadMutation.mutate(fileList as unknown as File[]);
              return false;
            }}
          >
            <Button icon={<UploadOutlined />} loading={uploadMutation.isPending}>
              Upload
            </Button>
          </Upload>
        )
      }
    >
      {attachments.length > 0 ? (
        <Table
          columns={columns}
          dataSource={attachments}
          rowKey="id"
          loading={isLoading}
          pagination={false}
          size="small"
        />
      ) : (
        <Empty description="No attachments" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      )}
    </Card>
  );
};

export default AttachmentSection;
