import React, { useEffect, useState, useMemo } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import {
  FlaskConical,
  Plus,
  Search,
  Users,
  Calendar,
  Trash2,
  ArrowRight,
  Target,
  Sparkles,
} from 'lucide-react';
import { experimentsApi } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { EmptyState } from '@/components/ui/EmptyState';
import { TableSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/context/ToastContext';
import type { Experiment } from '@/types';

export const ExperimentsPage: React.FC = () => {
  const { openNewExperiment } = useOutletContext<{ openNewExperiment: () => void }>();
  const { success, error } = useToast();

  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Delete state
  const [deleteTarget, setDeleteTarget] = useState<Experiment | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchExperiments = async () => {
    try {
      setIsLoading(true);
      const data = await experimentsApi.list();
      setExperiments(data);
    } catch (err: any) {
      error('Failed to load experiments', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const filteredExperiments = useMemo(() => {
    if (!searchQuery.trim()) return experiments;
    const q = searchQuery.toLowerCase();
    return experiments.filter(
      (e) =>
        e.name.toLowerCase().includes(q) ||
        e.product_name.toLowerCase().includes(q) ||
        e.target_audience.toLowerCase().includes(q)
    );
  }, [experiments, searchQuery]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      setIsDeleting(true);
      await experimentsApi.delete(deleteTarget.id);
      success('Experiment deleted', `"${deleteTarget.name}" has been deleted.`);
      setExperiments((prev) => prev.filter((e) => e.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err: any) {
      error('Failed to delete experiment', err.message);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Research Experiments"
        description="Manage your synthetic user research experiments, target audiences, and simulation cohorts."
        badge={
          <Badge variant="purple" size="md">
            {experiments.length} {experiments.length === 1 ? 'Experiment' : 'Experiments'}
          </Badge>
        }
        actions={
          <Button
            variant="primary"
            size="md"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={openNewExperiment}
          >
            New Experiment
          </Button>
        }
      />

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200/80 shadow-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search experiments or products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs sm:text-sm rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
          />
        </div>

        <div className="text-xs text-slate-500 font-medium">
          Showing {filteredExperiments.length} of {experiments.length}
        </div>
      </div>

      {/* Content list */}
      {isLoading ? (
        <TableSkeleton rows={5} />
      ) : filteredExperiments.length === 0 ? (
        <EmptyState
          icon={<FlaskConical className="w-6 h-6 text-indigo-600" />}
          title={searchQuery ? 'No matching experiments' : 'No research experiments yet'}
          description={
            searchQuery
              ? `No experiments matched "${searchQuery}". Try a different keyword.`
              : 'Create an experiment to start generating synthetic user personas and running simulations.'
          }
          actionLabel={searchQuery ? 'Clear Search' : 'Create Experiment'}
          onAction={searchQuery ? () => setSearchQuery('') : openNewExperiment}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredExperiments.map((exp) => (
            <Card
              key={exp.id}
              hoverEffect
              className="flex flex-col justify-between overflow-hidden group"
            >
              <CardContent className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <Badge variant="info" size="sm">
                      {exp.product_name}
                    </Badge>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteTarget(exp);
                      }}
                      className="text-slate-300 hover:text-rose-600 p-1 rounded transition-colors"
                      title="Delete experiment"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <Link to={`/experiments/${exp.id}`}>
                    <h3 className="text-base font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1 mb-1.5">
                      {exp.name}
                    </h3>
                  </Link>

                  <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-4">
                    {exp.product_description}
                  </p>

                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs text-slate-600 mb-4 space-y-1">
                    <div className="flex items-center gap-1.5 font-medium text-slate-700">
                      <Target className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                      <span className="truncate">Target: {exp.target_audience}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-1.5 font-medium">
                    <Users className="w-3.5 h-3.5 text-slate-400" />
                    <span>{exp.number_of_personas} Personas</span>
                  </div>

                  <Link to={`/experiments/${exp.id}`}>
                    <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-3 h-3" />}>
                      Explore
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Research Experiment"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? All associated personas, surveys, conversations, and reports will be permanently deleted.`}
        confirmLabel="Delete Experiment"
        isLoading={isDeleting}
      />
    </div>
  );
};
