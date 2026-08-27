# Career GPS AI (PathForge) - AI Prompt and Agent Log

This file documents how AI was used to develop the capstone and how the finished application calls language models. It is written for project review and presentation use. Do not add API keys, real resumes, transcripts, or private user data.

## 1. Development workflow: two AI agents

| Agent | Primary role | Representative prompt | Human responsibility |
| --- | --- | --- | --- |
| Claude Code | Requirements analysis, architecture planning, and design/code review | "Analyze the capstone requirements and propose a modular architecture for a career-planning agent. Keep extraction, deterministic tools, reasoning, and verification separate." | Chose the product direction, reviewed tradeoffs, accepted or rejected recommendations, and protected provider boundaries. |
| OpenAI Codex | Focused implementation, tests, debugging, and documentation | "Implement the provider-neutral career-plan flow with typed schemas, trace metadata, deterministic fallbacks, and backend tests. Preserve the BackgroundExtractor and CareerReasoner protocols." | Reviewed diffs, ran tests, validated behavior, and decided what shipped. |

The agents were used as junior collaborators. Product decisions, architecture ownership, verification, and final presentation choices remained human decisions.

## 2. Runtime LLM integration

Career GPS AI integrates LLMs directly through provider implementations behind two protocols:

- `BackgroundExtractor`: converts uploaded or pasted evidence into a typed career profile.
- `CareerReasoner`: combines the profile, career goal, deterministic tool outputs, and evidence into a typed career plan.

Supported modes include Gemini, OpenAI, local Qwen, a partner local HTTP service, hybrid fallback modes, and a deterministic fake provider for demos and tests. The application code depends on protocols and schemas rather than a single model vendor.

## 3. Core system prompts

### Background extraction

Source: `backend/app/providers/openai_provider.py`

```text
Extract a versioned CareerProfile from the submitted background.
Use only facts present in the artifact. Preserve uncertainty in warnings. Return JSON only.
```

Expected output: a schema-valid `BackgroundArtifactExtraction` containing extracted entities, evidence spans, confidence, and warnings.

### Career reasoning

Source: `backend/app/providers/openai_provider.py`

```text
You are PathForge AI, a career-navigation reasoner.
Synthesize the supplied profile, goal, deterministic tool outputs, and evidence into a typed CareerPlan.
Do not invent user skills or market facts. Use caveats for uncertainty. Return JSON only.
```

Expected output: a schema-valid `CareerPlan` containing recommended paths, strengths, gaps, actions, projects, evidence, caveats, and confidence.

### Local Qwen schema wrappers

Source: `backend/app/providers/qwen_provider.py`

```text
{EXTRACTION_PROMPT}
Return one JSON object that validates against this JSON schema:
{BackgroundArtifactExtraction JSON schema}
```

```text
{REASONING_PROMPT}
Return one JSON object only. It must validate against this JSON schema:
{CareerPlan JSON schema}
```

### Hosted extraction

Source: `frontend/worker/index.js`

```text
Extract a career profile JSON object with keys: education, experience, skills, projects,
certifications, interests, constraints, source_artifacts, extraction_confidence, warnings.
```

### Hosted reasoning

Source: `frontend/worker/index.js`

```text
Create a career plan JSON object with keys: recommended_paths, strengths, gaps, next_actions,
project_recommendations, evidence, caveats, overall_confidence. Keep every recommendation
practical and evidence-grounded.
```

The hosted JSON guard appends: `Return only valid JSON.`

## 4. User-facing background prompt

Source: `backend/app/services/document_intake.py` and `frontend/worker/index.js`

```text
Use the background below to evaluate career fit, identify role-specific evidence,
and recommend practical next steps.

Candidate Background
{Education}
{Experience}
{Projects}
{Skills}
{Certifications}
{Interests}
{Constraints}

Source Documents
- {filename} ({artifact_type})

Review Notes
- {warnings}
```

## 5. Guided intake questions

The app can build useful background evidence without requiring a resume:

1. What are you doing now?
2. What school, training, courses, certifications, or self-study have you completed?
3. What jobs, volunteer work, internships, or responsibilities have you had?
4. What skills, tools, software, languages, or strengths do you have?
5. What have you built, improved, organized, solved, or helped complete?
6. What kind of work, industries, or problems are you interested in?
7. What should the plan account for?
8. What else should the agent know about you?

## 6. Prompt-design decisions

- Schema-bound JSON makes outputs renderable, testable, and easier to verify.
- Extraction and reasoning are separate so facts can be reviewed before recommendations are generated.
- Deterministic tools create role evidence, gaps, project ideas, and next actions before the reasoner synthesizes the final plan.
- Prompts prohibit invented skills and route uncertainty into warnings and caveats.
- Trace fields preserve provider, latency, tool use, warnings, fallbacks, and routing metadata.

## 7. Verification and iteration

The automated evaluation covers five synthetic personas. The committed evaluation results show schema-valid outputs and six evidence citations per case; the deliberately ambiguous persona also triggers a verifier warning instead of silently presenting unsupported strengths.

Before presenting, run:

```powershell
python -m pytest backend/tests -q
python backend/scripts/evaluate.py --provider fake --output backend/evaluation/results.json
```

## 8. Safe-use rules

- Never commit API keys or `.env` files.
- Use synthetic or explicitly permitted documents in demos.
- Do not claim a skill unless the profile contains supporting evidence.
- Treat model output as a draft plan, not a guaranteed career outcome.
- Keep warnings, caveats, evidence, provider, and fallback trace visible.

