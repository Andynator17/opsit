import React from 'react';
import { Select, Spin } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { recordService } from '../../../services/record.service';

interface ReferenceFieldProps {
  referenceTable: string;
  displayField?: string;
  valueField?: string;       // which field to use as the stored value (default: "id")
  disabled?: boolean;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

const ReferenceField: React.FC<ReferenceFieldProps> = ({
  referenceTable,
  displayField = 'name',
  valueField = 'id',
  disabled,
  placeholder,
  ...rest
}) => {
  const { data, isLoading } = useQuery({
    queryKey: ['ref-options', referenceTable],
    queryFn: () => recordService.getRecords(referenceTable, {}),
    staleTime: 5 * 60 * 1000,
  });

  const options = (data?.items ?? []).map((item) => {
    let label: string;
    if (displayField === 'full_name' || referenceTable === 'user') {
      const fn = String(item.first_name ?? '');
      const ln = String(item.last_name ?? '');
      const email = String(item.email ?? '');
      label = fn || ln ? `${fn} ${ln}`.trim() : email;
    } else {
      label = String(item[displayField] ?? item.name ?? item.id ?? '');
    }
    return { value: String(item[valueField] ?? item.id), label };
  });

  return (
    <Select
      showSearch
      allowClear
      disabled={disabled}
      placeholder={placeholder}
      optionFilterProp="label"
      loading={isLoading}
      notFoundContent={isLoading ? <Spin size="small" /> : 'No data'}
      options={options}
      {...rest}
    />
  );
};

export default ReferenceField;
