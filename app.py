"""
Quiz Studio Dashboard with Live Scrubber, Custom Font Controls, and 1-Click MP4 Generation.
"""

import os
import streamlit as st
from PIL import Image
from moviepy.editor import ImageSequenceClip

from project import QuizProject, TimelineScene, QuizOption
from templates import TemplateRegistry, apply_watermark

st.set_page_config(page_title="Quiz Studio Pro", layout="wide", page_icon="🎬")

# Initialize Session Project State
if "project" not in st.session_state:
    project = QuizProject(title="Trivia Video")
    project.add_scene(
        question_text="Which planet is known as the Red Planet?",
        options=[
            QuizOption(text="Venus"),
            QuizOption(text="Mars", is_correct=True),
            QuizOption(text="Jupiter"),
            QuizOption(text="Saturn")
        ],
        correct_answer="Mars",
        question_font_size=42,
        option_font_size=32
    )
    st.session_state.project = project

project = st.session_state.project

st.title("⚡ Quiz Studio Dashboard")

# MAIN TWO-COLUMN STUDIO LAYOUT
col_preview, col_controls = st.columns([1, 1])

# ---------------------------------------------------------
# LEFT COLUMN: CANVAS PREVIEW & ONE-CLICK MP4 PLAYBACK
# ---------------------------------------------------------
with col_preview:
    st.subheader("📺 Interactive Canvas Preview")
    
    # Scrubber Slider
    total_duration = max(1.0, project.total_duration)
    scrub_time = st.slider("⏱️ Scrub Timeline (Seconds)", 0.0, total_duration, 0.0, step=0.2)

    # Fetch active scene & local offset
    scene, scene_time = project.get_scene_at_time(scrub_time)

    if scene:
        # Render canvas frame dynamically
        template = TemplateRegistry.get(scene.template_name)
        frame_img = template.render_frame(
            scene=scene,
            time_sec=scene_time,
            resolution=project.resolution,
            palette=project.theme_palette
        )
        frame_img = apply_watermark(frame_img, project.settings.watermark)
        st.image(frame_img, use_container_width=True)
        st.caption(f"Template: **{scene.template_name}** | Q-Size: `{scene.question_font_size}px` | Opt-Size: `{scene.option_font_size}px`")
    else:
        st.info("No scenes found in project. Click 'Add Scene' to get started!")

    st.divider()

    # ONE-CLICK VIDEO RENDERING
    st.subheader("🎬 1-Click Video Export")
    if st.button("🚀 Render & Play Full Video MP4", type="primary", use_container_width=True):
        with st.spinner("Rendering full video clip... Please wait..."):
            frames = []
            fps = 15  # Fast render preview fps
            dt = 1.0 / fps
            
            # Step through entire timeline
            t = 0.0
            while t < project.total_duration:
                s, local_t = project.get_scene_at_time(t)
                if s:
                    tmpl = TemplateRegistry.get(s.template_name)
                    img = tmpl.render_frame(s, local_t, project.resolution, project.theme_palette)
                    img = apply_watermark(img, project.settings.watermark)
                    # Convert PIL image to array
                    import numpy as np
                    frames.append(np.array(img.convert("RGB")))
                t += dt

            if frames:
                clip = ImageSequenceClip(frames, fps=fps)
                output_path = "/tmp/quiz_preview.mp4"
                clip.write_videofile(output_path, codec="libx264", logger=None)
                st.success("Render complete!")
                st.video(output_path)

# ---------------------------------------------------------
# RIGHT COLUMN: SCENE & TYPOGRAPHY EDITOR
# ---------------------------------------------------------
with col_controls:
    st.subheader("⚙️ Scene & Template Controls")

    # Select Active Scene
    scene_titles = [f"Scene {i+1}: {s.question_text[:28]}..." for i, s in enumerate(project.scenes)]
    selected_idx = st.selectbox("Active Scene", range(len(scene_titles)), format_func=lambda i: scene_titles[i]) if scene_titles else None

    # Add / Remove Scene Toolbar
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        if st.button("➕ Add Scene", use_container_width=True):
            project.add_scene(
                question_text="New Quiz Question?",
                options=[QuizOption(text="Option A"), QuizOption(text="Option B")],
                correct_answer="Option A"
            )
            st.rerun()
    with btn_c2:
        if selected_idx is not None and st.button("🗑️ Delete Scene", use_container_width=True):
            project.remove_scene(project.scenes[selected_idx].id)
            st.rerun()

    st.divider()

    if selected_idx is not None:
        active_scene = project.scenes[selected_idx]

        tab_design, tab_content, tab_watermark = st.tabs(["🎨 Template & Fonts", "📝 Content & Answers", "🏷️ Watermark & Layout"])

        # TAB 1: TEMPLATE & REAL-TIME FONT CONTROLS
        with tab_design:
            active_scene.template_name = st.selectbox(
                "Select Layout Template",
                TemplateRegistry.list_templates(),
                index=TemplateRegistry.list_templates().index(active_scene.template_name) if active_scene.template_name in TemplateRegistry.list_templates() else 0
            )

            st.write("**Font Sizing Controls (Live Canvas Update):**")
            active_scene.question_font_size = st.slider("Question Font Size", 20, 80, int(active_scene.question_font_size), step=2)
            active_scene.option_font_size = st.slider("Options Font Size", 16, 60, int(active_scene.option_font_size), step=2)
            active_scene.duration = st.number_input("Scene Duration (Sec)", 1.0, 30.0, float(active_scene.duration), 0.5)

        # TAB 2: CONTENT & MULTIPLE CHOICE
        with tab_content:
            active_scene.question_text = st.text_input("Question Text", value=active_scene.question_text)
            
            st.write("**Answer Options:**")
            updated_opts = []
            for i, opt in enumerate(active_scene.options):
                oc1, oc2 = st.columns([3, 1])
                with oc1:
                    txt = st.text_input(f"Option {chr(65+i)}", value=opt.text, key=f"opt_txt_{active_scene.id}_{i}")
                with oc2:
                    is_corr = st.checkbox("Correct", value=(opt.text == active_scene.correct_answer), key=f"opt_corr_{active_scene.id}_{i}")
                    if is_corr:
                        active_scene.correct_answer = txt
                updated_opts.append(QuizOption(text=txt, is_correct=is_corr))
            active_scene.options = updated_opts

        # TAB 3: WATERMARK & ASPECT RATIO
        with tab_watermark:
            wm = project.settings.watermark
            wm.enabled = st.checkbox("Enable Overlay Watermark", value=wm.enabled)
            if wm.enabled:
                wm.text = st.text_input("Channel Handle / Logo Text", value=wm.text)
                wm.position = st.selectbox("Position", ["Top Left", "Top Right", "Bottom Left", "Bottom Right"], index=["Top Left", "Top Right", "Bottom Left", "Bottom Right"].index(wm.position))
                wm.opacity = st.slider("Opacity", 0.1, 1.0, float(wm.opacity), 0.05)

            st.write("**Aspect Ratio Output:**")
            ratio = st.selectbox("Resolution Mode", ["9:16 Vertical (Shorts/TikTok)", "16:9 Horizontal (YouTube)"])
            if "9:16" in ratio:
                project.settings.width, project.settings.height = 1080, 1920
            else:
                project.settings.width, project.settings.height = 1920, 1080
