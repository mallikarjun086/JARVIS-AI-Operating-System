import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { AIChatPage } from './pages/AIChat';
import { MemoryConsolePage } from './pages/MemoryConsole';
import { DatasetTrainerConsolePage } from './pages/DatasetTrainerConsole';
import { PlannerConsolePage } from './pages/PlannerConsole';
import { ToolConsolePage } from './pages/ToolConsole';
import { AutomationConsolePage } from './pages/AutomationConsole';
import { BrowserConsolePage } from './pages/BrowserConsole';
import { SWEConsolePage } from './pages/SWEConsole';
import { MultiAgentConsolePage } from './pages/MultiAgentConsole';
import { VisionConsolePage } from './pages/VisionConsole';
import { VoiceConsolePage } from './pages/VoiceConsole';
import { WorkflowConsolePage } from './pages/WorkflowConsole';
import { SecurityConsolePage } from './pages/SecurityConsole';
import { SettingsPage } from './pages/Settings';
import { AuditLogsPage } from './pages/AuditLogs';

const LayoutWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <div className="app-container">
      <Sidebar isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />
      <div className="main-content">
        <Navbar onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)} />
        <main className="page-body">{children}</main>
      </div>
    </div>
  );
};


export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute />}>
            <Route
              path="/dashboard"
              element={
                <LayoutWrapper>
                  <Dashboard />
                </LayoutWrapper>
              }
            />
            <Route
              path="/ai-console"
              element={
                <LayoutWrapper>
                  <AIChatPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/security-console"
              element={
                <LayoutWrapper>
                  <SecurityConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/workflow-console"
              element={
                <LayoutWrapper>
                  <WorkflowConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/voice-console"
              element={
                <LayoutWrapper>
                  <VoiceConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/multi-agent-console"
              element={
                <LayoutWrapper>
                  <MultiAgentConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/vision-console"
              element={
                <LayoutWrapper>
                  <VisionConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/planner-console"
              element={
                <LayoutWrapper>
                  <PlannerConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/swe-console"
              element={
                <LayoutWrapper>
                  <SWEConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/browser-console"
              element={
                <LayoutWrapper>
                  <BrowserConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/automation-console"
              element={
                <LayoutWrapper>
                  <AutomationConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/tool-console"
              element={
                <LayoutWrapper>
                  <ToolConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/memory-console"
              element={
                <LayoutWrapper>
                  <MemoryConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/dataset-trainer"
              element={
                <LayoutWrapper>
                  <DatasetTrainerConsolePage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/audit-logs"
              element={
                <LayoutWrapper>
                  <AuditLogsPage />
                </LayoutWrapper>
              }
            />
            <Route
              path="/settings"
              element={
                <LayoutWrapper>
                  <SettingsPage />
                </LayoutWrapper>
              }
            />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
