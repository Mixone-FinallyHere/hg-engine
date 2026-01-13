"""
Constants Loader
================
Parses C header files and ASM include files to extract constant definitions.
This allows editors to use symbolic names instead of raw numbers.
"""

import re
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class ConstantsLoader:
    """Load and manage constants from header and include files."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the constants loader.
        
        Args:
            project_root: Path to hg-engine root. Auto-detected if None.
        """
        if project_root is None:
            # Auto-detect: go up from scripts/editors/common to project root
            self.project_root = Path(__file__).parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self._cache: Dict[str, Dict[str, int]] = {}
        self._reverse_cache: Dict[str, Dict[int, str]] = {}
    
    def _parse_c_header(self, filepath: Path) -> Dict[str, int]:
        """
        Parse a C header file for #define constants.
        
        Handles:
            #define SPECIES_BULBASAUR 1
            #define SPECIES_IVYSAUR (SPECIES_BULBASAUR + 1)
            #define MAX_SPECIES (SPECIES_LAST)
        """
        constants = {}
        
        if not filepath.exists():
            return constants
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Pattern for #define NAME value
        define_pattern = re.compile(
            r'#define\s+(\w+)\s+(.+?)(?:\s*//.*)?$',
            re.MULTILINE
        )
        
        for match in define_pattern.finditer(content):
            name = match.group(1)
            value_str = match.group(2).strip()
            
            # Skip function-like macros
            if '(' in name:
                continue
            
            value = self._evaluate_expression(value_str, constants)
            if value is not None:
                constants[name] = value
        
        return constants
    
    def _parse_asm_include(self, filepath: Path) -> Dict[str, int]:
        """
        Parse an ASM include file for .equ and equ constants.
        
        Handles:
            .equ SPECIES_BULBASAUR, 1
            SPECIES_IVYSAUR equ 2
            .equ SPECIES_VENUSAUR, (SPECIES_IVYSAUR + 1)
        """
        constants = {}
        
        if not filepath.exists():
            return constants
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Pattern for .equ NAME, value
        equ_pattern1 = re.compile(
            r'\.equ\s+(\w+)\s*,\s*(.+?)(?:\s*//.*)?$',
            re.MULTILINE
        )
        
        # Pattern for NAME equ value
        equ_pattern2 = re.compile(
            r'^(\w+)\s+equ\s+(.+?)(?:\s*//.*)?$',
            re.MULTILINE
        )
        
        for pattern in [equ_pattern1, equ_pattern2]:
            for match in pattern.finditer(content):
                name = match.group(1)
                value_str = match.group(2).strip()
                
                value = self._evaluate_expression(value_str, constants)
                if value is not None:
                    constants[name] = value
        
        return constants
    
    def _evaluate_expression(self, expr: str, known: Dict[str, int]) -> Optional[int]:
        """
        Evaluate a constant expression.
        
        Handles:
            - Plain integers: 42, 0x2A
            - Simple references: SPECIES_BULBASAUR
            - Arithmetic: (SPECIES_X + 1), (SPECIES_Y - 10)
            - Parenthesized expressions
        """
        expr = expr.strip()
        
        # Remove trailing commas (common in ASM)
        expr = expr.rstrip(',')
        
        # Try plain integer
        try:
            if expr.startswith('0x') or expr.startswith('0X'):
                return int(expr, 16)
            elif expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                return int(expr)
        except ValueError:
            pass
        
        # Try simple reference
        if expr in known:
            return known[expr]
        
        # Try to evaluate expression with known constants
        try:
            # Replace known constants in expression
            eval_expr = expr
            
            # Remove outer parentheses for cleaner parsing
            while eval_expr.startswith('(') and eval_expr.endswith(')'):
                eval_expr = eval_expr[1:-1].strip()
            
            # Replace constant names with their values
            for name, value in sorted(known.items(), key=lambda x: -len(x[0])):
                eval_expr = re.sub(r'\b' + re.escape(name) + r'\b', str(value), eval_expr)
            
            # Only evaluate if it looks safe (numbers, operators, parentheses)
            if re.match(r'^[\d\s+\-*/()]+$', eval_expr):
                return int(eval(eval_expr))
        except:
            pass
        
        return None
    
    def load_species(self) -> Dict[str, int]:
        """Load species constants from both C header and ASM include."""
        if 'species' in self._cache:
            return self._cache['species']
        
        constants = {}
        
        # Load from C header
        c_path = self.project_root / 'include' / 'constants' / 'species.h'
        constants.update(self._parse_c_header(c_path))
        
        # Load from ASM include (may have additional defines)
        asm_path = self.project_root / 'asm' / 'include' / 'species.inc'
        constants.update(self._parse_asm_include(asm_path))
        
        self._cache['species'] = constants
        self._reverse_cache['species'] = {v: k for k, v in constants.items()}
        
        return constants
    
    def load_moves(self) -> Dict[str, int]:
        """Load move constants."""
        if 'moves' in self._cache:
            return self._cache['moves']
        
        constants = {}
        
        c_path = self.project_root / 'include' / 'constants' / 'moves.h'
        constants.update(self._parse_c_header(c_path))
        
        asm_path = self.project_root / 'asm' / 'include' / 'moves.inc'
        constants.update(self._parse_asm_include(asm_path))
        
        self._cache['moves'] = constants
        self._reverse_cache['moves'] = {v: k for k, v in constants.items()}
        
        return constants
    
    def load_abilities(self) -> Dict[str, int]:
        """Load ability constants."""
        if 'abilities' in self._cache:
            return self._cache['abilities']
        
        constants = {}
        
        c_path = self.project_root / 'include' / 'constants' / 'ability.h'
        constants.update(self._parse_c_header(c_path))
        
        asm_path = self.project_root / 'asm' / 'include' / 'abilities.inc'
        constants.update(self._parse_asm_include(asm_path))
        
        self._cache['abilities'] = constants
        self._reverse_cache['abilities'] = {v: k for k, v in constants.items()}
        
        return constants
    
    def load_items(self) -> Dict[str, int]:
        """Load item constants."""
        if 'items' in self._cache:
            return self._cache['items']
        
        constants = {}
        
        c_path = self.project_root / 'include' / 'constants' / 'item.h'
        constants.update(self._parse_c_header(c_path))
        
        asm_path = self.project_root / 'asm' / 'include' / 'items.inc'
        constants.update(self._parse_asm_include(asm_path))
        
        self._cache['items'] = constants
        self._reverse_cache['items'] = {v: k for k, v in constants.items()}
        
        return constants
    
    def load_types(self) -> Dict[str, int]:
        """Load type constants from battle.h."""
        if 'types' in self._cache:
            return self._cache['types']
        
        constants = {}
        
        # Types are defined in battle.h
        c_path = self.project_root / 'include' / 'battle.h'
        all_constants = self._parse_c_header(c_path)
        
        # Filter to only TYPE_* constants
        constants = {k: v for k, v in all_constants.items() if k.startswith('TYPE_')}
        
        self._cache['types'] = constants
        self._reverse_cache['types'] = {v: k for k, v in constants.items()}
        
        return constants
    
    def get_name(self, category: str, value: int) -> Optional[str]:
        """Get the constant name for a numeric value."""
        if category not in self._reverse_cache:
            # Try to load the category
            loader = getattr(self, f'load_{category}', None)
            if loader:
                loader()
        
        return self._reverse_cache.get(category, {}).get(value)
    
    def get_value(self, category: str, name: str) -> Optional[int]:
        """Get the numeric value for a constant name."""
        if category not in self._cache:
            loader = getattr(self, f'load_{category}', None)
            if loader:
                loader()
        
        return self._cache.get(category, {}).get(name)
    
    def get_sorted_list(self, category: str) -> List[Tuple[str, int]]:
        """Get a sorted list of (name, value) pairs for a category."""
        if category not in self._cache:
            loader = getattr(self, f'load_{category}', None)
            if loader:
                loader()
        
        constants = self._cache.get(category, {})
        return sorted(constants.items(), key=lambda x: x[1])


# Singleton instance for convenience
_default_loader: Optional[ConstantsLoader] = None

def get_constants_loader() -> ConstantsLoader:
    """Get or create the default constants loader."""
    global _default_loader
    if _default_loader is None:
        _default_loader = ConstantsLoader()
    return _default_loader
