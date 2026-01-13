"""
Changelog Generator UI
======================
Tkinter GUI for generating and viewing changelogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base_editor import BaseEditor
from common.changelog import ChangelogGenerator, Changelog, VersionSnapshot


class ChangelogEditor(BaseEditor):
    """GUI for generating and viewing changelogs."""
    
    def __init__(self, master: Optional[tk.Tk] = None):
        self.generator = ChangelogGenerator()
        self.current_changelog: Optional[Changelog] = None
        
        super().__init__(master, title="Changelog Generator - hg-engine")
        
        self._refresh_versions()
    
    def _setup_custom_menus(self):
        """Add changelog-specific menu items."""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Download Vanilla from GitHub", command=self._download_vanilla)
        tools_menu.add_command(label="Create Version Snapshot", command=self._create_snapshot)
        tools_menu.add_separator()
        tools_menu.add_command(label="Export Changelog...", command=self._export_changelog)
    
    def _setup_custom_toolbar(self):
        """Add changelog-specific toolbar items."""
        ttk.Button(self.toolbar, text="Refresh", command=self._refresh_versions).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Get Vanilla", command=self._download_vanilla).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="New Snapshot", command=self._create_snapshot).pack(side=tk.LEFT, padx=2)
    
    def _setup_detail_view(self):
        """Setup the changelog UI."""
        # Remove the list panel since we don't need it in the same way
        self.list_frame.pack_forget()
        
        # Top frame - version selection
        selection_frame = ttk.LabelFrame(self.detail_content, text="Compare Versions", padding=10)
        selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # From version
        from_frame = ttk.Frame(selection_frame)
        from_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(from_frame, text="From:", width=10).pack(side=tk.LEFT)
        self.from_version_var = tk.StringVar(value="vanilla")
        self.from_version_combo = ttk.Combobox(from_frame, textvariable=self.from_version_var, 
                                                values=["vanilla"], width=30, state='readonly')
        self.from_version_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # To version
        to_frame = ttk.Frame(selection_frame)
        to_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(to_frame, text="To:", width=10).pack(side=tk.LEFT)
        self.to_version_var = tk.StringVar(value="current")
        self.to_version_combo = ttk.Combobox(to_frame, textvariable=self.to_version_var,
                                              values=["current"], width=30, state='readonly')
        self.to_version_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Generate button
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Generate Changelog", command=self._generate_changelog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Markdown", command=self._export_markdown).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export JSON", command=self._export_json).pack(side=tk.LEFT, padx=5)
        
        # Progress bar (hidden by default)
        self.progress_frame = ttk.Frame(selection_frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                            maximum=1.0, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        # Versions list
        versions_frame = ttk.LabelFrame(self.detail_content, text="Saved Versions", padding=10)
        versions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        columns = ('name', 'created', 'description')
        self.versions_tree = ttk.Treeview(versions_frame, columns=columns, show='headings', height=5)
        self.versions_tree.heading('name', text='Name')
        self.versions_tree.heading('created', text='Created')
        self.versions_tree.heading('description', text='Description')
        self.versions_tree.column('name', width=100)
        self.versions_tree.column('created', width=150)
        self.versions_tree.column('description', width=300)
        self.versions_tree.pack(fill=tk.X)
        
        versions_buttons = ttk.Frame(versions_frame)
        versions_buttons.pack(fill=tk.X, pady=5)
        ttk.Button(versions_buttons, text="Delete Selected", command=self._delete_version).pack(side=tk.LEFT)
        
        # Changelog output
        output_frame = ttk.LabelFrame(self.detail_content, text="Changelog Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Summary
        self.summary_label = ttk.Label(output_frame, text="No changelog generated yet", font=('Arial', 10))
        self.summary_label.pack(anchor=tk.W, pady=5)
    
    def _refresh_versions(self):
        """Refresh the list of available versions."""
        versions = self.generator.list_versions()
        
        # Update treeview
        for item in self.versions_tree.get_children():
            self.versions_tree.delete(item)
        
        for v in versions:
            self.versions_tree.insert('', tk.END, values=(v.name, v.created_at[:19] if v.created_at else '', v.description))
        
        # Update combobox values
        version_names = [v.name for v in versions]
        
        from_values = version_names + ["current"]
        to_values = ["current"] + version_names
        
        self.from_version_combo['values'] = from_values
        self.to_version_combo['values'] = to_values
        
        # Check if vanilla exists
        if not self.generator.has_vanilla_data():
            self.set_status("Vanilla data not found. Click 'Get Vanilla' to download from GitHub.")
        else:
            self.set_status(f"Found {len(versions)} version(s)")
    
    def _download_vanilla(self):
        """Download vanilla data from GitHub."""
        if self.generator.has_vanilla_data():
            result = messagebox.askyesno(
                "Vanilla Data Exists",
                "Vanilla data already exists. Re-download and replace it?"
            )
            if not result:
                return
        
        # Show progress
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        def download_thread():
            def progress_callback(message: str, progress: float):
                self.progress_var.set(progress)
                self.progress_label.config(text=message)
                self.root.update_idletasks()
            
            success = self.generator.download_vanilla_from_github(progress_callback)
            
            # Hide progress on main thread
            self.root.after(100, lambda: self._download_complete(success))
        
        thread = threading.Thread(target=download_thread)
        thread.start()
    
    def _download_complete(self, success: bool):
        """Handle download completion."""
        self.progress_frame.pack_forget()
        
        if success:
            messagebox.showinfo("Success", "Vanilla data downloaded successfully!")
            self._refresh_versions()
        else:
            messagebox.showerror("Error", "Failed to download vanilla data. Check your internet connection.")
    
    def _create_snapshot(self):
        """Create a new version snapshot."""
        dialog = SnapshotDialog(self.root)
        if dialog.result:
            name, description = dialog.result
            try:
                snapshot = self.generator.create_version_snapshot(name, description)
                messagebox.showinfo("Success", f"Created snapshot: {snapshot.name}")
                self._refresh_versions()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create snapshot: {e}")
    
    def _delete_version(self):
        """Delete the selected version."""
        selection = self.versions_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.versions_tree.item(item, 'values')
        name = values[0]
        
        if name == "vanilla":
            messagebox.showwarning("Warning", "Cannot delete vanilla baseline")
            return
        
        result = messagebox.askyesno("Confirm", f"Delete version '{name}'?")
        if result:
            if self.generator.delete_version(name):
                messagebox.showinfo("Success", f"Deleted version: {name}")
                self._refresh_versions()
    
    def _generate_changelog(self):
        """Generate changelog between selected versions."""
        from_version = self.from_version_var.get()
        to_version = self.to_version_var.get()
        
        if from_version == to_version:
            messagebox.showwarning("Warning", "Please select different versions to compare")
            return
        
        self.set_status("Generating changelog...")
        self.root.update_idletasks()
        
        try:
            self.current_changelog = self.generator.generate_changelog(from_version, to_version)
            
            # Display markdown output
            markdown = self.current_changelog.to_markdown()
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, markdown)
            
            # Update summary
            total = len(self.current_changelog.changes)
            added = len(self.current_changelog.filter_by_type(self.generator.ChangeType.ADDED if hasattr(self.generator, 'ChangeType') else None))
            
            from common.changelog import ChangeType
            added = len(self.current_changelog.filter_by_type(ChangeType.ADDED))
            modified = len(self.current_changelog.filter_by_type(ChangeType.MODIFIED))
            removed = len(self.current_changelog.filter_by_type(ChangeType.REMOVED))
            
            self.summary_label.config(
                text=f"Total: {total} changes | ✅ Added: {added} | 📝 Modified: {modified} | ❌ Removed: {removed}"
            )
            
            self.set_status(f"Generated changelog with {total} changes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate changelog: {e}")
            import traceback
            traceback.print_exc()
    
    def _export_markdown(self):
        """Export changelog as markdown file."""
        if not self.current_changelog:
            messagebox.showwarning("Warning", "Generate a changelog first")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfilename="CHANGELOG.md"
        )
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.current_changelog.to_markdown())
            messagebox.showinfo("Success", f"Saved to {filepath}")
    
    def _export_json(self):
        """Export changelog as JSON file."""
        if not self.current_changelog:
            messagebox.showwarning("Warning", "Generate a changelog first")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfilename="changelog.json"
        )
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.current_changelog.to_json())
            messagebox.showinfo("Success", f"Saved to {filepath}")
    
    def _export_changelog(self):
        """Open export dialog."""
        self._export_markdown()
    
    def _on_item_select(self, event):
        """Not used in changelog editor."""
        pass
    
    def _on_search(self):
        """Not used in changelog editor."""
        pass
    
    def save(self) -> bool:
        """Not applicable for changelog editor."""
        return True


class SnapshotDialog(tk.Toplevel):
    """Dialog for creating a new snapshot."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Version Snapshot")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Version Name:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Description (optional):").pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.desc_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Create", command=self._ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        
        self.wait_window()
    
    def _ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a version name")
            return
        self.result = (name, self.desc_var.get().strip())
        self.destroy()


def main():
    """Run the changelog editor standalone."""
    editor = ChangelogEditor()
    editor.run()


if __name__ == "__main__":
    main()
