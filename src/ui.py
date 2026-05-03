# -------- UI: Layout and Styling --------

import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes


# ---------------- Theme ----------------
class DarkSurveillanceTheme(Base):
    def __init__(self):
        super().__init__(
            primary_hue=colors.blue,
            secondary_hue=colors.slate,
            neutral_hue=colors.slate,
            spacing_size=sizes.spacing_md,
            radius_size=sizes.radius_md,
            text_size=sizes.text_md,
            font=fonts.GoogleFont("Inter"),
            font_mono=fonts.GoogleFont("IBM Plex Mono"),
        )
        super().set(
            # ── Page ──
            body_background_fill="#0d0f12",
            body_background_fill_dark="#0d0f12",
            body_text_color="#dde2ea",
            body_text_color_dark="#dde2ea",
            body_text_color_subdued="#7a8a9e",
            body_text_color_subdued_dark="#7a8a9e",

            # ── Containers ──
            background_fill_primary="#0d0f12",
            background_fill_primary_dark="#0d0f12",
            background_fill_secondary="#13161b",
            background_fill_secondary_dark="#13161b",

            # ── Blocks / panels ──
            block_background_fill="#13161b",
            block_background_fill_dark="#13161b",
            block_border_color="#252b36",
            block_border_color_dark="#252b36",
            block_border_width="1px",
            block_label_background_fill="#13161b",
            block_label_background_fill_dark="#13161b",
            block_label_text_color="#7a8a9e",
            block_label_text_color_dark="#7a8a9e",
            block_title_text_color="#7a8a9e",
            block_title_text_color_dark="#7a8a9e",
            block_shadow="none",

            # ── Panel ──
            panel_background_fill="#13161b",
            panel_background_fill_dark="#13161b",
            panel_border_color="#252b36",
            panel_border_color_dark="#252b36",

            # ── Inputs ──
            input_background_fill="#1a1e26",
            input_background_fill_dark="#1a1e26",
            input_border_color="#252b36",
            input_border_color_dark="#252b36",
            input_border_color_focus="#4a8fff",
            input_border_color_focus_dark="#4a8fff",
            input_border_width="1px",
            input_placeholder_color="#4a5a6e",
            input_placeholder_color_dark="#4a5a6e",
            input_shadow="none",
            input_shadow_focus="0 0 0 3px rgba(74,143,255,0.15)",

            # ── Buttons ──
            button_primary_background_fill="#1a1e26",
            button_primary_background_fill_dark="#1a1e26",
            button_primary_background_fill_hover="#21283a",
            button_primary_background_fill_hover_dark="#21283a",
            button_primary_border_color="#4a8fff",
            button_primary_border_color_dark="#4a8fff",
            button_primary_border_color_hover="#4a8fff",
            button_primary_border_color_hover_dark="#4a8fff",
            button_primary_text_color="#4a8fff",
            button_primary_text_color_dark="#4a8fff",
            button_primary_text_color_hover="#7aaaff",
            button_primary_text_color_hover_dark="#7aaaff",

            button_secondary_background_fill="#1a1e26",
            button_secondary_background_fill_dark="#1a1e26",
            button_secondary_background_fill_hover="#21283a",
            button_secondary_background_fill_hover_dark="#21283a",
            button_secondary_border_color="#252b36",
            button_secondary_border_color_dark="#252b36",
            button_secondary_border_color_hover="#4a8fff",
            button_secondary_border_color_hover_dark="#4a8fff",
            button_secondary_text_color="#dde2ea",
            button_secondary_text_color_dark="#dde2ea",

            # ── Borders ──
            border_color_primary="#252b36",
            border_color_primary_dark="#252b36",
            border_color_accent="#4a8fff",
            border_color_accent_dark="#4a8fff",

            # ── Table ──
            table_even_background_fill="#13161b",
            table_even_background_fill_dark="#13161b",
            table_odd_background_fill="#1a1e26",
            table_odd_background_fill_dark="#1a1e26",
            table_border_color="#252b36",
            table_border_color_dark="#252b36",

            # ── Misc ──
            shadow_drop="none",
            shadow_drop_lg="none",
            color_accent="#4a8fff",
            color_accent_soft="rgba(74,143,255,0.15)",
            color_accent_soft_dark="rgba(74,143,255,0.15)",
            link_text_color="#4a8fff",
            link_text_color_dark="#4a8fff",
            link_text_color_hover="#7aaaff",
            link_text_color_hover_dark="#7aaaff",
        )


# Minimal CSS only for the custom HTML header
header_css = """
.sia-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 18px;
    border-bottom: 1px solid #252b36;
    margin-bottom: 20px;
}
.sia-header-title {
    font-size: 17px;
    font-weight: 600;
    color: #dde2ea;
    font-family: Inter, sans-serif;
}
.sia-header-sub {
    font-size: 12px;
    color: #7a8a9e;
    margin-top: 3px;
    font-family: Inter, sans-serif;
}
"""


# ---------------- Layout ----------------
def build_ui(analyze_video_fn, query_logs_fn):
    """
    Builds and returns the Gradio Blocks app.
    Accepts backend functions as arguments to keep UI and logic decoupled.
    """
    theme = DarkSurveillanceTheme()

    with gr.Blocks(
        theme=theme,
        css=header_css,
        title="Surveillance Intelligence Analyzer"
    ) as app:

        current_video_state = gr.State(None)

        gr.HTML("""
            <div class="sia-header">
                <span style="font-size:22px;line-height:1">🛡</span>
                <div>
                    <div class="sia-header-title">Surveillance Intelligence Analyzer</div>
                    <div class="sia-header-sub">Florence-2 frame analysis · Gemini reasoning</div>
                </div>
            </div>
        """)

        with gr.Row():

            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### Ingest")
                    video_upload = gr.File(
                        label="Upload Video",
                        file_types=[".mp4", ".avi", ".mov"]
                    )
                    analyze_btn = gr.Button("Run Analysis", variant="primary")
                    analyze_output = gr.Textbox(
                        label="Status",
                        lines=3,
                        interactive=False,
                    )

                    analyze_btn.click(
                        analyze_video_fn,
                        inputs=video_upload,
                        outputs=[analyze_output, current_video_state],
                        show_progress=True
                    )

            with gr.Column(scale=2):
                with gr.Group():
                    gr.Markdown("### Query")
                    question = gr.Textbox(
                        label="Question",
                        placeholder="e.g. Identify suspicious activity, summarize key events...",
                        lines=3
                    )
                    ask_btn = gr.Button("Generate Report", variant="primary")
                    answer_output = gr.Textbox(
                        label="Report",
                        lines=20,
                        interactive=False
                    )

                    ask_btn.click(
                        query_logs_fn,
                        inputs=[question, current_video_state],
                        outputs=answer_output
                    )

    return app