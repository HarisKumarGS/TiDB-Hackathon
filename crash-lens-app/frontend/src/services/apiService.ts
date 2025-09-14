import { Repository, Crash, CrashDetail, ApiCrashDetailResponse } from '@/types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://127.0.0.1:8000/api/v1';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Repository Management
  async getRepositories(): Promise<Repository[]> {
    const response = await this.request<{success: boolean, message: string, data: Repository[], total: number}>('/repositories');
    return response.data || [];
  }

  async addRepository(repository: Omit<Repository, 'id'>): Promise<Repository> {
    const response = await this.request<{success: boolean, message: string, data: Repository}>('/repositories', {
      method: 'POST',
      body: JSON.stringify(repository),
    });
    return response.data;
  }

  async removeRepository(id: string): Promise<void> {
    return this.request<void>(`/repositories/${id}`, {
      method: 'DELETE',
    });
  }

  // Crash Management
  async getCrashes(repositoryId?: string): Promise<Crash[]> {
    if (repositoryId) {
      const response = await this.request<{success: boolean, message: string, data: Crash[], total: number}>(`/repositories/${repositoryId}/crashes`);
      return response.data || [];
    } else {
      // Return empty array if no repository ID provided
      return [];
    }
  }

  async getCrashDetail(id: string): Promise<ApiCrashDetailResponse> {
    const response = await this.request<ApiCrashDetailResponse>(`/crashes/${id}/rca`);
    return response;
  }

  async updateCrashStatus(
    id: string, 
    status: 'Resolved' | 'Closed',
    comment?: string
  ): Promise<Crash> {
    const response = await this.request<{success: boolean, message: string, data: Crash}>(`/crashes/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status, comment }),
    });
    return response.data;
  }

  async resolveCrash(id: string): Promise<Crash> {
    return this.updateCrashStatus(id, 'Resolved');
  }

  async closeCrash(id: string, comment: string): Promise<Crash> {
    return this.updateCrashStatus(id, 'Closed', comment);
  }

  // Analytics
  async getCrashAnalytics(repositoryId: string, timeframe: string) {
    return this.request(`/analytics/${repositoryId}?timeframe=${timeframe}`);
  }

  // Insights
  async getInsights(repositoryId: string) {
    const response = await this.request<{
      total_crashes: number;
      critical_issues: number;
      affected_users: number;
      resolved_today: number;
      crashes_past_3_days: number;
      weekly_data: Array<{
        week: string;
        crashes: number;
        resolved: number;
      }>;
      severity_breakdown: {
        critical: number;
        high: number;
        medium: number;
        low: number;
      };
      component_breakdown: Array<{
        component: string;
        count: number;
        percentage: number;
      }>;
      generated_at: string;
    }>(`/insights/${repositoryId}`);
    return response;
  }

  // GitHub Integration
  async createPullRequest(crashRcaId: string): Promise<{
    message: string;
    crash_rca_id: string;
    pr_details: {
      pr_url: string;
      pr_number: number;
      branch_name: string;
      title: string;
      body: string;
    };
  }> {
    const response = await this.request<{
      message: string;
      crash_rca_id: string;
      pr_details: {
        pr_url: string;
        pr_number: number;
        branch_name: string;
        title: string;
        body: string;
      };
    }>(`/github/create-pr/${crashRcaId}`, {
      method: 'POST',
    });
    return response;
  }

  async getPullRequestStatus(crashRcaId: string): Promise<{
    crash_rca_id: string;
    has_git_diff: boolean;
    can_create_pr: boolean;
    message: string;
  }> {
    const response = await this.request<{
      crash_rca_id: string;
      has_git_diff: boolean;
      can_create_pr: boolean;
      message: string;
    }>(`/github/pr-status/${crashRcaId}`);
    return response;
  }

  async validateGitDiff(crashRcaId: string): Promise<{
    crash_rca_id: string;
    is_valid: boolean;
    files_count?: number;
    files?: string[];
    can_create_pr: boolean;
    error?: string;
    message?: string;
  }> {
    const response = await this.request<{
      crash_rca_id: string;
      is_valid: boolean;
      files_count?: number;
      files?: string[];
      can_create_pr: boolean;
      error?: string;
      message?: string;
    }>(`/github/validate-diff/${crashRcaId}`, {
      method: 'POST',
    });
    return response;
  }

  // Crash Simulation
  async simulateCrash(request: {
    scenario: string;
    format?: string;
    min_logs?: number;
    no_jitter?: boolean;
    users_impacted?: number;
    repository_id: string;
    comment?: string;
  }): Promise<{
    success: boolean;
    crash_id: string;
    scenario: string;
    error_details: {
      title: string;
      description: string;
      severity: string;
      component: string;
      error_type: string;
    };
    users_impacted: number;
    logs_generated: number;
    sample_link: string;
    slack_notification_sent: boolean;
    database_entry_created: boolean;
    message: string;
  }> {
    const response = await this.request<{
      success: boolean;
      crash_id: string;
      scenario: string;
      error_details: {
        title: string;
        description: string;
        severity: string;
        component: string;
        error_type: string;
      };
      users_impacted: number;
      logs_generated: number;
      sample_link: string;
      slack_notification_sent: boolean;
      database_entry_created: boolean;
      message: string;
    }>('/simulate-crash', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response;
  }
}

export const apiService = new ApiService();

// Error handling utilities
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public endpoint?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Retry utility for failed requests
export async function withRetry<T>(
  operation: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> {
  for (let i = 0; i < retries; i++) {
    try {
      return await operation();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
  throw new Error('Max retries exceeded');
}
