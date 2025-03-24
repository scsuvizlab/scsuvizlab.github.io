/**
 * main.js - Application Entry Point for Life in 2045 Interactive Reader
 * Updated to remove hard-coded references and rely fully on book structure
 */

/**
 * Main application initialization
 */
document.addEventListener('DOMContentLoaded', function() {
    // Debug logging function
    function debug(msg, obj) {
        console.log(`DEBUG: ${msg}`, obj);
    }
    
    // Initialize application state with nulls - values will be filled from book structure
    const state = {
        currentNodeId: null,
        currentPOV: null,
        nodeLoader: window.nodeLoader || new NodeLoader(),
        history: [],
        isLoading: false
    };
    
    debug("NodeLoader initialized:", state.nodeLoader);
    
    // DOM element references for use across modules
    const elements = {
        contentDisplay: document.getElementById('content-display'),
        chapterTitle: document.getElementById('chapter-title'),
        breadcrumbTrail: document.getElementById('breadcrumb-trail'),
        loadingIndicator: document.getElementById('loading-indicator'),
        prevButton: document.getElementById('prev-button'),
        nextButton: document.getElementById('next-button'),
        povControls: document.getElementById('pov-controls'),
        sceneContent: document.getElementById('scene-content'),
        contextSidebar: {
            locationInfo: document.getElementById('location-info'),
            timelineInfo: document.getElementById('timeline-info'),
            themeTags: document.getElementById('theme-tags'),
            relatedNonFiction: document.getElementById('related-nonfiction'),
            availablePOVs: document.getElementById('available-povs'),
            readingPath: document.getElementById('reading-path')
        }
    };

    // Log all elements to check if they're found
    debug("DOM Elements:", elements);
    
    // Simple UI controller
    const ui = {
        updateContentDisplay: function(node) {
            debug("Updating content display with node:", node);
            
            // Update chapter title
            let title = node.data.chapterTitle || node.data.label || 'Untitled';
            let subtitle = node.data.subtitle || '';
            
            debug("Setting chapter title to:", { title, subtitle });
            
            if (elements.chapterTitle) {
                elements.chapterTitle.innerHTML = `
                    <h1>${title}</h1>
                    <div class="subtitle">${subtitle}</div>
                `;
            } else {
                console.error("Could not find chapter title element");
            }
            
            // Update scene content
            const content = node.data.content || '<p>No content available for this node.</p>';
            
            debug("Setting scene content to:", content.substring(0, 100) + "...");
            
            // First try scene-content ID
            if (elements.sceneContent) {
                elements.sceneContent.innerHTML = content;
                debug("Content set to scene-content element");
            } 
            // Fall back to content-display if scene-content not found
            else if (elements.contentDisplay) {
                // Try to find a child element for content, or use contentDisplay directly
                const contentContainer = elements.contentDisplay.querySelector('.scene-content') || elements.contentDisplay;
                contentContainer.innerHTML = content;
                debug("Content set to content-display or child element");
            } else {
                console.error("Could not find any content display element");
                // Last resort, try to find element by class
                const contentElements = document.getElementsByClassName('scene-content');
                if (contentElements.length > 0) {
                    contentElements[0].innerHTML = content;
                    debug("Content set to element found by class");
                }
            }
            
            // Display content in console as well for debugging
            console.log("NODE CONTENT:", content);
        },
        
        showLoadingIndicator: function() {
            if (elements.loadingIndicator) {
                elements.loadingIndicator.style.display = 'block';
            }
        },
        
        hideLoadingIndicator: function() {
            if (elements.loadingIndicator) {
                elements.loadingIndicator.style.display = 'none';
            }
        },
        
        showError: function(message) {
            let errorContainer = elements.sceneContent || elements.contentDisplay;
            
            if (errorContainer) {
                errorContainer.innerHTML = `
                    <div class="error-message">
                        <p>Sorry, there was an error:</p>
                        <p>${message}</p>
                    </div>
                `;
            } else {
                alert(`Error: ${message}`);
            }
        }
    };
    
    // Create sidebar controller
    const sidebar = new SidebarController(elements, state);
    
    // Simple navigation manager
    const navigation = {
        updateNavigationButtons: function(node) {
            // Previous button
            const hasPrevious = node.navigation && node.navigation.previous;
            if (elements.prevButton) {
                elements.prevButton.disabled = !hasPrevious;
            }
            
            // Next button
            const hasNext = node.navigation && node.navigation.next;
            if (elements.nextButton) {
                elements.nextButton.disabled = !hasNext;
            }
        }
    };
    
    // Main content loader function
    async function loadContent(nodeId, pov) {
        try {
            // Check if we have valid parameters
            if (!nodeId) {
                throw new Error("No node ID specified");
            }
            
            debug(`Loading content for nodeId: ${nodeId}, POV: ${pov}`);
            ui.showLoadingIndicator();
            
            // Update current state
            state.currentNodeId = nodeId;
            state.currentPOV = pov;
            
            // Load the node using the NodeLoader
            const node = await state.nodeLoader.loadNode(nodeId, pov);
            debug("Loaded node:", node);
            
            // Update UI components with the new node data
            ui.updateContentDisplay(node);
            sidebar.updateContextSidebar(node);
            navigation.updateNavigationButtons(node);
            sidebar.setupPOVControls(node, pov);
            
            // Add to history for back navigation
            state.history.push({ nodeId, pov });
            
            ui.hideLoadingIndicator();
            
            // Return the loaded node
            return node;
        } catch (error) {
            console.error('Error loading content:', error);
            
            ui.showError(`Failed to load content: ${error.message}`);
            
            ui.hideLoadingIndicator();
            throw error;
        }
    }
    
    // Set up navigation button handlers
    if (elements.prevButton) {
        elements.prevButton.addEventListener('click', async () => {
            debug("Previous button clicked");
            try {
                if (state.nodeLoader.currentNode && 
                    state.nodeLoader.currentNode.navigation && 
                    state.nodeLoader.currentNode.navigation.previous) {
                    
                    await loadContent(
                        state.nodeLoader.currentNode.navigation.previous, 
                        state.currentPOV
                    );
                } else {
                    // Try to use book structure for previous node
                    const prevNodeId = state.nodeLoader.getPreviousNodeInCriticalPath(state.currentNodeId);
                    if (prevNodeId) {
                        await loadContent(prevNodeId, state.currentPOV);
                    }
                }
            } catch (error) {
                console.error("Failed to navigate to previous node:", error);
            }
        });
    }
    
    if (elements.nextButton) {
        elements.nextButton.addEventListener('click', async () => {
            debug("Next button clicked");
            try {
                if (state.nodeLoader.currentNode && 
                    state.nodeLoader.currentNode.navigation && 
                    state.nodeLoader.currentNode.navigation.next) {
                    
                    await loadContent(
                        state.nodeLoader.currentNode.navigation.next, 
                        state.currentPOV
                    );
                } else {
                    // Try to use book structure for next node
                    const nextNodeId = state.nodeLoader.getNextNodeInCriticalPath(state.currentNodeId);
                    if (nextNodeId) {
                        await loadContent(nextNodeId, state.currentPOV);
                    }
                }
            } catch (error) {
                console.error("Failed to navigate to next node:", error);
            }
        });
    }
    
    // Custom event listeners
    document.addEventListener('navigateToNode', (event) => {
        debug("navigateToNode event received:", event.detail);
        const { nodeId, pov } = event.detail;
        loadContent(nodeId, pov || state.currentPOV);
    });
    
    document.addEventListener('changePOV', (event) => {
        debug("changePOV event received:", event.detail);
        const { nodeId, pov } = event.detail;
        loadContent(nodeId || state.currentNodeId, pov);
    });
    
    document.addEventListener('loadRelatedNonFiction', (event) => {
        debug("loadRelatedNonFiction event received:", event.detail);
        const { nodeId, index } = event.detail;
        
        if (nodeId) {
            // Load specific non-fiction node
            loadContent(nodeId, state.currentPOV);
        } else if (index !== undefined && 
                  state.nodeLoader.currentNode && 
                  state.nodeLoader.currentNode.navigation && 
                  state.nodeLoader.currentNode.navigation.relatedNonFiction &&
                  state.nodeLoader.currentNode.navigation.relatedNonFiction[index]) {
            
            const relatedNodeId = state.nodeLoader.currentNode.navigation.relatedNonFiction[index];
            loadContent(relatedNodeId, state.currentPOV);
        } else {
            console.warn("Could not find related non-fiction content");
        }
    });
    
    // Listen for book structure loaded event
    document.addEventListener('bookStructureLoaded', (event) => {
        debug("Book structure loaded:", event.detail);
        const { bookStructure, defaultStartNodeId, defaultPOV } = event.detail;
        
        // Set default values from book structure
        if (!state.currentNodeId && defaultStartNodeId) {
            state.currentNodeId = defaultStartNodeId;
        }
        
        if (!state.currentPOV && defaultPOV) {
            state.currentPOV = defaultPOV;
        }
        
        // Now that we have the book structure and defaults, load the initial content
        if (state.currentNodeId) {
            loadContent(state.currentNodeId, state.currentPOV).catch(error => {
                console.error("Failed to load initial content:", error);
                
                // If the start node fails, try to load the first node in critical path
                if (bookStructure && 
                    bookStructure.criticalPath && 
                    bookStructure.criticalPath.length > 0) {
                    
                    const firstNode = bookStructure.criticalPath[0];
                    loadContent(firstNode.id, firstNode.defaultPOV || state.currentPOV).catch(e => {
                        console.error("Failed to load fallback node:", e);
                        ui.showError("Failed to load any content. Please check your book structure.");
                    });
                } else {
                    ui.showError("Failed to load initial content and no fallback available.");
                }
            });
        } else {
            ui.showError("No default start node defined in book structure.");
        }
    });
    
    // Handle book structure load failure
    document.addEventListener('bookStructureLoadFailed', (event) => {
        debug("Book structure load failed:", event.detail);
        ui.showError(`Failed to load book structure: ${event.detail.error}`);
    });
    
    // Register loading callbacks to show/hide loading indicator
    state.nodeLoader.onLoading(
        () => {
            state.isLoading = true;
            ui.showLoadingIndicator();
        },
        () => {
            state.isLoading = false;
            ui.hideLoadingIndicator();
        }
    );
    
    console.log('Life in 2045 Reader initialized - waiting for book structure');
    
    // The initial content loading will happen after book structure is loaded
    // via the bookStructureLoaded event listener above
});

/**
 * Handles unhandled errors at the application level
 */
window.addEventListener('error', function(event) {
    console.error('Application Error:', event.error);
    alert('An error occurred. Please check the console for details.');
});