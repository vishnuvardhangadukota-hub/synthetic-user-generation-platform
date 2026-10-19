// ============================================================================
// Core Domain Types for Synthetic User Generation Platform
// Strict alignment with Backend OpenAPI / Pydantic models
// ============================================================================

export interface Experiment {
  id: string;
  name: string;
  product_name: string;
  product_description: string;
  target_audience: string;
  research_objectives: string[];
  number_of_personas: number;
  created_at: string;
  updated_at: string;
}

export interface ExperimentCreatePayload {
  name: string;
  product_name: string;
  product_description: string;
  target_audience: string;
  research_objectives: string[];
  number_of_personas?: number;
}

export interface ExperimentUpdatePayload {
  name?: string;
  product_name?: string;
  product_description?: string;
  target_audience?: string;
  research_objectives?: string[];
  number_of_personas?: number;
}

export interface Persona {
  id: string;
  experiment_id: string;
  name: string;
  age: number;
  occupation: string;
  location: string;
  demographics: Record<string, any>;
  personality_traits: string[];
  behavioral_patterns: string[];
  psychological_profile: Record<string, any>;
  preferences: Record<string, any>;
  opinions: Record<string, any>;
  memory_summary: string;
  is_synthetic_test_data: boolean;
  created_at: string;
  updated_at: string;
}

export interface PersonaGenerateRequest {
  number_of_personas?: number;
}

export interface PersonaGenerateResponse {
  experiment_id: string;
  personas: Persona[];
}

export interface SurveyQuestion {
  id: string;
  survey_id: string;
  question_text: string;
  question_type: 'rating' | 'yes_no' | 'short_answer' | 'opinion' | 'open_ended';
  options?: string[];
  order: number;
  created_at: string;
}

export interface QuestionCreatePayload {
  question_text: string;
  question_type: 'rating' | 'yes_no' | 'short_answer' | 'opinion' | 'open_ended';
  options?: string[];
  order?: number;
}

export interface Survey {
  id: string;
  experiment_id: string;
  title: string;
  description?: string;
  status: string; // "draft", "completed", etc.
  questions: SurveyQuestion[];
  created_at: string;
  updated_at: string;
}

export interface SurveyCreatePayload {
  title: string;
  description?: string;
}

export interface SurveyResponseItem {
  id: string;
  experiment_id: string;
  survey_id: string;
  question_id: string;
  persona_id: string;
  persona_name?: string;
  answer: string;
  rating_score?: number | null;
  reasoning?: string;
  created_at: string;
}

export interface SurveyRunResponse {
  survey_id: string;
  total_personas: number;
  total_responses_generated: number;
  responses: SurveyResponseItem[];
}

export interface QuestionGroupedResponses {
  question_id: string;
  question_text: string;
  question_type: string;
  responses: SurveyResponseItem[];
}

export interface SurveyResponsesGrouped {
  survey_id: string;
  experiment_id: string;
  grouped_by_question: QuestionGroupedResponses[];
}

export interface ConversationHistoryItem {
  id: string;
  user_message: string;
  persona_response: string;
  created_at: string;
}

export interface PersonaFullMemoryResponse {
  persona_id: string;
  core_attributes: Record<string, any>;
  behavioral_memories: Record<string, any>[];
  opinions: Record<string, any>[];
  conversation_history: ConversationHistoryItem[];
  memory_summary: string;
}

export interface ConversationResponse {
  persona_id: string;
  response: string;
  memory_updated: boolean;
}

export interface SentimentDistribution {
  positive_percentage?: number;
  neutral_percentage?: number;
  negative_percentage?: number;
  counts?: {
    positive?: number;
    neutral?: number;
    negative?: number;
  };
}

export interface SupportingReference {
  reference_id: string;
  source_type: 'survey' | 'interview';
  persona_id: string;
  persona_name: string;
  content_snippet: string;
}

export interface InsightReport {
  id: string;
  experiment_id: string;
  recurring_themes: Array<{
    theme: string;
    description: string;
    percentage?: number;
    supporting_quotes?: string[];
  }>;
  sentiment_distribution: SentimentDistribution;
  agreement_patterns: string[];
  disagreements: string[];
  behavioral_trends: string[];
  supporting_references: SupportingReference[];
  limitations: string;
  created_at: string;
}

export interface UsageScorePersonaItem {
  persona_id: string;
  persona_name: string;
  occupation: string;
  age: number;
  price_sensitivity?: string;
  would_use: boolean;
  score: number; // 1-10
  category: string; // 'Would Use', 'Unlikely', 'Maybe'
  reasoning: string;
}

export interface UsageScoreReport {
  id: string;
  experiment_id: string;
  overall_score: number;
  would_use_percentage: number;
  segmentation_breakdown: {
    by_age_group?: Record<string, { average_score: number; would_use_pct: number; count: number }>;
    by_occupation?: Record<string, { average_score: number; would_use_pct: number; count: number }>;
    [key: string]: any;
  };
  persona_scores: UsageScorePersonaItem[];
  calculation_method: string;
  limitations: string;
  created_at: string;
}

export interface DashboardSummaryCards {
  total_personas: number;
  total_responses: number;
  survey_responses: number;
  interview_responses: number;
  themes_discovered: number;
  positive_sentiment_pct: number | null;
  validation_score: number | null;
  experiment_status: string;
}

export interface DashboardPayload {
  experiment: {
    id: string;
    name: string;
    product_name: string;
    product_description: string;
    target_audience: string;
    research_objectives: string[];
    number_of_personas: number;
    created_at: string;
  };
  summary_cards: DashboardSummaryCards;
  theme_clusters: Array<{
    theme: string;
    description: string;
    percentage?: number;
    representative_quotes?: string[];
  }>;
  sentiment_breakdown: {
    positive?: { count: number; percentage: number };
    neutral?: { count: number; percentage: number };
    negative?: { count: number; percentage: number };
    total?: number;
  };
  key_quotes: Array<{
    quote: string;
    persona_name: string;
    source: string;
  }>;
  validation_score: {
    available: boolean;
    score?: number | null;
    would_use_percentage?: number | null;
    rating?: string;
  };
  surveys: Array<{
    id: string;
    title: string;
    status: string;
  }>;
  has_insight_report: boolean;
  has_usage_score: boolean;
}

export interface AnalyticsOverview {
  total_experiments: number;
  total_personas: number;
  total_surveys: number;
  total_responses: number;
  survey_responses: number;
  interview_responses: number;
  total_insights: number;
  total_usage_scores: number;
  average_usage_score: number | null;
  average_would_use_percentage: number | null;
}
