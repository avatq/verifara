"use client";

import { useState } from "react";
import { EvidenceItem } from "@/types/evidence";

export function EvidenceDetailsPanel({ item }: { item: EvidenceItem }) {
  const [open, setOpen] = useState(false);
  const details = item.details as Record<string, any>;

  const rows: { label: string; value: string }[] = [];

  if (item.key === "metadata" && details.metadata) {
    const m = details.metadata;
    if (m.camera_make || m.camera_model) rows.push({ label: "الكاميرا", value: `${m.camera_make ?? ""} ${m.camera_model ?? ""}`.trim() });
    if (m.software) rows.push({ label: "البرنامج", value: m.software });
    if (m.datetime_original) rows.push({ label: "تاريخ الالتقاط", value: m.datetime_original });
    if (m.dimensions) rows.push({ label: "الأبعاد", value: m.dimensions });
    rows.push({ label: "بيانات GPS", value: m.gps_present ? "موجودة" : "غير موجودة" });
  }

  if (item.key === "forensics") {
    const ela = details.error_level_analysis;
    const noise = details.noise_consistency;
    if (ela?.cluster?.found) {
      rows.push({ label: "بقعة ELA مشبوهة", value: `${(ela.cluster.size_ratio * 100).toFixed(1)}% من المساحة، ${ela.cluster.touches_border ? "تلامس الحافة" : "داخلية"}` });
    }
    if (noise?.cluster?.found) {
      rows.push({ label: "بقعة ضوضاء مشبوهة", value: `${(noise.cluster.size_ratio * 100).toFixed(1)}% من المساحة، ${noise.cluster.touches_border ? "تلامس الحافة" : "داخلية"}` });
    }
    if (ela?.mean_error_level !== undefined) rows.push({ label: "متوسط خطأ الضغط (ELA)", value: String(ela.mean_error_level) });
  }

  if (item.key === "ai_analysis") {
    if (details.likely_source) rows.push({ label: "المصدر المرجَّح", value: `${details.likely_source} (${(details.likely_source_score * 100).toFixed(1)}%)` });
    if (details.model_type) rows.push({ label: "نوع النموذج", value: details.model_type });
    if (details.reasoning) rows.push({ label: "تفسير النموذج", value: details.reasoning });
  }

  if (item.key === "provenance") {
    if (details.digital_source_types?.length) rows.push({ label: "digitalSourceType", value: details.digital_source_types.join(", ") });
    if (details.claim_generator) rows.push({ label: "الأداة المُصدرة (claim_generator)", value: details.claim_generator });
    if (details.actions?.length) rows.push({ label: "الإجراءات المسجَّلة", value: details.actions.join(", ") });
  }

  const flags: string[] = details.flags ?? [];

  if (rows.length === 0 && flags.length === 0) return null;

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen(!open)}
        className="text-xs text-accent-violet hover:underline"
      >
        {open ? "إخفاء التفاصيل ▲" : "عرض التفاصيل الفنية الكاملة ▼"}
      </button>

      {open && (
        <div className="mt-2 space-y-2 rounded-lg bg-base-950/50 p-3 text-xs">
          {rows.length > 0 && (
            <table className="w-full">
              <tbody>
                {rows.map((r, idx) => (
                  <tr key={idx} className="border-b border-base-800 last:border-0">
                    <td className="py-1.5 pl-3 text-slate-500 whitespace-nowrap align-top">{r.label}</td>
                    <td className="py-1.5 text-slate-300 break-words">{r.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {flags.length > 0 && (
            <div className={rows.length > 0 ? "pt-2 border-t border-base-800" : ""}>
              <p className="text-slate-500 mb-1">ملاحظات مفصَّلة:</p>
              <ul className="space-y-1">
                {flags.map((f, idx) => (
                  <li key={idx} className="text-slate-300">• {f}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
