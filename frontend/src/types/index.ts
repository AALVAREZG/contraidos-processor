/**
 * TypeScript type definitions
 */

export interface UploadResponse {
  upload_id: string;
  filename: string;
  size_bytes: number;
  file_type: string;
  status: string;
  message: string;
}

export interface AnalysisResult {
  analysis_id: string;
  analysis_type: string;
  status: string;
  summary: Summary;
  details: Details;
  validation: Validation;
  chart_data: ChartData;
  metadata: Record<string, any>;
  created_at: string;
}

export interface Summary {
  total_operations: number;
  arqueo_count: number;
  cargo_count: number;
  valid_cargo_count: number;
  invalid_cargo_count: number;
  unique_contraidos: number;
  date_range: {
    earliest: string | null;
    latest: string | null;
  };
}

export interface Details {
  by_fase: ByFase;
  by_contraido: ContraidoGroup[];
  orphan_operations: Operation[];
  calculations: Calculations;
}

export interface ByFase {
  AINP: {
    count: number;
    total_amount: number;
    operations: number[];
  };
  'M;P': {
    count: number;
    valid: {
      count: number;
      total_amount: number;
      operations: number[];
    };
    invalid: {
      count: number;
      total_amount: number;
      operations: number[];
    };
  };
}

export interface ContraidoGroup {
  num_contraido: string;
  operations: Operation[];
  total_arqueo: number;
  total_cargo_valid: number;
  total_cargo_invalid: number;
  net_balance: number;
  has_invalid_operations: boolean;
  needs_attention: boolean;
}

export interface Operation {
  num_operacion: number;
  ano: number;
  aplicacion: number;
  fase: string;
  estado: string | number;
  importe: number;
  cpgc: number;
  fecha: string;
  tercero: string;
  descripcion: string;
  is_valid: boolean;
}

export interface Calculations {
  total_arqueo_positive: number;
  total_cargo_negative: number;
  total_cargo_invalid: number;
  net_balance: number;
  percentage_invalid: number;
}

export interface Validation {
  is_valid: boolean;
  issues: Issue[];
  warnings: Issue[];
  total_issues: number;
  total_warnings: number;
}

export interface Issue {
  type: string;
  severity: string;
  operation?: number;
  contraido?: string;
  amount?: number;
  estado?: string | number;
  balance?: number;
  message: string;
}

export interface ChartData {
  fase_distribution: ChartConfig;
  balance_summary: ChartConfig;
  top_contraidos: ChartConfig;
}

export interface ChartConfig {
  type: string;
  title: string;
  data: any[];
}

export interface ExportRequest {
  format: 'excel' | 'json';
  options?: Record<string, any>;
}

export interface ExportResponse {
  export_id: string;
  download_url: string;
  filename: string;
  format: string;
  size_bytes: number;
}
