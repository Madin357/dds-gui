"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n";

interface SyncStatus { total_jobs: number; active_jobs: number; last_sync: { id: string; status: string; sync_type: string; started_at: string; completed_at: string | null; records_synced: number; records_failed: number; duration_ms: number | null; } | null; recent_errors: number; }
interface SyncJob { id: string; name: string; source_type: string; is_active: boolean; schedule_cron: string | null; tables_to_sync: string[]; }

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function SettingsPage() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [jobs, setJobs] = useState<SyncJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const { t } = useI18n();

  useEffect(() => {
    Promise.all([apiFetch<SyncStatus>("/sync/status"), apiFetch<SyncJob[]>("/sync/jobs")])
      .then(([s, j]) => { setSyncStatus(s); setJobs(j); }).catch(console.error).finally(() => setLoading(false));
  }, []);

  async function triggerSync(jobId: string) {
    setSyncing(jobId);
    try {
      await apiFetch(`/sync/jobs/${jobId}/trigger`, { method: "POST", body: JSON.stringify({ sync_type: "incremental" }) });
      setTimeout(async () => { const s = await apiFetch<SyncStatus>("/sync/status"); setSyncStatus(s); setSyncing(null); }, 2000);
    } catch (e) { console.error(e); setSyncing(null); }
  }

  const syncStatusLabel = (status: string) => {
    const map: Record<string, string> = { completed: t("settings.statusCompleted"), running: t("settings.statusRunning"), failed: t("settings.statusFailed"), partial: t("settings.statusPartial"), pending: t("settings.statusPending") };
    return map[status] || status;
  };
  const syncTypeLabel = (type: string) => {
    const map: Record<string, string> = { full: t("settings.typeFull"), incremental: t("settings.typeIncremental") };
    return map[type] || type;
  };

  if (loading) return <div className="animate-pulse text-slate-400 py-8">{t("settings.loading")}</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("settings.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("settings.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatusCard label={t("settings.activeSyncJobs")} value={syncStatus?.active_jobs ?? 0} />
        <StatusCard label={t("settings.lastSync")} value={syncStatus?.last_sync ? timeAgo(syncStatus.last_sync.started_at) : t("settings.never")} />
        <StatusCard label={t("settings.recordsSynced")} value={syncStatus?.last_sync?.records_synced ?? 0} />
        <StatusCard label={t("settings.recentErrors")} value={syncStatus?.recent_errors ?? 0} alert={(syncStatus?.recent_errors ?? 0) > 0} />
      </div>

      {syncStatus?.last_sync && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-3">{t("settings.lastSyncRun")}</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><span className="text-slate-500">{t("settings.statusLabel")}</span><p className={`font-medium ${syncStatus.last_sync.status === "completed" ? "text-green-600" : syncStatus.last_sync.status === "failed" ? "text-red-600" : "text-amber-600"}`}>{syncStatusLabel(syncStatus.last_sync.status)}</p></div>
            <div><span className="text-slate-500">{t("settings.typeLabel")}</span><p className="font-medium text-slate-700">{syncTypeLabel(syncStatus.last_sync.sync_type)}</p></div>
            <div><span className="text-slate-500">{t("settings.duration")}</span><p className="font-medium text-slate-700">{syncStatus.last_sync.duration_ms ? `${(syncStatus.last_sync.duration_ms / 1000).toFixed(1)}s` : "—"}</p></div>
            <div><span className="text-slate-500">{t("settings.failedRecords")}</span><p className={`font-medium ${syncStatus.last_sync.records_failed > 0 ? "text-red-600" : "text-slate-700"}`}>{syncStatus.last_sync.records_failed}</p></div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("settings.syncJobs")}</h2>
        <table className="w-full text-sm">
          <thead className="border-b"><tr>
            <th className="text-left px-3 py-2 font-medium text-slate-600">{t("settings.name")}</th>
            <th className="text-left px-3 py-2 font-medium text-slate-600">{t("settings.source")}</th>
            <th className="text-center px-3 py-2 font-medium text-slate-600">{t("settings.activeCol")}</th>
            <th className="text-left px-3 py-2 font-medium text-slate-600">{t("settings.schedule")}</th>
            <th className="text-left px-3 py-2 font-medium text-slate-600">{t("settings.tables")}</th>
            <th className="px-3 py-2"></th>
          </tr></thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.id} className="border-b border-slate-50">
                <td className="px-3 py-3 font-medium text-slate-700">{t(`syncJobNames.${j.name}` as any) || j.name}</td>
                <td className="px-3 py-3 text-slate-500 uppercase text-xs">{j.source_type}</td>
                <td className="px-3 py-3 text-center"><span className={`px-2 py-0.5 rounded text-xs font-medium ${j.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>{j.is_active ? t("common.active") : t("common.inactive")}</span></td>
                <td className="px-3 py-3 text-slate-500 text-xs font-mono">{j.schedule_cron || t("settings.manual")}</td>
                <td className="px-3 py-3 text-slate-500 text-xs">{t("settings.tablesCount", { count: j.tables_to_sync.length })}</td>
                <td className="px-3 py-3"><button onClick={() => triggerSync(j.id)} disabled={syncing === j.id} className="px-3 py-1 text-xs font-medium bg-[#1e3a5f] text-white rounded-lg hover:bg-[#2d5a8e] transition disabled:opacity-50">{syncing === j.id ? t("settings.syncing") : t("settings.syncNow")}</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusCard({ label, value, alert }: { label: string; value: string | number; alert?: boolean }) {
  return (<div className={`bg-white rounded-lg shadow-sm p-5 ${alert ? "border-l-4 border-red-500" : ""}`}><p className="text-sm text-slate-500">{label}</p><p className={`text-2xl font-bold mt-1 ${alert ? "text-red-600" : "text-slate-800"}`}>{String(value)}</p></div>);
}
