import { Repository, Crash, CrashDetail } from '@/data/mockData';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:3001/api';

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
    return this.request<Repository[]>('/repository');
  }

  async addRepository(repository: Omit<Repository, 'id'>): Promise<Repository> {
    return this.request<Repository>('/repository', {
      method: 'POST',
      body: JSON.stringify(repository),
    });
  }

  async removeRepository(id: string): Promise<void> {
    return this.request<void>(`/repository/${id}`, {
      method: 'DELETE',
    });
  }

  // Crash Management
  async getCrashes(repositoryId?: string): Promise<Crash[]> {
    const query = repositoryId ? `?repositoryId=${repositoryId}` : '';
    return this.request<Crash[]>(`/crash${query}`);
  }

  async getCrashDetail(id: string): Promise<CrashDetail> {
    return this.request<CrashDetail>(`/crash/${id}`);
  }

  async updateCrashStatus(
    id: string, 
    status: 'Resolved' | 'Closed',
    comment?: string
  ): Promise<Crash> {
    return this.request<Crash>(`/crash/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status, comment }),
    });
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