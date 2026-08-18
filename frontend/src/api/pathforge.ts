import type {
  BackgroundPromptResponse,
  CareerGoal,
  CareerPlanResponse,
  CareerProfile,
  ProviderMode,
  ProviderOptionsResponse,
  SelectOption
} from "../types/pathforge";

const localApiBase =
  typeof window !== "undefined" && ["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://localhost:8000"
    : "";
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? localApiBase;

async function check<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? `Request failed with ${response.status}`);
  }
  return response.json();
}

export async function getProviderOptions(): Promise<ProviderOptionsResponse> {
  return check(await fetch(`${API_BASE}/api/provider-options`));
}

export async function getGoalSpecializations(sector: string, targetRole: string): Promise<SelectOption[]> {
  const params = new URLSearchParams({ sector, target_role: targetRole });
  return check(await fetch(`${API_BASE}/api/goal-specializations?${params.toString()}`));
}

export async function extractProfile(backgroundText: string, providerMode: ProviderMode): Promise<{ profile: CareerProfile }> {
  const form = new FormData();
  form.set("background_text", backgroundText);
  form.set("artifact_type", "resume");
  form.set("provider_mode", providerMode);
  return check(await fetch(`${API_BASE}/api/profiles/extract`, { method: "POST", body: form }));
}

export async function createBackgroundPrompt(files: File[], providerMode: ProviderMode): Promise<BackgroundPromptResponse> {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  form.set("provider_mode", providerMode);
  return check(await fetch(`${API_BASE}/api/background-prompt`, { method: "POST", body: form }));
}

export async function createProfile(profile: CareerProfile): Promise<{ id: string; profile: CareerProfile }> {
  return check(await fetch(`${API_BASE}/api/profiles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile)
  }));
}

export async function createCareerPlan(profile: CareerProfile, goal: CareerGoal, providerMode: ProviderMode): Promise<CareerPlanResponse> {
  return check(await fetch(`${API_BASE}/api/career-plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, goal, provider_mode: providerMode })
  }));
}
