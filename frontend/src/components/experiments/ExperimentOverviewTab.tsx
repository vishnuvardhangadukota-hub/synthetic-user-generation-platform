import React from 'react';
import {
  Users,
  MessagesSquare,
  Sparkles,
  TrendingUp,
  Award,
  CheckCircle2,
  Quote,
  Target,
  FileQuestion,
  HelpCircle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { DashboardPayload } from '@/types';

interface ExperimentOverviewTabProps {
  dashboard: DashboardPayload | null;
  onNavigateTab: (tab: string) => void;
}

export const ExperimentOverviewTab: React.FC<ExperimentOverviewTabProps> = ({
  dashboard,
  onNavigateTab,
}) => {
  if (!dashboard) return null;

  const cards = dashboard.summary_cards;
  const sentiment = dashboard.sentiment_breakdown;
  const themes = dashboard.theme_clusters;
  const quotes = dashboard.key_quotes;
  const validation = dashboard.validation_score;

  return (
    <div className="space-y-6">
      {/* Summary Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Personas
            </span>
            <span className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.total_personas}</p>
          <button
            onClick={() => onNavigateTab('personas')}
            className="text-xs text-indigo-600 hover:text-indigo-800 font-medium mt-1 inline-flex items-center gap-1"
          >
            Manage Cohort &rarr;
          </button>
        </div>

        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Responses
            </span>
            <span className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <MessagesSquare className="w-4 h-4" />
            </span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.total_responses}</p>
          <p className="text-xs text-slate-500 mt-1">
            {cards.survey_responses} survey &bull; {cards.interview_responses} interview
          </p>
        </div>

        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Themes Discovered
            </span>
            <span className="w-8 h-8 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">{cards.themes_discovered}</p>
          <button
            onClick={() => onNavigateTab('insights')}
            className="text-xs text-violet-600 hover:text-violet-800 font-medium mt-1 inline-flex items-center gap-1"
          >
            View Insights &rarr;
          </button>
        </div>

        <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Validation Score
            </span>
            <span className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Award className="w-4 h-4" />
            </span>
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {cards.validation_score != null ? `${cards.validation_score}%` : 'N/A'}
          </p>
          <button
            onClick={() => onNavigateTab('usage-score')}
            className="text-xs text-amber-600 hover:text-amber-800 font-medium mt-1 inline-flex items-center gap-1"
          >
            Usage Scoring &rarr;
          </button>
        </div>
      </div>

      {/* Sentiment & Status Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment breakdown */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Sentiment Breakdown</CardTitle>
            <CardDescription>Synthesized qualitative tone</CardDescription>
          </CardHeader>
          <CardContent className="p-5 space-y-4">
            {sentiment && (sentiment.total ?? 0) > 0 ? (
              <>
                <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex">
                  <div
                    style={{ width: `${sentiment.positive?.percentage || 0}%` }}
                    className="bg-emerald-500 transition-all duration-500"
                    title={`Positive: ${sentiment.positive?.percentage}%`}
                  />
                  <div
                    style={{ width: `${sentiment.neutral?.percentage || 0}%` }}
                    className="bg-slate-400 transition-all duration-500"
                    title={`Neutral: ${sentiment.neutral?.percentage}%`}
                  />
                  <div
                    style={{ width: `${sentiment.negative?.percentage || 0}%` }}
                    className="bg-rose-500 transition-all duration-500"
                    title={`Negative: ${sentiment.negative?.percentage}%`}
                  />
                </div>

                <div className="space-y-2.5 pt-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2 text-slate-700 font-medium">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      Positive
                    </span>
                    <span className="font-semibold text-slate-900">
                      {sentiment.positive?.percentage}% ({sentiment.positive?.count})
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2 text-slate-700 font-medium">
                      <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
                      Neutral
                    </span>
                    <span className="font-semibold text-slate-900">
                      {sentiment.neutral?.percentage}% ({sentiment.neutral?.count})
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-2 text-slate-700 font-medium">
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                      Negative
                    </span>
                    <span className="font-semibold text-slate-900">
                      {sentiment.negative?.percentage}% ({sentiment.negative?.count})
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="py-6 text-center text-xs text-slate-400">
                Run surveys or interviews and synthesize insights to calculate sentiment.
              </div>
            )}
          </CardContent>
        </Card>

        {/* Status & Validation Meter */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between w-full">
              <div>
                <CardTitle>Research Status & Validation</CardTitle>
                <CardDescription>Experiment progress checklist</CardDescription>
              </div>
              <Badge
                variant={
                  cards.experiment_status === 'Analysis Complete'
                    ? 'success'
                    : cards.experiment_status === 'Responses Collected'
                    ? 'info'
                    : cards.experiment_status === 'Personas Generated'
                    ? 'purple'
                    : 'default'
                }
                size="md"
              >
                {cards.experiment_status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-5">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/60 flex items-start gap-3">
                <CheckCircle2
                  className={`w-5 h-5 shrink-0 ${
                    cards.total_personas > 0 ? 'text-emerald-500' : 'text-slate-300'
                  }`}
                />
                <div>
                  <p className="text-xs font-semibold text-slate-900">Personas</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {cards.total_personas > 0
                      ? `${cards.total_personas} generated`
                      : 'None generated'}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/60 flex items-start gap-3">
                <CheckCircle2
                  className={`w-5 h-5 shrink-0 ${
                    cards.total_responses > 0 ? 'text-emerald-500' : 'text-slate-300'
                  }`}
                />
                <div>
                  <p className="text-xs font-semibold text-slate-900">Simulations</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {cards.total_responses > 0
                      ? `${cards.total_responses} responses`
                      : 'No responses yet'}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/60 flex items-start gap-3">
                <CheckCircle2
                  className={`w-5 h-5 shrink-0 ${
                    dashboard.has_insight_report ? 'text-emerald-500' : 'text-slate-300'
                  }`}
                />
                <div>
                  <p className="text-xs font-semibold text-slate-900">Synthesis</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {dashboard.has_insight_report ? 'Report generated' : 'Pending insights'}
                  </p>
                </div>
              </div>
            </div>

            {validation.available && (
              <div className="mt-4 p-4 rounded-xl bg-amber-50/50 border border-amber-200/60 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-amber-900">
                    Product Validation Score
                  </p>
                  <p className="text-xs text-amber-700 mt-0.5">
                    Adoption Intent: {validation.would_use_percentage}% personas likely to use
                  </p>
                </div>
                <div className="text-xl font-bold text-amber-900">
                  {validation.score}/100
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Theme Clusters & Key Quotes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Theme Clusters */}
        <Card>
          <CardHeader>
            <CardTitle>Discovered Theme Clusters</CardTitle>
            <CardDescription>Qualitative clusters extracted from cohort responses</CardDescription>
          </CardHeader>
          <CardContent className="p-5">
            {themes && themes.length > 0 ? (
              <div className="space-y-3.5">
                {themes.map((t, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl border border-slate-150 bg-slate-50/50 hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <h4 className="text-xs font-semibold text-slate-900">{t.theme}</h4>
                      {t.percentage != null && (
                        <Badge variant="purple" size="sm">
                          {t.percentage}% prevalence
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{t.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-slate-400">
                No themes extracted yet. Collect survey or conversation responses, then generate
                insights.
              </div>
            )}
          </CardContent>
        </Card>

        {/* Key Quotes */}
        <Card>
          <CardHeader>
            <CardTitle>Representative Persona Quotes</CardTitle>
            <CardDescription>Direct voices from simulation sessions</CardDescription>
          </CardHeader>
          <CardContent className="p-5">
            {quotes && quotes.length > 0 ? (
              <div className="space-y-3.5">
                {quotes.map((q, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl border border-slate-100 bg-white shadow-xs relative pl-8"
                  >
                    <Quote className="w-4 h-4 text-indigo-400 absolute left-2.5 top-3.5" />
                    <p className="text-xs italic text-slate-700 leading-relaxed mb-1.5">
                      "{q.quote}"
                    </p>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium">
                      <span className="text-slate-800 font-semibold">{q.persona_name}</span>
                      <span className="uppercase text-[10px] tracking-wider text-slate-400">
                        {q.source}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-slate-400">
                No quotes collected yet. Run surveys or interviews to populate persona voices.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
