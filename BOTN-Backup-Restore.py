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
        
        # Required files for verification
        self.required_character_presets = {
            "CP_Human", "CP_Foxen", "CP_Vulwarg", "CP_Neko", "CP_Thriae", 
            "CP_Harpy", "CP_Bovaur", "CP_Sylvan", "CP_Dragon", "CP_Titan", 
            "CP_Demon", "CP_Seraphim", "CP_Formurian", "CP_Starfallen", "CP_Risu", "CP_Hybrid"
        }
        self.required_savegames = {f"{i}.sav" for i in range(10)} | {"GameActions.sav"}

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

        # Create scrollable frame for file checkboxes
        file_list_frame = ctk.CTkScrollableFrame(backup_tab, height=200)
        file_list_frame.pack(pady=10, fill="both", expand=True)
        self.file_list = file_list_frame
        self.file_checkboxes = {}  # Store checkboxes: {filename: checkbox_var}

        btn_frame = ctk.CTkFrame(backup_tab)
        btn_frame.pack(fill="x", pady=5)
        self.backup_btn = ctk.CTkButton(btn_frame, text="Backup",
                                        command=self.do_backup, state="disabled")
        self.backup_btn.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save to...", command=self.select_dest_dir).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Select All", command=self.select_all_files).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Deselect All", command=self.deselect_all_files).pack(side="left", padx=5)
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

    def verify_archive(self, archive_path):
        """Verify archive contains required files based on current selector type.
        
        This function checks the CONTENTS of the archive (files inside .zip/.rar/.7z),
        NOT the archive filename itself.
        
        For SaveGames: Requires 0.sav and GameActions.sav (other saves optional).
                      Fails if any CP_ files are found.
        For CharacterPresets: Requires all CP_ files to be present.
        """
        archive_files = []
        archive_files_lower = []
        
        try:
            # Extract list of files INSIDE the archive (not the archive name)
            if archive_path.lower().endswith(".zip"):
                with zipfile.ZipFile(archive_path) as zf:
                    # zf.namelist() returns list of files inside the zip archive
                    archive_files = [m for m in zf.namelist() if not m.endswith("/")]
                    archive_files_lower = [m.lower() for m in archive_files]
            elif archive_path.lower().endswith(".rar"):
                with rarfile.RarFile(archive_path) as rf:
                    # rf.namelist() returns list of files inside the rar archive
                    archive_files = [m for m in rf.namelist() if not m.endswith("/")]
                    archive_files_lower = [m.lower() for m in archive_files]
            elif archive_path.lower().endswith(".7z"):
                with py7zr.SevenZipFile(archive_path, mode="r") as z:
                    # z.getnames() returns list of files inside the 7z archive
                    archive_files = [m for m in z.getnames() if not m.endswith("/")]
                    archive_files_lower = [m.lower() for m in archive_files]
            else:
                return True, []  # .sav files don't need verification
        except Exception as e:
            return False, [f"Error reading archive: {str(e)}"]
        
        # Different verification logic for SaveGames vs CharacterPresets
        if self.selector_var.get() == "SaveGames":
            # For SaveGames: Must have 0.sav and GameActions.sav, must NOT have CP_ files
            errors = []
            
            # Check for required files: 0.sav and GameActions.sav
            has_0_sav = False
            has_gameactions = False
            
            # Check for forbidden CP_ files
            cp_files_found = []
            
            for arch_file in archive_files_lower:
                basename = os.path.basename(arch_file)
                name_without_ext = os.path.splitext(basename)[0]
                
                # Check for required files
                if basename == "0.sav":
                    has_0_sav = True
                if basename == "gameactions.sav":
                    has_gameactions = True
                
                # Check for forbidden CP_ files
                if name_without_ext.startswith("cp_"):
                    cp_files_found.append(os.path.basename(arch_file))
            
            # Build error messages
            if not has_0_sav:
                errors.append("Missing required file: 0.sav")
            if not has_gameactions:
                errors.append("Missing required file: GameActions.sav")
            if cp_files_found:
                errors.append(f"Archive contains CharacterPreset files (not allowed in SaveGames): {', '.join(cp_files_found)}")
            
            return len(errors) == 0, errors
        
        elif self.selector_var.get() == "CharacterPresets":
            # For CharacterPresets: Must have all required CP_ files
            required_files = self.required_character_presets
            missing_files = []
            
            for req_file in required_files:
                found = False
                req_lower = req_file.lower()
                
                # Iterate through files found INSIDE the archive
                for arch_file in archive_files_lower:
                    # Get just the filename (basename) from the path inside the archive
                    basename = os.path.basename(arch_file)
                    name_without_ext = os.path.splitext(basename)[0]
                    
                    # For CP files, check if filename (without extension) starts with the required prefix
                    # This handles cases like:
                    # - CP_Human_Breeder_Female_Mine.sav matching CP_Human
                    # - CP_Human.sav matching CP_Human
                    # - CP_Human_Anything_Else.sav matching CP_Human
                    if name_without_ext == req_lower or name_without_ext.startswith(req_lower + "_"):
                        found = True
                        break
                
                if not found:
                    missing_files.append(req_file)
            
            return len(missing_files) == 0, missing_files
        
        return True, []  # No verification needed

    def copy_flat(self, src_path, dest_dir):
        dst = os.path.join(dest_dir, os.path.basename(src_path))
        # Don't copy if source and destination are the same
        if os.path.abspath(src_path) == os.path.abspath(dst):
            return
        if os.path.exists(src_path):
            try:
                shutil.copy2(src_path, dst)
            except PermissionError:
                # File is locked, skip it
                raise PermissionError(f"File is locked and cannot be copied: {os.path.basename(src_path)}")

    def handle_drop(self, event):
        for f in self.tk.splitlist(event.data):
            if f.lower().endswith((".zip", ".rar", ".7z", ".sav")):
                # Verify archive if it's not a standalone .sav file
                if not f.lower().endswith(".sav"):
                    is_valid, missing = self.verify_archive(f)
                    if not is_valid:
                        messagebox.showerror(
                            "Invalid Archive",
                            f"Archive '{os.path.basename(f)}' is missing required files for {self.selector_var.get()}:\n\n" +
                            ", ".join(missing) + "\n\nFile not added to selection.",
                            parent=self
                        )
                        continue
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
            # Verify archive if it's not a standalone .sav file
            if not f.lower().endswith(".sav"):
                is_valid, missing = self.verify_archive(f)
                if not is_valid:
                    messagebox.showerror(
                        "Invalid Archive",
                        f"Archive '{os.path.basename(f)}' is missing required files for {self.selector_var.get()}:\n\n" +
                        ", ".join(missing) + "\n\nFile not added to selection.",
                        parent=self
                    )
                    continue
            self.selected_zips.append(f)
            self.restore_list.insert("end", os.path.basename(f) + "\n")
        if self.selected_zips:
            self.restore_btn.configure(state="normal")
            self.clear_btn.configure(state="normal")

    def do_restore(self):
        path = self.get_current_path()
        os.makedirs(path, exist_ok=True)

        errors = []
        try:
            for arc in self.selected_zips:
                try:
                    if arc.lower().endswith(".sav"):
                        dest_file = os.path.join(path, os.path.basename(arc))
                        try:
                            shutil.copy2(arc, dest_file)
                        except Exception as e:
                            errors.append(f"Error copying {os.path.basename(arc)}: {str(e)}")
                            continue
                        continue

                    if arc.lower().endswith(".zip"):
                        with zipfile.ZipFile(arc) as zf:
                            # First, extract all files
                            sav_files_to_flatten = []
                            for m in zf.namelist():
                                if m.endswith("/"):
                                    continue
                                if os.path.splitext(m)[1].lower() in self.excluded_ext:
                                    continue

                                try:
                                    # Normalize path separators for cross-platform compatibility
                                    normalized_m = m.replace("/", os.sep).replace("\\", os.sep)
                                    
                                    # Remove existing file if it exists to avoid conflicts
                                    dest_path = os.path.join(path, normalized_m)
                                    if os.path.exists(dest_path):
                                        try:
                                            os.remove(dest_path)
                                        except Exception:
                                            pass  # If we can't remove it, try extracting anyway
                                    
                                    zf.extract(m, path)
                                    
                                    # Track .sav files in nested directories for flattening
                                    if m.lower().endswith(".sav"):
                                        extracted_path = os.path.join(path, normalized_m)
                                        if os.path.exists(extracted_path) and (os.sep in normalized_m or "/" in m):
                                            sav_files_to_flatten.append(extracted_path)
                                except Exception as e:
                                    errors.append(f"Error extracting {m} from {os.path.basename(arc)}: {str(e)}")
                                    continue
                            
                            # Now flatten nested .sav files
                            for extracted_path in sav_files_to_flatten:
                                try:
                                    self.copy_flat(extracted_path, path)
                                except Exception as e:
                                    errors.append(f"Error copying {os.path.basename(extracted_path)}: {str(e)}")

                    elif arc.lower().endswith(".rar"):
                        with rarfile.RarFile(arc) as rf:
                            # First, extract all files
                            sav_files_to_flatten = []
                            for m in rf.namelist():
                                if m.endswith("/"):
                                    continue
                                if os.path.splitext(m)[1].lower() in self.excluded_ext:
                                    continue

                                try:
                                    # Normalize path separators for cross-platform compatibility
                                    normalized_m = m.replace("/", os.sep).replace("\\", os.sep)
                                    
                                    # Remove existing file if it exists to avoid conflicts
                                    dest_path = os.path.join(path, normalized_m)
                                    if os.path.exists(dest_path):
                                        try:
                                            os.remove(dest_path)
                                        except Exception:
                                            pass  # If we can't remove it, try extracting anyway
                                    
                                    rf.extract(m, path)
                                    
                                    # Track .sav files in nested directories for flattening
                                    if m.lower().endswith(".sav"):
                                        extracted_path = os.path.join(path, normalized_m)
                                        if os.path.exists(extracted_path) and (os.sep in normalized_m or "/" in m):
                                            sav_files_to_flatten.append(extracted_path)
                                except Exception as e:
                                    errors.append(f"Error extracting {m} from {os.path.basename(arc)}: {str(e)}")
                                    continue
                            
                            # Now flatten nested .sav files
                            for extracted_path in sav_files_to_flatten:
                                try:
                                    self.copy_flat(extracted_path, path)
                                except Exception as e:
                                    errors.append(f"Error copying {os.path.basename(extracted_path)}: {str(e)}")

                    elif arc.lower().endswith(".7z"):
                        with py7zr.SevenZipFile(arc, mode="r") as z:
                            members = [
                                m for m in z.getnames()
                                if not m.endswith("/")
                                and os.path.splitext(m)[1].lower() not in self.excluded_ext
                            ]
                            if members:
                                try:
                                    # Remove existing files to avoid conflicts
                                    for m in members:
                                        normalized_m = m.replace("/", os.sep).replace("\\", os.sep)
                                        dest_path = os.path.join(path, normalized_m)
                                        if os.path.exists(dest_path):
                                            try:
                                                os.remove(dest_path)
                                            except Exception:
                                                pass  # If we can't remove it, try extracting anyway
                                    
                                    # Extract all files
                                    z.extract(path=path, targets=members)
                                    
                                    # Now flatten nested .sav files
                                    for m in members:
                                        if m.lower().endswith(".sav"):
                                            normalized_m = m.replace("/", os.sep).replace("\\", os.sep)
                                            extracted_path = os.path.join(path, normalized_m)
                                            if os.path.exists(extracted_path) and (os.sep in normalized_m or "/" in m):
                                                try:
                                                    self.copy_flat(extracted_path, path)
                                                except Exception as e:
                                                    errors.append(f"Error copying {m}: {str(e)}")
                                except Exception as e:
                                    errors.append(f"Error extracting from {os.path.basename(arc)}: {str(e)}")
                                    continue

                except Exception as e:
                    errors.append(f"Error processing {os.path.basename(arc)}: {str(e)}")
                    continue

            if errors:
                error_msg = "Restore completed with some errors:\n\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    error_msg += f"\n... and {len(errors) - 10} more errors"
                messagebox.showwarning("Restore completed with errors", error_msg, parent=self)
            else:
                messagebox.showinfo("Success", "Restore completed", parent=self)
            
            self.selected_zips.clear()
            self.restore_list.delete("0.0", "end")
            self.restore_btn.configure(state="disabled")
            self.clear_btn.configure(state="disabled")
            self.update_file_list()

        except Exception as e:
            messagebox.showerror("Error", f"Fatal error: {str(e)}", parent=self)

    def clear_restore_list(self):
        self.selected_zips.clear()
        self.restore_list.delete("0.0", "end")
        self.restore_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")

    def get_current_path(self):
        return os.path.join(self.path_entry.get(), self.selector_var.get())

    def update_file_list(self, *_):
        path = self.get_current_path()
        # Clear existing checkboxes
        for widget in self.file_list.winfo_children():
            widget.destroy()
        self.file_checkboxes.clear()

        if os.path.exists(path):
            files = [
                f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
                and os.path.splitext(f)[1].lower() not in self.excluded_ext
            ]

            if files:
                # Create checkboxes for each file
                for f in sorted(files):
                    var = ctk.BooleanVar(value=True)  # Default to selected
                    checkbox = ctk.CTkCheckBox(self.file_list, text=f, variable=var)
                    checkbox.pack(anchor="w", padx=5, pady=2)
                    self.file_checkboxes[f] = var
                self.backup_btn.configure(state="normal")
            else:
                self.backup_btn.configure(state="disabled")

    def select_all_files(self):
        for var in self.file_checkboxes.values():
            var.set(True)

    def deselect_all_files(self):
        for var in self.file_checkboxes.values():
            var.set(False)

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

        # Get selected files
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

if __name__ == "__main__":
    app = App()
    app.mainloop()
