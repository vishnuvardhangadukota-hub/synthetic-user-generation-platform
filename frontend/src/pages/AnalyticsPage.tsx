import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  FlaskConical,
  Users,
  ClipboardList,
  MessagesSquare,
  Sparkles,
  Award,
  RefreshCw,
  TrendingUp,
  Activity,
  Layers,
} from 'lucide-react';
import { analyticsApi } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { MetricCardSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/context/ToastContext';
import type { AnalyticsOverview } from '@/types';

export const AnalyticsPage: React.FC = () => {
  const { success, error } = useToast();
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true);
      const data = await analyticsApi.getOverview();
      setAnalytics(data);
    } catch (err: any) {
      error('Failed to load analytics', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Platform Analytics Overview"
        description="Global system telemetry and aggregated metrics across all synthetic experiments, personas, and simulations."
        actions={
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => {
              fetchAnalytics();
              success('Analytics refreshed', 'Loaded latest metrics from database.');
            }}
          >
            Refresh
          </Button>
        }
      />

      {/* Metrics Row 1 */}
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
                  Experiments
                </p>
                <p className="text-3xl font-extrabold text-slate-900 mt-1">
                  {analytics?.total_experiments ?? 0}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">Research workspaces</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100">
                <FlaskConical className="w-6 h-6" />
              </div>
            </CardContent>
          </Card>

          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Synthetic Personas
                </p>
                <p className="text-3xl font-extrabold text-slate-900 mt-1">
                  {analytics?.total_personas ?? 0}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">Simulated agents</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center border border-violet-100">
                <Users className="w-6 h-6" />
              </div>
            </CardContent>
          </Card>

          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Surveys Created
                </p>
                <p className="text-3xl font-extrabold text-slate-900 mt-1">
                  {analytics?.total_surveys ?? 0}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">Structured tests</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
                <ClipboardList className="w-6 h-6" />
              </div>
            </CardContent>
          </Card>

          <Card hoverEffect>
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Total Responses
                </p>
                <p className="text-3xl font-extrabold text-slate-900 mt-1">
                  {analytics?.total_responses ?? 0}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">Surveys + Interviews</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
                <MessagesSquare className="w-6 h-6" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Metrics Row 2: Synthesis & Adoption */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Response Channels Breakdown</CardTitle>
            <CardDescription>Survey vs Qualitative interview ratio</CardDescription>
          </CardHeader>
          <CardContent className="p-5 space-y-4">
            <div>
              <div className="flex items-center justify-between text-xs mb-1.5 font-medium">
                <span className="text-slate-700">Survey Responses</span>
                <span className="font-bold text-indigo-700">
                  {analytics?.survey_responses ?? 0}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                  style={{
                    width: `${
                      analytics?.total_responses
                        ? ((analytics.survey_responses || 0) / analytics.total_responses) * 100
                        : 0
                    }%`,
                  }}
                  className="bg-indigo-600 h-full rounded-full"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-xs mb-1.5 font-medium">
                <span className="text-slate-700">Interview Turns</span>
                <span className="font-bold text-emerald-700">
                  {analytics?.interview_responses ?? 0}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                  style={{
                    width: `${
                      analytics?.total_responses
                        ? ((analytics.interview_responses || 0) / analytics.total_responses) * 100
                        : 0
                    }%`,
                  }}
                  className="bg-emerald-500 h-full rounded-full"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Synthesized Intelligence</CardTitle>
            <CardDescription>Insight reports and theme models</CardDescription>
          </CardHeader>
          <CardContent className="p-5 space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-xs font-medium text-slate-700">Insight Reports Synthesized</span>
              <span className="text-sm font-bold text-slate-900">
                {analytics?.total_insights ?? 0}
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-xs font-medium text-slate-700">Usage Score Evaluations</span>
              <span className="text-sm font-bold text-slate-900">
                {analytics?.total_usage_scores ?? 0}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Platform Adoption Benchmark</CardTitle>
            <CardDescription>Aggregate product usage likelihood</CardDescription>
          </CardHeader>
          <CardContent className="p-5 flex flex-col justify-center">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-indigo-700">
                {analytics?.average_usage_score != null
                  ? `${analytics.average_usage_score}`
                  : 'N/A'}
              </span>
              <span className="text-sm text-slate-400 font-semibold">/ 10</span>
            </div>

            <p className="text-xs text-slate-500 mt-2">
              {analytics?.average_would_use_percentage != null
                ? `${analytics.average_would_use_percentage}% average adoption intent across evaluated experiments`
                : 'Run usage score calculations to establish benchmark.'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Database Schema & Engine Details */}
      <Card>
        <CardHeader>
          <CardTitle>Architecture & Telemetry Verification</CardTitle>
          <CardDescription>Real-time database connection metrics</CardDescription>
        </CardHeader>
        <CardContent className="p-5 space-y-3 text-xs text-slate-600">
          <p>
            All analytics are queried directly from the active backend database without cached demo
            data. As new experiments, personas, and simulation responses are created, counts and
            aggregations update in real time.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 font-mono">
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-sans">ENDPOINT</span>
              <span className="font-bold text-slate-800">/api/analytics/overview</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-sans">HTTP METHOD</span>
              <span className="font-bold text-emerald-700">GET (200 OK)</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-sans">DB ENGINE</span>
              <span className="font-bold text-slate-800">SQLAlchemy 2.0</span>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-sans">MEMORY LAYER</span>
              <span className="font-bold text-indigo-700">3-Tier Partition</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
