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
    if not settings.gemini_api_key:
        raise SystemExit("GEMINI_API_KEY is not configured.")
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise SystemExit("Install dependencies first: pip install -r requirements.txt") from exc

    client = AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_base_url,
        timeout=20,
    )
    response = await client.chat.completions.create(
        model=settings.gemini_model,
        messages=[{"role": "user", "content": "Reply with only PATHFORGE_GEMINI_OK."}],
    )
    print((response.choices[0].message.content or "").strip())


if __name__ == "__main__":
    asyncio.run(main())

