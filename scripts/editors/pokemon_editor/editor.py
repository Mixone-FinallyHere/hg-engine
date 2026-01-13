"""
Pokemon Data Editor
===================
Tkinter GUI for editing Pokemon base stats, types, abilities, learnsets, and other data.
Includes sprite display support.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, List
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base_editor import BaseEditor, LabeledEntry, LabeledCombobox, LabeledSpinbox
from common.asm_parser import ASMParser, MondataEntry
from common.json_handler import JSONHandler, LearnsetEntry
from common.constants import ConstantsLoader

# Try to import PIL for sprites
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class PokemonEditor(BaseEditor):
    """Editor for Pokemon data (mondata.s) and learnsets."""
    
    def __init__(self, master: Optional[tk.Tk] = None):
        self.asm_parser = ASMParser()
        self.json_handler = JSONHandler()
        self.constants = ConstantsLoader()
        
        # Data
        self.pokemon_data: Dict[str, MondataEntry] = {}
        self.learnset_data: Dict[str, LearnsetEntry] = {}
        self.filtered_list: List[str] = []
        self.current_species: Optional[str] = None
        self.move_names: List[str] = []
        
        # Sprite cache
        self.sprite_cache: Dict[str, any] = {}
        self.current_sprite = None
        
        super().__init__(master, title="Pokemon Data Editor - hg-engine")
        
        # Load data on startup
        self._load_data()
    
    def _setup_custom_menus(self):
        """Add Pokemon-specific menu items."""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Recalculate BST", command=self._recalculate_bst)
        tools_menu.add_command(label="Find by Type...", command=self._find_by_type)
        tools_menu.add_command(label="Find by Ability...", command=self._find_by_ability)
        tools_menu.add_command(label="Find by Move...", command=self._find_by_move)
    
    def _setup_custom_toolbar(self):
        """Add Pokemon-specific toolbar items."""
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Label(self.toolbar, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.type_filter_var = tk.StringVar(value="All")
        self.type_filter_combo = ttk.Combobox(
            self.toolbar, textvariable=self.type_filter_var,
            values=["All"], width=15, state='readonly'
        )
        self.type_filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.type_filter_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_filters())
    
    def _setup_detail_view(self):
        """Setup the Pokemon detail editing view with tabs."""
        # Header with sprite and basic info
        header_frame = ttk.Frame(self.detail_content)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sprite display
        sprite_frame = ttk.LabelFrame(header_frame, text="Sprite", padding=5)
        sprite_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.sprite_label = ttk.Label(sprite_frame, text="No sprite" if not HAS_PIL else "Select Pokemon")
        self.sprite_label.pack()
        
        # Basic info next to sprite
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.species_label = ttk.Label(info_frame, text="Species: ", font=('Arial', 12, 'bold'))
        self.species_label.pack(anchor=tk.W)
        
        self.display_name_entry = LabeledEntry(info_frame, "Display Name:", width=30)
        self.display_name_entry.pack(fill=tk.X, pady=2)
        self.display_name_entry.bind_change(self._on_data_change)
        
        self.bst_label = ttk.Label(info_frame, text="BST: 0", font=('Arial', 10, 'bold'))
        self.bst_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.detail_content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stats tab
        stats_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(stats_tab, text="Base Stats")
        self._setup_stats_tab(stats_tab)
        
        # Types & Abilities tab
        types_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(types_tab, text="Types & Abilities")
        self._setup_types_tab(types_tab)
        
        # Learnset tab
        learnset_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(learnset_tab, text="Learnset")
        self._setup_learnset_tab(learnset_tab)
        
        # Other tab
        other_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(other_tab, text="Other")
        self._setup_other_tab(other_tab)
    
    def _setup_stats_tab(self, parent: ttk.Frame):
        """Setup the base stats tab."""
        self.stat_entries = {}
        stat_names = ['HP', 'Attack', 'Defense', 'Speed', 'Sp. Atk', 'Sp. Def']
        stat_keys = ['hp', 'atk', 'def', 'spe', 'spa', 'spdef']
        
        stats_frame = ttk.LabelFrame(parent, text="Base Stats", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        for i, (name, key) in enumerate(zip(stat_names, stat_keys)):
            row = i // 3
            col = i % 3
            
            frame = ttk.Frame(stats_grid)
            frame.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            
            ttk.Label(frame, text=f"{name}:", width=8).pack(side=tk.LEFT)
            var = tk.IntVar()
            spinbox = ttk.Spinbox(frame, textvariable=var, from_=1, to=255, width=5)
            spinbox.pack(side=tk.LEFT)
            
            self.stat_entries[key] = var
            var.trace('w', lambda *args: self._on_data_change())
        
        # EV Yield
        ev_frame = ttk.LabelFrame(parent, text="EV Yield", padding=10)
        ev_frame.pack(fill=tk.X, pady=5)
        
        self.ev_entries = {}
        ev_grid = ttk.Frame(ev_frame)
        ev_grid.pack(fill=tk.X)
        
        for i, (name, key) in enumerate(zip(stat_names, stat_keys)):
            row = i // 3
            col = i % 3
            
            frame = ttk.Frame(ev_grid)
            frame.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            
            ttk.Label(frame, text=f"{name}:", width=8).pack(side=tk.LEFT)
            var = tk.IntVar()
            spinbox = ttk.Spinbox(frame, textvariable=var, from_=0, to=3, width=3)
            spinbox.pack(side=tk.LEFT)
            
            self.ev_entries[key] = var
            var.trace('w', lambda *args: self._on_data_change())
    
    def _setup_types_tab(self, parent: ttk.Frame):
        """Setup the types and abilities tab."""
        # Types
        types_frame = ttk.LabelFrame(parent, text="Types", padding=10)
        types_frame.pack(fill=tk.X, pady=5)
        
        types_row = ttk.Frame(types_frame)
        types_row.pack(fill=tk.X)
        
        self.type1_combo = LabeledCombobox(types_row, "Type 1:", [], width=20)
        self.type1_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.type1_combo.bind_change(self._on_data_change)
        
        self.type2_combo = LabeledCombobox(types_row, "Type 2:", [], width=20)
        self.type2_combo.pack(side=tk.LEFT)
        self.type2_combo.bind_change(self._on_data_change)
        
        # Abilities
        abilities_frame = ttk.LabelFrame(parent, text="Abilities", padding=10)
        abilities_frame.pack(fill=tk.X, pady=5)
        
        self.ability1_combo = LabeledCombobox(abilities_frame, "Ability 1:", [], width=35)
        self.ability1_combo.pack(fill=tk.X, pady=2)
        self.ability1_combo.bind_change(self._on_data_change)
        
        self.ability2_combo = LabeledCombobox(abilities_frame, "Ability 2:", [], width=35)
        self.ability2_combo.pack(fill=tk.X, pady=2)
        self.ability2_combo.bind_change(self._on_data_change)
        
        self.hidden_ability_combo = LabeledCombobox(abilities_frame, "Hidden Ability:", [], width=35)
        self.hidden_ability_combo.pack(fill=tk.X, pady=2)
        self.hidden_ability_combo.bind_change(self._on_data_change)
        
        # Egg Groups
        egg_frame = ttk.LabelFrame(parent, text="Egg Groups", padding=10)
        egg_frame.pack(fill=tk.X, pady=5)
        
        egg_groups = [
            "EGG_GROUP_MONSTER", "EGG_GROUP_WATER_1", "EGG_GROUP_BUG",
            "EGG_GROUP_FLYING", "EGG_GROUP_GROUND", "EGG_GROUP_FAIRY",
            "EGG_GROUP_PLANT", "EGG_GROUP_HUMAN_LIKE", "EGG_GROUP_WATER_3",
            "EGG_GROUP_MINERAL", "EGG_GROUP_AMORPHOUS", "EGG_GROUP_WATER_2",
            "EGG_GROUP_DITTO", "EGG_GROUP_DRAGON", "EGG_GROUP_UNDISCOVERED"
        ]
        
        egg_row = ttk.Frame(egg_frame)
        egg_row.pack(fill=tk.X)
        
        self.egg_group1_combo = LabeledCombobox(egg_row, "Egg Group 1:", egg_groups, width=25)
        self.egg_group1_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.egg_group1_combo.bind_change(self._on_data_change)
        
        self.egg_group2_combo = LabeledCombobox(egg_row, "Egg Group 2:", egg_groups, width=25)
        self.egg_group2_combo.pack(side=tk.LEFT)
        self.egg_group2_combo.bind_change(self._on_data_change)
    
    def _setup_learnset_tab(self, parent: ttk.Frame):
        """Setup the learnset tab with level moves, TM/HM, egg, and tutor moves."""
        # Create inner notebook for different move types
        move_notebook = ttk.Notebook(parent)
        move_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Level moves tab
        level_tab = ttk.Frame(move_notebook, padding=5)
        move_notebook.add(level_tab, text="Level Up")
        self._setup_level_moves(level_tab)
        
        # TM/HM tab
        tm_tab = ttk.Frame(move_notebook, padding=5)
        move_notebook.add(tm_tab, text="TM/HM")
        self._setup_tm_moves(tm_tab)
        
        # Egg moves tab
        egg_tab = ttk.Frame(move_notebook, padding=5)
        move_notebook.add(egg_tab, text="Egg Moves")
        self._setup_egg_moves(egg_tab)
        
        # Tutor moves tab
        tutor_tab = ttk.Frame(move_notebook, padding=5)
        move_notebook.add(tutor_tab, text="Tutor")
        self._setup_tutor_moves(tutor_tab)
    
    def _setup_level_moves(self, parent: ttk.Frame):
        """Setup level-up moves section."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_level_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove", command=self._remove_level_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Sort by Level", command=self._sort_level_moves).pack(side=tk.LEFT, padx=2)
        
        columns = ('level', 'move')
        self.level_moves_tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        self.level_moves_tree.heading('level', text='Level')
        self.level_moves_tree.heading('move', text='Move')
        self.level_moves_tree.column('level', width=60)
        self.level_moves_tree.column('move', width=250)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.level_moves_tree.yview)
        self.level_moves_tree.configure(yscrollcommand=scrollbar.set)
        
        self.level_moves_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.level_moves_tree.bind('<Double-1>', self._edit_level_move)
    
    def _setup_tm_moves(self, parent: ttk.Frame):
        """Setup TM/HM moves section."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_tm_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove", command=self._remove_tm_move).pack(side=tk.LEFT, padx=2)
        
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tm_moves_list = tk.Listbox(parent, yscrollcommand=scrollbar.set, height=12, selectmode=tk.EXTENDED)
        self.tm_moves_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tm_moves_list.yview)
    
    def _setup_egg_moves(self, parent: ttk.Frame):
        """Setup egg moves section."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_egg_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove", command=self._remove_egg_move).pack(side=tk.LEFT, padx=2)
        
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.egg_moves_list = tk.Listbox(parent, yscrollcommand=scrollbar.set, height=12, selectmode=tk.EXTENDED)
        self.egg_moves_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.egg_moves_list.yview)
    
    def _setup_tutor_moves(self, parent: ttk.Frame):
        """Setup tutor moves section."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Move", command=self._add_tutor_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove", command=self._remove_tutor_move).pack(side=tk.LEFT, padx=2)
        
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tutor_moves_list = tk.Listbox(parent, yscrollcommand=scrollbar.set, height=12, selectmode=tk.EXTENDED)
        self.tutor_moves_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tutor_moves_list.yview)
    
    def _setup_other_tab(self, parent: ttk.Frame):
        """Setup the other properties tab."""
        # Basic properties
        basic_frame = ttk.LabelFrame(parent, text="Basic Properties", padding=10)
        basic_frame.pack(fill=tk.X, pady=5)
        
        self.catch_rate_spin = LabeledSpinbox(basic_frame, "Catch Rate:", from_=1, to=255)
        self.catch_rate_spin.pack(fill=tk.X, pady=2)
        self.catch_rate_spin.bind_change(self._on_data_change)
        
        self.base_exp_spin = LabeledSpinbox(basic_frame, "Base Exp:", from_=0, to=999)
        self.base_exp_spin.pack(fill=tk.X, pady=2)
        self.base_exp_spin.bind_change(self._on_data_change)
        
        self.base_friendship_spin = LabeledSpinbox(basic_frame, "Base Friendship:", from_=0, to=255)
        self.base_friendship_spin.pack(fill=tk.X, pady=2)
        self.base_friendship_spin.bind_change(self._on_data_change)
        
        # Breeding
        breed_frame = ttk.LabelFrame(parent, text="Breeding", padding=10)
        breed_frame.pack(fill=tk.X, pady=5)
        
        self.gender_ratio_spin = LabeledSpinbox(breed_frame, "Gender Ratio:", from_=0, to=255)
        self.gender_ratio_spin.pack(fill=tk.X, pady=2)
        self.gender_ratio_spin.bind_change(self._on_data_change)
        
        ttk.Label(breed_frame, text="(0=All Male, 254=All Female, 255=Genderless, 127=50/50)", 
                  foreground='gray').pack(anchor=tk.W)
        
        self.egg_cycles_spin = LabeledSpinbox(breed_frame, "Egg Cycles:", from_=1, to=120)
        self.egg_cycles_spin.pack(fill=tk.X, pady=2)
        self.egg_cycles_spin.bind_change(self._on_data_change)
        
        growth_rates = [
            "GROWTH_MEDIUM_FAST", "GROWTH_ERRATIC", "GROWTH_FLUCTUATING",
            "GROWTH_MEDIUM_SLOW", "GROWTH_FAST", "GROWTH_SLOW"
        ]
        self.growth_rate_combo = LabeledCombobox(breed_frame, "Growth Rate:", growth_rates, width=25)
        self.growth_rate_combo.pack(fill=tk.X, pady=2)
        self.growth_rate_combo.bind_change(self._on_data_change)
        
        # Held Items
        items_frame = ttk.LabelFrame(parent, text="Wild Held Items", padding=10)
        items_frame.pack(fill=tk.X, pady=5)
        
        self.item1_combo = LabeledCombobox(items_frame, "Common (50%):", [], width=30)
        self.item1_combo.pack(fill=tk.X, pady=2)
        self.item1_combo.bind_change(self._on_data_change)
        
        self.item2_combo = LabeledCombobox(items_frame, "Rare (5%):", [], width=30)
        self.item2_combo.pack(fill=tk.X, pady=2)
        self.item2_combo.bind_change(self._on_data_change)
    
    def _load_data(self):
        """Load Pokemon and learnset data."""
        try:
            self.pokemon_data = self.asm_parser.parse_mondata()
            self.set_status(f"Loaded {len(self.pokemon_data)} Pokemon from mondata.s")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Pokemon data: {e}")
            self.pokemon_data = {}
        
        try:
            self.learnset_data = self.json_handler.load_learnsets()
            self.set_status(f"Loaded {len(self.pokemon_data)} Pokemon, {len(self.learnset_data)} learnsets")
        except Exception as e:
            print(f"Warning: Could not load learnsets: {e}")
            self.learnset_data = {}
        
        self._populate_constants()
        self._populate_list()
    
    def _populate_constants(self):
        """Load constants for dropdowns."""
        try:
            types = self.constants.load_types()
            type_names = sorted([k for k in types.keys() if k.startswith('TYPE_')])
            self.type1_combo.set_values(type_names)
            self.type2_combo.set_values(type_names)
            self.type_filter_combo['values'] = ["All"] + type_names
        except Exception as e:
            print(f"Warning: Could not load types: {e}")
        
        try:
            abilities = self.constants.load_abilities()
            ability_names = sorted([k for k in abilities.keys() if k.startswith('ABILITY_')])
            self.ability1_combo.set_values(ability_names)
            self.ability2_combo.set_values(ability_names)
            self.hidden_ability_combo.set_values(ability_names)
        except Exception as e:
            print(f"Warning: Could not load abilities: {e}")
        
        try:
            items = self.constants.load_items()
            item_names = sorted([k for k in items.keys() if k.startswith('ITEM_')])
            self.item1_combo.set_values(item_names)
            self.item2_combo.set_values(item_names)
        except Exception as e:
            print(f"Warning: Could not load items: {e}")
        
        try:
            moves = self.constants.load_moves()
            self.move_names = sorted([k for k in moves.keys() if k.startswith('MOVE_')])
        except Exception as e:
            print(f"Warning: Could not load moves: {e}")
    
    def _populate_list(self):
        """Populate the Pokemon list."""
        self.item_list.delete(0, tk.END)
        self.filtered_list = sorted(self.pokemon_data.keys())
        
        for species in self.filtered_list:
            entry = self.pokemon_data[species]
            display = f"{species}"
            if entry.display_name:
                display += f" ({entry.display_name})"
            self.item_list.insert(tk.END, display)
    
    def _apply_filters(self):
        """Apply search and type filters to the list."""
        search_term = self.search_var.get().lower()
        type_filter = self.type_filter_var.get()
        
        self.item_list.delete(0, tk.END)
        self.filtered_list = []
        
        for species in sorted(self.pokemon_data.keys()):
            entry = self.pokemon_data[species]
            
            if search_term:
                if search_term not in species.lower() and search_term not in entry.display_name.lower():
                    continue
            
            if type_filter != "All":
                if type_filter not in entry.types:
                    continue
            
            self.filtered_list.append(species)
            display = f"{species}"
            if entry.display_name:
                display += f" ({entry.display_name})"
            self.item_list.insert(tk.END, display)
        
        self.set_status(f"Showing {len(self.filtered_list)} of {len(self.pokemon_data)} Pokemon")
    
    def _on_search(self):
        """Handle search input."""
        self._apply_filters()
    
    def _on_item_select(self, event):
        """Handle Pokemon selection."""
        selection = self.item_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.filtered_list):
            species = self.filtered_list[index]
            self._load_pokemon(species)
    
    def _get_sprite_path(self, species: str) -> Optional[Path]:
        """Get the sprite path for a species."""
        sprite_name = species.replace('SPECIES_', '').lower()
        sprite_dir = self.asm_parser.project_root / 'data' / 'graphics' / 'sprites' / sprite_name
        
        paths_to_try = [
            sprite_dir / 'male' / 'front.png',
            sprite_dir / 'front.png',
            sprite_dir / 'male' / 'back.png',
        ]
        
        for path in paths_to_try:
            if path.exists():
                return path
        
        return None
    
    def _load_sprite(self, species: str):
        """Load and display the sprite for a species."""
        if not HAS_PIL:
            self.sprite_label.config(text="PIL not installed", image='')
            return
        
        if species in self.sprite_cache:
            self.current_sprite = self.sprite_cache[species]
            self.sprite_label.config(image=self.current_sprite, text='')
            return
        
        sprite_path = self._get_sprite_path(species)
        if sprite_path is None:
            self.sprite_label.config(text="No sprite", image='')
            return
        
        try:
            img = Image.open(sprite_path)
            # Sprites are 160x80 (two 80x80 frames), take left half
            if img.width == 160:
                img = img.crop((0, 0, 80, 80))
            # Scale up for visibility
            img = img.resize((96, 96), Image.Resampling.NEAREST)
            
            photo = ImageTk.PhotoImage(img)
            self.sprite_cache[species] = photo
            self.current_sprite = photo
            self.sprite_label.config(image=photo, text='')
        except Exception as e:
            print(f"Error loading sprite: {e}")
            self.sprite_label.config(text="Error", image='')
    
    def _load_pokemon(self, species: str):
        """Load a Pokemon's data into the editor."""
        if species not in self.pokemon_data:
            return
        
        self.current_species = species
        entry = self.pokemon_data[species]
        learnset = self.learnset_data.get(species)
        
        self._loading = True
        
        try:
            # Header
            self.species_label.config(text=f"Species: {species}")
            self.display_name_entry.set(entry.display_name)
            
            # Sprite
            self._load_sprite(species)
            
            # Base stats
            for key, var in self.stat_entries.items():
                var.set(entry.basestats.get(key, 0))
            
            self._update_bst()
            
            # Types
            if entry.types:
                self.type1_combo.set(entry.types[0] if len(entry.types) > 0 else "")
                self.type2_combo.set(entry.types[1] if len(entry.types) > 1 else entry.types[0])
            
            # Abilities
            if entry.abilities:
                self.ability1_combo.set(entry.abilities[0] if len(entry.abilities) > 0 else "")
                self.ability2_combo.set(entry.abilities[1] if len(entry.abilities) > 1 else "ABILITY_NONE")
            self.hidden_ability_combo.set(entry.hiddenability)
            
            # Other properties
            self.catch_rate_spin.set(entry.catchrate)
            self.base_exp_spin.set(entry.baseexp)
            self.gender_ratio_spin.set(entry.genderratio)
            self.egg_cycles_spin.set(entry.eggcycles)
            self.base_friendship_spin.set(entry.basefriendship)
            self.growth_rate_combo.set(entry.growthrate)
            
            # EV yield
            for key, var in self.ev_entries.items():
                var.set(entry.evyield.get(key, 0))
            
            # Egg groups
            if entry.egggroups:
                self.egg_group1_combo.set(entry.egggroups[0] if len(entry.egggroups) > 0 else "")
                self.egg_group2_combo.set(entry.egggroups[1] if len(entry.egggroups) > 1 else entry.egggroups[0])
            
            # Items
            if entry.items:
                self.item1_combo.set(entry.items[0] if len(entry.items) > 0 else "ITEM_NONE")
                self.item2_combo.set(entry.items[1] if len(entry.items) > 1 else "ITEM_NONE")
            
            # Learnset
            self._load_learnset(learnset)
        
        finally:
            self._loading = False
    
    def _load_learnset(self, learnset: Optional[LearnsetEntry]):
        """Load learnset data into UI."""
        # Clear all
        for item in self.level_moves_tree.get_children():
            self.level_moves_tree.delete(item)
        self.tm_moves_list.delete(0, tk.END)
        self.egg_moves_list.delete(0, tk.END)
        self.tutor_moves_list.delete(0, tk.END)
        
        if learnset is None:
            return
        
        # Level moves
        for move_data in learnset.level_moves:
            if isinstance(move_data, dict):
                level = move_data.get('level', move_data.get('Level', 0))
                move = move_data.get('move', move_data.get('Move', ''))
            else:
                level, move = 0, str(move_data)
            self.level_moves_tree.insert('', tk.END, values=(level, move))
        
        # TM moves
        for move in learnset.machine_moves:
            self.tm_moves_list.insert(tk.END, move)
        
        # Egg moves
        for move in learnset.egg_moves:
            self.egg_moves_list.insert(tk.END, move)
        
        # Tutor moves
        for move in learnset.tutor_moves:
            self.tutor_moves_list.insert(tk.END, move)
    
    def _on_data_change(self):
        """Handle data changes in the editor."""
        if hasattr(self, '_loading') and self._loading:
            return
        
        if self.current_species:
            self._save_current_to_data()
            self.set_modified(True)
        
        self._update_bst()
    
    def _update_bst(self):
        """Update the BST display."""
        total = sum(var.get() for var in self.stat_entries.values())
        self.bst_label.config(text=f"BST: {total}")
    
    def _save_current_to_data(self):
        """Save current editor state back to data."""
        if not self.current_species:
            return
        
        entry = self.pokemon_data[self.current_species]
        
        entry.display_name = self.display_name_entry.get()
        entry.basestats = {key: var.get() for key, var in self.stat_entries.items()}
        entry.types = [self.type1_combo.get(), self.type2_combo.get()]
        entry.abilities = [self.ability1_combo.get(), self.ability2_combo.get()]
        entry.hiddenability = self.hidden_ability_combo.get()
        entry.catchrate = self.catch_rate_spin.get()
        entry.baseexp = self.base_exp_spin.get()
        entry.genderratio = self.gender_ratio_spin.get()
        entry.eggcycles = self.egg_cycles_spin.get()
        entry.basefriendship = self.base_friendship_spin.get()
        entry.growthrate = self.growth_rate_combo.get()
        entry.evyield = {key: var.get() for key, var in self.ev_entries.items()}
        entry.egggroups = [self.egg_group1_combo.get(), self.egg_group2_combo.get()]
        entry.items = [self.item1_combo.get(), self.item2_combo.get()]
        
        # Save learnset
        self._save_learnset_to_data()
    
    def _save_learnset_to_data(self):
        """Save learnset data."""
        if not self.current_species:
            return
        
        if self.current_species not in self.learnset_data:
            self.learnset_data[self.current_species] = LearnsetEntry(species=self.current_species)
        
        entry = self.learnset_data[self.current_species]
        
        entry.level_moves = []
        for item in self.level_moves_tree.get_children():
            values = self.level_moves_tree.item(item, 'values')
            entry.level_moves.append({'level': int(values[0]), 'move': values[1]})
        
        entry.machine_moves = list(self.tm_moves_list.get(0, tk.END))
        entry.egg_moves = list(self.egg_moves_list.get(0, tk.END))
        entry.tutor_moves = list(self.tutor_moves_list.get(0, tk.END))
    
    # Move editing methods
    def _add_level_move(self):
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        dialog = MoveDialog(self.root, "Add Level-Up Move", self.move_names, show_level=True)
        if dialog.result:
            level, move = dialog.result
            self.level_moves_tree.insert('', tk.END, values=(level, move))
            self._save_learnset_to_data()
            self.set_modified(True)
    
    def _remove_level_move(self):
        selection = self.level_moves_tree.selection()
        if selection:
            for item in selection:
                self.level_moves_tree.delete(item)
            self._save_learnset_to_data()
            self.set_modified(True)
    
    def _edit_level_move(self, event):
        selection = self.level_moves_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.level_moves_tree.item(item, 'values')
        dialog = MoveDialog(self.root, "Edit Level-Up Move", self.move_names, 
                           show_level=True, initial_level=int(values[0]), initial_move=values[1])
        if dialog.result:
            level, move = dialog.result
            self.level_moves_tree.item(item, values=(level, move))
            self._save_learnset_to_data()
            self.set_modified(True)
    
    def _sort_level_moves(self):
        items = []
        for item in self.level_moves_tree.get_children():
            values = self.level_moves_tree.item(item, 'values')
            items.append((int(values[0]), values[1]))
        items.sort(key=lambda x: x[0])
        for item in self.level_moves_tree.get_children():
            self.level_moves_tree.delete(item)
        for level, move in items:
            self.level_moves_tree.insert('', tk.END, values=(level, move))
        self._save_learnset_to_data()
        self.set_modified(True)
    
    def _add_tm_move(self):
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        dialog = MoveDialog(self.root, "Add TM/HM Move", self.move_names)
        if dialog.result:
            _, move = dialog.result
            self.tm_moves_list.insert(tk.END, move)
            self._save_learnset_to_data()
            self.set_modified(True)
    
    def _remove_tm_move(self):
        selection = list(self.tm_moves_list.curselection())
        for i in reversed(selection):
            self.tm_moves_list.delete(i)
        self._save_learnset_to_data()
        self.set_modified(True)
    
    def _add_egg_move(self):
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        dialog = MoveDialog(self.root, "Add Egg Move", self.move_names)
        if dialog.result:
            _, move = dialog.result
            self.egg_moves_list.insert(tk.END, move)
            self._save_learnset_to_data()
            self.set_modified(True)
    
    def _remove_egg_move(self):
        selection = list(self.egg_moves_list.curselection())
        for i in reversed(selection):
            self.egg_moves_list.delete(i)
        self._save_learnset_to_data()
        self.set_modified(True)
    
    def _add_tutor_move(self):
        if not self.current_species:
            messagebox.showwarning("Warning", "Please select a Pokemon first")
            return
        dialog = MoveDialog(self.root, "Add Tutor Move", self.move_names)
        if dialog.result:
            _, move = dialog.result
            self.tutor_moves_list.insert(tk.END, move)
            self._save_learnset_to_data()
            self.set_modified(True)
    
    def _remove_tutor_move(self):
        selection = list(self.tutor_moves_list.curselection())
        for i in reversed(selection):
            self.tutor_moves_list.delete(i)
        self._save_learnset_to_data()
        self.set_modified(True)
    
    # Search methods
    def _recalculate_bst(self):
        self._update_bst()
    
    def _find_by_type(self):
        self.set_status("Use the Type dropdown filter in the toolbar")
    
    def _find_by_ability(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Find by Ability")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select Ability:").pack(pady=5)
        
        ability_var = tk.StringVar()
        abilities = self.constants.load_abilities()
        ability_names = sorted([k for k in abilities.keys() if k.startswith('ABILITY_')])
        
        combo = ttk.Combobox(dialog, textvariable=ability_var, values=ability_names, width=35)
        combo.pack(pady=5)
        
        result_list = tk.Listbox(dialog, height=10)
        result_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def search():
            ability = ability_var.get()
            result_list.delete(0, tk.END)
            for species, entry in self.pokemon_data.items():
                if ability in entry.abilities or ability == entry.hiddenability:
                    ha = " (HA)" if ability == entry.hiddenability else ""
                    result_list.insert(tk.END, f"{species} ({entry.display_name}){ha}")
        
        ttk.Button(dialog, text="Search", command=search).pack(pady=5)
    
    def _find_by_move(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Find by Move")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Select Move:").pack(pady=5)
        
        move_var = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=move_var, values=self.move_names, width=35)
        combo.pack(pady=5)
        
        columns = ('species', 'source')
        tree = ttk.Treeview(dialog, columns=columns, show='headings')
        tree.heading('species', text='Pokemon')
        tree.heading('source', text='Learn Method')
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def search():
            target = move_var.get()
            for item in tree.get_children():
                tree.delete(item)
            
            for species, entry in self.learnset_data.items():
                sources = []
                for move_data in entry.level_moves:
                    move = move_data.get('move', move_data.get('Move', '')) if isinstance(move_data, dict) else move_data
                    if move == target:
                        level = move_data.get('level', move_data.get('Level', 0)) if isinstance(move_data, dict) else 0
                        sources.append(f"Level {level}")
                        break
                if target in entry.machine_moves:
                    sources.append("TM/HM")
                if target in entry.egg_moves:
                    sources.append("Egg")
                if target in entry.tutor_moves:
                    sources.append("Tutor")
                
                if sources:
                    tree.insert('', tk.END, values=(species, ", ".join(sources)))
        
        ttk.Button(dialog, text="Search", command=search).pack(pady=5)
    
    def save(self) -> bool:
        try:
            self.json_handler.save_learnsets(self.learnset_data)
            self.asm_parser.save_mondata(self.pokemon_data)
            self.set_status("Learnsets and mondata saved successfully")
            messagebox.showinfo("Save", "Learnsets saved to learnsets.json\nmondata saved to armips/data/mondata.s")
            self.set_modified(False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            return False


class MoveDialog(tk.Toplevel):
    """Dialog for selecting a move."""
    
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
            ttk.Spinbox(level_frame, textvariable=self.level_var, from_=0, to=100, width=10).pack(side=tk.LEFT)
        else:
            self.level_var = tk.IntVar(value=0)
        
        move_frame = ttk.Frame(main_frame)
        move_frame.pack(fill=tk.X, pady=5)
        ttk.Label(move_frame, text="Move:", width=10).pack(side=tk.LEFT)
        self.move_var = tk.StringVar(value=initial_move)
        self.move_combo = ttk.Combobox(move_frame, textvariable=self.move_var, values=move_names, width=35)
        self.move_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
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
    """Run the Pokemon editor standalone."""
    editor = PokemonEditor()
    editor.run()


if __name__ == "__main__":
    main()
