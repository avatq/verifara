import { EvidenceLevel } from "@/types/evidence";

const LEVEL_CONFIG: Record<EvidenceLevel, { label: string; dot: string; text: string }> = {
  good: { label: "جيد", dot: "bg-status-good", text: "text-status-good" },
  minor: { label: "ملاحظة بسيطة", dot: "bg-status-minor", text: "text-status-minor" },
  low: { label: "إشارة ضعيفة", dot: "bg-status-low", text: "text-status-low" },
  conflict: { label: "تعارض", dot: "bg-status-conflict", text: "text-status-conflict" },
  na: { label: "غير قابل للتطبيق", dot: "bg-status-na", text: "text-status-na" },
};

export function EvidenceBadge({ level }: { level: EvidenceLevel }) {
  const cfg = LEVEL_CONFIG[level];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${cfg.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} aria-hidden />
      {cfg.label}
    </span>
  );
}
