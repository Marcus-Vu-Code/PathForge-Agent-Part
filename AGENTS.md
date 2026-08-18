# PathForge AI Agent Guidelines

- Preserve the `BackgroundExtractor` and `CareerReasoner` provider boundaries. The app should depend on protocols, not OpenAI or local model internals.
- Keep Pydantic schemas backward-compatible unless intentionally versioning `schema_version`.
- Never commit secrets, API keys, real resumes, or unnecessarily sensitive artifacts.
- Run backend tests before finishing meaningful changes: `python -m pytest backend/tests -q`.
- Prefer small focused changes that keep the fake provider and OpenAI/local provider modes working.
- Keep local multimodal and MoLE behavior behind HTTP clients. The model service owns adapters, routing, and PEFT/LoRA loading.
- Preserve trace fields for tools, evidence, latency, fallback, warnings, and routing metadata.

