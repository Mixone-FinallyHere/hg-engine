"""
Moveset/Learnset Editor
=======================
Tkinter GUI for editing Pokemon learnsets (level-up moves, TM/HM, egg moves, tutor moves).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base_editor import BaseEditor, LabeledEntry, LabeledCombobox, LabeledSpinbox
from common.json_handler import JSONHandler, LearnsetEntry
from common.constants import ConstantsLoader


class MovesetEditor(BaseEditor):
    """Editor for Pokemon learnsets (learnsets.json)."""
    
    def __init__(self, master: Optional[tk.Tk] = None):
        self.json_handler = JSONHandler()
        self.constants = ConstantsLoader()
        
        # Data
        self.learnset_data: Dict[str, LearnsetEntry] = {}
        self.filtered_list: List[str] = []
        self.current_species: Optional[str] = None
        self.move_names: List[str] = []
        
        super().__init__(master, title="Moveset Editor - hg-engine")
        
        # Load data on startup
        self._load_data()
    
    def _setup_custom_menus(self):
        """Add moveset-specific menu items."""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Add Level Move", command=self._add_level_move)
        tools_menu.add_command(label="Add TM/HM Move", command=self._add_tm_move)
        tools_menu.add_command(label="Sort Level Moves", command=self._sort_level_moves)
        tools_menu.add_separator()
        tools_menu.add_command(label="Find Pokemon with Move...", command=self._find_pokemon_with_move)
    
    def _setup_custom_toolbar(self):
        """Add moveset-specific toolbar items."""
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(self.toolbar, text="+ Level", command=self._add_level_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="+ TM/HM", command=self._add_tm_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="+ Egg", command=self._add_egg_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="+ Tutor", command=self._add_tutor_move).pack(side=tk.LEFT, padx=2)
    
    def _setup_detail_view(self):
        """Setup the learnset detail editing view."""
        # Species header
        self.species_label = ttk.Label(
            self.detail_content,
            text="Select a Pokemon",
            font=('Arial', 14, 'bold')
        )
        self.species_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # Create notebook for different move categories
        self.notebook = ttk.Notebook(self.detail_content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Level-up moves tab
        level_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(level_frame, text="Level-Up Moves")
        self._setup_level_moves_tab(level_frame)
        
        # TM/HM moves tab
        tm_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tm_frame, text="TM/HM Moves")
        self._setup_tm_moves_tab(tm_frame)
        
        # Egg moves tab
        egg_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(egg_frame, text="Egg Moves")
        self._setup_egg_moves_tab(egg_frame)
        
        # Tutor moves tab
        tutor_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tutor_frame, text="Tutor Moves")
        self._setup_tutor_moves_tab(tutor_frame)
    
    def _setup_level_moves_tab(self, parent: ttk.Frame):
        """Setup the level-up moves editing tab."""
        # Toolbar for this tab
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_level_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove Selected", command=self._remove_level_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Sort by Level", command=self._sort_level_moves).pack(side=tk.LEFT, padx=2)
        
        # Treeview for level moves
        columns = ('level', 'move')
        self.level_moves_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        self.level_moves_tree.heading('level', text='Level')
        self.level_moves_tree.heading('move', text='Move')
        self.level_moves_tree.column('level', width=60)
        self.level_moves_tree.column('move', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.level_moves_tree.yview)
        self.level_moves_tree.configure(yscrollcommand=scrollbar.set)
        
        self.level_moves_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-click to edit
        self.level_moves_tree.bind('<Double-1>', self._edit_level_move)
    
    def _setup_tm_moves_tab(self, parent: ttk.Frame):
        """Setup the TM/HM moves editing tab."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_tm_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove Selected", command=self._remove_tm_move).pack(side=tk.LEFT, padx=2)
        
        # Listbox for TM moves
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tm_moves_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.tm_moves_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tm_moves_list.yview)
    
    def _setup_egg_moves_tab(self, parent: ttk.Frame):
        """Setup the egg moves editing tab."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_egg_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove Selected", command=self._remove_egg_move).pack(side=tk.LEFT, padx=2)
        
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.egg_moves_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.egg_moves_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.egg_moves_list.yview)
    
    def _setup_tutor_moves_tab(self, parent: ttk.Frame):
        """Setup the tutor moves editing tab."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_tutor_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove Selected", command=self._remove_tutor_move).pack(side=tk.LEFT, padx=2)
        
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tutor_moves_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.tutor_moves_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tutor_moves_list.yview)
    
    def _load_data(self):
        """Load learnset data."""
        try:
            self.learnset_data = self.json_handler.load_learnsets()
            self._load_move_names()
            self._populate_list()
            self.set_status(f"Loaded learnsets for {len(self.learnset_data)} Pokemon")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load learnset data: {e}")
    
    def _load_move_names(self):
        """Load move names for dropdowns."""
        try:
            moves = self.constants.load_moves()
            self.move_names = sorted([k for k in moves.keys() if k.startswith('MOVE_')])
        except Exception as e:
            print(f"Warning: Could not load moves: {e}")
            self.move_names = []
    
    def _populate_list(self):
        """Populate the Pokemon list."""
        self.item_list.delete(0, tk.END)
        self.filtered_list = sorted(self.learnset_data.keys())
        
        for species in self.filtered_list:
            entry = self.learnset_data[species]
            level_count = len(entry.level_moves)
            tm_count = len(entry.machine_moves)
            self.item_list.insert(tk.END, f"{species} ({level_count}L/{tm_count}TM)")
    
    def _on_search(self):
        """Handle search input."""
        search_term = self.search_var.get().lower()
        
        self.item_list.delete(0, tk.END)
        self.filtered_list = []
        
        for species in sorted(self.learnset_data.keys()):
            if search_term and search_term not in species.lower():
                continue
            
            self.filtered_list.append(species)
            entry = self.learnset_data[species]
            level_count = len(entry.level_moves)
            tm_count = len(entry.machine_moves)
            self.item_list.insert(tk.END, f"{species} ({level_count}L/{tm_count}TM)")
        
        self.set_status(f"Showing {len(self.filtered_list)} of {len(self.learnset_data)} Pokemon")
    
    def _on_item_select(self, event):
        """Handle Pokemon selection."""
        selection = self.item_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.filtered_list):
            species = self.filtered_list[index]
            self._load_learnset(species)
    
    def _load_learnset(self, species: str):
        """Load a Pokemon's learnset into the editor."""
        if species not in self.learnset_data:
            return
        
        self.current_species = species
        entry = self.learnset_data[species]
        
        self.species_label.config(text=f"Learnset: {species}")
        
        # Clear all lists
        for item in self.level_moves_tree.get_children():
            self.level_moves_tree.delete(item)
        self.tm_moves_list.delete(0, tk.END)
        self.egg_moves_list.delete(0, tk.END)
        self.tutor_moves_list.delete(0, tk.END)
        
        # Populate level moves
        for move_data in entry.level_moves:
            if isinstance(move_data, dict):
                level = move_data.get('level', move_data.get('Level', 0))
                move = move_data.get('move', move_data.get('Move', ''))
            else:
                level, move = 0, str(move_data)
            self.level_moves_tree.insert('', tk.END, values=(level, move))
        
        # Populate TM moves
        for move in entry.machine_moves:
            self.tm_moves_list.insert(tk.END, move)
        
        # Populate egg moves
        for move in entry.egg_moves:
            self.egg_moves_list.insert(tk.END, move)
        
        # Populate tutor moves
        for move in entry.tutor_moves:
            self.tutor_moves_list.insert(tk.END, move)
    
    def _add_level_move(self):
        """Add a new level-up move."""
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        
        dialog = MoveDialog(self.root, "Add Level-Up Move", self.move_names, show_level=True)
        if dialog.result:
            level, move = dialog.result
            self.level_moves_tree.insert('', tk.END, values=(level, move))
            self._save_current_to_data()
            self.set_modified(True)
    
    def _remove_level_move(self):
        """Remove selected level-up move."""
        selection = self.level_moves_tree.selection()
        if selection:
            self.level_moves_tree.delete(selection[0])
            self._save_current_to_data()
            self.set_modified(True)
    
    def _edit_level_move(self, event):
        """Edit a level-up move on double-click."""
        selection = self.level_moves_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.level_moves_tree.item(item, 'values')
        
        dialog = MoveDialog(
            self.root,
            "Edit Level-Up Move",
            self.move_names,
            show_level=True,
            initial_level=int(values[0]),
            initial_move=values[1]
        )
        
        if dialog.result:
            level, move = dialog.result
            self.level_moves_tree.item(item, values=(level, move))
            self._save_current_to_data()
            self.set_modified(True)
    
    def _sort_level_moves(self):
        """Sort level moves by level."""
        if not self.current_species:
            return
        
        # Get all items
        items = []
        for item in self.level_moves_tree.get_children():
            values = self.level_moves_tree.item(item, 'values')
            items.append((int(values[0]), values[1]))
        
        # Sort by level
        items.sort(key=lambda x: x[0])
        
        # Clear and repopulate
        for item in self.level_moves_tree.get_children():
            self.level_moves_tree.delete(item)
        
        for level, move in items:
            self.level_moves_tree.insert('', tk.END, values=(level, move))
        
        self._save_current_to_data()
        self.set_modified(True)
    
    def _add_tm_move(self):
        """Add a TM/HM move."""
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        
        dialog = MoveDialog(self.root, "Add TM/HM Move", self.move_names)
        if dialog.result:
            _, move = dialog.result
            self.tm_moves_list.insert(tk.END, move)
            self._save_current_to_data()
            self.set_modified(True)
    
    def _remove_tm_move(self):
        """Remove selected TM/HM move."""
        selection = self.tm_moves_list.curselection()
        if selection:
            self.tm_moves_list.delete(selection[0])
            self._save_current_to_data()
            self.set_modified(True)
    
    def _add_egg_move(self):
        """Add an egg move."""
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        
        dialog = MoveDialog(self.root, "Add Egg Move", self.move_names)
        if dialog.result:
            _, move = dialog.result
            self.egg_moves_list.insert(tk.END, move)
            self._save_current_to_data()
            self.set_modified(True)
    
    def _remove_egg_move(self):
        """Remove selected egg move."""
        selection = self.egg_moves_list.curselection()
        if selection:
            self.egg_moves_list.delete(selection[0])
            self._save_current_to_data()
            self.set_modified(True)
    
    def _add_tutor_move(self):
        """Add a tutor move."""
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        
        dialog = MoveDialog(self.root, "Add Tutor Move", self.move_names)
        if dialog.result:
            _, move = dialog.result
            self.tutor_moves_list.insert(tk.END, move)
            self._save_current_to_data()
            self.set_modified(True)
    
    def _remove_tutor_move(self):
        """Remove selected tutor move."""
        selection = self.tutor_moves_list.curselection()
        if selection:
            self.tutor_moves_list.delete(selection[0])
            self._save_current_to_data()
            self.set_modified(True)
    
    def _save_current_to_data(self):
        """Save current editor state to data."""
        if not self.current_species:
            return
        
        entry = self.learnset_data[self.current_species]
        
        # Save level moves
        entry.level_moves = []
        for item in self.level_moves_tree.get_children():
            values = self.level_moves_tree.item(item, 'values')
            entry.level_moves.append({
                'level': int(values[0]),
                'move': values[1]
            })
        
        # Save TM moves
        entry.machine_moves = list(self.tm_moves_list.get(0, tk.END))
        
        # Save egg moves
        entry.egg_moves = list(self.egg_moves_list.get(0, tk.END))
        
        # Save tutor moves
        entry.tutor_moves = list(self.tutor_moves_list.get(0, tk.END))
    
    def save(self) -> bool:
        """Save learnset data."""
        return self._do_save(None)
    
    def _do_save(self, filepath: Path) -> bool:
        """Save learnset data to file."""
        try:
            self.json_handler.save_learnsets(self.learnset_data)
            self.set_modified(False)
            self.set_status("Learnsets saved successfully")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            return False
    
    def _find_pokemon_with_move(self):
        """Find all Pokemon that can learn a specific move."""
        dialog = MoveDialog(self.root, "Find Pokemon with Move", self.move_names)
        if not dialog.result:
            return
        
        _, target_move = dialog.result
        
        results = []
        for species, entry in self.learnset_data.items():
            sources = []
            
            # Check level moves
            for move_data in entry.level_moves:
                move = move_data.get('move', move_data.get('Move', '')) if isinstance(move_data, dict) else move_data
                if move == target_move:
                    level = move_data.get('level', move_data.get('Level', 0)) if isinstance(move_data, dict) else 0
                    sources.append(f"Level {level}")
                    break
            
            # Check TM moves
            if target_move in entry.machine_moves:
                sources.append("TM/HM")
            
            # Check egg moves
            if target_move in entry.egg_moves:
                sources.append("Egg")
            
            # Check tutor moves
            if target_move in entry.tutor_moves:
                sources.append("Tutor")
            
            if sources:
                results.append((species, ", ".join(sources)))
        
        # Show results
        result_dialog = tk.Toplevel(self.root)
        result_dialog.title(f"Pokemon that learn {target_move}")
        result_dialog.geometry("500x400")
        
        ttk.Label(result_dialog, text=f"Found {len(results)} Pokemon:").pack(pady=5)
        
        columns = ('species', 'source')
        tree = ttk.Treeview(result_dialog, columns=columns, show='headings')
        tree.heading('species', text='Pokemon')
        tree.heading('source', text='Learn Method')
        tree.column('species', width=200)
        tree.column('source', width=250)
        
        scrollbar = ttk.Scrollbar(result_dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        for species, source in sorted(results):
            tree.insert('', tk.END, values=(species, source))


class MoveDialog(tk.Toplevel):
    """Dialog for selecting a move (and optionally level)."""
    
    def __init__(self, parent, title: str, move_names: List[str],
                 show_level: bool = False, initial_level: int = 1, initial_move: str = ""):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        if show_level:
            level_frame = ttk.Frame(main_frame)
            level_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(level_frame, text="Level:", width=10).pack(side=tk.LEFT)
            self.level_var = tk.IntVar(value=initial_level)
            self.level_spin = ttk.Spinbox(level_frame, textvariable=self.level_var, from_=0, to=100, width=10)
            self.level_spin.pack(side=tk.LEFT)
        else:
            self.level_var = tk.IntVar(value=0)
        
        move_frame = ttk.Frame(main_frame)
        move_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(move_frame, text="Move:", width=10).pack(side=tk.LEFT)
        self.move_var = tk.StringVar(value=initial_move)
        self.move_combo = ttk.Combobox(move_frame, textvariable=self.move_var, values=move_names, width=35)
        self.move_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="OK", command=self._ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        
        self.move_combo.focus_set()
        self.wait_window()
    
    def _ok(self):
        move = self.move_var.get()
        if not move:
            messagebox.showwarning("Warning", "Please select a move")
            return
        
        self.result = (self.level_var.get(), move)
        self.destroy()


def main():
    """Run the moveset editor standalone."""
    editor = MovesetEditor()
    editor.run()


if __name__ == "__main__":
    main()
