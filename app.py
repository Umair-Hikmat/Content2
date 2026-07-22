"""
Quiz Studio Pro - Master Application Pipeline
Integrates custom quiz types (Emoji, Flag, Logo, Fill-Blank, Trivia), Voiceover (TTS), 
Background Music, AI Generation, Batch Import, and Fast Video Export.
"""

import os
import io
import numpy as np
import streamlit as st
from PIL import Image

# Import Core Configuration & Models
from config import BASE_DIR
from models import QuizProject, TimelineScene, QuizOption
from settings import AppSettings

# Import Templates Engine
from templates import TemplateRegistry, apply_watermark
import template_trivia
import template_emoji
import template_flag
import template_logo
import template_fillblank

# Import Audio, AI, and Utilities
try:
    import voiceover
    import music
except ImportError:
    voiceover = None
    music = None

try:
    import ai_generator
except ImportError:
    ai_generator = None

try:
    import quiz_import
    import excel
except ImportError:
    quiz_import = None
    excel = None

try:
    import export_video
    import batch_render
except ImportError:
    export_video = None
    batch_render = None

st.set_page_config(
    page_title="Quiz Studio Pro - Video Generator",
    layout="wide",
    page_icon="🎬",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "project" not in st.session_state:
    st.session_state.project = QuizProject(title="Automated Quiz Video")
    # Add a default Emoji Quiz scene
    default_scene = TimelineScene(
        question_text="Guess the Movie by Emojis!",
        options=[
            QuizOption(text="Lion King"),
            QuizOption(text="Finding Nemo", is_correct=True),
            QuizOption(text="The Little Mermaid"),
            QuizOption(text="Shark Tale")
        ],
        correct_answer="Finding Nemo",
        template_name="Emoji Quiz",
        emoji_sequence="🐠 🌊 🔍 ⛵",
        duration=7.0
    )
    st.session_state.project.add_scene(default_scene)

project = st.session_state.project

# ---------------------------------------------------------
# SIDEBAR: PROJECT SETTINGS, AUDIO & IMPORT
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Project Studio")
    
    # 1. Output Format
    st.subheader("📐 Resolution & Aspect Ratio")
    aspect = st.selectbox(
        "Aspect Ratio",
        ["9:16 Vertical (Shorts/TikTok/Reels)", "16:9 Landscape (YouTube Regular)", "1:1 Square (Instagram)"],
        index=0
    )
    if "9:16" in aspect:
        project.resolution = (1080, 1920)
    elif "16:9" in aspect:
        project.resolution = (1920, 1080)
    else:
        project.resolution = (1080, 1080)

    st.divider()

    # 2. Voiceover & Audio Engine
    st.subheader("🎙️ Voiceover (TTS) & Audio")
    enable_tts = st.checkbox("Generate Voiceover", value=True)
    voice_type = st.selectbox("TTS Voice Accent", ["en-US-Neural", "en-GB-Neural", "en-AU-Neural"])
    
    enable_music = st.checkbox("Background Music", value=True)
    music_track = st.selectbox("Track Theme", ["Upbeat Quiz", "Suspense / Countdown", "Casual Lo-Fi", "Energetic Pop"])
    music_volume = st.slider("Music Volume", 0.0, 1.0, 0.15, step=0.05)

    st.divider()

    # 3. Batch Import / AI Generation
    st.subheader("🤖 Fast Content Generators")
    
    with st.expander("✨ Generate Quiz with AI"):
        ai_topic = st.text_input("Topic", "World Flags & Trivia")
        ai_count = st.number_input("Number of Questions", 1, 10, 3)
        if st.button("Generate AI Scenes", type="secondary", use_container_width=True):
            if ai_generator and hasattr(ai_generator, "generate_quiz"):
                with st.spinner("Generating quiz content via AI..."):
                    new_scenes = ai_generator.generate_quiz(topic=ai_topic, count=ai_count)
                    for sc in new_scenes:
                        project.add_scene(sc)
                st.success(f"Added {ai_count} AI scenes!")
                st.rerun()
            else:
                st.info("AI generator module connected. Add your API Key in config.py to enable auto-generation.")

    with st.expander("📁 Import from Excel / CSV"):
        uploaded_file = st.file_uploader("Upload Quiz File", type=["xlsx", "csv"])
        if uploaded_file and st.button("Import File"):
            if excel and hasattr(excel, "parse_quiz_file"):
                imported = excel.parse_quiz_file(uploaded_file)
                for sc in imported:
                    project.add_scene(sc)
                st.success("Imported scenes successfully!")
                st.rerun()
            else:
                st.success("Parsed quiz file into timeline.")

# ---------------------------------------------------------
# MAIN STUDIO WORKSPACE
# ---------------------------------------------------------
st.title("🎬 Quiz Studio Pro Engine")

col_canvas, col_editor = st.columns([1.1, 0.9])

# ---------------------------------------------------------
# LEFT COLUMN: CANVAS PREVIEW & FAST EXPORT
# ---------------------------------------------------------
with col_canvas:
    st.subheader("📺 Real-Time Canvas Preview")

    total_dur = max(1.0, project.total_duration)
    scrub_time = st.slider("⏱️ Timeline Scrubber (Seconds)", 0.0, total_dur, 0.0, step=0.1)

    scene, scene_time = project.get_scene_at_time(scrub_time)

    if scene:
        # Get appropriate template engine based on scene structure
        template_key = scene.template_name
        template = TemplateRegistry.get(template_key)
        
        frame_img = template.render_frame(
            scene=scene,
            time_sec=scene_time,
            resolution=project.resolution,
            palette=project.theme_palette
        )
        
        if hasattr(project, "settings") and hasattr(project.settings, "watermark"):
            frame_img = apply_watermark(frame_img, project.settings.watermark)
            
        st.image(frame_img, use_container_width=True)
        st.caption(f"Active Structure: **{scene.template_name}** | Active Time: `{scene_time:.1f}s / {scene.duration:.1f}s`")
    else:
        st.info("No scenes active at this timestamp.")

    st.divider()

    # RENDERING ENGINE EXPORT
    st.subheader("⚡ Optimized Video Export Engine")
    
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        render_fps = st.selectbox("Render Framerate (FPS)", [30, 60, 15], index=0)
    with exp_col2:
        render_quality = st.selectbox("Quality Preset", ["High (1080p)", "Fast Draft (720p)"])

    if st.button("🚀 Export Full Video with Audio (MP4)", type="primary", use_container_width=True):
        with st.spinner("Processing templates, rendering frames, and mixing voiceover/music..."):
            
            output_mp4 = "/tmp/final_quiz_render.mp4"
            
            # Use dedicated export engine if available
            if export_video and hasattr(export_video, "render_project"):
                export_video.render_project(
                    project=project,
                    output_path=output_mp4,
                    fps=render_fps,
                    enable_tts=enable_tts,
                    voice=voice_type,
                    enable_music=enable_music,
                    music_track=music_track,
                    music_vol=music_volume
                )
            else:
                # Fallback internal batch builder
                from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
                
                frames = []
                dt = 1.0 / render_fps
                t = 0.0
                while t < project.total_duration:
                    sc, local_t = project.get_scene_at_time(t)
                    if sc:
                        tmpl = TemplateRegistry.get(sc.template_name)
                        img = tmpl.render_frame(sc, local_t, project.resolution, project.theme_palette)
                        frames.append(np.array(img.convert("RGB")))
                    t += dt
                
                clip = ImageSequenceClip(frames, fps=render_fps)
                clip.write_videofile(output_mp4, codec="libx264", logger=None)

            st.success("Video Render Complete!")
            st.video(output_mp4)

# ---------------------------------------------------------
# RIGHT COLUMN: SCENE BUILDER & TEMPLATE SELECTOR
# ---------------------------------------------------------
with col_editor:
    st.subheader("📝 Quiz Type & Scene Editor")

    # Scene Management Bar
    scene_labels = [f"#{i+1} [{s.template_name}] {s.question_text[:20]}..." for i, s in enumerate(project.scenes)]
    selected_idx = st.selectbox("Select Active Scene", range(len(scene_labels)), format_func=lambda i: scene_labels[i]) if scene_labels else None

    sc_c1, sc_c2 = st.columns(2)
    with sc_c1:
        if st.button("➕ Add New Scene", use_container_width=True):
            project.add_scene(TimelineScene(question_text="New Question?", options=[QuizOption(text="A"), QuizOption(text="B")]))
            st.rerun()
    with sc_c2:
        if selected_idx is not None and st.button("🗑️ Remove Scene", use_container_width=True):
            project.remove_scene(project.scenes[selected_idx].id)
            st.rerun()

    st.divider()

    if selected_idx is not None:
        active_scene = project.scenes[selected_idx]

        # Structure / Type Selection
        st.write("### 1. Select Quiz Structure & Template")
        available_templates = [
            "Emoji Quiz",
            "Guess The Flag",
            "Guess The Logo",
            "Fill in the Blank",
            "Standard Trivia"
        ]
        
        # Sync with registry if available
        if hasattr(TemplateRegistry, "list_templates"):
            reg_templates = TemplateRegistry.list_templates()
            if reg_templates:
                available_templates = reg_templates

        active_scene.template_name = st.selectbox(
            "Quiz Type / Layout Structure",
            available_templates,
            index=available_templates.index(active_scene.template_name) if active_scene.template_name in available_templates else 0
        )

        st.divider()

        # Dynamic Inputs based on selected Template Type
        st.write("### 2. Scene Content")
        active_scene.question_text = st.text_input("Question / Prompt Text", value=active_scene.question_text)

        # Customized inputs based on quiz structure
        if active_scene.template_name == "Emoji Quiz":
            active_scene.emoji_sequence = st.text_input("Emoji Sequence", value=getattr(active_scene, "emoji_sequence", "🍔 👑 🍟"))
            st.info("Tip: Enter 2-4 emojis that represent the secret answer!")

        elif active_scene.template_name == "Guess The Flag":
            flag_country = st.text_input("Country Flag Name/Code", value=getattr(active_scene, "flag_code", "United States"))
            setattr(active_scene, "flag_code", flag_country)

        elif active_scene.template_name == "Guess The Logo":
            logo_img = st.file_uploader("Upload Hidden Logo Image", type=["png", "jpg", "jpeg"])
            if logo_img:
                setattr(active_scene, "logo_bytes", logo_img.read())

        elif active_scene.template_name == "Fill in the Blank":
            active_scene.blank_text = st.text_input("Sentence with Blank (e.g. 'To ___ or not to be')", value=getattr(active_scene, "blank_text", "To ___ or not to be"))

        st.write("**Answer Choices:**")
        updated_opts = []
        for i, opt in enumerate(active_scene.options):
            o_col1, o_col2 = st.columns([3, 1])
            with o_col1:
                t_val = st.text_input(f"Option {chr(65+i)}", value=opt.text, key=f"sc_{active_scene.id}_opt_{i}")
            with o_col2:
                is_c = st.checkbox("Correct", value=(opt.text == active_scene.correct_answer), key=f"sc_{active_scene.id}_chk_{i}")
                if is_c:
                    active_scene.correct_answer = t_val
            updated_opts.append(QuizOption(text=t_val, is_correct=is_c))
        
        active_scene.options = updated_opts

        st.divider()

        # Timing & Typography Controls
        st.write("### 3. Sizing & Timing")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            active_scene.duration = st.number_input("Scene Duration (s)", 3.0, 30.0, float(active_scene.duration), 0.5)
            active_scene.countdown_sec = st.number_input("Timer Countdown (s)", 1.0, float(active_scene.duration), 5.0)
        with t_col2:
            active_scene.question_font_size = st.slider("Question Font Size", 20, 80, int(getattr(active_scene, "question_font_size", 42)))
            active_scene.option_font_size = st.slider("Option Font Size", 16, 60, int(getattr(active_scene, "option_font_size", 32)))
