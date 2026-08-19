import { EvidenceReport } from "@/types/evidence";
import { EvidenceBadge } from "./EvidenceBadge";
import { VerdictCard } from "./VerdictCard";

export function EvidenceReportView({ report }: { report: EvidenceReport }) {
  return (
    <div className="space-y-6">
      <VerdictCard report={report} />

      <div className="rounded-xl border border-base-700 bg-base-900 p-4">
        <div className="flex flex-wrap gap-4 text-xs text-slate-500">
          <span>نوع الملف: {report.file_type}</span>
          <span className="font-mono">SHA-256: {report.file_hash.slice(0, 16)}…</span>
          <span>التقييم التفصيلي: {report.overall_assessment}</span>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {report.items.map((item) => (
          <div key={item.key} className="rounded-xl border border-base-700 bg-base-900 p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-200">{item.label}</h3>
              <div className="flex items-center gap-2">
                {item.score_percent !== null && (
                  <span className="text-xs font-mono text-slate-500">
                    {item.score_percent}%
                  </span>
                )}
                <EvidenceBadge level={item.level} />
              </div>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">{item.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
