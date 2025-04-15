"""
Node editor panel for the Interactive Book Editor.
FIXED: Ensured full implementations for all tab classes are included.
FIXED: Corrected layout initialization in tab widgets to avoid conflicts.
REVISED: Show 'POV Character' field for 'fiction' and 'character_pov' types.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QGroupBox, QPushButton, QScrollArea, QTabWidget
)
from PyQt5.QtCore import pyqtSignal, Qt
import traceback # For debugging potential errors in updates

from editor_panel import EditorPanel
# Assuming Node is defined in node.py for type hints if needed
# from node import Node

class BasicNodePropertiesTab(QWidget):
    """Tab for basic node properties (ID, title, type, chapter, POV)."""
    property_changed = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Create layout WITHOUT assigning self as parent initially
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Create Widgets
        self.node_id_label = QLabel()
        self.node_title_edit = QLineEdit()
        self.node_type_combo = QComboBox()
        self.pov_character_label = QLabel("POV Character:")
        self.pov_character_edit = QLineEdit()
        self.node_chapter_combo = QComboBox()

        # Configure Widgets
        self.node_type_combo.addItems(["fiction", "nonfiction", "character", "character_pov", "interactive", "world"])
        self.pov_character_edit.setPlaceholderText("Character name for this POV (e.g., Alec, Nicole, Omniscient)")
        self.node_chapter_combo.setEditable(True)

        # Add Widgets to Layout
        layout.addRow("ID:", self.node_id_label)
        layout.addRow("Title:", self.node_title_edit)
        layout.addRow("Type:", self.node_type_combo)
        layout.addRow(self.pov_character_label, self.pov_character_edit)
        self.pov_character_label.hide()
        self.pov_character_edit.hide()
        layout.addRow("Chapter:", self.node_chapter_combo)

        # Connect Signals
        self.node_title_edit.textChanged.connect(lambda text: self.property_changed.emit("title", text))
        self.node_type_combo.currentTextChanged.connect(self._on_type_changed)
        self.pov_character_edit.textChanged.connect(
            lambda text: self.property_changed.emit("metadata.povCharacter", text.strip() or None)
        )
        self.node_chapter_combo.currentTextChanged.connect(self._on_chapter_changed)

        # Set the layout for this widget
        self.setLayout(layout)

    def _on_type_changed(self, text):
        """Handle node type changes, show/hide POV field."""
        is_pov_editable = (text in ["fiction", "character_pov"])
        self.pov_character_label.setVisible(is_pov_editable)
        self.pov_character_edit.setVisible(is_pov_editable)
        self.property_changed.emit("node_type", text)
        if not is_pov_editable and self.pov_character_edit.text():
             self.pov_character_edit.clear()
             self.property_changed.emit("metadata.povCharacter", None)

    def _on_chapter_changed(self, text):
        """Handle chapter changes, emit only the text."""
        self.property_changed.emit("chapter", text.strip() or None)

    def update_for_node(self, node):
        """Update the tab for the selected node."""
        try:
            print(f"--- BasicNodePropertiesTab: update_for_node START (Node ID: {getattr(node, 'id', 'N/A')}) ---")
            if not node:
                 print("BasicNodePropertiesTab: Received None node. Clearing fields."); self.node_id_label.setText(""); self.node_title_edit.setText(""); self.node_type_combo.setCurrentIndex(0); self.node_chapter_combo.setEditText(""); self.pov_character_edit.setText(""); self.pov_character_label.hide(); self.pov_character_edit.hide(); return

            print("BasicNodePropertiesTab: Blocking signals...")
            self.node_title_edit.blockSignals(True); self.node_type_combo.blockSignals(True); self.node_chapter_combo.blockSignals(True); self.pov_character_edit.blockSignals(True)

            node_id_val = node.id or "N/A"; print(f"BasicNodePropertiesTab: Setting ID Label to: '{node_id_val}'"); self.node_id_label.setText(node_id_val); print("BasicNodePropertiesTab: ID Label set.")
            node_title_val = node.title or ""; print(f"BasicNodePropertiesTab: Setting Title Edit to: '{node_title_val}'"); self.node_title_edit.setText(node_title_val); print("BasicNodePropertiesTab: Title Edit set.")
            node_type = node.node_type or "fiction"; print(f"BasicNodePropertiesTab: Setting Type Combo to: '{node_type}'"); index = self.node_type_combo.findText(node_type); target_index = index if index >= 0 else 0; self.node_type_combo.setCurrentIndex(target_index); print(f"BasicNodePropertiesTab: Type Combo index set to {target_index}.")
            is_pov_editable = (node_type in ["fiction", "character_pov"]); print(f"BasicNodePropertiesTab: Setting POV fields visible: {is_pov_editable}"); self.pov_character_label.setVisible(is_pov_editable); self.pov_character_edit.setVisible(is_pov_editable)
            if is_pov_editable: metadata = getattr(node, 'metadata', {}); pov_char_val = metadata.get("povCharacter", ""); print(f"BasicNodePropertiesTab: Setting POV Edit to: '{pov_char_val}'"); self.pov_character_edit.setText(pov_char_val); print("BasicNodePropertiesTab: POV Edit set.")
            else: print("BasicNodePropertiesTab: Clearing POV Edit."); self.pov_character_edit.clear()
            current_chapter = node.chapter or ""; print(f"BasicNodePropertiesTab: Setting Chapter Combo to: '{current_chapter}'"); index = self.node_chapter_combo.findText(current_chapter)
            if index >= 0: self.node_chapter_combo.setCurrentIndex(index); print(f"BasicNodePropertiesTab: Chapter Combo index set to {index}.")
            else:
                print(f"BasicNodePropertiesTab: Chapter '{current_chapter}' not in list, setting edit text.")
                # Check if lineEdit exists and text is different before setting
                if self.node_chapter_combo.lineEdit() and self.node_chapter_combo.lineEdit().text() != current_chapter: self.node_chapter_combo.setEditText(current_chapter)
                elif not self.node_chapter_combo.lineEdit(): self.node_chapter_combo.setEditText(current_chapter) # Safety check
                print(f"BasicNodePropertiesTab: Chapter Combo edit text set.")

            print("BasicNodePropertiesTab: Unblocking signals..."); self.node_title_edit.blockSignals(False); self.node_type_combo.blockSignals(False); self.node_chapter_combo.blockSignals(False); self.pov_character_edit.blockSignals(False)
            print("BasicNodePropertiesTab: Forcing update/repaint..."); self.update(); print(f"--- BasicNodePropertiesTab: update_for_node END (Node ID: {getattr(node, 'id', 'N/A')}) ---")
        except Exception as e:
             print(f"ERROR in BasicNodePropertiesTab.update_for_node: {e}")
             traceback.print_exc()

    def set_available_chapters(self, chapters):
        """Set the available chapters for the chapter combo box."""
        try:
            print(f"BasicNodePropertiesTab: Setting {len(chapters)} available chapters.")
            self.node_chapter_combo.blockSignals(True)
            current_text = self.node_chapter_combo.currentText(); self.node_chapter_combo.clear(); self.node_chapter_combo.addItem("")
            chapter_ids = set()
            for chapter in chapters: chapter_id = chapter.get("id");
            if chapter_id and chapter_id not in chapter_ids: self.node_chapter_combo.addItem(chapter_id); chapter_ids.add(chapter_id)
            index = self.node_chapter_combo.findText(current_text);
            if index >= 0: self.node_chapter_combo.setCurrentIndex(index)
            else: self.node_chapter_combo.setEditText(current_text);
            self.node_chapter_combo.blockSignals(False); print("BasicNodePropertiesTab: Available chapters set.")
        except Exception as e:
             print(f"ERROR in BasicNodePropertiesTab.set_available_chapters: {e}")
             traceback.print_exc()


# --- FileDetailsTab ---
class FileDetailsTab(QWidget):
    """Tab for file details (file path, position)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create layout WITHOUT assigning self as parent initially
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.node_file_path_label = QLabel()
        layout.addRow("File Path:", self.node_file_path_label)
        self.node_position_label = QLabel()
        layout.addRow("Position:", self.node_position_label)
        # Set the layout for this widget
        self.setLayout(layout)

    def update_for_node(self, node):
        """Update the tab for the selected node."""
        try:
            self.node_file_path_label.setText(getattr(node, 'file_path', "") or "")
            pos = getattr(node, 'position', None)
            if isinstance(pos, (list, tuple)) and len(pos) == 2:
                 try:
                     pos_x = float(pos[0]); pos_y = float(pos[1])
                     self.node_position_label.setText(f"({pos_x:.1f}, {pos_y:.1f})")
                 except (ValueError, TypeError): self.node_position_label.setText("(Invalid Pos)")
            else: self.node_position_label.setText("(N/A)")
        except Exception as e:
             print(f"ERROR in FileDetailsTab.update_for_node: {e}")
             traceback.print_exc()


# --- ConnectionsTab ---
class ConnectionsTab(QWidget):
    """Tab for node connections."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create layout WITHOUT assigning self as parent initially
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Outgoing Group
        self.outgoing_group = QGroupBox("Outgoing Connections")
        outgoing_layout = QVBoxLayout() # Layout for the groupbox
        self.outgoing_group.setLayout(outgoing_layout) # Set layout on groupbox
        self.outgoing_layout = outgoing_layout # Store reference to inner layout
        layout.addWidget(self.outgoing_group) # Add groupbox to main layout

        # Incoming Group
        self.incoming_group = QGroupBox("Incoming Connections")
        incoming_layout = QVBoxLayout() # Layout for the groupbox
        self.incoming_group.setLayout(incoming_layout) # Set layout on groupbox
        self.incoming_layout = incoming_layout # Store reference to inner layout
        layout.addWidget(self.incoming_group) # Add groupbox to main layout

        # Set the main layout for this widget
        self.setLayout(layout)

    def update_for_node(self, node, book_graph):
        """Update connection lists for the selected node."""
        # Clear previous widgets safely
        for i in reversed(range(self.outgoing_layout.count())):
             widget = self.outgoing_layout.itemAt(i).widget()
             if widget: widget.deleteLater()
        for i in reversed(range(self.incoming_layout.count())):
             widget = self.incoming_layout.itemAt(i).widget()
             if widget: widget.deleteLater()

        # Add default text if no node/graph
        if not node or not book_graph:
             self.outgoing_layout.addWidget(QLabel("N/A"))
             self.incoming_layout.addWidget(QLabel("N/A"))
             return

        # Add outgoing connections
        outgoing_found = False
        try:
            # Ensure node.id exists before querying edges
            if hasattr(node, 'id') and node.id:
                for _, target, data in book_graph.graph.out_edges(node.id, data=True):
                    target_node = None
                    try:
                        target_node = book_graph.get_node(target)
                        edge_type = data.get("edge_type", "default")
                        if target_node:
                            self.outgoing_layout.addWidget(QLabel(f"{target_node.title} ({edge_type})"))
                            outgoing_found = True
                        else: print(f"ConnectionsTab: Warning - Target node '{target}' not found.")
                    except Exception as e_inner: print(f"ConnectionsTab: Error processing single outgoing edge to '{target}': {e_inner}")
            else:
                 print(f"ConnectionsTab: Cannot get outgoing edges for invalid node object.")
        except Exception as e_outer: print(f"ConnectionsTab: Error iterating outgoing edges for '{getattr(node, 'id', 'N/A')}': {e_outer}")
        if not outgoing_found: self.outgoing_layout.addWidget(QLabel("No outgoing connections"))

        # Add incoming connections
        incoming_found = False
        try:
             # Ensure node.id exists before querying edges
            if hasattr(node, 'id') and node.id:
                for source, _, data in book_graph.graph.in_edges(node.id, data=True):
                    source_node = None
                    try:
                        source_node = book_graph.get_node(source)
                        edge_type = data.get("edge_type", "default")
                        if source_node:
                            self.incoming_layout.addWidget(QLabel(f"{source_node.title} ({edge_type})"))
                            incoming_found = True
                        else: print(f"ConnectionsTab: Warning - Source node '{source}' not found.")
                    except Exception as e_inner: print(f"ConnectionsTab: Error processing single incoming edge from '{source}': {e_inner}")
            else:
                 print(f"ConnectionsTab: Cannot get incoming edges for invalid node object.")
        except Exception as e_outer: print(f"ConnectionsTab: Error iterating incoming edges for '{getattr(node, 'id', 'N/A')}': {e_outer}")
        if not incoming_found: self.incoming_layout.addWidget(QLabel("No incoming connections"))


# --- NodeEditorPanel ---
class NodeEditorPanel(EditorPanel):
    """Editor panel for nodes. Uses inherited layout."""
    node_updated = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node = None; self.book_graph = None

        # Use self.layout inherited from EditorPanel
        self.header_label = QLabel("Node Properties")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        self.layout.addWidget(self.header_label)

        # Restore TabWidget
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)

        # Create the tabs (using full implementations)
        self.basic_tab = BasicNodePropertiesTab(self)
        self.file_tab = FileDetailsTab(self)
        self.connections_tab = ConnectionsTab(self)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.basic_tab, "Basic")
        self.tab_widget.addTab(self.file_tab, "File Details")
        self.tab_widget.addTab(self.connections_tab, "Connections")

        # Connect signals from the basic_tab
        self.basic_tab.property_changed.connect(self.on_property_changed)

    def set_book_graph(self, book_graph):
        self.book_graph = book_graph
        # Pass graph to connections tab too
        self.connections_tab.book_graph = book_graph

    def set_available_chapters(self, chapters):
        self.basic_tab.set_available_chapters(chapters)

    def update_for_node(self, node):
        """Update the panel for the selected node."""
        print(f"NodeEditorPanel: update_for_node called for node ID: {getattr(node, 'id', 'N/A')}")
        if not node: self.clear_panel(); return
        self.current_node = node
        try:
            print("NodeEditorPanel: Updating Basic tab...")
            self.basic_tab.update_for_node(node)
            print("NodeEditorPanel: Updating File tab...")
            self.file_tab.update_for_node(node)
            if self.book_graph:
                print("NodeEditorPanel: Updating Connections tab...")
                self.connections_tab.update_for_node(node, self.book_graph)
            else: print("NodeEditorPanel: Warning - book_graph not set.")
            print("NodeEditorPanel: update_for_node finished.")
        except Exception as e:
             print(f"ERROR in NodeEditorPanel.update_for_node: {e}")
             traceback.print_exc()


    def clear_panel(self):
        """Clear the panel."""
        print("NodeEditorPanel: Clearing panel.")
        # Import Node locally only when needed for the dummy object
        try:
            from node import Node
            dummy_node = Node(node_id="", title="", node_type="", chapter=None, file_path="", position=(0,0), metadata={})
            self.basic_tab.update_for_node(dummy_node)
            self.file_tab.update_for_node(dummy_node)
            self.connections_tab.update_for_node(dummy_node, None)
        except Exception as e:
             print(f"ERROR in NodeEditorPanel.clear_panel: {e}")
             traceback.print_exc()
        self.current_node = None

    def on_property_changed(self, property_name, new_value):
        """Handle when a property is changed."""
        if self.current_node:
            print(f"NodeEditorPanel: Property '{property_name}' changed to '{new_value}' for node {self.current_node.id}")
            try:
                if property_name.startswith("metadata."):
                     metadata_key = property_name.split(".", 1)[1]
                     # Ensure metadata dictionary exists before modifying
                     if not hasattr(self.current_node, 'metadata') or self.current_node.metadata is None:
                          self.current_node.metadata = {}

                     if new_value is None or new_value == "":
                          # Use pop with default to avoid KeyError if key doesn't exist
                          self.current_node.metadata.pop(metadata_key, None)
                          print(f"NodeEditorPanel: Removed metadata key '{metadata_key}' (if existed)")
                     else:
                          self.current_node.metadata[metadata_key] = new_value
                          print(f"NodeEditorPanel: Set metadata '{metadata_key}' to '{new_value}'")
                else:
                     if hasattr(self.current_node, property_name):
                          setattr(self.current_node, property_name, new_value)
                     else: print(f"NodeEditorPanel: Warning - Node object does not have attribute '{property_name}'")
                # Emit signal only after successful update attempt
                self.node_updated.emit(self.current_node)
            except Exception as e:
                 print(f"ERROR in NodeEditorPanel.on_property_changed: {e}")
                 traceback.print_exc()

