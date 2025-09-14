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
    // Connect to the real WebSocket server
    const connectToWebSocket = () => {
      const wsUrl = 'ws://localhost:8000/api/v1/ws';
      
      try {
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onopen = () => {
          console.log('WebSocket connected to Realtime Updates');
        };
        
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
        
        wsRef.current.onclose = (event) => {
          console.log('WebSocket connection closed:', event.code, event.reason);
          // Implement reconnection logic
          setTimeout(() => {
            if (wsRef.current?.readyState === WebSocket.CLOSED) {
              connectToWebSocket();
            }
          }, 5000);
        };
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
      }
    };

    connectToWebSocket();

    // Cleanup on unmount
    return () => {
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
          return 'Notification';
      }
    };

    toast({
      title: getTitle(),
      description: `${alert.message}`,
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
