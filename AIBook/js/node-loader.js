/**
 * Enhanced NodeLoader for Life in 2045 Interactive Book
 * Updated to remove hard-coded references and rely fully on book structure
 */

class NodeLoader {
    constructor() {
        this.cache = {};
        this.currentNode = null;
        this.history = [];
        this.loadingCallbacks = [];
        this.characterData = {};
        this.worldData = {};
        this.bookStructure = null;
        this.defaultStartNodeId = null;
        this.defaultPOV = null;
        
        // Initialize by loading the book structure
        this.initBookStructure();
    }
    
    /**
     * Initialize the book structure by loading the JSON file
     */
    async initBookStructure() {
        try {
            console.log("Loading book structure...");
            const response = await fetch('content/book-structure.json');
            if (!response.ok) {
                throw new Error(`Failed to load book structure: ${response.status}`);
            }
            
            this.bookStructure = await response.json();
            console.log("Book structure loaded successfully:", this.bookStructure.title);
            
            // Set defaults from book structure
            if (this.bookStructure.defaultStartNode) {
                this.defaultStartNodeId = this.bookStructure.defaultStartNode;
                console.log(`Default start node set to: ${this.defaultStartNodeId}`);
            } else {
                console.warn("No default start node defined in book structure");
            }
            
            if (this.bookStructure.defaultPOV) {
                this.defaultPOV = this.bookStructure.defaultPOV;
                console.log(`Default POV set to: ${this.defaultPOV}`);
            } else {
                this.defaultPOV = "Omniscient"; // Reasonable fallback
                console.warn("No default POV defined in book structure, using 'Omniscient'");
            }
            
            // Trigger an event that the book structure is loaded
            const event = new CustomEvent('bookStructureLoaded', {
                detail: { 
                    bookStructure: this.bookStructure,
                    defaultStartNodeId: this.defaultStartNodeId,
                    defaultPOV: this.defaultPOV
                }
            });
            document.dispatchEvent(event);
            
        } catch (error) {
            console.error("Error loading book structure:", error);
            // Create a minimal default structure without hard-coded nodes
            this.bookStructure = {
                title: "Life in 2045",
                defaultStartNode: null,
                defaultPOV: "Omniscient",
                criticalPath: [],
                chapters: []
            };
            
            // Trigger event with empty structure
            const event = new CustomEvent('bookStructureLoadFailed', {
                detail: { error: error.message }
            });
            document.dispatchEvent(event);
        }
    }
    
    /**
     * Get the node definition from the book structure
     * @param {string} nodeId - The node ID to look up
     * @returns {Object|null} - The node definition or null if not found
     */
    getNodeDefinition(nodeId) {
        if (!this.bookStructure) return null;
        
        // Check critical path
        const criticalPathNode = this.bookStructure.criticalPath.find(node => node.id === nodeId);
        if (criticalPathNode) return criticalPathNode;
        
        // Check character POVs
        if (this.bookStructure.characterPOVs) {
            for (const baseNodeId in this.bookStructure.characterPOVs) {
                const povNodes = this.bookStructure.characterPOVs[baseNodeId];
                const povNode = povNodes.find(pov => pov.nodeId === nodeId);
                if (povNode) {
                    return {
                        id: nodeId,
                        title: `${baseNodeId} (${povNode.character} POV)`,
                        type: "fiction",
                        defaultPOV: povNode.character,
                        filePath: povNode.filePath
                    };
                }
            }
        }
        
        // Check tracks for non-fiction nodes
        if (this.bookStructure.tracks) {
            for (const trackId in this.bookStructure.tracks) {
                const track = this.bookStructure.tracks[trackId];
                if (track.nodeSequence && track.nodeSequence.includes(nodeId)) {
                    return {
                        id: nodeId,
                        title: this.formatNodeTitle(nodeId),
                        type: trackId === "nonfiction" ? "nonfiction" : "fiction",
                        defaultPOV: this.bookStructure.defaultPOV || "Omniscient",
                        filePath: this.inferFilePath(nodeId, trackId)
                    };
                }
            }
        }
        
        return null;
    }
    
    /**
     * Format a node ID into a readable title
     * @param {string} nodeId - The node ID to format
     * @returns {string} - A formatted title
     */
    formatNodeTitle(nodeId) {
        return nodeId
            .replace(/^(ch\d+|nf)-/, '')
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    /**
     * Infer a file path from a node ID and track
     * @param {string} nodeId - The node ID
     * @param {string} trackId - The track ID
     * @returns {string} - The inferred file path
     */
    inferFilePath(nodeId, trackId) {
        if (trackId === "nonfiction") {
            return `nonfiction/${nodeId}.json`;
        } else if (nodeId.includes('-pov')) {
            return `fiction/character_povs/${nodeId}.json`;
        } else if (nodeId.includes('ch')) {
            return `fiction/critical_path/${nodeId}.json`;
        } else {
            return `fiction/${nodeId}.json`;
        }
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
            // Wait for book structure to be loaded if it's not yet
            if (!this.bookStructure) {
                console.log("Waiting for book structure to load...");
                await new Promise(resolve => {
                    const checkInterval = setInterval(() => {
                        if (this.bookStructure) {
                            clearInterval(checkInterval);
                            resolve();
                        }
                    }, 100);
                    
                    // Set a timeout in case the structure never loads
                    setTimeout(() => {
                        clearInterval(checkInterval);
                        resolve();
                    }, 5000);
                });
            }
            
            // Use default POV if none specified
            if (!povCharacter && this.defaultPOV) {
                povCharacter = this.defaultPOV;
            }
            
            console.log(`Loading node: ${nodeId}, POV: ${povCharacter || 'default'}`);
            
            // Determine the correct node ID based on POV
            let targetNodeId = nodeId;
            let targetFilePath = null;
            
            // If POV is specified, check if there's a specific POV version
            if (povCharacter && this.bookStructure && this.bookStructure.characterPOVs) {
                const povVersions = this.bookStructure.characterPOVs[nodeId];
                if (povVersions) {
                    const matchingPOV = povVersions.find(pov => pov.character === povCharacter);
                    if (matchingPOV) {
                        targetNodeId = matchingPOV.nodeId;
                        targetFilePath = matchingPOV.filePath;
                        console.log(`Found POV version: ${targetNodeId}, FilePath: ${targetFilePath}`);
                    }
                }
            }
            
            // Get node definition from book structure
            const nodeDefinition = this.getNodeDefinition(targetNodeId);
            if (nodeDefinition && nodeDefinition.filePath) {
                targetFilePath = nodeDefinition.filePath;
                console.log(`Using path from node definition: ${targetFilePath}`);
            }
            
            // Fetch the target node
            const node = await this._fetchNode(targetNodeId, targetFilePath);
            
            // Add to history if requested
            if (addToHistory) {
                this.history.push({
                    nodeId: targetNodeId,
                    pov: povCharacter,
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
     * @param {string} filePath - Optional file path from book structure
     * @returns {Promise} Promise resolving to the node data
     */
    async _fetchNode(nodeId, filePath = null) {
        // Check cache first
        if (this.cache[nodeId]) {
            console.log(`Using cached node: ${nodeId}`);
            return this.cache[nodeId];
        }
        
        console.log(`Attempting to load node: ${nodeId}`);
        
        // Try to load from the provided file path first
        if (filePath) {
            try {
                const fullPath = `content/${filePath}`;
                console.log(`Loading from specified path: ${fullPath}`);
                
                const response = await fetch(fullPath);
                if (response.ok) {
                    const nodeData = await response.json();
                    console.log(`Successfully loaded node from path: ${fullPath}`);
                    this.cache[nodeId] = nodeData;
                    return nodeData;
                } else {
                    console.warn(`File not found at specified path: ${fullPath}`);
                    // Continue to try other methods
                }
            } catch (error) {
                console.warn(`Error loading from specified path: ${error.message}`);
                // Continue to try other methods
            }
        }
        
        // Get node definition from book structure
        const nodeDefinition = this.getNodeDefinition(nodeId);
        if (nodeDefinition && nodeDefinition.filePath) {
            try {
                const fullPath = `content/${nodeDefinition.filePath}`;
                console.log(`Loading from book structure path: ${fullPath}`);
                
                const response = await fetch(fullPath);
                if (response.ok) {
                    const nodeData = await response.json();
                    console.log(`Successfully loaded node from book structure path: ${fullPath}`);
                    this.cache[nodeId] = nodeData;
                    return nodeData;
                } else {
                    console.warn(`File not found at book structure path: ${fullPath}`);
                    // Continue to try other methods
                }
            } catch (error) {
                console.warn(`Error loading from book structure path: ${error.message}`);
                // Continue to try other methods
            }
        }
        
        // Attempt to infer path based on node ID as a fallback
        let nodePath;
        try {
            if (nodeId.includes('nf-')) {
                nodePath = `content/nonfiction/${nodeId}.json`;
            } else if (nodeId.includes('-pov')) {
                nodePath = `content/fiction/character_povs/${nodeId}.json`;
            } else if (nodeId.includes('incidental')) {
                nodePath = `content/fiction/incidental/${nodeId}.json`;
            } else if (nodeId.includes('sidequest')) {
                nodePath = `content/fiction/sidequests/${nodeId}.json`;
            } else {
                // Default to critical path
                nodePath = `content/fiction/critical_path/${nodeId}.json`;
            }
            
            console.log(`Trying inferred path: ${nodePath}`);
            
            // Try to fetch the actual JSON file
            const response = await fetch(nodePath);
            
            if (response.ok) {
                const nodeData = await response.json();
                console.log(`Successfully loaded node from inferred path: ${nodePath}`);
                this.cache[nodeId] = nodeData;
                return nodeData;
            } else {
                console.warn(`Node file not found at inferred path: ${nodePath}. Status: ${response.status}`);
                // Fall back to simulated node
            }
        } catch (error) {
            console.warn(`Error fetching node file: ${error.message}`);
            // Fall back to simulated node
        }
        
        // If we get here, either the fetch failed or the file didn't exist
        // Create a simulated node as fallback
        console.log(`Creating simulated node for: ${nodeId}`);
        const simulatedNode = this._createSimulatedNode(nodeId);
        
        // Cache the simulated node
        this.cache[nodeId] = simulatedNode;
        
        return simulatedNode;
    }
    
    /**
     * Create a simulated node for testing or error recovery
     * @private
     * @param {string} nodeId - ID of the node to create
     * @returns {Object} Simulated node data
     */
    _createSimulatedNode(nodeId) {
        // Try to find the node in the book structure
        let bookNode = null;
        let nodeType = "fiction";
        let chapterId = null;
        let title = this.formatNodeTitle(nodeId);
        let defaultPOV = this.defaultPOV || "Omniscient";
        
        if (this.bookStructure) {
            // Check critical path
            const criticalPathNode = this.bookStructure.criticalPath.find(node => node.id === nodeId);
            if (criticalPathNode) {
                bookNode = criticalPathNode;
                nodeType = bookNode.type || "fiction";
                chapterId = bookNode.chapter;
                title = bookNode.title || title;
                defaultPOV = bookNode.defaultPOV || defaultPOV;
            }
            
            // Check if it's a POV node
            if (!bookNode && nodeId.includes('-pov')) {
                const baseNodeId = nodeId.split('-pov')[0];
                const povChar = nodeId.split('-pov')[1]?.replace('-', '') || 'Unknown';
                
                // Look for the base node
                const baseNode = this.bookStructure.criticalPath.find(node => node.id === baseNodeId);
                if (baseNode) {
                    bookNode = { ...baseNode };
                    bookNode.title = `${baseNode.title} (${povChar} POV)`;
                    bookNode.defaultPOV = povChar;
                }
            }
            
            // Check if it's a non-fiction node
            if (!bookNode && nodeId.includes('nf-')) {
                nodeType = "nonfiction";
                
                // Try to find it in the non-fiction track
                if (this.bookStructure.tracks && this.bookStructure.tracks.nonfiction) {
                    const nonFictionNodes = this.bookStructure.tracks.nonfiction.nodeSequence;
                    if (nonFictionNodes && nonFictionNodes.includes(nodeId)) {
                        title = nodeId.replace('nf-', '').split('-').map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ');
                    }
                }
            }
        }
        
        // Get chapter title if possible
        let chapterTitle = "Unknown Chapter";
        if (chapterId && this.bookStructure && this.bookStructure.chapters) {
            const chapter = this.bookStructure.chapters.find(ch => ch.id === chapterId);
            if (chapter) {
                chapterTitle = chapter.title;
            }
        }
        
        // Basic node structure
        const node = {
            id: nodeId,
            data: {
                label: title,
                content: `<p>This is simulated content for node "${nodeId}".</p>
                         <p>In a full implementation, this would be loaded from a JSON file or API.</p>`,
                chapterTitle: title,
                subtitle: chapterTitle,
                location: "Simulated Location",
                timeline: "2045",
                tags: ["simulation", "test", "interactive-book"],
                branchPoints: []
            },
            navigation: {
                next: null,
                previous: null
            },
            metadata: {
                povCharacter: defaultPOV,
                generated: true
            }
        };
        
        // Set navigation based on book structure
        if (bookNode) {
            if (bookNode.nextNode) {
                node.navigation.next = bookNode.nextNode;
            }
        }
        
        // Find previous and next nodes from critical path
        if (this.bookStructure && this.bookStructure.criticalPath) {
            const criticalPathIndex = this.bookStructure.criticalPath.findIndex(n => n.id === nodeId);
            if (criticalPathIndex > 0) {
                node.navigation.previous = this.bookStructure.criticalPath[criticalPathIndex - 1].id;
            }
            if (criticalPathIndex !== -1 && criticalPathIndex < this.bookStructure.criticalPath.length - 1) {
                // Only set next if not already set from bookNode.nextNode
                if (!node.navigation.next) {
                    node.navigation.next = this.bookStructure.criticalPath[criticalPathIndex + 1].id;
                }
            }
        }
        
        // Add related non-fiction for fiction nodes
        if (nodeType === "fiction" && this.bookStructure && this.bookStructure.relatedContent) {
            const relatedContent = this.bookStructure.relatedContent[nodeId];
            if (relatedContent && relatedContent.length > 0) {
                node.navigation.relatedNonFiction = relatedContent;
            }
        }
        
        // Add character POVs if they exist
        if (nodeType === "fiction" && this.bookStructure && this.bookStructure.characterPOVs) {
            const povs = this.bookStructure.characterPOVs[nodeId];
            if (povs && povs.length > 0) {
                node.navigation.alternateVersions = povs.map(pov => ({
                    povCharacter: pov.character,
                    nodeId: pov.nodeId
                }));
            }
        }
        
        // For non-fiction nodes, adjust the content style
        if (nodeType === "nonfiction") {
            node.data.content = `<div class="nonfiction-content">
                <h3>Concept Overview</h3>
                <p>This is simulated non-fiction content about "${title}".</p>
                <p>In a full implementation, this would contain educational material.</p>
                <div class="info-box">
                    <h4>Key Concepts</h4>
                    <ul>
                        <li>Concept 1</li>
                        <li>Concept 2</li>
                        <li>Concept 3</li>
                    </ul>
                </div>
            </div>`;
        }
        
        return node;
    }
    
    /**
     * Navigate to the next node in sequence
     * @returns {Promise} Promise resolving to the next node data
     */
    async loadNextNode() {
        if (!this.currentNode) {
            throw new Error('No current node');
        }
        
        // First check navigation in the node itself
        if (this.currentNode.navigation && this.currentNode.navigation.next) {
            return this.loadNode(this.currentNode.navigation.next);
        }
        
        // If not defined in the node, use the book structure
        const nextNodeId = this.getNextNodeInCriticalPath(this.currentNode.id);
        if (nextNodeId) {
            return this.loadNode(nextNodeId);
        }
        
        throw new Error('No next node defined');
    }
    
    /**
     * Navigate to the previous node in sequence
     * @returns {Promise} Promise resolving to the previous node data
     */
    async loadPreviousNode() {
        if (!this.currentNode) {
            throw new Error('No current node');
        }
        
        // First check navigation in the node itself
        if (this.currentNode.navigation && this.currentNode.navigation.previous) {
            return this.loadNode(this.currentNode.navigation.previous);
        }
        
        // If not defined in the node, use the book structure
        const previousNodeId = this.getPreviousNodeInCriticalPath(this.currentNode.id);
        if (previousNodeId) {
            return this.loadNode(previousNodeId);
        }
        
        throw new Error('No previous node defined');
    }
    
    /**
     * Load a related non-fiction node
     * @param {number} index - Index in the related non-fiction array
     * @returns {Promise} Promise resolving to the related node
     */
    async loadRelatedNonFiction(index) {
        if (!this.currentNode || 
            !this.currentNode.navigation || 
            !this.currentNode.navigation.relatedNonFiction ||
            !this.currentNode.navigation.relatedNonFiction[index]) {
            
            console.warn("No related non-fiction content at index", index);
            return null;
        }
        
        const relatedNodeId = this.currentNode.navigation.relatedNonFiction[index];
        return this.loadNode(relatedNodeId);
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
    
    /**
     * Get a node from the critical path
     * @param {string} nodeId - Node ID to find
     * @returns {Object|null} Node from critical path or null
     */
    getNodeInCriticalPath(nodeId) {
        if (!this.bookStructure || !this.bookStructure.criticalPath) return null;
        return this.bookStructure.criticalPath.find(node => node.id === nodeId);
    }
    
    /**
     * Get the next node ID in the critical path
     * @param {string} currentNodeId - Current node ID
     * @returns {string|null} Next node ID or null
     */
    getNextNodeInCriticalPath(currentNodeId) {
        const currentNode = this.getNodeInCriticalPath(currentNodeId);
        if (currentNode && currentNode.nextNode) {
            return currentNode.nextNode;
        }
        
        // If not found directly, try to find it in the sequence
        if (this.bookStructure && this.bookStructure.criticalPath) {
            const currentIndex = this.bookStructure.criticalPath.findIndex(node => node.id === currentNodeId);
            if (currentIndex !== -1 && currentIndex < this.bookStructure.criticalPath.length - 1) {
                return this.bookStructure.criticalPath[currentIndex + 1].id;
            }
        }
        
        return null;
    }
    
    /**
     * Get the previous node ID in the critical path
     * @param {string} currentNodeId - Current node ID
     * @returns {string|null} Previous node ID or null
     */
    getPreviousNodeInCriticalPath(currentNodeId) {
        if (!this.bookStructure || !this.bookStructure.criticalPath) return null;
        
        const currentIndex = this.bookStructure.criticalPath.findIndex(node => node.id === currentNodeId);
        if (currentIndex > 0) {
            return this.bookStructure.criticalPath[currentIndex - 1].id;
        }
        
        return null;
    }
    
    /**
     * Get all nodes in a specific chapter
     * @param {string} chapterId - Chapter ID
     * @returns {Array} Array of nodes in the chapter
     */
    getNodesInChapter(chapterId) {
        if (!this.bookStructure || !this.bookStructure.chapters) return [];
        
        const chapter = this.bookStructure.chapters.find(ch => ch.id === chapterId);
        if (chapter && chapter.nodes) {
            return chapter.nodes;
        }
        
        return [];
    }
    
    /**
     * Get all available character POVs for a node
     * @param {string} nodeId - Node ID
     * @returns {Array} Array of character IDs
     */
    getAvailablePOVs(nodeId) {
        if (!this.bookStructure || !this.bookStructure.characterPOVs) return [];
        
        const povs = this.bookStructure.characterPOVs[nodeId];
        if (povs) {
            return povs.map(pov => pov.character);
        }
        
        return [];
    }
    
    /**
     * Get all related non-fiction for a node
     * @param {string} nodeId - Node ID
     * @returns {Array} Array of non-fiction node IDs
     */
    getRelatedNonFiction(nodeId) {
        if (!this.bookStructure || !this.bookStructure.relatedContent) return [];
        
        const related = this.bookStructure.relatedContent[nodeId];
        if (related) {
            return related;
        }
        
        return [];
    }
    
    /**
     * Get all available reading tracks
     * @returns {Object} Object of track definitions
     */
    getAvailableTracks() {
        if (!this.bookStructure || !this.bookStructure.tracks) return {};
        
        return this.bookStructure.tracks;
    }
    
    /**
     * Get nodes in a specific track
     * @param {string} trackId - Track ID
     * @returns {Array} Array of node IDs in the track
     */
    getNodesInTrack(trackId) {
        if (!this.bookStructure || !this.bookStructure.tracks || !this.bookStructure.tracks[trackId]) return [];
        
        return this.bookStructure.tracks[trackId].nodeSequence || [];
    }
    
    /**
     * Get all characters
     * @returns {Array} Array of character definitions
     */
    getCharacters() {
        if (!this.bookStructure || !this.bookStructure.characters) return [];
        
        return this.bookStructure.characters;
    }
    
    /**
     * Validate the book structure format
     * @returns {Object} Validation results with any errors
     */
    validateBookStructure() {
        if (!this.bookStructure) {
            return { valid: false, errors: ["Book structure not loaded"] };
        }
        
        const errors = [];
        
        // Check required top-level properties
        if (!this.bookStructure.title) errors.push("Missing title");
        if (!this.bookStructure.defaultStartNode) errors.push("Missing defaultStartNode");
        if (!this.bookStructure.defaultPOV) errors.push("Missing defaultPOV");
        
        // Check critical path
        if (!this.bookStructure.criticalPath || !Array.isArray(this.bookStructure.criticalPath)) {
            errors.push("Missing or invalid criticalPath");
        } else if (this.bookStructure.criticalPath.length === 0) {
            errors.push("criticalPath is empty");
        } else {
            // Check each node in critical path
            this.bookStructure.criticalPath.forEach((node, index) => {
                if (!node.id) errors.push(`Node at index ${index} is missing id`);
                if (!node.title) errors.push(`Node ${node.id || index} is missing title`);
                if (!node.type) errors.push(`Node ${node.id || index} is missing type`);
            });
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
}

// Create global instance
window.nodeLoader = new NodeLoader();