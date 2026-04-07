import React from 'react';
import { Select, Tag } from 'antd';
import type { SysChoice } from '../../../types/metadata';

interface ChoiceFieldProps {
  choices: SysChoice[];
  disabled?: boolean;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

const ChoiceField: React.FC<ChoiceFieldProps> = ({ choices, disabled, placeholder, ...rest }) => {
  return (
    <Select
      showSearch
      allowClear
      disabled={disabled}
      placeholder={placeholder}
      optionFilterProp="label"
      {...rest}
    >
      {choices.map((c) => (
        <Select.Option key={c.value} value={c.value} label={c.label}>
          {c.color ? <Tag color={c.color}>{c.label}</Tag> : c.label}
        </Select.Option>
      ))}
    </Select>
  );
};

export default ChoiceField;
