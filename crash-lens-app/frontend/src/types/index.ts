// API Response interfaces to match the actual API structure
export interface RCAData {
  id: string;
  crash_id: string;
  created_at: string;
  updated_at: string;
  description: string;
  problem_identification: string;
  data_collection: string;
  root_cause_identification: string;
  solution: string;
  git_diff: string;
  pull_request_url?: string;
  author: any;
  supporting_documents?: string[];
}

export interface ApiCrashDetailResponse {
  data: {
    crash: {
      id: string;
      component: string;
      created_at: string;
      error_log: string;
      error_type: string;
      impacted_users: number;
      severity: 'critical' | 'high' | 'medium' | 'low';
      status: 'open' | 'in progress' | 'resolved' | 'closed';
      updated_at: string;
      comment: string | null;
    };
    rca: RCAData;
  };
  message: string;
  success: boolean;
}

export interface Repository {
  id: string;
  name: string;
  url: string;
  document_url?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  // Additional frontend-specific fields
  owner?: string;
  crashCount?: number;
  lastCrash?: string;
}

export interface Crash {
  id: string;
  repository_id: string;
  created_at: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in progress' | 'resolved' | 'closed';
  component: string;
  error_type: string;
  description?: string;
  impacted_users: number;
  comment?: string;
  error_log?: string;
  updated_at?: string;
}

export interface CrashDetail extends Crash {
  rca_id: string;
  problemIdentification: string;
  dataCollection: string;
  analysis: string;
  rootCause: string;
  solution: string;
  changesRequired: string;
  gitDiff: string;
  pullRequestUrl?: string;
  author: {
    name: string;
    email: string;
    avatar: string;
  } | null;
  stakeholders: Array<{
    name: string;
    role: string;
    email: string;
  }>;
  supportingDocs: Array<{
    title: string;
    url: string;
    type: string;
  }>;
}

// Insights API interfaces
export interface WeeklyCrashData {
  week: string;
  crashes: number;
  resolved: number;
}

export interface SeverityCount {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface ComponentCount {
  component: string;
  count: number;
  percentage: number;
}

export interface InsightsData {
  total_crashes: number;
  critical_issues: number;
  affected_users: number;
  resolved_today: number;
  crashes_past_3_days: number;
  weekly_data: WeeklyCrashData[];
  severity_breakdown: SeverityCount;
  component_breakdown: ComponentCount[];
  generated_at: string;
}
