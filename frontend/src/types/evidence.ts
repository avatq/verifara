// يطابق تمامًا EvidenceReport.to_dict() من backend/app/services/evidence_engine.py
// أي تغيير هنا يجب أن يقابله تغيير مطابق في الـ backend والعكس صحيح.

export type EvidenceLevel = "good" | "minor" | "low" | "na" | "conflict";

export interface EvidenceItem {
  key: string;
  label: string;
  level: EvidenceLevel;
  summary: string;
  details: Record<string, unknown>;
}

export interface EvidenceReport {
  file_hash: string;
  file_type: "image" | "document" | "video" | "audio";
  overall_assessment: string;
  evidence_confidence: number;
  items: EvidenceItem[];
}

export interface ApiError {
  detail: string;
}
