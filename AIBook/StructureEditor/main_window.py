"""
MainWindow class for the Interactive Book Editor.
REVISED: Moved model_edge_changed signal here from DataManager.
         Passes self to DataManager to allow signal emission.
         Connects local signal.
"""

print("Importing main_window.py: Starting imports...") 
import os
import sys
import traceback 
from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QAction, QFileDialog, QMessageBox,
    QApplication, QVBoxLayout, QWidget, QInputDialog
)
# Import pyqtSignal here
from PyQt5.QtCore import Qt, QSettings, QPointF, pyqtSignal 

print("Importing main_window.py: Importing Node, Edge...")
from node import Node, Edge
print("Importing main_window.py: Importing BookGraph...")
from book_graph import BookGraph
print("Importing main_window.py: Importing DataManager...")
from data_manager import DataManager 
print("Importing main_window.py: Importing GraphView...")
from graph_view import GraphView
print("Importing main_window.py: Importing PropertiesEditor...")
from properties_editor import PropertiesEditor
print("Importing main_window.py: Importing GraphNodeItem...")
from graph_items import GraphNodeItem 
print("Importing main_window.py: Finished importing project modules.")

print("Defining MainWindow class...") 
class MainWindow(QMainWindow): # Inherits QObject via QMainWindow
    """ Main application window for the Interactive Book Editor. """

    # --- MOVED SIGNAL DEFINITION HERE ---
    model_edge_changed = pyqtSignal(str, str) 
    # --- End Moved Signal ---
    
    def __init__(self):
        """Initialize a new MainWindow instance."""
        print("MainWindow __init__ started.") 
        super().__init__()
        
        self.book_graph = None 
        self.data_manager = DataManager() 
        # --- Pass self (MainWindow instance) to DataManager ---
        self.data_manager.set_signal_emitter(self) 
        # --- End Pass Self ---
        self.project_path = None
        
        self.init_ui()
        self.setup_connections()
        
        self.setWindowTitle("Interactive Book Editor")
        self.resize(1200, 800)
        self.data_manager.enable_auto_save(False)
        print("MainWindow __init__ finished.") 

    def init_ui(self):
        """Initialize the UI components."""
        central_widget = QWidget(self); central_layout = QVBoxLayout(central_widget); central_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_view = GraphView(self); central_layout.addWidget(self.graph_view); self.setCentralWidget(central_widget)
        self.properties_dock = QDockWidget("Properties", self); self.properties_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.properties_editor = PropertiesEditor(self); self.properties_dock.setWidget(self.properties_editor); self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
        self.create_menus(); self.statusBar().showMessage("Ready. Please create or open a project.")

    def create_menus(self):
        """Create the menu bar and menus."""
        file_menu=self.menuBar().addMenu("&File");file_menu.addAction(QAction("&New Project...",self,shortcut="Ctrl+N",triggered=self.on_new_project));file_menu.addAction(QAction("&Open Project...",self,shortcut="Ctrl+O",triggered=self.on_open_project));file_menu.addSeparator();file_menu.addAction(QAction("&Import Node...",self,shortcut="Ctrl+I",triggered=self.on_import_node));file_menu.addSeparator();file_menu.addAction(QAction("&Save",self,shortcut="Ctrl+S",triggered=self.on_save));file_menu.addAction(QAction("Force Save &All",self,triggered=self.on_force_save_all));file_menu.addSeparator();file_menu.addAction(QAction("E&xit",self,shortcut="Alt+F4",triggered=self.close));edit_menu=self.menuBar().addMenu("&Edit");edit_menu.addAction(QAction("&Delete Selected Node",self,shortcut="Delete",triggered=self.on_delete_selected_node));view_menu=self.menuBar().addMenu("&View");view_menu.addAction(QAction("&Fit in View",self,shortcut="F",triggered=self.graph_view.fit_in_view));view_menu.addSeparator();properties_action=self.properties_dock.toggleViewAction();properties_action.setText("&Properties Panel");properties_action.setCheckable(True);properties_action.setChecked(True);view_menu.addAction(properties_action);debug_menu=self.menuBar().addMenu("&Debug");debug_menu.addAction(QAction("&Print Graph Structure",self,triggered=self.debug_print_graph_structure));debug_menu.addAction(QAction("&Force Create Connection",self,triggered=self.debug_force_create_connection));debug_menu.addAction(QAction("&Refresh Graph View",self,triggered=self.debug_refresh_graph_view));debug_menu.addAction(QAction("Create &Book Node",self,triggered=self.debug_create_book_node));debug_menu.addAction(QAction("Update &All Navigation",self,triggered=self.debug_update_all_navigation));

    def setup_connections(self):
        """Set up signal-slot connections."""
        # Graph view UI signals
        self.graph_view.node_selected.connect(self.properties_editor.display_node)
        self.graph_view.edge_selected.connect(self.properties_editor.display_edge)
        self.graph_view.selection_cleared.connect(self.properties_editor.clear_display) 
        
        # Connect graph changes to handlers that update model first
        self.graph_view.node_moved.connect(self.data_manager.on_node_updated) # AutoSave handles model update
        self.graph_view.edge_created.connect(self.handle_edge_created_signal) 
        self.graph_view.edge_deleted.connect(self.handle_edge_deleted_signal) 

        # Connect properties editor changes to handlers
        self.properties_editor.node_updated.connect(self.handle_node_updated_signal) 
        self.properties_editor.edge_updated.connect(self.handle_edge_updated_signal) 
        self.properties_editor.chapters_updated.connect(self.handle_chapters_updated_signal) 

        # --- MODIFIED: Connect LOCAL signal to UI refresh handler ---
        self.model_edge_changed.connect(self.handle_model_edge_changed)
        # --- End Modification ---


    # --- Specific Handlers ---
    def handle_edge_created_signal(self, edge):
        """Adds edge to model BEFORE triggering auto-save/UI update."""
        if not self.book_graph: return
        print(f"MainWindow: Handling edge created signal for {edge.source_id}->{edge.target_id}")
        add_success = self.book_graph.add_edge(edge) # Add to model
        if add_success:
             # Trigger DataManager which calls AutoSave and emits model_edge_changed
             self.data_manager.on_edge_added(edge) 
        else:
             print(f"MainWindow: ERROR - Failed to add edge {edge.source_id}->{edge.target_id} to BookGraph model.")
             self.graph_view.remove_edge(edge.source_id, edge.target_id) # Remove visual if model add failed

    def handle_edge_deleted_signal(self, edge):
        """Removes edge from model BEFORE triggering auto-save/UI update."""
        if not self.book_graph: return
        print(f"MainWindow: Handling edge deleted signal for {edge.source_id}->{edge.target_id}")
        remove_success = self.book_graph.remove_edge(edge.source_id, edge.target_id) # Remove from model
        if remove_success:
            if self.properties_editor.current_edge and \
               self.properties_editor.current_edge.source_id == edge.source_id and \
               self.properties_editor.current_edge.target_id == edge.target_id:
                self.properties_editor.clear_display()
            # Trigger DataManager which calls AutoSave and emits model_edge_changed
            self.data_manager.on_edge_removed(edge.source_id, edge.target_id) 
            self.statusBar().showMessage(f"Deleted connection: {edge.source_id} -> {edge.target_id}", 3000)
        else:
             print(f"MainWindow: ERROR - Failed to remove edge {edge.source_id}->{edge.target_id} from BookGraph model.")

    def handle_node_updated_signal(self, node):
        """Handles node property updates from editor: updates view then triggers save."""
        if not self.book_graph: return
        print(f"MainWindow: Handling node updated signal for {node.id}")
        self.graph_view.update_node(node) # Update view first
        self.data_manager.on_node_updated(node) # Trigger save chain
        self.statusBar().showMessage(f"Node '{node.title}' updated", 3000)

    def handle_edge_updated_signal(self, edge):
        """Handles edge property updates from editor: updates view then triggers save."""
        if not self.book_graph: return
        print(f"MainWindow: Handling edge updated signal for {edge.source_id}->{edge.target_id}")
        self.graph_view.update_edge(edge) # Update view first
        self.data_manager.on_edge_updated(edge) # Trigger save chain
        self.statusBar().showMessage(f"Connection {edge.source_id}->{edge.target_id} updated", 3000)

    def handle_chapters_updated_signal(self, chapters):
        """Handles chapter updates from editor: updates UI, model, then triggers save."""
        print("MainWindow: Handling chapters updated signal...")
        self.properties_editor.set_available_chapters(chapters) 
        if self.book_graph:
             new_chapter_info = {ch['id']: ch for ch in chapters if 'id' in ch}
             self.book_graph.chapter_info = new_chapter_info 
             if chapters: self.data_manager.on_chapter_updated(chapters[0]['id']) 
             else: self.data_manager.save_book_structure(self.book_graph)
        self.statusBar().showMessage("Chapters updated", 3000)

    def handle_model_edge_changed(self, source_id, target_id):
        """Refreshes the properties editor if the currently selected node is affected."""
        print(f"MainWindow: Model edge changed ({source_id} -> {target_id}). Checking properties editor.")
        try: # Add try-except for safety
            current_node = self.properties_editor.current_node
            if current_node and (current_node.id == source_id or current_node.id == target_id):
                print(f"MainWindow: Refreshing properties editor for node {current_node.id}")
                # Get the potentially updated node object from the graph
                updated_node_obj = self.book_graph.get_node(current_node.id)
                if updated_node_obj:
                     self.properties_editor.display_node(updated_node_obj) 
                else:
                     print(f"MainWindow: Warning - Could not get updated node object for {current_node.id} during refresh.")
                     self.properties_editor.clear_display() # Clear if node somehow disappeared
        except Exception as e:
             print(f"ERROR in MainWindow.handle_model_edge_changed: {e}")
             traceback.print_exc()


    # --- Project Loading/Saving/Management Methods ---
    # (Remain the same)
    def load_project_ui_update(self):
        if not self.book_graph: return
        self.graph_view.set_book_graph(self.book_graph); self.properties_editor.set_book_graph(self.book_graph); self.properties_editor.set_available_chapters(list(self.book_graph.get_chapters().values()))
        self.setWindowTitle(f"Interactive Book Editor - {os.path.basename(self.project_path)}"); self.statusBar().showMessage(f"Project loaded: {self.project_path}", 5000); self.data_manager.enable_auto_save(True) 
    def on_new_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, "New Project Location", "", QFileDialog.ShowDirsOnly);
        if not dir_path: return
        if os.path.exists(os.path.join(dir_path, "content")) and os.listdir(dir_path): reply = QMessageBox.question(self, "Directory Not Empty", "Project 'content' directory exists or parent not empty. Continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No);
        if reply == QMessageBox.No: return
        success, book_graph = self.data_manager.create_new_project(dir_path) 
        if success and book_graph: self.project_path = dir_path; self.book_graph = book_graph; self.load_project_ui_update(); QMessageBox.information(self, "Project Created", f"New project created at {dir_path}")
        else: QMessageBox.critical(self, "Error", "Failed to create new project."); self.data_manager.enable_auto_save(False)
    def on_open_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Project", "", QFileDialog.ShowDirsOnly);
        if not dir_path: return
        if not self.data_manager.set_project_root(dir_path): QMessageBox.critical(self, "Error", "Invalid project directory."); self.data_manager.enable_auto_save(False); return
        book_graph = self.data_manager.load_book_structure()
        if not book_graph: QMessageBox.critical(self, "Error", "Failed to load book structure."); self.data_manager.enable_auto_save(False); self.project_path = None; self.book_graph = None; self.graph_view.set_book_graph(None); self.properties_editor.set_book_graph(None); self.setWindowTitle("Interactive Book Editor"); self.statusBar().showMessage("Failed to load project."); return
        self.project_path = dir_path; self.book_graph = book_graph; self.load_project_ui_update()
    def on_import_node(self):
        if not self.project_path or not self.book_graph: QMessageBox.warning(self, "Warning", "Please open or create a project first."); return
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Node", "", "JSON Files (*.json)")
        if not file_path: return
        imported_node = self.data_manager.import_node(file_path, self.book_graph) 
        if not imported_node: QMessageBox.critical(self, "Error", "Failed to import node."); return
        self.graph_view.add_node(imported_node); QMessageBox.information(self, "Node Imported", f"Node '{imported_node.title}' imported successfully.")
    def on_save(self):
        if not self.project_path or not self.book_graph: QMessageBox.warning(self, "Warning", "No project open to save."); return
        print("Manual Save: Triggering force_save_all...");
        if self.data_manager.force_save_all(): self.statusBar().showMessage("Project saved manually.", 3000)
        else: QMessageBox.critical(self, "Error", "Failed to save project.")
    def on_force_save_all(self):
        if not self.project_path or not self.book_graph: QMessageBox.warning(self, "Warning", "No project open to save."); return
        print("Force Save All: Triggering..."); 
        if self.data_manager.force_save_all(): self.statusBar().showMessage("Project force saved.", 3000)
        else: QMessageBox.critical(self, "Error", "Failed to force save project.")
    def on_delete_selected_node(self):
        selected_items = self.graph_view.scene.selectedItems(); selected_nodes = [item for item in selected_items if isinstance(item, GraphNodeItem)] 
        if not selected_nodes: self.statusBar().showMessage("No node selected for deletion.", 3000); return
        node_item = selected_nodes[0]; node_id = node_item.node.id; node_title = node_item.node.title
        if node_id == "book": QMessageBox.warning(self, "Deletion Denied", "The main 'book' node cannot be deleted."); return
        reply = QMessageBox.question(self, "Confirm Deletion", f"Delete node '{node_title}' (ID: {node_id})?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes: return
        if self.data_manager.remove_node(node_id, self.book_graph):
            self.graph_view.remove_node(node_id) 
            if self.properties_editor.current_node and self.properties_editor.current_node.id == node_id: self.properties_editor.clear_display()
            self.statusBar().showMessage(f"Node '{node_title}' deleted.", 3000)
        else: QMessageBox.warning(self, "Deletion Failed", f"Failed to delete node '{node_title}'.")

    # --- Debug Methods ---
    def debug_print_graph_structure(self):
        if not self.book_graph: print("DEBUG: No book graph loaded."); return
        print("\n=== DEBUG: BOOK GRAPH STRUCTURE ==="); print(f"Nodes ({self.book_graph.graph.number_of_nodes()}):")
        for node_id, data in self.book_graph.graph.nodes(data=True): print(f"  - {node_id}: {data.get('title', 'N/A')} (Type: {data.get('node_type', 'N/A')}, Chapter: {data.get('chapter', 'N/A')}, Pos: {data.get('position')})") 
        print(f"\nEdges ({self.book_graph.graph.number_of_edges()}):")
        for source, target, data in self.book_graph.graph.edges(data=True): print(f"  - {source} -> {target} (Type: {data.get('edge_type', 'N/A')})")
        print("\nChapters:"); 
        for chapter_id, info in self.book_graph.chapter_info.items(): print(f"  - {chapter_id}: {info.get('title', 'N/A')} (Nodes: {info.get('nodes', [])})")
        print("===================================\n")
    def debug_force_create_connection(self):
        if not self.book_graph or not self.graph_view.node_items: QMessageBox.warning(self, "Debug", "No nodes available."); return
        node_ids = list(self.graph_view.node_items.keys()); source_id, ok1 = QInputDialog.getItem(self, "Debug Connect", "Source Node:", node_ids, 0, False);
        if not ok1: return; target_id, ok2 = QInputDialog.getItem(self, "Debug Connect", "Target Node:", node_ids, 0, False);
        if not ok2: return; edge_types = ["critical-path", "character-pov", "branch-point", "concept-sequence", "related-concept", "fiction-nonfiction", "default"]; edge_type, ok3 = QInputDialog.getItem(self, "Debug Connect", "Edge Type:", edge_types, 0, False);
        if not ok3: return;
        if source_id == target_id: QMessageBox.warning(self, "Debug", "Cannot connect node to itself."); return
        edge = Edge(source_id=source_id, target_id=target_id, edge_type=edge_type)
        self.handle_edge_created_signal(edge) # Use the proper handler
        self.statusBar().showMessage(f"Debug: Edge {source_id}->{target_id} created attempt.", 3000)
    def debug_refresh_graph_view(self): print("DEBUG: Refreshing graph view..."); self.graph_view.refresh_graph(); print("DEBUG: Graph view refreshed."); self.statusBar().showMessage("Debug: Graph view refreshed.", 3000)
    def debug_create_book_node(self):
        if not self.book_graph: QMessageBox.warning(self, "Debug", "No project loaded."); return
        if self.book_graph.get_node("book"): QMessageBox.information(self, "Debug", "Book node already exists."); return
        book_node = Node(node_id="book", title="Book Properties", node_type="book", position=(50, 50), metadata={"author": "Author", "version": "1.0", "defaultStartNode": "", "defaultPOV": "Omniscient"})
        if self.book_graph.add_node(book_node): self.graph_view.add_node(book_node); self.data_manager.on_node_added(book_node); QMessageBox.information(self, "Debug", "Book node created.")
        else: QMessageBox.warning(self, "Debug", "Failed to add book node.")
    def debug_update_all_navigation(self):
        if not self.book_graph: QMessageBox.warning(self, "Debug", "No project loaded."); return
        count = self.data_manager.update_all_node_navigation(self.book_graph); QMessageBox.information(self, "Debug", f"Updated navigation for {count} nodes.")

    # --- Window Close Event ---
    def closeEvent(self, event): event.accept() 

