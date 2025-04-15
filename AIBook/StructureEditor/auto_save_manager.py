"""
SimplifiedAutoSaveManager class for the Interactive Book Editor.
REVISED: Ensures book_graph.update_node/update_edge is called *before* updating files or saving structure.
"""

import os
import json
import traceback # For detailed error logging
from path_manager import PathManager
from character_pov_manager import CharacterPOVManager
from book_structure_manager import BookStructureManager
from node_file_manager import NodeFileManager
from node_content_updater import SimplifiedNodeContentUpdater 

class SimplifiedAutoSaveManager:
    """
    Manages automatic saving of book graph changes. Updates the BookGraph model
    before triggering saves or file updates.
    """
    
    def __init__(self, path_manager=None, character_pov_manager=None):
        """Initialize a new SimplifiedAutoSaveManager instance."""
        self.path_manager = path_manager or PathManager()
        self.character_pov_manager = character_pov_manager or CharacterPOVManager()
        self.book_structure_manager = BookStructureManager(self.path_manager, self.character_pov_manager)
        self.node_file_manager = NodeFileManager(self.path_manager, self.character_pov_manager)
        self.node_content_updater = SimplifiedNodeContentUpdater(self.path_manager) 
        self.book_graph = None
        self.auto_save_enabled = True
    
    def set_book_graph(self, book_graph):
        """Set the book graph to monitor."""
        self.book_graph = book_graph

    def enable_auto_save(self, enabled=True):
        """Enable or disable auto-saving."""
        self.auto_save_enabled = enabled
        print(f"Auto-save {'enabled' if enabled else 'disabled'}.")

    def _save_structure(self, context=""):
        """Internal helper to save the main book structure."""
        if not self.book_graph:
            print(f"AutoSave ({context}): Cannot save structure, book_graph not set.")
            return False
        print(f"AutoSave ({context}): Saving book structure...")
        # Pass the current graph state to the saver
        success = self.book_structure_manager.save_book_structure(self.book_graph) 
        if success:
            print(f"AutoSave ({context}): Book structure saved successfully.")
        else:
            print(f"AutoSave ({context}): ERROR saving book structure.")
        return success

    def on_node_added(self, node):
        """Handle node addition."""
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling node added - {node.id}")
        try:
            # Node is already added to book_graph by MainWindow/DataManager logic
            # 1. Ensure node file exists/is created
            self.node_file_manager.save_node_content_file(
                node, self.book_structure_manager.get_original_structure_data()
            )
            # 2. Update navigation for all nodes (simpler for now)
            self.node_content_updater.update_all_node_navigation(self.book_graph)
            # 3. Save the structure
            self._save_structure(f"Node Added {node.id}")
            return True
        except Exception as e:
            print(f"ERROR in on_node_added for {node.id}: {e}")
            traceback.print_exc()
            return False

    def on_node_updated(self, node):
        """Handle node updates (position, properties)."""
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling node updated - {node.id}")
        try:
            # --- Step 1: Update the BookGraph Model ---
            # Ensure the graph object itself reflects the changes passed via the node object
            print(f"AutoSave: Updating node {node.id} in BookGraph model...")
            update_success = self.book_graph.update_node(node)
            if not update_success:
                 print(f"AutoSave: WARNING - Failed to update node {node.id} in BookGraph model.")
                 # If the graph update fails, saving the structure might use stale data

            # --- Step 2: Update Node Content File ---
            # (Logic remains the same - reads updated 'node' object)
            if node.file_path and node.node_type != "book":
                full_path = self.path_manager.get_full_content_path(node.file_path)
                if full_path and os.path.exists(full_path):
                    try:
                        with open(full_path, 'r+', encoding='utf-8') as f:
                            content = json.load(f)
                            content.setdefault("data", {})
                            content.setdefault("metadata", {})
                            content["nodeType"] = node.node_type 
                            content["data"]["label"] = node.title 
                            if node.chapter: content["metadata"]["chapter"] = node.chapter
                            elif "chapter" in content.get("metadata", {}): del content["metadata"]["chapter"]
                            if "povCharacter" in node.metadata: content["metadata"]["povCharacter"] = node.metadata["povCharacter"]
                            f.seek(0)
                            json.dump(content, f, indent=2, ensure_ascii=False)
                            f.truncate()
                    except Exception as file_e:
                        print(f"AutoSave: WARNING - Failed to update content file for {node.id}: {file_e}")

            # --- Step 3: Update Navigation ---
            # Reads from the updated graph model
            self.node_content_updater.update_all_node_navigation(self.book_graph)

            # --- Step 4: Save Overall Book Structure ---
            # Reads from the updated graph model
            self._save_structure(f"Node Updated {node.id}")
            
            return True
        except Exception as e:
            print(f"ERROR in on_node_updated for {node.id}: {e}")
            traceback.print_exc()
            return False

    def on_node_removed(self, node_id):
        """Handle node removal."""
        # Assumes node is already removed from book_graph model by DataManager.remove_node
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling node removed - {node_id}")
        try:
            # Update navigation based on the graph *after* node removal
            self.node_content_updater.update_all_node_navigation(self.book_graph)
            # Save the structure reflecting the removal
            self._save_structure(f"Node Removed {node_id}")
            return True
        except Exception as e:
            print(f"ERROR in on_node_removed for {node_id}: {e}")
            traceback.print_exc()
            return False

    def on_edge_added(self, edge):
        """Handle edge addition."""
        # Assumes edge is already added to book_graph model
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling edge added - {edge.source_id} -> {edge.target_id} ({edge.edge_type})")
        try:
            # Update navigation based on the new edge
            self.node_content_updater.update_node_navigation(edge.source_id, self.book_graph)
            self.node_content_updater.update_node_navigation(edge.target_id, self.book_graph)
            if edge.edge_type == "critical-path": # Update neighbors too
                 prev = self.node_content_updater._get_critical_path_neighbor(edge.source_id, self.book_graph, "previous")
                 next_ = self.node_content_updater._get_critical_path_neighbor(edge.target_id, self.book_graph, "next")
                 if prev: self.node_content_updater.update_node_navigation(prev, self.book_graph)
                 if next_: self.node_content_updater.update_node_navigation(next_, self.book_graph)
            # Save structure reflecting the new edge
            self._save_structure(f"Edge Added {edge.source_id}->{edge.target_id}")
            return True
        except Exception as e:
            print(f"ERROR in on_edge_added for {edge.source_id}->{edge.target_id}: {e}")
            traceback.print_exc()
            return False

    def on_edge_updated(self, edge):
        """Handle edge updates (type, metadata)."""
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling edge updated - {edge.source_id} -> {edge.target_id} (Type: {edge.edge_type}, Meta: {edge.metadata})")
        try:
            # --- Step 1: Update the BookGraph Model ---
            print(f"AutoSave: Updating edge {edge.source_id}->{edge.target_id} in BookGraph model")
            update_success = self.book_graph.update_edge(edge) # Ensure graph model has latest edge data
            if not update_success:
                 print(f"AutoSave: WARNING - Failed to update edge {edge.source_id}->{edge.target_id} in BookGraph model.")

            # --- Step 2: Update Navigation ---
            # Rerun navigation updates as type/metadata might affect it
            self.node_content_updater.update_all_node_navigation(self.book_graph)

            # --- Step 3: Save Structure ---
            # Reads the updated graph model
            self._save_structure(f"Edge Updated {edge.source_id}->{edge.target_id}")
            return True
        except Exception as e:
            print(f"ERROR in on_edge_updated for {edge.source_id}->{edge.target_id}: {e}")
            traceback.print_exc()
            return False

    def on_edge_removed(self, source_id, target_id):
        """Handle edge removal."""
        # Assumes edge is already removed from book_graph model
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling edge removed - {source_id} -> {target_id}")
        try:
            # Update navigation based on graph *after* edge removal
            self.node_content_updater.update_all_node_navigation(self.book_graph)
            # Save structure reflecting removal
            self._save_structure(f"Edge Removed {source_id}->{target_id}")
            return True
        except Exception as e:
            print(f"ERROR in on_edge_removed for {source_id}->{target_id}: {e}")
            traceback.print_exc()
            return False

    def on_chapter_updated(self, chapter_id):
        """Handle chapter updates."""
        # Assumes chapter info is updated in book_graph model by MainWindow
        if not self.auto_save_enabled or not self.book_graph: return False
        print(f"AutoSave: Handling chapter updated - {chapter_id}")
        try:
            # Update relevant node files if needed (e.g., their chapter metadata)
            self.node_content_updater.update_all_node_navigation(self.book_graph)
            # Save the structure reflecting chapter changes
            self._save_structure(f"Chapter Updated {chapter_id}")
            return True
        except Exception as e:
            print(f"ERROR in on_chapter_updated for {chapter_id}: {e}")
            traceback.print_exc()
            return False
    
    def force_save_all(self):
        """Force save all nodes and the book structure."""
        # (Implementation remains the same as previous version)
        if not self.book_graph: print("ForceSave: Cannot save, book_graph not set."); return False
        print("ForceSave: Starting forced save..."); success = True
        try:
            nodes = self.book_graph.get_all_nodes()
            print(f"ForceSave: Updating {len(nodes)} nodes in graph model...")
            for node in nodes: self.book_graph.update_node(node) # Ensure graph model is sync'd
            print(f"ForceSave: Checking/Saving content for {len(nodes)} nodes...")
            for node in nodes:
                if node.node_type != "book":
                    self.node_file_manager.save_node_content_file(node, self.book_structure_manager.get_original_structure_data())
                    if node.file_path:
                         full_path = self.path_manager.get_full_content_path(node.file_path)
                         if full_path and os.path.exists(full_path):
                              try:
                                   with open(full_path, 'r+', encoding='utf-8') as f:
                                        content = json.load(f); content.setdefault("data", {}); content.setdefault("metadata", {})
                                        content["nodeType"] = node.node_type; content["data"]["label"] = node.title 
                                        if node.chapter: content["metadata"]["chapter"] = node.chapter
                                        elif "chapter" in content.get("metadata", {}): del content["metadata"]["chapter"]
                                        if "povCharacter" in node.metadata: content["metadata"]["povCharacter"] = node.metadata["povCharacter"]
                                        f.seek(0); json.dump(content, f, indent=2, ensure_ascii=False); f.truncate()
                              except Exception as file_e: print(f"ForceSave: WARNING - Failed to update content file for {node.id}: {file_e}")
            print("ForceSave: Updating navigation data for all nodes...")
            self.node_content_updater.update_all_node_navigation(self.book_graph)
            print("ForceSave: Saving main book structure file...")
            if not self.book_structure_manager.save_book_structure(self.book_graph): success = False
            if success: print("ForceSave: Completed successfully.")
            else: print("ForceSave: ERROR saving main book structure file.")
            return success
        except Exception as e: print(f"ERROR in force_save_all: {e}"); traceback.print_exc(); return False

