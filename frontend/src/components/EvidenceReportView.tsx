import { EvidenceReport } from "@/types/evidence";
import { EvidenceBadge } from "./EvidenceBadge";

export function EvidenceReportView({ report }: { report: EvidenceReport }) {
  return (
    <div className="space-y-6">
      {/* التقييم العام */}
      <div className="rounded-2xl border border-base-700 bg-base-900 p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">التقييم العام</p>
            <h2 className="font-display text-2xl font-bold text-slate-100 mt-1">
              {report.overall_assessment}
            </h2>
          </div>
          <div className="text-right">
            <p className="text-xs uppercase tracking-wide text-slate-500">مستوى الثقة</p>
            <p className="font-display text-3xl font-extrabold bg-gradient-to-l from-accent-violet to-accent-blue bg-clip-text text-transparent">
              {report.evidence_confidence}%
            </p>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">
          <span>نوع الملف: {report.file_type}</span>
          <span className="font-mono">SHA-256: {report.file_hash.slice(0, 16)}…</span>
        </div>
      </div>

      {/* Evidence Scorecard */}
      <div className="grid gap-4 sm:grid-cols-2">
        {report.items.map((item) => (
          <div key={item.key} className="rounded-xl border border-base-700 bg-base-900 p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-200">{item.label}</h3>
              <EvidenceBadge level={item.level} />
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">{item.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
