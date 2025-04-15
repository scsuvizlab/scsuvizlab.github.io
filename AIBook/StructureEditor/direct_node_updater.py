"""
Direct node content updater for emergency fixes.
This script directly modifies node content files based on the graph structure.
"""

import os
import sys
import json

def update_specific_node(project_path, node_id, file_path, next_node_id=None, prev_node_id=None, alt_versions=None, related_nf=None):
    """
    Directly update a specific node's navigation data.
    
    Args:
        project_path: Path to the project directory
        node_id: ID of the node to update
        file_path: Path to the node content file (relative to content directory)
        next_node_id: ID of the next node (or None to leave unchanged)
        prev_node_id: ID of the previous node (or None to leave unchanged)
        alt_versions: List of alternate version dictionaries (or None to leave unchanged)
        related_nf: List of related non-fiction IDs (or None to leave unchanged)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Build full path to the content file
    full_path = os.path.join(project_path, "content", file_path)
    
    print(f"Attempting to update node {node_id} at {full_path}")
    
    # Check if file exists
    if not os.path.exists(full_path):
        print(f"ERROR: File not found: {full_path}")
        return False
    
    try:
        # Read the current content
        with open(full_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Make sure navigation section exists
        if "navigation" not in content:
            content["navigation"] = {}
        
        # Print current navigation values
        print(f"Current navigation for {node_id}:")
        print(f"  next: {content['navigation'].get('next')}")
        print(f"  previous: {content['navigation'].get('previous')}")
        
        # Update navigation data if provided
        if next_node_id is not None:
            content["navigation"]["next"] = next_node_id
        
        if prev_node_id is not None:
            content["navigation"]["previous"] = prev_node_id
        
        if alt_versions is not None:
            content["navigation"]["alternateVersions"] = alt_versions
        
        if related_nf is not None:
            content["navigation"]["relatedNonFiction"] = related_nf
        
        # Write the updated content back
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        print(f"Successfully updated navigation for {node_id}:")
        print(f"  next: {content['navigation'].get('next')}")
        print(f"  previous: {content['navigation'].get('previous')}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update {node_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_critical_path(project_path, critical_path_sequence):
    """
    Update the navigation data for all nodes in a critical path sequence.
    
    Args:
        project_path: Path to the project directory
        critical_path_sequence: List of tuples (node_id, file_path)
        
    Returns:
        bool: True if all nodes were successfully updated, False otherwise
    """
    success = True
    
    # Process each node in the sequence
    for i, (node_id, file_path) in enumerate(critical_path_sequence):
        # Determine previous and next nodes
        prev_id = None if i == 0 else critical_path_sequence[i-1][0]
        next_id = None if i == len(critical_path_sequence)-1 else critical_path_sequence[i+1][0]
        
        # Update this node
        if not update_specific_node(project_path, node_id, file_path, next_id, prev_id):
            success = False
    
    return success

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python direct_node_updater.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    # Example: Update preface-main to point to nf-interactive-knowledge
    update_specific_node(
        project_path, 
        "preface-main", 
        "fiction/preface-main.json", 
        next_node_id="nf-interactive-knowledge",
        prev_node_id=None
    )
    
    # Example: Update a critical path
    critical_path = [
        ("preface-main", "fiction/preface-main.json"),
        ("nf-interactive-knowledge", "nonfiction/nf-interactive-knowledge.json"),
        ("ch1-scene1-restaurant", "fiction/ch1-scene1-restaurant.json"),
        ("ch1-scene2-alec-bedroom", "fiction/ch1-scene2-alec-bedroom.json")
    ]
    
    update_critical_path(project_path, critical_path)
