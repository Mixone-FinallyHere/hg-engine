#!/usr/bin/env python3
"""
hg-engine Data Editors Launcher
===============================
Main launcher for all hg-engine data editing tools.

Usage:
    python main.py                 # Launch the main menu
    python main.py pokemon         # Launch Pokemon editor directly
    python main.py moveset         # Launch Moveset editor directly
    python main.py trainer         # Launch Trainer editor directly
    python main.py changelog       # Generate changelog
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class EditorLauncher:
    """Main launcher window for all editors."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("hg-engine Data Editors")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the launcher UI."""
        # Header
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill=tk.X)
        
        ttk.Label(
            header,
            text="hg-engine Data Editors",
            font=('Arial', 18, 'bold')
        ).pack()
        
        ttk.Label(
            header,
            text="Tools for editing Pokemon HeartGold ROM data",
            font=('Arial', 10)
        ).pack(pady=(5, 0))
        
        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20)
        
        # Editor buttons
        buttons_frame = ttk.Frame(self.root, padding=20)
        buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Save button (always visible)
        self.save_button = ttk.Button(buttons_frame, text="💾 Save", command=self._save_current_editor, width=25)
        self.save_button.pack(pady=(0, 10))
        self.save_button.state(['disabled'])  # Disabled until an editor is launched

        editors = [
            ("🎮 Pokemon Data Editor", "Edit Pokemon stats, types, and abilities & learnsets", self._launch_pokemon),
            ("📜 Moveset Editor", "Edit Pokemon learnsets (standalone)", self._launch_moveset),
            ("👤 Trainer Editor", "Edit trainer teams and AI", self._launch_trainer),
            ("📋 Changelog Manager", "Compare versions and generate changelogs", self._launch_changelog),
        ]
        
        for title, desc, command in editors:
            frame = ttk.Frame(buttons_frame)
            frame.pack(fill=tk.X, pady=5)
            
            btn = ttk.Button(frame, text=title, command=command, width=25)
            btn.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=desc, foreground='gray').pack(side=tk.LEFT, padx=10)
        
        # Footer
        footer = ttk.Frame(self.root, padding=10)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(
            footer,
            text="Part of hg-engine - Battle engine upgrade for Pokemon HeartGold",
            font=('Arial', 8),
            foreground='gray'
        ).pack()
    
    def _save_current_editor(self):
        """Call save() on the current editor if available."""
        if hasattr(self, 'current_editor') and self.current_editor:
            try:
                if hasattr(self.current_editor, 'save'):
                    result = self.current_editor.save()
                    if result:
                        messagebox.showinfo("Save", "Data saved successfully.")
                    else:
                        messagebox.showwarning("Save", "Save failed or not implemented.")
                else:
                    messagebox.showwarning("Save", "Current editor does not support saving.")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error during save: {e}")
        else:
            messagebox.showwarning("Save", "No editor is currently open.")

    def _launch_pokemon(self):
        """Launch the Pokemon editor."""
        try:
            from pokemon_editor import PokemonEditor
            self.current_editor = PokemonEditor(self.root)
            self.save_button.state(['!disabled'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Pokemon editor: {e}")
            import traceback
            traceback.print_exc()
    
    def _launch_moveset(self):
        """Launch the moveset editor."""
        try:
            from moveset_editor import MovesetEditor
            self.current_editor = MovesetEditor(self.root)
            self.save_button.state(['!disabled'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Moveset editor: {e}")
            import traceback
            traceback.print_exc()
    
    def _launch_trainer(self):
        """Launch the trainer editor."""
        try:
            from trainer_editor import TrainerEditor
            self.current_editor = TrainerEditor(self.root)
            self.save_button.state(['!disabled'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Trainer editor: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_changelog(self):
        """Generate a changelog (legacy method - redirects to changelog UI)."""
        self._launch_changelog()
    
    def _launch_changelog(self):
        """Launch the changelog manager UI."""
        try:
            from changelog_ui import ChangelogEditor
            self.current_editor = ChangelogEditor(self.root)
            self.save_button.state(['disabled'])  # Changelog editor does not support save
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Changelog editor: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the launcher."""
        self.root.mainloop()


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    if not args:
        # Launch main menu
        launcher = EditorLauncher()
        launcher.run()
    else:
        cmd = args[0].lower()
        
        if cmd == 'pokemon':
            from pokemon_editor import PokemonEditor
            editor = PokemonEditor()
            editor.run()
        
        elif cmd == 'moveset':
            from moveset_editor import MovesetEditor
            editor = MovesetEditor()
            editor.run()
        
        elif cmd == 'trainer':
            from trainer_editor import TrainerEditor
            editor = TrainerEditor()
            editor.run()
        
        elif cmd == 'changelog':
            from changelog_ui import ChangelogEditor
            editor = ChangelogEditor()
            editor.run()
        
        elif cmd == 'download-vanilla':
            from common.changelog import ChangelogGenerator
            generator = ChangelogGenerator()
            
            def progress(msg, pct):
                print(f"{msg} ({int(pct*100)}%)")
            
            if generator.download_vanilla_from_github(progress):
                print("Vanilla data downloaded successfully!")
            else:
                print("Failed to download vanilla data")
                sys.exit(1)
        
        elif cmd == 'save-vanilla':
            from common.changelog import ChangelogGenerator
            generator = ChangelogGenerator()
            generator.save_vanilla_snapshot()
            print("Vanilla snapshot saved!")
        
        elif cmd == 'snapshot':
            from common.changelog import ChangelogGenerator
            name = args[1] if len(args) > 1 else "unnamed"
            desc = args[2] if len(args) > 2 else ""
            generator = ChangelogGenerator()
            snapshot = generator.create_version_snapshot(name, desc)
            print(f"Snapshot created: {snapshot.name}")
        
        else:
            print(f"Unknown command: {cmd}")
            print("Available commands: pokemon, moveset, trainer, changelog, download-vanilla, save-vanilla, snapshot <name> [desc]")
            sys.exit(1)


if __name__ == "__main__":
    main()
