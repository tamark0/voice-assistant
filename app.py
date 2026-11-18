import traceback

import gradio as gr

from src.vsa import db, pipeline
from src.vsa.config import SIGNS_DIR

db.init_db()
MAX_SIGNS = 8


def hidden():
    return [gr.update(value=None, visible=False) for _ in range(MAX_SIGNS)]


async def handle(audio):
    try:
        if audio is None:
            return ("", "Record or upload audio first.", *hidden())
        text, signs, missing = await pipeline.run(audio)
        line = " → ".join(s["gloss"] for s in signs) or "(no matching signs)"
        if missing:
            line += f"   | not in vocabulary: {', '.join(missing)}"
        vids = [
            gr.update(value=signs[i]["video"], label=signs[i]["gloss"], visible=True)
            if i < len(signs) else gr.update(value=None, visible=False)
            for i in range(MAX_SIGNS)
        ]
        return (text, line, *vids)
    except Exception:
        tb = traceback.format_exc()
        print(tb)  # full traceback in the terminal
        return ("", "ERROR: " + tb.strip().splitlines()[-1], *hidden())


with gr.Blocks(title="Voice Sign Assistant") as demo:
    gr.Markdown("# Voice Sign Assistant (ASL MVP)")
    audio = gr.Audio(sources=["microphone", "upload"], type="filepath",
                     label="Speak or upload audio")
    btn = gr.Button("Translate", variant="primary")
    transcript = gr.Textbox(label="Transcript")
    glosses = gr.Textbox(label="Gloss sequence")
    with gr.Row():
        videos = [gr.Video(visible=False, height=240) for _ in range(MAX_SIGNS)]
    btn.click(handle, audio, [transcript, glosses, *videos])

demo.launch(allowed_paths=[str(SIGNS_DIR)])