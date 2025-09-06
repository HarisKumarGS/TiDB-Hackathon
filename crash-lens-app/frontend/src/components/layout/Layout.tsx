import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useWebSocketNotifications } from '@/hooks/useWebSocketNotifications';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  // Initialize WebSocket notifications
  useWebSocketNotifications();

  return (
    <div className="flex h-screen bg-background overflow-hidden circuit-pattern">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* <Header /> */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}