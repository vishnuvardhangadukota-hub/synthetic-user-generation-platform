import React, { useEffect, useState } from 'react';
import {
  Award,
  Play,
  TrendingUp,
  Users,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
} from 'lucide-react';
import { usageScoreApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input, Textarea } from '@/components/ui/FormControls';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type { UsageScoreReport, UsageScorePersonaItem } from '@/types';

interface ExperimentUsageScoreTabProps {
  experimentId: string;
  hasPersonas: boolean;
  onRefreshParent: () => void;
}

export const ExperimentUsageScoreTab: React.FC<ExperimentUsageScoreTabProps> = ({
  experimentId,
  hasPersonas,
  onRefreshParent,
}) => {
  const { success, error } = useToast();

  const [report, setReport] = useState<UsageScoreReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Calculation Modal
  const [calcModalOpen, setCalcModalOpen] = useState(false);
  const [customQuestion, setCustomQuestion] = useState('');
  const [isCalculating, setIsCalculating] = useState(false);

  const fetchScore = async () => {
    try {
      setIsLoading(true);
      const data = await usageScoreApi.getLatest(experimentId);
      setReport(data);
    } catch {
      setReport(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScore();
  }, [experimentId]);

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hasPersonas) {
      error(
        'No personas available',
        'Please generate synthetic personas first before evaluating product usage score.'
      );
      return;
    }

    try {
      setIsCalculating(true);
      const res = await usageScoreApi.calculate(
        experimentId,
        customQuestion.trim() || undefined
      );
      setReport(res);
      success(
        'Usage Score Computed',
        `Overall score: ${res.overall_score}/10 (${res.would_use_percentage}% adoption intent)`
      );
      setCalcModalOpen(false);
      setCustomQuestion('');
      onRefreshParent();
    } catch (err: any) {
      error('Usage score calculation failed', err.message);
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Product Usage Likelihood Evaluation</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Simulates "Would Use This Product" adoption scoring and demographic breakdown.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          leftIcon={<Sparkles className="w-4 h-4" />}
          onClick={() => setCalcModalOpen(true)}
          disabled={!hasPersonas}
        >
          {report ? 'Re-evaluate Usage Score' : 'Calculate Usage Score'}
        </Button>
      </div>

      {!report ? (
        <EmptyState
          icon={<Award className="w-6 h-6 text-indigo-600" />}
          title="No usage score calculated yet"
          description={
            hasPersonas
              ? 'Click "Calculate Usage Score" to run adoption evaluations across all personas.'
              : 'Generate personas first before computing adoption likelihood.'
          }
          actionLabel={hasPersonas ? 'Calculate Usage Score' : undefined}
          onAction={hasPersonas ? () => setCalcModalOpen(true) : undefined}
        />
      ) : (
        <div className="space-y-6">
          {/* Top Score Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Card className="bg-gradient-to-br from-indigo-50/60 to-white">
              <CardContent className="p-6">
                <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
                  Overall Usage Score
                </span>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-extrabold text-slate-900">
                    {report.overall_score}
                  </span>
                  <span className="text-base text-slate-400 font-semibold">/ 10</span>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Validation rating: {report.overall_score >= 7 ? 'High Product Demand' : report.overall_score >= 4 ? 'Moderate Fit / Niche' : 'Low Adoption Intent'}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-emerald-50/60 to-white">
              <CardContent className="p-6">
                <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600">
                  Adoption Intent Percentage
                </span>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-extrabold text-emerald-700">
                    {report.would_use_percentage}%
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Of cohort personas responded affirmatively to regular product usage.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-violet-50/60 to-white">
              <CardContent className="p-6">
                <span className="text-xs font-semibold uppercase tracking-wider text-violet-600">
                  Total Cohort Evaluated
                </span>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-4xl font-extrabold text-slate-900">
                    {report.persona_scores?.length || 0}
                  </span>
                  <span className="text-base text-slate-400 font-semibold">Personas</span>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  Individually simulated against personal budget and habits.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Segment Breakdowns */}
          {report.segmentation_breakdown && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* By Age Group */}
              {report.segmentation_breakdown.by_age_group && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Breakdown by Age Group</CardTitle>
                  </CardHeader>
                  <CardContent className="p-5">
                    <div className="space-y-3">
                      {Object.entries(report.segmentation_breakdown.by_age_group).map(
                        ([group, data]: [string, any]) => (
                          <div
                            key={group}
                            className="p-3 rounded-lg border border-slate-100 bg-slate-50/70 flex items-center justify-between"
                          >
                            <div>
                              <p className="text-xs font-semibold text-slate-900">{group}</p>
                              <p className="text-[11px] text-slate-500">
                                {data.count} {data.count === 1 ? 'persona' : 'personas'}
                              </p>
                            </div>
                            <div className="text-right">
                              <span className="text-xs font-bold text-indigo-700 block">
                                {data.average_score} / 10
                              </span>
                              <span className="text-[11px] text-slate-500">
                                {data.would_use_pct}% would use
                              </span>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* By Occupation */}
              {report.segmentation_breakdown.by_occupation && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Breakdown by Occupation</CardTitle>
                  </CardHeader>
                  <CardContent className="p-5">
                    <div className="space-y-3">
                      {Object.entries(report.segmentation_breakdown.by_occupation).map(
                        ([occ, data]: [string, any]) => (
                          <div
                            key={occ}
                            className="p-3 rounded-lg border border-slate-100 bg-slate-50/70 flex items-center justify-between"
                          >
                            <div>
                              <p className="text-xs font-semibold text-slate-900">{occ}</p>
                              <p className="text-[11px] text-slate-500">
                                {data.count} {data.count === 1 ? 'persona' : 'personas'}
                              </p>
                            </div>
                            <div className="text-right">
                              <span className="text-xs font-bold text-indigo-700 block">
                                {data.average_score} / 10
                              </span>
                              <span className="text-[11px] text-slate-500">
                                {data.would_use_pct}% would use
                              </span>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Persona Scores Table */}
          <Card>
            <CardHeader>
              <CardTitle>Individual Persona Evaluation Details</CardTitle>
              <CardDescription>
                Score attribution, category decisions, and simulation reasoning
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50/70 text-slate-500 border-b border-slate-100">
                    <tr>
                      <th className="px-5 py-3 font-semibold">Persona</th>
                      <th className="px-4 py-3 font-semibold">Occupation & Age</th>
                      <th className="px-4 py-3 font-semibold">Price Sensitivity</th>
                      <th className="px-4 py-3 font-semibold">Score</th>
                      <th className="px-4 py-3 font-semibold">Verdict</th>
                      <th className="px-5 py-3 font-semibold">Reasoning</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {report.persona_scores?.map((ps: UsageScorePersonaItem) => (
                      <tr key={ps.persona_id} className="hover:bg-slate-50/50">
                        <td className="px-5 py-3.5 font-semibold text-slate-900">
                          {ps.persona_name}
                        </td>
                        <td className="px-4 py-3.5 text-slate-600">
                          {ps.occupation}, {ps.age}
                        </td>
                        <td className="px-4 py-3.5 text-slate-500">
                          {ps.price_sensitivity || 'Moderate'}
                        </td>
                        <td className="px-4 py-3.5 font-bold text-slate-900">
                          {ps.score} / 10
                        </td>
                        <td className="px-4 py-3.5">
                          <Badge
                            variant={
                              ps.would_use ? 'success' : ps.category === 'Maybe' ? 'warning' : 'error'
                            }
                            size="sm"
                          >
                            {ps.category || (ps.would_use ? 'Would Use' : 'Unlikely')}
                          </Badge>
                        </td>
                        <td className="px-5 py-3.5 text-slate-600 max-w-xs leading-relaxed">
                          {ps.reasoning}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Calculation Method & Disclaimer */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-xs space-y-2 text-slate-600">
            <p>
              <strong className="text-slate-800">Methodology:</strong> {report.calculation_method}
            </p>
            <p className="text-[11px] text-slate-500 italic">
              <strong>Limitations:</strong> {report.limitations}
            </p>
          </div>
        </div>
      )}

      {/* Calculate Usage Score Modal */}
      <Modal
        isOpen={calcModalOpen}
        onClose={() => setCalcModalOpen(false)}
        title="Evaluate Product Usage Scoring"
        description="Optionally configure a custom product usage evaluation question or use the intelligent default."
        maxWidth="md"
      >
        <form onSubmit={handleCalculate} className="space-y-4">
          <Textarea
            label="Custom Evaluation Question (Optional)"
            placeholder="e.g., How likely are you to subscribe to QuickBite Pro for ₹299/month based on your daily food habits?"
            rows={3}
            value={customQuestion}
            onChange={(e) => setCustomQuestion(e.target.value)}
            helperText="Leave blank to use the standard adoption likelihood prompt formulated for your product."
          />

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2.5">
            <Button
              variant="outline"
              size="md"
              type="button"
              onClick={() => setCalcModalOpen(false)}
              disabled={isCalculating}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="md"
              type="submit"
              isLoading={isCalculating}
              leftIcon={<Award className="w-4 h-4" />}
            >
              Run Evaluation
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
