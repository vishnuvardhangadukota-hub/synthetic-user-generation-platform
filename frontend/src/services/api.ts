// ============================================================================
// Synthetic User Generation Platform - Typed API Services
// Strictly maps to backend routes in app/api/routes/
// ============================================================================

import { apiClient } from './apiClient';
import type {
  Experiment,
  ExperimentCreatePayload,
  ExperimentUpdatePayload,
  Persona,
  PersonaGenerateResponse,
  PersonaFullMemoryResponse,
  ConversationResponse,
  Survey,
  SurveyCreatePayload,
  QuestionCreatePayload,
  SurveyQuestion,
  SurveyRunResponse,
  SurveyResponsesGrouped,
  InsightReport,
  UsageScoreReport,
  DashboardPayload,
  AnalyticsOverview,
} from '@/types';

export const experimentsApi = {
  list: () => apiClient.get<Experiment[]>('/api/experiments'),
  getById: (id: string) => apiClient.get<Experiment>(`/api/experiments/${id}`),
  create: (data: ExperimentCreatePayload) => apiClient.post<Experiment>('/api/experiments', data),
  update: (id: string, data: ExperimentUpdatePayload) => apiClient.put<Experiment>(`/api/experiments/${id}`, data),
  delete: (id: string) => apiClient.delete<{ message: string; id: string }>(`/api/experiments/${id}`),
};

export const personasApi = {
  generate: (experimentId: string, numberOfPersonas?: number) =>
    apiClient.post<PersonaGenerateResponse>(
      `/api/experiments/${experimentId}/personas/generate`,
      numberOfPersonas ? { number_of_personas: numberOfPersonas } : {}
    ),
  listByExperiment: (experimentId: string) =>
    apiClient.get<Persona[]>(`/api/experiments/${experimentId}/personas`),
  getById: (personaId: string) =>
    apiClient.get<Persona>(`/api/personas/${personaId}`),
  delete: (personaId: string) =>
    apiClient.delete<{ message: string; id: string }>(`/api/personas/${personaId}`),
};

export const conversationsApi = {
  getMemory: (personaId: string) =>
    apiClient.get<PersonaFullMemoryResponse>(`/api/personas/${personaId}/memory`),
  sendMessage: (personaId: string, message: string) =>
    apiClient.post<ConversationResponse>(`/api/personas/${personaId}/conversation`, { message }),
};

export const surveysApi = {
  listByExperiment: (experimentId: string) =>
    apiClient.get<Survey[]>(`/api/experiments/${experimentId}/surveys`),
  create: (experimentId: string, data: SurveyCreatePayload) =>
    apiClient.post<Survey>(`/api/experiments/${experimentId}/surveys`, data),
  addQuestion: (surveyId: string, data: QuestionCreatePayload) =>
    apiClient.post<SurveyQuestion>(`/api/surveys/${surveyId}/questions`, data),
  run: (surveyId: string) =>
    apiClient.post<SurveyRunResponse>(`/api/surveys/${surveyId}/run`),
  getResponsesGrouped: (surveyId: string) =>
    apiClient.get<SurveyResponsesGrouped>(`/api/surveys/${surveyId}/responses`),
};

export const insightsApi = {
  generate: (experimentId: string) =>
    apiClient.post<InsightReport>(`/api/experiments/${experimentId}/insights`),
  getLatest: (experimentId: string) =>
    apiClient.get<InsightReport>(`/api/experiments/${experimentId}/insights`),
};

export const usageScoreApi = {
  calculate: (experimentId: string, customQuestion?: string) =>
    apiClient.post<UsageScoreReport>(
      `/api/experiments/${experimentId}/usage-score`,
      customQuestion ? { custom_question: customQuestion } : {}
    ),
  getLatest: (experimentId: string) =>
    apiClient.get<UsageScoreReport>(`/api/experiments/${experimentId}/usage-score`),
};

export const dashboardApi = {
  getExperimentDashboard: (experimentId: string) =>
    apiClient.get<DashboardPayload>(`/api/experiments/${experimentId}/dashboard`),
  downloadPdf: (experimentId: string) =>
    apiClient.downloadBlob(
      `/api/experiments/${experimentId}/report/pdf`,
      `research_report_${experimentId}.pdf`
    ),
};

export const analyticsApi = {
  getOverview: () =>
    apiClient.get<AnalyticsOverview>('/api/analytics/overview'),
};
