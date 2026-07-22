"""
Streamlit Quiz Studio Application with User-Friendly Editor.
"""

import streamlit as st
from PIL import Image

from project import QuizProject, TimelineScene, QuizOption
from templates import TemplateRegistry, apply_watermark

st.set_page_config(page_title="Quiz Studio Pro", layout="wide", page_icon="🎬")

# Initialize Project in Session State
if "project" not in st.session_state:
    project = QuizProject(title="My Trivia Video")
    # Add initial sample scene
    project.add_scene(
        question_text="What is the capital of France?",
        options=[QuizOption(text="Berlin"), QuizOption(text="Paris", is_correct=True), QuizOption(text="Madrid"), QuizOption(text="Rome")],
        correct_answer="Paris",
        voice_over_text="What is the capital of France?"
    )
    st.session_state.project = project

project = st.session_state.project

st.title("🎬 Quiz Studio Editor")

# --- TOP TOOLBAR & PREVIEW SECTION ---
col_preview, col_editor = st.columns([1, 1])

with col_preview:
    st.subheader("📺 Live Video Canvas Preview")
    
    # Timeline Scrubbing Slider
    total_dur = max(1.0, project.total_duration)
    scrub_time = st.slider("⏱️ Scrub Timeline (Seconds)", 0.0, total_dur, 0.0, step=0.2)
    
    # Render Preview Frame at Scrubbed Timestamp
    scene, scene_local_time = project.get_scene_at_time(scrub_time)
    if scene:
        template = TemplateRegistry.get(scene.template_name)
        frame_img = template.render_frame(
            scene=scene,
            time_sec=scene_local_time,
            resolution=project.resolution,
            palette=project.theme_palette
        )
        frame_img = apply_watermark(frame_img, project.settings.watermark)
        st.image(frame_img, use_container_width=True)
        st.caption(f"Scene ID: `{scene.id}` | Scene Time: {scene_local_time:.1f}s / {scene.duration:.1f}s")
    else:
        st.info("No scenes found in timeline. Add a scene to start!")

# --- RIGHT SIDE EDITOR PANEL ---
with col_editor:
    st.subheader("⚙️ Studio Control Panel")

    # Timeline Selector Buttons
    scene_titles = [f"Scene {i+1}: {s.question_text[:25]}..." for i, s in enumerate(project.scenes)]
    selected_idx = st.selectbox("Select Active Scene", range(len(scene_titles)), format_func=lambda i: scene_titles[i]) if scene_titles else None

    # Global Add / Remove Buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ Add New Scene", use_container_width=True):
            project.add_scene(
                question_text="New Question?",
                options=[QuizOption(text="Option A"), QuizOption(text="Option B")],
                correct_answer="Option A"
            )
            st.rerun()
    with col_b:
        if selected_idx is not None and st.button("🗑️ Delete Current Scene", use_container_width=True):
            project.remove_scene(project.scenes[selected_idx].id)
            st.rerun()

    st.divider()

    if selected_idx is not None:
        active_scene = project.scenes[selected_idx]

        tab_content, tab_voice, tab_style, tab_global = st.tabs([
            "📝 Question Content", "🎙️ Voiceover & Audio", "🎨 Background & Fonts", "🛡️ Watermark & Video"
        ])

        # --- TAB 1: QUESTION CONTENT ---
        with tab_content:
            active_scene.question_text = st.text_input("Question Text", value=active_scene.question_text)
            active_scene.template_name = st.selectbox("Quiz Template", TemplateRegistry.list_templates(), index=0)
            active_scene.duration = st.number_input("Scene Duration (Seconds)", min_value=1.0, max_value=60.0, value=float(active_scene.duration), step=0.5)

            st.write("**Multiple Choice Options:**")
            updated_options = []
            for i, opt in enumerate(active_scene.options):
                c1, c2 = st.columns([3, 1])
                with c1:
                    txt = st.text_input(f"Option {chr(65+i)}", value=opt.text, key=f"opt_txt_{active_scene.id}_{i}")
                with c2:
                    is_corr = st.checkbox("Correct", value=(opt.text == active_scene.correct_answer), key=f"opt_corr_{active_scene.id}_{i}")
                    if is_corr:
                        active_scene.correct_answer = txt
                updated_options.append(QuizOption(text=txt, is_correct=is_corr))
            active_scene.options = updated_options

        # --- TAB 2: VOICEOVER & AUDIO SYNTHESIS ---
        with tab_voice:
            active_scene.voice_over_text = st.text_area("Voiceover Text (TTS Script)", value=active_scene.voice_over_text)
            active_scene.voice_provider = st.selectbox("Voice Engine Provider", ["Edge TTS", "ElevenLabs", "Custom Voice Clone"], index=0)

            if active_scene.voice_provider in ["ElevenLabs", "Custom Voice Clone"]:
                active_scene.voice_clone_id = st.text_input("Voice Model / Clone ID", value=active_scene.voice_clone_id, placeholder="e.g. 21m00Tcm4TlvDq8ikWAM")
            else:
                active_scene.voice_name = st.selectbox("Voice Model", ["en-US-ChristopherNeural", "en-US-JennyNeural", "en-GB-SoniaNeural"], index=0)

            v_col1, v_col2 = st.columns(2)
            with v_col1:
                active_scene.voice_speed = st.slider("Speech Speed Multiplier", 0.5, 2.0, float(active_scene.voice_speed), 0.1)
            with v_col2:
                active_scene.voice_pitch = st.slider("Voice Pitch Shift", 0.5, 1.5, float(active_scene.voice_pitch), 0.1)

            st.subheader("🎵 Background Music")
            active_scene.music_volume = st.slider("Music Volume", 0.0, 1.0, float(active_scene.music_volume), 0.05)

        # --- TAB 3: BACKGROUND & FONTS ---
        with tab_style:
            active_scene.background_type = st.selectbox("Background Style", ["Animated Gradient", "Solid Color", "Custom Image"], index=["Animated Gradient", "Solid Color", "Custom Image"].index(active_scene.background_type))
            
            bg_c1, bg_c2 = st.columns(2)
            with bg_c1:
                active_scene.background_color_1 = st.color_picker("Primary Color", value=active_scene.background_color_1)
            with bg_c2:
                if active_scene.background_type == "Animated Gradient":
                    active_scene.background_color_2 = st.color_picker("Secondary Gradient Color", value=active_scene.background_color_2)

            if active_scene.background_type == "Custom Image":
                uploaded_bg = st.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])
                if uploaded_bg:
                    bg_path = f"/tmp/{uploaded_bg.name}"
                    with open(bg_path, "wb") as f:
                        f.write(uploaded_bg.getbuffer())
                    active_scene.background_image_path = bg_path

            st.divider()
            st.write("**Typography Sizing:**")
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                active_scene.question_font_size = st.slider("Question Text Size", 24, 72, int(active_scene.question_font_size))
            with f_col2:
                active_scene.option_font_size = st.slider("Options Text Size", 18, 48, int(active_scene.option_font_size))

        # --- TAB 4: WATERMARK & GLOBAL VIDEO SETTINGS ---
        with tab_global:
            st.subheader("🏷️ Logo & Channel Watermark")
            wm = project.settings.watermark
            wm.enabled = st.checkbox("Enable Overlay Watermark", value=wm.enabled)
            if wm.enabled:
                wm.text = st.text_input("Watermark Text / Channel Handle", value=wm.text)
                wm.position = st.selectbox("Watermark Position", ["Top Left", "Top Right", "Bottom Left", "Bottom Right"], index=["Top Left", "Top Right", "Bottom Left", "Bottom Right"].index(wm.position))
                wm.opacity = st.slider("Watermark Opacity", 0.1, 1.0, float(wm.opacity), 0.05)

            st.divider()
            st.subheader("📐 Global Output Resolution")
            res_choice = st.selectbox("Aspect Ratio Preset", ["9:16 Vertical (Shorts/TikTok/Reels)", "16:9 Horizontal (YouTube)"], index=0)
            if "9:16" in res_choice:
                project.settings.width, project.settings.height = 1080, 1920
            else:
                project.settings.width, project.settings.height = 1920, 1080

            if st.button("💾 Save Project Configuration", use_container_width=True):
                project.save()
                st.success("Project settings successfully saved!")
