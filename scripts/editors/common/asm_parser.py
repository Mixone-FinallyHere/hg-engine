"""
ASM Parser
==========
Parses armips assembly files to extract data defined with macros.
Supports mondata, movedata, trainerdata, and other hg-engine macro formats.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass, field


@dataclass
class MondataEntry:
    """Represents a single Pokemon's data from mondata.s"""
    species: str
    display_name: str = ""
    basestats: Dict[str, int] = field(default_factory=dict)
    types: List[str] = field(default_factory=list)
    catchrate: int = 45
    baseexp: int = 0
    evyield: Dict[str, int] = field(default_factory=dict)
    items: List[str] = field(default_factory=list)
    genderratio: int = 127
    eggcycles: int = 20
    basefriendship: int = 70
    growthrate: str = "GROWTH_MEDIUM_FAST"
    egggroups: List[str] = field(default_factory=list)
    abilities: List[str] = field(default_factory=list)
    hiddenability: str = "ABILITY_NONE"
    runrate: int = 0
    colorflip: str = ""
    raw_lines: List[str] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


@dataclass
class MovedataEntry:
    """Represents a single move's data from moves.s"""
    move_id: str
    display_name: str = ""
    battleeffect: str = ""
    basepower: int = 0
    type: str = "TYPE_NORMAL"
    accuracy: int = 100
    pp: int = 35
    effectchance: int = 0
    target: str = "TARGET_SELECTED_POKEMON"
    priority: int = 0
    flags: List[str] = field(default_factory=list)
    contesteffect: str = ""
    contesttype: str = ""
    raw_lines: List[str] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


@dataclass
class TrainerdataEntry:
    """Represents a single trainer's data from trainers.s"""
    trainer_id: str
    name: str = ""
    trainer_class: str = ""
    sprite: str = ""
    items: List[str] = field(default_factory=list)
    aiflags: List[str] = field(default_factory=list)
    trainermontype_flags: List[str] = field(default_factory=list)  # Bitfield flags as list
    extra_flags: List[str] = field(default_factory=list)  # Additional extra type flags
    nummons: int = 0
    battletype: str = "battletype_pokemon_trainer"
    party: List[Dict[str, Any]] = field(default_factory=list)  # Pokemon in party
    raw_lines: List[str] = field(default_factory=list)
    line_start: int = 0
    line_end: int = 0


class ASMParser:
    """Parser for armips assembly data files."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the ASM parser.
        
        Args:
            project_root: Path to hg-engine root. Auto-detected if None.
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
    
    def parse_mondata(self, filepath: Optional[Path] = None) -> Dict[str, MondataEntry]:
        """
        Parse mondata.s file and extract Pokemon data.
        
        Args:
            filepath: Path to mondata.s. Uses default if None.
            
        Returns:
            Dictionary mapping species name to MondataEntry.
        """
        if filepath is None:
            filepath = self.project_root / 'armips' / 'data' / 'mondata.s'
        
        entries = {}
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_entry: Optional[MondataEntry] = None
        current_lines: List[str] = []
        line_start = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for mondata macro start
            mondata_match = re.match(r'^mondata\s+(\w+)\s*,\s*"([^"]*)"', stripped)
            if mondata_match:
                # Save previous entry
                if current_entry:
                    current_entry.raw_lines = current_lines
                    current_entry.line_end = line_num - 1
                    entries[current_entry.species] = current_entry
                
                # Start new entry
                species = mondata_match.group(1)
                display_name = mondata_match.group(2)
                current_entry = MondataEntry(
                    species=species,
                    display_name=display_name,
                    line_start=line_num
                )
                current_lines = [line]
                continue
            
            if current_entry is None:
                continue
            
            current_lines.append(line)
            
            # Parse individual fields
            if stripped.startswith('basestats'):
                # basestats 45, 49, 49, 45, 65, 65
                match = re.match(r'basestats\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', stripped)
                if match:
                    current_entry.basestats = {
                        'hp': int(match.group(1)),
                        'atk': int(match.group(2)),
                        'def': int(match.group(3)),
                        'spe': int(match.group(4)),
                        'spa': int(match.group(5)),
                        'spdef': int(match.group(6))
                    }
            
            elif stripped.startswith('types '):
                # types TYPE_GRASS, TYPE_POISON
                match = re.match(r'types\s+(\w+)\s*(?:,\s*(\w+))?', stripped)
                if match:
                    current_entry.types = [match.group(1)]
                    if match.group(2):
                        current_entry.types.append(match.group(2))
            
            elif stripped.startswith('catchrate'):
                match = re.match(r'catchrate\s+(\d+)', stripped)
                if match:
                    current_entry.catchrate = int(match.group(1))
            
            elif stripped.startswith('baseexp'):
                match = re.match(r'baseexp\s+(\d+)', stripped)
                if match:
                    current_entry.baseexp = int(match.group(1))
            
            elif stripped.startswith('evyield'):
                # evyield 0, 0, 0, 0, 1, 0
                match = re.match(r'evyield\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', stripped)
                if match:
                    current_entry.evyield = {
                        'hp': int(match.group(1)),
                        'atk': int(match.group(2)),
                        'def': int(match.group(3)),
                        'spe': int(match.group(4)),
                        'spa': int(match.group(5)),
                        'spdef': int(match.group(6))
                    }
            
            elif stripped.startswith('items '):
                # items ITEM_NONE, ITEM_NONE
                match = re.match(r'items\s+(\w+)\s*(?:,\s*(\w+))?', stripped)
                if match:
                    current_entry.items = [match.group(1)]
                    if match.group(2):
                        current_entry.items.append(match.group(2))
            
            elif stripped.startswith('genderratio'):
                match = re.match(r'genderratio\s+(\d+)', stripped)
                if match:
                    current_entry.genderratio = int(match.group(1))
            
            elif stripped.startswith('eggcycles'):
                match = re.match(r'eggcycles\s+(\d+)', stripped)
                if match:
                    current_entry.eggcycles = int(match.group(1))
            
            elif stripped.startswith('basefriendship'):
                match = re.match(r'basefriendship\s+(\d+)', stripped)
                if match:
                    current_entry.basefriendship = int(match.group(1))
            
            elif stripped.startswith('growthrate'):
                match = re.match(r'growthrate\s+(\w+)', stripped)
                if match:
                    current_entry.growthrate = match.group(1)
            
            elif stripped.startswith('egggroups'):
                # egggroups EGG_GROUP_MONSTER, EGG_GROUP_GRASS
                match = re.match(r'egggroups\s+(\w+)\s*(?:,\s*(\w+))?', stripped)
                if match:
                    current_entry.egggroups = [match.group(1)]
                    if match.group(2):
                        current_entry.egggroups.append(match.group(2))
            
            elif stripped.startswith('abilities'):
                # abilities ABILITY_OVERGROW, ABILITY_NONE
                match = re.match(r'abilities\s+(\w+)\s*(?:,\s*(\w+))?', stripped)
                if match:
                    current_entry.abilities = [match.group(1)]
                    if match.group(2):
                        current_entry.abilities.append(match.group(2))
            
            elif stripped.startswith('hiddenability'):
                match = re.match(r'hiddenability\s+(\w+)', stripped)
                if match:
                    current_entry.hiddenability = match.group(1)
            
            elif stripped.startswith('terminatealiases') or stripped.startswith('terminatealiasesaliases'):
                # End of entry (but we use mondata start to delimit)
                pass
        
        # Save last entry
        if current_entry:
            current_entry.raw_lines = current_lines
            current_entry.line_end = len(lines)
            entries[current_entry.species] = current_entry
        
        return entries
    
    def parse_movedata(self, filepath: Optional[Path] = None) -> Dict[str, MovedataEntry]:
        """
        Parse moves.s file and extract move data.
        
        Args:
            filepath: Path to moves.s. Uses default if None.
            
        Returns:
            Dictionary mapping move ID to MovedataEntry.
        """
        if filepath is None:
            filepath = self.project_root / 'armips' / 'data' / 'moves.s'
        
        entries = {}
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_entry: Optional[MovedataEntry] = None
        current_lines: List[str] = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for movedata macro start
            movedata_match = re.match(r'^movedata\s+(\w+)\s*,\s*"([^"]*)"', stripped)
            if movedata_match:
                # Save previous entry
                if current_entry:
                    current_entry.raw_lines = current_lines
                    current_entry.line_end = line_num - 1
                    entries[current_entry.move_id] = current_entry
                
                # Start new entry
                move_id = movedata_match.group(1)
                display_name = movedata_match.group(2)
                current_entry = MovedataEntry(
                    move_id=move_id,
                    display_name=display_name,
                    line_start=line_num
                )
                current_lines = [line]
                continue
            
            if current_entry is None:
                continue
            
            current_lines.append(line)
            
            # Parse individual fields
            if stripped.startswith('battleeffect'):
                match = re.match(r'battleeffect\s+(\w+)', stripped)
                if match:
                    current_entry.battleeffect = match.group(1)
            
            elif stripped.startswith('basepower'):
                match = re.match(r'basepower\s+(\d+)', stripped)
                if match:
                    current_entry.basepower = int(match.group(1))
            
            elif stripped.startswith('type '):
                match = re.match(r'type\s+(\w+)', stripped)
                if match:
                    current_entry.type = match.group(1)
            
            elif stripped.startswith('accuracy'):
                match = re.match(r'accuracy\s+(\d+)', stripped)
                if match:
                    current_entry.accuracy = int(match.group(1))
            
            elif stripped.startswith('pp '):
                match = re.match(r'pp\s+(\d+)', stripped)
                if match:
                    current_entry.pp = int(match.group(1))
            
            elif stripped.startswith('effectchance'):
                match = re.match(r'effectchance\s+(\d+)', stripped)
                if match:
                    current_entry.effectchance = int(match.group(1))
            
            elif stripped.startswith('target'):
                match = re.match(r'target\s+(\w+)', stripped)
                if match:
                    current_entry.target = match.group(1)
            
            elif stripped.startswith('priority'):
                match = re.match(r'priority\s+(-?\d+)', stripped)
                if match:
                    current_entry.priority = int(match.group(1))
            
            elif stripped.startswith('contesttype'):
                match = re.match(r'contesttype\s+(\w+)', stripped)
                if match:
                    current_entry.contesttype = match.group(1)
            
            elif stripped.startswith('contesteffect'):
                match = re.match(r'contesteffect\s+(\w+)', stripped)
                if match:
                    current_entry.contesteffect = match.group(1)
            
            elif stripped.startswith('terminatedata'):
                # End of entry
                pass
        
        # Save last entry
        if current_entry:
            current_entry.raw_lines = current_lines
            current_entry.line_end = len(lines)
            entries[current_entry.move_id] = current_entry
        
        return entries
    
    def parse_trainerdata(self, filepath: Optional[Path] = None) -> Dict[str, TrainerdataEntry]:
        """
        Parse trainers.s file and extract trainer data.
        
        Args:
            filepath: Path to trainers.s. Uses default if None.
            
        Returns:
            Dictionary mapping trainer ID to TrainerdataEntry.
        """
        if filepath is None:
            filepath = self.project_root / 'armips' / 'data' / 'trainers' / 'trainers.s'
        
        entries = {}
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_entry: Optional[TrainerdataEntry] = None
        current_pokemon: Optional[Dict[str, Any]] = None
        current_lines: List[str] = []
        in_party = False
        item_index = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip comments and empty lines for parsing (but keep in raw_lines)
            if stripped.startswith('//') or not stripped:
                if current_entry:
                    current_lines.append(line)
                continue
            
            # Check for trainerdata macro start
            trainer_match = re.match(r'^trainerdata\s+(\w+)\s*,\s*"([^"]*)"', stripped)
            if trainer_match:
                # Save previous entry
                if current_entry:
                    if current_pokemon:
                        current_entry.party.append(current_pokemon)
                    current_entry.raw_lines = current_lines
                    current_entry.line_end = line_num - 1
                    entries[current_entry.trainer_id] = current_entry
                
                # Start new entry
                trainer_id = trainer_match.group(1)
                name = trainer_match.group(2)
                current_entry = TrainerdataEntry(
                    trainer_id=trainer_id,
                    name=name,
                    line_start=line_num
                )
                current_lines = [line]
                current_pokemon = None
                in_party = False
                item_index = 0
                continue
            
            if current_entry is None:
                continue
            
            current_lines.append(line)
            
            # Parse trainer header fields (before party)
            if not in_party:
                if stripped.startswith('trainerclass'):
                    match = re.match(r'trainerclass\s+(\w+)', stripped)
                    if match:
                        current_entry.trainer_class = match.group(1)
                
                elif stripped.startswith('nummons'):
                    match = re.match(r'nummons\s+(\d+)', stripped)
                    if match:
                        current_entry.nummons = int(match.group(1))
                
                elif stripped.startswith('trainermontype'):
                    # trainermontype can be flags separated by |
                    match = re.match(r'trainermontype\s+(.+)', stripped)
                    if match:
                        flags_str = match.group(1).strip()
                        # Split by | and clean up
                        flags = [f.strip() for f in flags_str.split('|') if f.strip() and f.strip() != '0']
                        current_entry.trainermontype_flags = flags
                
                elif stripped.startswith('aiflags'):
                    match = re.match(r'aiflags\s+(.+)', stripped)
                    if match:
                        flags_str = match.group(1).strip()
                        flags = [f.strip() for f in flags_str.split('|') if f.strip() and f.strip() != '0']
                        current_entry.aiflags = flags
                
                elif stripped.startswith('battletype'):
                    match = re.match(r'battletype\s+(\w+)', stripped)
                    if match:
                        current_entry.battletype = match.group(1)
                
                elif stripped.startswith('item '):
                    match = re.match(r'item\s+(\w+)', stripped)
                    if match:
                        if len(current_entry.items) < 4:
                            current_entry.items.append(match.group(1))
                
                elif stripped.startswith('party '):
                    # Start of party section
                    in_party = True
                    current_pokemon = None
            
            # Parse party Pokemon fields
            if in_party:
                # New pokemon starts with 'ivs' typically, or explicit pokemon/monwithform
                if stripped.startswith('ivs ') or stripped.startswith('ivs\t'):
                    # Save previous pokemon if exists
                    if current_pokemon:
                        current_entry.party.append(current_pokemon)
                    # Start new pokemon
                    current_pokemon = {
                        'species': '',
                        'level': 0,
                        'ivs': 0,
                        'ability_slot': 0,
                        'item': '',
                        'moves': [],
                        'ability': '',
                        'ball': '',
                        'iv_values': [],
                        'ev_values': [],
                        'nature': '',
                        'shinylock': 0,
                        'additionalflags': [],
                    }
                    match = re.match(r'ivs\s+(\d+)', stripped)
                    if match:
                        current_pokemon['ivs'] = int(match.group(1))
                
                elif current_pokemon is not None:
                    if stripped.startswith('abilityslot'):
                        match = re.match(r'abilityslot\s+(\d+)', stripped)
                        if match:
                            current_pokemon['ability_slot'] = int(match.group(1))
                    
                    elif stripped.startswith('level ') or stripped.startswith('level\t'):
                        match = re.match(r'level\s+(\d+)', stripped)
                        if match:
                            current_pokemon['level'] = int(match.group(1))
                    
                    elif stripped.startswith('pokemon '):
                        match = re.match(r'pokemon\s+(\w+)', stripped)
                        if match:
                            current_pokemon['species'] = match.group(1)
                    
                    elif stripped.startswith('monwithform'):
                        match = re.match(r'monwithform\s+(\w+)\s*,\s*(\d+)', stripped)
                        if match:
                            current_pokemon['species'] = match.group(1)
                            current_pokemon['form'] = int(match.group(2))
                    
                    elif stripped.startswith('item '):
                        match = re.match(r'item\s+(\w+)', stripped)
                        if match:
                            current_pokemon['item'] = match.group(1)
                    
                    elif stripped.startswith('move '):
                        match = re.match(r'move\s+(\w+)', stripped)
                        if match:
                            current_pokemon['moves'].append(match.group(1))
                    
                    elif stripped.startswith('ability ') and not stripped.startswith('abilityslot'):
                        match = re.match(r'ability\s+(\w+)', stripped)
                        if match:
                            current_pokemon['ability'] = match.group(1)
                    
                    elif stripped.startswith('ball '):
                        match = re.match(r'ball\s+(\w+)', stripped)
                        if match:
                            current_pokemon['ball'] = match.group(1)
                    
                    elif stripped.startswith('setivs'):
                        match = re.match(r'setivs\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', stripped)
                        if match:
                            current_pokemon['iv_values'] = [int(match.group(i)) for i in range(1, 7)]
                    
                    elif stripped.startswith('setevs'):
                        match = re.match(r'setevs\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', stripped)
                        if match:
                            current_pokemon['ev_values'] = [int(match.group(i)) for i in range(1, 7)]
                    
                    elif stripped.startswith('nature '):
                        match = re.match(r'nature\s+(\w+)', stripped)
                        if match:
                            current_pokemon['nature'] = match.group(1)
                    
                    elif stripped.startswith('shinylock'):
                        match = re.match(r'shinylock\s+(\d+)', stripped)
                        if match:
                            current_pokemon['shinylock'] = int(match.group(1))
                    
                    elif stripped.startswith('additionalflags'):
                        match = re.match(r'additionalflags\s+(.+)', stripped)
                        if match:
                            flags_str = match.group(1).strip()
                            if flags_str != '0':
                                flags = [f.strip() for f in flags_str.split('|') if f.strip() and f.strip() != '0']
                                current_pokemon['additionalflags'] = flags
                    
                    elif stripped.startswith('ballseal'):
                        match = re.match(r'ballseal\s+(\d+)', stripped)
                        if match:
                            current_pokemon['ballseal'] = int(match.group(1))
                    
                    elif stripped.startswith('nickname'):
                        # Capture everything after 'nickname'
                        match = re.match(r'nickname\s+(.+)', stripped)
                        if match:
                            current_pokemon['nickname_raw'] = match.group(1)
                
                elif stripped.startswith('endparty'):
                    # End of party
                    if current_pokemon:
                        current_entry.party.append(current_pokemon)
                        current_pokemon = None
                    in_party = False
        
        # Save last entry
        if current_entry:
            if current_pokemon:
                current_entry.party.append(current_pokemon)
            current_entry.raw_lines = current_lines
            current_entry.line_end = len(lines)
            entries[current_entry.trainer_id] = current_entry
        
        return entries
    
    def write_mondata_entry(self, entry: MondataEntry) -> str:
        """Generate ASM source for a mondata entry."""
        lines = []
        lines.append(f'mondata {entry.species}, "{entry.display_name}"')
        
        if entry.basestats:
            stats = entry.basestats
            lines.append(f"    basestats {stats.get('hp', 0)}, {stats.get('atk', 0)}, {stats.get('def', 0)}, {stats.get('spe', 0)}, {stats.get('spa', 0)}, {stats.get('spdef', 0)}")
        
        if entry.types:
            if len(entry.types) == 2:
                lines.append(f"    types {entry.types[0]}, {entry.types[1]}")
            else:
                lines.append(f"    types {entry.types[0]}, {entry.types[0]}")
        
        lines.append(f"    catchrate {entry.catchrate}")
        lines.append(f"    baseexp {entry.baseexp}")
        
        if entry.evyield:
            ev = entry.evyield
            lines.append(f"    evyield {ev.get('hp', 0)}, {ev.get('atk', 0)}, {ev.get('def', 0)}, {ev.get('spe', 0)}, {ev.get('spa', 0)}, {ev.get('spdef', 0)}")
        
        if entry.items:
            if len(entry.items) == 2:
                lines.append(f"    items {entry.items[0]}, {entry.items[1]}")
            else:
                lines.append(f"    items {entry.items[0]}, ITEM_NONE")
        
        lines.append(f"    genderratio {entry.genderratio}")
        lines.append(f"    eggcycles {entry.eggcycles}")
        lines.append(f"    basefriendship {entry.basefriendship}")
        lines.append(f"    growthrate {entry.growthrate}")
        
        if entry.egggroups:
            if len(entry.egggroups) == 2:
                lines.append(f"    egggroups {entry.egggroups[0]}, {entry.egggroups[1]}")
            else:
                lines.append(f"    egggroups {entry.egggroups[0]}, {entry.egggroups[0]}")
        
        if entry.abilities:
            if len(entry.abilities) == 2:
                lines.append(f"    abilities {entry.abilities[0]}, {entry.abilities[1]}")
            else:
                lines.append(f"    abilities {entry.abilities[0]}, ABILITY_NONE")
        
        lines.append(f"    hiddenability {entry.hiddenability}")
        lines.append(f"    runrate {entry.runrate}")
        
        if entry.colorflip:
            lines.append(f"    colorflip {entry.colorflip}")
        
        lines.append("    terminatealiases")
        lines.append("")
        
        return '\n'.join(lines)
    
    def save_mondata(self, data: Dict[str, MondataEntry], filepath: Path = None) -> None:
        """Save all mondata entries to mondata.s file."""
        if filepath is None:
            filepath = self.project_root / "armips/data/mondata.s"
        lines = [
            ".nds",
            ".thumb",
            "",
            ".include \"armips/include/macros.s\"",
            ".include \"armips/include/constants.s\"",
            ".include \"armips/include/config.s\"",
            "",
            ".include \"asm/include/abilities.inc\"",
            ".include \"asm/include/items.inc\"",
            ".include \"asm/include/species.inc\"",
            "",
            "// all the mon personal data.  learnsets are specifically in data/mon/learnsets.json",
            "// basestats and evyields fields are formatted as such:  hp atk def speed spatk spdef",
            ""
        ]
        for entry in data.values():
            lines.append(self.write_mondata_entry(entry))
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
