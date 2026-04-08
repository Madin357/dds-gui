"use client";

import { useEffect, useState, use } from "react";
import { apiFetch } from "@/lib/api";

interface StudentDetail {
  id: string;
  student_code: string | null;
  first_name: string;
  last_name: string;
  email: string | null;
  gender: string | null;
  date_of_birth: string | null;
  enrollment_date: string | null;
  current_gpa: number | null;
  current_semester: number | null;
  is_active: boolean;
  dropout_risk: number | null;
  performance_risk: number | null;
  attendance_rate: number | null;
  avg_score: number | null;
  gpa_trend: string | null;
  risk_factors: Record<string, any> | null;
  program_name: string | null;
}

interface Attendance {
  id: string;
  course_name: string | null;
  session_date: string;
  status: string;
}

interface Assessment {
  id: string;
  course_name: string | null;
  type: string;
  title: string | null;
  score: number | null;
  max_score: number;
  percentage: number | null;
  grade: string | null;
  assessed_at: string;
}

function riskColor(score: number | null) {
  if (score === null) return "bg-slate-100 text-slate-600";
  if (score >= 70) return "bg-red-100 text-red-700 border border-red-200";
  if (score >= 40) return "bg-amber-100 text-amber-700 border border-amber-200";
  return "bg-green-100 text-green-700 border border-green-200";
}

export default function StudentDetailPage(props: { params: Promise<{ id: string }> }) {
  const { id } = use(props.params);
  const [student, setStudent] = useState<StudentDetail | null>(null);
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<StudentDetail>(`/students/${id}`),
      apiFetch<Attendance[]>(`/students/${id}/attendance`),
      apiFetch<Assessment[]>(`/students/${id}/assessments`),
    ])
      .then(([s, a, as_]) => {
        setStudent(s);
        setAttendance(a);
        setAssessments(as_);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="animate-pulse text-slate-400 py-8">Loading student data...</div>;
  if (!student) return <p className="text-red-500">Student not found</p>;

  // Attendance summary
  const attPresent = attendance.filter((a) => a.status === "present" || a.status === "late").length;
  const attAbsent = attendance.filter((a) => a.status === "absent").length;
  const attTotal = attendance.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <a href="/students" className="text-sm text-[#0ea5e9] hover:underline">← Back to Students</a>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              {student.first_name} {student.last_name}
            </h1>
            <div className="flex gap-4 mt-2 text-sm text-slate-500">
              <span>Code: {student.student_code || "—"}</span>
              <span>Program: {student.program_name || "—"}</span>
              <span>Semester: {student.current_semester || "—"}</span>
              <span>GPA: {student.current_gpa?.toFixed(2) || "—"}</span>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-lg text-sm font-medium ${student.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {student.is_active ? "Active" : "Dropped"}
          </span>
        </div>
      </div>

      {/* Risk Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`rounded-lg p-5 ${riskColor(student.dropout_risk)}`}>
          <p className="text-sm font-medium opacity-80">Dropout Risk</p>
          <p className="text-3xl font-bold mt-1">{student.dropout_risk?.toFixed(0) || "—"}<span className="text-lg">/100</span></p>
          <p className="text-xs mt-1 opacity-70">
            {(student.dropout_risk || 0) >= 70 ? "High risk — immediate attention needed" :
             (student.dropout_risk || 0) >= 40 ? "Medium risk — monitor closely" : "Low risk"}
          </p>
        </div>
        <div className={`rounded-lg p-5 ${riskColor(student.performance_risk)}`}>
          <p className="text-sm font-medium opacity-80">Performance Risk</p>
          <p className="text-3xl font-bold mt-1">{student.performance_risk?.toFixed(0) || "—"}<span className="text-lg">/100</span></p>
          <p className="text-xs mt-1 opacity-70">GPA trend: {student.gpa_trend || "unknown"}</p>
        </div>
        <div className="bg-white rounded-lg p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Attendance Rate</p>
          <p className="text-3xl font-bold text-slate-800 mt-1">{student.attendance_rate?.toFixed(1) || "—"}%</p>
          <p className="text-xs text-slate-400 mt-1">{attPresent} present, {attAbsent} absent of {attTotal} sessions</p>
        </div>
      </div>

      {/* Risk Factors */}
      {student.risk_factors && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Risk Factors</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(student.risk_factors).map(([key, value]) => (
              <div key={key} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 capitalize">{key.replace(/_/g, " ")}</p>
                <p className="text-sm font-semibold text-slate-700 mt-1">
                  {value !== null && value !== undefined ? String(typeof value === "number" ? value.toFixed(1) : value) : "N/A"}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assessments */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Assessments ({assessments.length})</h2>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="text-left px-3 py-2 font-medium text-slate-600">Course</th>
              <th className="text-left px-3 py-2 font-medium text-slate-600">Type</th>
              <th className="text-right px-3 py-2 font-medium text-slate-600">Score</th>
              <th className="text-center px-3 py-2 font-medium text-slate-600">Grade</th>
              <th className="text-right px-3 py-2 font-medium text-slate-600">Date</th>
            </tr>
          </thead>
          <tbody>
            {assessments.slice(0, 20).map((a) => (
              <tr key={a.id} className="border-b border-slate-50">
                <td className="px-3 py-2 text-slate-700">{a.course_name || "—"}</td>
                <td className="px-3 py-2 text-slate-500 capitalize">{a.type}</td>
                <td className="px-3 py-2 text-right">{a.score?.toFixed(1) || "—"} / {a.max_score}</td>
                <td className="px-3 py-2 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    a.grade === "A" ? "bg-green-100 text-green-700" :
                    a.grade === "B" ? "bg-blue-100 text-blue-700" :
                    a.grade === "C" ? "bg-amber-100 text-amber-700" :
                    "bg-red-100 text-red-700"
                  }`}>{a.grade || "—"}</span>
                </td>
                <td className="px-3 py-2 text-right text-slate-500">{a.assessed_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
