export type CareerProfile = {
  schema_version: string;
  education: Array<Record<string, unknown>>;
  experience: Array<Record<string, unknown>>;
  skills: string[];
  projects: Array<Record<string, unknown>>;
  certifications: string[];
  interests: string[];
  constraints: Record<string, unknown>;
  source_artifacts: Array<Record<string, unknown>>;
};

export type CareerGoal = {
  target_role: string;
  target_sector?: string | null;
  target_function?: string | null;
  horizon_months: number;
  priorities: string[];
};

export type ProviderMode =
  | "fake"
  | "openai"
  | "gemini"
  | "qwen"
  | "local"
  | "hybrid-local-first"
  | "hybrid-openai-first"
  | "hybrid-gemini-first";

export type SelectOption = {
  value: string;
  label: string;
  description?: string | null;
};

export type RoleOption = SelectOption & {
  specializations: string[];
};

export type SectorOption = SelectOption & {
  roles: RoleOption[];
};

export type IntelligentSystemOption = SelectOption & {
  provider_mode: ProviderMode;
  configured: boolean;
};

export type ProviderOptionsResponse = {
  default_provider_mode: ProviderMode;
  intelligent_systems: IntelligentSystemOption[];
  sectors: SectorOption[];
  specializations: SelectOption[];
};

export type BackgroundPromptResponse = {
  background_prompt: string;
  profile: CareerProfile;
  extraction: {
    extraction_confidence: number;
    warnings: string[];
  };
  sources: Array<{
    filename: string;
    artifact_type: string;
    content_type: string;
    character_count: number;
  }>;
  warnings: string[];
};

export type CareerPlanResponse = {
  run_id: string;
  profile_id?: string | null;
  created_at: string;
  plan: {
    recommended_paths: Array<{ title: string; rationale: string; fit_summary: string; confidence: number }>;
    strengths: string[];
    gaps: Array<{ skill: string; reason: string; relevance: number; evidence_count: number; supporting_evidence_ids?: string[] }>;
    next_actions: Array<{ title: string; rationale: string; impact: number; effort: number; priority: number; constraint_notes?: string[] }>;
    project_recommendations: Array<{ title: string; description: string; addressed_gaps: string[]; expected_artifacts?: string[]; estimated_weeks?: number }>;
    evidence: Array<{ claim: string; source_title: string; source_url?: string | null; extracted_requirement?: string | null }>;
    caveats: string[];
    overall_confidence: number;
  };
  trace: {
    provider: string;
    model_version?: string | null;
    tools_called: string[];
    evidence_ids: string[];
    latency_ms: number;
    fallback_events: string[];
    routing_trace?: unknown;
    warnings: string[];
  };
};
