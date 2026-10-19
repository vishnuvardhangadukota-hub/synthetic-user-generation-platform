import React from 'react';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'rectangular' | 'circular' | 'text';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'rectangular',
  className = '',
  ...props
}) => {
  const variantStyles = {
    rectangular: 'rounded-lg',
    circular: 'rounded-full',
    text: 'rounded h-4',
  };

  return (
    <div
      className={`animate-pulse bg-slate-200/80 ${variantStyles[variant]} ${className}`}
      {...props}
    />
  );
};

export const MetricCardSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" className="w-24 h-3.5" />
        <Skeleton variant="circular" className="w-7 h-7" />
      </div>
      <Skeleton variant="text" className="w-16 h-7" />
      <Skeleton variant="text" className="w-32 h-3" />
    </div>
  );
};

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-4">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <Skeleton variant="text" className="w-40 h-5" />
        <Skeleton variant="text" className="w-24 h-4" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 py-2">
          <Skeleton variant="circular" className="w-9 h-9 shrink-0" />
          <div className="space-y-1.5 flex-1">
            <Skeleton variant="text" className="w-1/3 h-4" />
            <Skeleton variant="text" className="w-1/2 h-3" />
          </div>
          <Skeleton variant="text" className="w-20 h-6 rounded-full shrink-0" />
        </div>
      ))}
    </div>
  );
};
