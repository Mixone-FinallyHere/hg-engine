"""
Base Editor
===========
Base class for all tkinter-based data editors.
Provides common UI patterns, file handling, and undo/redo functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Any, List, Dict, Callable
from pathlib import Path
from abc import ABC, abstractmethod
import copy


class UndoStack:
    """Manages undo/redo history for editor state."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._undo_stack: List[Any] = []
        self._redo_stack: List[Any] = []
    
    def push(self, state: Any):
        """Push a new state onto the undo stack."""
        self._undo_stack.append(copy.deepcopy(state))
        self._redo_stack.clear()  # Clear redo stack on new action
        
        # Trim if too large
        if len(self._undo_stack) > self.max_size:
            self._undo_stack.pop(0)
    
    def undo(self, current_state: Any) -> Optional[Any]:
        """Undo: move current state to redo, return previous state."""
        if not self._undo_stack:
            return None
        
        self._redo_stack.append(copy.deepcopy(current_state))
        return self._undo_stack.pop()
    
    def redo(self, current_state: Any) -> Optional[Any]:
        """Redo: move current state to undo, return next state."""
        if not self._redo_stack:
            return None
        
        self._undo_stack.append(copy.deepcopy(current_state))
        return self._redo_stack.pop()
    
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0
    
    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()


class BaseEditor(ABC):
    """
    Base class for data editors.
    
    Provides:
    - Standard window layout with menu bar
    - Search/filter functionality
    - Undo/redo support
    - File save/load handling
    - Status bar
    """
    
    def __init__(self, master: Optional[tk.Tk] = None, title: str = "Data Editor"):
        """
        Initialize the base editor.
        
        Args:
            master: Parent tkinter window. Creates new Tk if None.
            title: Window title.
        """
        if master is None:
            self.root = tk.Tk()
            self._owns_root = True
        else:
            self.root = tk.Toplevel(master)
            self._owns_root = False
        
        self.root.title(title)
        self.root.geometry("1200x800")
        
        # State
        self._modified = False
        self._current_file: Optional[Path] = None
        self._undo_stack = UndoStack()
        
        # Setup UI
        self._setup_menu()
        self._setup_toolbar()
        self._setup_main_frame()
        self._setup_status_bar()
        
        # Bind shortcuts
        self.root.bind('<Control-s>', lambda e: self.save())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-Shift-z>', lambda e: self.redo())
        self.root.bind('<Control-f>', lambda e: self._focus_search())
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_menu(self):
        """Setup the menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As...", command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._on_close)
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find...", command=self._focus_search, accelerator="Ctrl+F")
        
        # Allow subclasses to add menus
        self._setup_custom_menus()
    
    def _setup_custom_menus(self):
        """Override in subclass to add custom menus."""
        pass
    
    def _setup_toolbar(self):
        """Setup the toolbar."""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Search box
        ttk.Label(self.toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._on_search())
        self.search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear search button
        ttk.Button(self.toolbar, text="Clear", command=self._clear_search).pack(side=tk.LEFT)
        
        # Allow subclasses to add toolbar items
        self._setup_custom_toolbar()
    
    def _setup_custom_toolbar(self):
        """Override in subclass to add custom toolbar items."""
        pass
    
    def _setup_main_frame(self):
        """Setup the main content frame."""
        # Main paned window for list/detail view
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - list view
        self.list_frame = ttk.Frame(self.paned)
        self.paned.add(self.list_frame, weight=1)
        
        # List with scrollbar
        list_scroll = ttk.Scrollbar(self.list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.item_list = tk.Listbox(
            self.list_frame,
            yscrollcommand=list_scroll.set,
            selectmode=tk.SINGLE,
            font=('Consolas', 10)
        )
        self.item_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.item_list.yview)
        
        self.item_list.bind('<<ListboxSelect>>', self._on_item_select)
        
        # Right panel - detail view
        self.detail_frame = ttk.Frame(self.paned)
        self.paned.add(self.detail_frame, weight=3)
        
        # Detail content with scrollbar
        detail_canvas = tk.Canvas(self.detail_frame)
        detail_scroll = ttk.Scrollbar(self.detail_frame, orient=tk.VERTICAL, command=detail_canvas.yview)
        self.detail_content = ttk.Frame(detail_canvas)
        
        detail_canvas.configure(yscrollcommand=detail_scroll.set)
        
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        detail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.detail_window = detail_canvas.create_window((0, 0), window=self.detail_content, anchor=tk.NW)
        
        def configure_scroll(event):
            detail_canvas.configure(scrollregion=detail_canvas.bbox("all"))
            detail_canvas.itemconfig(self.detail_window, width=event.width)
        
        self.detail_content.bind('<Configure>', lambda e: detail_canvas.configure(scrollregion=detail_canvas.bbox("all")))
        detail_canvas.bind('<Configure>', configure_scroll)
        
        # Allow subclasses to customize
        self._setup_detail_view()
    
    @abstractmethod
    def _setup_detail_view(self):
        """Override to setup the detail view content."""
        pass
    
    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.modified_label = ttk.Label(self.status_frame, text="")
        self.modified_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def set_status(self, message: str):
        """Update the status bar message."""
        self.status_label.config(text=message)
    
    def set_modified(self, modified: bool = True):
        """Set the modified state."""
        self._modified = modified
        if modified:
            self.modified_label.config(text="Modified")
            if not self.root.title().endswith("*"):
                self.root.title(self.root.title() + "*")
        else:
            self.modified_label.config(text="")
            self.root.title(self.root.title().rstrip("*"))
    
    def _focus_search(self):
        """Focus the search entry."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
    
    def _clear_search(self):
        """Clear the search box."""
        self.search_var.set("")
        self.search_entry.focus_set()
    
    def _on_search(self):
        """Handle search input change. Override for custom behavior."""
        pass
    
    def _on_item_select(self, event):
        """Handle item selection in the list. Override for custom behavior."""
        pass
    
    def _on_close(self):
        """Handle window close."""
        if self._modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?"
            )
            if result is None:  # Cancel
                return
            if result:  # Yes
                if not self.save():
                    return
        
        self.root.destroy()
    
    def open_file(self):
        """Open a file dialog to load data."""
        pass
    
    def save(self) -> bool:
        """Save the current data. Returns True if successful."""
        if self._current_file:
            return self._do_save(self._current_file)
        return self.save_as()
    
    def save_as(self) -> bool:
        """Save with a new filename."""
        return False
    
    def _do_save(self, filepath: Path) -> bool:
        """Actually save to the file. Override in subclass."""
        return False
    
    def undo(self):
        """Undo the last action."""
        pass
    
    def redo(self):
        """Redo the last undone action."""
        pass
    
    def run(self):
        """Start the editor main loop."""
        if self._owns_root:
            self.root.mainloop()


class LabeledEntry(ttk.Frame):
    """A labeled entry widget."""
    
    def __init__(self, parent, label: str, width: int = 20, **kwargs):
        super().__init__(parent)
        
        self.label = ttk.Label(self, text=label, width=15, anchor=tk.W)
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, width=width, **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def get(self) -> str:
        return self.var.get()
    
    def set(self, value: str):
        self.var.set(value)
    
    def bind_change(self, callback: Callable):
        self.var.trace('w', lambda *args: callback())


class LabeledCombobox(ttk.Frame):
    """A labeled combobox widget."""
    
    def __init__(self, parent, label: str, values: List[str], width: int = 20, **kwargs):
        super().__init__(parent)
        
        self.label = ttk.Label(self, text=label, width=15, anchor=tk.W)
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.var = tk.StringVar()
        self.combo = ttk.Combobox(self, textvariable=self.var, values=values, width=width, **kwargs)
        self.combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def get(self) -> str:
        return self.var.get()
    
    def set(self, value: str):
        self.var.set(value)
    
    def set_values(self, values: List[str]):
        self.combo['values'] = values
    
    def bind_change(self, callback: Callable):
        self.var.trace('w', lambda *args: callback())


class LabeledSpinbox(ttk.Frame):
    """A labeled spinbox widget for numeric values."""
    
    def __init__(self, parent, label: str, from_: int = 0, to: int = 255, width: int = 10, **kwargs):
        super().__init__(parent)
        
        self.label = ttk.Label(self, text=label, width=15, anchor=tk.W)
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.var = tk.IntVar()
        self.spinbox = ttk.Spinbox(
            self, textvariable=self.var, from_=from_, to=to, width=width, **kwargs
        )
        self.spinbox.pack(side=tk.LEFT)
    
    def get(self) -> int:
        try:
            return self.var.get()
        except tk.TclError:
            return 0
    
    def set(self, value: int):
        self.var.set(value)
    
    def bind_change(self, callback: Callable):
        self.var.trace('w', lambda *args: callback())
