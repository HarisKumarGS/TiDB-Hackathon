import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { useWebSocketNotifications } from "@/hooks/useWebSocketNotifications";
import Dashboard from "./pages/Dashboard";
import CrashList from "./pages/CrashList";
import CrashDetail from "./pages/CrashDetail";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const WebSocketProvider = ({ children }: { children: React.ReactNode }) => {
  useWebSocketNotifications();
  return <>{children}</>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <WebSocketProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/crashes" element={<CrashList />} />
              <Route path="/crashes/:id" element={<CrashDetail />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </WebSocketProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
