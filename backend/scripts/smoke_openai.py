from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import Settings


async def main() -> None:
    settings = Settings()
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is not configured.")
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise SystemExit("Install dependencies first: pip install -r requirements.txt") from exc

    client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=20)
    response = await client.responses.create(
        model=settings.openai_model,
        input="Reply with only PATHFORGE_OK.",
    )
    print((response.output_text or "").strip())


if __name__ == "__main__":
    asyncio.run(main())

