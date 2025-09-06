import { useEffect, useRef } from 'react';
import { useToast } from '@/hooks/use-toast';

interface CrashAlert {
  id: string;
  type: 'crash_detected' | 'crash_resolved' | 'critical_crash';
  message: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  repositoryName: string;
  timestamp: string;
}

export function useWebSocketNotifications() {
  const { toast } = useToast();
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Simulate WebSocket connection for demo
    // In production, this would connect to your actual WebSocket server
    const simulateWebSocket = () => {
      const mockAlerts: CrashAlert[] = [
        {
          id: 'alert-1',
          type: 'crash_detected',
          message: 'Critical crash detected in UserAuth module',
          severity: 'Critical',
          repositoryName: 'web-frontend',
          timestamp: new Date().toISOString()
        },
        {
          id: 'alert-2', 
          type: 'crash_detected',
          message: 'High severity crash in PaymentProcessor',
          severity: 'High',
          repositoryName: 'web-frontend',
          timestamp: new Date().toISOString()
        },
        {
          id: 'alert-3',
          type: 'crash_resolved',
          message: 'DataSync module crash has been resolved',
          severity: 'Medium',
          repositoryName: 'api-service',
          timestamp: new Date().toISOString()
        }
      ];

      let alertIndex = 0;
      const interval = setInterval(() => {
        if (alertIndex < mockAlerts.length) {
          const alert = mockAlerts[alertIndex];
          handleCrashAlert(alert);
          alertIndex++;
        } else {
          clearInterval(interval);
        }
      }, 10000); // Send an alert every 10 seconds

      return () => clearInterval(interval);
    };

    const cleanup = simulateWebSocket();

    // Cleanup on unmount
    return () => {
      cleanup();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleCrashAlert = (alert: CrashAlert) => {
    const getVariant = () => {
      if (alert.type === 'crash_resolved') return 'default';
      if (alert.severity === 'Critical') return 'destructive';
      return 'default';
    };

    const getTitle = () => {
      switch (alert.type) {
        case 'crash_detected':
          return `${alert.severity} Crash Detected`;
        case 'crash_resolved':
          return 'Crash Resolved';
        case 'critical_crash':
          return 'Critical System Failure';
        default:
          return 'Crash Alert';
      }
    };

    toast({
      title: getTitle(),
      description: `${alert.message} in ${alert.repositoryName}`,
      variant: getVariant(),
      duration: alert.severity === 'Critical' ? 0 : 5000, // Critical alerts stay until dismissed
    });
  };

  const connectWebSocket = (url: string) => {
    try {
      wsRef.current = new WebSocket(url);
      
      wsRef.current.onmessage = (event) => {
        try {
          const alert: CrashAlert = JSON.parse(event.data);
          handleCrashAlert(alert);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket connection closed');
        // Implement reconnection logic here if needed
      };
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
    }
  };

  return {
    connectWebSocket,
    disconnect: () => wsRef.current?.close(),
  };
}