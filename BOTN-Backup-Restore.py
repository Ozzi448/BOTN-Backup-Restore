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
        self.excluded_ext = {".jpg", ".jpeg", ".gif", ".png", ".txt", ".md"}

        self.load_position()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        menubar = Menu(self)
        self.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Preferences", accelerator="Ctrl+P", command=self.open_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self.quit)

        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(pady=10, fill="x", padx=10)
        self.selector_var = ctk.StringVar(value="CharacterPresets")
        ctk.CTkRadioButton(selector_frame, text="CharacterPresets",
                           variable=self.selector_var, value="CharacterPresets").pack(side="left", padx=10)
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
        for sub in ("CharacterPresets", "SaveGames"):
            os.makedirs(os.path.join(self.base_path, sub), exist_ok=True)
        self.path_entry.insert(0, self.base_path)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=10, fill="both", expand=True, padx=10)

        backup_tab = self.tabview.add("Backup")
        restore_tab = self.tabview.add("Restore")

        self.file_list = ctk.CTkTextbox(backup_tab, height=200)
        self.file_list.pack(pady=10, fill="both", expand=True)

        btn_frame = ctk.CTkFrame(backup_tab)
        btn_frame.pack(fill="x", pady=5)
        self.backup_btn = ctk.CTkButton(btn_frame, text="Backup",
                                        command=self.do_backup, state="disabled")
        self.backup_btn.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save to...", command=self.select_dest_dir).pack(side="left", padx=5)
        self.dest_dir = None

        self.restore_list = ctk.CTkTextbox(restore_tab, height=200)
        self.restore_list.pack(pady=10, fill="both", expand=True)
        self.restore_list._textbox.drop_target_register(DND_FILES)
        self.restore_list._textbox.dnd_bind("<<Drop>>", self.handle_drop)

        restore_btn_frame = ctk.CTkFrame(restore_tab)
        restore_btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(restore_btn_frame, text="Add Archive",
                      command=self.add_archive).pack(side="left", padx=5)
        self.restore_btn = ctk.CTkButton(restore_btn_frame, text="Restore",
                                         command=self.do_restore, state="disabled")
        self.restore_btn.pack(side="left", padx=5)
        self.clear_btn = ctk.CTkButton(restore_btn_frame, text="Clear",
                                       command=self.clear_restore_list, state="disabled")
        self.clear_btn.pack(side="left", padx=5)

        self.selected_zips = []
        self.update_file_list()

    def open_preferences(self):
        pref = ctk.CTkToplevel(self)
        pref.title("Preferences")
        pref.iconbitmap(resource_path("OBF_101.ico"))
        pref.transient(self)
        pref.grab_set()

        pref.update_idletasks()
        w, h = 300, 120
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

    def change_theme(self, *_):
        ctk.set_appearance_mode(self.theme_var.get().lower())

    def load_position(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\BOTNBackup", 0, winreg.KEY_READ)
            x = winreg.QueryValueEx(key, "X")[0]
            y = winreg.QueryValueEx(key, "Y")[0]
            winreg.CloseKey(key)
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

    def copy_flat(self, src_path, dest_dir):
        dst = os.path.join(dest_dir, os.path.basename(src_path))
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst)

    def handle_drop(self, event):
        for f in self.tk.splitlist(event.data):
            if f.lower().endswith((".zip", ".rar", ".7z", ".sav")):
                self.selected_zips.append(f)
                self.restore_list.insert("end", os.path.basename(f) + "\n")
        if self.selected_zips:
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

        try:
            for arc in self.selected_zips:

                if arc.lower().endswith(".sav"):
                    os.makedirs(path, exist_ok=True)
                    shutil.copy2(arc, os.path.join(path, os.path.basename(arc)))
                    continue

                if arc.lower().endswith(".zip"):
                    with zipfile.ZipFile(arc) as zf:
                        for m in zf.namelist():
                            if m.endswith("/"):
                                continue
                            if os.path.splitext(m)[1].lower() in self.excluded_ext:
                                continue

                            zf.extract(m, path)
                            if m.lower().endswith(".sav"):
                                self.copy_flat(os.path.join(path, m), path)

                elif arc.lower().endswith(".rar"):
                    with rarfile.RarFile(arc) as rf:
                        for m in rf.namelist():
                            if m.endswith("/"):
                                continue
                            if os.path.splitext(m)[1].lower() in self.excluded_ext:
                                continue

                            rf.extract(m, path)
                            if m.lower().endswith(".sav"):
                                self.copy_flat(os.path.join(path, m), path)

                elif arc.lower().endswith(".7z"):
                    with py7zr.SevenZipFile(arc, mode="r") as z:
                        members = [
                            m for m in z.getnames()
                            if not m.endswith("/")
                            and os.path.splitext(m)[1].lower() not in self.excluded_ext
                        ]
                        if members:
                            z.extract(path=path, targets=members)
                            for m in members:
                                if m.lower().endswith(".sav"):
                                    self.copy_flat(os.path.join(path, m), path)

            messagebox.showinfo("Success", "Restore completed", parent=self)
            self.selected_zips.clear()
            self.restore_list.delete("0.0", "end")
            self.restore_btn.configure(state="disabled")
            self.clear_btn.configure(state="disabled")
            self.update_file_list()

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def clear_restore_list(self):
        self.selected_zips.clear()
        self.restore_list.delete("0.0", "end")
        self.restore_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")

    def get_current_path(self):
        return os.path.join(self.path_entry.get(), self.selector_var.get())

    def update_file_list(self, *_):
        path = self.get_current_path()
        self.file_list.delete("0.0", "end")

        if os.path.exists(path):
            files = [
                f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
                and os.path.splitext(f)[1].lower() not in self.excluded_ext
            ]

            if files:
                self.backup_btn.configure(state="normal")
                for f in files:
                    self.file_list.insert("end", f + "\n")
            else:
                self.backup_btn.configure(state="disabled")

    def browse_path(self):
        d = filedialog.askdirectory()
        if d:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, d)
            self.update_file_list()

    def select_dest_dir(self):
        self.dest_dir = filedialog.askdirectory()

    def do_backup(self):
        if not self.dest_dir:
            self.dest_dir = filedialog.askdirectory()
            if not self.dest_dir:
                return

        zip_name = f"{self.selector_var.get()}_{datetime.now().strftime('%d-%m-%Y')}.zip"
        zip_path = os.path.join(self.dest_dir, zip_name)
        path = self.get_current_path()

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in os.listdir(path):
                    if os.path.splitext(f)[1].lower() not in self.excluded_ext:
                        zf.write(os.path.join(path, f), f)

            messagebox.showinfo("Success", f"Backup created at {zip_path}", parent=self)

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

if __name__ == "__main__":
    app = App()
    app.mainloop()
