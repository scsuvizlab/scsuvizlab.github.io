"""
CharacterPOVManager class for the Interactive Book Editor.
This class handles character POV node operations.
"""

class CharacterPOVManager:
    """
    Manages character point-of-view (POV) node operations.
    
    Responsible for:
    - Identifying character POV nodes
    - Extracting character information from node IDs
    - Managing relationships between base nodes and their POV variants
    """
    
    def is_character_pov_node(self, node_id):
        """
        Check if a node is a character POV node based on ID or name pattern.
        
        Args:
            node_id (str): The node ID to check
            
        Returns:
            bool: True if it appears to be a character POV node, False otherwise
        """
        # Check the node ID for patterns that suggest it's a character POV node
        if node_id.endswith('-pov') or '-pov-' in node_id:
            return True
            
        # Check if it matches a pattern like "ch1-scene1-character-pov"
        parts = node_id.split('-')
        if len(parts) >= 4 and parts[-1] == 'pov':
            return True
            
        return False
    
    def get_character_from_pov_node(self, node_id):
        """
        Extract the character name from a character POV node ID.
        
        Args:
            node_id (str): The node ID to parse
            
        Returns:
            str: The character name, or None if it can't be determined
        """
        # Try to extract character name from the ID
        # Format might be like "ch1-scene1-alec-pov"
        parts = node_id.split('-')
        
        if len(parts) >= 3 and parts[-1] == 'pov':
            # Return the part before "pov" - likely the character name
            return parts[-2].capitalize()
        
        # If no clear pattern, just return a default
        return None
    
    def get_base_node_from_pov(self, pov_node_id):
        """
        Try to determine the base/critical path node that a POV node branches from.
        
        Args:
            pov_node_id (str): The POV node ID
            
        Returns:
            str: The likely base node ID, or None if can't determine
        """
        if not self.is_character_pov_node(pov_node_id):
            return None
            
        # Try to extract the base node ID by removing character and POV parts
        parts = pov_node_id.split('-')
        
        if len(parts) >= 4 and parts[-1] == 'pov':
            # Remove the last two parts (character and "pov")
            base_parts = parts[:-2]
            
            # Some node IDs might have a scene number that needs to be preserved
            if len(parts) >= 5 and parts[-3].isdigit():
                base_parts = parts[:-2]
            
            return '-'.join(base_parts)
        
        return None
    
    def create_pov_node_id(self, base_node_id, character_name):
        """
        Create a character POV node ID from a base node ID and character name.
        
        Args:
            base_node_id (str): The base node ID
            character_name (str): The character name
            
        Returns:
            str: The POV node ID
        """
        # Convert character name to lowercase for the ID
        character_slug = character_name.lower()
        
        # Create a POV node ID like "base-node-character-pov"
        return f"{base_node_id}-{character_slug}-pov"
    
    def create_pov_entry(self, base_node_id, pov_node_id, character_name, file_path):
        """
        Create a POV entry for the characterPOVs structure in book-structure.json.
        
        Args:
            base_node_id (str): The base node ID
            pov_node_id (str): The POV node ID
            character_name (str): The character name
            file_path (str): The file path for the POV node
            
        Returns:
            dict: The POV entry
        """
        return {
            "character": character_name,
            "nodeId": pov_node_id,
            "filePath": file_path
        }
