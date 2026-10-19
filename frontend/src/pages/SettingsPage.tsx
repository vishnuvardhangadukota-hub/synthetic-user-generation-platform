import React, { useState, useEffect } from 'react';
import {
  Settings,
  Server,
  Database,
  Cloud,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  RefreshCw,
  Terminal,
} from 'lucide-react';
import { apiClient, API_BASE_URL } from '@/services/apiClient';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useToast } from '@/context/ToastContext';

export const SettingsPage: React.FC = () => {
  const { success, error } = useToast();
  const [isPinging, setIsPinging] = useState(false);
  const [healthStatus, setHealthStatus] = useState<{ status: string; app_name?: string } | null>(
    null
  );
  const [pingError, setPingError] = useState<string | null>(null);

  const testConnection = async () => {
    try {
      setIsPinging(true);
      setPingError(null);
      const res = await apiClient.checkHealth();
      setHealthStatus(res);
      success('Connected to backend', `Status: ${res.status} (${res.app_name || 'FastAPI'})`);
    } catch (err: any) {
      setPingError(err.message || 'Connection failed');
      error('Connection check failed', err.message);
    } finally {
      setIsPinging(false);
    }
  };

  useEffect(() => {
    testConnection();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <PageHeader
        title="Settings & System Diagnostics"
        description="Environment parameters, API connectivity verification, and deployment configurations."
      />

      {/* Backend Connectivity Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2.5">
            <Server className="w-5 h-5 text-indigo-600" />
            <div>
              <CardTitle>FastAPI Backend Gateway</CardTitle>
              <CardDescription>Live connection verification to the Python backend API</CardDescription>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${isPinging ? 'animate-spin' : ''}`} />}
            onClick={testConnection}
            isLoading={isPinging}
          >
            Test Connection
          </Button>
        </CardHeader>
        <CardContent className="p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider block">
                API Base URL
              </span>
              <span className="text-sm font-mono font-semibold text-slate-900 mt-0.5 block">
                {API_BASE_URL}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  healthStatus?.status === 'online'
                    ? 'bg-emerald-500'
                    : pingError
                    ? 'bg-rose-500'
                    : 'bg-amber-400'
                }`}
              />
              <span className="text-xs font-semibold text-slate-700">
                {healthStatus?.status === 'online'
                  ? 'Service Healthy (online)'
                  : pingError
                  ? 'Unreachable'
                  : 'Checking...'}
              </span>
            </div>
          </div>

          {healthStatus && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-lg border border-slate-100 bg-white">
                <span className="text-slate-400 block font-medium">Application</span>
                <span className="font-semibold text-slate-900 mt-0.5 block">
                  {healthStatus.app_name || 'Synthetic Research Platform'}
                </span>
              </div>
              <div className="p-3 rounded-lg border border-slate-100 bg-white">
                <span className="text-slate-400 block font-medium">Interactive Docs</span>
                <a
                  href={`${API_BASE_URL}/docs`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-indigo-600 hover:text-indigo-800 mt-0.5 inline-flex items-center gap-1"
                >
                  Swagger UI <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="p-3 rounded-lg border border-slate-100 bg-white">
                <span className="text-slate-400 block font-medium">OpenAPI Schema</span>
                <a
                  href={`${API_BASE_URL}/openapi.json`}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-indigo-600 hover:text-indigo-800 mt-0.5 inline-flex items-center gap-1"
                >
                  openapi.json <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          )}

          {pingError && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Failed to connect to API</p>
                <p className="mt-0.5">{pingError}</p>
                <p className="mt-1 text-slate-500">
                  Ensure the FastAPI backend is running via{' '}
                  <code className="font-mono text-slate-700">uvicorn app.main:app --port 8000</code>.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Deployment & Production Readiness Guidance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Cloud className="w-4 h-4 text-indigo-600" />
              <CardTitle className="text-sm">Render Deployment: Frontend Static Site</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-5 space-y-3 text-xs text-slate-600">
            <p>Deploy the frontend as a high-performance static site on Render or Vercel:</p>
            <div className="p-3 rounded-lg bg-slate-900 text-slate-200 font-mono space-y-1.5 text-[11px]">
              <p className="text-slate-400"># Render Static Site Configuration</p>
              <p>
                <span className="text-indigo-400">Build Command:</span> npm run build
              </p>
              <p>
                <span className="text-indigo-400">Publish Directory:</span> dist
              </p>
              <p>
                <span className="text-indigo-400">Environment Variable:</span>{' '}
                VITE_API_BASE_URL=https://your-api.onrender.com
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4 text-indigo-600" />
              <CardTitle className="text-sm">Render Deployment: FastAPI Backend</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-5 space-y-3 text-xs text-slate-600">
            <p>Deploy the FastAPI backend as a Render Web Service with Python 3.11+:</p>
            <div className="p-3 rounded-lg bg-slate-900 text-slate-200 font-mono space-y-1.5 text-[11px]">
              <p className="text-slate-400"># Render Web Service Configuration</p>
              <p>
                <span className="text-indigo-400">Build Command:</span> pip install -r requirements.txt
              </p>
              <p>
                <span className="text-indigo-400">Start Command:</span> uvicorn app.main:app --host 0.0.0.0 --port $PORT
              </p>
              <p>
                <span className="text-indigo-400">Persistent Disk:</span> Mount at /data for persistent sqlite/data
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Database & Architecture Specifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-600" />
            <CardTitle className="text-sm">Database & Persistent Architecture</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-5 space-y-3 text-xs text-slate-600">
          <p>
            In production environments, configure <code className="font-mono text-slate-800">DATABASE_URL</code> to
            a managed PostgreSQL instance (e.g., Render PostgreSQL or Supabase) or mount a persistent disk for
            SQLite to ensure persona memories, simulation responses, and research reports persist across service redeploys.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
