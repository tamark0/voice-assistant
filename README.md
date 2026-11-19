# Voice Sign Assistant (ASL MVP)

A locally running app that turns **spoken English into American Sign Language (ASL) video clips**.
Speech recognition, the language model and the sign database all run on your own machine, with no external AI APIs.

```
Mic / audio file
   → Whisper Small (faster-whisper, CPU, INT8)      → transcript
   → Google ADK agent (Qwen3 8B via Ollama/LiteLLM)
        ├─ get_vocabulary()  ← SQLite
        └─ lookup_signs()    ← SQLite → stores clip paths in session state
   → Gradio page: transcript, gloss sequence, sign clips
```

**Scope of the MVP:** a small ASL vocabulary (about 24 words) of pre-recorded, single-word clips.
Output is a sequence of isolated signs, **not fluent ASL**, and it is not a substitute for an interpreter.
See `docs/WRITEUP.md` for the project write-up and `ai.md` for how AI tools were used.

## Tech stack

| Part | Choice |
|---|---|
| Speech-to-text | Whisper Small via `faster-whisper` (CPU, INT8) |
| LLM runtime / model | Ollama, Qwen3 8B |
| Agent framework | Google ADK (with LiteLLM for Ollama) |
| Database | SQLite (`data/signs.db`, created at startup) |
| UI | Gradio |
| Python / packages | 3.12, managed with `uv` |
| Tested on | Windows 11, 16 GB RAM, NVIDIA GPU |

## Requirements

- Windows 11 (the commands below are PowerShell; Linux/macOS should work with equivalent commands but are untested)
- [uv](https://docs.astral.sh/uv/) and Git
- [Ollama](https://ollama.com/) and roughly 6 GB of free VRAM for Qwen3 8B (less VRAM works, but it is slower)
- A free [Kaggle](https://www.kaggle.com/) account (to download the sign clips)
- A microphone, or an audio file to upload

## Setup

### 1. Get the code and install dependencies

```powershell
git clone <your-repo-url> voice-sign-assistant
cd voice-sign-assistant
uv sync
```

`uv sync` installs everything listed in `pyproject.toml`, including `av` pinned below version 19 (see Troubleshooting).

### 2. Install the language model

```powershell
winget install Ollama.Ollama
ollama pull qwen3:8b
ollama run qwen3:8b "hello"      # sanity check, then type /bye
```

### 3. Configure

```powershell
copy .env.example .env
```
The defaults work as they are. Edit `.env` to change the model or Whisper size.

### 4. Download the sign clips (not included in this repo)

The clips come from the **WLASL** dataset, which is licensed for computational use only (C-UDA), so they are not redistributed here.

1. Open https://www.kaggle.com/datasets/risangbaskoro/wlasl-processed (free Kaggle login), click **Download**, and save the file as **`data/wlasl-processed.zip`**. It is about 5 GB. Do not unzip it.
2. Check or edit the words in `data/starter_glosses.txt` (one word per line).
3. Extract one clip per word:
   ```powershell
   uv run python scripts/build_assets.py
   ```
   Words that are not in the dataset print as `MISSING`. Find alternatives with:
   ```powershell
   uv run python scripts/build_assets.py search thank
   ```
   The clips are copied to `assets/signs/` and are registered in the database at app startup. The file name is the gloss (`thank you` becomes `THANK_YOU.mp4`).

## Run

```powershell
ollama serve                 # skip if the Ollama tray app is already running
uv run python app.py
```

Open **http://127.0.0.1:7860** (use `127.0.0.1` or `localhost`; browsers block the microphone on other addresses), allow microphone access, record "Hello, thank you for the water" and click **Translate**.
You can also upload an audio file instead of using the microphone.

The first request is slow (about a minute) while Whisper downloads (~480 MB) and Qwen3 loads into memory. Later requests are much faster. Timings are printed in the terminal as `[timing] ...` lines.

Stop the app with **Ctrl+C** in the terminal.

## Project structure

```
app.py                     Gradio UI
src/vsa/config.py          paths and settings from .env
src/vsa/db.py              SQLite: signs + aliases, startup registration
src/vsa/stt.py             Whisper transcription
src/vsa/agent.py           ADK agent + tools (get_vocabulary, lookup_signs)
src/vsa/pipeline.py        audio → transcript → agent → signs
scripts/build_assets.py    extracts chosen clips from the WLASL zip
scripts/debug.py           tests the speech and agent stages separately
data/starter_glosses.txt   vocabulary list
assets/signs/              sign clips (ignored by git)
docs/WRITEUP.md            one-page project write-up
ai.md                      AI tools used and how
```

## Debugging a single stage

```powershell
uv run python scripts/debug.py stt C:\path\to\recording.wav
uv run python scripts/debug.py agent "Hello, thank you for the water"
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `TypeError: open() got an unexpected keyword argument 'metadata_errors'` | PyAV 19 removed an option that `faster-whisper` 1.2.x still uses. Keep `av<19` (already set in `pyproject.toml`): `uv add "av==18.1.0"`. |
| "Microphone not found" | Use http://127.0.0.1:7860, allow the mic in the browser, and check Windows **Settings → Privacy & security → Microphone**. Or upload an audio file. |
| Connection refused / `11434` | Ollama is not running. Start the app or run `ollama serve`. |
| `model 'qwen3:8b' not found` | `ollama pull qwen3:8b` |
| Slow requests after the first one | Run `ollama ps` and check it says `100% GPU`; otherwise try `qwen3:4b` (set `OLLAMA_MODEL=ollama_chat/qwen3:4b`) or `WHISPER_MODEL=base` in `.env`. |
| "unauthenticated requests to the HF Hub" | A warning only. Optionally set `HF_TOKEN` in `.env`. |
| `ModuleNotFoundError: No module named 'src'` | Run commands from the project root. `scripts/debug.py` handles its own path. |
| Gloss box shows "(no matching signs)" | Compare with the vocabulary printed by `scripts/debug.py`; add words or aliases (`db.py`). |
| Clips don't play | Re-encode with ffmpeg: `ffmpeg -i in.mp4 -c:v libx264 -pix_fmt yuv420p out.mp4` |

## Known limitations

- Isolated single-word clips from different signers, in English-like word order; no ASL grammar, facial expression or spatial referencing.
- Vocabulary of about 24 words. The full word list is passed to the LLM on every request, so it does not scale past roughly 100–150 words without a search tool.
- Small local models can occasionally skip a tool call; there is no fallback lookup yet.
- Not evaluated with Deaf or fluent ASL users.

## Roadmap

Continuous clip playback, a `search_signs` tool for larger vocabularies, ASL-aware gloss ordering and fingerspelling for unknown words, a consistent 3D avatar, automated tests, and replacing research-licensed clips with properly licensed recordings from Deaf signers.

## Licenses and data

- Project code: add your own license file before publishing (for example MIT).
- WLASL clips: Computational Use of Data Agreement (C-UDA). Used locally for this MVP; do not redistribute them or use them commercially without checking the terms.
- Third-party components (Whisper, Qwen3, Google ADK, Gradio, Ollama) keep their own licenses.
