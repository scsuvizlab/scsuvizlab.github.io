"""
Book editor panel for the Interactive Book Editor.
REVISED: Made Chapter ID editable in the ChaptersTab.
Ensures chapter_id is assigned before use in on_add_chapter.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QListWidget, QPushButton, QTabWidget, QGroupBox, QMessageBox,
    QListWidgetItem, QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt
import re # Import regex for ID validation
import traceback # For debugging

from editor_panel import EditorPanel

# --- BasicBookPropertiesTab remains unchanged ---
class BasicBookPropertiesTab(QWidget):
    property_changed = pyqtSignal(str, object) 
    def __init__(self, parent=None):
        super().__init__(parent); layout = QFormLayout(); layout.setContentsMargins(10, 10, 10, 10)
        self.book_id_label = QLabel(); layout.addRow("ID:", self.book_id_label)
        self.book_title_edit = QLineEdit(); self.book_title_edit.textChanged.connect(lambda text: self.property_changed.emit("title", text)); layout.addRow("Title:", self.book_title_edit)
        self.book_author_edit = QLineEdit(); self.book_author_edit.textChanged.connect(lambda text: self.property_changed.emit("metadata.author", text)); layout.addRow("Author:", self.book_author_edit)
        self.book_version_edit = QLineEdit(); self.book_version_edit.textChanged.connect(lambda text: self.property_changed.emit("metadata.version", text)); layout.addRow("Version:", self.book_version_edit)
        self.default_start_node_combo = QComboBox(); self.default_start_node_combo.setEditable(True); self.default_start_node_combo.currentTextChanged.connect(lambda text: self.property_changed.emit("metadata.defaultStartNode", text)); layout.addRow("Default Start Node:", self.default_start_node_combo)
        self.default_pov_edit = QLineEdit(); self.default_pov_edit.textChanged.connect(lambda text: self.property_changed.emit("metadata.defaultPOV", text)); layout.addRow("Default POV:", self.default_pov_edit)
        self.setLayout(layout) 
    def update_for_node(self, node):
        self.book_id_label.setText(node.id); self.book_title_edit.setText(node.title)
        self.book_author_edit.setText(node.metadata.get("author", "")); self.book_version_edit.setText(node.metadata.get("version", "1.0")); self.default_pov_edit.setText(node.metadata.get("defaultPOV", "Omniscient"))
        current_default = node.metadata.get("defaultStartNode", ""); index = self.default_start_node_combo.findText(current_default)
        if index >= 0: self.default_start_node_combo.setCurrentIndex(index)
        else: self.default_start_node_combo.setEditText(current_default)
    def set_available_nodes(self, nodes):
        current_text = self.default_start_node_combo.currentText(); self.default_start_node_combo.clear(); self.default_start_node_combo.addItem("")
        for node in nodes:
            if node.node_type != "book": self.default_start_node_combo.addItem(node.id)
        if current_text: index = self.default_start_node_combo.findText(current_text); self.default_start_node_combo.setCurrentIndex(index) if index >= 0 else self.default_start_node_combo.setEditText(current_text)


class ChaptersTab(QWidget):
    """Tab for managing book chapters."""
    chapters_changed = pyqtSignal(list) 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.book_graph = None
        self.main_layout = QHBoxLayout() 
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.list_layout = QVBoxLayout(); self.main_layout.addLayout(self.list_layout, 2) 
        self.chapter_list = QListWidget(); self.chapter_list.currentItemChanged.connect(self.on_chapter_selected); self.list_layout.addWidget(self.chapter_list)
        self.list_buttons_layout = QHBoxLayout(); self.list_layout.addLayout(self.list_buttons_layout)
        self.add_button = QPushButton("Add"); self.add_button.clicked.connect(self.on_add_chapter); self.list_buttons_layout.addWidget(self.add_button)
        self.remove_button = QPushButton("Remove"); self.remove_button.clicked.connect(self.on_remove_chapter); self.list_buttons_layout.addWidget(self.remove_button)
        self.details_layout = QVBoxLayout(); self.main_layout.addLayout(self.details_layout, 3) 
        self.details_group = QGroupBox("Chapter Details"); self.details_form = QFormLayout(); self.details_group.setLayout(self.details_form); self.details_layout.addWidget(self.details_group) 
        self.chapter_id_edit = QLineEdit() 
        self.chapter_id_edit.editingFinished.connect(self.on_chapter_id_changed) 
        self.details_form.addRow("ID:", self.chapter_id_edit)
        self.chapter_title_edit = QLineEdit(); self.chapter_title_edit.textChanged.connect(self.on_chapter_title_changed); self.details_form.addRow("Title:", self.chapter_title_edit)
        self.start_node_combo = QComboBox(); self.start_node_combo.setEditable(True); self.start_node_combo.currentTextChanged.connect(self.on_start_node_changed); self.details_form.addRow("Start Node:", self.start_node_combo)
        self.chapter_description_edit = QTextEdit(); self.chapter_description_edit.textChanged.connect(self.on_chapter_description_changed); self.details_form.addRow("Description:", self.chapter_description_edit)
        self.order_buttons_layout = QVBoxLayout(); self.main_layout.addLayout(self.order_buttons_layout)
        self.move_up_button = QPushButton("↑"); self.move_up_button.clicked.connect(self.on_move_chapter_up); self.order_buttons_layout.addWidget(self.move_up_button)
        self.move_down_button = QPushButton("↓"); self.move_down_button.clicked.connect(self.on_move_chapter_down); self.order_buttons_layout.addWidget(self.move_down_button)
        self.order_buttons_layout.addStretch(1)
        self.setLayout(self.main_layout) 
        self.current_chapter_id = None; self.chapter_list_updating = False; self.disable_chapter_details()

    def set_book_graph(self, book_graph):
        """Set the book graph instance for this tab."""
        self.book_graph = book_graph
        
    def update_chapter_list(self):
        """Rebuilds the chapter list widget and attempts to re-select the previously selected item."""
        if not self.book_graph: return
        print("ChaptersTab: Updating chapter list...") # Debug
        self.chapter_list_updating = True 
        stored_current_id = self.current_chapter_id 
        self.chapter_list.clear()
        item_to_select = None
        try:
            # Use items() for dictionary iteration in Python 3
            for chapter_id, chapter_info in self.book_graph.chapter_info.items(): 
                item = QListWidgetItem(chapter_info.get("title", chapter_id))
                item.setData(Qt.UserRole, chapter_id)
                self.chapter_list.addItem(item)
                if chapter_id == stored_current_id:
                    item_to_select = item
            
            if item_to_select:
                self.chapter_list.setCurrentItem(item_to_select)
            elif self.chapter_list.count() > 0: 
                self.chapter_list.setCurrentRow(0)
            else:
                 self.disable_chapter_details()
                 
        except Exception as e:
             print(f"ERROR in ChaptersTab.update_chapter_list loop: {e}")
             traceback.print_exc()
             
        self.chapter_list_updating = False
        current_item = self.chapter_list.currentItem()
        if current_item:
             # Avoid potential infinite loop by checking flag again
             if not self.chapter_list_updating:
                  self.on_chapter_selected(current_item, None) 
        elif self.chapter_list.count() == 0: # Ensure details disabled if list is empty
             self.disable_chapter_details()
        print("ChaptersTab: Chapter list update finished.") # Debug


    def on_chapter_selected(self, current, previous):
        """Update details panel when a chapter is selected in the list."""
        if not current or self.chapter_list_updating: 
             # Only disable if not updating, otherwise might interfere with list rebuild selection
             if not self.chapter_list_updating: self.disable_chapter_details()
             return
        
        chapter_id = current.data(Qt.UserRole)
        print(f"ChaptersTab: Chapter selected: {chapter_id}") # Debug
        self.current_chapter_id = chapter_id 
        
        if self.book_graph and chapter_id in self.book_graph.chapter_info:
            chapter_info = self.book_graph.chapter_info[chapter_id]
            self.chapter_id_edit.blockSignals(True); self.chapter_title_edit.blockSignals(True); self.start_node_combo.blockSignals(True); self.chapter_description_edit.blockSignals(True)
            self.chapter_id_edit.setText(chapter_id) 
            self.chapter_title_edit.setText(chapter_info.get("title", "")); self.chapter_description_edit.setText(chapter_info.get("description", ""))
            start_node = chapter_info.get("startNode", ""); index = self.start_node_combo.findText(start_node)
            if index >= 0: self.start_node_combo.setCurrentIndex(index)
            else: self.start_node_combo.setEditText(start_node or "")
            self.chapter_id_edit.blockSignals(False); self.chapter_title_edit.blockSignals(False); self.start_node_combo.blockSignals(False); self.chapter_description_edit.blockSignals(False)
            self.enable_chapter_details()
        else: 
            print(f"ChaptersTab: Selected chapter ID '{chapter_id}' not found in book_graph.chapter_info.") # Debug
            self.disable_chapter_details()

    def on_chapter_id_changed(self):
        """Handle editing finished for the chapter ID field."""
        if not self.book_graph or not self.current_chapter_id or self.chapter_list_updating: return 
        
        old_id = self.current_chapter_id; new_id = self.chapter_id_edit.text().strip()
        if not new_id: QMessageBox.warning(self, "Invalid ID", "Chapter ID cannot be empty."); self.chapter_id_edit.setText(old_id); return
        if new_id == old_id: return 
        if not re.match(r'^[a-zA-Z0-9_-]+$', new_id): QMessageBox.warning(self, "Invalid ID", "Chapter ID can only contain letters, numbers, underscores, and hyphens."); self.chapter_id_edit.setText(old_id); return
        if new_id in self.book_graph.chapter_info: QMessageBox.warning(self, "Duplicate ID", f"Chapter ID '{new_id}' already exists."); self.chapter_id_edit.setText(old_id); return
        
        print(f"ChaptersTab: Attempting to rename chapter '{old_id}' to '{new_id}'")
        success = self.book_graph.rename_chapter(old_id, new_id) 
        if success:
            print(f"ChaptersTab: Renamed chapter successfully.")
            # Important: Update current_chapter_id *before* refreshing list
            self.current_chapter_id = new_id 
            self.update_chapter_list() # Refresh list; this will re-select based on new ID
            self.chapters_changed.emit(list(self.book_graph.chapter_info.values())) 
        else:
            print(f"ChaptersTab: BookGraph rename failed.")
            QMessageBox.critical(self, "Error", f"Failed to rename chapter '{old_id}' to '{new_id}'. Check logs.")
            self.chapter_id_edit.setText(old_id); self.update_chapter_list() 
            
    def on_add_chapter(self):
        """Handle adding a new chapter."""
        if not self.book_graph: return
        print("ChaptersTab: Adding new chapter...") # Debug
        try:
            base_id = "chapter"
            counter = 1
            # --- THIS IS THE LINE FROM THE TRACEBACK ---
            chapter_id = f"{base_id}{counter}" # Initial assignment
            # --- Ensure chapter_id is checked correctly ---
            while chapter_id in self.book_graph.chapter_info: 
                counter += 1
                chapter_id = f"{base_id}{counter}" # Reassignment inside loop
            
            title = f"Chapter {counter}"
            print(f"ChaptersTab: Generated new chapter ID: {chapter_id}, Title: {title}") # Debug
            self.book_graph.add_chapter(chapter_id, title)
            
            # Update list will handle selection
            self.update_chapter_list() 
            
            # Emit signal AFTER list update and selection
            self.chapters_changed.emit(list(self.book_graph.chapter_info.values()))
            print(f"ChaptersTab: Chapter {chapter_id} added and signal emitted.") # Debug
        except Exception as e:
             print(f"ERROR in ChaptersTab.on_add_chapter: {e}")
             traceback.print_exc()


    def on_remove_chapter(self):
        if not self.book_graph or not self.current_chapter_id: return
        reply = QMessageBox.question(self, "Confirm Chapter Removal", f"Remove chapter '{self.current_chapter_id}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes: return
        if self.book_graph.remove_chapter(self.current_chapter_id): self.update_chapter_list(); self.chapters_changed.emit(list(self.book_graph.chapter_info.values()))
        else: QMessageBox.warning(self, "Remove Failed", f"Failed to remove chapter '{self.current_chapter_id}'.", QMessageBox.Ok)
    def on_chapter_title_changed(self):
        if not self.book_graph or not self.current_chapter_id or self.chapter_list_updating: return
        if self.current_chapter_id in self.book_graph.chapter_info: self.book_graph.chapter_info[self.current_chapter_id]["title"] = self.chapter_title_edit.text(); current_item = self.chapter_list.currentItem()
        if current_item: current_item.setText(self.chapter_title_edit.text())
        self.chapters_changed.emit(list(self.book_graph.chapter_info.values()))
    def on_start_node_changed(self):
        if not self.book_graph or not self.current_chapter_id or self.chapter_list_updating: return
        if self.current_chapter_id in self.book_graph.chapter_info: start_node = self.start_node_combo.currentText()
        if start_node: self.book_graph.chapter_info[self.current_chapter_id]["startNode"] = start_node
        elif "startNode" in self.book_graph.chapter_info[self.current_chapter_id]: del self.book_graph.chapter_info[self.current_chapter_id]["startNode"]
        self.chapters_changed.emit(list(self.book_graph.chapter_info.values()))
    def on_chapter_description_changed(self):
        if not self.book_graph or not self.current_chapter_id or self.chapter_list_updating: return
        if self.current_chapter_id in self.book_graph.chapter_info: self.book_graph.chapter_info[self.current_chapter_id]["description"] = self.chapter_description_edit.toPlainText()
        self.chapters_changed.emit(list(self.book_graph.chapter_info.values()))
    def on_move_chapter_up(self):
        if not self.current_chapter_id: return; current_row = self.chapter_list.currentRow()
        if current_row <= 0: return; item = self.chapter_list.takeItem(current_row); self.chapter_list.insertItem(current_row - 1, item); self.chapter_list.setCurrentItem(item); self.update_chapter_order()
    def on_move_chapter_down(self):
        if not self.current_chapter_id: return; current_row = self.chapter_list.currentRow()
        if current_row >= self.chapter_list.count() - 1: return; item = self.chapter_list.takeItem(current_row); self.chapter_list.insertItem(current_row + 1, item); self.chapter_list.setCurrentItem(item); self.update_chapter_order()
    def update_chapter_order(self): 
        if not self.book_graph: return
        new_order_info = {}
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i); chapter_id = item.data(Qt.UserRole)
            if chapter_id in self.book_graph.chapter_info: new_order_info[chapter_id] = self.book_graph.chapter_info[chapter_id]
        self.book_graph.chapter_info = new_order_info 
        self.chapters_changed.emit(list(self.book_graph.chapter_info.values()))
    def enable_chapter_details(self): 
        self.chapter_id_edit.setEnabled(True); self.chapter_title_edit.setEnabled(True); self.chapter_description_edit.setEnabled(True); self.start_node_combo.setEnabled(True); self.remove_button.setEnabled(True)
    def disable_chapter_details(self): 
        self.chapter_id_edit.setText(""); self.chapter_id_edit.setEnabled(False); self.chapter_title_edit.setText(""); self.chapter_description_edit.setText(""); self.start_node_combo.setCurrentIndex(0); self.chapter_title_edit.setEnabled(False); self.chapter_description_edit.setEnabled(False); self.start_node_combo.setEnabled(False); self.remove_button.setEnabled(False); self.current_chapter_id = None
    def set_available_nodes(self, nodes): # Ensure this method exists
        current_text = self.start_node_combo.currentText(); self.start_node_combo.clear(); self.start_node_combo.addItem("")
        for node in nodes:
            if node.node_type != "book": self.start_node_combo.addItem(node.id)
        if current_text: index = self.start_node_combo.findText(current_text); self.start_node_combo.setCurrentIndex(index) if index >= 0 else self.start_node_combo.setEditText(current_text)


class BookNodeEditor(EditorPanel):
    """Editor panel for book nodes. Uses inherited layout."""
    # (Content remains the same as book_editor_fix_3)
    node_updated = pyqtSignal(object) 
    chapters_updated = pyqtSignal(list) 
    def __init__(self, parent=None):
        super().__init__(parent); self.current_node = None; self.book_graph = None
        self.header_label = QLabel("Book Properties"); self.header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        self.layout.addWidget(self.header_label) 
        self.tab_widget = QTabWidget(self); self.layout.addWidget(self.tab_widget) 
        self.basic_tab = BasicBookPropertiesTab(self); self.chapters_tab = ChaptersTab(self)
        self.tab_widget.addTab(self.basic_tab, "Basic"); self.tab_widget.addTab(self.chapters_tab, "Chapters")
        self.basic_tab.property_changed.connect(self.on_property_changed); self.chapters_tab.chapters_changed.connect(self.on_chapters_changed)
    def set_book_graph(self, book_graph): self.book_graph = book_graph; self.chapters_tab.set_book_graph(book_graph); self.update_node_lists() 
    def update_node_lists(self):
        if self.book_graph: nodes = self.book_graph.get_all_nodes(); self.basic_tab.set_available_nodes(nodes); self.chapters_tab.set_available_nodes(nodes) 
    def update_for_node(self, node): self.current_node = node; self.basic_tab.update_for_node(node); self.chapters_tab.update_chapter_list(); self.update_node_lists()
    def clear_panel(self): self.current_node = None
    def on_property_changed(self, property_name, new_value):
        if not self.current_node: return
        if property_name.startswith("metadata."):
             metadata_key = property_name.split(".", 1)[1]
             if new_value is None or new_value == "": 
                  if metadata_key in self.current_node.metadata: del self.current_node.metadata[metadata_key]
             else: self.current_node.metadata[metadata_key] = new_value
        else:
             if hasattr(self.current_node, property_name): setattr(self.current_node, property_name, new_value)
             else: print(f"BookNodeEditor: Warning - Node has no attribute '{property_name}'")
        self.node_updated.emit(self.current_node)
    def on_chapters_changed(self, chapters): self.chapters_updated.emit(chapters)

