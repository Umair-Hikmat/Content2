"""
Streamlit Web Interface for Quiz Studio.
Run with: streamlit run app.py
"""

from pathlib import Path
import tempfile
import streamlit as st
from PIL import Image

# Core Pipeline Imports
from project import QuizProject, TimelineScene
from models import Option
from templates import TemplateRegistry
from quiz_import import QuizImporter
from export_video import VideoExporter
from ai_generator import AIGenerator

# Force template registration on startup
import template_trivia
import template_emoji
import template_fillblank
import template_logo
import template_flag


# Page Configuration
st.set_page_config(
    page_title="Quiz Studio Web",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    if "project" not in st_state_keys():
        st.session_state.project = QuizProject(title="Streamlit Quiz Project")
        # Default starting scene
        st.session_state.project.add_scene(
            TimelineScene(
                template_name="General Trivia",
                question_text="What is the capital of France?",
                correct_answer="Paris",
                options=[
                    Option(text="London", is_correct=False),
                    Option(text="Paris", is_correct=True),
                    Option(text="Berlin", is_correct=False),
                    Option(text="Madrid", is_correct=False),
                ],
                explanation_text="Paris has been the capital of France since 987 AD.",
            )
        )
    if "active_scene_idx" not in st.session_state:
        st.session_state.active_scene_idx = 0


def st_state_keys():
    return st.session_state.keys()


init_session_state()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Global Controls
# -----------------------------------------------------------------------------
st.sidebar.title("🎬 Quiz Studio")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Navigation Mode",
    ["Scene Editor & Preview", "Batch Import (Excel/CSV)", "AI Question Generator", "Export Video"],
)

st.sidebar.markdown("---")

# Project Summary Info
scene_count = len(st.session_state.project.scenes)
total_duration = st.session_state.project.total_duration
st.sidebar.metric("Total Scenes", scene_count)
st.sidebar.metric("Total Video Length", f"{total_duration:.1f} sec")


# -----------------------------------------------------------------------------
# MODE 1: Scene Editor & Real-Time Preview
# -----------------------------------------------------------------------------
if app_mode == "Scene Editor & Preview":
    st.header("✏️ Interactive Scene Editor")

    if scene_count == 0:
        st.info("No scenes in project. Click 'Add New Scene' in the sidebar.")
    else:
        col_controls, col_preview = st.columns([1, 1], gap="medium")

        # Select Scene to Edit
        scene_indices = list(range(scene_count))
        current_idx = st.selectbox(
            "Select Active Scene",
            options=scene_indices,
            format_func=lambda i: f"Scene {i + 1}: {st.session_state.project.scenes[i].question_text[:30]}...",
            index=st.session_state.active_scene_idx,
        )
        st.session_state.active_scene_idx = current_idx
        scene = st.session_state.project.scenes[current_idx]

        with col_controls:
            st.subheader("Scene Properties")

            # Template Selector
            available_templates = [
                "General Trivia",
                "Guess the Emoji",
                "Fill in the Blank",
                "Guess the Logo",
                "Guess the Flag",
            ]
            template_choice = st.selectbox(
                "Template",
                available_templates,
                index=available_templates.index(scene.template_name)
                if scene.template_name in available_templates
                else 0,
            )
            scene.template_name = template_choice

            # Question Text
            scene.question_text = st.text_area("Question / Prompt Text", value=scene.question_text)

            # Correct Answer
            scene.correct_answer = st.text_input("Correct Answer", value=scene.correct_answer)

            # Scene Duration
            scene.duration = st.slider("Duration (seconds)", 3.0, 15.0, value=float(scene.duration), step=0.5)

            # Explanation Text
            scene.explanation_text = st.text_input("Explanation / Reveal Note", value=scene.explanation_text)

            # Managing Options for Trivia
            if template_choice == "General Trivia":
                st.markdown("**Multiple Choice Options**")
                for i in range(4):
                    opt_text = scene.options[i].text if i < len(scene.options) else ""
                    new_opt_text = st.text_input(f"Option {chr(65+i)}", value=opt_text, key=f"opt_{current_idx}_{i}")
                    
                    is_corr = (new_opt_text.strip().lower() == scene.correct_answer.strip().lower())
                    if i < len(scene.options):
                        scene.options[i].text = new_opt_text
                        scene.options[i].is_correct = is_corr
                    else:
                        scene.options.append(Option(text=new_opt_text, is_correct=is_corr))

            # Delete Scene Button
            if st.button("🗑️ Delete Scene", type="secondary"):
                st.session_state.project.scenes.pop(current_idx)
                st.session_state.active_scene_idx = max(0, current_idx - 1)
                st.rerun()

        with col_preview:
            st.subheader("Frame Preview")
            
            # Preview Time Scrubbing
            preview_time = st.slider(
                "Preview Timeline (seconds)",
                0.0,
                float(scene.duration),
                value=1.0,
                step=0.2,
            )

            # Render frame using registered template engine
            template = TemplateRegistry.get(scene.template_name)
            res = st.session_state.project.resolution
            
            pil_frame = template.render_frame(
                scene=scene,
                time_sec=preview_time,
                resolution=res,
                palette=st.session_state.project.theme_palette,
            )

            # Convert RGBA preview to RGB composite
            bg_color = st.session_state.project.theme_palette.get("background", "#0F0F1A")
            composite_img = Image.new("RGB", res, bg_color)
            composite_img.paste(pil_frame, (0, 0), mask=pil_frame)

            st.image(composite_img, caption=f"Timestamp: {preview_time:.1f}s", use_container_width=True)

    st.markdown("---")
    if st.button("➕ Add New Scene"):
        st.session_state.project.add_scene(
            TimelineScene(
                template_name="General Trivia",
                question_text="New Question Prompt?",
                correct_answer="New Answer",
            )
        )
        st.session_state.active_scene_idx = len(st.session_state.project.scenes) - 1
        st.rerun()


# -----------------------------------------------------------------------------
# MODE 2: Excel / CSV Batch Import
# -----------------------------------------------------------------------------
elif app_mode == "Batch Import (Excel/CSV)":
    st.header("📊 Import Question Bank")
    st.write("Upload an Excel (`.xlsx`) or CSV (`.csv`) spreadsheet to generate a full timeline instantly.")

    uploaded_file = st.file_uploader("Choose spreadsheet file", type=["xlsx", "csv"])
    import_template = st.selectbox(
        "Apply Template to Imported Questions",
        ["General Trivia", "Guess the Emoji", "Fill in the Blank", "Guess the Logo", "Guess the Flag"],
    )

    if uploaded_file is not None:
        # Write bytes to temporary local file for pandas/openpyxl parser
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = Path(tmp.name)

        if st.button("🚀 Process & Overwrite Timeline"):
            try:
                imported_proj = QuizImporter.import_from_excel(tmp_path, template_name=import_template)
                st.session_state.project = imported_proj
                st.session_state.active_scene_idx = 0
                st.success(f"Successfully loaded {len(imported_proj.scenes)} scenes into project!")
            except Exception as e:
                st.error(f"Failed to import file: {e}")


# -----------------------------------------------------------------------------
# MODE 3: AI Question Generator
# -----------------------------------------------------------------------------
elif app_mode == "AI Question Generator":
    st.header("✨ AI Question Wizard")
    st.write("Generate structured questions using an LLM integration.")

    topic = st.text_input("Topic", value="World Geography")
    count = st.slider("Number of Questions", 1, 10, 5)
    difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")

    ai_gen = AIGenerator()
    prompt_text = ai_gen.build_prompt_for_topic(topic, count=count, difficulty=difficulty)

    with st.expander("Show AI System Prompt"):
        st.code(prompt_text, language="json")

    raw_json_input = st.text_area("Paste LLM JSON Response Here:", height=200)

    if st.button("Parse & Append to Timeline"):
        if raw_json_input.strip():
            try:
                parsed_q_list = ai_gen.parse_ai_response(raw_json_input)
                for q in parsed_q_list:
                    opts = [
                        Option(text=o["text"], is_correct=o.get("is_correct", False))
                        for o in q.get("options", [])
                    ]
                    scene = TimelineScene(
                        template_name="General Trivia",
                        duration=7.0,
                        question_text=q.get("question_text", ""),
                        correct_answer=q.get("correct_answer", ""),
                        options=opts,
                        explanation_text=q.get("explanation_text", ""),
                    )
                    st.session_state.project.add_scene(scene)
                st.success(f"Added {len(parsed_q_list)} new scenes from AI response!")
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")


# -----------------------------------------------------------------------------
# MODE 4: Video Export Engine
# -----------------------------------------------------------------------------
elif app_mode == "Export Video":
    st.header("🚀 Render & Export Video")

    if len(st.session_state.project.scenes) == 0:
        st.warning("Cannot render empty project. Add scenes first.")
    else:
        st.write(f"Ready to compile **{len(st.session_state.project.scenes)} scenes** into an MP4 video.")

        output_filename = st.text_input("Output Filename", value="quiz_short_video.mp4")

        if st.button("🎬 Start Video Rendering", type="primary"):
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def render_progress(ratio: float):
                progress_bar.progress(min(1.0, max(0.0, ratio)))
                status_text.text(f"Rendering frames... {int(ratio * 100)}%")

            # Create temp output path
            with tempfile.TemporaryDirectory() as tmpdir:
                out_file_path = Path(tmpdir) / output_filename
                
                exporter = VideoExporter(st.session_state.project)
                
                with st.spinner("Compiling audio and video tracks via FFmpeg..."):
                    rendered_path = exporter.render_to_file(out_file_path, progress_callback=render_progress)

                st.success("Render Complete!")

                # Provide native video playback and download button
                with open(rendered_path, "rb") as video_bytes:
                    v_data = video_bytes.read()
                    
                    st.video(v_data)
                    st.download_button(
                        label="💾 Download MP4 Video",
                        data=v_data,
                        file_name=output_filename,
                        mime="video/mp4",
                    )
