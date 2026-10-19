import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FlaskConical,
  Users,
  ClipboardList,
  MessagesSquare,
  BarChart3,
  Settings,
  Sparkles,
  ExternalLink,
  Activity,
  Layers,
} from 'lucide-react';
import { apiClient } from '@/services/apiClient';

export interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const check = async () => {
      try {
        const res = await apiClient.checkHealth();
        if (mounted) setIsBackendOnline(res.status === 'online');
      } catch {
        if (mounted) setIsBackendOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { name: 'Overview', to: '/', icon: LayoutDashboard },
    { name: 'Experiments', to: '/experiments', icon: FlaskConical },
    { name: 'Personas', to: '/personas', icon: Users },
    { name: 'Surveys & Simulation', to: '/surveys', icon: ClipboardList },
    { name: 'Interviews & Memory', to: '/interviews', icon: MessagesSquare },
    { name: 'Platform Analytics', to: '/analytics', icon: BarChart3 },
    { name: 'Settings', to: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col h-full select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-slate-100 flex items-center justify-between">
        <NavLink
          to="/"
          onClick={onCloseMobile}
          className="flex items-center gap-2.5 group"
        >
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-sm shadow-indigo-200 group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4 fill-white/20" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-slate-900 block leading-tight">
              Synthetic
            </span>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
              User Research
            </span>
          </div>
        </NavLink>

        <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-medium border border-slate-200/60">
          v2.0
        </span>
      </div>

      {/* Navigation items */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Platform
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50/80 text-indigo-700 font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Footer Info & Backend Status */}
      <div className="p-3 border-t border-slate-100 bg-slate-50/50 space-y-2">
        <div className="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-white border border-slate-200/70 shadow-xs">
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                isBackendOnline === true
                  ? 'bg-emerald-500 animate-pulse'
                  : isBackendOnline === false
                  ? 'bg-rose-500'
                  : 'bg-amber-400'
              }`}
            />
            <span className="text-xs font-medium text-slate-700">API Status</span>
          </div>
          <span
            className={`text-[11px] font-semibold ${
              isBackendOnline === true
                ? 'text-emerald-700'
                : isBackendOnline === false
                ? 'text-rose-700'
                : 'text-amber-700'
            }`}
          >
            {isBackendOnline === true
              ? 'Connected'
              : isBackendOnline === false
              ? 'Disconnected'
              : 'Checking...'}
          </span>
        </div>

        <div className="px-2 pt-1 flex items-center justify-between text-[11px] text-slate-400">
          <span>FastAPI Engine</span>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="hover:text-indigo-600 transition-colors flex items-center gap-1 font-medium"
          >
            Swagger Docs
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </div>
      </div>
    </aside>
  );
};
