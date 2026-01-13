"""
Changelog Generator
===================
Generates changelogs comparing current data to vanilla HeartGold or saved versions.
Supports downloading vanilla baseline from GitHub and creating version snapshots.
"""

import json
import os
import urllib.request
import urllib.error
import zipfile
import io
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .asm_parser import ASMParser, MondataEntry, MovedataEntry, TrainerdataEntry
from .json_handler import JSONHandler, LearnsetEntry


# GitHub repository info for vanilla data
GITHUB_REPO = "BluRosie/hg-engine"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Files to download for vanilla baseline
VANILLA_FILES = [
    "armips/data/mondata.s",
    "armips/data/moves.s",
    "armips/data/trainers/trainers.s",
    "data/learnsets/learnsets.json",
]


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass
class Change:
    """Represents a single change."""
    change_type: ChangeType
    category: str  # pokemon, move, trainer, learnset, etc.
    item_id: str   # The ID of the changed item
    field: str     # The specific field that changed (empty for add/remove)
    old_value: Any = None
    new_value: Any = None
    description: str = ""


@dataclass
class Changelog:
    """Complete changelog with all changes."""
    generated_at: str = ""
    compare_from: str = "vanilla"  # Version being compared from
    compare_to: str = "current"    # Version being compared to
    changes: List[Change] = field(default_factory=list)
    
    def add(self, change: Change):
        self.changes.append(change)
    
    def filter_by_category(self, category: str) -> List[Change]:
        return [c for c in self.changes if c.category == category]
    
    def filter_by_type(self, change_type: ChangeType) -> List[Change]:
        return [c for c in self.changes if c.change_type == change_type]
    
    def summary(self) -> Dict[str, int]:
        """Get summary of changes by category and type."""
        summary = {}
        for change in self.changes:
            key = f"{change.category}_{change.change_type.value}"
            summary[key] = summary.get(key, 0) + 1
        return summary
    
    def to_markdown(self) -> str:
        """Generate markdown changelog."""
        lines = [
            "# hg-engine Changelog",
            f"Generated: {self.generated_at}",
            f"Comparing: **{self.compare_from}** → **{self.compare_to}**",
            "",
            "## Summary",
            "",
        ]
        
        # Summary
        summary = self.summary()
        total = len(self.changes)
        added = len(self.filter_by_type(ChangeType.ADDED))
        modified = len(self.filter_by_type(ChangeType.MODIFIED))
        removed = len(self.filter_by_type(ChangeType.REMOVED))
        
        lines.append(f"- **Total Changes:** {total}")
        lines.append(f"- ✅ Added: {added}")
        lines.append(f"- 📝 Modified: {modified}")
        lines.append(f"- ❌ Removed: {removed}")
        lines.append("")
        
        # Group by category
        categories = {}
        for change in self.changes:
            if change.category not in categories:
                categories[change.category] = []
            categories[change.category].append(change)
        
        category_titles = {
            'pokemon': '## Pokémon Changes',
            'move': '## Move Changes',
            'trainer': '## Trainer Changes',
            'learnset': '## Learnset Changes',
            'ability': '## Ability Changes',
            'item': '## Item Changes',
        }
        
        for category, changes in categories.items():
            title = category_titles.get(category, f"## {category.title()} Changes")
            lines.append(title)
            lines.append("")
            
            # Group by item ID
            by_item = {}
            for change in changes:
                if change.item_id not in by_item:
                    by_item[change.item_id] = []
                by_item[change.item_id].append(change)
            
            for item_id, item_changes in sorted(by_item.items()):
                first = item_changes[0]
                
                if first.change_type == ChangeType.ADDED:
                    lines.append(f"### ✅ Added: {item_id}")
                    if first.description:
                        lines.append(f"  {first.description}")
                elif first.change_type == ChangeType.REMOVED:
                    lines.append(f"### ❌ Removed: {item_id}")
                else:
                    lines.append(f"### 📝 Modified: {item_id}")
                    for change in item_changes:
                        if change.field:
                            lines.append(f"  - **{change.field}**: {change.old_value} → {change.new_value}")
                
                lines.append("")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def to_json(self) -> str:
        """Generate JSON changelog."""
        data = {
            "generated_at": self.generated_at,
            "compare_from": self.compare_from,
            "compare_to": self.compare_to,
            "summary": self.summary(),
            "changes": [
                {
                    "type": c.change_type.value,
                    "category": c.category,
                    "item_id": c.item_id,
                    "field": c.field,
                    "old_value": str(c.old_value) if c.old_value is not None else None,
                    "new_value": str(c.new_value) if c.new_value is not None else None,
                    "description": c.description
                }
                for c in self.changes
            ]
        }
        return json.dumps(data, indent=2)


@dataclass
class VersionSnapshot:
    """Represents a saved version snapshot."""
    name: str
    created_at: str
    description: str = ""
    path: Path = None


class ChangelogGenerator:
    """
    Generates changelogs by comparing current data to vanilla or saved versions.
    Supports downloading vanilla baseline from GitHub.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the changelog generator.
        
        Args:
            project_root: Path to hg-engine root. Auto-detected if None.
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.snapshots_dir = Path(__file__).parent.parent / 'snapshots'
        self.vanilla_dir = self.snapshots_dir / 'vanilla'
        self.asm_parser = ASMParser(project_root)
        self.json_handler = JSONHandler(project_root)
    
    def get_snapshots_dir(self) -> Path:
        """Get the snapshots directory, creating if needed."""
        if not self.snapshots_dir.exists():
            self.snapshots_dir.mkdir(parents=True)
        return self.snapshots_dir
    
    def get_vanilla_dir(self) -> Path:
        """Get the vanilla data directory, creating if needed."""
        if not self.vanilla_dir.exists():
            self.vanilla_dir.mkdir(parents=True)
        return self.vanilla_dir
    
    def has_vanilla_data(self) -> bool:
        """Check if vanilla data has been downloaded."""
        return (self.vanilla_dir / 'mondata.json').exists()
    
    def download_vanilla_from_github(self, progress_callback: Optional[Callable[[str, float], None]] = None) -> bool:
        """
        Download vanilla hg-engine data from GitHub.
        
        Args:
            progress_callback: Optional callback(message, progress) where progress is 0.0-1.0
        
        Returns:
            True if successful, False otherwise.
        """
        vanilla_dir = self.get_vanilla_dir()
        temp_dir = vanilla_dir / 'temp'
        
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(parents=True)
            
            total_files = len(VANILLA_FILES)
            
            for i, file_path in enumerate(VANILLA_FILES):
                url = f"{GITHUB_RAW_BASE}/{file_path}"
                local_path = temp_dir / Path(file_path).name
                
                if progress_callback:
                    progress_callback(f"Downloading {Path(file_path).name}...", i / total_files)
                
                try:
                    with urllib.request.urlopen(url, timeout=30) as response:
                        content = response.read()
                        with open(local_path, 'wb') as f:
                            f.write(content)
                except urllib.error.URLError as e:
                    print(f"Failed to download {file_path}: {e}")
                    return False
            
            if progress_callback:
                progress_callback("Parsing downloaded data...", 0.8)
            
            # Parse and save as JSON snapshots
            self._parse_and_save_vanilla(temp_dir, vanilla_dir)
            
            # Save metadata
            metadata = {
                "source": f"https://github.com/{GITHUB_REPO}",
                "branch": GITHUB_BRANCH,
                "downloaded_at": datetime.now().isoformat(),
                "files": VANILLA_FILES
            }
            with open(vanilla_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            if progress_callback:
                progress_callback("Vanilla data downloaded successfully!", 1.0)
            
            return True
            
        except Exception as e:
            print(f"Error downloading vanilla data: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False
    
    def _parse_and_save_vanilla(self, source_dir: Path, dest_dir: Path):
        """Parse downloaded files and save as JSON snapshots."""
        # For now, we'll store the raw files and parse them when needed
        # In a full implementation, we'd parse the .s files
        
        # Copy learnsets.json directly if it exists
        learnsets_src = source_dir / 'learnsets.json'
        if learnsets_src.exists():
            shutil.copy(learnsets_src, dest_dir / 'learnsets.json')
        
        # Store raw .s files for future parsing
        raw_dir = dest_dir / 'raw'
        raw_dir.mkdir(exist_ok=True)
        
        for src_file in source_dir.iterdir():
            if src_file.suffix == '.s':
                shutil.copy(src_file, raw_dir / src_file.name)
        
        # Create placeholder JSON files
        # In a real implementation, we'd parse the .s files
        placeholders = ['mondata.json', 'movedata.json', 'trainerdata.json']
        for placeholder in placeholders:
            filepath = dest_dir / placeholder
            if not filepath.exists():
                with open(filepath, 'w') as f:
                    json.dump({"_note": "Parse from raw/*.s files", "_files": list(raw_dir.glob('*.s'))}, f, indent=2, default=str)
    
    def list_versions(self) -> List[VersionSnapshot]:
        """List all saved version snapshots."""
        versions = []
        
        # Add vanilla if exists
        if self.has_vanilla_data():
            metadata_path = self.vanilla_dir / 'metadata.json'
            created_at = ""
            if metadata_path.exists():
                with open(metadata_path) as f:
                    meta = json.load(f)
                    created_at = meta.get('downloaded_at', '')
            
            versions.append(VersionSnapshot(
                name="vanilla",
                created_at=created_at,
                description="Vanilla hg-engine from GitHub",
                path=self.vanilla_dir
            ))
        
        # Ensure snapshots dir exists
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Add other snapshots
        for item in self.snapshots_dir.iterdir():
            if item.is_dir() and item.name != 'vanilla':
                metadata_path = item / 'metadata.json'
                if metadata_path.exists():
                    with open(metadata_path) as f:
                        meta = json.load(f)
                    versions.append(VersionSnapshot(
                        name=meta.get('name', item.name),
                        created_at=meta.get('created_at', ''),
                        description=meta.get('description', ''),
                        path=item
                    ))
        
        return sorted(versions, key=lambda v: v.created_at, reverse=True)
    
    def create_version_snapshot(self, name: str, description: str = "") -> VersionSnapshot:
        """
        Create a new version snapshot of current data.
        
        Args:
            name: Name for the version (e.g., "v1.0", "pre-fairy-patch")
            description: Optional description
        
        Returns:
            The created VersionSnapshot
        """
        # Sanitize name for filesystem
        safe_name = "".join(c for c in name if c.isalnum() or c in '-_').strip()
        if not safe_name:
            safe_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        snapshot_dir = self.snapshots_dir / safe_name
        if snapshot_dir.exists():
            raise ValueError(f"Version '{name}' already exists")
        
        snapshot_dir.mkdir(parents=True)
        
        created_at = datetime.now().isoformat()
        
        # Save current data
        try:
            mondata = self.asm_parser.parse_mondata()
            self._save_snapshot(mondata, snapshot_dir / 'mondata.json')
        except Exception as e:
            print(f"Warning: Could not save mondata: {e}")
        
        try:
            movedata = self.asm_parser.parse_movedata()
            self._save_snapshot(movedata, snapshot_dir / 'movedata.json')
        except Exception as e:
            print(f"Warning: Could not save movedata: {e}")
        
        try:
            trainerdata = self.asm_parser.parse_trainerdata()
            self._save_snapshot(trainerdata, snapshot_dir / 'trainerdata.json')
        except Exception as e:
            print(f"Warning: Could not save trainerdata: {e}")
        
        # Copy learnsets
        learnsets_path = self.project_root / 'data' / 'learnsets' / 'learnsets.json'
        if learnsets_path.exists():
            shutil.copy(learnsets_path, snapshot_dir / 'learnsets.json')
        
        # Save metadata
        metadata = {
            "name": name,
            "created_at": created_at,
            "description": description,
        }
        with open(snapshot_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return VersionSnapshot(
            name=name,
            created_at=created_at,
            description=description,
            path=snapshot_dir
        )
    
    def delete_version(self, name: str) -> bool:
        """Delete a version snapshot."""
        if name == "vanilla":
            return False  # Don't allow deleting vanilla
        
        for version in self.list_versions():
            if version.name == name and version.path:
                shutil.rmtree(version.path)
                return True
        return False
    
    def _save_snapshot(self, data: Dict, filepath: Path):
        """Save a data dictionary as JSON snapshot."""
        serializable = {}
        for key, entry in data.items():
            if hasattr(entry, '__dict__'):
                serializable[key] = {
                    k: v for k, v in entry.__dict__.items() 
                    if not k.startswith('_') and k != 'raw_lines'
                }
            else:
                serializable[key] = entry
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, default=str)
    
    def _load_snapshot(self, filepath: Path) -> Dict:
        """Load a JSON snapshot."""
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_changelog(self, from_version: str = "vanilla", to_version: str = "current") -> Changelog:
        """
        Generate a changelog comparing two versions.
        
        Args:
            from_version: Version name to compare from (default: "vanilla")
            to_version: Version name to compare to (default: "current")
        
        Returns:
            Changelog object with all changes
        """
        changelog = Changelog(
            generated_at=datetime.now().isoformat(),
            compare_from=from_version,
            compare_to=to_version
        )
        
        # Get from_version directory
        from_dir = self._get_version_dir(from_version)
        if from_dir is None:
            print(f"Warning: Version '{from_version}' not found")
            return changelog
        
        # Compare Pokemon data
        self._compare_pokemon(changelog, from_dir, to_version)
        
        # Compare move data
        self._compare_moves(changelog, from_dir, to_version)
        
        # Compare trainer data
        self._compare_trainers(changelog, from_dir, to_version)
        
        # Compare learnsets
        self._compare_learnsets(changelog, from_dir, to_version)
        
        return changelog
    
    def _get_version_dir(self, version_name: str) -> Optional[Path]:
        """Get directory for a version name."""
        if version_name == "vanilla":
            return self.vanilla_dir if self.has_vanilla_data() else None
        elif version_name == "current":
            return None  # Will use live data
        else:
            for v in self.list_versions():
                if v.name == version_name:
                    return v.path
        return None
    
    def _get_version_data(self, version_dir: Optional[Path], data_type: str) -> Dict:
        """Get data from a version (directory or current)."""
        if version_dir is None:
            # Load current data
            if data_type == 'mondata':
                return {k: v.__dict__ for k, v in self.asm_parser.parse_mondata().items()}
            elif data_type == 'movedata':
                return {k: v.__dict__ for k, v in self.asm_parser.parse_movedata().items()}
            elif data_type == 'trainerdata':
                return {k: v.__dict__ for k, v in self.asm_parser.parse_trainerdata().items()}
            elif data_type == 'learnsets':
                return self.json_handler.load_learnsets_raw()
        else:
            # Load from snapshot
            filepath = version_dir / f'{data_type}.json'
            return self._load_snapshot(filepath)
    
    def _compare_pokemon(self, changelog: Changelog, from_dir: Path, to_version: str):
        """Compare Pokemon data changes."""
        from_data = self._load_snapshot(from_dir / 'mondata.json')
        to_dir = self._get_version_dir(to_version) if to_version != "current" else None
        to_data = self._get_version_data(to_dir, 'mondata')
        
        if not from_data:
            return
        
        # Check for added/modified Pokemon
        for species, entry in to_data.items():
            if isinstance(entry, dict):
                entry_dict = entry
            else:
                entry_dict = entry.__dict__ if hasattr(entry, '__dict__') else {}
            
            if species not in from_data:
                changelog.add(Change(
                    change_type=ChangeType.ADDED,
                    category='pokemon',
                    item_id=species,
                    field='',
                    description=f"New Pokemon: {entry_dict.get('display_name', species)}"
                ))
            else:
                from_entry = from_data[species]
                
                # Compare base stats
                if entry_dict.get('basestats') != from_entry.get('basestats'):
                    changelog.add(Change(
                        change_type=ChangeType.MODIFIED,
                        category='pokemon',
                        item_id=species,
                        field='basestats',
                        old_value=from_entry.get('basestats'),
                        new_value=entry_dict.get('basestats')
                    ))
                
                # Compare types
                if entry_dict.get('types') != from_entry.get('types'):
                    changelog.add(Change(
                        change_type=ChangeType.MODIFIED,
                        category='pokemon',
                        item_id=species,
                        field='types',
                        old_value=from_entry.get('types'),
                        new_value=entry_dict.get('types')
                    ))
                
                # Compare abilities
                if entry_dict.get('abilities') != from_entry.get('abilities'):
                    changelog.add(Change(
                        change_type=ChangeType.MODIFIED,
                        category='pokemon',
                        item_id=species,
                        field='abilities',
                        old_value=from_entry.get('abilities'),
                        new_value=entry_dict.get('abilities')
                    ))
        
        # Check for removed Pokemon
        for species in from_data:
            if species not in to_data:
                changelog.add(Change(
                    change_type=ChangeType.REMOVED,
                    category='pokemon',
                    item_id=species,
                    field=''
                ))
    
    def _compare_moves(self, changelog: Changelog, from_dir: Path, to_version: str):
        """Compare move data changes."""
        from_data = self._load_snapshot(from_dir / 'movedata.json')
        to_dir = self._get_version_dir(to_version) if to_version != "current" else None
        to_data = self._get_version_data(to_dir, 'movedata')
        
        if not from_data:
            return
        
        for move_id, entry in to_data.items():
            if isinstance(entry, dict):
                entry_dict = entry
            else:
                entry_dict = entry.__dict__ if hasattr(entry, '__dict__') else {}
            
            if move_id not in from_data:
                changelog.add(Change(
                    change_type=ChangeType.ADDED,
                    category='move',
                    item_id=move_id,
                    field='',
                    description=f"New Move: {entry_dict.get('display_name', move_id)}"
                ))
            else:
                from_entry = from_data[move_id]
                
                fields_to_check = ['basepower', 'accuracy', 'pp', 'type', 'priority', 'effectchance']
                
                for field in fields_to_check:
                    if entry_dict.get(field) != from_entry.get(field):
                        changelog.add(Change(
                            change_type=ChangeType.MODIFIED,
                            category='move',
                            item_id=move_id,
                            field=field,
                            old_value=from_entry.get(field),
                            new_value=entry_dict.get(field)
                        ))
        
        for move_id in from_data:
            if move_id not in to_data:
                changelog.add(Change(
                    change_type=ChangeType.REMOVED,
                    category='move',
                    item_id=move_id,
                    field=''
                ))
    
    def _compare_trainers(self, changelog: Changelog, from_dir: Path, to_version: str):
        """Compare trainer data changes."""
        from_data = self._load_snapshot(from_dir / 'trainerdata.json')
        to_dir = self._get_version_dir(to_version) if to_version != "current" else None
        to_data = self._get_version_data(to_dir, 'trainerdata')
        
        if not from_data:
            return
        
        for trainer_id, entry in to_data.items():
            if isinstance(entry, dict):
                entry_dict = entry
            else:
                entry_dict = entry.__dict__ if hasattr(entry, '__dict__') else {}
            
            if trainer_id not in from_data:
                changelog.add(Change(
                    change_type=ChangeType.ADDED,
                    category='trainer',
                    item_id=trainer_id,
                    field='',
                    description=f"New Trainer: {entry_dict.get('name', trainer_id)}"
                ))
            else:
                from_entry = from_data[trainer_id]
                
                # Compare Pokemon team
                if entry_dict.get('party') != from_entry.get('party'):
                    changelog.add(Change(
                        change_type=ChangeType.MODIFIED,
                        category='trainer',
                        item_id=trainer_id,
                        field='party',
                        old_value=f"{len(from_entry.get('party', []))} Pokemon",
                        new_value=f"{len(entry_dict.get('party', []))} Pokemon"
                    ))
        
        for trainer_id in from_data:
            if trainer_id not in to_data:
                changelog.add(Change(
                    change_type=ChangeType.REMOVED,
                    category='trainer',
                    item_id=trainer_id,
                    field=''
                ))
    
    def _compare_learnsets(self, changelog: Changelog, from_dir: Path, to_version: str):
        """Compare learnset changes."""
        from_path = from_dir / 'learnsets.json'
        if not from_path.exists():
            return
        
        with open(from_path, 'r') as f:
            from_data = json.load(f)
        
        if to_version == "current":
            current_path = self.project_root / 'data' / 'learnsets' / 'learnsets.json'
            if not current_path.exists():
                return
            with open(current_path, 'r') as f:
                to_data = json.load(f)
        else:
            to_dir = self._get_version_dir(to_version)
            if to_dir is None:
                return
            to_path = to_dir / 'learnsets.json'
            if not to_path.exists():
                return
            with open(to_path, 'r') as f:
                to_data = json.load(f)
        
        for species, learnset in to_data.items():
            if species not in from_data:
                changelog.add(Change(
                    change_type=ChangeType.ADDED,
                    category='learnset',
                    item_id=species,
                    field='',
                    description=f"New learnset for {species}"
                ))
            else:
                from_learnset = from_data[species]
                
                # Compare level moves count
                from_level = len(from_learnset.get('LevelMoves', []))
                to_level = len(learnset.get('LevelMoves', []))
                if from_level != to_level:
                    changelog.add(Change(
                        change_type=ChangeType.MODIFIED,
                        category='learnset',
                        item_id=species,
                        field='LevelMoves',
                        old_value=f"{from_level} moves",
                        new_value=f"{to_level} moves"
                    ))
                
                # Compare TM/HM moves count
                from_tm = len(from_learnset.get('MachineMoves', []))
                to_tm = len(learnset.get('MachineMoves', []))
                if from_tm != to_tm:
                    changelog.add(Change(
                        change_type=ChangeType.MODIFIED,
                        category='learnset',
                        item_id=species,
                        field='MachineMoves',
                        old_value=f"{from_tm} TMs",
                        new_value=f"{to_tm} TMs"
                    ))
        
        for species in from_data:
            if species not in to_data:
                changelog.add(Change(
                    change_type=ChangeType.REMOVED,
                    category='learnset',
                    item_id=species,
                    field=''
                ))
