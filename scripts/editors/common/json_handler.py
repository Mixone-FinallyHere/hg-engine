"""
JSON Handler
=============
Handles loading and saving JSON data files like learnsets.json
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class LearnsetEntry:
    """Represents a Pokemon's learnset data."""
    species: str
    level_moves: List[Dict[str, Any]] = field(default_factory=list)  # [{"level": 1, "move": "MOVE_X"}]
    machine_moves: List[str] = field(default_factory=list)  # ["MOVE_X", "MOVE_Y"]
    egg_moves: List[str] = field(default_factory=list)
    tutor_moves: List[str] = field(default_factory=list)


class JSONHandler:
    """Handler for JSON data files."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the JSON handler.
        
        Args:
            project_root: Path to hg-engine root. Auto-detected if None.
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
    
    def load_learnsets(self, filepath: Optional[Path] = None) -> Dict[str, LearnsetEntry]:
        """
        Load learnsets from learnsets.json.
        
        Args:
            filepath: Path to learnsets.json. Uses default if None.
            
        Returns:
            Dictionary mapping species name to LearnsetEntry.
        """
        if filepath is None:
            filepath = self.project_root / 'data' / 'learnsets' / 'learnsets.json'
        
        entries = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for species, learnset_data in data.items():
            entry = LearnsetEntry(species=species)
            
            # Parse LevelMoves
            if 'LevelMoves' in learnset_data:
                for item in learnset_data['LevelMoves']:
                    if isinstance(item, dict):
                        entry.level_moves.append(item)
                    elif isinstance(item, list) and len(item) == 2:
                        entry.level_moves.append({
                            'level': item[0],
                            'move': item[1]
                        })
            
            # Parse MachineMoves
            if 'MachineMoves' in learnset_data:
                entry.machine_moves = learnset_data['MachineMoves']
            
            # Parse EggMoves
            if 'EggMoves' in learnset_data:
                entry.egg_moves = learnset_data['EggMoves']
            
            # Parse TutorMoves
            if 'TutorMoves' in learnset_data:
                entry.tutor_moves = learnset_data['TutorMoves']
            
            entries[species] = entry
        
        return entries
    
    def save_learnsets(self, entries: Dict[str, LearnsetEntry], filepath: Optional[Path] = None):
        """
        Save learnsets to learnsets.json.
        
        Args:
            entries: Dictionary mapping species name to LearnsetEntry.
            filepath: Path to learnsets.json. Uses default if None.
        """
        if filepath is None:
            filepath = self.project_root / 'data' / 'learnsets' / 'learnsets.json'
        
        data = {}
        
        for species, entry in entries.items():
            learnset_data = {}
            
            if entry.level_moves:
                learnset_data['LevelMoves'] = entry.level_moves
            
            if entry.machine_moves:
                learnset_data['MachineMoves'] = entry.machine_moves
            
            if entry.egg_moves:
                learnset_data['EggMoves'] = entry.egg_moves
            
            if entry.tutor_moves:
                learnset_data['TutorMoves'] = entry.tutor_moves
            
            data[species] = learnset_data
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_json(self, filepath: Path) -> Any:
        """Load arbitrary JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_json(self, data: Any, filepath: Path, indent: int = 2):
        """Save arbitrary data to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
