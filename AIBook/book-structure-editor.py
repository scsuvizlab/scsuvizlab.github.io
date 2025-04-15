import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                            QPushButton, QFileDialog, QMessageBox, QListWidget,
                            QGroupBox, QFormLayout, QTabWidget, QSplitter,
                            QAction, QToolBar, QStatusBar, QTreeWidget, 
                            QTreeWidgetItem, QCheckBox, QTextEdit, QDialog,
                            QDialogButtonBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import networkx as nx

class BookStructureEditor(QMainWindow):
    """Main application window for the Book Structure Editor."""
    
    def __init__(self):
        super().__init__()
        self.book_structure = None
        self.current_file = None
        self.graph = nx.DiGraph()
        self.node_positions = {}
        self.modified = False
        self.panning = False
        self.pan_start = None
        self.zoom_scale = 1.0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Book Structure Editor")
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create central widget with splitter
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Left panel - Tree view and properties
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        
        # Structure tree widget
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels(["Book Structure"])
        self.structure_tree.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(QLabel("Book Structure:"))
        left_layout.addWidget(self.structure_tree)
        
        # Node properties widget
        self.properties_group = QGroupBox("Node Properties")
        properties_layout = QFormLayout(self.properties_group)
        
        self.node_id_edit = QLineEdit()
        self.node_title_edit = QLineEdit()
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems(["fiction", "nonfiction"])
        self.chapter_combo = QComboBox()
        self.pov_combo = QComboBox()
        self.file_path_edit = QLineEdit()
        self.file_path_browse = QPushButton("Browse...")
        self.file_path_browse.clicked.connect(self.browse_file_path)
        
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(self.file_path_browse)
        
        properties_layout.addRow("Node ID:", self.node_id_edit)
        properties_layout.addRow("Title:", self.node_title_edit)
        properties_layout.addRow("Type:", self.node_type_combo)
        properties_layout.addRow("Chapter:", self.chapter_combo)
        properties_layout.addRow("Default POV:", self.pov_combo)
        properties_layout.addRow("File Path:", file_path_layout)
        
        self.prev_node_combo = QComboBox()
        self.next_node_combo = QComboBox()
        
        properties_layout.addRow("Previous Node:", self.prev_node_combo)
        properties_layout.addRow("Next Node:", self.next_node_combo)
        
        self.update_node_btn = QPushButton("Update Node")
        self.update_node_btn.clicked.connect(self.update_node)
        properties_layout.addRow("", self.update_node_btn)
        
        left_layout.addWidget(self.properties_group)
        
        # Add buttons for common actions
        button_layout = QHBoxLayout()
        
        self.add_node_btn = QPushButton("Add Node")
        self.add_node_btn.clicked.connect(self.add_node_dialog)
        
        self.delete_node_btn = QPushButton("Delete Node")
        self.delete_node_btn.clicked.connect(self.delete_node)
        
        button_layout.addWidget(self.add_node_btn)
        button_layout.addWidget(self.delete_node_btn)
        
        left_layout.addLayout(button_layout)
        
        # Right panel - Graph visualization
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        
        # Graph visualization
        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        right_layout.addWidget(self.canvas)
        
        # Graph controls
        graph_controls_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.refresh_graph_btn = QPushButton("Refresh Graph")
        self.refresh_graph_btn.clicked.connect(self.refresh_graph)
        
        self.reset_view_btn = QPushButton("Reset View")
        self.reset_view_btn.clicked.connect(self.reset_view)
        
        graph_controls_layout.addWidget(self.zoom_in_btn)
        graph_controls_layout.addWidget(self.zoom_out_btn)
        graph_controls_layout.addWidget(self.refresh_graph_btn)
        graph_controls_layout.addWidget(self.reset_view_btn)
        
        right_layout.addLayout(graph_controls_layout)
        
        # Add a status label for navigation tips
        self.nav_tips_label = QLabel("Tip: Use mouse wheel to zoom, right-click and drag to pan")
        self.nav_tips_label.setStyleSheet("color: #666; font-style: italic;")
        right_layout.addWidget(self.nav_tips_label)
        
        # Add panels to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([300, 900])  # Initial sizes
        
        # Disable controls until a file is loaded
        self.enable_controls(False)
        
        # Set up node tracking
        self.current_node = None
        
        # Show the window
        self.show()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        add_node_action = QAction("Add Node", self)
        add_node_action.triggered.connect(self.add_node_dialog)
        edit_menu.addAction(add_node_action)
        
        edit_menu.addSeparator()
        
        add_chapter_action = QAction("Add Chapter", self)
        add_chapter_action.triggered.connect(self.add_chapter_dialog)
        edit_menu.addAction(add_chapter_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh Graph", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_graph)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Add toolbar actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        add_node_action = QAction("Add Node", self)
        add_node_action.triggered.connect(self.add_node_dialog)
        toolbar.addAction(add_node_action)
        
        delete_node_action = QAction("Delete Node", self)
        delete_node_action.triggered.connect(self.delete_node)
        toolbar.addAction(delete_node_action)
        
        toolbar.addSeparator()
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_graph)
        toolbar.addAction(refresh_action)
    
    def enable_controls(self, enabled=True):
        """Enable or disable controls based on whether a file is loaded."""
        self.properties_group.setEnabled(enabled)
        self.add_node_btn.setEnabled(enabled)
        self.delete_node_btn.setEnabled(enabled)
        self.zoom_in_btn.setEnabled(enabled)
        self.zoom_out_btn.setEnabled(enabled)
        self.refresh_graph_btn.setEnabled(enabled)
    
    def new_file(self):
        """Create a new book structure file."""
        if self.modified and not self.confirm_discard_changes():
            return
            
        # Create a basic book structure
        self.book_structure = {
            "title": "New Book",
            "author": "",
            "version": "1.0",
            "defaultStartNode": "",
            "defaultPOV": "Omniscient",
            "criticalPath": [],
            "chapters": [],
            "characterPOVs": {},
            "relatedContent": {},
            "tracks": {
                "fiction": {
                    "name": "Narrative Track",
                    "description": "Follow the story in chronological order",
                    "startNode": "",
                    "nodeSequence": []
                },
                "nonfiction": {
                    "name": "Concepts & Context",
                    "description": "Explore the ideas behind the story",
                    "startNode": "",
                    "nodeSequence": []
                }
            },
            "characters": []
        }
        
        self.current_file = None
        self.modified = True
        self.enable_controls(True)
        self.populate_tree()
        self.build_graph()
        self.update_window_title()
        
        # Add a default chapter
        self.add_chapter({
            "id": "chapter1",
            "title": "Chapter 1",
            "description": "First chapter of the book",
            "startNode": "",
            "nodes": []
        })
    
    def open_file(self):
        """Open a book structure JSON file."""
        if self.modified and not self.confirm_discard_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Book Structure", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.book_structure = json.load(f)
                
                self.current_file = file_path
                self.modified = False
                self.enable_controls(True)
                self.populate_tree()
                self.build_graph()
                self.update_window_title()
                self.statusBar.showMessage(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def save_file(self):
        """Save the current book structure to a file."""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            with open(self.current_file, 'w') as f:
                json.dump(self.book_structure, f, indent=2)
            
            self.modified = False
            self.update_window_title()
            self.statusBar.showMessage(f"Saved: {self.current_file}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
            return False
    
    def save_file_as(self):
        """Save the current book structure to a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Book Structure", "", "JSON Files (*.json)"
        )
        
        if file_path:
            self.current_file = file_path
            return self.save_file()
        
        return False
    
    def confirm_discard_changes(self):
        """Confirm whether to discard unsaved changes."""
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "There are unsaved changes. Do you want to discard them?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def update_window_title(self):
        """Update the window title to show the current file and modification status."""
        title = "Book Structure Editor"
        
        if self.current_file:
            file_name = os.path.basename(self.current_file)
            title = f"{file_name} - {title}"
            
            if self.modified:
                title = f"*{title}"
        
        self.setWindowTitle(title)
    
    def populate_tree(self):
        """Populate the tree widget with the book structure."""
        self.structure_tree.clear()
        
        if not self.book_structure:
            return
        
        # Book details root item
        book_item = QTreeWidgetItem(self.structure_tree)
        book_item.setText(0, "Book Details")
        book_item.setData(0, Qt.UserRole, {"type": "book_details"})
        
        title_item = QTreeWidgetItem(book_item)
        title_item.setText(0, f"Title: {self.book_structure['title']}")
        
        author_item = QTreeWidgetItem(book_item)
        author_item.setText(0, f"Author: {self.book_structure.get('author', '')}")
        
        version_item = QTreeWidgetItem(book_item)
        version_item.setText(0, f"Version: {self.book_structure.get('version', '1.0')}")
        
        # Critical path
        critical_path_item = QTreeWidgetItem(self.structure_tree)
        critical_path_item.setText(0, "Critical Path")
        critical_path_item.setData(0, Qt.UserRole, {"type": "critical_path"})
        
        for node in self.book_structure.get("criticalPath", []):
            node_item = QTreeWidgetItem(critical_path_item)
            node_item.setText(0, f"{node['id']} - {node.get('title', 'No Title')}")
            node_item.setData(0, Qt.UserRole, {"type": "node", "id": node["id"]})
        
        # Chapters
        chapters_item = QTreeWidgetItem(self.structure_tree)
        chapters_item.setText(0, "Chapters")
        chapters_item.setData(0, Qt.UserRole, {"type": "chapters"})
        
        for chapter in self.book_structure.get("chapters", []):
            chapter_item = QTreeWidgetItem(chapters_item)
            chapter_item.setText(0, f"{chapter['id']} - {chapter.get('title', 'No Title')}")
            chapter_item.setData(0, Qt.UserRole, {"type": "chapter", "id": chapter["id"]})
            
            for node_id in chapter.get("nodes", []):
                node_item = QTreeWidgetItem(chapter_item)
                # Find node details
                node_details = next((n for n in self.book_structure.get("criticalPath", []) if n["id"] == node_id), None)
                if node_details:
                    node_item.setText(0, f"{node_id} - {node_details.get('title', 'No Title')}")
                else:
                    node_item.setText(0, node_id)
                node_item.setData(0, Qt.UserRole, {"type": "node", "id": node_id})
        
        # Tracks
        tracks_item = QTreeWidgetItem(self.structure_tree)
        tracks_item.setText(0, "Tracks")
        tracks_item.setData(0, Qt.UserRole, {"type": "tracks"})
        
        for track_id, track in self.book_structure.get("tracks", {}).items():
            track_item = QTreeWidgetItem(tracks_item)
            track_item.setText(0, f"{track_id} - {track.get('name', 'No Name')}")
            track_item.setData(0, Qt.UserRole, {"type": "track", "id": track_id})
            
            for node_id in track.get("nodeSequence", []):
                node_item = QTreeWidgetItem(track_item)
                # Find node details
                node_details = next((n for n in self.book_structure.get("criticalPath", []) if n["id"] == node_id), None)
                if node_details:
                    node_item.setText(0, f"{node_id} - {node_details.get('title', 'No Title')}")
                else:
                    node_item.setText(0, node_id)
                node_item.setData(0, Qt.UserRole, {"type": "node", "id": node_id})
        
        # Characters
        characters_item = QTreeWidgetItem(self.structure_tree)
        characters_item.setText(0, "Characters")
        characters_item.setData(0, Qt.UserRole, {"type": "characters"})
        
        for character in self.book_structure.get("characters", []):
            character_item = QTreeWidgetItem(characters_item)
            character_item.setText(0, f"{character['id']} - {character.get('name', 'No Name')}")
            character_item.setData(0, Qt.UserRole, {"type": "character", "id": character["id"]})
        
        # Expand root items
        for i in range(self.structure_tree.topLevelItemCount()):
            self.structure_tree.topLevelItem(i).setExpanded(True)
    
    def on_tree_item_clicked(self, item, column):
        """Handle tree item selection."""
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        item_type = item_data.get("type")
        
        if item_type == "node":
            node_id = item_data.get("id")
            self.load_node_properties(node_id)
            self.highlight_node(node_id)
    
    def load_node_properties(self, node_id):
        """Load node properties into the form."""
        node = next((n for n in self.book_structure.get("criticalPath", []) if n["id"] == node_id), None)
        
        if not node:
            self.properties_group.setEnabled(False)
            self.current_node = None
            return
        
        self.properties_group.setEnabled(True)
        self.current_node = node
        
        # Update form fields
        self.node_id_edit.setText(node["id"])
        self.node_title_edit.setText(node.get("title", ""))
        
        # Set node type
        index = self.node_type_combo.findText(node.get("type", "fiction"))
        if index >= 0:
            self.node_type_combo.setCurrentIndex(index)
        
        # Update chapters combo
        self.chapter_combo.clear()
        for chapter in self.book_structure.get("chapters", []):
            self.chapter_combo.addItem(f"{chapter['id']} - {chapter.get('title', '')}", chapter["id"])
        
        # Set current chapter
        if "chapter" in node:
            index = self.chapter_combo.findData(node["chapter"])
            if index >= 0:
                self.chapter_combo.setCurrentIndex(index)
        
        # Update POV combo
        self.pov_combo.clear()
        self.pov_combo.addItem("Omniscient", "Omniscient")
        for character in self.book_structure.get("characters", []):
            self.pov_combo.addItem(character.get("name", character["id"]), character["id"])
        
        # Set current POV
        if "defaultPOV" in node:
            index = self.pov_combo.findText(node["defaultPOV"])
            if index >= 0:
                self.pov_combo.setCurrentIndex(index)
        
        # Set file path
        self.file_path_edit.setText(node.get("filePath", ""))
        
        # Update prev/next node combos
        self.prev_node_combo.clear()
        self.next_node_combo.clear()
        
        self.prev_node_combo.addItem("None", "")
        self.next_node_combo.addItem("None", "")
        
        for n in self.book_structure.get("criticalPath", []):
            if n["id"] != node_id:
                self.prev_node_combo.addItem(f"{n['id']} - {n.get('title', '')}", n["id"])
                self.next_node_combo.addItem(f"{n['id']} - {n.get('title', '')}", n["id"])
        
        # Set current prev/next nodes
        prev_node = None
        for n in self.book_structure.get("criticalPath", []):
            if n.get("nextNode") == node_id:
                prev_node = n["id"]
                break
        
        if prev_node:
            index = self.prev_node_combo.findData(prev_node)
            if index >= 0:
                self.prev_node_combo.setCurrentIndex(index)
        
        if "nextNode" in node and node["nextNode"]:
            index = self.next_node_combo.findData(node["nextNode"])
            if index >= 0:
                self.next_node_combo.setCurrentIndex(index)
    
    def update_node(self):
        """Update node properties from the form."""
        if not self.current_node:
            return
        
        # Get current node data
        old_node_id = self.current_node["id"]
        node_id = self.node_id_edit.text().strip()
        
        # Basic validation
        if not node_id:
            QMessageBox.warning(self, "Invalid Input", "Node ID cannot be empty")
            return
        
        # Update node data
        self.current_node["id"] = node_id
        self.current_node["title"] = self.node_title_edit.text().strip()
        self.current_node["type"] = self.node_type_combo.currentText()
        self.current_node["chapter"] = self.chapter_combo.currentData()
        self.current_node["defaultPOV"] = self.pov_combo.currentText()
        self.current_node["filePath"] = self.file_path_edit.text().strip()
        
        # Update nextNode
        next_node = self.next_node_combo.currentData()
        if next_node:
            self.current_node["nextNode"] = next_node
        elif "nextNode" in self.current_node:
            del self.current_node["nextNode"]
        
        # Update other nodes that point to this one
        prev_node = self.prev_node_combo.currentData()
        
        # First, remove any previous connections
        for node in self.book_structure.get("criticalPath", []):
            if node.get("nextNode") == old_node_id and node["id"] != prev_node:
                node["nextNode"] = None
        
        # Set new connection
        if prev_node:
            prev_node_obj = next((n for n in self.book_structure.get("criticalPath", []) if n["id"] == prev_node), None)
            if prev_node_obj:
                prev_node_obj["nextNode"] = node_id
        
        # Update any references to the node if ID changed
        if old_node_id != node_id:
            # Update in chapters
            for chapter in self.book_structure.get("chapters", []):
                if old_node_id in chapter.get("nodes", []):
                    chapter["nodes"] = [node_id if n == old_node_id else n for n in chapter["nodes"]]
                
                if chapter.get("startNode") == old_node_id:
                    chapter["startNode"] = node_id
            
            # Update in tracks
            for track in self.book_structure.get("tracks", {}).values():
                if old_node_id in track.get("nodeSequence", []):
                    track["nodeSequence"] = [node_id if n == old_node_id else n for n in track["nodeSequence"]]
                
                if track.get("startNode") == old_node_id:
                    track["startNode"] = node_id
            
            # Update nextNode references
            for node in self.book_structure.get("criticalPath", []):
                if node.get("nextNode") == old_node_id:
                    node["nextNode"] = node_id
        
        self.modified = True
        self.update_window_title()
        self.populate_tree()
        self.build_graph()
        self.statusBar.showMessage(f"Updated node: {node_id}")
    
    def add_node_dialog(self):
        """Show dialog for adding a new node."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Node")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        node_id_edit = QLineEdit()
        node_title_edit = QLineEdit()
        node_type_combo = QComboBox()
        node_type_combo.addItems(["fiction", "nonfiction"])
        
        chapter_combo = QComboBox()
        chapter_combo.addItem("None", "")
        for chapter in self.book_structure.get("chapters", []):
            chapter_combo.addItem(f"{chapter['id']} - {chapter.get('title', '')}", chapter["id"])
        
        pov_combo = QComboBox()
        pov_combo.addItem("Omniscient", "Omniscient")
        for character in self.book_structure.get("characters", []):
            pov_combo.addItem(character.get("name", character["id"]), character["id"])
        
        file_path_edit = QLineEdit()
        file_path_browse = QPushButton("Browse...")
        
        def browse_file_path():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "Select Node JSON File", "", "JSON Files (*.json)"
            )
            if file_path:
                file_path_edit.setText(file_path)
        
        file_path_browse.clicked.connect(browse_file_path)
        
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(file_path_edit)
        file_path_layout.addWidget(file_path_browse)
        
        form_layout.addRow("Node ID:", node_id_edit)
        form_layout.addRow("Title:", node_title_edit)
        form_layout.addRow("Type:", node_type_combo)
        form_layout.addRow("Chapter:", chapter_combo)
        form_layout.addRow("Default POV:", pov_combo)
        form_layout.addRow("File Path:", file_path_layout)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create new node
            node_id = node_id_edit.text().strip()
            
            # Basic validation
            if not node_id:
                QMessageBox.warning(self, "Invalid Input", "Node ID cannot be empty")
                return
            
            # Check for duplicate ID
            if any(n["id"] == node_id for n in self.book_structure.get("criticalPath", [])):
                QMessageBox.warning(self, "Duplicate ID", f"Node ID '{node_id}' already exists")
                return
            
            # Create node object
            node = {
                "id": node_id,
                "title": node_title_edit.text().strip(),
                "type": node_type_combo.currentText(),
                "defaultPOV": pov_combo.currentText()
            }
            
            # Add chapter if selected
            chapter_id = chapter_combo.currentData()
            if chapter_id:
                node["chapter"] = chapter_id
                
                # Add node to chapter's nodes list
                for chapter in self.book_structure.get("chapters", []):
                    if chapter["id"] == chapter_id:
                        if "nodes" not in chapter:
                            chapter["nodes"] = []
                        chapter["nodes"].append(node_id)
                        break
            
            # Add file path if specified
            file_path = file_path_edit.text().strip()
            if file_path:
                node["filePath"] = file_path
            
            # Add node to critical path
            self.book_structure["criticalPath"].append(node)
            
            self.modified = True
            self.update_window_title()
            self.populate_tree()
            self.build_graph()
            self.statusBar.showMessage(f"Added node: {node_id}")
    
    def add_chapter_dialog(self):
        """Show dialog for adding a new chapter."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Chapter")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        chapter_id_edit = QLineEdit()
        chapter_title_edit = QLineEdit()
        chapter_desc_edit = QTextEdit()
        chapter_desc_edit.setMaximumHeight(100)
        
        start_node_combo = QComboBox()
        start_node_combo.addItem("None", "")
        for node in self.book_structure.get("criticalPath", []):
            start_node_combo.addItem(f"{node['id']} - {node.get('title', '')}", node["id"])
        
        form_layout.addRow("Chapter ID:", chapter_id_edit)
        form_layout.addRow("Title:", chapter_title_edit)
        form_layout.addRow("Description:", chapter_desc_edit)
        form_layout.addRow("Start Node:", start_node_combo)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create new chapter
            chapter_id = chapter_id_edit.text().strip()
            
            # Basic validation
            if not chapter_id:
                QMessageBox.warning(self, "Invalid Input", "Chapter ID cannot be empty")
                return
            
            # Check for duplicate ID
            if any(c["id"] == chapter_id for c in self.book_structure.get("chapters", [])):
                QMessageBox.warning(self, "Duplicate ID", f"Chapter ID '{chapter_id}' already exists")
                return
            
            # Create chapter object
            chapter = {
                "id": chapter_id,
                "title": chapter_title_edit.text().strip(),
                "description": chapter_desc_edit.toPlainText(),
                "startNode": start_node_combo.currentData(),
                "nodes": []
            }
            
            # Add chapter
            self.add_chapter(chapter)
    
    def add_chapter(self, chapter):
        """Add a chapter to the book structure."""
        if "chapters" not in self.book_structure:
            self.book_structure["chapters"] = []
        
        self.book_structure["chapters"].append(chapter)
        
        self.modified = True
        self.update_window_title()
        self.populate_tree()
        self.statusBar.showMessage(f"Added chapter: {chapter['id']}")
    
    def delete_node(self):
        """Delete the currently selected node."""
        if not self.current_node:
            return
        
        node_id = self.current_node["id"]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete node '{node_id}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Remove node from critical path
        self.book_structure["criticalPath"] = [
            n for n in self.book_structure.get("criticalPath", []) if n["id"] != node_id
        ]
        
        # Update nextNode references
        for node in self.book_structure.get("criticalPath", []):
            if node.get("nextNode") == node_id:
                node["nextNode"] = None
        
        # Remove from chapters
        for chapter in self.book_structure.get("chapters", []):
            if node_id in chapter.get("nodes", []):
                chapter["nodes"] = [n for n in chapter["nodes"] if n != node_id]
            
            if chapter.get("startNode") == node_id:
                chapter["startNode"] = ""
        
        # Remove from tracks
        for track in self.book_structure.get("tracks", {}).values():
            if node_id in track.get("nodeSequence", []):
                track["nodeSequence"] = [n for n in track["nodeSequence"] if n != node_id]
            
            if track.get("startNode") == node_id:
                track["startNode"] = ""
        
        # Remove from character POVs
        character_povs = self.book_structure.get("characterPOVs", {})
        keys_to_remove = []
        for key in character_povs.keys():
            if key == node_id:
                keys_to_remove.append(key)
            else:
                character_povs[key] = [pov for pov in character_povs[key] if pov.get("nodeId") != node_id]
        
        for key in keys_to_remove:
            del character_povs[key]
        
        # Remove from related content
        related_content = self.book_structure.get("relatedContent", {})
        keys_to_remove = []
        for key in related_content.keys():
            if key == node_id:
                keys_to_remove.append(key)
            else:
                related_content[key] = [rel for rel in related_content[key] if rel != node_id]
        
        for key in keys_to_remove:
            del related_content[key]
        
        self.current_node = None
        self.modified = True
        self.update_window_title()
        self.properties_group.setEnabled(False)
        self.populate_tree()
        self.build_graph()
        self.statusBar.showMessage(f"Deleted node: {node_id}")
    
    def build_graph(self):
        """Build a network graph of the book structure."""
        self.graph = nx.DiGraph()
        
        if not self.book_structure:
            self.refresh_graph()
            return
        
        # Add nodes to graph
        for node in self.book_structure.get("criticalPath", []):
            node_id = node["id"]
            node_type = node.get("type", "fiction")
            node_title = node.get("title", node_id)
            
            self.graph.add_node(node_id, title=node_title, type=node_type)
        
        # Add edges for nextNode connections
        for node in self.book_structure.get("criticalPath", []):
            if "nextNode" in node and node["nextNode"]:
                source = node["id"]
                target = node["nextNode"]
                
                if self.graph.has_node(target):  # Ensure target exists
                    self.graph.add_edge(source, target, type="next")
        
        # Add edges for character POVs
        for base_node_id, pov_list in self.book_structure.get("characterPOVs", {}).items():
            if not self.graph.has_node(base_node_id):
                continue
                
            for pov in pov_list:
                pov_node_id = pov.get("nodeId")
                if pov_node_id and self.graph.has_node(pov_node_id):
                    self.graph.add_edge(base_node_id, pov_node_id, type="pov")
        
        # Add edges for related content
        for node_id, related_list in self.book_structure.get("relatedContent", {}).items():
            if not self.graph.has_node(node_id):
                continue
                
            for related_id in related_list:
                if self.graph.has_node(related_id):
                    self.graph.add_edge(node_id, related_id, type="related")
        
        # Calculate layout
        try:
            # Try to reuse existing positions for stability
            if not self.node_positions or len(self.node_positions) < len(self.graph.nodes):
                self.node_positions = nx.kamada_kawai_layout(self.graph)
        except:
            # Fall back to spring layout if kamada_kawai fails
            self.node_positions = nx.spring_layout(self.graph)
        
        self.refresh_graph()
    
    def refresh_graph(self):
        """Refresh the graph visualization."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not self.graph or len(self.graph) == 0:
            ax.text(0.5, 0.5, "No nodes to display", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes)
            self.canvas.draw()
            return
        
        # Define node colors
        node_colors = {
            "fiction": "#6ecff6",
            "nonfiction": "#9370db"
        }
        
        # Define edge colors
        edge_colors = {
            "next": "#ffd700",
            "pov": "#6ecff6",
            "related": "#ff69b4"
        }
        
        # Extract node positions, colors, and labels
        pos = self.node_positions
        
        # Draw the nodes
        for node_type, color in node_colors.items():
            nodes = [n for n, attrs in self.graph.nodes(data=True) if attrs.get("type") == node_type]
            nx.draw_networkx_nodes(self.graph, pos, nodelist=nodes, node_color=color, node_size=500, alpha=0.8, ax=ax)
        
        # Draw edges
        for edge_type, color in edge_colors.items():
            edges = [(u, v) for u, v, attrs in self.graph.edges(data=True) if attrs.get("type") == edge_type]
            nx.draw_networkx_edges(self.graph, pos, edgelist=edges, edge_color=color, arrows=True, width=1.5, ax=ax)
        
        # Draw labels
        labels = {n: attrs.get("title", n) for n, attrs in self.graph.nodes(data=True)}
        nx.draw_networkx_labels(self.graph, pos, labels=labels, font_size=8, ax=ax)
        
        # Set plot properties
        ax.set_axis_off()
        ax.set_title("Book Structure Graph")
        
        # Update plot
        self.canvas.draw()
    
    def zoom_in(self):
        """Zoom in on the graph."""
        ax = self.figure.gca()
        x_lim = ax.get_xlim()
        y_lim = ax.get_ylim()
        
        # Zoom in 20%
        ax.set_xlim([x_lim[0] * 0.8, x_lim[1] * 0.8])
        ax.set_ylim([y_lim[0] * 0.8, y_lim[1] * 0.8])
        
        self.canvas.draw()
    
    def zoom_out(self):
        """Zoom out on the graph."""
        ax = self.figure.gca()
        x_lim = ax.get_xlim()
        y_lim = ax.get_ylim()
        
        # Zoom out 20%
        ax.set_xlim([x_lim[0] * 1.2, x_lim[1] * 1.2])
        ax.set_ylim([y_lim[0] * 1.2, y_lim[1] * 1.2])
        
        self.canvas.draw()
    
    def reset_view(self):
        """Reset the graph view to default."""
        self.build_graph()
        self.statusBar.showMessage("View reset to default")
    
    def on_scroll(self, event):
        """Handle mouse wheel scroll events for zooming."""
        if event.inaxes:
            ax = event.inaxes
            x_lim = ax.get_xlim()
            y_lim = ax.get_ylim()
            
            # Get the current mouse position
            x_data, y_data = event.xdata, event.ydata
            
            # Zoom factor: positive steps = zoom in, negative = zoom out
            zoom_factor = 1.1 if event.button == 'up' else 0.9
            
            # Calculate new zoom
            x_left = x_data - (x_data - x_lim[0]) * zoom_factor
            x_right = x_data + (x_lim[1] - x_data) * zoom_factor
            y_bottom = y_data - (y_data - y_lim[0]) * zoom_factor
            y_top = y_data + (y_lim[1] - y_data) * zoom_factor
            
            # Apply new limits
            ax.set_xlim([x_left, x_right])
            ax.set_ylim([y_bottom, y_top])
            
            # Update canvas
            self.canvas.draw()
    
    def on_mouse_press(self, event):
        """Handle mouse button press events."""
        if event.button == 3:  # Right mouse button
            self.panning = True
            self.pan_start = (event.x, event.y)
            self.canvas.setCursor(Qt.ClosedHandCursor)
            
    def on_mouse_release(self, event):
        """Handle mouse button release events."""
        if event.button == 3:  # Right mouse button
            self.panning = False
            self.canvas.setCursor(Qt.ArrowCursor)
    
    def on_mouse_move(self, event):
        """Handle mouse movement events."""
        if self.panning and hasattr(event, 'x') and hasattr(event, 'y'):
            if self.pan_start:
                # Calculate movement delta
                dx = event.x - self.pan_start[0]
                dy = event.y - self.pan_start[1]
                
                if dx == 0 and dy == 0:
                    return
                
                # Update the figure pan
                ax = self.figure.gca()
                
                # Convert canvas pixels to data coordinates
                x_lim = ax.get_xlim()
                y_lim = ax.get_ylim()
                
                # Scale movement to data coordinates
                transform = ax.transData.inverted()
                dx_data, dy_data = transform.transform((event.x, event.y)) - transform.transform(self.pan_start)
                
                # Pan by moving the limits
                ax.set_xlim([x_lim[0] - dx_data, x_lim[1] - dx_data])
                ax.set_ylim([y_lim[0] - dy_data, y_lim[1] - dy_data])
                
                # Update canvas
                self.canvas.draw()
                
                # Update starting position for next movement
                self.pan_start = (event.x, event.y)
    
    def highlight_node(self, node_id):
        """Highlight a specific node in the graph."""
        if not self.graph.has_node(node_id):
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        pos = self.node_positions
        
        # Define node colors
        node_colors = {
            "fiction": "#6ecff6",
            "nonfiction": "#9370db"
        }
        
        # Define edge colors
        edge_colors = {
            "next": "#ffd700",
            "pov": "#6ecff6",
            "related": "#ff69b4"
        }
        
        # Draw regular nodes
        for node_type, color in node_colors.items():
            nodes = [n for n, attrs in self.graph.nodes(data=True) 
                    if attrs.get("type") == node_type and n != node_id]
            nx.draw_networkx_nodes(self.graph, pos, nodelist=nodes, node_color=color, 
                                node_size=500, alpha=0.6, ax=ax)
        
        # Draw highlighted node
        highlighted_node = self.graph.nodes[node_id]
        node_type = highlighted_node.get("type", "fiction")
        color = node_colors.get(node_type, "#6ecff6")
        
        nx.draw_networkx_nodes(self.graph, pos, nodelist=[node_id], node_color="red", 
                             node_size=700, alpha=1.0, ax=ax)
        
        # Draw edges
        for edge_type, color in edge_colors.items():
            edges = [(u, v) for u, v, attrs in self.graph.edges(data=True) if attrs.get("type") == edge_type]
            nx.draw_networkx_edges(self.graph, pos, edgelist=edges, edge_color=color, arrows=True, width=1.5, ax=ax)
        
        # Draw labels
        labels = {n: attrs.get("title", n) for n, attrs in self.graph.nodes(data=True)}
        nx.draw_networkx_labels(self.graph, pos, labels=labels, font_size=8, ax=ax)
        
        # Set plot properties
        ax.set_axis_off()
        ax.set_title(f"Book Structure Graph - Highlighting: {highlighted_node.get('title', node_id)}")
        
        # Update plot
        self.canvas.draw()
    
    def browse_file_path(self):
        """Open a file dialog to select a node JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Node JSON File", "", "JSON Files (*.json)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def show_about(self):
        """Show an about dialog."""
        QMessageBox.about(
            self, "About Book Structure Editor",
            "Book Structure Editor v1.0\n\n"
            "A tool for editing and visualizing interactive book structures.\n\n"
            "Created for managing complex interactive book node relationships."
        )

def main():
    """Main function to start the application."""
    app = QApplication(sys.argv)
    editor = BookStructureEditor()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
