import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Spin } from 'antd';

const RoleRedirect: React.FC = () => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Agents and admins go to the agent dashboard
  if (user?.is_admin || user?.is_support_agent) {
    return <Navigate to="/app/dashboard" replace />;
  }

  // End-users go to the portal
  return <Navigate to="/portal" replace />;
};

export default RoleRedirect;
