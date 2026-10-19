import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Quote,
  Layers,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import { insightsApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type { InsightReport } from '@/types';

interface ExperimentInsightsTabProps {
  experimentId: string;
  hasResponses: boolean;
  onRefreshParent: () => void;
}

export const ExperimentInsightsTab: React.FC<ExperimentInsightsTabProps> = ({
  experimentId,
  hasResponses,
  onRefreshParent,
}) => {
  const { success, error } = useToast();

  const [insight, setInsight] = useState<InsightReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchInsight = async () => {
    try {
      setIsLoading(true);
      const data = await insightsApi.getLatest(experimentId);
      setInsight(data);
    } catch {
      setInsight(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInsight();
  }, [experimentId]);

  const handleGenerateInsights = async () => {
    if (!hasResponses) {
      error(
        'No responses available',
        'Please run at least one survey or interview before extracting insights.'
      );
      return;
    }

    try {
      setIsGenerating(true);
      const res = await insightsApi.generate(experimentId);
      setInsight(res);
      success('Insights generated', 'Qualitative insight report extracted successfully.');
      onRefreshParent();
    } catch (err: any) {
      error('Failed to generate insights', err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Trigger */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Qualitative Insight Synthesis</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            AI synthesis agent analyzes survey responses & interviews to extract recurring patterns.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          leftIcon={<Sparkles className="w-4 h-4" />}
          onClick={handleGenerateInsights}
          isLoading={isGenerating}
          disabled={!hasResponses}
        >
          {insight ? 'Regenerate Insights' : 'Synthesize Insights'}
        </Button>
      </div>

      {!insight ? (
        <EmptyState
          icon={<Sparkles className="w-6 h-6 text-indigo-600" />}
          title="No insights synthesized yet"
          description={
            hasResponses
              ? 'Click "Synthesize Insights" above to run the qualitative synthesis agent over collected responses.'
              : 'Execute surveys or hold interviews with personas first to generate raw response data for insight extraction.'
          }
          actionLabel={hasResponses ? 'Synthesize Insights' : undefined}
          onAction={hasResponses ? handleGenerateInsights : undefined}
        />
      ) : (
        <div className="space-y-6">
          {/* Sentiment & Agreement Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Sentiment distribution card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Sentiment Distribution</CardTitle>
                <CardDescription>Overall emotional tone</CardDescription>
              </CardHeader>
              <CardContent className="p-5 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 font-medium">Positive</span>
                  <span className="font-bold text-emerald-600">
                    {insight.sentiment_distribution?.positive_percentage ?? 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    style={{
                      width: `${insight.sentiment_distribution?.positive_percentage ?? 0}%`,
                    }}
                    className="bg-emerald-500 h-full rounded-full"
                  />
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-slate-600 font-medium">Neutral</span>
                  <span className="font-bold text-slate-600">
                    {insight.sentiment_distribution?.neutral_percentage ?? 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    style={{
                      width: `${insight.sentiment_distribution?.neutral_percentage ?? 0}%`,
                    }}
                    className="bg-slate-400 h-full rounded-full"
                  />
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-slate-600 font-medium">Negative</span>
                  <span className="font-bold text-rose-600">
                    {insight.sentiment_distribution?.negative_percentage ?? 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    style={{
                      width: `${insight.sentiment_distribution?.negative_percentage ?? 0}%`,
                    }}
                    className="bg-rose-500 h-full rounded-full"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Agreement Patterns */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Consensus & Agreements</CardTitle>
                <CardDescription>High-confidence patterns across personas</CardDescription>
              </CardHeader>
              <CardContent className="p-5">
                {insight.agreement_patterns?.length > 0 ? (
                  <ul className="space-y-2 text-xs text-slate-700">
                    {insight.agreement_patterns.map((p, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">No clear consensus identified.</p>
                )}
              </CardContent>
            </Card>

            {/* Disagreements */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Friction & Polarizations</CardTitle>
                <CardDescription>Areas where persona opinions diverge</CardDescription>
              </CardHeader>
              <CardContent className="p-5">
                {insight.disagreements?.length > 0 ? (
                  <ul className="space-y-2 text-xs text-slate-700">
                    {insight.disagreements.map((d, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">No major friction points observed.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Recurring Themes Detail */}
          <Card>
            <CardHeader>
              <CardTitle>Recurring Research Themes</CardTitle>
              <CardDescription>
                Core themes synthesized from persona surveys and interviews
              </CardDescription>
            </CardHeader>
            <CardContent className="p-5">
              <div className="space-y-4">
                {insight.recurring_themes?.map((t, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 space-y-2.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-sm font-semibold text-slate-900">{t.theme}</h4>
                      {t.percentage != null && (
                        <Badge variant="purple" size="sm">
                          {t.percentage}% prevalence
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{t.description}</p>

                    {/* Supporting quotes if any */}
                    {t.supporting_quotes && t.supporting_quotes.length > 0 && (
                      <div className="pt-2 border-t border-slate-200/60 space-y-1.5">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                          Quotes
                        </span>
                        {t.supporting_quotes.map((q, qi) => (
                          <p key={qi} className="text-xs italic text-slate-700 bg-white p-2 rounded-lg border border-slate-100">
                            "{q}"
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Behavioral Trends & Supporting References */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Behavioral trends */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Observed Behavioral Trends</CardTitle>
              </CardHeader>
              <CardContent className="p-5">
                <ul className="space-y-2 text-xs text-slate-700">
                  {insight.behavioral_trends?.map((bt, i) => (
                    <li key={i} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                      &bull; {bt}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Supporting references */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Supporting Citations & Evidence</CardTitle>
              </CardHeader>
              <CardContent className="p-5">
                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {insight.supporting_references?.map((sr, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-white border border-slate-150 text-xs shadow-2xs">
                      <p className="italic text-slate-700 mb-1">"{sr.content_snippet}"</p>
                      <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium">
                        <span className="text-indigo-600 font-semibold">{sr.persona_name}</span>
                        <Badge variant="outline" size="sm">
                          {sr.source_type}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Limitations Disclaimer */}
          {insight.limitations && (
            <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200/80 text-amber-900 text-xs flex items-start gap-3">
              <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-amber-950 mb-0.5">Simulation Disclaimer & Methodology Limits</p>
                <p className="leading-relaxed text-amber-800">{insight.limitations}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
