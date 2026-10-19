import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input, Textarea } from '@/components/ui/FormControls';
import { experimentsApi } from '@/services/api';
import { useToast } from '@/context/ToastContext';
import { Plus, Trash2, Sparkles } from 'lucide-react';
import type { Experiment } from '@/types';

export interface CreateExperimentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (experiment: Experiment) => void;
}

export const CreateExperimentModal: React.FC<CreateExperimentModalProps> = ({
  isOpen,
  onClose,
  onCreated,
}) => {
  const { success, error } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [name, setName] = useState('');
  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [objectives, setObjectives] = useState<string[]>([
    'Understand price sensitivity & willingness to pay',
    'Assess core feature demand and usability expectations',
  ]);
  const [numberOfPersonas, setNumberOfPersonas] = useState(3);

  const handleAddObjective = () => {
    setObjectives([...objectives, '']);
  };

  const handleObjectiveChange = (index: number, value: string) => {
    const updated = [...objectives];
    updated[index] = value;
    setObjectives(updated);
  };

  const handleRemoveObjective = (index: number) => {
    if (objectives.length <= 1) return;
    setObjectives(objectives.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !productName.trim() || !productDescription.trim() || !targetAudience.trim()) {
      error('Validation error', 'Please fill in all required fields.');
      return;
    }

    const filteredObjectives = objectives.map((o) => o.trim()).filter(Boolean);
    if (filteredObjectives.length === 0) {
      error('Validation error', 'Please provide at least one research objective.');
      return;
    }

    try {
      setIsSubmitting(true);
      const created = await experimentsApi.create({
        name: name.trim(),
        product_name: productName.trim(),
        product_description: productDescription.trim(),
        target_audience: targetAudience.trim(),
        research_objectives: filteredObjectives,
        number_of_personas: numberOfPersonas,
      });

      success('Experiment created', `Experiment "${created.name}" created successfully.`);
      onCreated(created);
      onClose();
      // Reset form
      setName('');
      setProductName('');
      setProductDescription('');
      setTargetAudience('');
      setObjectives(['Understand pricing sensitivity', 'Assess feature demand']);
      setNumberOfPersonas(3);
    } catch (err: any) {
      error('Failed to create experiment', err.message || 'An unexpected error occurred.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Research Experiment"
      description="Define your product, target audience, and research goals to simulate synthetic user cohorts."
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Experiment Name"
          placeholder="e.g., QuickBite Pricing & Retention Study"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          <Input
            label="Product Name"
            placeholder="e.g., QuickBite Pro"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            required
          />

          <Input
            label="Default Persona Count (1-20)"
            type="number"
            min={1}
            max={20}
            value={numberOfPersonas}
            onChange={(e) => setNumberOfPersonas(parseInt(e.target.value) || 3)}
            required
          />
        </div>

        <Textarea
          label="Product Description"
          placeholder="Explain what the product does, its value proposition, key features, and pricing model..."
          rows={3}
          value={productDescription}
          onChange={(e) => setProductDescription(e.target.value)}
          required
        />

        <Textarea
          label="Target Audience Definition"
          placeholder="e.g., Working professionals aged 25-40 in metropolitan cities who order takeout 3+ times weekly..."
          rows={2}
          value={targetAudience}
          onChange={(e) => setTargetAudience(e.target.value)}
          required
        />

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-slate-700">
              Research Objectives <span className="text-rose-500">*</span>
            </label>
            <button
              type="button"
              onClick={handleAddObjective}
              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add Objective
            </button>
          </div>

          <div className="space-y-2">
            {objectives.map((obj, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  type="text"
                  value={obj}
                  onChange={(e) => handleObjectiveChange(idx, e.target.value)}
                  placeholder={`Objective ${idx + 1}`}
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
                  required
                />
                {objectives.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveObjective(idx)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-md transition-colors"
                    title="Remove objective"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2.5">
          <Button variant="outline" size="md" type="button" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="md"
            type="submit"
            isLoading={isSubmitting}
            leftIcon={<Sparkles className="w-4 h-4" />}
          >
            Create Experiment
          </Button>
        </div>
      </form>
    </Modal>
  );
};
