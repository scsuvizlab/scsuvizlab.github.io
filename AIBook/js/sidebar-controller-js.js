/**
 * Enhanced sidebar-controller-js.js - Sidebar Management with Book Structure Support
 */

// Define the SidebarController class
class SidebarController {
    /**
     * Initialize the SidebarController
     * @param {Object} elements - DOM element references
     * @param {Object} state - Global application state
     */
    constructor(elements, state) {
        this.elements = elements;
        this.state = state;
        this.contextSidebar = elements.contextSidebar;
    }

    /**
     * Update all sections of the context sidebar
     * @param {Object} node - The current node data
     */
    updateContextSidebar(node) {
        this.updateSceneInformation(node);
        this.updateRelatedNonFiction(node);
        this.updateAvailablePOVs(node);
        this.updateReadingPath(node);
        this.updateBookNavigator(node);
    }
    
    /**
     * Update scene information (location, timeline, themes)
     * @param {Object} node - The current node data
     */
    updateSceneInformation(node) {
        // Update location
        if (this.contextSidebar.locationInfo) {
            this.contextSidebar.locationInfo.textContent = 
                node.data.location || 'Unknown location';
        }
            
        // Update timeline
        if (this.contextSidebar.timelineInfo) {
            this.contextSidebar.timelineInfo.textContent = 
                node.data.timeline || 'Present day';
        }
            
        // Update theme tags
        if (this.contextSidebar.themeTags) {
            this.updateThemeTags(node.data.tags || []);
        }
    }
    
    /**
     * Update theme tags display
     * @param {Array} tags - Array of theme tags
     */
    updateThemeTags(tags) {
        const container = this.contextSidebar.themeTags;
        if (!container) return;
        
        container.innerHTML = '';
        
        if (tags.length === 0) {
            container.innerHTML = '<em>No themes specified</em>';
            return;
        }
        
        tags.forEach(tag => {
            const tagElement = document.createElement('div');
            tagElement.className = 'tag';
            tagElement.textContent = tag;
            container.appendChild(tagElement);
        });
    }
    
    /**
     * Update related non-fiction links
     * @param {Object} node - The current node data
     */
    updateRelatedNonFiction(node) {
        const container = this.contextSidebar.relatedNonFiction;
        if (!container) return;
        
        container.innerHTML = '';
        
        // First try to get related content from node data
        let relatedNodes = node.navigation?.relatedNonFiction || [];
        
        // If empty, try to get from book structure
        if (relatedNodes.length === 0 && this.state.nodeLoader.bookStructure) {
            relatedNodes = this.state.nodeLoader.getRelatedNonFiction(node.id) || [];
        }
        
        if (relatedNodes.length === 0) {
            container.innerHTML = '<em>No related content available</em>';
            return;
        }
        
        relatedNodes.forEach((relatedNodeId, index) => {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'related-link';
            
            // Try to get title from book structure
            let title = relatedNodeId;
            if (this.state.nodeLoader.bookStructure) {
                const nodeInfo = this.state.nodeLoader.bookStructure.criticalPath.find(n => n.id === relatedNodeId);
                if (nodeInfo) {
                    title = nodeInfo.title;
                } else {
                    // Try to parse from the ID
                    title = relatedNodeId.replace('nf-', '').split('-').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ');
                }
            }
            
            link.textContent = title;
            
            // Create a closure to preserve the index
            link.addEventListener('click', (e) => {
                e.preventDefault();
                // We'll trigger a custom event that the contentLoader will listen for
                const event = new CustomEvent('loadRelatedNonFiction', {
                    detail: { index, nodeId: relatedNodeId }
                });
                document.dispatchEvent(event);
            });
            
            container.appendChild(link);
        });
    }
    
    /**
     * Update available character POVs in the sidebar
     * @param {Object} node - The current node data
     */
    updateAvailablePOVs(node) {
        const container = this.contextSidebar.availablePOVs;
        if (!container) return;
        
        container.innerHTML = '';
        
        // Get available POVs from the node
        const availablePOVs = this.getAvailablePOVs(node);
        
        if (availablePOVs.length === 0) {
            container.innerHTML = '<em>No alternative perspectives available</em>';
            return;
        }
        
        availablePOVs.forEach(pov => {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'related-link';
            
            if (pov === this.state.currentPOV) {
                link.classList.add('active');
                link.textContent = `${pov} (Current)`;
            } else {
                link.textContent = pov;
            }
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                // Trigger a custom event to load the content with new POV
                const event = new CustomEvent('changePOV', {
                    detail: { 
                        nodeId: this.state.currentNodeId, 
                        pov: pov 
                    }
                });
                document.dispatchEvent(event);
            });
            
            container.appendChild(link);
        });
    }
    
    /**
     * Update reading path in the sidebar
     * @param {Object} node - The current node data
     */
    updateReadingPath(node) {
        const container = this.contextSidebar.readingPath;
        if (!container) return;
        
        container.innerHTML = '';
        
        // Get reading path from navigation if available
        const previous = node.navigation?.previous;
        const next = node.navigation?.next;
        
        // Create a simple reading path with previous, current, and next
        const readingPath = [];
        
        if (previous) {
            // Try to get info from book structure
            let prevLabel = 'Previous Scene';
            if (this.state.nodeLoader.bookStructure) {
                const prevNode = this.state.nodeLoader.getNodeInCriticalPath(previous);
                if (prevNode) {
                    prevLabel = prevNode.title;
                }
            }
            
            readingPath.push({
                id: previous,
                label: prevLabel,
                isCurrent: false
            });
        }
        
        // Current node
        let currentLabel = node.data.label || 'Current Scene';
        if (this.state.nodeLoader.bookStructure) {
            const currentNodeInfo = this.state.nodeLoader.getNodeInCriticalPath(node.id);
            if (currentNodeInfo) {
                currentLabel = currentNodeInfo.title;
            }
        }
        
        readingPath.push({
            id: node.id,
            label: currentLabel,
            isCurrent: true
        });
        
        if (next) {
            // Try to get info from book structure
            let nextLabel = 'Next Scene';
            if (this.state.nodeLoader.bookStructure) {
                const nextNode = this.state.nodeLoader.getNodeInCriticalPath(next);
                if (nextNode) {
                    nextLabel = nextNode.title;
                }
            }
            
            readingPath.push({
                id: next,
                label: nextLabel,
                isCurrent: false
            });
        }
        
        // If we couldn't get a proper reading path, create a default one
        if (readingPath.length === 1 && this.state.nodeLoader.bookStructure) {
            const currentIndex = this.state.nodeLoader.bookStructure.criticalPath.findIndex(n => n.id === node.id);
            
            if (currentIndex > 0) {
                const prevNode = this.state.nodeLoader.bookStructure.criticalPath[currentIndex - 1];
                readingPath.unshift({
                    id: prevNode.id,
                    label: prevNode.title,
                    isCurrent: false
                });
            }
            
            if (currentIndex < this.state.nodeLoader.bookStructure.criticalPath.length - 1) {
                const nextNode = this.state.nodeLoader.bookStructure.criticalPath[currentIndex + 1];
                readingPath.push({
                    id: nextNode.id,
                    label: nextNode.title,
                    isCurrent: false
                });
            }
        }
        
        // Render the reading path
        readingPath.forEach(item => {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'related-link';
            
            if (item.isCurrent) {
                link.classList.add('active');
            }
            
            link.textContent = item.label;
            
            if (!item.isCurrent) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    // Trigger a custom event to load the content
                    const event = new CustomEvent('navigateToNode', {
                        detail: { 
                            nodeId: item.id, 
                            pov: this.state.currentPOV 
                        }
                    });
                    document.dispatchEvent(event);
                });
            }
            
            container.appendChild(link);
        });
    }
    
    /**
     * Update the book navigator sidebar with nodes from current chapter and book structure
     * @param {Object} currentNode - The current node data
     */
    updateBookNavigator(currentNode) {
        const container = document.getElementById('book-navigator');
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        // If we don't have book structure data, show a message
        if (!this.state.nodeLoader.bookStructure) {
            container.innerHTML = '<div class="nav-loading">Book structure not available</div>';
            return;
        }
        
        const bookStructure = this.state.nodeLoader.bookStructure;
        const currentNodeId = currentNode.id;
        
        // Find current node in critical path to get chapter info
        const pathNode = bookStructure.criticalPath.find(node => node.id === currentNodeId);
        const currentChapter = pathNode ? pathNode.chapter : null;
        
        // If we have a chapter, show nodes from that chapter
        if (currentChapter) {
            const chapterInfo = bookStructure.chapters.find(ch => ch.id === currentChapter);
            if (chapterInfo) {
                // Add chapter header
                const chapterHeader = document.createElement('div');
                chapterHeader.className = 'chapter-divider';
                chapterHeader.textContent = chapterInfo.title;
                container.appendChild(chapterHeader);
                
                // Add nodes from this chapter
                if (chapterInfo.nodes && chapterInfo.nodes.length > 0) {
                    chapterInfo.nodes.forEach(nodeId => {
                        const nodeInfo = bookStructure.criticalPath.find(n => n.id === nodeId);
                        if (nodeInfo) {
                            const nodeLink = this.createNodeLink(nodeInfo, nodeId === currentNodeId);
                            container.appendChild(nodeLink);
                        }
                    });
                }
            }
        }
        
        // Find current node index in critical path
        const currentIndex = bookStructure.criticalPath.findIndex(node => node.id === currentNodeId);
        
        // If not in a chapter or not found in critical path, show surrounding nodes
        if (!currentChapter || currentIndex === -1) {
            // Show a header
            const surroundingHeader = document.createElement('div');
            surroundingHeader.className = 'chapter-divider';
            surroundingHeader.textContent = 'Navigation';
            container.appendChild(surroundingHeader);
            
            // Get surrounding nodes
            if (currentIndex !== -1) {
                const start = Math.max(0, currentIndex - 2);
                const end = Math.min(bookStructure.criticalPath.length - 1, currentIndex + 2);
                
                for (let i = start; i <= end; i++) {
                    const nodeInfo = bookStructure.criticalPath[i];
                    const nodeLink = this.createNodeLink(nodeInfo, i === currentIndex);
                    container.appendChild(nodeLink);
                }
            } else {
                // Show direct navigation
                this.displayDirectNavigation(container, currentNode);
            }
        }
        
        // Add tracks section
        if (bookStructure.tracks && Object.keys(bookStructure.tracks).length > 0) {
            const tracksHeader = document.createElement('div');
            tracksHeader.className = 'chapter-divider';
            tracksHeader.textContent = 'Reading Tracks';
            container.appendChild(tracksHeader);
            
            // Add track links
            Object.entries(bookStructure.tracks).forEach(([trackId, track]) => {
                const trackLink = document.createElement('div');
                trackLink.className = 'node-link track-link';
                
                const indicator = document.createElement('span');
                indicator.className = 'node-type-indicator';
                indicator.classList.add(trackId === 'nonfiction' ? 'nonfiction' : 'fiction');
                
                trackLink.appendChild(indicator);
                trackLink.appendChild(document.createTextNode(track.name));
                
                trackLink.addEventListener('click', () => {
                    const event = new CustomEvent('navigateToNode', {
                        detail: { 
                            nodeId: track.startNode,
                            pov: this.state.nodeLoader.bookStructure.defaultPOV
                        }
                    });
                    document.dispatchEvent(event);
                });
                
                container.appendChild(trackLink);
            });
        }
        
        // Add chapter jump menu
        this.addChapterJumpMenu(container);
    }
    
    /**
     * Create a node link element
     * @param {Object} nodeInfo - Node information from book structure
     * @param {boolean} isCurrent - Whether this is the current node
     * @returns {HTMLElement} - The node link element
     */
    createNodeLink(nodeInfo, isCurrent) {
        const link = document.createElement('div');
        link.className = 'node-link';
        
        // Add classes based on relationship to current node
        if (isCurrent) {
            link.classList.add('current');
        }
        
        // Add node type indicator
        const indicator = document.createElement('span');
        indicator.className = 'node-type-indicator';
        indicator.classList.add(nodeInfo.type === 'nonfiction' ? 'nonfiction' : 'fiction');
        
        // Add node title
        link.appendChild(indicator);
        link.appendChild(document.createTextNode(nodeInfo.title));
        
        // Add click event
        link.addEventListener('click', () => {
            const event = new CustomEvent('navigateToNode', {
                detail: { 
                    nodeId: nodeInfo.id, 
                    pov: nodeInfo.defaultPOV || this.state.nodeLoader.bookStructure.defaultPOV 
                }
            });
            document.dispatchEvent(event);
        });
        
        return link;
    }
    
    /**
     * Add a chapter jump menu to the navigator
     * @param {HTMLElement} container - The container element
     */
    addChapterJumpMenu(container) {
        if (!this.state.nodeLoader.bookStructure || !this.state.nodeLoader.bookStructure.chapters) {
            return;
        }
        
        const chapters = this.state.nodeLoader.bookStructure.chapters;
        
        // Create a chapter selector header
        const jumpHeader = document.createElement('div');
        jumpHeader.className = 'chapter-divider';
        jumpHeader.textContent = 'Jump to Chapter';
        container.appendChild(jumpHeader);
        
        // Create a select element
        const select = document.createElement('select');
        select.id = 'chapter-select';
        select.className = 'chapter-select';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select a Chapter';
        select.appendChild(defaultOption);
        
        // Add chapter options
        chapters.forEach(chapter => {
            const option = document.createElement('option');
            option.value = chapter.id;
            option.textContent = chapter.title;
            select.appendChild(option);
        });
        
        // Add change event
        select.addEventListener('change', (e) => {
            const chapterId = e.target.value;
            if (chapterId) {
                const chapter = chapters.find(c => c.id === chapterId);
                if (chapter && chapter.startNode) {
                    const event = new CustomEvent('navigateToNode', {
                        detail: { 
                            nodeId: chapter.startNode,
                            pov: this.state.nodeLoader.bookStructure.defaultPOV
                        }
                    });
                    document.dispatchEvent(event);
                    
                    // Reset select
                    select.value = '';
                }
            }
        });
        
        // Add to container
        container.appendChild(select);
    }
    
    /**
     * Display direct next/previous navigation when not in critical path
     * @param {HTMLElement} container - The container element
     * @param {Object} node - The current node data
     */
    displayDirectNavigation(container, node) {
        if (node.navigation) {
            // Previous node
            if (node.navigation.previous) {
                const prevLink = document.createElement('div');
                prevLink.className = 'node-link previous';
                prevLink.innerHTML = '<i class="fas fa-arrow-left"></i> Previous Node';
                prevLink.addEventListener('click', () => {
                    const event = new CustomEvent('navigateToNode', {
                        detail: { 
                            nodeId: node.navigation.previous, 
                            pov: this.state.currentPOV 
                        }
                    });
                    document.dispatchEvent(event);
                });
                container.appendChild(prevLink);
            }
            
            // Current node indicator
            const currentIndicator = document.createElement('div');
            currentIndicator.className = 'node-link current';
            currentIndicator.textContent = node.data.label || 'Current Node';
            container.appendChild(currentIndicator);
            
            // Next node
            if (node.navigation.next) {
                const nextLink = document.createElement('div');
                nextLink.className = 'node-link next';
                nextLink.innerHTML = 'Next Node <i class="fas fa-arrow-right"></i>';
                nextLink.addEventListener('click', () => {
                    const event = new CustomEvent('navigateToNode', {
                        detail: { 
                            nodeId: node.navigation.next, 
                            pov: this.state.currentPOV 
                        }
                    });
                    document.dispatchEvent(event);
                });
                container.appendChild(nextLink);
            }
        }
    }
    
    /**
     * Set up POV controls in the top bar
     * @param {Object} node - The current node data
     * @param {string} currentPOV - Currently selected POV
     */
    setupPOVControls(node, currentPOV) {
        const container = this.elements.povControls;
        if (!container) return;
        
        container.innerHTML = '';
        
        // Get available POVs from the node
        const availablePOVs = this.getAvailablePOVs(node);
        
        // Create POV buttons
        availablePOVs.forEach(pov => {
            const button = document.createElement('button');
            button.className = 'pov-button';
            button.textContent = pov;
            button.setAttribute('data-pov', pov);
            
            if (pov === currentPOV) {
                button.classList.add('active');
            }
            
            button.addEventListener('click', () => {
                // Trigger a custom event to load the content with new POV
                const event = new CustomEvent('changePOV', {
                    detail: { 
                        nodeId: this.state.currentNodeId, 
                        pov: pov 
                    }
                });
                document.dispatchEvent(event);
            });
            
            container.appendChild(button);
        });
    }
    
    /**
     * Get available POVs from node data and book structure
     * @param {Object} node - The node data
     * @returns {Array} - Array of available POV strings
     */
    getAvailablePOVs(node) {
        // Start with POVs from the node data
        let availablePOVs = [];
        
        // Get POVs from node metadata or alternateVersions
        if (node.metadata && node.metadata.povCharacter) {
            availablePOVs.push(node.metadata.povCharacter);
        }
        
        if (node.navigation && node.navigation.alternateVersions) {
            node.navigation.alternateVersions.forEach(v => {
                if (v.povCharacter && !availablePOVs.includes(v.povCharacter)) {
                    availablePOVs.push(v.povCharacter);
                }
            });
        }
        
        // Check book structure if available
        if (this.state.nodeLoader.bookStructure) {
            const povs = this.state.nodeLoader.getAvailablePOVs(node.id);
            if (povs && povs.length > 0) {
                povs.forEach(pov => {
                    if (!availablePOVs.includes(pov)) {
                        availablePOVs.push(pov);
                    }
                });
            }
        }
        
        // Add the current POV if not already included
        if (this.state.currentPOV && !availablePOVs.includes(this.state.currentPOV)) {
            availablePOVs.unshift(this.state.currentPOV);
        }
        
        // Add the standard set of characters if none specified
        if (availablePOVs.length === 0) {
            availablePOVs = ['Zach', 'Nicole', 'Steve', 'Alec', 'Omniscient'];
        }
        
        return availablePOVs;
    }
    
    /**
     * Update progress tracking display
     */
    updateProgressTracking() {
        const progressContainer = document.getElementById('reading-progress');
        if (!progressContainer) return;
        
        if (!this.state.nodeLoader.bookStructure || !this.state.currentNodeId) {
            progressContainer.innerHTML = '';
            return;
        }
        
        const criticalPath = this.state.nodeLoader.bookStructure.criticalPath;
        const currentIndex = criticalPath.findIndex(node => node.id === this.state.currentNodeId);
        
        if (currentIndex !== -1) {
            const progress = Math.round((currentIndex / (criticalPath.length - 1)) * 100);
            
            progressContainer.innerHTML = `
                <div class="progress">
                    <div class="progress-bar" role="progressbar" 
                         style="width: ${progress}%" 
                         aria-valuenow="${progress}" 
                         aria-valuemin="0" 
                         aria-valuemax="100"></div>
                </div>
                <div class="progress-text">${progress}% Complete</div>
            `;
        } else {
            progressContainer.innerHTML = '';
        }
    }
}

// Make it available globally
window.SidebarController = SidebarController;