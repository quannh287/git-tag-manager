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

# macOS Native Colors (works with both light/dark mode)
COLOR_SUCCESS = "#34C759"  # macOS Green
COLOR_ACCENT = "#007AFF"   # macOS Blue
COLOR_ORANGE = "#FF9500"   # macOS Orange


class GitTagManagerGUI(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main GUI Application với hỗ trợ Drag & Drop."""

    def __init__(self):
        super().__init__()
        # Init DnD
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Git Tag Manager")
        self.geometry("680x600")

        # Follow system appearance (light/dark mode)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)  # Log box expand

        # Set app icon
        self._set_app_icon()

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

    def _set_app_icon(self):
        """Set app icon từ assets folder."""
        try:
            from PIL import Image, ImageTk

            # Tìm đường dẫn đến icon
            module_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(module_dir)

            # Ưu tiên .icns, fallback .png
            icon_icns = os.path.join(project_root, "assets", "app_icons.icns")
            icon_png = os.path.join(project_root, "assets", "app_icons.png")

            icon_path = icon_icns if os.path.exists(icon_icns) else icon_png

            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                # Resize for window icon
                icon_image = icon_image.resize((128, 128), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, icon_photo)
                # Giữ reference để tránh garbage collection
                self._icon_photo = icon_photo
        except Exception:
            # Bỏ qua nếu không load được icon
            pass

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
            fg_color="transparent",
            border_width=1,
            text_color=COLOR_ACCENT,
            border_color=COLOR_ACCENT,
            command=open_config_file
        ).pack(side="right")

    def _create_selection_frame(self):
        """Tạo frame chọn project và strategy."""
        self.sel_frame = ctk.CTkFrame(self)
        self.sel_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.sel_frame.grid_columnconfigure((0, 1), weight=1)

        # Drop zone - nổi bật hơn
        self.drop_zone = ctk.CTkFrame(
            self.sel_frame,
            height=60,
            border_width=2,
            border_color=COLOR_ACCENT,
            fg_color="transparent"
        )
        self.drop_zone.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 10))
        self.drop_zone.grid_propagate(False)

        self.lbl_drop = ctk.CTkLabel(
            self.drop_zone,
            text="📂 Drag & Drop Project Folder Here",
            font=("Arial", 13),
            text_color=COLOR_ACCENT
        )
        self.lbl_drop.place(relx=0.5, rely=0.5, anchor="center")

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

        # Strategy selector with Edit button
        ctk.CTkLabel(
            self.sel_frame,
            text="STRATEGY",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).grid(row=1, column=1, sticky="w", padx=15, pady=(5, 0))

        # Frame to hold combobox and edit button
        strat_frame = ctk.CTkFrame(self.sel_frame, fg_color="transparent")
        strat_frame.grid(row=2, column=1, sticky="ew", padx=15, pady=(5, 15))
        strat_frame.grid_columnconfigure(0, weight=1)

        self.combo_strat = ctk.CTkComboBox(
            strat_frame,
            values=[],
            command=self.on_strategy_change
        )
        self.combo_strat.grid(row=0, column=0, sticky="ew")

        self.btn_edit_strat = ctk.CTkButton(
            strat_frame,
            text="✎",
            width=32,
            fg_color="transparent",
            border_width=1,
            text_color=COLOR_ACCENT,
            border_color=COLOR_ACCENT,
            command=self._show_edit_strategy_dialog
        )
        self.btn_edit_strat.grid(row=0, column=1, padx=(8, 0))

    def _create_dashboard(self):
        """Tạo dashboard hiển thị current/next tag."""
        self.dash_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dash_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.dash_frame.grid_columnconfigure((0, 1), weight=1)

        # Current Card
        self.c_curr = ctk.CTkFrame(self.dash_frame)
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
            text="↻ Reload",
            width=90,
            fg_color="transparent",
            border_width=1,
            text_color=COLOR_ACCENT,
            border_color=COLOR_ACCENT,
            command=self.reload_config
        )
        self.btn_act.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 20))

        self.btn_run = ctk.CTkButton(
            self,
            text="Create Tag & Push",
            height=44,
            font=("SF Pro", 14, "bold"),
            fg_color=COLOR_ACCENT,
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

        # Defer dialog để không block drag/drop event
        self.after(100, lambda: self._show_add_project_dialog(raw_path))

    def _show_edit_strategy_dialog(self):
        """Hiển thị dialog để sửa strategy format."""
        proj_name = self.combo_proj.get()
        strat_name = self.combo_strat.get()

        if not proj_name or not strat_name:
            self.log("Please select a project and strategy first.")
            return

        proj = self.config['projects'].get(proj_name)
        if not proj:
            return

        strat = proj['strategies'].get(strat_name)
        if not strat:
            return

        # Tạo edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Strategy: {strat_name}")
        dialog.geometry("450x280")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 280) // 2
        dialog.geometry(f"+{x}+{y}")

        # Format entry
        ctk.CTkLabel(dialog, text="Format:", font=("Arial", 12, "bold")).pack(pady=(20, 5), padx=20, anchor="w")
        format_entry = ctk.CTkEntry(dialog, width=400)
        format_entry.insert(0, strat['format'])
        format_entry.pack(padx=20)

        # Hint
        ctk.CTkLabel(
            dialog,
            text="Placeholders: {major}, {minor}, {patch}, {build}",
            font=("Arial", 10),
            text_color="gray"
        ).pack(padx=20, anchor="w")

        # Increment type
        ctk.CTkLabel(dialog, text="Increment:", font=("Arial", 12, "bold")).pack(pady=(15, 5), padx=20, anchor="w")
        increment_var = ctk.StringVar(value=strat['increment'])
        increment_menu = ctk.CTkOptionMenu(
            dialog,
            values=["major", "minor", "patch", "build"],
            variable=increment_var,
            width=400
        )
        increment_menu.pack(padx=20)

        # Save button
        def save_changes():
            new_format = format_entry.get().strip()
            new_increment = increment_var.get()

            if not new_format:
                return

            # Update config
            self.config['projects'][proj_name]['strategies'][strat_name] = {
                'format': new_format,
                'increment': new_increment
            }
            save_config(self.config)
            self.log(f"Strategy '{strat_name}' updated: {new_format} ({new_increment})")
            dialog.destroy()
            self.calculate()

        ctk.CTkButton(
            dialog,
            text="Save",
            fg_color=COLOR_ACCENT,
            command=save_changes
        ).pack(pady=20)

    def _show_add_project_dialog(self, path: str):
        """Hiển thị dialog để nhập tên project."""
        folder_name = os.path.basename(path)
        dialog = ctk.CTkInputDialog(
            text=f"Git Repo Detected!\nEnter Project Name:",
            title="Add Project"
        )
        project_name = dialog.get_input()

        if project_name:
            self.add_new_project(project_name, path)

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
