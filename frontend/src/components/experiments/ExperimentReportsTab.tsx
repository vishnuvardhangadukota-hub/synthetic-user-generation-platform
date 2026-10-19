import React, { useState } from 'react';
import {
  FileText,
  Download,
  CheckCircle2,
  AlertCircle,
  FileCheck,
  Printer,
  Sparkles,
} from 'lucide-react';
import { dashboardApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useToast } from '@/context/ToastContext';

interface ExperimentReportsTabProps {
  experimentId: string;
  experimentName: string;
  hasPersonas: boolean;
  hasResponses: boolean;
}

export const ExperimentReportsTab: React.FC<ExperimentReportsTabProps> = ({
  experimentId,
  experimentName,
  hasPersonas,
  hasResponses,
}) => {
  const { success, error } = useToast();
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (!hasPersonas && !hasResponses) {
      error(
        'Insufficient Data',
        'Experiment has no personas or responses. Generate personas and run a survey before downloading.'
      );
      return;
    }

    try {
      setIsDownloading(true);
      await dashboardApi.downloadPdf(experimentId);
      success('PDF downloaded', 'Publication-grade research report downloaded successfully.');
    } catch (err: any) {
      error('Failed to download PDF', err.message);
    } finally {
      setIsDownloading(false);
    }
  };

  const isReady = hasPersonas || hasResponses;

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white overflow-hidden p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="max-w-xl space-y-2">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/10 text-indigo-200 text-xs font-semibold backdrop-blur-xs">
              <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
              Automated PDF Generator
            </div>
            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              Executive Research Report (PDF)
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Downloads a publication-ready PDF research report containing executive metrics,
              synthetic persona profiles, survey response charts, recurring themes, and usage validation.
            </p>
          </div>

          <div className="shrink-0">
            <Button
              variant="primary"
              size="lg"
              leftIcon={<Download className="w-5 h-5" />}
              onClick={handleDownload}
              isLoading={isDownloading}
              disabled={!isReady}
              className="bg-indigo-500 hover:bg-indigo-400 text-white font-semibold shadow-lg shadow-indigo-950/40"
            >
              Download PDF Report
            </Button>
          </div>
        </div>
      </Card>

      {/* Report Structure Checklist */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Report Inclusions & Sections</CardTitle>
            <CardDescription>Generated automatically from your live experiment database</CardDescription>
          </CardHeader>
          <CardContent className="p-5 space-y-3">
            <div className="flex items-start gap-2.5 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-900">1. Executive Summary & Objective Cards:</strong> Key
                hypotheses, participant counts, and status indicators.
              </div>
            </div>

            <div className="flex items-start gap-2.5 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-900">2. Synthetic Persona Cohort Profiles:</strong> Complete
                demographic, occupation, psychological, and behavioral snapshots.
              </div>
            </div>

            <div className="flex items-start gap-2.5 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-900">3. Simulation Responses & Verbatims:</strong> Grouped
                survey distributions and qualitative interview excerpts.
              </div>
            </div>

            <div className="flex items-start gap-2.5 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-900">4. Thematic & Sentiment Analysis:</strong> Discovered
                recurring theme clusters and consensus patterns.
              </div>
            </div>

            <div className="flex items-start gap-2.5 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-900">5. Product Usage Validation:</strong> Likelihood scoring
                breakdowns by age and occupation segments.
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Report Readiness Diagnostics</CardTitle>
            <CardDescription>Verifies prerequisite simulation data</CardDescription>
          </CardHeader>
          <CardContent className="p-5 space-y-3.5">
            <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-slate-50">
              <div className="flex items-center gap-2 text-xs">
                {hasPersonas ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                )}
                <span className="font-semibold text-slate-800">Personas Generated</span>
              </div>
              <Badge variant={hasPersonas ? 'success' : 'warning'} size="sm">
                {hasPersonas ? 'Ready' : 'Missing'}
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-slate-50">
              <div className="flex items-center gap-2 text-xs">
                {hasResponses ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                )}
                <span className="font-semibold text-slate-800">Survey / Interview Data</span>
              </div>
              <Badge variant={hasResponses ? 'success' : 'default'} size="sm">
                {hasResponses ? 'Collected' : 'Pending'}
              </Badge>
            </div>

            <p className="text-[11px] text-slate-500 leading-relaxed pt-2">
              The PDF generator is powered by ReportLab and generates true vector PDFs with custom
              page geometry, multi-color tables, and structured disclaimers.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
