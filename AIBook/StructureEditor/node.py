"""
Node and Edge classes for the Interactive Book Editor.
These classes represent the fundamental data structures for the book graph.
"""

class Node:
    """
    Represents a content node in the interactive book structure.
    
    A node can be a fiction scene, non-fiction article, character profile, etc.
    Each node has a unique ID, title, type, and other metadata.
    """
    
    def __init__(self, node_id, title=None, node_type=None, chapter=None, 
                 file_path=None, position=None, metadata=None):
        """
        Initialize a new Node instance.
        
        Args:
            node_id (str): Unique identifier for the node
            title (str, optional): Display name for the node
            node_type (str, optional): Type of node (fiction, nonfiction, character, etc.)
            chapter (str, optional): Chapter this node belongs to
            file_path (str, optional): Path to the content file
            position (tuple, optional): (x, y) coordinates for display
            metadata (dict, optional): Additional properties
        """
        self.id = node_id
        self.title = title or node_id
        self.node_type = node_type or "fiction"
        self.chapter = chapter
        self.file_path = file_path
        self.position = position or (0, 0)
        self.metadata = metadata or {}
    
    def to_dict(self):
        """
        Convert the node to a dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of the node
        """
        node_dict = {
            "id": self.id,
            "title": self.title,
            "type": self.node_type,
        }
        
        if self.chapter:
            node_dict["chapter"] = self.chapter
        
        if self.file_path:
            node_dict["filePath"] = self.file_path
            
        if self.position != (0, 0):
            node_dict["position"] = self.position
        
        if self.metadata:
            # Add all metadata as top-level keys
            for key, value in self.metadata.items():
                if key not in node_dict:  # Don't overwrite existing keys
                    node_dict[key] = value
        
        return node_dict
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Node instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing node data
            
        Returns:
            Node: A new Node instance
        """
        # Extract the standard fields - check both 'id' and 'nodeId' for compatibility
        node_id = data.get("id") or data.get("nodeId")
        
        # Ensure we have a node ID
        if not node_id:
            raise ValueError("Node data must contain a valid ID (either 'id' or 'nodeId')")
        
        # Debug print the node ID
        print(f"Creating node from data with ID: {node_id}")
            
        title = data.get("title")
        node_type = data.get("type") or data.get("nodeType")
        chapter = data.get("chapter")
        file_path = data.get("filePath")
        position = data.get("position")
        
        # All other fields go into metadata
        metadata = {}
        for key, value in data.items():
            if key not in ["id", "nodeId", "title", "type", "nodeType", "chapter", "filePath", "position"]:
                metadata[key] = value
        
        return cls(
            node_id=node_id,
            title=title,
            node_type=node_type,
            chapter=chapter,
            file_path=file_path,
            position=position,
            metadata=metadata
        )


class Edge:
    """
    Represents a connection between two nodes in the interactive book structure.
    
    An edge can represent various relationships like critical path, character POV alternatives,
    related content, etc.
    """
    
    def __init__(self, source_id, target_id, edge_type=None, metadata=None):
        """
        Initialize a new Edge instance.
        
        Args:
            source_id (str): ID of the source node
            target_id (str): ID of the target node
            edge_type (str, optional): Type of edge (critical-path, character-pov, etc.)
            metadata (dict, optional): Additional properties
        """
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type or "default"
        self.metadata = metadata or {}
    
    def to_dict(self):
        """
        Convert the edge to a dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of the edge
        """
        edge_dict = {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type,
        }
        
        if self.metadata:
            # Add all metadata as top-level keys
            for key, value in self.metadata.items():
                if key not in edge_dict:  # Don't overwrite existing keys
                    edge_dict[key] = value
        
        return edge_dict
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Edge instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing edge data
            
        Returns:
            Edge: A new Edge instance
        """
        # Extract the standard fields - check both common formats
        source_id = data.get("source") or data.get("source_id") or data.get("sourceId")
        target_id = data.get("target") or data.get("target_id") or data.get("targetId")
        edge_type = data.get("type") or data.get("edge_type") or data.get("edgeType")
        
        # Check for required fields
        if not source_id or not target_id:
            raise ValueError("Edge data must contain valid source and target IDs")
        
        # All other fields go into metadata
        metadata = {}
        for key, value in data.items():
            if key not in ["source", "source_id", "sourceId", "target", "target_id", "targetId", "type", "edge_type", "edgeType"]:
                metadata[key] = value
        
        return cls(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            metadata=metadata
        )