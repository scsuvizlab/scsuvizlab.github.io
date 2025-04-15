"""
Test script for the auto-save functionality.
"""

import os
import sys
import shutil
import tempfile
import json
from data_manager import DataManager
from node import Node, Edge

def test_auto_save():
    """Test auto-save functionality."""
    print("Testing auto-save functionality...")
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a DataManager instance
        data_manager = DataManager()
        
        # Create a new project
        project_path = os.path.join(temp_dir, "test_project")
        result = data_manager.create_new_project(project_path)
        
        if not result:
            print("Failed to create project")
            return False
        
        # Load the book structure
        book_graph = data_manager.load_book_structure()
        
        if not book_graph:
            print("Failed to load book graph")
            return False
        
        # Test 1: Add a new node
        print("\nTest 1: Adding a new node with auto-save")
        
        # Create a node
        new_node = Node(
            node_id="auto-save-test-node",
            title="Auto-Save Test Node",
            node_type="fiction",
            chapter="chapter1",
            position=(300, 300)
        )
        
        # Add the node to the graph
        book_graph.add_node(new_node)
        
        # Trigger auto-save
        data_manager.on_node_added(new_node)
        
        # Check if the node file was created
        node_file_path = os.path.join(project_path, "content", "fiction", "auto-save-test-node.json")
        print(f"Node file exists: {os.path.isfile(node_file_path)}")
        
        # Check if the node is in the book structure JSON
        structure_path = os.path.join(project_path, "content", "book-structure.json")
        with open(structure_path, 'r', encoding='utf-8') as f:
            structure_data = json.load(f)
        
        node_in_critical_path = any(n.get("id") == "auto-save-test-node" for n in structure_data.get("criticalPath", []))
        print(f"Node exists in critical path: {node_in_critical_path}")
        
        # Test 2: Update the node
        print("\nTest 2: Updating the node with auto-save")
        
        # Update the node
        new_node.title = "Updated Title"
        book_graph.update_node(new_node)
        
        # Trigger auto-save
        data_manager.on_node_updated(new_node)
        
        # Check if the node file was updated
        with open(node_file_path, 'r', encoding='utf-8') as f:
            node_data = json.load(f)
        
        node_title_updated = node_data.get("data", {}).get("label") == "Updated Title"
        print(f"Node title updated in file: {node_title_updated}")
        
        # Test 3: Create a connection
        print("\nTest 3: Adding an edge with auto-save")
        
        # Create an edge
        edge = Edge(
            source_id="preface-main",
            target_id="auto-save-test-node",
            edge_type="critical-path"
        )
        
        # Add the edge to the graph
        book_graph.add_edge(edge)
        
        # Trigger auto-save
        data_manager.on_edge_added(edge)
        
        # Check if the edge is in the book structure JSON
        with open(structure_path, 'r', encoding='utf-8') as f:
            structure_data = json.load(f)
        
        # Look for the edge in the book structure
        edge_found = False
        if "edges" in structure_data:
            for e in structure_data["edges"]:
                if e.get("source") == "preface-main" and e.get("target") == "auto-save-test-node":
                    edge_found = True
                    break
        
        print(f"Edge exists in book structure: {edge_found}")
        print(f"Number of edges in structure: {len(structure_data.get('edges', []))}")
        
        # Test 4: Remove a node
        print("\nTest 4: Removing a node with auto-save")
        
        # Remove the node
        result = data_manager.remove_node("auto-save-test-node", book_graph)
        print(f"Node removal result: {result}")
        
        # Check if the node was removed from the book structure JSON
        with open(structure_path, 'r', encoding='utf-8') as f:
            structure_data = json.load(f)
        
        node_in_critical_path = any(n.get("id") == "auto-save-test-node" for n in structure_data.get("criticalPath", []))
        print(f"Node exists in critical path after removal: {node_in_critical_path}")
        
        # Check if the edge was removed
        edge_found = False
        if "edges" in structure_data:
            for e in structure_data["edges"]:
                if e.get("source") == "preface-main" and e.get("target") == "auto-save-test-node":
                    edge_found = True
                    break
        
        print(f"Edge still exists in book structure: {edge_found}")
        
        # Test 5: Force save all
        print("\nTest 5: Force save all")
        
        # Create another node
        another_node = Node(
            node_id="another-test-node",
            title="Another Test Node",
            node_type="fiction",
            chapter="chapter1",
            position=(400, 400)
        )
        
        # Add the node to the graph
        book_graph.add_node(another_node)
        
        # Force save all
        data_manager.force_save_all()
        
        # Check if the node file was created
        node_file_path = os.path.join(project_path, "content", "fiction", "another-test-node.json")
        print(f"Node file exists: {os.path.isfile(node_file_path)}")
        
        # Check if the node is in the book structure JSON
        with open(structure_path, 'r', encoding='utf-8') as f:
            structure_data = json.load(f)
        
        node_in_critical_path = any(n.get("id") == "another-test-node" for n in structure_data.get("criticalPath", []))
        print(f"Node exists in critical path: {node_in_critical_path}")
        
        return True
    except Exception as e:
        print(f"Error in test_auto_save: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Testing the auto-save functionality\n")
    
    success = test_auto_save()
    
    print(f"\nTests {'succeeded' if success else 'failed'}.")