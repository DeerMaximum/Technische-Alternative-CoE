export interface GetConfigEntryResponse {
  entries: ConfigEntryMetadata[]
}

export interface ConfigEntryMetadata {
  title: string;
  entry_id: string;
}

export interface ExposedEntityConfig{
  entity_id: string;
  id: number;
}

export interface ExposedEntitiesConfig{
  analog: ExposedEntityConfig[],
  digital: ExposedEntityConfig[],
}

export interface ExposedEntitiesConfigResponse {
  config: ExposedEntitiesConfig;
}

