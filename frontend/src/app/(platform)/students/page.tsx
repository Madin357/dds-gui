"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n";

interface Student { id: string; student_code: string | null; first_name: string; last_name: string; current_gpa: number | null; current_semester: number | null; attendance_rate: number | null; dropout_risk: number | null; performance_risk: number | null; is_active: boolean; }
interface StudentList { items: Student[]; total: number; page: number; page_size: number; }

export default function StudentsPage() {
  const [data, setData] = useState<StudentList | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const { t } = useI18n();

  useEffect(() => {
    setLoading(true);
    let url = `/students?page=${page}&page_size=20`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (riskFilter) url += `&risk_level=${riskFilter}`;
    apiFetch<StudentList>(url).then(setData).catch(console.error).finally(() => setLoading(false));
  }, [page, search, riskFilter]);

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  function riskBadge(score: number | null) {
    if (score === null) return <span className="text-xs text-slate-400">—</span>;
    const cls = score >= 70 ? "bg-red-100 text-red-700" : score >= 40 ? "bg-amber-100 text-amber-700" : "bg-green-100 text-green-700";
    const label = score >= 70 ? t("students.high") : score >= 40 ? t("students.medium") : t("students.low");
    return <span className={`px-2 py-0.5 rounded text-xs font-medium ${cls}`}>{score.toFixed(0)} ({label})</span>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("students.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("students.subtitle")}</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <input type="text" placeholder={t("students.searchPlaceholder")} value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-[#0ea5e9]" />
        <select value={riskFilter} onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0ea5e9]">
          <option value="">{t("students.allRiskLevels")}</option>
          <option value="high">{t("students.highRisk")}</option>
          <option value="medium">{t("students.mediumRisk")}</option>
          <option value="low">{t("students.lowRisk")}</option>
        </select>
        {data && <span className="self-center text-sm text-slate-500">{t("students.studentsCount", { count: data.total })}</span>}
      </div>
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">{t("students.name")}</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">{t("students.code")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("students.gpa")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("students.semester")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("students.attendance")}</th>
              <th className="text-center px-4 py-3 font-medium text-slate-600">{t("students.dropoutRisk")}</th>
              <th className="text-center px-4 py-3 font-medium text-slate-600">{t("students.status")}</th>
            </tr>
          </thead>
          <tbody>
            {loading ? [...Array(8)].map((_, i) => (<tr key={i}><td colSpan={7} className="px-4 py-3"><div className="h-4 bg-slate-100 rounded animate-pulse" /></td></tr>))
            : data?.items.map((s) => (
              <tr key={s.id} className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer transition" onClick={() => window.location.href = `/students/${s.id}`}>
                <td className="px-4 py-3 font-medium text-slate-700">{s.first_name} {s.last_name}</td>
                <td className="px-4 py-3 text-slate-500">{s.student_code || "—"}</td>
                <td className="px-4 py-3 text-right text-slate-700">{s.current_gpa?.toFixed(2) || "—"}</td>
                <td className="px-4 py-3 text-right text-slate-500">{s.current_semester || "—"}</td>
                <td className="px-4 py-3 text-right text-slate-700">{s.attendance_rate?.toFixed(1) || "—"}%</td>
                <td className="px-4 py-3 text-center">{riskBadge(s.dropout_risk)}</td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${s.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{s.is_active ? t("students.active") : t("students.dropped")}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-4 py-2 text-sm border rounded-lg hover:bg-slate-50 disabled:opacity-40">{t("common.previous")}</button>
          <span className="text-sm text-slate-500">{t("common.pageOf", { page, total: totalPages })}</span>
          <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page >= totalPages} className="px-4 py-2 text-sm border rounded-lg hover:bg-slate-50 disabled:opacity-40">{t("common.next")}</button>
        </div>
      )}
    </div>
  );
}
