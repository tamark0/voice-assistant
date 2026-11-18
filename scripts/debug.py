"""Test each stage on its own.
  uv run python scripts/debug.py stt path\\to\\audio.wav
  uv run python scripts/debug.py agent "Hello, thank you for the water"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # must come first

import asyncio
import traceback

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.vsa import db
from src.vsa.agent import root_agent
from src.vsa.config import APP_NAME
from src.vsa.stt import transcribe

db.init_db()
print("Vocabulary:", db.vocabulary())

mode, arg = sys.argv[1], sys.argv[2]

if mode == "stt":
    try:
        print("Transcript:", repr(transcribe(arg)))
    except Exception:
        traceback.print_exc()

elif mode == "agent":
    async def go():
        svc = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=svc)
        await svc.create_session(app_name=APP_NAME, user_id="u", session_id="s")
        msg = types.Content(role="user", parts=[types.Part(text=arg)])
        async for ev in runner.run_async(user_id="u", session_id="s", new_message=msg):
            print("EVENT:", ev.content)
        s = await svc.get_session(app_name=APP_NAME, user_id="u", session_id="s")
        print("STATE:", dict(s.state))
    try:
        asyncio.run(go())
    except Exception:
        traceback.print_exc()