"""
BookGraph class for the Interactive Book Editor.
Represents the book structure using NetworkX.
ADDED: rename_chapter method.
FIXED: Added missing 'import re'.
"""

import networkx as nx
import re # Import the regular expression module
from node import Node, Edge # Assuming Node and Edge classes are defined

class BookGraph:
    """
    Represents the book structure as a graph using NetworkX.
    Manages nodes, edges, chapters, and metadata.
    """
    
    def __init__(self):
        """Initialize a new BookGraph instance."""
        self.graph = nx.DiGraph() 
        self.chapter_info = {} 
        self.metadata = {} 
        
    def add_node(self, node):
        """Add a node to the graph."""
        if not isinstance(node, Node): print("BookGraph.add_node: Error - Input must be a Node object."); return False
        if node.id in self.graph: print(f"BookGraph.add_node: Warning - Node {node.id} already exists. Updating."); return self.update_node(node) 
        self.graph.add_node(node.id, title=node.title, node_type=node.node_type, chapter=node.chapter,
                            file_path=node.file_path, position=node.position, metadata=node.metadata.copy())
        print(f"BookGraph.add_node: Node {node.id} added."); return True

    def update_node(self, node):
        """Update an existing node's attributes in the graph."""
        if not isinstance(node, Node): print("BookGraph.update_node: Error - Input must be a Node object."); return False
        if node.id not in self.graph: print(f"BookGraph.update_node: Error - Node {node.id} not found."); return False
        node_data = self.graph.nodes[node.id]
        node_data['title'] = node.title; node_data['node_type'] = node.node_type; node_data['chapter'] = node.chapter
        node_data['file_path'] = node.file_path; node_data['position'] = node.position; node_data['metadata'] = node.metadata.copy() 
        return True

    def remove_node(self, node_id):
        """Remove a node and its connected edges from the graph."""
        if node_id not in self.graph: print(f"BookGraph.remove_node: Warning - Node {node_id} not found."); return False
        try:
            self.graph.remove_node(node_id); print(f"BookGraph.remove_node: Node {node_id} removed.")
            for chapter_data in self.chapter_info.values():
                 if "nodes" in chapter_data and node_id in chapter_data["nodes"]: chapter_data["nodes"].remove(node_id)
            return True
        except Exception as e: print(f"BookGraph.remove_node: Error removing node {node_id}: {e}"); return False

    def get_node(self, node_id):
        """Get a Node object by its ID."""
        if node_id in self.graph:
            node_data = self.graph.nodes[node_id]
            return Node(node_id=node_id, title=node_data.get('title', node_id), node_type=node_data.get('node_type'),
                        chapter=node_data.get('chapter'), file_path=node_data.get('file_path'),
                        position=node_data.get('position', (0.0, 0.0)), metadata=node_data.get('metadata', {}).copy())
        return None

    def get_all_nodes(self):
        """Get a list of all Node objects in the graph."""
        return [self.get_node(node_id) for node_id in self.graph.nodes()]

    def add_edge(self, edge):
        """Add an edge to the graph."""
        if not isinstance(edge, Edge): print("BookGraph.add_edge: Error - Input must be an Edge object."); return False
        if not edge.source_id or not edge.target_id: print("BookGraph.add_edge: Error - Edge must have source and target IDs."); return False
        if edge.source_id not in self.graph or edge.target_id not in self.graph: print(f"BookGraph.add_edge: Error - Source ({edge.source_id}) or Target ({edge.target_id}) node not found."); return False
        if self.graph.has_edge(edge.source_id, edge.target_id): print(f"BookGraph.add_edge: Warning - Edge {edge.source_id}->{edge.target_id} already exists. Updating."); return self.update_edge(edge) 
        self.graph.add_edge(edge.source_id, edge.target_id, edge_type=edge.edge_type, metadata=edge.metadata.copy())
        print(f"BookGraph.add_edge: Edge {edge.source_id}->{edge.target_id} [{edge.edge_type}] added."); return True

    def update_edge(self, edge):
        """Update an existing edge's attributes."""
        if not isinstance(edge, Edge): print("BookGraph.update_edge: Error - Input must be an Edge object."); return False
        if not self.graph.has_edge(edge.source_id, edge.target_id): print(f"BookGraph.update_edge: Error - Edge {edge.source_id}->{edge.target_id} not found."); return False
        edge_data = self.graph.edges[edge.source_id, edge.target_id]
        edge_data['edge_type'] = edge.edge_type; edge_data['metadata'] = edge.metadata.copy() 
        return True

    def remove_edge(self, source_id, target_id):
        """Remove an edge from the graph."""
        if not self.graph.has_edge(source_id, target_id): print(f"BookGraph.remove_edge: Warning - Edge {source_id}->{target_id} not found."); return False
        try: self.graph.remove_edge(source_id, target_id); print(f"BookGraph.remove_edge: Edge {source_id}->{target_id} removed."); return True
        except Exception as e: print(f"BookGraph.remove_edge: Error removing edge {source_id}->{target_id}: {e}"); return False

    def get_edge(self, source_id, target_id):
        """Get an Edge object by its source and target IDs."""
        if self.graph.has_edge(source_id, target_id):
            edge_data = self.graph.edges[source_id, target_id]
            return Edge(source_id=source_id, target_id=target_id, edge_type=edge_data.get('edge_type'), metadata=edge_data.get('metadata', {}).copy())
        return None

    def get_all_edges(self):
        """Get a list of all Edge objects in the graph."""
        return [self.get_edge(u, v) for u, v in self.graph.edges()]

    # --- Chapter Management ---
    def add_chapter(self, chapter_id, title, description=""):
        """Add or update a chapter definition."""
        if not chapter_id or not title: print("BookGraph.add_chapter: Error - Chapter ID and Title are required."); return False
        self.chapter_info[chapter_id] = {"id": chapter_id, "title": title, "description": description,
                                         "nodes": self.chapter_info.get(chapter_id, {}).get("nodes", []), 
                                         "startNode": self.chapter_info.get(chapter_id, {}).get("startNode", "")}
        print(f"BookGraph.add_chapter: Chapter '{chapter_id}' added/updated."); return True

    def remove_chapter(self, chapter_id):
        """Remove a chapter definition."""
        if chapter_id not in self.chapter_info: print(f"BookGraph.remove_chapter: Warning - Chapter '{chapter_id}' not found."); return False
        nodes_in_chapter = self.chapter_info[chapter_id].get("nodes", [])
        if nodes_in_chapter:
             print(f"BookGraph.remove_chapter: Warning - Chapter '{chapter_id}' contains nodes. Unassigning them.")
             for node_id in nodes_in_chapter:
                  node = self.get_node(node_id)
                  if node and node.chapter == chapter_id: node.chapter = None; self.update_node(node) 
        del self.chapter_info[chapter_id]; print(f"BookGraph.remove_chapter: Chapter '{chapter_id}' removed."); return True

    def get_chapters(self):
        """Get the chapter information dictionary."""
        return self.chapter_info

    def rename_chapter(self, old_id, new_id):
        """Renames a chapter ID, updating chapter_info and associated nodes."""
        if old_id not in self.chapter_info: print(f"BookGraph.rename_chapter: Error - Old chapter ID '{old_id}' not found."); return False
        if new_id == old_id: return True 
        if new_id in self.chapter_info: print(f"BookGraph.rename_chapter: Error - New chapter ID '{new_id}' already exists."); return False
        # Use re.match for validation (import re at the top)
        if not new_id or not re.match(r'^[a-zA-Z0-9_-]+$', new_id): print(f"BookGraph.rename_chapter: Error - New chapter ID '{new_id}' is invalid."); return False
        print(f"BookGraph.rename_chapter: Renaming '{old_id}' to '{new_id}'...")
        try:
            chapter_data = self.chapter_info.pop(old_id)
            chapter_data['id'] = new_id 
            self.chapter_info[new_id] = chapter_data
            nodes_updated_count = 0
            for node_id in list(self.graph.nodes()): 
                node = self.get_node(node_id) 
                if node and node.chapter == old_id:
                    node.chapter = new_id 
                    self.update_node(node) 
                    nodes_updated_count += 1
            print(f"BookGraph.rename_chapter: Updated chapter_info and {nodes_updated_count} nodes."); return True
        except Exception as e: print(f"BookGraph.rename_chapter: Error during rename: {e}"); return False

    # --- Serialization/Deserialization ---
    def to_dict(self):
        """Convert the graph structure to a dictionary suitable for JSON."""
        graph_dict = {"metadata": self.metadata.copy(), "chapters": list(self.chapter_info.values()),
                      "nodes": [node.to_dict() for node in self.get_all_nodes()], 
                      "edges": [edge.to_dict() for edge in self.get_all_edges()]}
        return graph_dict

    @classmethod
    def from_dict(cls, data):
        """Create a BookGraph instance from a dictionary (e.g., loaded from JSON)."""
        graph = cls(); graph.metadata = data.get("metadata", {})
        for node_data in data.get("nodes", []):
            try: node = Node.from_dict(node_data); graph.add_node(node)
            except ValueError as e: print(f"BookGraph.from_dict: Skipping invalid node data: {node_data} ({e})")
        for edge_data in data.get("edges", []):
             try:
                 if edge_data.get("source") in graph.graph.nodes and edge_data.get("target") in graph.graph.nodes:
                     edge = Edge.from_dict(edge_data); graph.add_edge(edge)
                 else: print(f"BookGraph.from_dict: Skipping edge due to missing node: {edge_data}")
             except ValueError as e: print(f"BookGraph.from_dict: Skipping invalid edge data: {edge_data} ({e})")
        for chapter_data in data.get("chapters", []):
             if "id" in chapter_data and "title" in chapter_data:
                  graph.add_chapter(chapter_data["id"], chapter_data["title"], chapter_data.get("description"))
                  if "startNode" in chapter_data: graph.chapter_info[chapter_data["id"]]["startNode"] = chapter_data["startNode"]
        return graph

