import React, { useState } from 'react';
import {
  Users,
  Plus,
  Trash2,
  MessagesSquare,
  Sparkles,
  Info,
  Brain,
  MapPin,
  Briefcase,
  UserCheck,
} from 'lucide-react';
import { personasApi, conversationsApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type { Persona, PersonaFullMemoryResponse } from '@/types';

interface ExperimentPersonasTabProps {
  experimentId: string;
  personas: Persona[];
  onRefresh: () => void;
  onSelectForInterview: (persona: Persona) => void;
}

export const ExperimentPersonasTab: React.FC<ExperimentPersonasTabProps> = ({
  experimentId,
  personas,
  onRefresh,
  onSelectForInterview,
}) => {
  const { success, error } = useToast();

  // Generation Modal
  const [generateModalOpen, setGenerateModalOpen] = useState(false);
  const [generateCount, setGenerateCount] = useState(3);
  const [isGenerating, setIsGenerating] = useState(false);

  // Detail / Memory Inspection Modal
  const [inspectedPersona, setInspectedPersona] = useState<Persona | null>(null);
  const [personaMemory, setPersonaMemory] = useState<PersonaFullMemoryResponse | null>(null);
  const [isLoadingMemory, setIsLoadingMemory] = useState(false);

  // Delete State
  const [deleteTarget, setDeleteTarget] = useState<Persona | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsGenerating(true);
      const res = await personasApi.generate(experimentId, generateCount);
      success('Personas generated', `Generated ${res.personas.length} synthetic personas.`);
      setGenerateModalOpen(false);
      onRefresh();
    } catch (err: any) {
      error('Failed to generate personas', err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleInspect = async (persona: Persona) => {
    setInspectedPersona(persona);
    setIsLoadingMemory(true);
    try {
      const mem = await conversationsApi.getMemory(persona.id);
      setPersonaMemory(mem);
    } catch (err: any) {
      error('Failed to load persona memory', err.message);
    } finally {
      setIsLoadingMemory(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      setIsDeleting(true);
      await personasApi.delete(deleteTarget.id);
      success('Persona deleted', `"${deleteTarget.name}" was removed from the experiment.`);
      setDeleteTarget(null);
      onRefresh();
    } catch (err: any) {
      error('Failed to delete persona', err.message);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Synthetic Persona Cohort</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {personas.length} diverse agent personas simulating target market behaviors.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          leftIcon={<Sparkles className="w-4 h-4" />}
          onClick={() => setGenerateModalOpen(true)}
        >
          Generate Cohort
        </Button>
      </div>

      {/* Personas Grid */}
      {personas.length === 0 ? (
        <EmptyState
          icon={<Users className="w-6 h-6 text-indigo-600" />}
          title="No synthetic personas generated yet"
          description="Generate synthetic user personas with varied ages, professions, behavioral traits, and preferences to start simulating."
          actionLabel="Generate Personas"
          actionIcon={<Sparkles className="w-4 h-4" />}
          onAction={() => setGenerateModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {personas.map((persona) => (
            <Card key={persona.id} hoverEffect className="flex flex-col justify-between">
              <CardContent className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                      {persona.name.charAt(0)}
                    </div>
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(persona)}
                      className="text-slate-300 hover:text-rose-600 p-1 rounded transition-colors"
                      title="Delete persona"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h4 className="text-base font-semibold text-slate-900 line-clamp-1">
                    {persona.name}
                  </h4>

                  <div className="flex items-center gap-2 text-xs text-slate-500 mt-1 mb-3 flex-wrap">
                    <span className="flex items-center gap-1 font-medium text-slate-700">
                      <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                      {persona.occupation}
                    </span>
                    <span>&bull;</span>
                    <span>{persona.age} yrs</span>
                    <span>&bull;</span>
                    <span className="flex items-center gap-1 text-slate-500">
                      <MapPin className="w-3 h-3 text-slate-400" />
                      {persona.location}
                    </span>
                  </div>

                  {/* Traits & Tags */}
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {persona.personality_traits?.slice(0, 3).map((trait, i) => (
                      <span
                        key={i}
                        className="text-[11px] px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium border border-slate-200/60"
                      >
                        {trait}
                      </span>
                    ))}
                    {(persona.personality_traits?.length || 0) > 3 && (
                      <span className="text-[11px] px-1.5 py-0.5 text-slate-400 font-medium">
                        +{persona.personality_traits.length - 3} more
                      </span>
                    )}
                  </div>

                  {/* Behavioral patterns preview */}
                  {persona.behavioral_patterns && persona.behavioral_patterns.length > 0 && (
                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-4 bg-slate-50/70 p-2.5 rounded-lg border border-slate-100 italic">
                      "{persona.behavioral_patterns[0]}"
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={<Brain className="w-3.5 h-3.5" />}
                    onClick={() => handleInspect(persona)}
                  >
                    Inspect Profile
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<MessagesSquare className="w-3.5 h-3.5 text-indigo-600" />}
                    onClick={() => onSelectForInterview(persona)}
                    className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
                  >
                    Interview
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Generate Cohort Modal */}
      <Modal
        isOpen={generateModalOpen}
        onClose={() => setGenerateModalOpen(false)}
        title="Generate Synthetic Personas"
        description="Specify how many user personas to generate for this experiment cohort."
        maxWidth="sm"
      >
        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Number of Personas (1 - 20)
            </label>
            <input
              type="number"
              min={1}
              max={20}
              value={generateCount}
              onChange={(e) => setGenerateCount(parseInt(e.target.value) || 1)}
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
              required
            />
            <p className="text-xs text-slate-500 mt-1.5">
              Personas are synthetically generated to match your target audience criteria with
              varied demographics, decision styles, and behavioral traits.
            </p>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2.5">
            <Button
              variant="outline"
              size="md"
              type="button"
              onClick={() => setGenerateModalOpen(false)}
              disabled={isGenerating}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="md"
              type="submit"
              isLoading={isGenerating}
              leftIcon={<Sparkles className="w-4 h-4" />}
            >
              Generate Personas
            </Button>
          </div>
        </form>
      </Modal>

      {/* Inspect Profile & Memory Modal */}
      <Modal
        isOpen={!!inspectedPersona}
        onClose={() => setInspectedPersona(null)}
        title={inspectedPersona ? `${inspectedPersona.name} — Full Profile & Memory` : 'Profile'}
        description="Comprehensive persona psychological profile, habits, opinions, and memory state."
        maxWidth="xl"
      >
        {inspectedPersona && (
          <div className="space-y-5">
            {/* Header summary */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">{inspectedPersona.name}</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {inspectedPersona.occupation} &bull; {inspectedPersona.age} years old &bull;{' '}
                  {inspectedPersona.location}
                </p>
              </div>
              <Button
                variant="primary"
                size="sm"
                leftIcon={<MessagesSquare className="w-3.5 h-3.5" />}
                onClick={() => {
                  const p = inspectedPersona;
                  setInspectedPersona(null);
                  onSelectForInterview(p);
                }}
              >
                Chat Now
              </Button>
            </div>

            {/* Demographics & Psychological Profile */}
            <div>
              <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Psychological Profile & Demographics
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
                {Object.entries(inspectedPersona.psychological_profile || {}).map(([k, v]) => (
                  <div key={k} className="p-2.5 rounded-lg border border-slate-100 bg-white">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                      {k.replace(/_/g, ' ')}
                    </span>
                    <span className="font-medium text-slate-800 mt-0.5 block">{String(v)}</span>
                  </div>
                ))}
                {Object.entries(inspectedPersona.demographics || {}).map(([k, v]) => (
                  <div key={k} className="p-2.5 rounded-lg border border-slate-100 bg-white">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                      {k.replace(/_/g, ' ')}
                    </span>
                    <span className="font-medium text-slate-800 mt-0.5 block">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Behavioral Patterns */}
            <div>
              <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Behavioral Patterns & Habits
              </h4>
              <div className="space-y-1.5">
                {inspectedPersona.behavioral_patterns?.map((bp, i) => (
                  <div
                    key={i}
                    className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs text-slate-700"
                  >
                    &bull; {bp}
                  </div>
                ))}
              </div>
            </div>

            {/* Preferences & Opinions */}
            <div>
              <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Preferences & Established Opinions
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {Object.entries(inspectedPersona.preferences || {}).map(([k, v]) => (
                  <div key={k} className="p-2 rounded-lg bg-indigo-50/50 border border-indigo-100">
                    <span className="font-semibold text-indigo-900 block">{k}:</span>
                    <span className="text-indigo-800">{String(v)}</span>
                  </div>
                ))}
                {Object.entries(inspectedPersona.opinions || {}).map(([k, v]) => (
                  <div key={k} className="p-2 rounded-lg bg-violet-50/50 border border-violet-100">
                    <span className="font-semibold text-violet-900 block">{k}:</span>
                    <span className="text-violet-800">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Memory Summary */}
            {inspectedPersona.memory_summary && (
              <div>
                <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Memory Summary
                </h4>
                <div className="p-3 rounded-lg bg-slate-100 text-xs text-slate-700 leading-relaxed font-mono">
                  {inspectedPersona.memory_summary}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Remove Persona"
        message={`Are you sure you want to remove "${deleteTarget?.name}"? Any survey responses or interview history for this persona will also be removed.`}
        confirmLabel="Remove Persona"
        isLoading={isDeleting}
      />
    </div>
  );
};
