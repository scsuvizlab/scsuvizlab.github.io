"""
Edge editor panel for the Interactive Book Editor.
FIXED: Removed redundant layout creation conflicting with base class.
"""

import json 
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QGroupBox, QTabWidget,
    QTextEdit, QLineEdit 
)
from PyQt5.QtCore import pyqtSignal

from editor_panel import EditorPanel

# --- BasicEdgePropertiesTab and EdgeMetadataTab remain unchanged ---
# --- from edge_editor_fix (the version with QLineEdit imported) ---
class BasicEdgePropertiesTab(QWidget):
    property_changed = pyqtSignal(str, object)
    def __init__(self, parent=None):
        super().__init__(parent); layout = QFormLayout(self); layout.setContentsMargins(10, 10, 10, 10)
        self.edge_source_label = QLabel(); layout.addRow("Source:", self.edge_source_label)
        self.edge_target_label = QLabel(); layout.addRow("Target:", self.edge_target_label)
        self.edge_type_combo = QComboBox(); self.edge_type_combo.addItems(["critical-path", "character-pov", "branch-point", "concept-sequence", "related-concept", "fiction-nonfiction", "default"])
        self.edge_type_combo.currentTextChanged.connect(lambda text: self.property_changed.emit("edge_type", text)); layout.addRow("Type:", self.edge_type_combo)
    def update_for_edge(self, edge):
        self.edge_type_combo.blockSignals(True) 
        self.edge_source_label.setText(edge.source_id); self.edge_target_label.setText(edge.target_id)
        index = self.edge_type_combo.findText(edge.edge_type)
        if index >= 0: self.edge_type_combo.setCurrentIndex(index)
        else: default_index = self.edge_type_combo.findText("default"); self.edge_type_combo.setCurrentIndex(default_index if default_index >=0 else 0)
        self.edge_type_combo.blockSignals(False)

class EdgeMetadataTab(QWidget): 
    metadata_changed = pyqtSignal(dict) 
    def __init__(self, parent=None):
        super().__init__(parent); layout = QFormLayout(self); layout.setContentsMargins(10, 10, 10, 10)
        self.branch_text_label = QLabel("Branch Text:"); self.branch_text_edit = QLineEdit(); self.branch_text_edit.setPlaceholderText("Text displayed for this branch choice")
        self.branch_text_edit.textChanged.connect(self._on_metadata_field_changed); layout.addRow(self.branch_text_label, self.branch_text_edit)
        self.raw_metadata_label = QLabel("Raw Metadata (JSON):"); self.raw_metadata_edit = QTextEdit(); self.raw_metadata_edit.setAcceptRichText(False); self.raw_metadata_edit.setPlaceholderText('{"key": "value", ...}'); self.raw_metadata_edit.setMaximumHeight(100)
        self.raw_metadata_edit.textChanged.connect(self._on_metadata_field_changed); layout.addRow(self.raw_metadata_label, self.raw_metadata_edit)
        self.current_metadata = {} 
    def update_for_edge(self, edge):
        self.current_metadata = edge.metadata.copy() if edge.metadata else {}; self.branch_text_edit.blockSignals(True); self.raw_metadata_edit.blockSignals(True)
        is_branch_point = (edge.edge_type == "branch-point"); self.branch_text_label.setVisible(is_branch_point); self.branch_text_edit.setVisible(is_branch_point)
        if is_branch_point: self.branch_text_edit.setText(self.current_metadata.get("text", ""))
        else: self.branch_text_edit.clear() 
        try: raw_text = json.dumps(self.current_metadata, indent=2) if self.current_metadata else "{}"; self.raw_metadata_edit.setText(raw_text)
        except Exception as e: print(f"Error formatting metadata: {e}"); self.raw_metadata_edit.setText(str(self.current_metadata)) 
        self.branch_text_edit.blockSignals(False); self.raw_metadata_edit.blockSignals(False)
    def _on_metadata_field_changed(self):
        new_metadata = {}; 
        if self.branch_text_edit.isVisible(): branch_text = self.branch_text_edit.text().strip(); new_metadata["text"] = branch_text if branch_text else None # Store None if empty
        if new_metadata.get("text") is None: del new_metadata["text"] # Clean up None value
        try:
            raw_data = json.loads(self.raw_metadata_edit.toPlainText() or '{}')
            if isinstance(raw_data, dict): temp_metadata = new_metadata.copy(); temp_metadata.update(raw_data); new_metadata = temp_metadata # Raw overrides specific fields if keys match
            else: print("Warning: Raw metadata not dict."); new_metadata = {k:v for k,v in new_metadata.items()} 
        except json.JSONDecodeError: print("Warning: Invalid JSON in raw metadata."); new_metadata = {k:v for k,v in new_metadata.items()} 
        if new_metadata != self.current_metadata: self.current_metadata = new_metadata; print(f"Metadata changed, emitting: {self.current_metadata}"); self.metadata_changed.emit(self.current_metadata) 


# --- EdgeEditorPanel MODIFIED ---
class EdgeEditorPanel(EditorPanel):
    """Editor panel for edges."""
    edge_updated = pyqtSignal(object) 
    
    def __init__(self, parent=None):
        """Initialize a new EdgeEditorPanel instance."""
        # Call base class __init__ which sets up self.layout
        super().__init__(parent)
        print("EdgeEditorPanel: Initializing...") # Debug
        self.current_edge = None
        
        # --- Use the layout from the base class (self.layout) ---
        # --- Do NOT create a new layout here: ---
        # self.layout = QVBoxLayout(self) # REMOVED THIS LINE

        # Add header to the existing layout
        self.header_label = QLabel("Connection Properties")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        self.layout.addWidget(self.header_label) # Add to inherited layout
        
        # Add TabWidget to the existing layout
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget) # Add to inherited layout
        
        # Create the tabs
        self.basic_tab = BasicEdgePropertiesTab(self)
        self.metadata_tab = EdgeMetadataTab(self) 
        
        # Add tabs to the tab widget
        self.tab_widget.addTab(self.basic_tab, "Basic")
        self.tab_widget.addTab(self.metadata_tab, "Metadata") 
        
        # Connect signals
        self.basic_tab.property_changed.connect(self.on_property_changed)
        self.metadata_tab.metadata_changed.connect(self.on_metadata_changed) 
        print("EdgeEditorPanel: Initialization complete.") # Debug

    def update_for_edge(self, edge):
        """Update the panel for the selected edge."""
        print(f"EdgeEditorPanel: update_for_edge called for edge: {getattr(edge, 'source_id', 'N/A')}->{getattr(edge, 'target_id', 'N/A')}") # Debug
        self.current_edge = edge
        self.basic_tab.update_for_edge(edge)
        self.metadata_tab.update_for_edge(edge) 

    def clear_panel(self):
        """Clear the panel."""
        print("EdgeEditorPanel: Clearing panel.") # Debug
        self.current_edge = None
        # Optionally clear fields
        # from node import Edge # Local import
        # dummy_edge = Edge("","", None)
        # self.basic_tab.update_for_edge(dummy_edge)
        # self.metadata_tab.update_for_edge(dummy_edge)


    def on_property_changed(self, property_name, new_value):
        """Handle when a basic property (like type) is changed."""
        if self.current_edge:
            setattr(self.current_edge, property_name, new_value)
            self.metadata_tab.update_for_edge(self.current_edge) # Update metadata tab based on new type
            self.edge_updated.emit(self.current_edge) 

    def on_metadata_changed(self, new_metadata):
        """Handle when metadata is changed in the metadata tab."""
        if self.current_edge:
            self.current_edge.metadata = new_metadata 
            print(f"EdgeEditorPanel: Metadata updated on edge object: {self.current_edge.metadata}") 
            self.edge_updated.emit(self.current_edge) 

