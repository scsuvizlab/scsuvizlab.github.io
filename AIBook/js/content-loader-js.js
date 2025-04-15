/**
 * contentLoader.js - Content Loading Logic for Life in 2045 Interactive Reader
 * 
 * This module handles loading node content from the NodeLoader and coordinates
 * updates to the UI, sidebar, and navigation when new content is loaded.
 */

class ContentLoader {
    /**
     * Initialize the ContentLoader
     * @param {Object} state - Global application state
     * @param {Object} elements - DOM element references
     * @param {Object} modules - References to other application modules
     */
    constructor(state, elements, modules) {
        this.state = state;
        this.elements = elements;
        this.modules = modules;
    }

    /**
     * Main method to load content by node ID and POV
     * @param {string} nodeId - ID of the node to load
     * @param {string} pov - Character POV to load
     * @returns {Promise} - Promise that resolves when content is loaded
     */
    async loadContent(nodeId, pov) {
        try {
            // Update current state
            this.state.currentNodeId = nodeId;
            this.state.currentPOV = pov;
            
            // Load the node using the NodeLoader
            const node = await this.state.nodeLoader.loadNode(nodeId, pov);
            
            // Update UI components with the new node data
            this.updateAllComponents(node);
            
            // Add to history for back navigation
            // Check if this node is already the last in history to avoid duplicates
            const lastHistoryItem = this.state.history.length > 0 ? 
                this.state.history[this.state.history.length - 1] : null;
                
            if (!lastHistoryItem || 
                lastHistoryItem.nodeId !== nodeId || 
                lastHistoryItem.pov !== pov) {
                this.state.history.push({ nodeId, pov });
            }
            
            // Return the loaded node
            return node;
        } catch (error) {
            this.handleLoadError(error);
        }
    }
    
    /**
     * Load a related non-fiction node
     * @param {number} index - Index of the related non-fiction in the current node
     * @returns {Promise} - Promise that resolves when content is loaded
     */
    async loadRelatedNonFiction(index) {
        try {
            const node = await this.state.nodeLoader.loadRelatedNonFiction(index);
            if (node) {
                // Update state and UI for the non-fiction content
                this.state.currentNodeId = node.id;
                this.updateAllComponents(node);
                
                // Add to history
                this.state.history.push({ 
                    nodeId: node.id, 
                    pov: this.state.currentPOV 
                });
                
                return node;
            }
        } catch (error) {
            this.handleLoadError(error);
        }
    }
    
    /**
     * Load the next node in sequence
     * @returns {Promise} - Promise that resolves when content is loaded
     */
    async loadNextNode() {
        if (this.state.nodeLoader.currentNode && 
            this.state.nodeLoader.currentNode.navigation && 
            this.state.nodeLoader.currentNode.navigation.next) {
            
            return this.loadContent(
                this.state.nodeLoader.currentNode.navigation.next, 
                this.state.currentPOV
            );
        } else {
            // In a demo, could use a hardcoded fallback
            console.warn('No next node defined in navigation');
            return null;
        }
    }
    
    /**
     * Load the previous node in sequence
     * @returns {Promise} - Promise that resolves when content is loaded
     */
    async loadPreviousNode() {
        if (this.state.nodeLoader.currentNode && 
            this.state.nodeLoader.currentNode.navigation && 
            this.state.nodeLoader.currentNode.navigation.previous) {
            
            return this.loadContent(
                this.state.nodeLoader.currentNode.navigation.previous, 
                this.state.currentPOV
            );
        } else {
            console.warn('No previous node defined in navigation');
            return null;
        }
    }
    
    /**
     * Load a branch node
     * @param {number} branchIndex - Index of the branch to follow
     * @returns {Promise} - Promise that resolves when content is loaded
     */
    async loadBranchNode(branchIndex) {
        if (this.state.nodeLoader.currentNode && 
            this.state.nodeLoader.currentNode.navigation &&
            this.state.nodeLoader.currentNode.navigation.branchPoints &&
            this.state.nodeLoader.currentNode.navigation.branchPoints[branchIndex]) {
            
            const branch = this.state.nodeLoader.currentNode.navigation.branchPoints[branchIndex];
            return this.loadContent(branch.targetNodeId, this.state.currentPOV);
        } else {
            console.warn('Invalid branch index or no branch points defined');
            return null;
        }
    }
    
    /**
     * Update all UI components with the new node data
     * @param {Object} node - The loaded node data
     */
    updateAllComponents(node) {
        // Update the main UI
        this.modules.ui.updateContentDisplay(node);
        this.modules.ui.updateBreadcrumb(node, this.state.currentPOV);
        
        // Update the sidebar
        this.modules.sidebar.updateContextSidebar(node);
        
        // Update navigation elements
        this.modules.navigation.setupBranchPoints(node);
        this.modules.navigation.updateNavigationButtons(node);
        
        // Update POV controls
        this.modules.sidebar.setupPOVControls(node, this.state.currentPOV);
    }
    
    /**
     * Handle errors when loading content
     * @param {Error} error - The error that occurred
     */
    handleLoadError(error) {
        console.error('Error loading content:', error);
        
        // Update UI to show error
        this.elements.contentDisplay.innerHTML = `
            <div class="error-message">
                <p>Sorry, there was an error loading the content.</p>
                <p>Error details: ${error.message}</p>
            </div>
        `;
        
        // Hide loading indicator
        this.modules.ui.hideLoadingIndicator();
        
        // Throw the error for further handling if needed
        throw error;
    }
}