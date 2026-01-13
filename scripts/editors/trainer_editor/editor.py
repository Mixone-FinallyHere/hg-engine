"""
Trainer Editor
==============
Tkinter GUI for editing trainer data (teams, AI, items, etc.).
Supports all trainer data type flags and extra flags for extended Pokemon configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List, Any
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base_editor import BaseEditor, LabeledEntry, LabeledCombobox, LabeledSpinbox
from common.asm_parser import ASMParser, TrainerdataEntry
from common.constants import ConstantsLoader


# Trainer data type flags (bitfield, can combine multiple)
TRAINER_DATA_TYPE_FLAGS = [
    ("TRAINER_DATA_TYPE_MOVES", 0x01, "Specify moves for Pokemon"),
    ("TRAINER_DATA_TYPE_ITEMS", 0x02, "Specify held items for Pokemon"),
    ("TRAINER_DATA_TYPE_ABILITY", 0x04, "Specify ability slot (0/1/2)"),
    ("TRAINER_DATA_TYPE_BALL", 0x08, "Specify Pokeball type"),
    ("TRAINER_DATA_TYPE_IV_EV_SET", 0x10, "Specify custom IVs and EVs"),
    ("TRAINER_DATA_TYPE_NATURE_SET", 0x20, "Specify nature"),
    ("TRAINER_DATA_TYPE_SHINY_LOCK", 0x40, "Specify shiny status"),
    ("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS", 0x80, "Enable extra flags"),
]

# Extra flags (only used if TRAINER_DATA_TYPE_ADDITIONAL_FLAGS is set)
# These are stored in the additionalflags field of each Pokemon
# Values from include/pokemon.h and armips/include/constants.s
TRAINER_DATA_EXTRA_FLAGS = [
    ("TRAINER_DATA_EXTRA_TYPE_STATUS", 0x01, "Pre-afflict status condition"),
    ("TRAINER_DATA_EXTRA_TYPE_HP", 0x02, "Force HP stat value"),
    ("TRAINER_DATA_EXTRA_TYPE_ATK", 0x04, "Force Attack stat value"),
    ("TRAINER_DATA_EXTRA_TYPE_DEF", 0x08, "Force Defense stat value"),
    ("TRAINER_DATA_EXTRA_TYPE_SPEED", 0x10, "Force Speed stat value"),
    ("TRAINER_DATA_EXTRA_TYPE_SP_ATK", 0x20, "Force Sp.Atk stat value"),
    ("TRAINER_DATA_EXTRA_TYPE_SP_DEF", 0x40, "Force Sp.Def stat value"),
    ("TRAINER_DATA_EXTRA_TYPE_PP_COUNTS", 0x80, "Specify PP counts for moves"),
    ("TRAINER_DATA_EXTRA_TYPE_NICKNAME", 0x100, "Give Pokemon a nickname"),
]

# AI flags
AI_FLAGS = [
    "F_BASIC_AI",
    "F_CHECK_TYPE_EFF",
    "F_CHECK_DAMAGE",
    "F_EXPERT_AI",
    "F_SETUP_FIRST_TURN",
    "F_PREFER_STAB",
    "F_RISKY_ATTACKS",
    "F_PRIORITIZE_SUPER_EFFECTIVE",
    "F_PREDICT_SWITCH",
    "F_DOUBLE_BATTLE",
]


class TrainerEditor(BaseEditor):
    """Editor for trainer data (trainers.s)."""
    
    def __init__(self, master: Optional[tk.Tk] = None):
        self.asm_parser = ASMParser()
        self.constants = ConstantsLoader()
        
        # Data
        self.trainer_data: Dict[str, TrainerdataEntry] = {}
        self.filtered_list: List[str] = []
        self.current_trainer: Optional[str] = None
        self.current_pokemon_index: int = -1
        
        # Constants
        self.species_names: List[str] = []
        self.move_names: List[str] = []
        self.item_names: List[str] = []
        self.ability_names: List[str] = []
        self.ball_names: List[str] = []
        self.nature_names: List[str] = []
        
        super().__init__(master, title="Trainer Editor - hg-engine")
        
        # Load data on startup
        self._load_data()
    
    def _setup_custom_menus(self):
        """Add trainer-specific menu items."""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Add Pokemon", command=self._add_pokemon)
        tools_menu.add_command(label="Duplicate Trainer", command=self._duplicate_trainer)
        tools_menu.add_separator()
        tools_menu.add_command(label="Find by Pokemon...", command=self._find_by_pokemon)
        tools_menu.add_command(label="Find by Class...", command=self._find_by_class)
    
    def _setup_custom_toolbar(self):
        """Add trainer-specific toolbar items."""
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Label(self.toolbar, text="Class:").pack(side=tk.LEFT, padx=(0, 5))
        self.class_filter_var = tk.StringVar(value="All")
        self.class_filter = ttk.Combobox(
            self.toolbar, textvariable=self.class_filter_var,
            values=["All"], width=20, state='readonly'
        )
        self.class_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.class_filter.bind('<<ComboboxSelected>>', lambda e: self._apply_filters())
    
    def _setup_detail_view(self):
        """Setup the trainer detail editing view."""
        # Create notebook for trainer info and pokemon
        self.notebook = ttk.Notebook(self.detail_content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Trainer info tab
        info_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(info_frame, text="Trainer Info")
        self._setup_trainer_info_tab(info_frame)
        
        # Data type flags tab
        flags_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(flags_frame, text="Data Flags")
        self._setup_flags_tab(flags_frame)
        
        # Pokemon team tab
        team_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(team_frame, text="Pokemon Team")
        self._setup_team_tab(team_frame)
    
    def _setup_trainer_info_tab(self, parent: ttk.Frame):
        """Setup the trainer info editing tab."""
        # Basic info
        basic_frame = ttk.LabelFrame(parent, text="Basic Info", padding=10)
        basic_frame.pack(fill=tk.X, pady=5)
        
        self.trainer_id_label = ttk.Label(basic_frame, text="ID: ", font=('Arial', 12, 'bold'))
        self.trainer_id_label.pack(anchor=tk.W)
        
        self.trainer_name_entry = LabeledEntry(basic_frame, "Name:", width=30)
        self.trainer_name_entry.pack(fill=tk.X, pady=2)
        self.trainer_name_entry.bind_change(self._on_data_change)
        
        self.trainer_class_entry = LabeledEntry(basic_frame, "Class:", width=30)
        self.trainer_class_entry.pack(fill=tk.X, pady=2)
        self.trainer_class_entry.bind_change(self._on_data_change)
        
        # Battle type
        battle_types = ["battletype_pokemon_trainer", "battletype_pokemon_trainer_double"]
        self.battle_type_combo = LabeledCombobox(basic_frame, "Battle Type:", battle_types, width=35)
        self.battle_type_combo.pack(fill=tk.X, pady=2)
        self.battle_type_combo.bind_change(self._on_data_change)
        
        # AI settings
        ai_frame = ttk.LabelFrame(parent, text="AI Flags", padding=10)
        ai_frame.pack(fill=tk.X, pady=5)
        
        self.ai_flags_var = {}
        ai_grid = ttk.Frame(ai_frame)
        ai_grid.pack(fill=tk.X)
        
        for i, flag in enumerate(AI_FLAGS):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(ai_grid, text=flag, variable=var, command=self._on_data_change)
            cb.grid(row=i // 2, column=i % 2, sticky=tk.W, padx=5, pady=2)
            self.ai_flags_var[flag] = var
        
        # Items
        items_frame = ttk.LabelFrame(parent, text="Trainer Items", padding=10)
        items_frame.pack(fill=tk.X, pady=5)
        
        self.trainer_items = []
        items_grid = ttk.Frame(items_frame)
        items_grid.pack(fill=tk.X)
        
        for i in range(4):
            row = i // 2
            col = i % 2
            combo = LabeledCombobox(items_grid, f"Item {i+1}:", [], width=20)
            combo.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            combo.bind_change(self._on_data_change)
            self.trainer_items.append(combo)
    
    def _setup_flags_tab(self, parent: ttk.Frame):
        """Setup the data type flags tab."""
        # Main trainer mon type flags
        type_frame = ttk.LabelFrame(parent, text="Pokemon Data Type Flags", padding=10)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="These flags control what data can be set for each Pokemon:", 
                  foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        self.type_flags_var = {}
        for flag_name, flag_val, description in TRAINER_DATA_TYPE_FLAGS:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(type_frame, text=f"{flag_name}", variable=var, 
                                command=self._on_flags_change)
            cb.pack(anchor=tk.W, pady=1)
            ttk.Label(type_frame, text=f"    {description}", foreground='gray').pack(anchor=tk.W)
            self.type_flags_var[flag_name] = var
        
        # Extra flags (only available when ADDITIONAL_FLAGS is set)
        self.extra_frame = ttk.LabelFrame(parent, text="Extra Flags (requires ADDITIONAL_FLAGS)", padding=10)
        self.extra_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.extra_frame, text="These flags are only available when ADDITIONAL_FLAGS is enabled:", 
                  foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        self.extra_flags_var = {}
        for flag_name, flag_val, description in TRAINER_DATA_EXTRA_FLAGS:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.extra_frame, text=f"{flag_name}", variable=var,
                                command=self._on_data_change)
            cb.pack(anchor=tk.W, pady=1)
            self.extra_flags_var[flag_name] = var
        
        # Initially disable extra flags frame
        self._update_extra_flags_state()
    
    def _setup_team_tab(self, parent: ttk.Frame):
        """Setup the Pokemon team editing tab."""
        # Split into left (list) and right (details)
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - team list
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)
        
        # Toolbar
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add", command=self._add_pokemon).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove", command=self._remove_pokemon).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↑", width=3, command=self._move_pokemon_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↓", width=3, command=self._move_pokemon_down).pack(side=tk.LEFT, padx=2)
        
        self.team_count_label = ttk.Label(toolbar, text="Team: 0/6")
        self.team_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Pokemon list
        columns = ('species', 'level')
        self.team_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        self.team_tree.heading('species', text='Pokemon')
        self.team_tree.heading('level', text='Level')
        self.team_tree.column('species', width=120)
        self.team_tree.column('level', width=50)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.team_tree.yview)
        self.team_tree.configure(yscrollcommand=scrollbar.set)
        
        self.team_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.team_tree.bind('<<TreeviewSelect>>', self._on_pokemon_select)
        
        # Right side - pokemon details
        detail_frame = ttk.Frame(paned)
        paned.add(detail_frame, weight=2)
        
        self._setup_pokemon_detail(detail_frame)
    
    def _setup_pokemon_detail(self, parent: ttk.Frame):
        """Setup the Pokemon detail editing section."""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        self.poke_detail_frame = ttk.Frame(canvas)
        
        self.poke_detail_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.poke_detail_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Basic pokemon info (always shown)
        basic_frame = ttk.LabelFrame(self.poke_detail_frame, text="Basic", padding=5)
        basic_frame.pack(fill=tk.X, pady=2)
        
        self.poke_species_combo = LabeledCombobox(basic_frame, "Species:", [], width=25)
        self.poke_species_combo.pack(fill=tk.X, pady=1)
        
        self.poke_level_spin = LabeledSpinbox(basic_frame, "Level:", from_=1, to=100)
        self.poke_level_spin.pack(fill=tk.X, pady=1)
        
        self.poke_form_spin = LabeledSpinbox(basic_frame, "Form:", from_=0, to=100)
        self.poke_form_spin.pack(fill=tk.X, pady=1)
        
        # Difficulty
        diff_frame = ttk.LabelFrame(self.poke_detail_frame, text="Difficulty", padding=5)
        diff_frame.pack(fill=tk.X, pady=2)
        
        self.poke_difficulty_spin = LabeledSpinbox(diff_frame, "Difficulty:", from_=0, to=255)
        self.poke_difficulty_spin.pack(fill=tk.X, pady=1)
        
        self.poke_ivs_spin = LabeledSpinbox(diff_frame, "IVs (base):", from_=0, to=31)
        self.poke_ivs_spin.pack(fill=tk.X, pady=1)
        
        self.poke_abilityslot_spin = LabeledSpinbox(diff_frame, "Ability Slot:", from_=0, to=2)
        self.poke_abilityslot_spin.pack(fill=tk.X, pady=1)
        
        # Item (requires TRAINER_DATA_TYPE_ITEMS)
        self.poke_item_frame = ttk.LabelFrame(self.poke_detail_frame, text="Held Item (requires ITEMS flag)", padding=5)
        self.poke_item_frame.pack(fill=tk.X, pady=2)
        
        self.poke_item_combo = LabeledCombobox(self.poke_item_frame, "Item:", [], width=25)
        self.poke_item_combo.pack(fill=tk.X, pady=1)
        
        # Moves (requires TRAINER_DATA_TYPE_MOVES)
        self.poke_moves_frame = ttk.LabelFrame(self.poke_detail_frame, text="Moves (requires MOVES flag)", padding=5)
        self.poke_moves_frame.pack(fill=tk.X, pady=2)
        
        self.poke_moves = []
        for i in range(4):
            combo = LabeledCombobox(self.poke_moves_frame, f"Move {i+1}:", [], width=25)
            combo.pack(fill=tk.X, pady=1)
            self.poke_moves.append(combo)
        
        # Ball (requires TRAINER_DATA_TYPE_BALL)
        self.poke_ball_frame = ttk.LabelFrame(self.poke_detail_frame, text="Ball (requires BALL flag)", padding=5)
        self.poke_ball_frame.pack(fill=tk.X, pady=2)
        
        self.poke_ball_combo = LabeledCombobox(self.poke_ball_frame, "Ball:", [], width=25)
        self.poke_ball_combo.pack(fill=tk.X, pady=1)
        
        # IVs/EVs (requires TRAINER_DATA_TYPE_IV_EV_SET)
        self.poke_ivev_frame = ttk.LabelFrame(self.poke_detail_frame, text="IVs/EVs (requires IV_EV_SET flag)", padding=5)
        self.poke_ivev_frame.pack(fill=tk.X, pady=2)
        
        iv_row = ttk.Frame(self.poke_ivev_frame)
        iv_row.pack(fill=tk.X)
        ttk.Label(iv_row, text="IVs:").pack(side=tk.LEFT)
        
        self.poke_iv_entries = {}
        for stat in ['hp', 'atk', 'def', 'spe', 'spa', 'spd']:
            frame = ttk.Frame(iv_row)
            frame.pack(side=tk.LEFT, padx=2)
            ttk.Label(frame, text=stat.upper(), width=4).pack(side=tk.LEFT)
            var = tk.IntVar(value=31)
            spin = ttk.Spinbox(frame, textvariable=var, from_=0, to=31, width=3)
            spin.pack(side=tk.LEFT)
            self.poke_iv_entries[stat] = var
        
        ev_row = ttk.Frame(self.poke_ivev_frame)
        ev_row.pack(fill=tk.X)
        ttk.Label(ev_row, text="EVs:").pack(side=tk.LEFT)
        
        self.poke_ev_entries = {}
        for stat in ['hp', 'atk', 'def', 'spe', 'spa', 'spd']:
            frame = ttk.Frame(ev_row)
            frame.pack(side=tk.LEFT, padx=2)
            ttk.Label(frame, text=stat.upper(), width=4).pack(side=tk.LEFT)
            var = tk.IntVar(value=0)
            spin = ttk.Spinbox(frame, textvariable=var, from_=0, to=252, width=4)
            spin.pack(side=tk.LEFT)
            self.poke_ev_entries[stat] = var
        
        # Nature (requires TRAINER_DATA_TYPE_NATURE_SET)
        self.poke_nature_frame = ttk.LabelFrame(self.poke_detail_frame, text="Nature (requires NATURE_SET flag)", padding=5)
        self.poke_nature_frame.pack(fill=tk.X, pady=2)
        
        natures = [
            "NATURE_HARDY", "NATURE_LONELY", "NATURE_BRAVE", "NATURE_ADAMANT", "NATURE_NAUGHTY",
            "NATURE_BOLD", "NATURE_DOCILE", "NATURE_RELAXED", "NATURE_IMPISH", "NATURE_LAX",
            "NATURE_TIMID", "NATURE_HASTY", "NATURE_SERIOUS", "NATURE_JOLLY", "NATURE_NAIVE",
            "NATURE_MODEST", "NATURE_MILD", "NATURE_QUIET", "NATURE_BASHFUL", "NATURE_RASH",
            "NATURE_CALM", "NATURE_GENTLE", "NATURE_SASSY", "NATURE_CAREFUL", "NATURE_QUIRKY",
        ]
        self.poke_nature_combo = LabeledCombobox(self.poke_nature_frame, "Nature:", natures, width=25)
        self.poke_nature_combo.pack(fill=tk.X, pady=1)
        
        # Shiny lock (requires TRAINER_DATA_TYPE_SHINY_LOCK)
        self.poke_shiny_frame = ttk.LabelFrame(self.poke_detail_frame, text="Shiny (requires SHINY_LOCK flag)", padding=5)
        self.poke_shiny_frame.pack(fill=tk.X, pady=2)
        
        self.poke_shiny_var = tk.BooleanVar()
        ttk.Checkbutton(self.poke_shiny_frame, text="Force Shiny", variable=self.poke_shiny_var).pack(anchor=tk.W)
        
        # Additional flags per Pokemon (requires TRAINER_DATA_TYPE_ADDITIONAL_FLAGS)
        self.poke_addflags_frame = ttk.LabelFrame(self.poke_detail_frame, text="Per-Pokemon Extra Flags (requires ADDITIONAL_FLAGS)", padding=5)
        self.poke_addflags_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.poke_addflags_frame, text="Enable extra data for this Pokemon:", foreground='gray').pack(anchor=tk.W)
        
        self.poke_extra_flags_var = {}
        for flag_name, flag_val, desc in TRAINER_DATA_EXTRA_FLAGS:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.poke_addflags_frame, text=f"{flag_name.replace('TRAINER_DATA_EXTRA_TYPE_', '')} - {desc}", 
                                 variable=var, command=self._on_poke_extra_flags_change)
            cb.pack(anchor=tk.W, padx=10)
            self.poke_extra_flags_var[flag_name] = var
        
        # Status (requires EXTRA_TYPE_STATUS)
        self.poke_status_frame = ttk.LabelFrame(self.poke_detail_frame, text="Status (EXTRA_TYPE_STATUS)", padding=5)
        self.poke_status_frame.pack(fill=tk.X, pady=2)
        
        statuses = ["STATUS_NONE", "STATUS_SLEEP", "STATUS_POISON", "STATUS_BURN", "STATUS_FREEZE", "STATUS_PARALYSIS", "STATUS_TOXIC"]
        self.poke_status_combo = LabeledCombobox(self.poke_status_frame, "Pre-Battle Status:", statuses, width=25)
        self.poke_status_combo.pack(fill=tk.X, pady=1)
        
        # Stat overrides (each requires its own EXTRA_TYPE flag)
        self.poke_statoverride_frame = ttk.LabelFrame(self.poke_detail_frame, text="Stat Overrides (each requires its EXTRA_TYPE flag)", padding=5)
        self.poke_statoverride_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.poke_statoverride_frame, text="Force stat values instead of calculating:", foreground='gray').pack(anchor=tk.W)
        
        stat_grid = ttk.Frame(self.poke_statoverride_frame)
        stat_grid.pack(fill=tk.X)
        
        self.poke_stat_overrides = {}
        stats = [('HP', 'hp'), ('ATK', 'atk'), ('DEF', 'def'), ('SPE', 'speed'), ('SPA', 'sp_atk'), ('SPD', 'sp_def')]
        for i, (label, key) in enumerate(stats):
            row = i // 3
            col = i % 3
            frame = ttk.Frame(stat_grid)
            frame.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            ttk.Label(frame, text=f"{label}:", width=4).pack(side=tk.LEFT)
            var = tk.IntVar(value=0)
            spin = ttk.Spinbox(frame, textvariable=var, from_=0, to=999, width=5)
            spin.pack(side=tk.LEFT)
            self.poke_stat_overrides[key] = var
        
        # PP Counts (requires EXTRA_TYPE_PP_COUNTS)
        self.poke_pp_frame = ttk.LabelFrame(self.poke_detail_frame, text="PP Counts (EXTRA_TYPE_PP_COUNTS)", padding=5)
        self.poke_pp_frame.pack(fill=tk.X, pady=2)
        
        pp_row = ttk.Frame(self.poke_pp_frame)
        pp_row.pack(fill=tk.X)
        
        self.poke_pp_counts = []
        for i in range(4):
            frame = ttk.Frame(pp_row)
            frame.pack(side=tk.LEFT, padx=5)
            ttk.Label(frame, text=f"Move {i+1}:").pack(side=tk.LEFT)
            var = tk.IntVar(value=0)
            spin = ttk.Spinbox(frame, textvariable=var, from_=0, to=64, width=4)
            spin.pack(side=tk.LEFT)
            self.poke_pp_counts.append(var)
        
        # Nickname (requires ADDITIONAL_FLAGS + NICKNAME extra flag)
        self.poke_nickname_frame = ttk.LabelFrame(self.poke_detail_frame, text="Nickname (requires ADDITIONAL_FLAGS + NICKNAME)", padding=5)
        self.poke_nickname_frame.pack(fill=tk.X, pady=2)
        
        self.poke_nickname_entry = LabeledEntry(self.poke_nickname_frame, "Nickname:", width=20)
        self.poke_nickname_entry.pack(fill=tk.X, pady=1)
        
        # Ball Seal (always at end of structure)
        self.poke_ballseal_frame = ttk.LabelFrame(self.poke_detail_frame, text="Ball Seal (always present)", padding=5)
        self.poke_ballseal_frame.pack(fill=tk.X, pady=2)
        
        self.poke_ballseal_spin = LabeledSpinbox(self.poke_ballseal_frame, "Ball Seal ID:", from_=0, to=255)
        self.poke_ballseal_spin.pack(fill=tk.X, pady=1)
        
        # Update button
        ttk.Button(self.poke_detail_frame, text="Update Pokemon", command=self._update_selected_pokemon).pack(pady=10)
    
    def _on_poke_extra_flags_change(self):
        """Handle changes to per-Pokemon extra flags checkboxes."""
        # This just updates the UI to show which extra fields are relevant
        self._update_pokemon_extra_visibility()
    
    def _update_pokemon_extra_visibility(self):
        """Update visibility hints for extra Pokemon fields based on per-Pokemon extra flags."""
        # Get which extra flags are checked for this Pokemon
        has_status = self.poke_extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_STATUS", tk.BooleanVar()).get()
        has_hp = self.poke_extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_HP", tk.BooleanVar()).get()
        has_pp = self.poke_extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_PP_COUNTS", tk.BooleanVar()).get()
        has_nickname = self.poke_extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_NICKNAME", tk.BooleanVar()).get()
        
        # Update labels with checkmarks
        self.poke_status_frame.config(text="Pre-Battle Status" + (" ✓" if has_status else " (enable STATUS flag above)"))
        self.poke_pp_frame.config(text="PP Counts" + (" ✓" if has_pp else " (enable PP_COUNTS flag above)"))
    
    def _on_flags_change(self):
        """Handle changes to trainer data type flags."""
        self._update_extra_flags_state()
        self._update_pokemon_detail_visibility()
        self._on_data_change()
    
    def _update_extra_flags_state(self):
        """Update the enabled state of extra flags based on ADDITIONAL_FLAGS."""
        additional_enabled = self.type_flags_var.get("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS", tk.BooleanVar()).get()
        
        for child in self.extra_frame.winfo_children():
            if isinstance(child, ttk.Checkbutton):
                if additional_enabled:
                    child.configure(state='normal')
                else:
                    child.configure(state='disabled')
    
    def _update_pokemon_detail_visibility(self):
        """Update visibility of pokemon detail sections based on flags."""
        # Check which trainer data type flags are enabled
        has_items = self.type_flags_var.get("TRAINER_DATA_TYPE_ITEMS", tk.BooleanVar()).get()
        has_moves = self.type_flags_var.get("TRAINER_DATA_TYPE_MOVES", tk.BooleanVar()).get()
        has_ball = self.type_flags_var.get("TRAINER_DATA_TYPE_BALL", tk.BooleanVar()).get()
        has_ivev = self.type_flags_var.get("TRAINER_DATA_TYPE_IV_EV_SET", tk.BooleanVar()).get()
        has_nature = self.type_flags_var.get("TRAINER_DATA_TYPE_NATURE_SET", tk.BooleanVar()).get()
        has_shiny = self.type_flags_var.get("TRAINER_DATA_TYPE_SHINY_LOCK", tk.BooleanVar()).get()
        has_additional = self.type_flags_var.get("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS", tk.BooleanVar()).get()
        
        # Check trainer-level extra flags (from Data Flags tab)
        has_trainer_nickname = has_additional and self.extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_NICKNAME", tk.BooleanVar()).get()
        has_trainer_status = has_additional and self.extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_STATUS", tk.BooleanVar()).get()
        has_trainer_pp = has_additional and self.extra_flags_var.get("TRAINER_DATA_EXTRA_TYPE_PP_COUNTS", tk.BooleanVar()).get()
        
        # Update frame labels to show enabled/disabled status
        self.poke_item_frame.config(text="Held Item" + (" ✓" if has_items else " (requires ITEMS flag)"))
        self.poke_moves_frame.config(text="Moves" + (" ✓" if has_moves else " (requires MOVES flag)"))
        self.poke_ball_frame.config(text="Ball" + (" ✓" if has_ball else " (requires BALL flag)"))
        self.poke_ivev_frame.config(text="IVs/EVs" + (" ✓" if has_ivev else " (requires IV_EV_SET flag)"))
        self.poke_nature_frame.config(text="Nature" + (" ✓" if has_nature else " (requires NATURE_SET flag)"))
        self.poke_shiny_frame.config(text="Shiny" + (" ✓" if has_shiny else " (requires SHINY_LOCK flag)"))
        
        # Additional flags sections
        self.poke_addflags_frame.config(text="Per-Pokemon Extra Flags" + (" ✓" if has_additional else " (requires ADDITIONAL_FLAGS)"))
        self.poke_status_frame.config(text="Pre-Battle Status" + (" ✓" if has_trainer_status else " (requires STATUS extra flag)"))
        self.poke_statoverride_frame.config(text="Stat Overrides" + (" ✓" if has_additional else " (requires ADDITIONAL_FLAGS + stat flags)"))
        self.poke_pp_frame.config(text="PP Counts" + (" ✓" if has_trainer_pp else " (requires PP_COUNTS extra flag)"))
        self.poke_nickname_frame.config(text="Nickname" + (" ✓" if has_trainer_nickname else " (requires NICKNAME extra flag)"))
    
    def _load_data(self):
        """Load trainer data."""
        try:
            self.trainer_data = self.asm_parser.parse_trainerdata()
            self._load_constants()
            self._populate_list()
            self._update_class_filter()
            self.set_status(f"Loaded {len(self.trainer_data)} trainers")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trainer data: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_constants(self):
        """Load constants for dropdowns."""
        try:
            species = self.constants.load_species()
            self.species_names = sorted([k for k in species.keys() if k.startswith('SPECIES_')])
            self.poke_species_combo.set_values(self.species_names)
        except Exception as e:
            print(f"Warning: Could not load species: {e}")
        
        try:
            moves = self.constants.load_moves()
            self.move_names = sorted([k for k in moves.keys() if k.startswith('MOVE_')])
            for combo in self.poke_moves:
                combo.set_values(["MOVE_NONE"] + self.move_names)
        except Exception as e:
            print(f"Warning: Could not load moves: {e}")
        
        try:
            items = self.constants.load_items()
            self.item_names = sorted([k for k in items.keys() if k.startswith('ITEM_')])
            self.poke_item_combo.set_values(["ITEM_NONE"] + self.item_names)
            for combo in self.trainer_items:
                combo.set_values(["ITEM_NONE"] + self.item_names)
        except Exception as e:
            print(f"Warning: Could not load items: {e}")
        
        # Load balls
        ball_items = [item for item in self.item_names if 'BALL' in item]
        self.poke_ball_combo.set_values(["ITEM_POKE_BALL"] + ball_items)
    
    def _populate_list(self):
        """Populate the trainer list."""
        self.item_list.delete(0, tk.END)
        self.filtered_list = sorted(self.trainer_data.keys())
        
        for trainer_id in self.filtered_list:
            entry = self.trainer_data[trainer_id]
            display = f"{trainer_id}: {entry.name}" if entry.name else trainer_id
            self.item_list.insert(tk.END, display)
    
    def _update_class_filter(self):
        """Update the class filter dropdown."""
        classes = set()
        for entry in self.trainer_data.values():
            if entry.trainer_class:
                classes.add(entry.trainer_class)
        
        all_classes = ["All"] + sorted(classes)
        self.class_filter['values'] = all_classes
    
    def _apply_filters(self):
        """Apply search and class filters."""
        search_term = self.search_var.get().lower()
        class_filter = self.class_filter_var.get()
        
        self.item_list.delete(0, tk.END)
        self.filtered_list = []
        
        for trainer_id in sorted(self.trainer_data.keys()):
            entry = self.trainer_data[trainer_id]
            
            if search_term:
                if search_term not in trainer_id.lower() and search_term not in entry.name.lower():
                    continue
            
            if class_filter != "All":
                if entry.trainer_class != class_filter:
                    continue
            
            self.filtered_list.append(trainer_id)
            display = f"{trainer_id}: {entry.name}" if entry.name else trainer_id
            self.item_list.insert(tk.END, display)
        
        self.set_status(f"Showing {len(self.filtered_list)} of {len(self.trainer_data)} trainers")
    
    def _on_search(self):
        """Handle search input."""
        self._apply_filters()
    
    def _on_item_select(self, event):
        """Handle trainer selection."""
        selection = self.item_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.filtered_list):
            trainer_id = self.filtered_list[index]
            self._load_trainer(trainer_id)
    
    def _load_trainer(self, trainer_id: str):
        """Load a trainer's data into the editor."""
        if trainer_id not in self.trainer_data:
            return
        
        self.current_trainer = trainer_id
        entry = self.trainer_data[trainer_id]
        
        self._loading = True
        
        try:
            # Basic info
            self.trainer_id_label.config(text=f"ID: {trainer_id}")
            self.trainer_name_entry.set(entry.name)
            self.trainer_class_entry.set(entry.trainer_class)
            self.battle_type_combo.set(entry.battletype or "battletype_pokemon_trainer")
            
            # AI flags
            for flag, var in self.ai_flags_var.items():
                var.set(flag in entry.aiflags)
            
            # Trainer mon type flags
            for flag_name, _, _ in TRAINER_DATA_TYPE_FLAGS:
                var = self.type_flags_var.get(flag_name)
                if var:
                    var.set(flag_name in entry.trainermontype_flags)
            
            # Extra flags
            for flag_name, _, _ in TRAINER_DATA_EXTRA_FLAGS:
                var = self.extra_flags_var.get(flag_name)
                if var:
                    var.set(flag_name in entry.extra_flags if hasattr(entry, 'extra_flags') else False)
            
            self._update_extra_flags_state()
            self._update_pokemon_detail_visibility()
            
            # Trainer items
            for i, combo in enumerate(self.trainer_items):
                if i < len(entry.items):
                    combo.set(entry.items[i])
                else:
                    combo.set("ITEM_NONE")
            
            # Load team
            self._load_team(entry.party)
        
        finally:
            self._loading = False
    
    def _load_team(self, party: List[Dict]):
        """Load the team into the treeview."""
        # Clear existing
        for item in self.team_tree.get_children():
            self.team_tree.delete(item)
        
        for i, poke in enumerate(party):
            species = poke.get('species', 'SPECIES_NONE')
            level = poke.get('level', 1)
            self.team_tree.insert('', tk.END, iid=str(i), values=(species, level))
        
        self.team_count_label.config(text=f"Team: {len(party)}/6")
        self.current_pokemon_index = -1
    
    def _on_pokemon_select(self, event):
        """Handle Pokemon selection in team tree."""
        selection = self.team_tree.selection()
        if not selection:
            return
        
        index = int(selection[0])
        self._load_pokemon_detail(index)
    
    def _load_pokemon_detail(self, index: int):
        """Load a Pokemon's details into the editor."""
        if not self.current_trainer:
            return
        
        entry = self.trainer_data[self.current_trainer]
        if index < 0 or index >= len(entry.party):
            return
        
        self.current_pokemon_index = index
        poke = entry.party[index]
        
        self._loading = True
        
        try:
            self.poke_species_combo.set(poke.get('species', 'SPECIES_NONE'))
            self.poke_level_spin.set(poke.get('level', 1))
            self.poke_form_spin.set(poke.get('form', 0))
            self.poke_difficulty_spin.set(poke.get('difficulty', 0))
            self.poke_ivs_spin.set(poke.get('ivs', 0))
            self.poke_abilityslot_spin.set(poke.get('abilityslot', 0))
            
            self.poke_item_combo.set(poke.get('item', 'ITEM_NONE'))
            
            moves = poke.get('moves', [])
            for i, combo in enumerate(self.poke_moves):
                if i < len(moves):
                    combo.set(moves[i])
                else:
                    combo.set("MOVE_NONE")
            
            self.poke_ball_combo.set(poke.get('ball', 'ITEM_POKE_BALL'))
            
            # IVs
            ivs = poke.get('setivs', {})
            for stat, var in self.poke_iv_entries.items():
                var.set(ivs.get(stat, 31))
            
            # EVs
            evs = poke.get('setevs', {})
            for stat, var in self.poke_ev_entries.items():
                var.set(evs.get(stat, 0))
            
            self.poke_nature_combo.set(poke.get('nature', 'NATURE_HARDY'))
            self.poke_shiny_var.set(poke.get('shinylock', False))
            self.poke_nickname_entry.set(poke.get('nickname', ''))
        
        finally:
            self._loading = False
    
    def _update_selected_pokemon(self):
        """Save the current Pokemon detail back to data."""
        if not self.current_trainer or self.current_pokemon_index < 0:
            return
        
        entry = self.trainer_data[self.current_trainer]
        if self.current_pokemon_index >= len(entry.party):
            return
        
        poke = entry.party[self.current_pokemon_index]
        
        poke['species'] = self.poke_species_combo.get()
        poke['level'] = self.poke_level_spin.get()
        poke['form'] = self.poke_form_spin.get()
        poke['difficulty'] = self.poke_difficulty_spin.get()
        poke['ivs'] = self.poke_ivs_spin.get()
        poke['abilityslot'] = self.poke_abilityslot_spin.get()
        poke['item'] = self.poke_item_combo.get()
        poke['moves'] = [combo.get() for combo in self.poke_moves]
        poke['ball'] = self.poke_ball_combo.get()
        poke['setivs'] = {stat: var.get() for stat, var in self.poke_iv_entries.items()}
        poke['setevs'] = {stat: var.get() for stat, var in self.poke_ev_entries.items()}
        poke['nature'] = self.poke_nature_combo.get()
        poke['shinylock'] = self.poke_shiny_var.get()
        poke['nickname'] = self.poke_nickname_entry.get()
        
        # Update treeview
        self.team_tree.item(str(self.current_pokemon_index), values=(poke['species'], poke['level']))
        
        self.set_modified(True)
        self.set_status(f"Updated Pokemon {self.current_pokemon_index + 1}")
    
    def _add_pokemon(self):
        """Add a new Pokemon to the team."""
        if not self.current_trainer:
            messagebox.showwarning("Warning", "Please select a trainer first")
            return
        
        entry = self.trainer_data[self.current_trainer]
        if len(entry.party) >= 6:
            messagebox.showwarning("Warning", "Team is full (6 Pokemon)")
            return
        
        new_poke = {
            'species': 'SPECIES_BULBASAUR',
            'level': 5,
            'form': 0,
            'difficulty': 0,
            'ivs': 0,
            'abilityslot': 0,
            'item': 'ITEM_NONE',
            'moves': ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE'],
            'ball': 'ITEM_POKE_BALL',
        }
        
        entry.party.append(new_poke)
        self._load_team(entry.party)
        self.set_modified(True)
    
    def _remove_pokemon(self):
        """Remove the selected Pokemon from the team."""
        if not self.current_trainer:
            return
        
        selection = self.team_tree.selection()
        if not selection:
            return
        
        index = int(selection[0])
        entry = self.trainer_data[self.current_trainer]
        
        if index < len(entry.party):
            entry.party.pop(index)
            self._load_team(entry.party)
            self.set_modified(True)
    
    def _move_pokemon_up(self):
        """Move selected Pokemon up in the team."""
        if not self.current_trainer:
            return
        
        selection = self.team_tree.selection()
        if not selection:
            return
        
        index = int(selection[0])
        if index <= 0:
            return
        
        entry = self.trainer_data[self.current_trainer]
        entry.party[index], entry.party[index-1] = entry.party[index-1], entry.party[index]
        self._load_team(entry.party)
        self.team_tree.selection_set(str(index-1))
        self.set_modified(True)
    
    def _move_pokemon_down(self):
        """Move selected Pokemon down in the team."""
        if not self.current_trainer:
            return
        
        selection = self.team_tree.selection()
        if not selection:
            return
        
        index = int(selection[0])
        entry = self.trainer_data[self.current_trainer]
        
        if index >= len(entry.party) - 1:
            return
        
        entry.party[index], entry.party[index+1] = entry.party[index+1], entry.party[index]
        self._load_team(entry.party)
        self.team_tree.selection_set(str(index+1))
        self.set_modified(True)
    
    def _on_data_change(self):
        """Handle data changes in the editor."""
        if hasattr(self, '_loading') and self._loading:
            return
        
        if self.current_trainer:
            self._save_current_to_data()
            self.set_modified(True)
    
    def _save_current_to_data(self):
        """Save current editor state back to data."""
        if not self.current_trainer:
            return
        
        entry = self.trainer_data[self.current_trainer]
        
        entry.name = self.trainer_name_entry.get()
        entry.trainer_class = self.trainer_class_entry.get()
        entry.battletype = self.battle_type_combo.get()
        
        # AI flags
        entry.aiflags = [flag for flag, var in self.ai_flags_var.items() if var.get()]
        
        # Trainer mon type flags
        entry.trainermontype_flags = [
            flag_name for flag_name, _, _ in TRAINER_DATA_TYPE_FLAGS
            if self.type_flags_var.get(flag_name, tk.BooleanVar()).get()
        ]
        
        # Extra flags
        if hasattr(entry, 'extra_flags'):
            entry.extra_flags = [
                flag_name for flag_name, _, _ in TRAINER_DATA_EXTRA_FLAGS
                if self.extra_flags_var.get(flag_name, tk.BooleanVar()).get()
            ]
        
        # Items
        entry.items = [combo.get() for combo in self.trainer_items if combo.get() != "ITEM_NONE"]
    
    def _duplicate_trainer(self):
        """Duplicate the current trainer."""
        if not self.current_trainer:
            messagebox.showwarning("Warning", "Please select a trainer first")
            return
        
        # Generate new ID
        base_id = self.current_trainer
        new_id = f"{base_id}_copy"
        counter = 1
        while new_id in self.trainer_data:
            new_id = f"{base_id}_copy{counter}"
            counter += 1
        
        # Deep copy
        import copy
        self.trainer_data[new_id] = copy.deepcopy(self.trainer_data[self.current_trainer])
        self.trainer_data[new_id].name = f"{self.trainer_data[self.current_trainer].name} (Copy)"
        
        self._populate_list()
        self.set_modified(True)
        self.set_status(f"Created duplicate: {new_id}")
    
    def _find_by_pokemon(self):
        """Find trainers using a specific Pokemon."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Find by Pokemon")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select Pokemon:").pack(pady=5)
        
        species_var = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=species_var, values=self.species_names, width=35)
        combo.pack(pady=5)
        
        result_list = tk.Listbox(dialog, height=10)
        result_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def search():
            target = species_var.get()
            result_list.delete(0, tk.END)
            
            for trainer_id, entry in self.trainer_data.items():
                for poke in entry.party:
                    if poke.get('species') == target:
                        result_list.insert(tk.END, f"{trainer_id}: {entry.name}")
                        break
        
        ttk.Button(dialog, text="Search", command=search).pack(pady=5)
    
    def _find_by_class(self):
        """Focus on class filter."""
        self.set_status("Use the Class dropdown filter in the toolbar")
    
    def save(self) -> bool:
        """Save the trainer data."""
        try:
            messagebox.showinfo(
                "Save",
                "Trainer data writing not yet fully implemented.\n"
                "Changes are stored in memory."
            )
            self.set_modified(False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            return False


def main():
    """Run the trainer editor standalone."""
    editor = TrainerEditor()
    editor.run()


if __name__ == "__main__":
    main()
