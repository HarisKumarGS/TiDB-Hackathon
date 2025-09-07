export interface Repository {
  id: string;
  name: string;
  url: string;
  created_at?: string;
  updated_at?: string;
  // Additional frontend-specific fields
  owner?: string;
  crashCount?: number;
  lastCrash?: string;
}

export interface Crash {
  id: string;
  repositoryId: string;
  timestamp: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  status: 'Open' | 'In Progress' | 'Resolved' | 'Closed';
  component: string;
  errorType: string;
  description: string;
  impactedUsers: number;
  logfileUrl?: string;
}

export interface CrashDetail extends Crash {
  problemIdentification: string;
  dataCollection: string;
  analysis: string;
  rootCause: string;
  solution: string;
  changesRequired: string;
  gitDiff: string;
  author: {
    name: string;
    email: string;
    avatar: string;
  };
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

export const mockRepositories: Repository[] = [
  {
    id: 'repo-1',
    name: 'web-frontend',
    url: 'https://github.com/company/web-frontend',
    owner: 'company',
    crashCount: 23,
    lastCrash: '2024-01-15T10:30:00Z'
  },
  {
    id: 'repo-2', 
    name: 'api-service',
    url: 'https://github.com/company/api-service',
    owner: 'company',
    crashCount: 15,
    lastCrash: '2024-01-14T08:15:00Z'
  },
  {
    id: 'repo-3',
    name: 'mobile-app',
    url: 'https://github.com/company/mobile-app', 
    owner: 'company',
    crashCount: 8,
    lastCrash: '2024-01-13T16:45:00Z'
  }
];

export const mockCrashes: Crash[] = [
  {
    id: 'crash-1',
    repositoryId: 'repo-1',
    timestamp: '2024-01-15T10:30:00Z',
    severity: 'Critical',
    status: 'Open',
    component: 'UserAuth',
    errorType: 'NullPointerException',
    description: 'Authentication service crashes during OAuth callback',
    impactedUsers: 1250,
    logfileUrl: '/logs/crash-1.log'
  },
  {
    id: 'crash-2',
    repositoryId: 'repo-1',
    timestamp: '2024-01-15T09:15:00Z',
    severity: 'High',
    status: 'In Progress',
    component: 'PaymentProcessor',
    errorType: 'TimeoutException',
    description: 'Payment processing timeout during peak hours',
    impactedUsers: 892,
    logfileUrl: '/logs/crash-2.log'
  },
  {
    id: 'crash-3',
    repositoryId: 'repo-2',
    timestamp: '2024-01-14T08:15:00Z',
    severity: 'Medium',
    status: 'Resolved',
    component: 'DataSync',
    errorType: 'DatabaseException',
    description: 'Database connection pool exhaustion',
    impactedUsers: 450,
    logfileUrl: '/logs/crash-3.log'
  },
  {
    id: 'crash-4',
    repositoryId: 'repo-1',
    timestamp: '2024-01-14T14:22:00Z',
    severity: 'Low',
    status: 'Closed',
    component: 'ImageUpload',
    errorType: 'ValidationError',
    description: 'File size validation bypass causing memory overflow',
    impactedUsers: 23,
    logfileUrl: '/logs/crash-4.log'
  },
  {
    id: 'crash-5',
    repositoryId: 'repo-3',
    timestamp: '2024-01-13T16:45:00Z',
    severity: 'Critical',
    status: 'Open',
    component: 'LocationService',
    errorType: 'PermissionException',
    description: 'GPS permission denial crashes the app on startup',
    impactedUsers: 2100,
    logfileUrl: '/logs/crash-5.log'
  }
];

export const mockCrashDetails: Record<string, CrashDetail> = {
  'crash-1': {
    ...mockCrashes[0],
    problemIdentification: 'OAuth callback endpoint is receiving malformed state parameters, causing a null pointer exception when attempting to validate the authentication token. This occurs specifically when users are redirected from third-party OAuth providers during the authentication flow.',
    dataCollection: 'Stack traces from authentication service logs, OAuth provider response headers, user session data, and network request logs from affected authentication attempts.',
    analysis: 'Root cause analysis reveals that the state parameter validation logic assumes a non-null value but OAuth providers occasionally send empty or malformed state values during network interruptions or when users rapidly navigate between authentication flows.',
    rootCause: 'The authentication state validation method lacks null-safety checks and proper error handling for malformed OAuth callback parameters. The code directly accesses the state parameter without validating its existence or format.',
    solution: 'Implement comprehensive null-safety checks in the OAuth callback handler, add proper validation for state parameters, and provide graceful fallback mechanisms for authentication failures.',
    changesRequired: 'Update AuthService.validateOAuthCallback() method with proper null checks and error handling. Add validation middleware for OAuth parameters.',
    gitDiff: `
diff --git a/src/auth/AuthService.js b/src/auth/AuthService.js
index 1234567..abcdefg 100644
--- a/src/auth/AuthService.js
+++ b/src/auth/AuthService.js
@@ -15,7 +15,12 @@ class AuthService {
   }
 
   validateOAuthCallback(params) {
-    const state = params.state;
+    if (!params || !params.state) {
+      throw new AuthError('Invalid OAuth state parameter');
+    }
+    
+    const state = params.state.trim();
+    
     if (state !== this.expectedState) {
       throw new AuthError('OAuth state mismatch');
     }
`,
    author: {
      name: 'Sarah Chen',
      email: 'sarah.chen@company.com',
      avatar: '/avatars/sarah.jpg'
    },
    stakeholders: [
      { name: 'Mike Johnson', role: 'Lead Engineer', email: 'mike.j@company.com' },
      { name: 'Lisa Wang', role: 'Product Manager', email: 'lisa.w@company.com' },
      { name: 'David Kim', role: 'Security Lead', email: 'david.k@company.com' }
    ],
    supportingDocs: [
      { title: 'OAuth Implementation Guide', url: 'https://docs.company.com/oauth', type: 'Documentation' },
      { title: 'Security Best Practices', url: 'https://confluence.company.com/security', type: 'Confluence' },
      { title: 'Error Monitoring Dashboard', url: 'https://monitoring.company.com/auth', type: 'Dashboard' }
    ]
  }
};

export const mockChartData = {
  crashRateByDay: [
    { date: '2024-01-08', crashes: 5 },
    { date: '2024-01-09', crashes: 8 },
    { date: '2024-01-10', crashes: 3 },
    { date: '2024-01-11', crashes: 12 },
    { date: '2024-01-12', crashes: 7 },
    { date: '2024-01-13', crashes: 15 },
    { date: '2024-01-14', crashes: 9 },
    { date: '2024-01-15', crashes: 23 }
  ],
  weeklyTrend: [
    { week: 'Week 1', crashes: 45, resolved: 38 },
    { week: 'Week 2', crashes: 62, resolved: 55 },
    { week: 'Week 3', crashes: 38, resolved: 41 },
    { week: 'Week 4', crashes: 79, resolved: 63 }
  ],
  severityDistribution: [
    { name: 'Critical', value: 15, color: '#ef4444' },
    { name: 'High', value: 28, color: '#f97316' },
    { name: 'Medium', value: 35, color: '#eab308' },
    { name: 'Low', value: 22, color: '#22c55e' }
  ],
  topComponents: [
    { component: 'UserAuth', crashes: 12, percentage: 36.36 },
    { component: 'PaymentProcessor', crashes: 8, percentage: 24.24 },
    { component: 'DataSync', crashes: 6, percentage: 18.18 },
    { component: 'ImageUpload', crashes: 4, percentage: 12.12 },
    { component: 'LocationService', crashes: 3, percentage: 9.09 }
  ]
};