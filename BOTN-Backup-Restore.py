import os
import zipfile
import rarfile
import py7zr
import shutil
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, Menu, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import winreg
import sys
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("BOTN Backup ~ Restore")
        self.geometry("600x500")
        self.iconbitmap(resource_path("OBF_101.ico"))

        self.theme_var = ctk.StringVar(value="System")
        self.excluded_ext = {".jpg", ".jpeg", ".gif", ".png", ".bmp", ".tiff", ".ico", ".webp", ".svg", ".txt", ".md", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}

        self.required_character_presets = {"CP_"}
        self.required_toy_presets = {"TS_"}
        self.required_savegames = {f"{i}.sav" for i in range(10)} | {"GameActions.sav"}

        self.load_position()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        menubar = Menu(self)
        self.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Preferences", accelerator="Ctrl+AltP", command=self.open_preferences)
        self.bind_all("<Control-Alt-p>", lambda e: self.open_preferences())
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self.quit)
        self.bind_all("<Alt-F4>", lambda e: self.quit())

        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(pady=10, fill="x", padx=10)
        self.selector_var = ctk.StringVar(value="CharacterPresets")
        ctk.CTkRadioButton(selector_frame, text="CharacterPresets",
                           variable=self.selector_var, value="CharacterPresets").pack(side="left", padx=10)
        ctk.CTkRadioButton(selector_frame, text="ToyPresets",
                           variable=self.selector_var, value="ToyPresets").pack(side="left", padx=10)
        ctk.CTkRadioButton(selector_frame, text="SaveGames",
                           variable=self.selector_var, value="SaveGames").pack(side="left", padx=10)
        self.selector_var.trace("w", self.update_file_list)

        path_frame = ctk.CTkFrame(self)
        path_frame.pack(pady=10, fill="x", padx=10)
        self.path_entry = ctk.CTkEntry(path_frame)
        self.path_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(path_frame, text="Browse", command=self.browse_path).pack(side="right", padx=5)

        self.base_path = os.path.expandvars(r"%LOCALAPPDATA%\OBF\Saved")
        os.makedirs(self.base_path, exist_ok=True)
        for sub in ("CharacterPresets", "ToyPresets", "SaveGames"):
            os.makedirs(os.path.join(self.base_path, sub), exist_ok=True)
        self.path_entry.insert(0, self.base_path)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=10, fill="both", expand=True, padx=10)

        backup_tab = self.tabview.add("Backup")
        restore_tab = self.tabview.add("Restore")

        file_list_frame = ctk.CTkScrollableFrame(backup_tab, height=200)
        file_list_frame.pack(pady=10, fill="both", expand=True)
        self.file_list = file_list_frame
        self.file_checkboxes = {}

        btn_frame = ctk.CTkFrame(backup_tab)
        btn_frame.pack(fill="x", pady=5)
        self.backup_btn = ctk.CTkButton(btn_frame, text="Backup",
                                        command=self.do_backup, state="disabled")
        self.backup_btn.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save to...", command=self.select_dest_dir).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Select All", command=self.select_all_files).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Deselect All", command=self.deselect_all_files).pack(side="left", padx=5)

        self.load_backup_path()

        self.restore_list = ctk.CTkTextbox(restore_tab, height=200)
        self.restore_list.pack(pady=10, fill="both", expand=True)
        self.restore_list._textbox.drop_target_register(DND_FILES)
        self.restore_list._textbox.dnd_bind("<<Drop>>", self.handle_drop)

        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(restore_tab, variable=self.progress_var)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)

        restore_btn_frame = ctk.CTkFrame(restore_tab)
        restore_btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(restore_btn_frame, text="Add Archive",
                      command=self.add_archive).pack(side="left", padx=5)

        self.restore_btn = ctk.CTkButton(
            restore_btn_frame,
            text="Restore",
            command=lambda: threading.Thread(target=self.do_restore, daemon=True).start(),
            state="disabled"
        )
        self.restore_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(restore_btn_frame, text="Clear",
                                       command=self.clear_restore_list, state="disabled")
        self.clear_btn.pack(side="left", padx=5)

        self.selected_zips = []
        self.update_file_list()

    def update_progress(self, current, total):
        if total <= 0:
            return
        self.after(0, lambda: self.progress_var.set(current / total))

    def handle_drop(self, event):
        for f in self.tk.splitlist(event.data):
            if f.lower().endswith((".zip", ".rar", ".7z", ".sav")):
                self.selected_zips.append(f)
                self.restore_list.insert("end", os.path.basename(f) + "\n")
        self.restore_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")

    def add_archive(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Supported files", "*.zip *.rar *.7z *.sav")]
        )
        for f in files:
            self.selected_zips.append(f)
            self.restore_list.insert("end", os.path.basename(f) + "\n")
        if self.selected_zips:
            self.restore_btn.configure(state="normal")
            self.clear_btn.configure(state="normal")

    def do_restore(self):
        path = self.get_current_path()
        os.makedirs(path, exist_ok=True)

        total = 0
        for arc in self.selected_zips:
            if arc.lower().endswith(".sav"):
                total += 1
            elif arc.lower().endswith(".zip"):
                with zipfile.ZipFile(arc) as z:
                    total += len([m for m in z.namelist() if not m.endswith("/")])
            elif arc.lower().endswith(".rar"):
                with rarfile.RarFile(arc) as r:
                    total += len([m for m in r.namelist() if not m.endswith("/")])
            elif arc.lower().endswith(".7z"):
                with py7zr.SevenZipFile(arc) as z:
                    total += len([m for m in z.getnames() if not m.endswith("/")])

        done = 0
        self.update_progress(0, total)

        for arc in self.selected_zips:
            if arc.lower().endswith(".sav"):
                shutil.copy2(arc, os.path.join(path, os.path.basename(arc)))
                done += 1
                self.update_progress(done, total)

            elif arc.lower().endswith(".zip"):
                with zipfile.ZipFile(arc) as z:
                    for m in z.namelist():
                        if not m.endswith("/"):
                            z.extract(m, path)
                            done += 1
                            self.update_progress(done, total)

            elif arc.lower().endswith(".rar"):
                with rarfile.RarFile(arc) as r:
                    for m in r.namelist():
                        if not m.endswith("/"):
                            r.extract(m, path)
                            done += 1
                            self.update_progress(done, total)

            elif arc.lower().endswith(".7z"):
                with py7zr.SevenZipFile(arc) as z:
                    members = [m for m in z.getnames() if not m.endswith("/")]
                    z.extract(path=path, targets=members)
                    for _ in members:
                        done += 1
                        self.update_progress(done, total)

        messagebox.showinfo("Success", "Restore completed", parent=self)
        self.clear_restore_list()
        self.update_file_list()

    def clear_restore_list(self):
        self.selected_zips.clear()
        self.restore_list.delete("0.0", "end")
        self.restore_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")

    def get_current_path(self):
        return os.path.join(self.path_entry.get(), self.selector_var.get())

    def update_file_list(self, *_):
        path = self.get_current_path()
        for widget in self.file_list.winfo_children():
            widget.after_idle(widget.destroy)
        self.file_checkboxes.clear()

        if os.path.exists(path):
            files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))
                     and os.path.splitext(f)[1].lower() not in self.excluded_ext]

            for f in files:
                var = ctk.BooleanVar(value=True)
                cb = ctk.CTkCheckBox(self.file_list, text=f, variable=var)
                cb.pack(anchor="w", padx=5, pady=2)
                self.file_checkboxes[f] = var

            self.backup_btn.configure(state="normal" if files else "disabled")

    def select_all_files(self):
        for v in self.file_checkboxes.values():
            v.set(True)

    def deselect_all_files(self):
        for v in self.file_checkboxes.values():
            v.set(False)

    def browse_path(self):
        d = filedialog.askdirectory()
        if d:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, d)
            self.update_file_list()

    def select_dest_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_dir = path
            self.save_backup_path()

    def do_backup(self):
        if not self.dest_dir:
            self.dest_dir = filedialog.askdirectory()
            if not self.dest_dir:
                return
            
            self.save_backup_path()

        selected_files = [
            f for f, var in self.file_checkboxes.items()
            if var.get()
        ]
        
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select at least one file to backup.", parent=self)
            return

        zip_name = f"{self.selector_var.get()}_{datetime.now().strftime('%d-%m-%Y')}.zip"
        zip_path = os.path.join(self.dest_dir, zip_name)
        path = self.get_current_path()

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in selected_files:
                    file_path = os.path.join(path, f)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        zf.write(file_path, f)

            messagebox.showinfo("Success", f"Backup created at {zip_path}\n\nFiles backed up: {len(selected_files)}", parent=self)

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def open_preferences(self):
        pref = ctk.CTkToplevel(self)
        pref.title("Preferences")
        pref.iconbitmap(resource_path("OBF_101.ico"))
        pref.transient(self)
        pref.grab_set()

        pref.update_idletasks()
        w, h = 310, 210
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (h // 2)
        pref.geometry(f"{w}x{h}+{x}+{y}")
        pref.attributes("-topmost", True)

        frame = ctk.CTkFrame(pref)
        frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(frame, text="Theme:").pack(side="left", padx=10)
        ctk.CTkOptionMenu(
            frame,
            values=["System", "Dark", "Light"],
            variable=self.theme_var,
            command=self.change_theme
        ).pack(side="left", padx=10)

        shortcut_frame = ctk.CTkFrame(pref)
        shortcut_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(shortcut_frame, text="Create Desktop Shortcut", command=self.create_desktop_shortcut).pack(fill="x")

        saved_frame = ctk.CTkFrame(pref)
        saved_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(saved_frame, text="Open %LOCALAPPDATA%\\OBF\\Saved\\", command=self.open_saved_folder).pack(fill="x")

    def create_desktop_shortcut(self):
        try:
            import win32com.client
            import winshell

            shell = win32com.client.Dispatch("WScript.Shell")
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "BOTN Backup ~ Restore.lnk")

            if os.path.exists(shortcut_path):
                messagebox.showwarning("Shortcut Exists", "A shortcut already exists on the desktop.", parent=self)
                return

            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.WorkingDirectory = os.path.dirname(sys.executable)
            shortcut.IconLocation = resource_path("OBF_101.ico")
            shortcut.Description = "BOTN Backup ~ Restore"
            shortcut.Save()

            messagebox.showinfo("Success", "Shortcut created successfully!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create shortcut:\n{str(e)}", parent=self)

    def open_saved_folder(self):
        saved_path = os.path.expandvars(r"%LOCALAPPDATA%\OBF\Saved")
        try:
            os.startfile(saved_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}", parent=self)

    def change_theme(self, *_):
        ctk.set_appearance_mode(self.theme_var.get().lower())

    def load_backup_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\BOTNBackup")
            self.dest_dir = winreg.QueryValueEx(key, "SavePath")[0]
        except Exception:
            self.dest_dir = None

    def save_backup_path(self):
        if not self.dest_dir:
            return
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\BOTNBackup")
            winreg.SetValueEx(key, "SavePath", 0, winreg.REG_SZ, self.dest_dir)
            winreg.CloseKey(key)
        except Exception:
            pass

    def load_position(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\BOTNBackup")
            x = winreg.QueryValueEx(key, "X")[0]
            y = winreg.QueryValueEx(key, "Y")[0]
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def save_position(self):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\BOTNBackup")
            winreg.SetValueEx(key, "X", 0, winreg.REG_DWORD, self.winfo_x())
            winreg.SetValueEx(key, "Y", 0, winreg.REG_DWORD, self.winfo_y())
            winreg.CloseKey(key)
        except Exception:
            pass

    def on_closing(self):
        self.save_position()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
