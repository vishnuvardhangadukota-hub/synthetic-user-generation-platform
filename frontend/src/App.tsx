import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from '@/context/ToastContext';
import { AppShell } from '@/components/layout/AppShell';

// Pages
import { DashboardPage } from '@/pages/DashboardPage';
import { ExperimentsPage } from '@/pages/ExperimentsPage';
import { ExperimentDetailPage } from '@/pages/ExperimentDetailPage';
import { PersonasPage } from '@/pages/PersonasPage';
import { SurveysPage } from '@/pages/SurveysPage';
import { InterviewsPage } from '@/pages/InterviewsPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

export function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<DashboardPage />} />
            <Route path="experiments" element={<ExperimentsPage />} />
            <Route path="experiments/:id" element={<ExperimentDetailPage />} />
            <Route path="personas" element={<PersonasPage />} />
            <Route path="surveys" element={<SurveysPage />} />
            <Route path="interviews" element={<InterviewsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;
