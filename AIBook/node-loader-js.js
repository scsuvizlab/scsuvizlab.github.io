/**
 * Node Loader System for Life in 2045 Interactive Book
 * Handles loading, caching, and processing of content nodes
 */

class NodeLoader {
    constructor() {
        this.cache = {};
        this.currentNode = null;
        this.history = [];
        this.loadingCallbacks = [];
        this.characterData = {};
        this.worldData = {};
    }

    /**
     * Load a content node by ID and character perspective
     * @param {string} nodeId - Unique identifier for the node
     * @param {string} povCharacter - Character POV to load (optional, uses default if not specified)
     * @param {boolean} addToHistory - Whether to add this node to navigation history
     * @returns {Promise} Promise resolving to the node data
     */
    async loadNode(nodeId, povCharacter = null, addToHistory = true) {
        this._triggerLoadingStart();
        
        try {
            // Determine the correct node ID based on POV
            let targetNodeId = nodeId;
            if (povCharacter) {
                // If a POV is requested, we need to find the appropriate node version
                const baseNode = await this._fetchNode(nodeId);
                
                if (baseNode.navigation && baseNode.navigation.alternateVersions) {
                    // Look for an alternate version matching the requested POV
                    const altVersion = baseNode.navigation.alternateVersions.find(
                        v => v.povCharacter === povCharacter
                    );
                    
                    if (altVersion) {
                        targetNodeId = altVersion.nodeId;
                    } else if (baseNode.metadata.povCharacter !== povCharacter) {
                        // If no alternate version exists and the base node isn't in the requested POV,
                        // we'll need to generate one
                        return this._generatePOV(baseNode, povCharacter);
                    }
                }
            }
            
            // Fetch the target node
            const node = await this._fetchNode(targetNodeId);
            
            // Add to history if requested
            if (addToHistory) {
                this.history.push({
                    nodeId: targetNodeId,
                    timestamp: new Date().toISOString()
                });
                this.currentNode = node;
            }
            
            this._triggerLoadingEnd();
            return node;
        } catch (error) {
            console.error('Error loading node:', error);
            this._triggerLoadingEnd();
            throw error;
        }
    }
    
    /**
     * Fetch a node from cache or server
     * @private
     * @param {string} nodeId - ID of the node to fetch
     * @returns {Promise} Promise resolving to the node data
     */
    async _fetchNode(nodeId) {
        // Check cache first
        if (this.cache[nodeId]) {
            return this.cache[nodeId];
        }
        
        // Determine the path to the node based on its type
        let nodePath;
        if (nodeId.includes('nonfiction')) {
            nodePath = `content/nonfiction/${nodeId}.json`;
        } else if (nodeId.includes('pov')) {
            nodePath = `content/fiction/character_povs/${nodeId}.json`;
        } else if (nodeId.includes('incidental')) {
            nodePath = `content/fiction/incidental/${nodeId}.json`;
        } else if (nodeId.includes('sidequest')) {
            nodePath = `content/fiction/sidequests/${nodeId}.json`;
        } else {
            // Default to critical path
            nodePath = `content/fiction/critical_path/${nodeId}.json`;
        }
        
        // Fetch the node
        const response = await fetch(nodePath);
        if (!response.ok) {
            throw new Error(`Failed to load node: ${nodeId}`);
        }
        
        const nodeData = await response.json();
        
        // Cache the node
        this.cache[nodeId] = nodeData;
        
        return nodeData;
    }
    
    /**
     * Generate a POV variation of a node using AI
     * @private
     * @param {Object} baseNode - The original node data
     * @param {string} povCharacter - Character to generate POV for
     * @returns {Promise} Promise resolving to the generated node data
     */
    async _generatePOV(baseNode, povCharacter) {
        // In a full implementation, this would call an AI service
        // For now, we'll create a placeholder version
        
        // First, ensure we have character data
        await this._loadCharacterData(povCharacter);
        
        // Create a copy of the base node
        const generatedNode = JSON.parse(JSON.stringify(baseNode));
        
        // Update metadata
        generatedNode.nodeId = `${baseNode.nodeId}-${povCharacter.toLowerCase()}-generated`;
        generatedNode.metadata.povCharacter = povCharacter;
        generatedNode.nodeType = "character_pov";
        generatedNode.parentId = baseNode.nodeId;
        
        // Create placeholder content
        generatedNode.content.text = `[This would be ${povCharacter}'s perspective on this scene, generated by AI based on character data and scene context.]`;
        
        // Add generation note
        generatedNode.metadata.generated = true;
        generatedNode.metadata.generationTimestamp = new Date().toISOString();
        
        // Cache the generated node
        this.cache[generatedNode.nodeId] = generatedNode;
        
        return generatedNode;
    }
    
    /**
     * Load character data if not already cached
     * @private
     * @param {string} characterId - ID of the character to load
     * @returns {Promise} Promise resolving when character data is loaded
     */
    async _loadCharacterData(characterId) {
        if (this.characterData[characterId]) {
            return this.characterData[characterId];
        }
        
        try {
            const response = await fetch(`content/characters/${characterId.toLowerCase()}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load character data: ${characterId}`);
            }
            
            const data = await response.json();
            this.characterData[characterId] = data;
            return data;
        } catch (error) {
            console.error('Error loading character data:', error);
            // Create placeholder character data
            this.characterData[characterId] = {
                characterId: characterId,
                name: characterId,
                type: "unknown"
            };
            return this.characterData[characterId];
        }
    }
    
    /**
     * Navigate to the next node in sequence
     * @returns {Promise} Promise resolving to the next node data
     */
    async loadNextNode() {
        if (!this.currentNode || !this.currentNode.navigation || !this.currentNode.navigation.next) {
            throw new Error('No next node defined');
        }
        
        return this.loadNode(this.currentNode.navigation.next);
    }
    
    /**
     * Navigate to the previous node in sequence
     * @returns {Promise} Promise resolving to the previous node data
     */
    async loadPreviousNode() {
        if (!this.currentNode || !this.currentNode.navigation || !this.currentNode.navigation.previous) {
            throw new Error('No previous node defined');
        }
        
        return this.loadNode(this.currentNode.navigation.previous);
    }
    
    /**
     * Follow a branch from the current node
     * @param {number} branchIndex - Index of the branch to follow
     * @returns {Promise} Promise resolving to the branch node data
     */
    async followBranch(branchIndex) {
        if (!this.currentNode || 
            !this.currentNode.navigation || 
            !this.currentNode.navigation.branchPoints ||
            !this.currentNode.navigation.branchPoints[branchIndex]) {
            throw new Error('Invalid branch index');
        }
        
        const branch = this.currentNode.navigation.branchPoints[branchIndex];
        return this.loadNode(branch.targetNodeId);
    }
    
    /**
     * Return from a temporary branch to the original path
     * @returns {Promise} Promise resolving to the return node data
     */
    async returnFromBranch() {
        if (!this.currentNode || 
            !this.currentNode.navigation || 
            !this.currentNode.navigation.returnNodeId) {
            throw new Error('No return path defined');
        }
        
        return this.loadNode(this.currentNode.navigation.returnNodeId);
    }
    
    /**
     * Load related non-fiction content
     * @param {number} index - Index of the related content to load
     * @returns {Promise} Promise resolving to the non-fiction node data
     */
    async loadRelatedNonFiction(index) {
        if (!this.currentNode || 
            !this.currentNode.navigation || 
            !this.currentNode.navigation.relatedNonFiction ||
            !this.currentNode.navigation.relatedNonFiction[index]) {
            throw new Error('Invalid related content index');
        }
        
        return this.loadNode(this.currentNode.navigation.relatedNonFiction[index], null, false);
    }
    
    /**
     * Register a callback for loading events
     * @param {Function} startCallback - Function to call when loading starts
     * @param {Function} endCallback - Function to call when loading ends
     */
    onLoading(startCallback, endCallback) {
        this.loadingCallbacks.push({
            start: startCallback,
            end: endCallback
        });
    }
    
    /**
     * Trigger loading start callbacks
     * @private
     */
    _triggerLoadingStart() {
        this.loadingCallbacks.forEach(callback => {
            if (callback.start) callback.start();
        });
    }
    
    /**
     * Trigger loading end callbacks
     * @private
     */
    _triggerLoadingEnd() {
        this.loadingCallbacks.forEach(callback => {
            if (callback.end) callback.end();
        });
    }
    
    /**
     * Get the current reading history
     * @returns {Array} Array of visited nodes
     */
    getHistory() {
        return [...this.history];
    }
    
    /**
     * Clear the node cache
     */
    clearCache() {
        this.cache = {};
    }
}

// Create global instance
window.nodeLoader = new NodeLoader();
