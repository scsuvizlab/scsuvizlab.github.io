/**
 * Enhanced NodeLoader for Life in 2045 Interactive Book
 * Updated to prioritize local navigation, fallback to critical path order
 */

class NodeLoader {
    constructor() {
        this.cache = {};
        this.currentNode = null;
        this.history = []; // History of {nodeId, pov} objects
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
            const response = await fetch('./content/book-structure.json');
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
                    // Try to get base node info for context
                    const baseNodeInfo = this.getNodeDefinition(baseNodeId);
                    return {
                        id: nodeId,
                        title: `${baseNodeInfo?.title || baseNodeId} (${povNode.character} POV)`,
                        type: "fiction", // Assume POV is fiction
                        chapter: baseNodeInfo?.chapter, // Inherit chapter from base node
                        defaultPOV: povNode.character,
                        filePath: povNode.filePath
                    };
                }
            }
        }

        // Check tracks for non-fiction nodes (or other track types)
        if (this.bookStructure.tracks) {
            for (const trackId in this.bookStructure.tracks) {
                const track = this.bookStructure.tracks[trackId];
                if (track.nodeSequence && track.nodeSequence.includes(nodeId)) {
                    return {
                        id: nodeId,
                        title: this.formatNodeTitle(nodeId), // Basic title from ID
                        type: trackId === "nonfiction" ? "nonfiction" : "fiction", // Infer type from track
                        defaultPOV: this.bookStructure.defaultPOV || "Omniscient",
                        filePath: this.inferFilePath(nodeId, trackId) // Infer path based on type/ID
                    };
                }
            }
        }

        console.warn(`Node definition not found for ID: ${nodeId}`);
        return null; // Node not found in defined structures
    }

    /**
     * Format a node ID into a readable title
     * @param {string} nodeId - The node ID to format
     * @returns {string} - A formatted title
     */
    formatNodeTitle(nodeId) {
        return nodeId
            .replace(/^(ch\d+|nf)-/, '') // Remove common prefixes
            .replace(/-pov$/, '') // Remove -pov suffix if present
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Infer a file path from a node ID and track/type
     * @param {string} nodeId - The node ID
     * @param {string} trackOrType - The track ID or node type ('fiction'/'nonfiction')
     * @returns {string} - The inferred file path relative to 'content/'
     */
    inferFilePath(nodeId, trackOrType) {
        if (trackOrType === "nonfiction" || nodeId.startsWith('nf-')) {
            return `nonfiction/${nodeId}.json`;
        } else if (nodeId.includes('-pov')) {
            // Assume POV files are in a specific subdirectory
            return `fiction/character_povs/${nodeId}.json`;
        } else {
            // Assume other fiction nodes might be in critical_path or just fiction root
            // This might need refinement based on actual project structure
             return `fiction/${nodeId}.json`; // Or maybe fiction/critical_path/
        }
    }

    /**
     * Load a content node by ID and character perspective
     * @param {string} nodeId - Unique identifier for the node
     * @param {string} [povCharacter=null] - Character POV to load (optional, uses default if not specified)
     * @param {boolean} [addToHistory=true] - Whether to add this node load to navigation history
     * @returns {Promise<Object>} Promise resolving to the node data
     */
    async loadNode(nodeId, povCharacter = null, addToHistory = true) {
        this._triggerLoadingStart();

        try {
            // Wait for book structure to be loaded if it's not yet
            if (!this.bookStructure) {
                console.log("Waiting for book structure to load...");
                await new Promise((resolve, reject) => {
                    const checkInterval = setInterval(() => {
                        if (this.bookStructure) {
                            clearInterval(checkInterval);
                            resolve();
                        }
                    }, 100);
                    // Set a timeout
                    setTimeout(() => {
                        clearInterval(checkInterval);
                        if (!this.bookStructure) {
                            reject(new Error("Book structure failed to load within timeout"));
                        } else {
                             resolve();
                        }
                    }, 5000);
                });
            }

            // Use default POV if none specified or if specified POV doesn't exist for this node
            let effectivePOV = povCharacter || this.defaultPOV || "Omniscient";
            let targetNodeId = nodeId;
            let targetFilePath = null;
            let isPovVersion = false;

            // Check if a specific POV version exists for the base nodeId
            if (povCharacter && this.bookStructure.characterPOVs && this.bookStructure.characterPOVs[nodeId]) {
                const povVersions = this.bookStructure.characterPOVs[nodeId];
                const matchingPOV = povVersions.find(pov => pov.character === povCharacter);
                if (matchingPOV) {
                    targetNodeId = matchingPOV.nodeId;
                    targetFilePath = matchingPOV.filePath;
                    effectivePOV = povCharacter; // Confirm POV being loaded
                    isPovVersion = true;
                    console.log(`Found POV version: ID=${targetNodeId}, Path=${targetFilePath}`);
                } else {
                     console.log(`POV '${povCharacter}' not found for base node '${nodeId}'. Loading base node.`);
                     // If specified POV doesn't exist, load the base node with its default POV or the global default
                     const baseNodeDef = this.getNodeDefinition(nodeId);
                     effectivePOV = (baseNodeDef && baseNodeDef.defaultPOV) ? baseNodeDef.defaultPOV : (this.defaultPOV || "Omniscient");
                }
            } else if (!povCharacter) {
                 // If no POV requested, use the node's default or global default
                 const baseNodeDef = this.getNodeDefinition(nodeId);
                 effectivePOV = (baseNodeDef && baseNodeDef.defaultPOV) ? baseNodeDef.defaultPOV : (this.defaultPOV || "Omniscient");
            }

             console.log(`Attempting to load: Node=${targetNodeId}, Effective POV=${effectivePOV}`);


            // If we didn't get a specific file path from POV lookup, try the node definition
            if (!targetFilePath) {
                 const nodeDefinition = this.getNodeDefinition(targetNodeId);
                 if (nodeDefinition && nodeDefinition.filePath) {
                    targetFilePath = nodeDefinition.filePath;
                    console.log(`Using path from node definition: ${targetFilePath}`);
                }
            }

            // Fetch the target node content
            const node = await this._fetchNode(targetNodeId, targetFilePath);

            // --- History Management ---
            if (addToHistory) {
                 const currentHistoryItem = this.history.length > 0 ? this.history[this.history.length - 1] : null;
                 // Add to history only if it's different from the last entry
                 if (!currentHistoryItem || currentHistoryItem.nodeId !== targetNodeId || currentHistoryItem.pov !== effectivePOV) {
                     this.history.push({
                        nodeId: targetNodeId, // Store the ID of the node actually loaded
                        pov: effectivePOV, // Store the POV actually used
                        timestamp: new Date().toISOString()
                    });
                     console.log(`History updated. New length: ${this.history.length}`, this.history);
                 } else {
                      console.log("Skipping history update, same node/pov as last entry.");
                 }
            } else {
                 console.log("Skipping history update as requested.");
            }

            this.currentNode = node; // Update the current node reference

            this._triggerLoadingEnd();
            return node;
        } catch (error) {
            console.error('Error in loadNode:', error);
            this._triggerLoadingEnd();
            throw error;
        }
    }


    /**
     * Fetch a node from cache or server
     * @private
     * @param {string} nodeId - ID of the node to fetch
     * @param {string} [filePath=null] - Optional file path relative to 'content/'
     * @returns {Promise<Object>} Promise resolving to the node data
     */
    async _fetchNode(nodeId, filePath = null) {
        // Check cache first
        if (this.cache[nodeId]) {
            console.log(`Using cached node: ${nodeId}`);
            return this.cache[nodeId];
        }

        console.log(`Workspaceing node: ${nodeId}`);
        let loadedData = null;
        let triedPaths = [];

        // Construct potential paths
        const pathsToTry = [];
        if (filePath) {
             pathsToTry.push(`content/${filePath}`);
        }
        // Add path from definition if different and not already tried
        const nodeDefinition = this.getNodeDefinition(nodeId);
        if (nodeDefinition && nodeDefinition.filePath && !pathsToTry.includes(`content/${nodeDefinition.filePath}`)) {
             pathsToTry.push(`content/${nodeDefinition.filePath}`);
        }
        // Add inferred path as a final fallback
        const inferredPath = `content/${this.inferFilePath(nodeId, nodeDefinition?.type || 'fiction')}`;
        if (!pathsToTry.includes(inferredPath)) {
             pathsToTry.push(inferredPath);
        }

        // Try fetching from potential paths
        for (const path of pathsToTry) {
            triedPaths.push(path);
            try {
                console.log(`Trying path: ${path}`);
                const response = await fetch(path);
                if (response.ok) {
                    loadedData = await response.json();
                    console.log(`Successfully loaded node from: ${path}`);
                    break; // Stop trying once loaded
                } else {
                    console.warn(`File not found or error at path: ${path} (Status: ${response.status})`);
                }
            } catch (error) {
                console.warn(`Error fetching from path ${path}: ${error.message}`);
            }
        }

        // If data was loaded successfully
        if (loadedData) {
            this.cache[nodeId] = loadedData;
            return loadedData;
        } else {
            // If fetch failed after trying all paths, create a simulated node
            console.log(`Failed to load node ${nodeId} from paths: ${triedPaths.join(', ')}. Creating simulated node.`);
            const simulatedNode = this._createSimulatedNode(nodeId);
            this.cache[nodeId] = simulatedNode; // Cache the simulated node
            return simulatedNode;
        }
    }


    /**
     * Create a simulated node for testing or error recovery
     * @private
     * @param {string} nodeId - ID of the node to create
     * @returns {Object} Simulated node data
     */
    _createSimulatedNode(nodeId) {
        console.log(`Creating simulated node for: ${nodeId}`);
        const nodeDefinition = this.getNodeDefinition(nodeId); // Get definition to infer properties

        const title = nodeDefinition?.title || this.formatNodeTitle(nodeId);
        const nodeType = nodeDefinition?.type || (nodeId.startsWith('nf-') ? 'nonfiction' : 'fiction');
        const chapterId = nodeDefinition?.chapter;
        const defaultPOV = nodeDefinition?.defaultPOV || this.defaultPOV || "Omniscient";

        let chapterTitle = "Unknown Chapter";
        if (chapterId && this.bookStructure?.chapters) {
            const chapter = this.bookStructure.chapters.find(ch => ch.id === chapterId);
            chapterTitle = chapter?.title || chapterTitle;
        }

        const content = `<p><b>Simulated Content</b></p><p>Content for node "<b>${nodeId}</b>" could not be loaded.</p><p>Path(s) attempted: ${nodeDefinition?.filePath ? `content/${nodeDefinition.filePath}` : 'N/A'}</p>`;

        const node = {
            id: nodeId, // Ensure the ID matches the requested ID
            nodeId: nodeId, // Include nodeId property as seen in some examples
            nodeType: nodeType, // Include nodeType property
            data: {
                label: title,
                content: content,
                chapterTitle: chapterTitle, // Use determined chapter title
                subtitle: `(${nodeType})`, // Indicate type in subtitle
                location: "Simulated Location",
                timeline: "2045",
                tags: ["simulated", "error"],
                branchPoints: [] // Default to empty
            },
            metadata: {
                 povCharacter: defaultPOV, // Use determined default POV
                 simulated: true // Flag as simulated
            },
            navigation: { // Ensure navigation object exists
                next: null,
                previous: null,
                alternateVersions: [], // Default to empty
                relatedNonFiction: [] // Default to empty
            }
        };

        // Attempt to set navigation based on critical path order (if applicable)
        if (this.bookStructure?.criticalPath) {
            const currentIndex = this.bookStructure.criticalPath.findIndex(n => n.id === nodeId);
            if (currentIndex > 0) {
                node.navigation.previous = this.bookStructure.criticalPath[currentIndex - 1].id;
            }
            if (currentIndex !== -1 && currentIndex < this.bookStructure.criticalPath.length - 1) {
                 // Only set next if not already defined (though it shouldn't be for simulated)
                if (!node.navigation.next) {
                     node.navigation.next = this.bookStructure.criticalPath[currentIndex + 1].id;
                }
            }
        }

        // Add related/POVs if defined in book structure, even if target files are missing
        if (this.bookStructure?.relatedContent?.[nodeId]) {
             node.navigation.relatedNonFiction = this.bookStructure.relatedContent[nodeId];
        }
        if (this.bookStructure?.characterPOVs?.[nodeId]) {
            node.navigation.alternateVersions = this.bookStructure.characterPOVs[nodeId].map(pov => ({
                povCharacter: pov.character,
                nodeId: pov.nodeId // Keep the reference ID even if file missing
            }));
        }


        console.log("Simulated node created:", node);
        return node;
    }


    /**
     * Navigate to the next node in sequence (prioritizing local, then critical path)
     * @returns {Promise<Object>} Promise resolving to the next node data
     */
    async loadNextNode() {
        if (!this.currentNode) {
            throw new Error('No current node');
        }

        // 1. Prioritize local navigation.next from the node file
        if (this.currentNode.navigation && this.currentNode.navigation.next) {
            console.log(`Navigating Next (Local): ${this.currentNode.navigation.next}`);
            // Ensure POV is passed correctly; use current if available, else default
            const povToLoad = this.currentNode.metadata?.povCharacter || this.defaultPOV;
            return this.loadNode(this.currentNode.navigation.next, povToLoad);
        }

        // 2. Fallback: Use criticalPath order from book structure
        const nextNodeIdFromPath = this.getNextNodeInCriticalPath(this.currentNode.id);
        if (nextNodeIdFromPath) {
             console.log(`Navigating Next (Critical Path Fallback): ${nextNodeIdFromPath}`);
             // Use default POV for the next node from critical path, or loader's default
             const nextNodeDef = this.getNodeDefinition(nextNodeIdFromPath);
             const povToLoad = (nextNodeDef && nextNodeDef.defaultPOV) ? nextNodeDef.defaultPOV : this.defaultPOV;
            return this.loadNode(nextNodeIdFromPath, povToLoad);
        }

        // 3. No next node found
        console.warn('No next node defined in local navigation or critical path order');
        throw new Error('No next node defined');
    }


    /**
     * Navigate to the previous node (prioritizing history, then local, then critical path)
     * @returns {Promise<Object>} Promise resolving to the previous node data
     */
     async loadPreviousNode() {
        // 1. Prioritize navigation history for a true "back" experience
        if (this.history && this.history.length > 1) {
             // Temporarily remove the current state to see the previous one
             const currentState = this.history.pop();
             const previousState = this.history[this.history.length - 1]; // Peek at the last element

             console.log(`Navigating Previous (History): Node=${previousState.nodeId}, POV=${previousState.pov}`);

             // We call loadNode directly, but tell it NOT to add to history again.
             try {
                  const loadedNode = await this.loadNode(previousState.nodeId, previousState.pov, false);
                  // History should now correctly reflect the state we just loaded.
                  return loadedNode;
             } catch(error) {
                  console.error("Failed to navigate to previous node from history:", error);
                  // Put the current state back if loading the previous one failed
                  this.history.push(currentState);
                  throw error; // Re-throw error after attempting recovery
             }
        }

        console.warn("No previous node in history. Trying other methods.");

        // 2. Fallback: Check local navigation.previous (if history is empty/disabled)
        if (this.currentNode?.navigation?.previous) {
             console.log(`Navigating Previous (Local Fallback): ${this.currentNode.navigation.previous}`);
             const povToLoad = this.currentNode.metadata?.povCharacter || this.defaultPOV;
             // Add to history since we are jumping via link, not going 'back'
             return this.loadNode(this.currentNode.navigation.previous, povToLoad, true);
        }

        // 3. Fallback: Use criticalPath order from book structure
        const previousNodeIdFromPath = this.getPreviousNodeInCriticalPath(this.currentNode?.id);
        if (previousNodeIdFromPath) {
            console.log(`Navigating Previous (Critical Path Fallback): ${previousNodeIdFromPath}`);
            const prevNodeDef = this.getNodeDefinition(previousNodeIdFromPath);
            const povToLoad = (prevNodeDef && prevNodeDef.defaultPOV) ? prevNodeDef.defaultPOV : this.defaultPOV;
            // Add to history since we are jumping via fallback
            return this.loadNode(previousNodeIdFromPath, povToLoad, true);
        }

        // 4. No previous node found
        console.warn('No previous node found in history, local navigation, or critical path order');
        throw new Error('No previous node defined');
    }


    /**
     * Load a related non-fiction node
     * @param {number} index - Index in the related non-fiction array
     * @returns {Promise<Object|null>} Promise resolving to the related node or null
     */
    async loadRelatedNonFiction(index) {
        if (!this.currentNode?.navigation?.relatedNonFiction?.[index]) {
            console.warn("No related non-fiction content at index", index);
            return null;
        }

        const relatedNodeId = this.currentNode.navigation.relatedNonFiction[index];
        // Load related non-fiction, use default POV for non-fiction usually
        return this.loadNode(relatedNodeId, this.defaultPOV);
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
     * @returns {Array<{nodeId: string, pov: string, timestamp: string}>} Array of visited nodes/povs
     */
    getHistory() {
        return [...this.history];
    }

    /**
     * Clear the node cache
     */
    clearCache() {
        this.cache = {};
        console.log("Node cache cleared.");
    }

    /**
     * Get a node from the critical path definition
     * @param {string} nodeId - Node ID to find
     * @returns {Object|null} Node definition from critical path or null
     */
    getNodeInCriticalPath(nodeId) {
        if (!this.bookStructure?.criticalPath) return null;
        return this.bookStructure.criticalPath.find(node => node.id === nodeId);
    }

    /**
     * Get the next node ID in the critical path order
     * @param {string} currentNodeId - Current node ID
     * @returns {string|null} Next node ID based on order or null
     */
     getNextNodeInCriticalPath(currentNodeId) {
        if (!this.bookStructure?.criticalPath) return null;

        const currentIndex = this.bookStructure.criticalPath.findIndex(node => node.id === currentNodeId);
        // Ensure currentIndex is valid and not the last element
        if (currentIndex !== -1 && currentIndex < this.bookStructure.criticalPath.length - 1) {
            // Return the ID of the next node in the array based on order
            return this.bookStructure.criticalPath[currentIndex + 1].id;
        }

        return null; // No next node found in the critical path order
    }


    /**
     * Get the previous node ID in the critical path order
     * @param {string} currentNodeId - Current node ID
     * @returns {string|null} Previous node ID based on order or null
     */
    getPreviousNodeInCriticalPath(currentNodeId) {
        if (!this.bookStructure?.criticalPath) return null;

        const currentIndex = this.bookStructure.criticalPath.findIndex(node => node.id === currentNodeId);
        if (currentIndex > 0) { // Ensure currentIndex is valid and not the first element
            // Return the ID of the previous node in the array based on order
            return this.bookStructure.criticalPath[currentIndex - 1].id;
        }

        return null; // No previous node found in the critical path order
    }


    /**
     * Get all nodes IDs in a specific chapter
     * @param {string} chapterId - Chapter ID
     * @returns {Array<string>} Array of node IDs in the chapter
     */
    getNodesInChapter(chapterId) {
        if (!this.bookStructure?.chapters) return [];
        const chapter = this.bookStructure.chapters.find(ch => ch.id === chapterId);
        return chapter?.nodes || [];
    }

    /**
     * Get all available character POVs for a node (from book structure)
     * @param {string} nodeId - Node ID
     * @returns {Array<string>} Array of character POV strings (e.g., "Nicole")
     */
    getAvailablePOVs(nodeId) {
        // Use optional chaining for safer access
        const povs = this.bookStructure?.characterPOVs?.[nodeId];
        return povs ? povs.map(pov => pov.character) : [];
    }


    /**
     * Get all related non-fiction for a node (from book structure)
     * @param {string} nodeId - Node ID
     * @returns {Array<string>} Array of related non-fiction node IDs
     */
    getRelatedNonFiction(nodeId) {
         // Use optional chaining
        return this.bookStructure?.relatedContent?.[nodeId] || [];
    }

    /**
     * Get all available reading tracks
     * @returns {Object} Object of track definitions
     */
    getAvailableTracks() {
        return this.bookStructure?.tracks || {};
    }

    /**
     * Get node IDs in a specific track sequence
     * @param {string} trackId - Track ID
     * @returns {Array<string>} Array of node IDs in the track sequence
     */
    getNodesInTrack(trackId) {
        return this.bookStructure?.tracks?.[trackId]?.nodeSequence || [];
    }

    /**
     * Get all defined characters
     * @returns {Array<Object>} Array of character definitions
     */
    getCharacters() {
        return this.bookStructure?.characters || [];
    }

    /**
     * Validate the loaded book structure format
     * @returns {{valid: boolean, errors: string[]}} Validation results
     */
    validateBookStructure() {
        if (!this.bookStructure) {
            return { valid: false, errors: ["Book structure not loaded"] };
        }

        const errors = [];
        const requiredProps = ['title', 'defaultStartNode', 'defaultPOV', 'criticalPath', 'chapters'];
        requiredProps.forEach(prop => {
            if (!this.bookStructure.hasOwnProperty(prop)) errors.push(`Missing top-level property: ${prop}`);
        });

        if (!Array.isArray(this.bookStructure.criticalPath)) {
            errors.push("criticalPath is not an array");
        } else if (this.bookStructure.criticalPath.length === 0) {
            // Allow empty critical path if structure is minimal/new
            // errors.push("criticalPath is empty");
        } else {
            const nodeIds = new Set();
            this.bookStructure.criticalPath.forEach((node, index) => {
                if (!node.id) errors.push(`Node in criticalPath at index ${index} is missing id`);
                else if (nodeIds.has(node.id)) errors.push(`Duplicate node id in criticalPath: ${node.id}`);
                else nodeIds.add(node.id);
                if (!node.filePath) errors.push(`Node ${node.id || index} in criticalPath is missing filePath`);
                // No longer checking for nextNode here
            });
        }

         if (!Array.isArray(this.bookStructure.chapters)) {
            errors.push("chapters is not an array");
        }

        // Add more checks for tracks, POVs, relatedContent as needed

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
}

// Create global instance if it doesn't exist
if (!window.nodeLoader) {
     window.nodeLoader = new NodeLoader();
}