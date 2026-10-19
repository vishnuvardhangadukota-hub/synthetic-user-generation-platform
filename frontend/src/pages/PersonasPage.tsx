import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Users,
  Search,
  Briefcase,
  MapPin,
  MessagesSquare,
  Brain,
  FlaskConical,
  ExternalLink,
} from 'lucide-react';
import { experimentsApi, personasApi } from '@/services/api';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { TableSkeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type { Experiment, Persona } from '@/types';

interface PersonaWithExp extends Persona {
  experiment_name?: string;
}

export const PersonasPage: React.FC = () => {
  const navigate = useNavigate();
  const { error } = useToast();

  const [personas, setPersonas] = useState<PersonaWithExp[]>([]);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedExpFilter, setSelectedExpFilter] = useState<string>('all');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setIsLoading(true);
        const expList = await experimentsApi.list();
        setExperiments(expList);

        const allPersonasPromises = expList.map(async (exp) => {
          try {
            const list = await personasApi.listByExperiment(exp.id);
            return list.map((p) => ({ ...p, experiment_name: exp.name }));
          } catch {
            return [];
          }
        });

        const results = await Promise.all(allPersonasPromises);
        setPersonas(results.flat());
      } catch (err: any) {
        error('Failed to load personas', err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAll();
  }, []);

  const filtered = personas.filter((p) => {
    const matchesExp = selectedExpFilter === 'all' || p.experiment_id === selectedExpFilter;
    if (!matchesExp) return false;
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.name.toLowerCase().includes(q) ||
      p.occupation.toLowerCase().includes(q) ||
      p.location.toLowerCase().includes(q) ||
      p.personality_traits?.some((t) => t.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Synthetic Personas"
        description="Global directory of simulated user personas across all research experiments."
        badge={
          <Badge variant="purple" size="md">
            {personas.length} Active Personas
          </Badge>
        }
      />

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search personas by name, job, trait..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs sm:text-sm rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={selectedExpFilter}
            onChange={(e) => setSelectedExpFilter(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            <option value="all">All Experiments ({experiments.length})</option>
            {experiments.map((exp) => (
              <option key={exp.id} value={exp.id}>
                {exp.name}
              </option>
            ))}
          </select>
          <span className="text-xs text-slate-400 font-medium shrink-0">
            {filtered.length} found
          </span>
        </div>
      </div>

      {isLoading ? (
        <TableSkeleton rows={4} />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<Users className="w-6 h-6 text-indigo-600" />}
          title="No synthetic personas found"
          description={
            searchQuery || selectedExpFilter !== 'all'
              ? 'Try resetting your search filters.'
              : 'Create an experiment and generate synthetic personas to build your simulation database.'
          }
          actionLabel="View Experiments"
          onAction={() => navigate('/experiments')}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((persona) => (
            <Card key={persona.id} hoverEffect className="flex flex-col justify-between">
              <CardContent className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                      {persona.name.charAt(0)}
                    </div>
                    {persona.experiment_name && (
                      <Link
                        to={`/experiments/${persona.experiment_id}`}
                        className="text-[11px] text-slate-400 hover:text-indigo-600 transition-colors flex items-center gap-1 font-medium truncate max-w-[140px]"
                      >
                        <FlaskConical className="w-3 h-3 shrink-0" />
                        <span className="truncate">{persona.experiment_name}</span>
                      </Link>
                    )}
                  </div>

                  <h3 className="text-base font-semibold text-slate-900 line-clamp-1">
                    {persona.name}
                  </h3>

                  <div className="flex items-center gap-2 text-xs text-slate-500 mt-1 mb-3">
                    <span className="flex items-center gap-1 font-medium text-slate-700">
                      <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                      {persona.occupation}
                    </span>
                    <span>&bull;</span>
                    <span>{persona.age} yrs</span>
                    <span>&bull;</span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-400" />
                      {persona.location}
                    </span>
                  </div>

                  {/* Traits preview */}
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {persona.personality_traits?.slice(0, 3).map((t, i) => (
                      <span
                        key={i}
                        className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium"
                      >
                        {t}
                      </span>
                    ))}
                  </div>

                  {/* Behavioral quote preview */}
                  {persona.behavioral_patterns && persona.behavioral_patterns.length > 0 && (
                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100 italic">
                      "{persona.behavioral_patterns[0]}"
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <Link
                    to={`/experiments/${persona.experiment_id}?tab=personas`}
                    className="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1"
                  >
                    View Cohort &rarr;
                  </Link>

                  <Link
                    to={`/experiments/${persona.experiment_id}?tab=interviews`}
                    className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1"
                  >
                    <MessagesSquare className="w-3.5 h-3.5" />
                    Interview
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
