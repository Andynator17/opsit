import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Form, Input, Select, Button, Typography, message, Space, Radio } from 'antd';
import { ArrowLeftOutlined, SendOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { portalService } from '../../services/portal.service';

const { Title, Text } = Typography;
const { TextArea } = Input;

const PortalNewTicket: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  const initialType = searchParams.get('type') || 'incident';
  const [ticketType, setTicketType] = useState(initialType);

  const { data: categories } = useQuery({
    queryKey: ['portal', 'categories', ticketType],
    queryFn: () => portalService.getCategories(ticketType),
  });

  const createMutation = useMutation({
    mutationFn: portalService.createTicket,
    onSuccess: (data) => {
      message.success(`Ticket ${data.number} created successfully!`);
      queryClient.invalidateQueries({ queryKey: ['portal'] });
      navigate(`/portal/tickets/${data.id}`);
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to create ticket');
    },
  });

  const handleSubmit = (values: any) => {
    createMutation.mutate({
      sys_class_name: ticketType,
      short_description: values.short_description,
      description: values.description,
      category: values.category,
      subcategory: values.subcategory,
      urgency: values.urgency || 'medium',
      impact: values.impact || 'medium',
    });
  };

  // Build category options from hierarchical data
  const parentCategories = categories?.filter((c) => !c.parent_category_id) ?? [];
  const getSubCategories = (parentId: string) =>
    categories?.filter((c) => c.parent_category_id === parentId) ?? [];

  const selectedCategory = Form.useWatch('category', form);

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/portal/tickets')}>
          Back
        </Button>
      </Space>

      <Card style={{ maxWidth: 700 }}>
        <Title level={4} style={{ marginBottom: 4 }}>
          {ticketType === 'incident' ? 'Report an Issue' : 'Request a Service'}
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          {ticketType === 'incident'
            ? 'Describe the issue you are experiencing and we will help you resolve it.'
            : 'Tell us what you need and we will get it sorted for you.'}
        </Text>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            urgency: 'medium',
            impact: 'medium',
          }}
        >
          {/* Ticket type selection */}
          <Form.Item label="What do you need?">
            <Radio.Group
              value={ticketType}
              onChange={(e) => {
                setTicketType(e.target.value);
                form.setFieldsValue({ category: undefined, subcategory: undefined });
              }}
              optionType="button"
              buttonStyle="solid"
            >
              <Radio.Button value="incident">Report an Issue</Radio.Button>
              <Radio.Button value="request">Request a Service</Radio.Button>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="short_description"
            label="Subject"
            rules={[
              { required: true, message: 'Please enter a subject' },
              { min: 5, message: 'Subject must be at least 5 characters' },
            ]}
          >
            <Input placeholder={ticketType === 'incident' ? 'Brief description of the issue' : 'What do you need?'} maxLength={255} />
          </Form.Item>

          <Form.Item
            name="description"
            label="Details"
          >
            <TextArea
              rows={4}
              placeholder={
                ticketType === 'incident'
                  ? 'Please describe the issue in detail: What happened? When did it start? What were you trying to do?'
                  : 'Please provide details about your request: What do you need? When do you need it? Any special requirements?'
              }
            />
          </Form.Item>

          {parentCategories.length > 0 && (
            <Form.Item name="category" label="Category">
              <Select
                placeholder="Select a category"
                allowClear
                options={parentCategories.map((c) => ({ label: c.name, value: c.name }))}
              />
            </Form.Item>
          )}

          {selectedCategory && getSubCategories(
            parentCategories.find((c) => c.name === selectedCategory)?.id || ''
          ).length > 0 && (
            <Form.Item name="subcategory" label="Subcategory">
              <Select
                placeholder="Select a subcategory"
                allowClear
                options={getSubCategories(
                  parentCategories.find((c) => c.name === selectedCategory)?.id || ''
                ).map((c) => ({ label: c.name, value: c.name }))}
              />
            </Form.Item>
          )}

          <Form.Item name="urgency" label="How urgent is this?">
            <Select
              options={[
                { label: 'Low — Can wait', value: 'low' },
                { label: 'Medium — Need help soon', value: 'medium' },
                { label: 'High — Blocking my work', value: 'high' },
                { label: 'Critical — Major outage', value: 'critical' },
              ]}
            />
          </Form.Item>

          <Form.Item name="impact" label="How many people are affected?">
            <Select
              options={[
                { label: 'Low — Just me', value: 'low' },
                { label: 'Medium — My team', value: 'medium' },
                { label: 'High — Department', value: 'high' },
                { label: 'Critical — Entire company', value: 'critical' },
              ]}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SendOutlined />}
              loading={createMutation.isPending}
              size="large"
            >
              Submit {ticketType === 'incident' ? 'Issue' : 'Request'}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default PortalNewTicket;
