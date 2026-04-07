import React, { useState, useMemo, useCallback } from 'react';
import { Table, Button, Space, Tag, Input, Select, message, Popconfirm, Typography, Spin } from 'antd';
import { PlusOutlined, SearchOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import type { ColumnsType } from 'antd/es/table';
import { TABLE_REGISTRY, isTicketType } from '../../config/tableRegistry';
import { useTableMetadata } from '../../hooks/useTableMetadata';
import { recordService } from '../../services/record.service';
import { useTabs } from '../../context/TabContext';
import type { SysDictionary, SysChoice } from '../../types/metadata';

dayjs.extend(relativeTime);

const { Title } = Typography;

interface DynamicListProps {
  registryKey: string;
  parentTabId?: string;
  initialSearch?: string;
  title?: string;
  createButtonText?: string;
  showMyGroupsFilter?: boolean;
}

const DynamicList: React.FC<DynamicListProps> = ({
  registryKey,
  parentTabId,
  initialSearch = '',
  title: titleOverride,
  createButtonText,
  showMyGroupsFilter = false,
}) => {
  const entry = TABLE_REGISTRY[registryKey];
  const queryClient = useQueryClient();
  const { addTab, addSubTab } = useTabs();
  const [searchText, setSearchText] = useState(initialSearch);
  const [choiceFilters, setChoiceFilters] = useState<Record<string, string | undefined>>({});
  const [myGroupsOnly, setMyGroupsOnly] = useState(false);

  const { listColumns, fields, choices, getField, getChoices, isLoading: metaLoading } = useTableMetadata(
    entry?.tableName ?? '',
    entry?.sysClassName,
  );

  // Build API params
  const apiParams = useMemo(() => {
    if (!entry) return {};
    const params: Record<string, unknown> = { ...entry.defaultFilters };
    if (searchText) params.search = searchText;
    if (myGroupsOnly) params.assigned_to_my_groups = true;
    Object.entries(choiceFilters).forEach(([key, val]) => {
      if (val) params[key] = val;
    });
    return params;
  }, [entry, searchText, myGroupsOnly, choiceFilters]);

  const { data, isLoading: dataLoading } = useQuery({
    queryKey: ['records', entry?.tableName, apiParams],
    queryFn: () => recordService.getRecords(entry!.tableName, apiParams),
    enabled: !!entry,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => recordService.deleteRecord(entry!.tableName, id),
    onSuccess: () => {
      message.success(`${entry?.label ?? 'Record'} deleted`);
      queryClient.invalidateQueries({ queryKey: ['records', entry?.tableName] });
    },
    onError: () => message.error('Failed to delete'),
  });

  // Resolve a display value for a reference field from the record
  const resolveRefDisplay = useCallback((record: Record<string, unknown>, fieldDef: SysDictionary): string => {
    // Try nested object: field name without _id suffix
    const baseName = fieldDef.column_name.replace(/_id$/, '');
    const nested = record[baseName] as Record<string, unknown> | undefined;
    if (nested) {
      const displayField = fieldDef.reference_display_field || 'name';
      if (displayField === 'full_name' || displayField === 'email') {
        const fn = nested.first_name || '';
        const ln = nested.last_name || '';
        if (fn || ln) return `${fn} ${ln}`.trim();
        return String(nested.email || nested.name || nested.id || '');
      }
      return String(nested[displayField] ?? nested.name ?? nested.id ?? '');
    }
    // Fallback: raw value
    const raw = record[fieldDef.column_name];
    return raw ? String(raw) : '';
  }, []);

  // Build Ant Design columns from metadata
  const columns: ColumnsType<Record<string, unknown>> = useMemo(() => {
    if (!listColumns.length || !fields.length) return [];

    const cols: ColumnsType<Record<string, unknown>> = listColumns.map((col) => {
      const fieldDef = getField(col.field_name);
      const fieldType = fieldDef?.field_type ?? 'string';

      return {
        title: fieldDef?.label ?? col.field_name,
        key: col.field_name,
        dataIndex: col.field_name,
        width: col.width ?? undefined,
        sorter: col.sort_direction ? true : undefined,
        defaultSortOrder: col.sort_direction === 'asc' ? 'ascend' as const : col.sort_direction === 'desc' ? 'descend' as const : undefined,
        render: (_: unknown, record: Record<string, unknown>) => {
          const value = record[col.field_name];

          if (fieldType === 'choice') {
            const choiceList = getChoices(col.field_name);
            const choice = choiceList.find((c: SysChoice) => c.value === value);
            if (choice) {
              return <Tag color={choice.color || undefined}>{choice.label}</Tag>;
            }
            return value != null ? String(value) : '-';
          }

          if (fieldType === 'reference' && fieldDef) {
            const display = resolveRefDisplay(record, fieldDef);
            return display || '-';
          }

          if (fieldType === 'datetime') {
            return value ? dayjs(String(value)).fromNow() : '-';
          }

          if (fieldType === 'boolean') {
            return value ? <Tag color="green">Yes</Tag> : <Tag color="default">No</Tag>;
          }

          // Default: string
          return value != null ? String(value) : '-';
        },
      };
    });

    // Actions column
    cols.push({
      title: 'Actions',
      key: '_actions',
      width: 100,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link" size="small" icon={<EditOutlined />}
            onClick={(e) => { e.stopPropagation(); handleRecordClick(record); }}
          />
          <Popconfirm
            title={`Delete ${entry?.label ?? 'record'}?`}
            onConfirm={(e) => { e?.stopPropagation(); deleteMutation.mutate(String(record.id)); }}
            onCancel={(e) => e?.stopPropagation()}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />} onClick={(e) => e.stopPropagation()} />
          </Popconfirm>
        </Space>
      ),
    });

    return cols;
  }, [listColumns, fields, getField, getChoices, resolveRefDisplay, entry, deleteMutation]);

  // Identify which choice fields are in the column list (for filter dropdowns)
  const filterableChoiceFields = useMemo(() => {
    return listColumns
      .map((col) => getField(col.field_name))
      .filter((f): f is SysDictionary => !!f && f.field_type === 'choice');
  }, [listColumns, getField]);

  const handleRecordClick = useCallback((record: Record<string, unknown>) => {
    const displayField = entry?.displayField ?? 'name';
    const tabTitle = String(record[displayField] || record.name || record.number || record.id);
    const tabData = {
      id: String(record.id),
      title: tabTitle,
      type: 'form' as const,
      closable: true,
      ticketType: isTicketType(registryKey) ? registryKey : undefined,
      listType: registryKey,
      mode: 'view' as const,
    };
    if (parentTabId) {
      addSubTab(parentTabId, tabData);
    } else {
      addTab(tabData);
    }
  }, [entry, registryKey, parentTabId, addTab, addSubTab]);

  const handleCreateClick = useCallback(() => {
    const createTabId = `create-${registryKey}-${Date.now()}`;
    const tabData = {
      id: createTabId,
      title: `New ${entry?.label ?? 'Record'}`,
      type: 'form' as const,
      closable: true,
      mode: 'create' as const,
      ticketType: isTicketType(registryKey) ? registryKey : undefined,
      listType: registryKey,
    };
    if (parentTabId) {
      addSubTab(parentTabId, tabData);
    } else {
      addTab(tabData);
    }
  }, [entry, registryKey, parentTabId, addTab, addSubTab]);

  if (!entry) {
    return <div>Unknown table: {registryKey}</div>;
  }

  if (metaLoading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 100 }} />;
  }

  const displayTitle = titleOverride ?? entry.pluralLabel;
  const createText = createButtonText ?? `Create ${entry.label}`;
  const showCreateButton = createButtonText !== '';

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2}>{displayTitle}</Title>
          {showCreateButton && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateClick}>
              {createText}
            </Button>
          )}
        </div>
        <Space size="middle" wrap>
          <Input
            placeholder={`Search ${entry.pluralLabel.toLowerCase()}...`}
            prefix={<SearchOutlined />}
            style={{ width: 300 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />
          {filterableChoiceFields.map((fieldDef) => {
            const fieldChoices = getChoices(fieldDef.column_name);
            return (
              <Select
                key={fieldDef.column_name}
                placeholder={fieldDef.label}
                style={{ width: 160 }}
                onChange={(v) => setChoiceFilters((prev) => ({ ...prev, [fieldDef.column_name]: v }))}
                value={choiceFilters[fieldDef.column_name]}
                allowClear
              >
                {fieldChoices.map((c) => (
                  <Select.Option key={c.value} value={c.value}>{c.label}</Select.Option>
                ))}
              </Select>
            );
          })}
          {showMyGroupsFilter && (
            <Button
              type={myGroupsOnly ? 'primary' : 'default'}
              onClick={() => setMyGroupsOnly(!myGroupsOnly)}
            >
              My Groups
            </Button>
          )}
        </Space>
        <Table
          columns={columns}
          dataSource={data?.items ?? []}
          loading={dataLoading}
          rowKey="id"
          onRow={(record) => ({
            onClick: () => handleRecordClick(record),
            style: { cursor: 'pointer' },
          })}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            total: data?.total,
            showTotal: (total) => `Total ${total} ${entry.pluralLabel.toLowerCase()}`,
          }}
        />
      </Space>
    </div>
  );
};

export default DynamicList;
