import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ClipboardList,
  FlaskConical,
  Play,
  ArrowRight,
  HelpCircle,
  Plus,
} from 'lucide-react';
import { experimentsApi, surveysApi } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { TableSkeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type { Experiment, Survey } from '@/types';

interface SurveyWithExp extends Survey {
  experiment_name?: string;
}

export const SurveysPage: React.FC = () => {
  const navigate = useNavigate();
  const { error } = useToast();

  const [surveys, setSurveys] = useState<SurveyWithExp[]>([]);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setIsLoading(true);
        const expList = await experimentsApi.list();
        setExperiments(expList);

        const promises = expList.map(async (exp) => {
          try {
            const list = await surveysApi.listByExperiment(exp.id);
            return list.map((s) => ({ ...s, experiment_name: exp.name }));
          } catch {
            return [];
          }
        });

        const res = await Promise.all(promises);
        setSurveys(res.flat());
      } catch (err: any) {
        error('Failed to load surveys', err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAll();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Surveys & Simulations"
        description="Structured simulation surveys deployed across synthetic persona cohorts."
        badge={
          <Badge variant="purple" size="md">
            {surveys.length} Surveys
          </Badge>
        }
      />

      {isLoading ? (
        <TableSkeleton rows={4} />
      ) : surveys.length === 0 ? (
        <EmptyState
          icon={<ClipboardList className="w-6 h-6 text-indigo-600" />}
          title="No surveys created yet"
          description="Open an experiment to design your first survey and run simulation across synthetic cohorts."
          actionLabel="Go to Experiments"
          onAction={() => navigate('/experiments')}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {surveys.map((survey) => (
            <Card key={survey.id} hoverEffect className="flex flex-col justify-between">
              <CardContent className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <Badge
                      variant={survey.status === 'completed' ? 'success' : 'default'}
                      size="sm"
                    >
                      {survey.status}
                    </Badge>
                    <Link
                      to={`/experiments/${survey.experiment_id}`}
                      className="text-[11px] text-slate-400 hover:text-indigo-600 flex items-center gap-1 font-medium truncate max-w-[160px]"
                    >
                      <FlaskConical className="w-3 h-3 shrink-0" />
                      <span className="truncate">{survey.experiment_name}</span>
                    </Link>
                  </div>

                  <h3 className="text-base font-semibold text-slate-900 line-clamp-1 mb-1">
                    {survey.title}
                  </h3>

                  <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-4">
                    {survey.description || 'Structured survey simulation for target audience.'}
                  </p>

                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between text-xs text-slate-600 mb-4">
                    <span>Questions configured:</span>
                    <strong className="text-slate-900 font-semibold">
                      {survey.questions?.length || 0}
                    </strong>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">
                    {new Date(survey.created_at).toLocaleDateString()}
                  </span>

                  <Link to={`/experiments/${survey.experiment_id}?tab=surveys`}>
                    <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3 h-3" />}>
                      Open Simulation
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
