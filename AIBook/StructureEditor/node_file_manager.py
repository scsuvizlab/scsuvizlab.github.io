"""
NodeFileManager class for the Interactive Book Editor.
REVISED: Ensures povCharacter metadata is correctly parsed and stored during import.
"""

import os
import json
import shutil
import traceback # For detailed error logging
from node import Node
from path_manager import PathManager
from character_pov_manager import CharacterPOVManager

class NodeFileManager:
    """
    Manages node content files.
    """
    
    def __init__(self, path_manager=None, character_pov_manager=None):
        """Initialize a new NodeFileManager instance."""
        self.path_manager = path_manager or PathManager()
        self.character_pov_manager = character_pov_manager or CharacterPOVManager()
    
    def save_node_content_file(self, node, structure_data=None):
        """Save a node's content to its JSON file."""
        # (Implementation remains the same as previous version)
        if node.node_type == "book": return False
        try:
            file_path = node.file_path
            is_pov_node = self.character_pov_manager.is_character_pov_node(node.id)
            if not file_path:
                file_path = self.path_manager.get_default_file_path(node, is_pov_node)
                node.file_path = file_path
            
            file_path = self.path_manager.normalize_path(file_path)
            full_path = self.path_manager.get_full_content_path(file_path)
            if not full_path: return False
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            if not os.path.exists(full_path):
                character_name = None
                base_node_id = None
                if is_pov_node:
                    character_name = self.character_pov_manager.get_character_from_pov_node(node.id)
                    base_node_id = self.character_pov_manager.get_base_node_from_pov(node.id)
                
                node_content = {
                    "id": node.id, "nodeId": node.id, "nodeType": node.node_type,
                    "data": { "label": node.title, "content": f"<p>Content for {node.title}</p>",
                              "chapterTitle": "Chapter", "subtitle": f"({node.node_type})",
                              "location": "", "timeline": "", "tags": [] },
                    "metadata": { "author": "Author", "lastModified": "2023-01-01T00:00:00Z",
                                  "povCharacter": character_name if is_pov_node else "Omniscient" },
                    "navigation": { "next": None, "previous": None, "alternateVersions": [], "relatedNonFiction": [] }
                }
                if is_pov_node and base_node_id:
                    node_content["navigation"]["alternateVersions"].append({"povCharacter": "Omniscient", "nodeId": base_node_id})
                elif structure_data and "characterPOVs" in structure_data and node.id in structure_data["characterPOVs"]:
                     povs = structure_data["characterPOVs"][node.id]
                     for pov in povs: node_content["navigation"]["alternateVersions"].append({"povCharacter": pov["character"], "nodeId": pov["nodeId"]})
                
                with open(full_path, 'w', encoding='utf-8') as f: json.dump(node_content, f, indent=2, ensure_ascii=False)
                print(f"Created node content file: {full_path}")
            return True
        except Exception as e:
            print(f"Error saving node content file {node.id}: {e}")
            traceback.print_exc()
            return False

    def load_node_content_file(self, file_path):
        """Load a node's content from its JSON file."""
        # (Implementation remains the same as previous version)
        try:
            full_path = self.path_manager.get_full_content_path(file_path)
            if not full_path or not os.path.isfile(full_path): return None
            with open(full_path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e:
            print(f"Error loading node content file {file_path}: {e}")
            traceback.print_exc()
            return None
    
    def import_node(self, file_path, book_graph, structure_data=None):
        """
        Import a node from an external JSON file. Ensures povCharacter metadata is stored.
        """
        if not os.path.isfile(file_path): return None
        print(f"NodeFileManager: Importing node from {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                node_data = json.load(f)
            
            # --- Create Node object ---
            # Use Node.from_dict which handles basic parsing
            node = Node.from_dict(node_data) 
            
            # --- Explicitly check for and store povCharacter ---
            # Node.from_dict puts extra keys in metadata, but let's be sure
            # Check both metadata and data sections from the source file
            pov_char_meta = node_data.get("metadata", {}).get("povCharacter")
            pov_char_data = node_data.get("data", {}).get("povCharacter")
            pov_character = pov_char_meta or pov_char_data
            
            if pov_character:
                 node.metadata["povCharacter"] = pov_character
                 print(f"NodeFileManager: Stored povCharacter '{pov_character}' for node {node.id}")
            elif self.character_pov_manager.is_character_pov_node(node.id):
                 # Try to infer if marked as POV node but missing explicit metadata
                 inferred_char = self.character_pov_manager.get_character_from_pov_node(node.id)
                 if inferred_char:
                      node.metadata["povCharacter"] = inferred_char
                      print(f"NodeFileManager: Inferred and stored povCharacter '{inferred_char}' for node {node.id}")


            # --- Handle ID conflicts ---
            original_id = node.id
            if node.id in book_graph.graph.nodes:
                base_id = node.id
                counter = 1
                while f"{base_id}_{counter}" in book_graph.graph.nodes: counter += 1
                node.id = f"{base_id}_{counter}"
                print(f"NodeFileManager: ID conflict. Renamed imported node from '{original_id}' to '{node.id}'")
                # Update ID in node_data if we copy it later? Less critical if we use the Node object.

            # --- Add Node to Graph ---
            book_graph.add_node(node)
            
            # --- Copy File and Set Path ---
            if self.path_manager.project_root:
                is_pov = self.character_pov_manager.is_character_pov_node(node.id) # Use the potentially renamed ID
                target_rel_path = self.path_manager.get_default_file_path(node, is_pov)
                target_full_path = self.path_manager.get_full_content_path(target_rel_path)
                
                if target_full_path:
                    target_dir = os.path.dirname(target_full_path)
                    if self.path_manager.ensure_directory_exists(target_dir):
                         # Use the potentially renamed node ID for the filename
                         final_filename = f"{node.id}.json"
                         final_target_path = os.path.join(target_dir, final_filename)
                         final_rel_path = self.path_manager.join_paths(os.path.basename(target_dir), final_filename)
                         if is_pov: # Adjust relative path for POV subdirectory
                              final_rel_path = self.path_manager.join_paths("fiction", "character_povs", final_filename)

                         try:
                              shutil.copy2(file_path, final_target_path) # Copy original file to new location/name
                              node.file_path = self.path_manager.normalize_path(final_rel_path)
                              book_graph.update_node(node) # Update graph with correct file path
                              print(f"NodeFileManager: Copied node file to {final_target_path}")
                         except Exception as copy_e:
                              print(f"NodeFileManager: ERROR copying file to {final_target_path}: {copy_e}")
                              # Should we remove the node from the graph if copy fails? Maybe.
                              book_graph.remove_node(node.id)
                              return None
                    else:
                         print(f"NodeFileManager: ERROR ensuring target directory exists: {target_dir}")
                         book_graph.remove_node(node.id)
                         return None
                else:
                     print("NodeFileManager: ERROR could not determine target path.")
                     book_graph.remove_node(node.id)
                     return None

            # --- Update Book Structure Data (Optional - passed from DataManager) ---
            if structure_data:
                 # Update criticalPath if applicable
                 if "criticalPath" in structure_data and not self.character_pov_manager.is_character_pov_node(node.id):
                      if not any(n.get("id") == node.id for n in structure_data["criticalPath"]):
                           structure_data["criticalPath"].append(node.to_dict()) # Add basic node info

                 # Update characterPOVs if applicable
                 if self.character_pov_manager.is_character_pov_node(node.id):
                      base_node_id = self.character_pov_manager.get_base_node_from_pov(node.id)
                      character_name = node.metadata.get("povCharacter") # Use stored metadata
                      if base_node_id and character_name:
                           structure_data.setdefault("characterPOVs", {}).setdefault(base_node_id, [])
                           if not any(pov.get("nodeId") == node.id for pov in structure_data["characterPOVs"][base_node_id]):
                                structure_data["characterPOVs"][base_node_id].append({
                                    "character": character_name, "nodeId": node.id, "filePath": node.file_path
                                })
            
            print(f"NodeFileManager: Node {node.id} imported successfully.")
            return node
            
        except Exception as e:
            print(f"ERROR importing node from {file_path}: {e}")
            traceback.print_exc()
            # Clean up if node was partially added?
            if 'node' in locals() and node.id in book_graph.graph.nodes:
                 book_graph.remove_node(node.id)
            return None

    def remove_node(self, node_id, book_graph, structure_data=None):
        """Remove a node from the book structure graph."""
        # (Implementation remains the same as previous version)
        if not book_graph or not node_id: return False
        try:
            node = book_graph.get_node(node_id)
            if not node: return False
            if node.node_type == "book": return False
            
            is_pov_node = self.character_pov_manager.is_character_pov_node(node_id)
            base_node_id = self.character_pov_manager.get_base_node_from_pov(node_id) if is_pov_node else None
            
            removed = book_graph.remove_node(node_id)
            if not removed: return False
            
            if structure_data:
                # Update criticalPath
                structure_data["criticalPath"] = [n for n in structure_data.get("criticalPath", []) if isinstance(n, dict) and n.get("id") != node_id]
                # Update node_positions
                structure_data.get("node_positions", {}).pop(node_id, None)
                # Update tracks
                for track in structure_data.get("tracks", {}).values():
                    if "nodeSequence" in track and node_id in track["nodeSequence"]: track["nodeSequence"].remove(node_id)
                    if track.get("startNode") == node_id: track["startNode"] = ""
                # Update characterPOVs
                if is_pov_node and base_node_id and base_node_id in structure_data.get("characterPOVs", {}):
                    structure_data["characterPOVs"][base_node_id] = [pov for pov in structure_data["characterPOVs"][base_node_id] if pov.get("nodeId") != node_id]
                    if not structure_data["characterPOVs"][base_node_id]: del structure_data["characterPOVs"][base_node_id]
                elif not is_pov_node: structure_data.get("characterPOVs", {}).pop(node_id, None)
                # Update relatedContent
                if "relatedContent" in structure_data:
                    for key in list(structure_data["relatedContent"].keys()):
                        if node_id in structure_data["relatedContent"][key]: structure_data["relatedContent"][key].remove(node_id)
                        if not structure_data["relatedContent"][key]: del structure_data["relatedContent"][key]
                    structure_data["relatedContent"].pop(node_id, None)
                # Update chapters
                for chapter in structure_data.get("chapters", []):
                    if "nodes" in chapter and node_id in chapter["nodes"]: chapter["nodes"].remove(node_id)
                    if chapter.get("startNode") == node_id: chapter["startNode"] = ""
                # Update defaultStartNode
                if structure_data.get("defaultStartNode") == node_id: structure_data["defaultStartNode"] = ""
            
            print(f"NodeFileManager: Node {node_id} removed from model.")
            return True
        except Exception as e:
            print(f"ERROR removing node {node_id}: {e}")
            traceback.print_exc()
            return False
