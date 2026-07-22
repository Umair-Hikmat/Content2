"""
Desktop Graphical User Interface (GUI) for Quiz Studio.
Tkinter application providing real-time canvas preview, project creation,
question bank loading, AI wizard prompt triggers, and video exporting.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from project import QuizProject, TimelineScene
from templates import TemplateRegistry
from quiz_import import QuizImporter
from export_video import VideoExporter
from ai_generator import AIGenerator

# Import templates to ensure registration
import template_trivia
import template_emoji
import template_fillblank
import template_logo
import template_flag


class QuizStudioGUI:
    """Main desktop interface window for Quiz Studio."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Quiz Studio - Short-Form Video Generator")
        self.root.geometry("1280x800")
        self.root.configure(bg="#0F0F1A")

        self.project = QuizProject(title="New Quiz Project")
        self.current_scene_index = 0
        self.preview_image_tk = None

        self._build_ui()
        self._refresh_scene_preview()

    def _build_ui(self):
        """Constructs layout panels, canvas, and controls."""
        # Top Header Bar
        header = tk.Frame(self.root, bg="#1A1A2E", height=50)
        header.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(
            header,
            text="🎬 Quiz Studio",
            font=("Segoe UI", 16, "bold"),
            fg="#00F5D4",
            bg="#1A1A2E"
        )
        title_lbl.pack(side=tk.LEFT, padx=15, pady=10)

        # Top Control Buttons
        btn_import = tk.Button(header, text="Import Excel/CSV", command=self._on_import_excel, bg="#7B2CBF", fg="#FFF")
        btn_import.pack(side=tk.RIGHT, padx=10, pady=10)

        btn_ai = tk.Button(header, text="✨ AI Assistant", command=self._on_ai_wizard, bg="#FF007F", fg="#FFF")
        btn_ai.pack(side=tk.RIGHT, padx=5, pady=10)

        btn_export = tk.Button(header, text="🚀 Export Video", command=self._on_export_video, bg="#00F5D4", fg="#000")
        btn_export.pack(side=tk.RIGHT, padx=5, pady=10)

        # Main Workspace Split Pane
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0F0F1A")
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Control Panel
        left_panel = tk.Frame(paned, bg="#161625", width=380)
        paned.add(left_panel)

        tk.Label(left_panel, text="Scene Editor", font=("Segoe UI", 12, "bold"), fg="#FFF", bg="#161625").pack(anchor="w", padx=10, pady=10)

        # Question Prompt Entry
        tk.Label(left_panel, text="Question Text:", fg="#AAA", bg="#161625").pack(anchor="w", padx=10)
        self.txt_question = tk.Text(left_panel, height=3, bg="#222235", fg="#FFF", insertbackground="white")
        self.txt_question.pack(fill=tk.X, padx=10, pady=5)

        # Correct Answer Entry
        tk.Label(left_panel, text="Correct Answer:", fg="#AAA", bg="#161625").pack(anchor="w", padx=10)
        self.ent_answer = tk.Entry(left_panel, bg="#222235", fg="#FFF", insertbackground="white")
        self.ent_answer.pack(fill=tk.X, padx=10, pady=5)

        # Template Selector
        tk.Label(left_panel, text="Template:", fg="#AAA", bg="#161625").pack(anchor="w", padx=10)
        self.cmb_template = ttk.Combobox(
            left_panel,
            values=["General Trivia", "Guess the Emoji", "Fill in the Blank", "Guess the Logo", "Guess the Flag"]
        )
        self.cmb_template.set("General Trivia")
        self.cmb_template.pack(fill=tk.X, padx=10, pady=5)

        # Navigation Controls
        nav_frame = tk.Frame(left_panel, bg="#161625")
        nav_frame.pack(fill=tk.X, padx=10, pady=15)

        btn_prev = tk.Button(nav_frame, text="◀ Prev", command=self._prev_scene, bg="#2A2A3D", fg="#FFF")
        btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.lbl_scene_num = tk.Label(nav_frame, text="Scene 1 / 1", fg="#FFF", bg="#161625")
        self.lbl_scene_num.pack(side=tk.LEFT, padx=10)

        btn_next = tk.Button(nav_frame, text="Next ▶", command=self._next_scene, bg="#2A2A3D", fg="#FFF")
        btn_next.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)

        btn_add = tk.Button(left_panel, text="+ Add New Scene", command=self._add_scene, bg="#333355", fg="#FFF")
        btn_add.pack(fill=tk.X, padx=10, pady=5)

        # Right Preview Panel
        right_panel = tk.Frame(paned, bg="#0F0F1A")
        paned.add(right_panel)

        self.preview_canvas = tk.Canvas(right_panel, width=360, height=640, bg="#000000", highlightthickness=0)
        self.preview_canvas.pack(expand=True, pady=10)

    def _get_current_scene(self) -> TimelineScene:
        """Retrieves or creates the active scene."""
        if not self.project.scenes:
            self.project.add_scene(TimelineScene(
                template_name="General Trivia",
                question_text="Sample Question Prompt?",
                correct_answer="Correct Answer"
            ))
        return self.project.scenes[self.current_scene_index]

    def _refresh_scene_preview(self):
        """Renders current scene frame to GUI canvas."""
        scene = self._get_current_scene()

        # Update input fields
        self.txt_question.delete("1.0", tk.END)
        self.txt_question.insert("1.0", scene.question_text)
        self.ent_answer.delete(0, tk.END)
        self.ent_answer.insert(0, scene.correct_answer)
        self.cmb_template.set(scene.template_name)

        self.lbl_scene_num.config(text=f"Scene {self.current_scene_index + 1} / {len(self.project.scenes)}")

        # Render preview frame using active template
        template = TemplateRegistry.get(scene.template_name)
        preview_res = (1080, 1920)
        pil_frame = template.render_frame(
            scene=scene,
            time_sec=1.0,
            resolution=preview_res,
            palette=self.project.theme_palette
        )

        # Scale down image for Tkinter viewport
        preview_frame = pil_frame.resize((360, 640), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (360, 640), "#0F0F1A")
        bg.paste(preview_frame, (0, 0), preview_frame)

        self.preview_image_tk = ImageTk.PhotoImage(bg)
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image_tk)

    def _prev_scene(self):
        if self.current_scene_index > 0:
            self.current_scene_index -= 1
            self._refresh_scene_preview()

    def _next_scene(self):
        if self.current_scene_index < len(self.project.scenes) - 1:
            self.current_scene_index += 1
            self._refresh_scene_preview()

    def _add_scene(self):
        self.project.add_scene(TimelineScene(
            template_name=self.cmb_template.get(),
            question_text="New Question Prompt?",
            correct_answer="New Answer"
        ))
        self.current_scene_index = len(self.project.scenes) - 1
        self._refresh_scene_preview()

    def _on_import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel & CSV Files", "*.xlsx *.csv")])
        if file_path:
            try:
                self.project = QuizImporter.import_from_excel(Path(file_path), self.cmb_template.get())
                self.current_scene_index = 0
                self._refresh_scene_preview()
                messagebox.showinfo("Success", f"Imported {len(self.project.scenes)} questions!")
            except Exception as e:
                messagebox.showerror("Import Error", str(e))

    def _on_ai_wizard(self):
        messagebox.showinfo("AI Wizard", "AI generation prompt tool active! Connect your LLM API Key in config.py.")

    def _on_export_video(self):
        out_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if out_path:
            try:
                exporter = VideoExporter(self.project)
                exporter.render_to_file(Path(out_path))
                messagebox.showinfo("Export Complete", f"Video exported successfully to:\n{out_path}")
            except Exception as e:
                messagebox.showerror("Render Error", str(e))


def main():
    root = tk.Tk()
    app = QuizStudioGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
