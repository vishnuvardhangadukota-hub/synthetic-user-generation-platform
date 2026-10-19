import React from 'react';
import { Menu, Plus, Sparkles, Activity } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export interface TopNavProps {
  onOpenMobileMenu: () => void;
  onOpenNewExperiment?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  onOpenMobileMenu,
  onOpenNewExperiment,
}) => {
  return (
    <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          aria-label="Open sidebar menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
          <span className="font-semibold text-slate-700">Workspace</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-600 font-medium">Synthetic Research Lab</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {onOpenNewExperiment && (
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={onOpenNewExperiment}
            className="shadow-sm"
          >
            New Experiment
          </Button>
        )}
      </div>
    </header>
  );
};
