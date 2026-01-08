"""
GUI module - Giao diện đồ họa cho Git Tag Manager.

Sử dụng customtkinter và tkinterdnd2 cho giao diện hiện đại với hỗ trợ drag & drop.
"""

import os
import threading
import customtkinter as ctk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

from .core import (
    load_or_create_config,
    save_config,
    run_git,
    get_tag_info,
    get_commit_info,
    open_config_file,
    DEFAULT_STRATEGIES,
)

# Colors
COLOR_CARD = "#2b2b2b"
COLOR_SUCCESS = "#2CC985"
COLOR_ACCENT = "#3B8ED0"
COLOR_DROP_HOVER = "#444444"


class GitTagManagerGUI(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main GUI Application với hỗ trợ Drag & Drop."""

    def __init__(self):
        super().__init__()
        # Init DnD
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Git Tag Manager Pro")
        self.geometry("700x650")
        ctk.set_appearance_mode("Dark")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)  # Log box expand

        self.config, is_new = load_or_create_config()
        self.target_tag = None

        self._create_header()
        self._create_selection_frame()
        self._create_dashboard()
        self._create_info_label()
        self._create_log_box()
        self._create_action_buttons()
        self._setup_drag_drop()

        self.reload_config()

    def _create_header(self):
        """Tạo header với title và nút config."""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            self.header_frame,
            text="Git Tag Manager 🧙‍♂️",
            font=("Roboto Medium", 20)
        ).pack(side="left")

        ctk.CTkButton(
            self.header_frame,
            text="⚙ Config",
            width=80,
            fg_color="#444",
            command=open_config_file
        ).pack(side="right")

    def _create_selection_frame(self):
        """Tạo frame chọn project và strategy."""
        self.sel_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD)
        self.sel_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.sel_frame.grid_columnconfigure((0, 1), weight=1)

        # Label hướng dẫn kéo thả
        self.lbl_drop = ctk.CTkLabel(
            self.sel_frame,
            text="📂 Drag & Drop Project Folder Here to Add",
            font=("Arial", 10, "italic"),
            text_color="gray"
        )
        self.lbl_drop.grid(row=0, column=0, columnspan=2, pady=(10, 0))

        # Project selector
        ctk.CTkLabel(
            self.sel_frame,
            text="PROJECT",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(5, 0))

        self.combo_proj = ctk.CTkComboBox(
            self.sel_frame,
            values=[],
            command=self.on_project_change
        )
        self.combo_proj.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))

        # Strategy selector
        ctk.CTkLabel(
            self.sel_frame,
            text="STRATEGY",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).grid(row=1, column=1, sticky="w", padx=15, pady=(5, 0))

        self.combo_strat = ctk.CTkComboBox(
            self.sel_frame,
            values=[],
            command=self.on_strategy_change
        )
        self.combo_strat.grid(row=2, column=1, sticky="ew", padx=15, pady=(5, 15))

    def _create_dashboard(self):
        """Tạo dashboard hiển thị current/next tag."""
        self.dash_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dash_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.dash_frame.grid_columnconfigure((0, 1), weight=1)

        # Current Card
        self.c_curr = ctk.CTkFrame(self.dash_frame, fg_color=COLOR_CARD)
        self.c_curr.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=10)

        ctk.CTkLabel(
            self.c_curr,
            text="CURRENT TAG",
            font=("Arial", 11)
        ).pack(pady=(10, 0))

        self.lbl_curr_val = ctk.CTkLabel(
            self.c_curr,
            text="...",
            font=("Roboto Mono", 20, "bold"),
            text_color="#AAA"
        )
        self.lbl_curr_val.pack(pady=5)

        # Next Card
        self.c_next = ctk.CTkFrame(
            self.dash_frame,
            fg_color=COLOR_CARD,
            border_width=2,
            border_color=COLOR_SUCCESS
        )
        self.c_next.grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=10)

        ctk.CTkLabel(
            self.c_next,
            text="NEXT TAG",
            font=("Arial", 11, "bold"),
            text_color=COLOR_SUCCESS
        ).pack(pady=(10, 0))

        self.lbl_next_val = ctk.CTkLabel(
            self.c_next,
            text="...",
            font=("Roboto Mono", 24, "bold"),
            text_color=COLOR_SUCCESS
        )
        self.lbl_next_val.pack(pady=5)

    def _create_info_label(self):
        """Tạo label hiển thị commit info."""
        self.lbl_commit = ctk.CTkLabel(
            self,
            text="Commit Info: ...",
            font=("Consolas", 12),
            text_color="#AAA"
        )
        self.lbl_commit.grid(row=3, column=0, padx=20, sticky="w")

    def _create_log_box(self):
        """Tạo log box."""
        self.log_box = ctk.CTkTextbox(self, height=120, font=("Consolas", 12))
        self.log_box.grid(row=5, column=0, sticky="nsew", padx=20, pady=10)

    def _create_action_buttons(self):
        """Tạo các nút action."""
        self.btn_act = ctk.CTkButton(
            self,
            text="RELOAD",
            width=80,
            fg_color="#555",
            command=self.reload_config
        )
        self.btn_act.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 20))

        self.btn_run = ctk.CTkButton(
            self,
            text="🚀 CREATE TAG & PUSH",
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=COLOR_ACCENT,
            hover_color="#2A75B0",
            command=self.execute_tag
        )
        self.btn_run.grid(row=6, column=0, sticky="e", padx=20, pady=(0, 20))

    def _setup_drag_drop(self):
        """Setup drag & drop handlers."""
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)

    def log(self, msg: str):
        """Thêm message vào log box."""
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def on_drop(self, event):
        """Xử lý khi user kéo thả folder vào app."""
        raw_path = event.data

        # Clean path: Windows/Mac sometimes wraps path in {} if it contains spaces
        if raw_path.startswith('{') and raw_path.endswith('}'):
            raw_path = raw_path[1:-1]

        if not os.path.isdir(raw_path):
            self.log(f"Error: Not a folder: {raw_path}")
            return

        git_dir = os.path.join(raw_path, '.git')
        if not os.path.exists(git_dir):
            self.log(f"Error: Not a Git repo (missing .git): {raw_path}")
            return

        # Ask for Project Name
        folder_name = os.path.basename(raw_path)
        dialog = ctk.CTkInputDialog(
            text=f"Git Repo Detected!\nEnter Project Name:",
            title="Add Project"
        )
        project_name = dialog.get_input()

        if project_name:
            self.add_new_project(project_name, raw_path)

    def add_new_project(self, name: str, path: str):
        """Thêm project mới vào config."""
        if name in self.config.get('projects', {}):
            if not messagebox.askyesno("Update", f"Project '{name}' exists. Overwrite?"):
                return

        if 'projects' not in self.config:
            self.config['projects'] = {}

        self.config['projects'][name] = {
            "path": path,
            "strategies": DEFAULT_STRATEGIES.copy()
        }

        save_config(self.config)
        self.log(f"Added project: {name}")
        self.reload_config()

        # Auto select
        self.combo_proj.set(name)
        self.on_project_change(name)

    def reload_config(self):
        """Reload config từ file."""
        self.config, _ = load_or_create_config()
        projs = list(self.config.get('projects', {}).keys())
        self.combo_proj.configure(values=projs)

        if projs:
            current = self.combo_proj.get()
            if current and current in projs:
                self.on_project_change(current)
            else:
                self.combo_proj.set(projs[0])
                self.on_project_change(projs[0])
        else:
            self.combo_proj.set("")
            self.combo_strat.set("")
            self.combo_strat.configure(values=[])

    def on_project_change(self, choice):
        """Xử lý khi user chọn project khác."""
        proj = self.config['projects'].get(choice)
        if not proj:
            return

        strats = list(proj.get('strategies', {}).keys())
        self.combo_strat.configure(values=strats)

        if strats:
            self.combo_strat.set(strats[0])
            self.calculate()
        else:
            self.combo_strat.set("")

    def on_strategy_change(self, choice):
        """Xử lý khi user chọn strategy khác."""
        self.calculate()

    def calculate(self):
        """Tính toán tag tiếp theo trong background thread."""
        proj_name = self.combo_proj.get()
        if not proj_name:
            return

        proj = self.config['projects'].get(proj_name)
        if not proj:
            return

        strat_name = self.combo_strat.get()
        if not strat_name:
            return

        strat = proj['strategies'].get(strat_name)
        if not strat:
            return

        def task():
            try:
                path = proj['path']
                curr, next_ver = get_tag_info(path, strat)
                c_info = get_commit_info(path)

                self.lbl_curr_val.configure(text=curr)
                self.lbl_next_val.configure(text=next_ver)
                self.lbl_commit.configure(text=f"HEAD: {c_info}")
                self.target_tag = next_ver
                self.log(f"Calculated: {next_ver}")
            except Exception as e:
                self.lbl_next_val.configure(text="Error")
                self.log(f"Error: {e}")

        threading.Thread(target=task, daemon=True).start()

    def execute_tag(self):
        """Tạo tag và push trong background thread."""
        if not self.target_tag:
            return

        tag = self.target_tag
        proj = self.config['projects'].get(self.combo_proj.get())
        if not proj:
            return

        path = proj['path']

        if not messagebox.askyesno("Confirm", f"Create tag {tag} and Push?"):
            return

        def task():
            try:
                self.log(f"Tagging {tag}...")
                run_git(['tag', '-a', tag, '-m', f"Release {tag}"], cwd=path)
                self.log("Pushing...")
                run_git(['push', 'origin', tag], cwd=path)
                self.log("SUCCESS!")
                self.after(0, self.calculate)
            except Exception as e:
                self.log(f"FAIL: {e}")

        threading.Thread(target=task, daemon=True).start()


def main():
    """Entry point cho GUI."""
    app = GitTagManagerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
