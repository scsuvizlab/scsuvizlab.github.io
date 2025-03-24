/**
 * Updated uiController.js - UI Update and Rendering Logic for Life in 2045 Interactive Reader
 * 
 * This module handles updates to the main content display, breadcrumb navigation,
 * loading indicators, and other UI elements. This version includes fixes for
 * breadcrumb updates and properly reflects the node type (fiction vs non-fiction).
 */

class UIController {
    /**
     * Initialize the UIController
     * @param {Object} elements - DOM element references
     * @param {Object} state - Global application state
     */
    constructor(elements, state) {
        this.elements = elements;
        this.state = state;
    }

    /**
     * Update the main content display with node data
     * @param {Object} node - The node data to display
     */
    updateContentDisplay(node) {
        console.log("Updating content display with:", node);
        
        // Update chapter title
        let title = node.data.chapterTitle || node.data.label || 'Chapter 1';
        let subtitle = node.data.subtitle || 'A New Beginning';
        
        if (this.elements.chapterTitle) {
            this.elements.chapterTitle.innerHTML = `
                <h1>${this.sanitizeHTML(title)}</h1>
                <div class="subtitle">${this.sanitizeHTML(subtitle)}</div>
            `;
        }
        
        // Get the scene content element
        const sceneContent = this.elements.sceneContent || document.getElementById('scene-content');
        
        if (!sceneContent) {
            console.error("Scene content element not found");
            return;
        }
        
        // Update scene content
        const content = node.data.content || '<p>No content available for this node.</p>';
        
        // Add special class for non-fiction content styling
        if (node.nodeType === 'nonfiction' || node.id?.startsWith('nf-')) {
            sceneContent.className = 'scene-content nonfiction-content';
        } else {
            sceneContent.className = 'scene-content';
        }
        
        sceneContent.innerHTML = content;
        
        // Process branch points if they exist
        this.processBranchPoints(node);
    }
    
    /**
     * Process branch points in the content and add proper styling/classes
     * @param {Object} node - The node data containing branch points
     */
    processBranchPoints(node) {
        // Check if there are branch points in the node data
        if (!node.data.branchPoints || node.data.branchPoints.length === 0) {
            return;
        }
        
        // Process each branch point
        node.data.branchPoints.forEach((branch, index) => {
            if (!branch.text) return;
            
            // Find text in content and wrap in branch point div
            const content = this.elements.sceneContent.innerHTML;
            const branchText = this.escapeRegExp(branch.text);
            const regex = new RegExp(`(${branchText})`, 'g');
            
            if (regex.test(content)) {
                const updatedContent = content.replace(
                    regex, 
                    `<div class="branch-point" data-branch-index="${index}">$1</div>`
                );
                this.elements.sceneContent.innerHTML = updatedContent;
            }
        });
    }
    
    /**
     * Update breadcrumb navigation
     * @param {Object} node - The current node
     * @param {string} pov - Current POV character
     */
    updateBreadcrumb(node, pov) {
        console.log("Updating breadcrumb with:", { node, pov });
        if (!this.elements.breadcrumbTrail) {
            console.error("Breadcrumb element not found");
            return;
        }
        
        const nodeType = node.nodeType || (node.id?.startsWith('nf-') ? 'nonfiction' : 'fiction');
        const chapter = node.data.chapterTitle || 'Chapter';
        const scene = node.data.label || 'Scene';
        
        // Create breadcrumb items
        this.elements.breadcrumbTrail.innerHTML = '';
        
        // Chapter item
        const chapterItem = document.createElement('div');
        chapterItem.className = 'breadcrumb-item';
        chapterItem.textContent = chapter;
        this.elements.breadcrumbTrail.appendChild(chapterItem);
        
        // Scene item
        const sceneItem = document.createElement('div');
        sceneItem.className = 'breadcrumb-item';
        sceneItem.textContent = scene;
        this.elements.breadcrumbTrail.appendChild(sceneItem);
        
        // Only show POV for fiction nodes
        if (nodeType !== 'nonfiction') {
            const povItem = document.createElement('div');
            povItem.className = 'breadcrumb-item';
            povItem.textContent = `${pov}'s POV`;
            this.elements.breadcrumbTrail.appendChild(povItem);
        } else {
            // For non-fiction, indicate it's educational content
            const typeItem = document.createElement('div');
            typeItem.className = 'breadcrumb-item';
            typeItem.textContent = 'Non-Fiction';
            this.elements.breadcrumbTrail.appendChild(typeItem);
        }
        
        console.log("Breadcrumb updated to:", this.elements.breadcrumbTrail.innerHTML);
    }
    
    /**
     * Show loading indicator
     */
    showLoadingIndicator() {
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = 'block';
        }
    }
    
    /**
     * Hide loading indicator
     */
    hideLoadingIndicator() {
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = 'none';
        }
    }
    
    /**
     * Display an error message in the content area
     * @param {string} message - Error message to display
     */
    showError(message) {
        const sceneContent = this.elements.sceneContent || document.getElementById('scene-content');
        if (sceneContent) {
            sceneContent.innerHTML = `
                <div class="error-message">
                    <p>Sorry, there was an error:</p>
                    <p>${this.sanitizeHTML(message)}</p>
                </div>
            `;
        }
    }
    
    /**
     * Create notification that appears and fades out
     * @param {string} message - Message to show in notification
     * @param {string} type - Type of notification (success, error, info)
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to document
        document.body.appendChild(notification);
        
        // Fade in
        setTimeout(() => {
            notification.classList.add('visible');
        }, 10);
        
        // Fade out and remove after delay
        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
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
    
    /**
     * Escape regular expression special characters
     * @param {string} string - String to escape
     * @returns {string} - Escaped string safe for RegExp
     */
    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// Make it available globally