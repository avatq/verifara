export type EvidenceLevel = "good" | "minor" | "low" | "na" | "conflict";
export type Verdict = "not_ai" | "ai_generated" | "inconclusive";

export interface EvidenceItem {
  key: string;
  label: string;
  level: EvidenceLevel;
  summary: string;
  details: Record<string, unknown>;
  score_percent: number | null;
}

export interface EvidenceReport {
  file_hash: string;
  file_type: "image" | "document" | "video" | "audio";
  overall_assessment: string;
  evidence_confidence: number;
  verdict: Verdict;
  verdict_label: string;
  confidence_label: string;
  items: EvidenceItem[];
}

export interface ApiError {
  detail: string;
}
