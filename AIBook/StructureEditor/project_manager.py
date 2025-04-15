"""
ProjectManager class for the Interactive Book Editor.
This class handles project-level operations.
REVISED: No longer saves book-structure.json; only creates directories,
default graph object, and default node file. Returns the graph object.
"""

import os
import json
import traceback # For detailed error logging
from path_manager import PathManager
from node import Node # Required for creating default nodes
from book_graph import BookGraph # Required for returning the graph object
# Removed BookStructureManager and CharacterPOVManager imports as they are not used here anymore

class ProjectManager:
    """
    Manages project-level operations like directory creation and
    initializing a default BookGraph object. Does NOT handle saving
    the main book-structure.json file itself.
    """
    
    def __init__(self):
        """Initialize a new ProjectManager instance."""
        self.project_root = None
        # Initialize PathManager internally
        self.path_manager = PathManager() 
    
    def set_project_root(self, root_path):
        """
        Set the root directory for the project.
        
        Args:
            root_path (str): Path to the project root directory.
            
        Returns:
            bool: True if path exists and is set, False otherwise.
        """
        if not isinstance(root_path, str):
            print(f"ProjectManager: Invalid project root path type: {type(root_path)}")
            self.project_root = None
            self.path_manager.set_project_root(None)
            return False

        abs_path = os.path.abspath(root_path)
        # Check if it IS a directory (if it exists)
        if os.path.exists(abs_path) and not os.path.isdir(abs_path):
             print(f"ProjectManager: Error - Path exists but is not a directory: {abs_path}")
             self.project_root = None
             self.path_manager.set_project_root(None)
             return False
             
        # Set the path (it might not exist yet during creation)
        self.project_root = abs_path
        self.path_manager.set_project_root(self.project_root) # Update PathManager's root
        print(f"ProjectManager: Project root set to: {self.project_root}")
        return True
    
    def get_project_root(self):
        """
        Get the project root directory.
        
        Returns:
            str: Path to the project root, or None if not set.
        """
        return self.project_root
    
    def create_project_directories(self, root_path):
        """
        Create the directory structure for a new project.
        
        Args:
            root_path (str): Path to the project root directory.
            
        Returns:
            bool: True if created successfully, False otherwise.
        """
        print(f"ProjectManager: Creating directory structure at: {root_path}")
        try:
            # Create project directory if it doesn't exist
            os.makedirs(root_path, exist_ok=True)
            
            # Create content directory
            content_dir = os.path.join(root_path, "content")
            os.makedirs(content_dir, exist_ok=True)
            
            # Create standard subdirectories within content
            node_types = ["fiction", "nonfiction", "character", "interactive", "world"]
            for node_type in node_types:
                os.makedirs(os.path.join(content_dir, node_type), exist_ok=True)
            
            # Create character_povs directory within fiction
            os.makedirs(os.path.join(content_dir, "fiction", "character_povs"), exist_ok=True)
            
            print("ProjectManager: Directory structure created successfully.")
            return True
        except (IOError, OSError) as e:
            print(f"ERROR creating project directories: {e}")
            return False
    
    def create_new_project(self, root_path):
        """
        Sets up directories and creates an initial BookGraph object with defaults,
        including the preface node content file. Does NOT save book-structure.json.
        
        Args:
            root_path (str): Path to the project root directory.
            
        Returns:
            tuple: (bool success, BookGraph | None) - Tuple containing success status 
                   and the created BookGraph object, or (False, None) on failure.
        """
        print(f"ProjectManager: Attempting to create new project structure at: {root_path}")
        try:
            # 1. Create project directories
            if not self.create_project_directories(root_path):
                print("ProjectManager: Failed to create directories.")
                return False, None # Return tuple on failure
            
            # 2. Set the project root for the internal path manager
            #    This path manager is mainly used here for creating the preface file path.
            if not self.set_project_root(root_path):
                 print("ProjectManager: Failed to set project root after creating directories.")
                 return False, None # Return tuple on failure

            # 3. Create an empty book graph object
            book_graph = BookGraph()
            
            # 4. Add default chapter info to the graph object
            book_graph.add_chapter("chapter1", "Chapter 1", "First chapter")
            
            # 5. Create default preface node object
            preface_file_path_rel = self.path_manager.normalize_path(os.path.join("fiction", "preface-main.json"))
            preface_node = Node(
                node_id="preface-main",
                title="Preface",
                node_type="fiction",
                chapter="chapter1",
                position=(200, 100),
                file_path=preface_file_path_rel 
            )
            book_graph.add_node(preface_node)
            
            # 6. Create default Book node object
            book_node = Node(
                node_id="book",
                title="New Interactive Book",
                node_type="book",
                position=(100, 100),
                metadata={
                    "author": "Author Name",
                    "version": "1.0",
                    "defaultStartNode": "preface-main",
                    "defaultPOV": "Omniscient"
                }
            )
            book_graph.add_node(book_node)
            
            # 7. Set project metadata on the graph object
            book_graph.metadata = {
                "title": "New Interactive Book",
                "author": "Author Name",
                "version": "1.0",
                "defaultStartNode": "preface-main",
                "defaultPOV": "Omniscient"
            }
            
            # 8. Update chapter info in the graph object
            if "chapter1" in book_graph.chapter_info:
                book_graph.chapter_info["chapter1"]["startNode"] = "preface-main"
                book_graph.chapter_info["chapter1"]["nodes"] = ["preface-main"]
            
            # 9. Create the actual preface content file on disk
            preface_content = {
                "id": "preface-main", "nodeId": "preface-main", "nodeType": "fiction",
                "data": {
                    "label": "Preface",
                    "content": "<h1>Welcome to Your Interactive Book</h1><p>This is the preface...</p>",
                    "chapterTitle": "Chapter 1", "subtitle": "Introduction",
                    "location": "Beginning", "timeline": "Start", "tags": ["introduction"]
                },
                "metadata": {"author": "Author Name", "lastModified": "2023-01-01T00:00:00Z", "povCharacter": "Omniscient"},
                "navigation": {"next": None, "previous": None, "alternateVersions": [], "relatedNonFiction": []}
            }
            preface_full_path = self.path_manager.get_full_content_path(preface_file_path_rel)
            if not preface_full_path:
                 print("ProjectManager: ERROR - Could not resolve full path for preface node.")
                 return False, None 
            preface_dir = os.path.dirname(preface_full_path)
            if not self.path_manager.ensure_directory_exists(preface_dir):
                 print(f"ProjectManager: ERROR - Could not create directory for preface node: {preface_dir}")
                 return False, None 
            with open(preface_full_path, 'w', encoding='utf-8') as f:
                json.dump(preface_content, f, indent=2, ensure_ascii=False)
            print(f"ProjectManager: Preface content file created at: {preface_full_path}")

            # 10. Return success status and the created book graph object
            #     NOTE: Does NOT save book-structure.json here.
            print("ProjectManager: New project structure prepared successfully (book_structure.json not saved yet).")
            return True, book_graph # Return tuple on success

        except Exception as e: # Catch potential errors
            print(f"ERROR creating new project structure: {e}")
            traceback.print_exc()
            return False, None # Return tuple on failure
    
    def is_valid_project(self, root_path):
        """Check if a directory contains a valid project structure."""
        # (Implementation remains the same)
        if not root_path or not os.path.isdir(root_path):
            return False
        content_dir = os.path.join(root_path, "content")
        structure_file = os.path.join(content_dir, "book-structure.json")
        if not os.path.isdir(content_dir) or not os.path.isfile(structure_file):
             # Allow check during creation where structure file might not exist yet
             if os.path.isdir(content_dir): 
                  print("ProjectManager: is_valid_project - Content dir exists, structure file might be created.")
                  return True # Consider it potentially valid during creation steps
             return False
        return True

