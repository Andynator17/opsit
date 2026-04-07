import { useQuery } from '@tanstack/react-query';
import { metadataService } from '../services/metadata.service';
import type { SysDictionary, SysChoice, FormSectionWithElements, SysUiList, SysRelationship } from '../types/metadata';

interface UseTableMetadataResult {
  fields: SysDictionary[];
  choices: SysChoice[];
  relationships: SysRelationship[];
  formSections: FormSectionWithElements[];
  listColumns: SysUiList[];

  getField: (columnName: string) => SysDictionary | undefined;
  getChoices: (fieldName: string) => SysChoice[];
  getDisplayField: () => string;

  isLoading: boolean;
  error: Error | null;
}

export function useTableMetadata(tableName: string, sysClassName?: string): UseTableMetadataResult {
  const metadataQuery = useQuery({
    queryKey: ['table-metadata', tableName, sysClassName],
    queryFn: () => metadataService.getTableMetadata(tableName, sysClassName),
    staleTime: 10 * 60 * 1000, // 10 min
  });

  const formQuery = useQuery({
    queryKey: ['form-layout', tableName, sysClassName],
    queryFn: () => metadataService.getFormLayout(tableName, 'default', sysClassName),
    staleTime: 10 * 60 * 1000,
  });

  const listQuery = useQuery({
    queryKey: ['list-layout', tableName, sysClassName],
    queryFn: () => metadataService.getListLayout(tableName, 'default', sysClassName),
    staleTime: 10 * 60 * 1000,
  });

  const fields = metadataQuery.data?.fields ?? [];
  const choices = metadataQuery.data?.choices ?? [];
  const relationships = metadataQuery.data?.relationships ?? [];

  const getField = (columnName: string) => fields.find(f => f.column_name === columnName);

  const getChoices = (fieldName: string) => choices.filter(c => c.field_name === fieldName);

  const getDisplayField = () => metadataQuery.data?.table?.display_field ?? 'name';

  return {
    fields,
    choices,
    relationships,
    formSections: formQuery.data?.sections ?? [],
    listColumns: listQuery.data?.columns ?? [],
    getField,
    getChoices,
    getDisplayField,
    isLoading: metadataQuery.isLoading || formQuery.isLoading || listQuery.isLoading,
    error: (metadataQuery.error ?? formQuery.error ?? listQuery.error) as Error | null,
  };
}
