"""
BookStructureManager class for the Interactive Book Editor.
REVISED: 
- Explicitly creates Node objects for character POVs during loading.
- Ensures chapter assignment and node types are robustly loaded and saved.
"""

import os
import json
import copy
import traceback # For detailed error logging
from node import Node, Edge
from book_graph import BookGraph
from path_manager import PathManager
from character_pov_manager import CharacterPOVManager

class BookStructureManager:
    """
    Manages the book structure data. Responsible for loading from and saving to 
    the book-structure.json file.
    """
    
    def __init__(self, path_manager=None, character_pov_manager=None):
        """Initialize a new BookStructureManager instance."""
        self.path_manager = path_manager or PathManager()
        self.character_pov_manager = character_pov_manager or CharacterPOVManager()
        self.original_structure_data = None 

    def load_book_structure(self):
        """
        Load the book structure from book-structure.json. Creates Node objects
        for both critical path and character POV nodes found in the structure.
        """
        structure_path = self.path_manager.get_book_structure_path()
        if not structure_path or not os.path.isfile(structure_path):
            print(f"BookStructureManager: Structure file not found at {structure_path}")
            return None, None
        print(f"BookStructureManager: Loading structure from {structure_path}")
        try:
            with open(structure_path, 'r', encoding='utf-8') as f: structure_data = json.load(f)
            self.original_structure_data = copy.deepcopy(structure_data)
            
            # --- Initialize BookGraph ---
            book_graph = BookGraph()
            
            # Set book metadata early
            book_graph.metadata = {"title": structure_data.get("title", "Book Title"), "author": structure_data.get("author", "Author Name"),
                                   "version": structure_data.get("version", "1.0"), "defaultStartNode": structure_data.get("defaultStartNode", ""),
                                   "defaultPOV": structure_data.get("defaultPOV", "Omniscient")}

            # --- Load Node Positions ---
            node_positions = structure_data.get("node_positions", {})

            # --- Create Nodes from criticalPath ---
            print(f"BookStructureManager: Loading {len(structure_data.get('criticalPath', []))} nodes from criticalPath...")
            nodes_created = set() # Keep track of nodes already created
            for node_data in structure_data.get("criticalPath", []):
                node_id = node_data.get("id")
                if not node_id:
                    print("BookStructureManager: Warning - Skipping node in criticalPath with missing ID.")
                    continue
                
                position = node_positions.get(node_id, (0.0, 0.0))
                # Ensure position is correctly formatted tuple of floats
                if isinstance(position, (list, tuple)) and len(position) == 2:
                     try: position = (float(position[0]), float(position[1]))
                     except (ValueError, TypeError): position = (0.0, 0.0)
                else: position = (0.0, 0.0)

                node = Node(
                    node_id=node_id,
                    title=node_data.get("title", node_id),
                    node_type=node_data.get("type", "fiction"), # Get type from criticalPath entry
                    chapter=node_data.get("chapter"), # Get chapter from criticalPath entry
                    file_path=self.path_manager.normalize_path(node_data.get("filePath")),
                    position=position,
                    metadata={} # Start with empty metadata, specific things added later if needed
                )
                book_graph.add_node(node)
                nodes_created.add(node_id)

            # --- Create Nodes from characterPOVs (if not already created) ---
            print(f"BookStructureManager: Loading {len(structure_data.get('characterPOVs', {}))} character POV definitions...")
            for base_node_id, pov_list in structure_data.get("characterPOVs", {}).items():
                for pov_data in pov_list:
                    pov_node_id = pov_data.get("nodeId")
                    character_name = pov_data.get("character")
                    file_path = self.path_manager.normalize_path(pov_data.get("filePath"))
                    
                    if not pov_node_id:
                         print(f"BookStructureManager: Warning - Skipping POV entry for base {base_node_id} with missing nodeId.")
                         continue
                         
                    if pov_node_id not in nodes_created:
                        print(f"BookStructureManager: Creating node object for POV node {pov_node_id}...")
                        position = node_positions.get(pov_node_id, (0.0, 0.0)) # Get position if available
                        if isinstance(position, (list, tuple)) and len(position) == 2:
                             try: position = (float(position[0]), float(position[1]))
                             except (ValueError, TypeError): position = (0.0, 0.0)
                        else: position = (0.0, 0.0)

                        # Try to infer chapter from base node if possible
                        base_node = book_graph.get_node(base_node_id)
                        pov_chapter = base_node.chapter if base_node else None

                        pov_node = Node(
                            node_id=pov_node_id,
                            # Infer title, default to ID if base node not found yet
                            title=f"{base_node.title} ({character_name} POV)" if base_node else f"{pov_node_id}",
                            node_type="character_pov", # Explicitly set type
                            chapter=pov_chapter, # Inherit chapter
                            file_path=file_path,
                            position=position,
                            metadata={"povCharacter": character_name} # Store POV character in metadata
                        )
                        book_graph.add_node(pov_node)
                        nodes_created.add(pov_node_id)
                    else:
                         # Node already exists (e.g., was also in criticalPath), ensure metadata is added
                         existing_node = book_graph.get_node(pov_node_id)
                         if existing_node and "povCharacter" not in existing_node.metadata:
                              existing_node.metadata["povCharacter"] = character_name
                              book_graph.update_node(existing_node) # Update graph model


            # --- Create 'book' node ---
            if not book_graph.get_node("book"):
                print("BookStructureManager: Creating missing 'book' node.")
                book_node_meta = {k: v for k, v in book_graph.metadata.items() if k != 'title'}
                book_node = Node(node_id="book", title=book_graph.metadata["title"], node_type="book", position=(100, 100), metadata=book_node_meta)
                book_graph.add_node(book_node)
            
            # --- Load Edges ---
            print(f"BookStructureManager: Loading {len(structure_data.get('edges', []))} edges...")
            for edge_data in structure_data.get("edges", []):
                 try:
                      # Ensure source and target exist before adding edge
                      source_id = edge_data.get("source")
                      target_id = edge_data.get("target")
                      if source_id in book_graph.graph.nodes and target_id in book_graph.graph.nodes:
                           edge = Edge.from_dict(edge_data)
                           book_graph.add_edge(edge)
                      else:
                           print(f"BookStructureManager: Warning - Skipping edge due to missing node(s): {source_id} -> {target_id}")
                 except ValueError as e:
                      print(f"BookStructureManager: Warning - Skipping invalid edge data: {edge_data} ({e})")


            # --- Load Chapters ---
            print(f"BookStructureManager: Loading {len(structure_data.get('chapters', []))} chapter definitions...")
            for chapter_data in structure_data.get("chapters", []):
                if "id" in chapter_data and "title" in chapter_data:
                    book_graph.add_chapter(chapter_data["id"], chapter_data["title"], chapter_data.get("description"))
                    if "startNode" in chapter_data: book_graph.chapter_info[chapter_data["id"]]["startNode"] = chapter_data["startNode"]
                    # Chapter node lists will be rebuilt on save based on node.chapter attribute

            print(f"BookStructureManager: Load successful. Graph has {book_graph.graph.number_of_nodes()} nodes and {book_graph.graph.number_of_edges()} edges.")
            return book_graph, self.original_structure_data
            
        except Exception as e:
            print(f"ERROR loading book structure: {e}")
            traceback.print_exc()
            self.original_structure_data = None 
            return None, None
    
    def save_book_structure(self, book_graph):
        """
        Save the book structure to book-structure.json.
        Rebuilds essential sections directly from the current BookGraph state.
        """
        structure_path = self.path_manager.get_book_structure_path()
        if not structure_path: print("BookStructureManager: Cannot save, project root not set."); return False
        print(f"BookStructureManager: Saving structure to {structure_path}")
        content_dir = os.path.dirname(structure_path)
        if not self.path_manager.ensure_directory_exists(content_dir): print(f"BookStructureManager: ERROR - Could not ensure content dir exists: {content_dir}"); return False

        try:
            structure_data = {}
            book_node = book_graph.get_node("book")
            if book_node:
                structure_data["title"] = book_node.title
                structure_data["author"] = book_node.metadata.get("author", "Author Name")
                structure_data["version"] = book_node.metadata.get("version", "1.0")
                structure_data["defaultStartNode"] = book_node.metadata.get("defaultStartNode", "")
                structure_data["defaultPOV"] = book_node.metadata.get("defaultPOV", "Omniscient")
            else: # Fallback
                structure_data["title"] = book_graph.metadata.get("title", "Book Title"); structure_data["author"] = book_graph.metadata.get("author", "Author Name"); structure_data["version"] = book_graph.metadata.get("version", "1.0"); structure_data["defaultStartNode"] = book_graph.metadata.get("defaultStartNode", ""); structure_data["defaultPOV"] = book_graph.metadata.get("defaultPOV", "Omniscient")

            # --- Rebuild sections from CURRENT BookGraph state ---
            all_nodes_in_graph = book_graph.get_all_nodes() # Get nodes once

            # 1. Node Positions 
            structure_data["node_positions"] = {}
            for node in all_nodes_in_graph:
                if node.node_type != "book": 
                    pos = node.position
                    if isinstance(pos, (list, tuple)) and len(pos) == 2:
                         try: structure_data["node_positions"][node.id] = (float(pos[0]), float(pos[1]))
                         except (ValueError, TypeError): structure_data["node_positions"][node.id] = (0.0, 0.0)
                    else: structure_data["node_positions"][node.id] = (0.0, 0.0)
            print(f"BookStructureManager: Saving {len(structure_data['node_positions'])} node positions.")

            # 2. Chapters (Rebuild completely based on node.chapter attribute)
            rebuilt_chapters_dict = {}
            for ch_id, ch_info in book_graph.chapter_info.items():
                 rebuilt_chapters_dict[ch_id] = {"id": ch_id, "title": ch_info.get("title", ch_id), "description": ch_info.get("description", ""), "startNode": ch_info.get("startNode", ""), "nodes": []}
            for node in all_nodes_in_graph: 
                 if node.node_type != "book" and node.chapter and node.chapter in rebuilt_chapters_dict:
                      if node.id not in rebuilt_chapters_dict[node.chapter]['nodes']:
                           rebuilt_chapters_dict[node.chapter]['nodes'].append(node.id)
                 elif node.node_type != "book" and node.chapter:
                      print(f"BookStructureManager: Warning - Node {node.id} references chapter '{node.chapter}' which is not defined. Creating entry.")
                      rebuilt_chapters_dict[node.chapter] = {"id": node.chapter, "title": node.chapter, "nodes": [node.id]} # Create chapter entry
            structure_data["chapters"] = list(rebuilt_chapters_dict.values())
            print(f"BookStructureManager: Saving {len(structure_data['chapters'])} chapters.")

            # 3. Critical Path (List of non-POV, non-book nodes)
            critical_path_list = []
            for node in all_nodes_in_graph: 
                if node.node_type != "book" and not self.character_pov_manager.is_character_pov_node(node.id):
                    file_path = node.file_path or self.path_manager.get_default_file_path(node, False)
                    node.file_path = self.path_manager.normalize_path(file_path) 
                    critical_path_list.append({"id": node.id, "title": node.title, "type": node.node_type, "chapter": node.chapter, "filePath": node.file_path})
            structure_data["criticalPath"] = critical_path_list
            print(f"BookStructureManager: Saving {len(critical_path_list)} nodes in criticalPath list.")

            # 4. Character POVs (Rebuild from graph edges and node metadata)
            character_povs_dict = {}
            for edge in book_graph.get_all_edges(): # Iterate through graph edges
                if edge.edge_type == "character-pov":
                    base_node_id = edge.source_id
                    pov_node = book_graph.get_node(edge.target_id) # Get node object from graph
                    if pov_node:
                        character_name = pov_node.metadata.get("povCharacter")
                        if not character_name:
                             character_name = self.character_pov_manager.get_character_from_pov_node(pov_node.id) or "Unknown"
                             print(f"BookStructureManager: Warning - povCharacter metadata missing for {pov_node.id}, inferred '{character_name}'.")
                        file_path = pov_node.file_path or self.path_manager.get_default_file_path(pov_node, True)
                        pov_node.file_path = self.path_manager.normalize_path(file_path) 
                        character_povs_dict.setdefault(base_node_id, [])
                        if not any(pov['nodeId'] == pov_node.id for pov in character_povs_dict[base_node_id]):
                             character_povs_dict[base_node_id].append({"character": character_name, "nodeId": pov_node.id, "filePath": pov_node.file_path})
            structure_data["characterPOVs"] = character_povs_dict
            print(f"BookStructureManager: Saving {len(character_povs_dict)} character POV entries.")

            # 5. Edges (Rebuild directly from graph)
            edges_list = [edge.to_dict() for edge in book_graph.get_all_edges()] # Iterate through graph edges
            structure_data["edges"] = edges_list
            print(f"BookStructureManager: Saving {len(edges_list)} edges.")

            # 6. Preserve other top-level keys from original data if they exist
            if self.original_structure_data:
                 preserved_keys = ["tracks", "relatedContent", "characters"] # Add others if needed
                 for key in preserved_keys:
                      if key in self.original_structure_data:
                           structure_data[key] = self.original_structure_data[key]
                      else: # Ensure key exists even if empty
                           structure_data.setdefault(key, {} if key != "characters" else []) 
            else: # Ensure default empty structures if no original data
                 structure_data.setdefault("relatedContent", {})
                 structure_data.setdefault("tracks", {})
                 structure_data.setdefault("characters", [])


            # --- Save to File ---
            with open(structure_path, 'w', encoding='utf-8') as f:
                json.dump(structure_data, f, indent=2, ensure_ascii=False)
            
            self.original_structure_data = copy.deepcopy(structure_data)
            print(f"BookStructureManager: Save successful.")
            return True
            
        except Exception as e: 
            print(f"ERROR saving book structure: {e}")
            traceback.print_exc()
            return False
    
    def get_original_structure_data(self):
        """Get the original structure data loaded from the file."""
        return self.original_structure_data
    
    def set_original_structure_data(self, data):
        """Set the original structure data (used after loading)."""
        self.original_structure_data = copy.deepcopy(data)

