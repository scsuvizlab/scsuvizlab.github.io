"""
PathManager class for the Interactive Book Editor.
This class handles file path operations and normalization.
Removed self-import line.
"""

import os
# Removed the problematic self-import: from path_manager import PathManager 

class PathManager:
    """
    Handles file path operations and normalization.
    
    Responsible for:
    - Normalizing paths for cross-platform compatibility
    - Generating default file paths for nodes
    - Resolving relative paths
    """
    
    def __init__(self, project_root=None):
        """
        Initialize a new PathManager instance.
        
        Args:
            project_root (str, optional): Root directory of the project.
        """
        self.project_root = None # Initialize to None
        if project_root:
             self.set_project_root(project_root) # Use setter to validate
        print(f"PathManager initialized. Project root: {self.project_root}")


    def set_project_root(self, root_path):
        """
        Set the project root path.
        
        Args:
            root_path (str): Path to the project root.
        """
        # Basic validation: check if it's a string and potentially exists
        if isinstance(root_path, str) and os.path.isdir(root_path):
             self.project_root = os.path.abspath(root_path) # Store absolute path
             print(f"PathManager: Project root set to {self.project_root}")
        elif isinstance(root_path, str):
             # Allow setting path even if dir doesn't exist yet (e.g., during new project creation)
             self.project_root = os.path.abspath(root_path)
             print(f"PathManager: Project root set to {self.project_root} (directory may not exist yet).")
        else:
             self.project_root = None
             print(f"PathManager: Invalid project root path provided: {root_path}")


    def get_book_structure_path(self):
        """
        Get the absolute path to the book-structure.json file.
        
        Returns:
            str: Absolute path to book-structure.json, or None if project root is not set.
        """
        if not self.project_root:
            print("PathManager: Cannot get structure path, project root not set.")
            return None
        
        # Ensure using 'content' subdirectory
        return os.path.join(self.project_root, "content", "book-structure.json")

    def normalize_path(self, path):
        """
        Normalize a file path to use forward slashes for web/internal consistency.
        
        Args:
            path (str): The file path to normalize.
            
        Returns:
            str: Normalized path with forward slashes. Returns empty string if input is None.
        """
        if path is None:
             return ""
        return str(path).replace('\\', '/') # Ensure input is string

    def get_default_file_path(self, node, is_pov_node=False):
        """
        Generate a default file path relative to the 'content' directory.
        
        Args:
            node (Node): The node object (must have id and node_type attributes).
            is_pov_node (bool): Whether this is a character POV node.
            
        Returns:
            str: The default relative file path (e.g., "fiction/node_id.json").
        """
        if not node or not hasattr(node, 'id') or not hasattr(node, 'node_type'):
             print("PathManager: ERROR - Cannot generate default path, invalid node object.")
             return f"unknown/{'unknown_node'}.json" # Fallback path

        node_id_safe = "".join(c for c in node.id if c.isalnum() or c in ('-', '_')) # Basic sanitize
        node_type = node.node_type or "fiction" # Default type if missing

        if is_pov_node:
            # Place POV nodes in a specific subdirectory under fiction
            path = os.path.join("fiction", "character_povs", f"{node_id_safe}.json")
        else:
            # Use node type as subdirectory, default to fiction if type is unclear
            subdir = node_type if node_type in ["nonfiction", "character", "interactive", "world"] else "fiction"
            path = os.path.join(subdir, f"{node_id_safe}.json")
            
        return self.normalize_path(path)

    def get_full_content_path(self, relative_path):
        """
        Get the absolute path to a content file in the project.
        
        Args:
            relative_path (str): Relative path within the content directory 
                                (e.g., "fiction/node_id.json").
            
        Returns:
            str: Absolute path to the content file, or None if project root or 
                 relative_path is not set/valid.
        """
        if not self.project_root:
            print("PathManager: Cannot get full content path, project root not set.")
            return None
        if not relative_path:
             print("PathManager: Cannot get full content path, relative path is empty.")
             return None
             
        # Ensure relative path uses correct separators for os.path.join
        # but the input `relative_path` is expected to use forward slashes
        # We normalize the *result* of join.
        content_dir = os.path.join(self.project_root, "content")
        # Clean the relative path before joining
        cleaned_relative_path = relative_path.strip('/\\') 
        full_path = os.path.join(content_dir, cleaned_relative_path)
        
        return os.path.abspath(full_path) # Return absolute path


    def ensure_directory_exists(self, path):
        """
        Ensure that a directory exists, creating it if necessary.
        Handles both absolute and relative paths (relative to project root if set).
        
        Args:
            path (str): Path to the directory.
            
        Returns:
            bool: True if the directory exists or was created, False otherwise.
        """
        if not path:
             print("PathManager: Cannot ensure directory, path is empty.")
             return False
             
        try:
            # Check if it's an absolute path
            if not os.path.isabs(path) and self.project_root:
                 # Assume relative to project root if root is set
                 abs_path = os.path.join(self.project_root, path)
            else:
                 abs_path = path
                 
            os.makedirs(abs_path, exist_ok=True)
            # print(f"PathManager: Ensured directory exists: {abs_path}") # Verbose
            return True
        except (IOError, OSError, TypeError) as e: # Added TypeError
            print(f"PathManager: ERROR ensuring directory exists '{path}': {e}")
            return False

    def join_paths(self, *paths):
        """
        Join paths using the appropriate separator and normalize the result.
        Filters out None or empty path components.
        
        Args:
            *paths: Path components to join.
            
        Returns:
            str: Normalized joined path.
        """
        # Filter out None or empty strings before joining
        valid_paths = [str(p) for p in paths if p] 
        if not valid_paths:
             return "" # Return empty if no valid paths
        joined = os.path.join(*valid_paths)
        return self.normalize_path(joined)

    def get_relative_path(self, full_path):
        """
        Convert an absolute path within the project's content directory 
        to a relative path (using forward slashes).
        
        Args:
            full_path (str): The absolute path to convert.
            
        Returns:
            str: The relative path from the 'content' directory, or None if
                 the path is outside the content directory or root is not set.
        """
        if not self.project_root or not full_path:
            return None
            
        content_dir = os.path.abspath(os.path.join(self.project_root, "content"))
        abs_full_path = os.path.abspath(full_path)
        
        # Check if the full path is inside the content directory
        if os.path.commonpath([content_dir]) == os.path.commonpath([content_dir, abs_full_path]):
            relative = os.path.relpath(abs_full_path, content_dir)
            return self.normalize_path(relative)
        else:
            print(f"PathManager: Path '{full_path}' is outside the content directory '{content_dir}'.")
            return None # Path is outside the content directory

