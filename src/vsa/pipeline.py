import uuid
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from .agent import root_agent
from .config import APP_NAME
from .stt import transcribe

_sessions = InMemorySessionService()
_runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=_sessions)

async def run(audio_path: str):
    text = transcribe(audio_path)
    if not text:
        return "", [], []
    sid, uid = str(uuid.uuid4()), "local_user"   # fresh session per utterance
    await _sessions.create_session(app_name=APP_NAME, user_id=uid, session_id=sid)
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    async for _ in _runner.run_async(user_id=uid, session_id=sid, new_message=msg):
        pass
    session = await _sessions.get_session(app_name=APP_NAME, user_id=uid, session_id=sid)
    signs = session.state.get("signs", [])
    missing = session.state.get("missing", [])
    return text, signs, missing