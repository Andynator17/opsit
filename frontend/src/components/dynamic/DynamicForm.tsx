import React, { useEffect, useState, useCallback } from 'react';
import {
  Form, Input, InputNumber, Switch, DatePicker, Button, Space, Card,
  Row, Col, Spin, message, Tag, Typography,
} from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { TABLE_REGISTRY, isTicketType } from '../../config/tableRegistry';
import { useTableMetadata } from '../../hooks/useTableMetadata';
import { recordService } from '../../services/record.service';
import { useClientScripts } from '../../hooks/useClientScripts';
import { useTabs } from '../../context/TabContext';
import ChoiceField from './fields/ChoiceField';
import ReferenceField from './fields/ReferenceField';
import JsonArrayField, { KNOWN_SCHEMAS } from './fields/JsonArrayField';
import ActivitySection from './sections/ActivitySection';
import AttachmentSection from './sections/AttachmentSection';
import StatusWorkflow from './sections/StatusWorkflow';
import type { SysDictionary, FormSectionWithElements, SysUiElement } from '../../types/metadata';

const { TextArea } = Input;

interface DynamicFormProps {
  registryKey: string;
  recordId?: string;
  mode: 'view' | 'edit' | 'create';
  parentTabId?: string;
  currentTabId?: string;
}

const DynamicForm: React.FC<DynamicFormProps> = ({
  registryKey,
  recordId,
  mode: initialMode,
  parentTabId,
  currentTabId,
}) => {
  const entry = TABLE_REGISTRY[registryKey];
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const { updateTab, removeTab, addTab, addSubTab, removeSubTab } = useTabs();
  const isCreate = initialMode === 'create';
  const [trackedValues, setTrackedValues] = useState<Record<string, unknown>>({});

  const {
    fields, choices, formSections, getField, getChoices, getDisplayField, isLoading: metaLoading,
  } = useTableMetadata(entry?.tableName ?? '', entry?.sysClassName);

  // Fetch record data
  const { data: record, isLoading: recordLoading } = useQuery({
    queryKey: ['record', entry?.tableName, recordId],
    queryFn: () => recordService.getRecord(entry!.tableName, recordId!),
    enabled: !!entry && !!recordId && !isCreate,
  });

  // Client scripts
  const { fieldStates } = useClientScripts({
    tableName: entry?.tableName === 'task' ? 'tasks' : (entry?.tableName ?? ''),
    sysClassName: entry?.sysClassName ?? registryKey,
    formValues: trackedValues,
    mode: isCreate ? 'create' : 'edit',
  });

  // Populate form when record loads
  useEffect(() => {
    if (record) {
      const values: Record<string, unknown> = { ...record as Record<string, unknown> };
      fields.forEach((f) => {
        if ((f.field_type === 'datetime' || f.field_type === 'date') && values[f.column_name]) {
          values[f.column_name] = dayjs(String(values[f.column_name]));
        }
      });
      form.setFieldsValue(values);
    }
  }, [record, form, fields]);

  // Track form values for client scripts
  useEffect(() => {
    if (record && !isCreate) {
      setTrackedValues(record as Record<string, unknown>);
    }
  }, [record, isCreate]);

  const handleValuesChange = useCallback((_: unknown, allValues: Record<string, unknown>) => {
    setTrackedValues(allValues);
  }, []);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => recordService.createRecord(entry!.tableName, data),
    onSuccess: (created) => {
      message.success(`${entry?.label ?? 'Record'} created`);
      queryClient.invalidateQueries({ queryKey: ['records', entry?.tableName] });

      const displayField = entry?.displayField ?? 'name';
      const newTabData = {
        id: String(created.id),
        title: String(created[displayField] || created.name || created.number || created.id),
        type: 'form' as const,
        closable: true,
        ticketType: isTicketType(registryKey) ? registryKey : undefined,
        listType: registryKey,
        mode: 'edit' as const,
      };
      if (parentTabId) {
        addSubTab(parentTabId, newTabData);
      } else {
        addTab(newTabData);
      }
      if (currentTabId && parentTabId) {
        removeSubTab(parentTabId, currentTabId);
      } else if (currentTabId) {
        removeTab(currentTabId);
      }
    },
    onError: (error: { response?: { data?: { detail?: string } } }) => {
      message.error(error.response?.data?.detail || 'Failed to create');
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => recordService.updateRecord(entry!.tableName, recordId!, data),
    onSuccess: (updated) => {
      message.success(`${entry?.label ?? 'Record'} updated`);
      queryClient.setQueryData(['record', entry?.tableName, recordId], updated);
      queryClient.invalidateQueries({ queryKey: ['records', entry?.tableName] });
      if (recordId) {
        const displayField = entry?.displayField ?? 'name';
        updateTab(recordId, { title: String(updated[displayField] || updated.name || updated.number || recordId) });
      }
    },
    onError: (error: { response?: { data?: { detail?: string } } }) => {
      message.error(error.response?.data?.detail || 'Failed to update');
    },
  });

  const handleSubmit = useCallback((values: Record<string, unknown>) => {
    const data = { ...values };
    fields.forEach((f) => {
      if ((f.field_type === 'datetime' || f.field_type === 'date') && data[f.column_name]) {
        data[f.column_name] = (data[f.column_name] as dayjs.Dayjs).toISOString();
      }
    });
    if (entry?.sysClassName && isCreate) {
      data.sys_class_name = entry.sysClassName;
    }
    if (isCreate) {
      createMutation.mutate(data);
    } else {
      updateMutation.mutate(data);
    }
  }, [fields, entry, isCreate, createMutation, updateMutation]);

  // Client script helpers
  const csField = useCallback((name: string, existingRules?: Record<string, unknown>[]) => ({
    hidden: fieldStates[name]?.hidden,
    rules: fieldStates[name]?.mandatory
      ? [...(existingRules || []), { required: true, message: 'This field is required' }]
      : existingRules,
  }), [fieldStates]);

  const isFieldReadonly = useCallback((name: string) => {
    return fieldStates[name]?.readonly;
  }, [fieldStates]);

  // Render a single field based on its dictionary definition
  const renderField = useCallback((fieldDef: SysDictionary) => {
    const disabled = isFieldReadonly(fieldDef.column_name);
    const placeholder = fieldDef.hint || undefined;

    switch (fieldDef.field_type) {
      case 'string':
        return <Input disabled={disabled} placeholder={placeholder} maxLength={fieldDef.max_length ?? undefined} />;
      case 'text':
        return <TextArea disabled={disabled} placeholder={placeholder} rows={4} />;
      case 'integer':
        return <InputNumber disabled={disabled} placeholder={placeholder} style={{ width: '100%' }} />;
      case 'boolean':
        return <Switch disabled={disabled} />;
      case 'datetime':
        return <DatePicker showTime disabled={disabled} style={{ width: '100%' }} />;
      case 'date':
        return <DatePicker disabled={disabled} style={{ width: '100%' }} />;
      case 'choice': {
        const fieldChoices = getChoices(fieldDef.column_name);
        return <ChoiceField choices={fieldChoices} disabled={disabled} placeholder={placeholder} />;
      }
      case 'reference': {
        const refTable = fieldDef.reference_table ?? '';
        // sys_db_object references store the table name string, not the UUID
        const useNameAsValue = refTable === 'sys_db_object';
        return (
          <ReferenceField
            referenceTable={refTable}
            displayField={fieldDef.reference_display_field ?? 'name'}
            valueField={useNameAsValue ? 'name' : 'id'}
            disabled={disabled}
            placeholder={placeholder}
          />
        );
      }
      case 'email':
        return <Input type="email" disabled={disabled} placeholder={placeholder} />;
      case 'phone':
        return <Input disabled={disabled} placeholder={placeholder} />;
      case 'url':
        return <Input type="url" disabled={disabled} placeholder={placeholder} />;
      case 'json':
        return <JsonArrayField columnName={fieldDef.column_name} disabled={disabled} />;
      case 'password':
        return <Input.Password disabled={disabled} placeholder={placeholder} />;
      default:
        return <Input disabled={disabled} placeholder={placeholder} />;
    }
  }, [isFieldReadonly, getChoices]);

  // Render a form element within a section
  const renderElement = useCallback((element: SysUiElement, sectionColumns: number) => {
    if (element.element_type === 'separator') {
      return <Col span={24} key={element.id}><hr style={{ border: 'none', borderTop: '1px solid #f0f0f0', margin: '8px 0' }} /></Col>;
    }
    if (element.element_type === 'annotation') {
      return (
        <Col span={24} key={element.id}>
          <Typography.Text type="secondary">{element.annotation_text}</Typography.Text>
        </Col>
      );
    }

    if (!element.field_name) return null;
    const fieldDef = getField(element.field_name);
    if (!fieldDef) return null;

    const baseSpan = sectionColumns === 1 ? 24 : 12;
    const colSpan = element.span > 1 ? 24 : baseSpan;

    const rules: Record<string, unknown>[] = [];
    if (fieldDef.is_mandatory) {
      rules.push({ required: true, message: `${fieldDef.label} is required` });
    }

    return (
      <Col span={colSpan} key={element.id}>
        <Form.Item
          name={fieldDef.column_name}
          label={fieldDef.label}
          valuePropName={fieldDef.field_type === 'boolean' ? 'checked' : 'value'}
          tooltip={fieldDef.description || undefined}
          {...csField(fieldDef.column_name, rules)}
        >
          {renderField(fieldDef)}
        </Form.Item>
      </Col>
    );
  }, [getField, csField, renderField]);

  // Render a section
  const renderSection = useCallback((section: FormSectionWithElements) => {
    if (section.section_type !== 'fields') return null;

    return (
      <Card
        key={section.id}
        title={section.title}
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Row gutter={16}>
          {section.elements.map((element) => renderElement(element, section.columns))}
        </Row>
      </Card>
    );
  }, [renderElement]);

  if (!entry) {
    return <div>Unknown table: {registryKey}</div>;
  }

  if (metaLoading || (recordLoading && !isCreate)) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />;
  }

  // Header data
  const rec = record as Record<string, unknown> | undefined;
  const isTicket = isTicketType(registryKey);
  const formTitle = isCreate
    ? `New ${entry.label}`
    : rec
      ? String(rec[entry.displayField] || rec.name || rec.number || recordId)
      : '';

  // Choice lookups for header badges
  const statusValue = rec?.status as string | undefined;
  const priorityValue = rec?.priority as string | undefined;
  const statusChoice = statusValue ? choices.find(c => c.field_name === 'status' && c.value === statusValue) : undefined;
  const priorityChoice = priorityValue ? choices.find(c => c.field_name === 'priority' && c.value === priorityValue) : undefined;

  // Priority color for left border accent
  const PRIORITY_COLORS: Record<string, string> = { critical: '#cf1322', high: '#fa8c16', medium: '#faad14', low: '#52c41a' };
  const accentColor = priorityValue ? PRIORITY_COLORS[priorityValue] ?? '#667eea' : '#667eea';

  // Build default values for create
  const initialValues: Record<string, unknown> = {};
  if (isCreate) {
    fields.forEach((f) => {
      if (f.default_value != null) {
        if (f.field_type === 'boolean') {
          initialValues[f.column_name] = f.default_value === 'true';
        } else if (f.field_type === 'integer') {
          initialValues[f.column_name] = Number(f.default_value);
        } else {
          initialValues[f.column_name] = f.default_value;
        }
      }
    });
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* Header */}
      {isTicket && !isCreate && rec ? (
        <Card
          size="small"
          style={{ marginBottom: 16, borderLeft: `4px solid ${accentColor}` }}
          bodyStyle={{ padding: '12px 16px' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space size="middle" align="center" wrap>
              <Typography.Title level={4} style={{ margin: 0 }}>{formTitle}</Typography.Title>
              {priorityChoice && <Tag color={priorityChoice.color || undefined}>{priorityChoice.label}</Tag>}
              {statusChoice && <Tag color={statusChoice.color || undefined}>{statusChoice.label}</Tag>}
              {statusValue && !statusChoice && <Tag>{statusValue}</Tag>}
              {rec.short_description && (
                <Typography.Text type="secondary" ellipsis style={{ maxWidth: 300 }}>
                  {String(rec.short_description)}
                </Typography.Text>
              )}
            </Space>
            <Space>
              {entry.hasStatusWorkflow && recordId && (
                <StatusWorkflow taskId={recordId} status={String(rec.status ?? '')} registryKey={registryKey} />
              )}
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={() => form.submit()}
                loading={createMutation.isPending || updateMutation.isPending}
              >
                Save
              </Button>
            </Space>
          </div>
        </Card>
      ) : (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Typography.Title level={3} style={{ margin: 0 }}>{formTitle}</Typography.Title>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={() => form.submit()}
            loading={createMutation.isPending || updateMutation.isPending}
          >
            {isCreate ? `Create ${entry.label}` : 'Save'}
          </Button>
        </div>
      )}

      {/* Form */}
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        onValuesChange={handleValuesChange}
        initialValues={initialValues}
      >
        {formSections.map((section) => renderSection(section))}
      </Form>

      {/* Task-specific sections */}
      {!isCreate && recordId && entry.hasAttachments && (
        <AttachmentSection taskId={recordId} />
      )}
      {!isCreate && recordId && rec && (entry.hasWorkNotes || entry.hasComments) && (
        <ActivitySection
          taskId={recordId}
          record={rec}
          showWorkNotes={entry.hasWorkNotes}
          showComments={entry.hasComments}
        />
      )}
    </div>
  );
};

export default DynamicForm;
