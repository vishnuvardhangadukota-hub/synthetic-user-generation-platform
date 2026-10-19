import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  MessagesSquare,
  FlaskConical,
  Users,
  ArrowRight,
  Brain,
  MessageCircle,
} from 'lucide-react';
import { experimentsApi, personasApi } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { TableSkeleton } from '@/components/ui/Skeleton';
import { ExperimentInterviewsTab } from '@/components/experiments/ExperimentInterviewsTab';
import { useToast } from '@/context/ToastContext';
import type { Experiment, Persona } from '@/types';

export const InterviewsPage: React.FC = () => {
  const navigate = useNavigate();
  const { error } = useToast();

  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExpId, setSelectedExpId] = useState<string>('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchExp = async () => {
      try {
        setIsLoading(true);
        const list = await experimentsApi.list();
        setExperiments(list);
        if (list.length > 0) {
          setSelectedExpId(list[0].id);
        }
      } catch (err: any) {
        error('Failed to load experiments', err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchExp();
  }, []);

  useEffect(() => {
    if (!selectedExpId) {
      setPersonas([]);
      return;
    }
    const loadPersonas = async () => {
      try {
        const pList = await personasApi.listByExperiment(selectedExpId);
        setPersonas(pList);
      } catch {
        setPersonas([]);
      }
    };
    loadPersonas();
  }, [selectedExpId]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Interviews & Memory Consistency"
        description="Conduct multi-turn qualitative interviews with synthetic personas while observing memory partition updates."
      />

      {/* Experiment Selector */}
      {experiments.length > 0 && (
        <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-xs flex items-center gap-3">
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider shrink-0">
            Select Experiment:
          </label>
          <select
            value={selectedExpId}
            onChange={(e) => setSelectedExpId(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs sm:text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            {experiments.map((exp) => (
              <option key={exp.id} value={exp.id}>
                {exp.name} ({exp.product_name})
              </option>
            ))}
          </select>
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={4} />
      ) : experiments.length === 0 ? (
        <EmptyState
          icon={<MessagesSquare className="w-6 h-6 text-indigo-600" />}
          title="No research experiments found"
          description="Create an experiment to start conducting 1-on-1 qualitative interviews with synthetic personas."
          actionLabel="Create Experiment"
          onAction={() => navigate('/experiments')}
        />
      ) : personas.length === 0 ? (
        <EmptyState
          icon={<Users className="w-6 h-6 text-indigo-600" />}
          title="No personas in this experiment"
          description="Open this experiment and generate synthetic personas before initiating interviews."
          actionLabel="Go to Experiment"
          onAction={() => navigate(`/experiments/${selectedExpId}?tab=personas`)}
        />
      ) : (
        <ExperimentInterviewsTab
          personas={personas}
          onRefreshParent={() => {}}
        />
      )}
    </div>
  );
};
