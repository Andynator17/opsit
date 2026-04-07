import api from './api';

export interface AttachmentInfo {
  id: string;
  task_id: string;
  file_name: string;
  file_size: number;
  content_type: string;
  uploaded_by_id: string;
  uploaded_by?: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  created_at: string;
}

export interface AttachmentListResponse {
  total: number;
  attachments: AttachmentInfo[];
}

const attachmentService = {
  /**
   * Upload files to a task (multipart/form-data).
   */
  async uploadFiles(taskId: string, files: File[]): Promise<AttachmentInfo[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post<AttachmentInfo[]>(
      `/tasks/${taskId}/attachments/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * List all attachments for a task.
   */
  async getAttachments(taskId: string): Promise<AttachmentListResponse> {
    const response = await api.get<AttachmentListResponse>(
      `/tasks/${taskId}/attachments/`
    );
    return response.data;
  },

  /**
   * Download attachment with auth token (blob download).
   */
  async downloadFile(taskId: string, attachmentId: string, fileName?: string): Promise<void> {
    const response = await api.get(
      `/tasks/${taskId}/attachments/${attachmentId}/download`,
      { responseType: 'blob' }
    );

    // Use provided filename, or try Content-Disposition, or fallback
    let downloadName = fileName || 'download';
    if (!fileName) {
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+?)"?$/);
        if (match) downloadName = match[1];
      }
    }

    // Create temporary download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', downloadName);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  /**
   * Delete an attachment (soft-delete).
   */
  async deleteAttachment(taskId: string, attachmentId: string): Promise<void> {
    await api.delete(`/tasks/${taskId}/attachments/${attachmentId}`);
  },
};

export default attachmentService;
