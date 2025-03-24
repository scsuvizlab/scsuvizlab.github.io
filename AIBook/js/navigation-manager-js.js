/**
 * navigationManager.js - Node Navigation for Life in 2045 Interactive Reader
 * 
 * This module handles navigation between nodes, branch points, and navigation buttons.
 */

class NavigationManager {
    /**
     * Initialize the NavigationManager
     * @param {Object} elements - DOM element references
     * @param {Object} state - Global application state
     */
    constructor(elements, state) {
        this.elements = elements;
        this.state = state;
    }

    /**
     * Set up branch points within the content
     * @param {Object} node - The current node data
     */
    setupBranchPoints(node) {
        // Find all branch point elements in the content
        const branchElements = document.querySelectorAll('.branch-point');
        
        branchElements.forEach((branchElement) => {
            // Get branch index from data attribute
            const branchIndex = parseInt(branchElement.getAttribute('data-branch-index'), 10);
            
            // Add click event listener
            branchElement.addEventListener('click', () => {
                this.followBranch(node, branchIndex);
            });
        });
    }
    
    /**
     * Follow a branch to a new node
     * @param {Object} node - The current node
     * @param {number} branchIndex - Index of the branch to follow
     */
    followBranch(node, branchIndex) {
        if (node.navigation && 
            node.navigation.branchPoints && 
            node.navigation.branchPoints[branchIndex]) {
            
            const branch = node.navigation.branchPoints[branchIndex];
            
            // Dispatch a navigation event
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: branch.targetNodeId,
                    pov: this.state.currentPOV
                }
            });
            document.dispatchEvent(event);
        } else {
            console.warn(`Invalid branch index (${branchIndex}) or no branch points defined`);
        }
    }
    
    /**
     * Update navigation buttons based on available paths
     * @param {Object} node - The current node data
     */
    updateNavigationButtons(node) {
        // Previous button
        this.updatePreviousButton(node);
        
        // Next button
        this.updateNextButton(node);
    }
    
    /**
     * Update the previous button state
     * @param {Object} node - The current node data
     */
    updatePreviousButton(node) {
        const hasPrevious = node.navigation && node.navigation.previous;
        
        // Update button state
        this.elements.prevButton.disabled = !hasPrevious;
        
        // Update button text
        if (hasPrevious) {
            const previousNodeId = node.navigation.previous;
            const cachedPrevNode = this.state.nodeLoader.cache[previousNodeId];
            
            if (cachedPrevNode && cachedPrevNode.data.label) {
                this.elements.prevButton.innerHTML = `
                    <i class="fas fa-arrow-left"></i> ${this.sanitizeHTML(cachedPrevNode.data.label)}
                `;
            } else {
                this.elements.prevButton.innerHTML = `<i class="fas fa-arrow-left"></i> Previous`;
            }
        } else {
            this.elements.prevButton.innerHTML = `<i class="fas fa-arrow-left"></i> Previous`;
        }
    }
    
    /**
     * Update the next button state
     * @param {Object} node - The current node data
     */
    updateNextButton(node) {
        const hasNext = node.navigation && node.navigation.next;
        
        // Update button state (we'll keep it enabled for demo purposes even without a next node)
        this.elements.nextButton.disabled = false;
        
        // Update button text
        if (hasNext) {
            const nextNodeId = node.navigation.next;
            const cachedNextNode = this.state.nodeLoader.cache[nextNodeId];
            
            if (cachedNextNode && cachedNextNode.data.label) {
                this.elements.nextButton.innerHTML = `
                    ${this.sanitizeHTML(cachedNextNode.data.label)} <i class="fas fa-arrow-right"></i>
                `;
            } else {
                this.elements.nextButton.innerHTML = `Continue <i class="fas fa-arrow-right"></i>`;
            }
        } else {
            // In a demo, we might want to keep the button enabled
            this.elements.nextButton.innerHTML = `Continue <i class="fas fa-arrow-right"></i>`;
        }
    }
    
    /**
     * Navigate to the previous node
     */
    navigateToPreviousNode() {
        if (this.elements.prevButton.disabled) {
            return;
        }
        
        if (this.state.nodeLoader.currentNode && 
            this.state.nodeLoader.currentNode.navigation && 
            this.state.nodeLoader.currentNode.navigation.previous) {
            
            const previousNodeId = this.state.nodeLoader.currentNode.navigation.previous;
            
            // Dispatch a navigation event
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: previousNodeId,
                    pov: this.state.currentPOV
                }
            });
            document.dispatchEvent(event);
        }
    }
    
    /**
     * Navigate to the next node
     */
    navigateToNextNode() {
        if (this.elements.nextButton.disabled) {
            return;
        }
        
        if (this.state.nodeLoader.currentNode && 
            this.state.nodeLoader.currentNode.navigation && 
            this.state.nodeLoader.currentNode.navigation.next) {
            
            const nextNodeId = this.state.nodeLoader.currentNode.navigation.next;
            
            // Dispatch a navigation event
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: nextNodeId,
                    pov: this.state.currentPOV
                }
            });
            document.dispatchEvent(event);
        } else {
            // In a demo, we might use a hardcoded next node
            const nextNodeId = 'ch1-scene2-alec-bedroom'; // Fallback node
            
            // Dispatch a navigation event
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: nextNodeId,
                    pov: this.state.currentPOV
                }
            });
            document.dispatchEvent(event);
        }
    }
    
    /**
     * Navigate back in history
     */
    navigateBack() {
        if (this.state.history.length <= 1) {
            return; // Can't go back if we're at the start
        }
        
        // Remove current node from history
        this.state.history.pop();
        
        // Get the previous node from history
        const previousState = this.state.history[this.state.history.length - 1];
        
        // Remove it from history to avoid duplication when we navigate to it
        this.state.history.pop();
        
        // Dispatch a navigation event
        const event = new CustomEvent('navigateToNode', {
            detail: {
                nodeId: previousState.nodeId,
                pov: previousState.pov
            }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Sanitize HTML to prevent XSS attacks
     * @param {string} html - HTML string to sanitize
     * @returns {string} - Sanitized HTML
     */
    sanitizeHTML(html) {
        const temp = document.createElement('div');
        temp.textContent = html;
        return temp.innerHTML;
    }
}