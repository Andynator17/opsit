import React, { useCallback, useState } from 'react';
import { Button, Input, Select, Space, Card, Row, Col, Empty } from 'antd';
import { PlusOutlined, DeleteOutlined, CodeOutlined, TableOutlined } from '@ant-design/icons';

export interface JsonArrayColumn {
  key: string;
  label: string;
  type: 'input' | 'select';
  options?: { value: string; label: string }[];
  placeholder?: string;
  span?: number; // Col span out of 24, default auto
}

// Pre-defined schemas for known JSON array types
const CONDITION_OPERATORS = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'is_empty', label: 'Is Empty' },
  { value: 'is_not_empty', label: 'Is Not Empty' },
  { value: 'in', label: 'In' },
  { value: 'not_in', label: 'Not In' },
  { value: 'changed', label: 'Changed' },
  { value: 'changed_to', label: 'Changed To' },
  { value: 'changed_from', label: 'Changed From' },
];

const SERVER_ACTION_TYPES = [
  { value: 'set_value', label: 'Set Value' },
  { value: 'set_value_from_query', label: 'Set Value from Query' },
];

const CLIENT_UI_ACTION_TYPES = [
  { value: 'set_hidden', label: 'Set Hidden' },
  { value: 'set_readonly', label: 'Set Readonly' },
  { value: 'set_mandatory', label: 'Set Mandatory' },
  { value: 'set_value', label: 'Set Value' },
];

export const KNOWN_SCHEMAS: Record<string, JsonArrayColumn[]> = {
  conditions: [
    { key: 'field', label: 'Field', type: 'input', placeholder: 'Field name', span: 7 },
    { key: 'operator', label: 'Operator', type: 'select', options: CONDITION_OPERATORS, placeholder: 'Operator', span: 7 },
    { key: 'value', label: 'Value', type: 'input', placeholder: 'Value', span: 8 },
  ],
  actions: [
    { key: 'type', label: 'Type', type: 'select', options: SERVER_ACTION_TYPES, placeholder: 'Action type', span: 6 },
    { key: 'field', label: 'Field', type: 'input', placeholder: 'Field name', span: 6 },
    { key: 'value', label: 'Value', type: 'input', placeholder: 'Value', span: 10 },
  ],
  ui_actions: [
    { key: 'type', label: 'Type', type: 'select', options: CLIENT_UI_ACTION_TYPES, placeholder: 'Action type', span: 6 },
    { key: 'field', label: 'Field', type: 'input', placeholder: 'Field name', span: 7 },
    { key: 'value', label: 'Value', type: 'input', placeholder: 'Value (true/false or value)', span: 9 },
  ],
};

interface JsonArrayFieldProps {
  value?: Record<string, unknown>[];
  onChange?: (value: Record<string, unknown>[]) => void;
  columns?: JsonArrayColumn[];
  columnName?: string; // used to auto-detect schema
  disabled?: boolean;
}

const JsonArrayField: React.FC<JsonArrayFieldProps> = ({
  value = [],
  onChange,
  columns: columnsProp,
  columnName,
  disabled = false,
}) => {
  const [showRawJson, setShowRawJson] = useState(false);

  // Auto-detect schema from column name, fallback to prop, fallback to generic
  const columns = columnsProp ?? (columnName ? KNOWN_SCHEMAS[columnName] : undefined);

  // Raw JSON editor (used for unknown schemas or when toggled)
  const renderJsonEditor = () => (
    <Input.TextArea
      value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
      onChange={(e) => {
        try {
          onChange?.(JSON.parse(e.target.value));
        } catch {
          // ignore parse errors while typing
        }
      }}
      rows={6}
      disabled={disabled}
      placeholder="JSON array..."
      style={{ fontFamily: 'monospace', fontSize: 12 }}
    />
  );

  // If no known schema, always show raw JSON textarea
  if (!columns) {
    return renderJsonEditor();
  }

  const items = Array.isArray(value) ? value : [];

  const handleAdd = useCallback(() => {
    const empty: Record<string, unknown> = {};
    columns.forEach((col) => { empty[col.key] = ''; });
    onChange?.([...items, empty]);
  }, [items, columns, onChange]);

  const handleRemove = useCallback((index: number) => {
    const updated = items.filter((_, i) => i !== index);
    onChange?.(updated);
  }, [items, onChange]);

  const handleCellChange = useCallback((index: number, key: string, cellValue: unknown) => {
    const updated = items.map((item, i) =>
      i === index ? { ...item, [key]: cellValue } : item
    );
    onChange?.(updated);
  }, [items, onChange]);

  return (
    <Card
      size="small"
      bodyStyle={{ padding: items.length ? '8px 12px' : '12px' }}
      extra={
        <Button
          type="text"
          size="small"
          icon={showRawJson ? <TableOutlined /> : <CodeOutlined />}
          onClick={() => setShowRawJson(!showRawJson)}
          title={showRawJson ? 'Builder view' : 'JSON view'}
        />
      }
    >
      {showRawJson ? (
        renderJsonEditor()
      ) : (
        <>
          {items.length === 0 && (
            <Empty description="No entries" image={Empty.PRESENTED_IMAGE_SIMPLE} style={{ margin: '4px 0' }} />
          )}
          {items.length > 0 && (
            <>
              {/* Header row */}
              <Row gutter={8} style={{ marginBottom: 4 }}>
                {columns.map((col) => (
                  <Col span={col.span ?? Math.floor(22 / columns.length)} key={col.key}>
                    <span style={{ fontSize: 11, fontWeight: 600, opacity: 0.6, textTransform: 'uppercase' }}>{col.label}</span>
                  </Col>
                ))}
                <Col span={2} />
              </Row>
              {/* Data rows */}
              {items.map((item, index) => (
                <Row gutter={8} key={index} style={{ marginBottom: 6 }} align="middle">
                  {columns.map((col) => (
                    <Col span={col.span ?? Math.floor(22 / columns.length)} key={col.key}>
                      {col.type === 'select' ? (
                        <Select
                          size="small"
                          style={{ width: '100%' }}
                          value={item[col.key] as string || undefined}
                          onChange={(v) => handleCellChange(index, col.key, v)}
                          placeholder={col.placeholder}
                          options={col.options}
                          disabled={disabled}
                          allowClear
                        />
                      ) : (
                        <Input
                          size="small"
                          value={item[col.key] as string ?? ''}
                          onChange={(e) => handleCellChange(index, col.key, e.target.value)}
                          placeholder={col.placeholder}
                          disabled={disabled}
                        />
                      )}
                    </Col>
                  ))}
                  <Col span={2} style={{ textAlign: 'center' }}>
                    {!disabled && (
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemove(index)}
                      />
                    )}
                  </Col>
                </Row>
              ))}
            </>
          )}
          {!disabled && (
            <Button
              type="dashed"
              size="small"
              icon={<PlusOutlined />}
              onClick={handleAdd}
              style={{ width: '100%', marginTop: items.length ? 4 : 0 }}
            >
              Add Entry
            </Button>
          )}
        </>
      )}
    </Card>
  );
};

export default JsonArrayField;
