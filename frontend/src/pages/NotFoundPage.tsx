import React from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle, ArrowLeft, Home } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 border border-indigo-100 shadow-sm">
        <HelpCircle className="w-7 h-7" />
      </div>
      <span className="text-xs font-mono font-bold uppercase tracking-widest text-indigo-600 mb-1">
        404 Error
      </span>
      <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 mb-2">
        Page Not Found
      </h1>
      <p className="text-sm text-slate-500 max-w-sm mb-6 leading-relaxed">
        The research page or resource you are looking for does not exist or has been relocated.
      </p>
      <div className="flex items-center gap-3">
        <Link to="/">
          <Button variant="primary" size="md" leftIcon={<Home className="w-4 h-4" />}>
            Back to Dashboard
          </Button>
        </Link>
        <Link to="/experiments">
          <Button variant="outline" size="md">
            View Experiments
          </Button>
        </Link>
      </div>
    </div>
  );
};
