# AI tools used in this project

## Summary

| Tool | Role |
|---|---|
| **Claude (Anthropic), chat interface** | Development assistant: architecture, code, debugging, documentation |
| **Whisper Small** via `faster-whisper` | Runtime component: speech-to-text, runs locally on CPU (INT8) |
| **Qwen3 8B** via Ollama | Runtime component: maps the transcript to sign glosses, runs locally |
| **Google ADK** | Agent framework that orchestrates the LLM and its tools (not a model itself) |

## 1. AI as a development assistant (Claude)

I gave Claude the project brief (local voice-to-ASL, Windows 11, 16 GB RAM, Python 3.12, `uv`, Ollama + Qwen3 8B, Whisper Small, Gradio, SQLite, Google ADK) and used it, over one long conversation, to:

- **Design the architecture:** Whisper → ADK agent with two tools (`get_vocabulary`, `lookup_signs`) → SQLite → Gradio. Claude proposed the split between the LLM (chooses glosses) and the database (the only source of sign videos).
- **Write the first version of the code:** all modules in `src/vsa/`, `app.py` and the setup commands.
- **Evaluate data sources:** I found two candidate repositories (SignBridge and SignAvatars). Claude read their READMEs and compared them against my constraints (simple, local, Python 3.12). It recommended SignBridge first, then dropped it after I couldn't get it to run and wanted fewer dependencies. SignAvatars was ruled out because it is 3D motion data with a heavy, old toolchain and restricted access. We then switched to extracting individual clips from the Kaggle version of WLASL.
- **Write helper scripts:** `scripts/build_assets.py` (extract clips from the zip) and `scripts/debug.py` (test each stage separately).
- **Debug errors I pasted into the chat:** the missing script path, `ModuleNotFoundError: No module named 'src'`, the browser microphone problem, a generic UI error (resolved by adding error reporting to `app.py` and replacing `gr.Gallery` with video players), and the PyAV issue below.
- **Write the documentation:** this file, `README.md` and the project write-up.

## 2. AI as part of the running application

- **Whisper Small** (through `faster-whisper`, CPU, INT8) transcribes microphone or uploaded audio.
- **Qwen3 8B** (served locally by Ollama, called through LiteLLM from Google ADK) receives the transcript and a vocabulary list, and returns an ordered list of glosses. Its instruction starts with `/no_think` to switch off Qwen3's reasoning mode and reduce latency, and the temperature is 0.1.
- **Guardrail:** the model can only choose from words returned by `get_vocabulary()`, and `lookup_signs` returns only clips that exist in SQLite, so the model cannot invent signs. Unknown words are reported as "not in vocabulary".
- No data leaves the machine at runtime. The only network use is one-off downloads (the Whisper weights, the Ollama model and the dataset).

## 3. Where the AI was wrong, and how it was resolved

- **Wrong diagnosis (PyAV).** Transcription failed with `open() got an unexpected keyword argument 'metadata_errors'`. Claude first said my PyAV was too old and suggested upgrading. That didn't help, and I reported that my version was already 19.0.2. Claude then searched the web, found that PyAV 19 (released 2026-09-29) *removed* that argument while `faster-whisper` 1.2.1 still passes it, acknowledged the earlier diagnosis was backwards, and recommended pinning `av` below 19 (`18.1.0`). That fixed it, and the pin is documented in `pyproject.toml` and the README.
- **A dependency that didn't work for me.** SignBridge was recommended but its `main.py` didn't run in my environment and pulled in many dependencies. I decided to simplify instead of debugging it.
- **Unverified assumptions.** Claude flagged where it had not verified something (for example, the dataset's internal layout and ADK API details across versions). I tested those on my machine, and the code in this repo is what ran successfully.

## 4. What I did myself

- Defined the requirements and constraints, and chose the stack.
- Chose the data source and made the decision to simplify (drop SignBridge, use the WLASL zip rather than API-based downloads).
- Ran, tested and debugged everything on my own machine, and reported the real errors back.
- Checked the final result end to end: spoken input produces the transcript, the gloss sequence and the sign clips.

## 5. Limits of AI use and verification

- Generated code was only trusted after I ran it. Nothing was merged without being executed.
- LLM output (glosses) is constrained by the database and checked against it; accuracy of the signs themselves depends on the WLASL clips, which I have not validated with ASL users.
- I did not use AI to generate any sign-language content. All clips are recordings from the WLASL dataset.
