import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  FlaskConical,
  Users,
  ClipboardList,
  MessagesSquare,
  Sparkles,
  Award,
  FileText,
  Download,
  Trash2,
  Calendar,
  Layers,
  ArrowLeft,
} from 'lucide-react';
import { experimentsApi, personasApi, dashboardApi } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Skeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/context/ToastContext';

// Tabs
import { ExperimentOverviewTab } from '@/components/experiments/ExperimentOverviewTab';
import { ExperimentPersonasTab } from '@/components/experiments/ExperimentPersonasTab';
import { ExperimentSurveysTab } from '@/components/experiments/ExperimentSurveysTab';
import { ExperimentInterviewsTab } from '@/components/experiments/ExperimentInterviewsTab';
import { ExperimentInsightsTab } from '@/components/experiments/ExperimentInsightsTab';
import { ExperimentUsageScoreTab } from '@/components/experiments/ExperimentUsageScoreTab';
import { ExperimentReportsTab } from '@/components/experiments/ExperimentReportsTab';

import type { Experiment, Persona, DashboardPayload } from '@/types';

export const ExperimentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { success, error } = useToast();

  const activeTab = searchParams.get('tab') || 'overview';

  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Cross-tab interaction
  const [interviewPersona, setInterviewPersona] = useState<Persona | null>(null);

  // Delete modal
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Quick PDF download from top bar
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  const fetchData = async () => {
    if (!id) return;
    try {
      setIsLoading(true);
      const [exp, personaList, dash] = await Promise.all([
        experimentsApi.getById(id),
        personasApi.listByExperiment(id).catch(() => [] as Persona[]),
        dashboardApi.getExperimentDashboard(id).catch(() => null),
      ]);
      setExperiment(exp);
      setPersonas(personaList);
      setDashboard(dash);
    } catch (err: any) {
      error('Failed to load experiment', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const setTab = (tab: string) => {
    setSearchParams({ tab });
  };

  const handleSelectPersonaForInterview = (p: Persona) => {
    setInterviewPersona(p);
    setTab('interviews');
  };

  const handleDelete = async () => {
    if (!experiment) return;
    try {
      setIsDeleting(true);
      await experimentsApi.delete(experiment.id);
      success('Experiment deleted', `"${experiment.name}" was deleted.`);
      navigate('/experiments');
    } catch (err: any) {
      error('Delete failed', err.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!id || !experiment) return;
    if (personas.length === 0) {
      error(
        'Cannot Download Report',
        'Experiment has no personas. Generate personas before downloading PDF.'
      );
      return;
    }
    try {
      setIsDownloadingPdf(true);
      await dashboardApi.downloadPdf(id);
      success('PDF downloaded', `Report for ${experiment.name} downloaded.`);
    } catch (err: any) {
      error('Download failed', err.message);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  if (isLoading && !experiment) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Skeleton variant="text" className="w-48 h-8" />
          <Skeleton variant="text" className="w-24 h-6 rounded-full" />
        </div>
        <Skeleton variant="rectangular" className="w-full h-32" />
        <Skeleton variant="rectangular" className="w-full h-96" />
      </div>
    );
  }

  if (!experiment) {
    return (
      <div className="text-center py-16">
        <h2 className="text-lg font-bold text-slate-800">Experiment Not Found</h2>
        <p className="text-sm text-slate-500 mt-1">The requested experiment does not exist.</p>
        <Button variant="primary" size="md" className="mt-4" onClick={() => navigate('/experiments')}>
          Back to Experiments
        </Button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FlaskConical },
    {
      id: 'personas',
      label: 'Personas',
      icon: Users,
      count: personas.length,
    },
    {
      id: 'surveys',
      label: 'Surveys & Simulation',
      icon: ClipboardList,
      count: dashboard?.surveys?.length || 0,
    },
    { id: 'interviews', label: 'Interviews & Memory', icon: MessagesSquare },
    { id: 'insights', label: 'Insights', icon: Sparkles },
    { id: 'usage-score', label: 'Usage Scoring', icon: Award },
    { id: 'reports', label: 'Report PDF', icon: FileText },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Top Header */}
      <PageHeader
        title={experiment.name}
        description={experiment.product_description}
        breadcrumbs={[
          { label: 'Experiments', href: '/experiments' },
          { label: experiment.name },
        ]}
        badge={
          <Badge variant="purple" size="md">
            Product: {experiment.product_name}
          </Badge>
        }
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Download className="w-4 h-4" />}
              onClick={handleDownloadPdf}
              isLoading={isDownloadingPdf}
              disabled={personas.length === 0}
            >
              Export PDF
            </Button>

            <Button
              variant="ghost"
              size="sm"
              leftIcon={<Trash2 className="w-4 h-4 text-slate-400 hover:text-rose-600" />}
              onClick={() => setDeleteConfirmOpen(true)}
              className="text-slate-500 hover:text-rose-600"
            >
              Delete
            </Button>
          </>
        }
      />

      {/* Target Audience Bar */}
      <div className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-700">Target Audience:</span>
          <span className="text-slate-600">{experiment.target_audience}</span>
        </div>

        <div className="flex items-center gap-4 text-slate-400">
          <span>
            Cohort target: <strong>{experiment.number_of_personas} personas</strong>
          </span>
          <span>&bull;</span>
          <span>
            Created {new Date(experiment.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-slate-200 flex items-center gap-1 overflow-x-auto scrollbar-none">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2.5 text-xs sm:text-sm font-semibold border-b-2 transition-all shrink-0 ${
                isActive
                  ? 'border-indigo-600 text-indigo-700 bg-indigo-50/50'
                  : 'border-transparent text-slate-500 hover:text-slate-900 hover:border-slate-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && tab.count > 0 && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                    isActive ? 'bg-indigo-200 text-indigo-800' : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Active Tab Content */}
      <div className="pt-2">
        {activeTab === 'overview' && (
          <ExperimentOverviewTab dashboard={dashboard} onNavigateTab={setTab} />
        )}

        {activeTab === 'personas' && (
          <ExperimentPersonasTab
            experimentId={experiment.id}
            personas={personas}
            onRefresh={fetchData}
            onSelectForInterview={handleSelectPersonaForInterview}
          />
        )}

        {activeTab === 'surveys' && (
          <ExperimentSurveysTab
            experimentId={experiment.id}
            hasPersonas={personas.length > 0}
            onRefreshParent={fetchData}
          />
        )}

        {activeTab === 'interviews' && (
          <ExperimentInterviewsTab
            personas={personas}
            initialSelectedPersona={interviewPersona}
            onRefreshParent={fetchData}
          />
        )}

        {activeTab === 'insights' && (
          <ExperimentInsightsTab
            experimentId={experiment.id}
            hasResponses={(dashboard?.summary_cards?.total_responses || 0) > 0}
            onRefreshParent={fetchData}
          />
        )}

        {activeTab === 'usage-score' && (
          <ExperimentUsageScoreTab
            experimentId={experiment.id}
            hasPersonas={personas.length > 0}
            onRefreshParent={fetchData}
          />
        )}

        {activeTab === 'reports' && (
          <ExperimentReportsTab
            experimentId={experiment.id}
            experimentName={experiment.name}
            hasPersonas={personas.length > 0}
            hasResponses={(dashboard?.summary_cards?.total_responses || 0) > 0}
          />
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleDelete}
        title="Delete Research Experiment"
        message={`Are you sure you want to delete "${experiment.name}"? This action cannot be undone.`}
        confirmLabel="Delete Experiment"
        isLoading={isDeleting}
      />
    </div>
  );
};
