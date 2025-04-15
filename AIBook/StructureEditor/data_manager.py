"""
DataManager class for the Interactive Book Editor.
REVISED: Removed pyqtSignal definition. Added signal_emitter reference
         to trigger signal emission on the owning QObject (e.g., MainWindow).
"""

import os 
import traceback 
# Removed pyqtSignal import as signal is defined elsewhere
from path_manager import PathManager
from character_pov_manager import CharacterPOVManager
from project_manager import ProjectManager
from book_structure_manager import BookStructureManager
from node_file_manager import NodeFileManager
from auto_save_manager import SimplifiedAutoSaveManager
from node_content_updater import SimplifiedNodeContentUpdater

class DataManager:
    """
    Facade that provides a unified interface to the specialized manager classes.
    Manages the shared PathManager instance and project state.
    Does NOT define signals itself, but can trigger them on an emitter.
    """
    
    def __init__(self):
        """Initialize a new DataManager instance."""
        print("DataManager: Initializing...")
        self.path_manager = PathManager() 
        self.character_pov_manager = CharacterPOVManager()
        self.project_manager = ProjectManager() 
        self.book_structure_manager = BookStructureManager(self.path_manager, self.character_pov_manager)
        self.node_file_manager = NodeFileManager(self.path_manager, self.character_pov_manager)
        self.node_content_updater = SimplifiedNodeContentUpdater(self.path_manager)
        self.auto_save_manager = SimplifiedAutoSaveManager(self.path_manager, self.character_pov_manager)
        
        self.project_root = None
        self.current_book_graph = None 
        self.signal_emitter = None # Reference to the object that will emit signals (e.g., MainWindow)
        print("DataManager: Initialization complete.")

    # --- NEW: Method to set the signal emitter ---
    def set_signal_emitter(self, emitter):
        """
        Sets the object responsible for emitting signals based on DataManager actions.
        The emitter object must have the required signals (e.g., model_edge_changed).
        
        Args:
            emitter: An object (usually a QObject like MainWindow) that has the necessary signals.
        """
        print(f"DataManager: Setting signal emitter to {emitter}")
        self.signal_emitter = emitter
    # --- End New Method ---
        
    # --- Project Manager Delegation ---
    def set_project_root(self, root_path):
        print(f"DataManager: Setting project root to: {root_path}")
        if not isinstance(root_path, str): print("DataManager: ERROR - Invalid root_path type."); self.project_root = None; self.path_manager.set_project_root(None); return False
        abs_path = os.path.abspath(root_path)
        if os.path.exists(abs_path) and not os.path.isdir(abs_path): print(f"DataManager: ERROR - Path exists but is not a directory: {abs_path}"); self.project_root = None; self.path_manager.set_project_root(None); return False
        self.project_root = abs_path; self.path_manager.set_project_root(self.project_root); print(f"DataManager: Project root set successfully to {self.project_root}"); return True

    def create_new_project(self, root_path):
        print(f"DataManager: Handling create_new_project for path: {root_path}")
        success, book_graph = self.project_manager.create_new_project(root_path)
        if success and book_graph:
            print("DataManager: Project structure created by ProjectManager.")
            if not self.set_project_root(root_path): print("DataManager: ERROR - Failed to set project root after structure creation."); return False, None 
            print("DataManager: Saving initial book-structure.json...")
            save_success = self.book_structure_manager.save_book_structure(book_graph)
            if not save_success: print("DataManager: ERROR - Failed to save initial book-structure.json."); return False, None 
            print("DataManager: Initial book-structure.json saved.")
            self.current_book_graph = book_graph; self.auto_save_manager.set_book_graph(book_graph) 
            _, _ = self.book_structure_manager.load_book_structure() 
            if not self.book_structure_manager.get_original_structure_data(): print("DataManager: WARNING - Could not load original structure data after project creation.")
            print("DataManager: create_new_project completed successfully."); return True, book_graph 
        else: print("DataManager: ProjectManager failed to create project structure."); self.project_root = None; self.current_book_graph = None; self.auto_save_manager.set_book_graph(None); return False, None 

    # --- Path Manager Delegation ---
    def get_book_structure_path(self): return self.path_manager.get_book_structure_path()
    def normalize_path(self, path): return self.path_manager.normalize_path(path)

    # --- Character POV Manager Delegation ---
    def is_character_pov_node(self, node_id): return self.character_pov_manager.is_character_pov_node(node_id)
    def get_character_from_pov_node(self, node_id): return self.character_pov_manager.get_character_from_pov_node(node_id)
    def get_base_node_from_pov(self, pov_node_id): return self.character_pov_manager.get_base_node_from_pov(pov_node_id)

    # --- Book Structure Manager Delegation ---
    def load_book_structure(self):
        if not self.project_root: print("DataManager: Cannot load structure, project root not set."); return None
        print("DataManager: Delegating load_book_structure...")
        book_graph, _ = self.book_structure_manager.load_book_structure() 
        if book_graph: print("DataManager: Book structure loaded successfully."); self.current_book_graph = book_graph; self.auto_save_manager.set_book_graph(book_graph) 
        else: print("DataManager: Failed to load book structure."); self.current_book_graph = None; self.auto_save_manager.set_book_graph(None)
        return book_graph 

    def save_book_structure(self, book_graph):
        if not self.project_root: print("DataManager: Cannot save structure, project root not set."); return False
        print("DataManager: Delegating save_book_structure...")
        if book_graph != self.current_book_graph: print("DataManager: WARNING - Saving a different book graph instance than the one managed.")
        return self.book_structure_manager.save_book_structure(book_graph)

    # --- Node File Manager Delegation ---
    def save_node_content_file(self, node):
        if not self.project_root: return False 
        original_data = self.book_structure_manager.get_original_structure_data()
        return self.node_file_manager.save_node_content_file(node, original_data)
    
    def remove_node(self, node_id, book_graph):
        if not self.project_root: return False 
        print(f"DataManager: Delegating remove_node for {node_id}")
        result = book_graph.remove_node(node_id) 
        if result: self.auto_save_manager.on_node_removed(node_id) 
        else: print(f"DataManager: BookGraph node removal failed for {node_id}")
        return result
    
    def import_node(self, file_path, book_graph):
        if not self.project_root: return None 
        print(f"DataManager: Delegating import_node for {file_path}")
        original_data = self.book_structure_manager.get_original_structure_data()
        node = self.node_file_manager.import_node(file_path, book_graph, original_data) 
        if node and book_graph == self.current_book_graph: self.auto_save_manager.on_node_added(node) 
        elif not node: print(f"DataManager: Node import failed for {file_path}")
        return node

    # --- Node Content Updater Delegation ---
    def update_node_navigation(self, node_id, book_graph):
        if not self.project_root: return False 
        return self.node_content_updater.update_node_navigation(node_id, book_graph)
    def update_all_node_navigation(self, book_graph):
        if not self.project_root: return 0 
        return self.node_content_updater.update_all_node_navigation(book_graph)
    def update_critical_path(self, book_graph):
        if not self.project_root: return False 
        return self.node_content_updater.update_critical_path_nodes(book_graph)

    # --- Auto-save Delegation ---
    def enable_auto_save(self, enabled=True): self.auto_save_manager.enable_auto_save(enabled)
    def on_node_added(self, node): self.auto_save_manager.on_node_added(node)
    def on_node_updated(self, node): self.auto_save_manager.on_node_updated(node)
    # on_node_removed is handled via self.remove_node

    def on_edge_added(self, edge):
        """Handle edge addition for auto-save AND trigger signal on emitter."""
        self.auto_save_manager.on_edge_added(edge)
        # --- Trigger signal on emitter ---
        if self.signal_emitter and hasattr(self.signal_emitter, 'model_edge_changed'):
            print("DataManager: Triggering model_edge_changed signal emission.")
            self.signal_emitter.model_edge_changed.emit(edge.source_id, edge.target_id)
        else:
             print("DataManager: Warning - Signal emitter not set or missing signal for on_edge_added.")
        # --- End Trigger ---
    
    def on_edge_updated(self, edge):
        """Handle edge update for auto-save."""
        self.auto_save_manager.on_edge_updated(edge)
        # Optionally trigger signal here too if UI needs refresh on edge type/metadata change
        if self.signal_emitter and hasattr(self.signal_emitter, 'model_edge_changed'):
             print("DataManager: Triggering model_edge_changed signal emission (on update).")
             self.signal_emitter.model_edge_changed.emit(edge.source_id, edge.target_id)

    
    def on_edge_removed(self, source_id, target_id):
        """Handle edge removal for auto-save AND trigger signal on emitter."""
        self.auto_save_manager.on_edge_removed(source_id, target_id)
        # --- Trigger signal on emitter ---
        if self.signal_emitter and hasattr(self.signal_emitter, 'model_edge_changed'):
            print("DataManager: Triggering model_edge_changed signal emission.")
            self.signal_emitter.model_edge_changed.emit(source_id, target_id)
        else:
             print("DataManager: Warning - Signal emitter not set or missing signal for on_edge_removed.")
        # --- End Trigger ---

    def on_chapter_updated(self, chapter_id): self.auto_save_manager.on_chapter_updated(chapter_id)
    def force_save_all(self):
        if not self.project_root: return False 
        return self.auto_save_manager.force_save_all()

