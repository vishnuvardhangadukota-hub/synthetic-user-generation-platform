import React, { useEffect, useState } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import {
  FlaskConical,
  Users,
  ClipboardList,
  MessagesSquare,
  Sparkles,
  ArrowRight,
  TrendingUp,
  BarChart2,
  CheckCircle2,
  FileText,
  Clock,
  Layers,
  Award,
} from 'lucide-react';
import { experimentsApi, analyticsApi } from '@/services/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { MetricCardSkeleton, TableSkeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import type { Experiment, AnalyticsOverview } from '@/types';

export const DashboardPage: React.FC = () => {
  const { openNewExperiment } = useOutletContext<{ openNewExperiment: () => void }>();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [expList, overview] = await Promise.all([
          experimentsApi.list().catch(() => [] as Experiment[]),
          analyticsApi.getOverview().catch(() => null),
        ]);
        if (mounted) {
          setExperiments(expList);
          setAnalytics(overview);
        }
      } finally {
        if (mounted) setIsLoading(false);
      }
    };
    fetchData();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 shadow-md">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-white/10 text-indigo-200 text-xs font-medium mb-3 backdrop-blur-xs border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
            <span>AI-Powered Synthetic Cohort Simulation</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
            Research Command Center
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed mb-6">
            Generate diverse synthetic user cohorts, run automated multi-mode surveys, interview
            personas with memory consistency, and extract qualitative insights for your product.
          </p>
          <div className="flex items-center gap-3 flex-wrap">
            <Button
              variant="primary"
              size="md"
              leftIcon={<FlaskConical className="w-4 h-4" />}
              onClick={openNewExperiment}
              className="bg-indigo-500 hover:bg-indigo-400 text-white shadow-md font-semibold"
            >
              Start New Experiment
            </Button>
            <Link to="/experiments">
              <Button
                variant="outline"
                size="md"
                className="bg-white/10 hover:bg-white/20 text-white border-white/20"
              >
                View Experiments Directory
              </Button>
            </Link>
          </div>
        </div>

        {/* Subtle decorative glow */}
        <div className="absolute -right-10 -bottom-10 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Metrics Row */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCardSkeleton />
          <MetricCardSkeleton />
          <MetricCardSkeleton />
          <MetricCardSkeleton />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Total Experiments
                </p>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {analytics?.total_experiments ?? experiments.length}
                </p>
                <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                  <span>Product workspaces</span>
                </p>
              </div>
              <div className="w-11 h-11 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100">
                <FlaskConical className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>

          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Synthetic Personas
                </p>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {analytics?.total_personas ?? 0}
                </p>
                <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                  <span>Active simulation agents</span>
                </p>
              </div>
              <div className="w-11 h-11 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center border border-violet-100">
                <Users className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>

          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Total Responses
                </p>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {analytics?.total_responses ?? 0}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  <span className="text-indigo-600 font-medium">
                    {analytics?.survey_responses ?? 0}
                  </span>{' '}
                  surveys &bull;{' '}
                  <span className="text-indigo-600 font-medium">
                    {analytics?.interview_responses ?? 0}
                  </span>{' '}
                  interviews
                </p>
              </div>
              <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
                <MessagesSquare className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>

          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Average Usage Score
                </p>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  {analytics?.average_usage_score != null
                    ? `${analytics.average_usage_score} / 10`
                    : 'N/A'}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  {analytics?.average_would_use_percentage != null
                    ? `${analytics.average_would_use_percentage}% adoption intent`
                    : 'Awaiting score runs'}
                </p>
              </div>
              <div className="w-11 h-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
                <Award className="w-5 h-5" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Section: Recent Experiments & Quick Workflow */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Experiments (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>Recent Research Experiments</CardTitle>
                <CardDescription>
                  Active research workspaces and persona simulations
                </CardDescription>
              </div>
              <Link to="/experiments">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  View All
                </Button>
              </Link>
            </CardHeader>

            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-5">
                  <TableSkeleton rows={3} />
                </div>
              ) : experiments.length === 0 ? (
                <div className="p-6">
                  <EmptyState
                    icon={<FlaskConical className="w-6 h-6 text-indigo-600" />}
                    title="No experiments found"
                    description="Create your first research experiment to generate synthetic personas and run surveys."
                    actionLabel="Create Experiment"
                    onAction={openNewExperiment}
                  />
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {experiments.slice(0, 5).map((exp) => (
                    <div
                      key={exp.id}
                      className="p-5 flex items-center justify-between hover:bg-slate-50/70 transition-colors group"
                    >
                      <div className="min-w-0 pr-4">
                        <div className="flex items-center gap-2 mb-1">
                          <Link
                            to={`/experiments/${exp.id}`}
                            className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors text-sm truncate block"
                          >
                            {exp.name}
                          </Link>
                          <Badge variant="outline" size="sm">
                            {exp.product_name}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-500 line-clamp-1">
                          Audience: {exp.target_audience}
                        </p>
                        <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-2">
                          <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {exp.number_of_personas} personas
                          </span>
                          <span>&bull;</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(exp.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <Link to={`/experiments/${exp.id}`}>
                          <Button variant="outline" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                            Open
                          </Button>
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Cards: Workflow Guide & Quick Actions */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Research Workflow</CardTitle>
              <CardDescription>Step-by-step synthetic simulation</CardDescription>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  1
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-900">Define Experiment</h4>
                  <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                    Set product description, audience criteria, and research questions.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  2
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-900">Generate Personas</h4>
                  <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                    AI agent generates diverse synthetic personas with demographics and psychographics.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  3
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-900">Run Surveys & Interviews</h4>
                  <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                    Simulate rating/yes-no surveys and conduct 1-on-1 interview conversations.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                  4
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-900">Insights & PDF Reports</h4>
                  <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                    Synthesize themes, sentiment, usage adoption scores, and download publication-ready PDFs.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Platform Highlights</CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-3">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-700">Memory Consistency</span>
                <Badge variant="success" size="sm">Active</Badge>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-700">Insight Extraction Agent</span>
                <Badge variant="info" size="sm">Deterministic/LLM</Badge>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-700">PDF Report Generator</span>
                <Badge variant="purple" size="sm">ReportLab 2.0</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
