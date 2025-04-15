"""
SimplifiedNodeContentUpdater class for the Interactive Book Editor.
REVISED: Handles branch points in addition to other navigation types.
"""

import os
import json
import traceback
from path_manager import PathManager
from character_pov_manager import CharacterPOVManager 

class SimplifiedNodeContentUpdater:
    """
    Directly updates navigation data in node content files based on graph connections.
    
    Responsible for:
    - Updating next/previous links (based on 'critical-path' edges)
    - Updating alternate POV versions (based on 'character-pov' edges)
    - Updating related non-fiction links (based on 'related-concept' or 'fiction-nonfiction' edges)
    - Updating branch points (based on 'branch-point' edges)
    - Syncing node content files with graph structure
    """
    
    def __init__(self, path_manager=None):
        """
        Initialize a new SimplifiedNodeContentUpdater instance.
        
        Args:
            path_manager (PathManager, optional): PathManager instance.
        """
        self.path_manager = path_manager or PathManager()
        self.character_pov_manager = CharacterPOVManager() 
    
    def update_node_navigation(self, node_id, book_graph):
        """
        Update navigation data in a node's content file based on its connections.
        
        Args:
            node_id (str): ID of the node to update.
            book_graph: The book graph containing connections.
            
        Returns:
            bool: True if successfully updated, False otherwise.
        """
        node = book_graph.get_node(node_id)
        if not node or node.node_type == "book" or not node.file_path:
            # print(f"Skipping navigation update for node_id={node_id}: invalid node, book node, or no file path.")
            return False
        
        full_path = self.path_manager.get_full_content_path(node.file_path)
        if not full_path or not os.path.exists(full_path):
            print(f"Node content file not found for {node_id}: {full_path}")
            return False
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                node_content = json.load(f)
            
            if "navigation" not in node_content:
                node_content["navigation"] = {}
            
            # --- Update Navigation Fields ---
            
            # 1. Update next/previous based ONLY on 'critical-path' edges
            next_node_id = self._get_critical_path_neighbor(node_id, book_graph, direction="next")
            prev_node_id = self._get_critical_path_neighbor(node_id, book_graph, direction="previous")
            
            if next_node_id: node_content["navigation"]["next"] = next_node_id
            elif "next" in node_content["navigation"]: del node_content["navigation"]["next"] 
                
            if prev_node_id: node_content["navigation"]["previous"] = prev_node_id
            elif "previous" in node_content["navigation"]: del node_content["navigation"]["previous"] 

            # 2. Update alternateVersions based on 'character-pov' edges
            alt_versions = self._get_alternate_versions(node_id, book_graph)
            node_content["navigation"]["alternateVersions"] = alt_versions # Assign (will be empty list if none)

            # 3. Update relatedNonFiction based on relevant edge types
            related_nf = self._get_related_nonfiction(node_id, book_graph)
            node_content["navigation"]["relatedNonFiction"] = related_nf # Assign (will be empty list if none)

            # 4. Update branchPoints based on 'branch-point' edges (NEW)
            branch_points = self._get_branch_points(node_id, book_graph)
            node_content["navigation"]["branchPoints"] = branch_points # Assign (will be empty list if none)


            # --- Save Updated Content ---
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(node_content, f, indent=2, ensure_ascii=False)
            
            # print(f"Updated navigation data for node: {node_id}") # Less verbose logging
            return True
            
        except Exception as e:
            print(f"ERROR updating node navigation for {node_id}: {e}")
            traceback.print_exc()
            return False

    def _get_critical_path_neighbor(self, node_id, book_graph, direction="next"):
        """Get the next or previous node specifically connected by a 'critical-path' edge."""
        if direction == "next":
            for _, target, data in book_graph.graph.out_edges(node_id, data=True):
                if data.get("edge_type") == "critical-path": return target 
        elif direction == "previous":
            for source, _, data in book_graph.graph.in_edges(node_id, data=True):
                if data.get("edge_type") == "critical-path": return source 
        return None 

    def _get_alternate_versions(self, node_id, book_graph):
        """Get alternate POV versions for a node based on 'character-pov' edges."""
        alternate_versions = []
        for _, target, data in book_graph.graph.out_edges(node_id, data=True):
            if data.get("edge_type") == "character-pov":
                target_node = book_graph.get_node(target)
                pov_character = "Unknown"
                if target_node:
                    pov_character = target_node.metadata.get("povCharacter") or \
                                    self.character_pov_manager.get_character_from_pov_node(target) or \
                                    "Unknown"
                alternate_versions.append({"povCharacter": pov_character, "nodeId": target})
        return alternate_versions 

    def _get_related_nonfiction(self, node_id, book_graph):
        """Get related non-fiction nodes based on relevant edges."""
        related_nonfiction_ids = set() 
        for _, target, data in book_graph.graph.out_edges(node_id, data=True):
            target_node = book_graph.get_node(target)
            if target_node and target_node.node_type == "nonfiction":
                if data.get("edge_type") in ["related-concept", "fiction-nonfiction"]:
                    related_nonfiction_ids.add(target)
        for source, _, data in book_graph.graph.in_edges(node_id, data=True):
            source_node = book_graph.get_node(source)
            if source_node and source_node.node_type == "nonfiction":
                if data.get("edge_type") in ["related-concept", "fiction-nonfiction"]:
                    related_nonfiction_ids.add(source) 
        return sorted(list(related_nonfiction_ids)) 

    def _get_branch_points(self, node_id, book_graph):
        """
        Get branch points originating from a node based on 'branch-point' edges.
        
        Args:
            node_id (str): The source node ID.
            book_graph: The book graph.
            
        Returns:
            list: List of branch point dictionaries [{text, targetNodeId}], or empty list.
        """
        branch_points = []
        for _, target, data in book_graph.graph.out_edges(node_id, data=True):
            if data.get("edge_type") == "branch-point":
                # Assumes branch text might be stored in edge metadata
                branch_text = data.get("metadata", {}).get("text", f"Branch to {target}") 
                branch_points.append({
                    "text": branch_text, # Need a way to define this text, using placeholder
                    "targetNodeId": target
                })
        return branch_points

    def update_all_node_navigation(self, book_graph):
        """Update navigation data for all nodes in the book graph."""
        success_count = 0
        nodes_to_update = book_graph.get_all_nodes()
        print(f"Attempting to update navigation for {len(nodes_to_update)} nodes...")
        for node in nodes_to_update:
            if node.node_type != "book": 
                if self.update_node_navigation(node.id, book_graph):
                    success_count += 1
        print(f"Finished updating navigation data. Successfully updated {success_count} node content files.")
        return success_count

    def update_critical_path_nodes(self, book_graph):
        """Update the navigation only for nodes involved in 'critical-path' edges."""
        updated_nodes = set()
        success = True
        print("Updating navigation for nodes in critical path...")
        try:
            for source, target, data in book_graph.graph.edges(data=True):
                if data.get("edge_type") == "critical-path":
                    if source not in updated_nodes:
                        if not self.update_node_navigation(source, book_graph): success = False 
                        updated_nodes.add(source)
                    if target not in updated_nodes:
                        if not self.update_node_navigation(target, book_graph): success = False 
                        updated_nodes.add(target)
            print(f"Finished updating critical path navigation for {len(updated_nodes)} nodes.")
            return success
        except Exception as e:
            print(f"ERROR updating critical path navigation: {e}")
            traceback.print_exc()
            return False
