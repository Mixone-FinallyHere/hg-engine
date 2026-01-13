# hg-engine Data Editors

A collection of tkinter-based GUI tools for editing Pokemon HeartGold ROM data.

## Requirements

- Python 3.7+
- tkinter (usually included with Python)

## Quick Start

```bash
# From the hg-engine root directory:
cd scripts/editors

# Launch the main menu
python main.py

# Or launch specific editors directly:
python main.py pokemon    # Pokemon Data Editor
python main.py moveset    # Moveset/Learnset Editor
python main.py trainer    # Trainer Editor
python main.py changelog  # Generate changelog (CLI)
```

## Editors

### Pokemon Data Editor
Edit Pokemon base stats, types, abilities, and other properties from `armips/data/mondata.s`.

Features:
- View and edit all Pokemon data
- Filter by type
- Search by name
- Find Pokemon by ability

### Moveset Editor
Edit Pokemon learnsets from `data/learnsets/learnsets.json`.

Features:
- Edit level-up moves
- Edit TM/HM compatibility
- Edit egg moves
- Edit tutor moves
- Find Pokemon that learn a specific move

### Trainer Editor
Edit trainer data from `armips/data/trainers/trainers.s`.

Features:
- Edit trainer teams
- Configure AI flags
- Set held items
- Filter by trainer class
- Find trainers using specific Pokemon

## Changelog Generator

Compare your current data to vanilla HeartGold and generate a detailed changelog.

### Setting up Vanilla Baseline

Before making modifications, save a vanilla snapshot:

```bash
python main.py save-vanilla
```

Or use the GUI:
1. Launch the main menu
2. Click "Generate Changelog"
3. When prompted, choose to save current data as vanilla

### Generating Changelogs

After making modifications:

```bash
# CLI output
python main.py changelog

# Or use the GUI for a formatted view
python main.py
# Then click "Generate Changelog"
```

## Project Structure

```
scripts/editors/
├── main.py                 # Main launcher
├── README.md               # This file
├── common/                 # Shared utilities
│   ├── __init__.py
│   ├── asm_parser.py       # Parse armips .s files
│   ├── base_editor.py      # Base tkinter editor class
│   ├── changelog.py        # Changelog generation
│   ├── constants.py        # Load constants from headers
│   └── json_handler.py     # JSON file handling
├── pokemon_editor/         # Pokemon data editor
│   ├── __init__.py
│   └── editor.py
├── moveset_editor/         # Moveset editor
│   ├── __init__.py
│   └── editor.py
├── trainer_editor/         # Trainer editor
│   ├── __init__.py
│   └── editor.py
├── vanilla/                # Vanilla data snapshots
|
└── snapshots/                # Version data snapshots
```

## Notes

- Currently, saving ASM files (mondata.s, trainers.s) is not fully implemented due to the complexity of preserving the exact ASM format
- Learnset data (JSON) can be saved directly
- All editors support undo/redo (Ctrl+Z / Ctrl+Y)
- Use Ctrl+S to save, Ctrl+F to search

## Future Improvements

- [ ] Full ASM file writing support
- [ ] Move data editor
- [ ] Wild encounter editor
- [ ] Evolution data editor
- [ ] Import/export to JSON
- [ ] Batch editing tools
