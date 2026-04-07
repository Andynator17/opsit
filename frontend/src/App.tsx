import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, theme as antdTheme } from 'antd';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { TabProvider } from './context/TabContext';
import ProtectedRoute from './components/ProtectedRoute';
import RoleRedirect from './components/RoleRedirect';
import DashboardLayout from './components/DashboardLayout';
import PortalLayout from './components/PortalLayout';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';

// Portal pages
import PortalOverview from './pages/portal/PortalOverview';
import PortalTickets from './pages/portal/PortalTickets';
import PortalTicketDetail from './pages/portal/PortalTicketDetail';
import PortalNewTicket from './pages/portal/PortalNewTicket';
import PortalProfile from './pages/portal/PortalProfile';
import PortalServices from './pages/portal/PortalServices';
import PortalKnowledge from './pages/portal/PortalKnowledge';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Inner component that has access to theme context
const AppContent: React.FC = () => {
  const { isDarkMode } = useTheme();

  // Ant Design theme configuration
  const themeConfig = {
    algorithm: isDarkMode ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    token: {
      colorPrimary: '#667eea',
      borderRadius: 6,
    },
  };

  return (
    <ConfigProvider theme={themeConfig}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* Role-based redirect */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <RoleRedirect />
                </ProtectedRoute>
              }
            />

            {/* Portal routes (any authenticated user) */}
            <Route
              path="/portal"
              element={
                <ProtectedRoute>
                  <PortalLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<PortalOverview />} />
              <Route path="tickets" element={<PortalTickets />} />
              <Route path="tickets/new" element={<PortalNewTicket />} />
              <Route path="tickets/:id" element={<PortalTicketDetail />} />
              <Route path="profile" element={<PortalProfile />} />
              <Route path="services" element={<PortalServices />} />
              <Route path="knowledge" element={<PortalKnowledge />} />
            </Route>

            {/* Agent/Admin routes — tab system handles all content */}
            <Route
              path="/app/*"
              element={
                <ProtectedRoute requireAgent>
                  <TabProvider>
                    <DashboardLayout />
                  </TabProvider>
                </ProtectedRoute>
              }
            />

            {/* Legacy redirects: old /dashboard → /app/dashboard */}
            <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ConfigProvider>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
