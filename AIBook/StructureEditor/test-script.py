"""
Test script for the refactored DataManager.
"""

import os
import sys
import shutil
import tempfile
from data_manager import DataManager
from node import Node

def test_project_creation():
    """Test creating a new project."""
    print("Testing project creation...")
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a DataManager instance
        data_manager = DataManager()
        
        # Create a new project
        project_path = os.path.join(temp_dir, "test_project")
        result = data_manager.create_new_project(project_path)
        
        print(f"Project creation result: {result}")
        print(f"Project directory exists: {os.path.isdir(project_path)}")
        print(f"Content directory exists: {os.path.isdir(os.path.join(project_path, 'content'))}")
        print(f"Book structure exists: {os.path.isfile(os.path.join(project_path, 'content', 'book-structure.json'))}")
        
        # Check the project structure
        for dir_name in ["fiction", "nonfiction", "character", "interactive", "world"]:
            print(f"{dir_name} directory exists: {os.path.isdir(os.path.join(project_path, 'content', dir_name))}")
        
        # Check the character_povs directory
        print(f"character_povs directory exists: {os.path.isdir(os.path.join(project_path, 'content', 'fiction', 'character_povs'))}")
        
        # Check the preface node file
        print(f"Preface node file exists: {os.path.isfile(os.path.join(project_path, 'content', 'fiction', 'preface-main.json'))}")
        
        # Load the book structure
        data_manager.set_project_root(project_path)
        book_graph = data_manager.load_book_structure()
        
        print(f"Book graph loaded: {book_graph is not None}")
        if book_graph:
            print(f"Number of nodes: {len(book_graph.get_all_nodes())}")
            
            # Check for the book node
            book_nodes = [node for node in book_graph.get_all_nodes() if node.node_type == "book"]
            print(f"Book node exists: {len(book_nodes) > 0}")
            
            # Check for the preface node
            preface_nodes = [node for node in book_graph.get_all_nodes() if node.id == "preface-main"]
            print(f"Preface node exists: {len(preface_nodes) > 0}")
            
            # Check chapters
            print(f"Number of chapters: {len(book_graph.chapter_info)}")
            print(f"Chapter 1 exists: {'chapter1' in book_graph.chapter_info}")
            
            if 'chapter1' in book_graph.chapter_info:
                print(f"Chapter 1 title: {book_graph.chapter_info['chapter1'].get('title')}")
                print(f"Chapter 1 start node: {book_graph.chapter_info['chapter1'].get('startNode')}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

def test_node_operations():
    """Test node operations."""
    print("\nTesting node operations...")
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a DataManager instance
        data_manager = DataManager()
        
        # Create a new project
        project_path = os.path.join(temp_dir, "test_project")
        data_manager.create_new_project(project_path)
        data_manager.set_project_root(project_path)
        
        # Load the book structure
        book_graph = data_manager.load_book_structure()
        
        if not book_graph:
            print("Failed to load book graph")
            return False
        
        # Create a new node
        new_node = Node(
            node_id="test-node",
            title="Test Node",
            node_type="fiction",
            chapter="chapter1",
            position=(300, 300)
        )
        
        # Add the node to the graph
        book_graph.add_node(new_node)
        
        # Save the node content file
        result = data_manager.save_node_content_file(new_node)
        print(f"Save node content result: {result}")
        
        # Check if the file was created
        node_file_path = os.path.join(project_path, "content", "fiction", "test-node.json")
        print(f"Node file exists: {os.path.isfile(node_file_path)}")
        
        # Save the book structure
        result = data_manager.save_book_structure(book_graph)
        print(f"Save book structure result: {result}")
        
        # Load the book structure again
        book_graph = data_manager.load_book_structure()
        
        if not book_graph:
            print("Failed to reload book graph")
            return False
        
        # Check if the node is in the graph
        test_nodes = [node for node in book_graph.get_all_nodes() if node.id == "test-node"]
        print(f"Test node exists in graph: {len(test_nodes) > 0}")
        
        if len(test_nodes) > 0:
            print(f"Test node title: {test_nodes[0].title}")
            print(f"Test node type: {test_nodes[0].node_type}")
            print(f"Test node chapter: {test_nodes[0].chapter}")
        
        # Test character POV functionality
        is_pov = data_manager.is_character_pov_node("chapter1-scene1-john-pov")
        print(f"Is POV node: {is_pov}")
        
        character = data_manager.get_character_from_pov_node("chapter1-scene1-john-pov")
        print(f"Character name: {character}")
        
        base_node = data_manager.get_base_node_from_pov("chapter1-scene1-john-pov")
        print(f"Base node: {base_node}")
        
        # Test removing a node
        result = data_manager.remove_node("test-node", book_graph)
        print(f"Remove node result: {result}")
        
        # Save the book structure
        result = data_manager.save_book_structure(book_graph)
        print(f"Save book structure after node removal result: {result}")
        
        # Load the book structure again
        book_graph = data_manager.load_book_structure()
        
        if not book_graph:
            print("Failed to reload book graph after node removal")
            return False
        
        # Check if the node was removed
        test_nodes = [node for node in book_graph.get_all_nodes() if node.id == "test-node"]
        print(f"Test node removed from graph: {len(test_nodes) == 0}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Testing the refactored DataManager\n")
    
    test_project_creation()
    test_node_operations()
    
    print("\nTests completed.")
