import gradio as gr
from query import ask


def handle_query(question):
    if not question.strip():
        return "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="Terraria Unofficial Guide") as demo:
    gr.Markdown("# Terraria Unofficial Guide\nAsk anything about Terraria game mechanics, items, bosses, and progression.")
    inp = gr.Textbox(label="Your question", placeholder="e.g. How do I summon the Eye of Cthulhu?")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
