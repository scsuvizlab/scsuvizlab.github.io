"""
Test script for the NodeContentUpdater.
"""

import os
import sys
import shutil
import tempfile
import json
from data_manager import DataManager
from node import Node, Edge

def test_node_content_updater():
    """Test node content updater functionality."""
    print("Testing node content updater functionality...")
    
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
        
        # Test 1: Create scene nodes with connections
        print("\nTest 1: Creating scene nodes with connections")
        
        # Create scene nodes
        scene1_node = Node(
            node_id="ch1-scene1-restaurant",
            title="The Island of Warmth",
            node_type="scene",
            chapter="chapter1",
            position=(300, 300)
        )
        
        scene2_node = Node(
            node_id="ch1-scene2-alec-bedroom",
            title="The Digital Divide",
            node_type="scene", 
            chapter="chapter1",
            position=(400, 300)
        )
        
        # Create POV node
        alec_pov_node = Node(
            node_id="ch1-scene1-alec-pov",
            title="Alec's Perspective",
            node_type="character_pov",
            chapter="chapter1",
            position=(300, 400),
            metadata={"povCharacter": "Alec"}
        )
        
        # Create nonfiction node
        nonfiction_node = Node(
            node_id="nf-human-craft-value",
            title="The Value of Human Craftsmanship",
            node_type="nonfiction",
            chapter="chapter1",
            position=(300, 200)
        )
        
        # Add nodes to the graph
        book_graph.add_node(scene1_node)
        book_graph.add_node(scene2_node)
        book_graph.add_node(alec_pov_node)
        book_graph.add_node(nonfiction_node)
        
        # Create a sample content for scene1 node
        scene1_content = {
            "nodeId": "ch1-scene1-restaurant",
            "nodeType": "scene",
            "data": {
                "label": "The Island of Warmth",
                "chapterTitle": "Chapter 1: A New Beginning",
                "subtitle": "Family Dinner at Zach's Place",
                "location": "Zach's Restaurant, Atlanta",
                "timeline": "2045, Evening",
                "tags": ["human craftsmanship", "AI society", "family tension", "economic transition", "rebellion"],
                "povCharacter": "Omniscient",
                "content": "<p>The restaurant was an island of warmth in a world of machine precision...</p>"
            },
            "metadata": {
                "criticalPath": True,
                "author": "User",
                "lastModified": "2025-03-16T12:00:00Z"
            },
            "navigation": {
                "next": None,
                "previous": "preface-main",
                "alternateVersions": [],
                "relatedNonFiction": []
            }
        }
        
        # Save the scene1 content file
        scene1_file_path = os.path.join(project_path, "content", "scene", "ch1-scene1-restaurant.json")
        os.makedirs(os.path.dirname(scene1_file_path), exist_ok=True)
        with open(scene1_file_path, 'w', encoding='utf-8') as f:
            json.dump(scene1_content, f, indent=2)
        
        # Update the file path in the node
        scene1_node.file_path = "scene/ch1-scene1-restaurant.json"
        book_graph.update_node(scene1_node)
        
        # Save node content files
        data_manager.save_node_content_file(scene2_node)
        data_manager.save_node_content_file(alec_pov_node)
        data_manager.save_node_content_file(nonfiction_node)
        
        # Create edges (connections)
        # Critical path: preface -> scene1 -> scene2
        critical_edge1 = Edge(
            source_id="preface-main",
            target_id="ch1-scene1-restaurant",
            edge_type="critical-path"
        )
        
        critical_edge2 = Edge(
            source_id="ch1-scene1-restaurant",
            target_id="ch1-scene2-alec-bedroom",
            edge_type="critical-path"
        )
        
        # Character POV: scene1 -> alec_pov
        pov_edge = Edge(
            source_id="ch1-scene1-restaurant",
            target_id="ch1-scene1-alec-pov",
            edge_type="character-pov"
        )
        
        # Related nonfiction: scene1 -> nonfiction
        nonfiction_edge = Edge(
            source_id="ch1-scene1-restaurant",
            target_id="nf-human-craft-value",
            edge_type="related-concept"
        )
        
        # Add edges to the graph
        book_graph.add_edge(critical_edge1)
        book_graph.add_edge(critical_edge2)
        book_graph.add_edge(pov_edge)
        book_graph.add_edge(nonfiction_edge)
        
        # Test 2: Update navigation data and verify
        print("\nTest 2: Updating and verifying navigation data")
        
        # Update navigation data for scene1
        data_manager.update_node_navigation("ch1-scene1-restaurant", book_graph)
        
        # Read the updated content file
        with open(scene1_file_path, 'r', encoding='utf-8') as f:
            updated_content = json.load(f)
        
        # Verify navigation data
        next_node = updated_content.get("navigation", {}).get("next")
        print(f"Next node is: {next_node} (expected: ch1-scene2-alec-bedroom)")
        
        prev_node = updated_content.get("navigation", {}).get("previous")
        print(f"Previous node is: {prev_node} (expected: preface-main)")
        
        alt_versions = updated_content.get("navigation", {}).get("alternateVersions", [])
        print(f"Alternate versions count: {len(alt_versions)}")
        for alt in alt_versions:
            print(f"  - POV: {alt.get('povCharacter')}, Node: {alt.get('nodeId')}")
        
        related_nf = updated_content.get("navigation", {}).get("relatedNonFiction", [])
        print(f"Related non-fiction count: {len(related_nf)}")
        for nf in related_nf:
            print(f"  - {nf}")
        
        # Test 3: Update all node navigation
        print("\nTest 3: Updating all node navigation")
        
        # Update all node navigation
        count = data_manager.update_all_node_navigation(book_graph)
        print(f"Updated {count} node content files")
        
        # Test 4: Force save all
        print("\nTest 4: Force save all")
        
        # Force save all
        data_manager.force_save_all()
        
        # Read updated alec_pov node content file
        alec_pov_file_path = os.path.join(project_path, "content", "character_pov", "ch1-scene1-alec-pov.json")
        if os.path.exists(alec_pov_file_path):
            with open(alec_pov_file_path, 'r', encoding='utf-8') as f:
                alec_content = json.load(f)
            
            # Verify navigation data
            print("\nAlec POV node navigation data:")
            next_node = alec_content.get("navigation", {}).get("next")
            print(f"Next node is: {next_node}")
            
            prev_node = alec_content.get("navigation", {}).get("previous")
            print(f"Previous node is: {prev_node}")
        
        return True
    except Exception as e:
        print(f"Error in test_node_content_updater: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("Testing the NodeContentUpdater functionality\n")
    
    success = test_node_content_updater()
    
    print(f"\nTests {'succeeded' if success else 'failed'}.")
