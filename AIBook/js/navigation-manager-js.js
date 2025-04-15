/**
 * navigationManager.js - Node Navigation for Life in 2045 Interactive Reader
 * Updated to prioritize local navigation and use loader logic
 */

class NavigationManager {
    /**
     * Initialize the NavigationManager
     * @param {Object} elements - DOM element references
     * @param {Object} state - Global application state (should include nodeLoader)
     */
    constructor(elements, state) {
        this.elements = elements;
        this.state = state; // Expects state.nodeLoader to be available

        // Initialize tooltips for navigation buttons
        this._setupTooltips();
    }

    /**
     * Set up tooltips for navigation buttons
     * @private
     */
    _setupTooltips() {
        // Create tooltip elements if they don't exist
        if (!document.getElementById('prev-button-tooltip')) {
            const prevTooltip = document.createElement('div');
            prevTooltip.id = 'prev-button-tooltip';
            prevTooltip.className = 'tooltip';
            document.body.appendChild(prevTooltip);
        }

        if (!document.getElementById('next-button-tooltip')) {
            const nextTooltip = document.createElement('div');
            nextTooltip.id = 'next-button-tooltip';
            nextTooltip.className = 'tooltip';
            document.body.appendChild(nextTooltip);
        }

        // Add event listeners for showing/hiding tooltips
        if (this.elements.prevButton) {
            this.elements.prevButton.addEventListener('mouseenter', (e) => {
                const isDisabled = this.elements.prevButton.disabled;
                this._showTooltip('prev-button-tooltip', e.target,
                    isDisabled ?
                    'No previous content in history' :
                    'Go back to previous content');
            });

            this.elements.prevButton.addEventListener('mouseleave', () => {
                this._hideTooltip('prev-button-tooltip');
            });
        }

        if (this.elements.nextButton) {
            this.elements.nextButton.addEventListener('mouseenter', (e) => {
                 const isDisabled = this.elements.nextButton.disabled;
                this._showTooltip('next-button-tooltip', e.target,
                    isDisabled ?
                    'End of current path' :
                    'Continue to next content');
            });

            this.elements.nextButton.addEventListener('mouseleave', () => {
                this._hideTooltip('next-button-tooltip');
            });
        }
    }

    /**
     * Show a tooltip with the given text
     * @private
     * @param {string} tooltipId - ID of the tooltip element
     * @param {HTMLElement} targetElement - Element to position tooltip near
     * @param {string} text - Text to display in the tooltip
     */
    _showTooltip(tooltipId, targetElement, text) {
        const tooltip = document.getElementById(tooltipId);
        if (!tooltip) return;

        tooltip.textContent = text;
        tooltip.style.display = 'block';

        // Position the tooltip above the target element
        const rect = targetElement.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px'; // Adjust spacing
    }

    /**
     * Hide a tooltip
     * @private
     * @param {string} tooltipId - ID of the tooltip element to hide
     */
    _hideTooltip(tooltipId) {
        const tooltip = document.getElementById(tooltipId);
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }

    /**
     * Set up branch points within the content
     * @param {Object} node - The current node data
     */
    setupBranchPoints(node) {
        // Find all branch point elements in the content
        const branchElements = this.elements.sceneContent?.querySelectorAll('.branch-point'); // Use optional chaining

        branchElements?.forEach((branchElement) => { // Use optional chaining
            // Get branch index from data attribute
            const branchIndex = parseInt(branchElement.getAttribute('data-branch-index'), 10);

            // Remove previous listeners to avoid duplicates
            const newElement = branchElement.cloneNode(true);
            branchElement.parentNode.replaceChild(newElement, branchElement);


            // Add click event listener
            newElement.addEventListener('click', () => {
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
        const branch = node?.navigation?.branchPoints?.[branchIndex]; // Use optional chaining

        if (branch?.targetNodeId) { // Check if targetNodeId exists
            console.log(`Following branch ${branchIndex} to: ${branch.targetNodeId}`);
            // Dispatch a navigation event
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: branch.targetNodeId,
                    pov: this.state.currentPOV // Or maybe branch.pov if branches can change POV
                }
            });
            document.dispatchEvent(event);
        } else {
            console.warn(`Invalid branch index (${branchIndex}) or branch definition missing targetNodeId`);
        }
    }

    /**
     * Update navigation buttons based on available paths
     * @param {Object} node - The current node data
     */
    updateNavigationButtons(node) {
        if (!node) return; // Don't update if node is null

        // Previous button state depends on history
        this.updatePreviousButton(node);

        // Next button state depends on local nav or critical path order
        this.updateNextButton(node);
    }

    /**
     * Update the previous button state based on history
     * @param {Object} node - The current node data (optional, mainly for context)
     */
    updatePreviousButton(node) {
        if (!this.elements.prevButton) return;

        // Previous button is enabled only if there's something in the history to go back to
        const canGoBack = this.state.history && this.state.history.length > 1;

        this.elements.prevButton.disabled = !canGoBack;
        this.elements.prevButton.classList.toggle('disabled', !canGoBack);


        // Update button text (optional: could show title of previous node in history)
        if (canGoBack) {
             const previousState = this.state.history[this.state.history.length - 2]; // Peek at previous state
             const prevNodeDef = this.state.nodeLoader?.getNodeDefinition(previousState.nodeId);
             const prevNodeTitle = prevNodeDef?.title || this.sanitizeHTML(previousState.nodeId);

            this.elements.prevButton.innerHTML = `
                <i class="fas fa-arrow-left"></i> ${prevNodeTitle}
            `;
        } else {
            this.elements.prevButton.innerHTML = `<i class="fas fa-arrow-left"></i> Previous`;
        }
    }


    /**
     * Update the next button state based on local nav or critical path order
     * @param {Object} node - The current node data
     */
    updateNextButton(node) {
        if (!this.elements.nextButton || !this.state.nodeLoader) return; // Need nodeLoader

        // 1. Check local navigation first
        let nextNodeId = node?.navigation?.next; // Use optional chaining

        // 2. If no local 'next', check critical path order as fallback
        if (!nextNodeId) {
            nextNodeId = this.state.nodeLoader.getNextNodeInCriticalPath(node?.id); // Use optional chaining
        }

        const hasNext = !!nextNodeId;

        // Update button state
        this.elements.nextButton.disabled = !hasNext;
        this.elements.nextButton.classList.toggle('disabled', !hasNext);


        // Update button text
        if (hasNext) {
            // Try to get the title of the next node for the button text
            const cachedNextNode = this.state.nodeLoader.cache[nextNodeId];
            let nextNodeTitle = "Continue"; // Default text
            if (cachedNextNode?.data?.label) { // Use optional chaining
                 nextNodeTitle = this.sanitizeHTML(cachedNextNode.data.label);
            } else {
                 // Try getting title from book structure if not cached
                 const nextNodeDef = this.state.nodeLoader.getNodeDefinition(nextNodeId);
                 if (nextNodeDef?.title) { // Use optional chaining
                      nextNodeTitle = this.sanitizeHTML(nextNodeDef.title);
                 } else {
                      // Fallback title if definition not found
                      nextNodeTitle = this.sanitizeHTML(this.state.nodeLoader.formatNodeTitle(nextNodeId));
                 }
            }

            this.elements.nextButton.innerHTML = `
                 ${nextNodeTitle} <i class="fas fa-arrow-right"></i>
            `;
        } else {
            // Change text when at the end
            this.elements.nextButton.innerHTML = `End of Path <i class="fas fa-check"></i>`;
        }
    }


    /**
     * Navigate to the next node using the loader's prioritized logic
     */
    async navigateToNextNode() {
        if (this.elements.nextButton.disabled || !this.state.nodeLoader) {
            console.warn("Next button disabled or nodeLoader not available.");
            return;
        }

        try {
             console.log("Calling nodeLoader.loadNextNode()");
             // Use the loader's logic which now includes fallback
            await this.state.nodeLoader.loadNextNode();
        } catch (error) {
            console.error("Failed to navigate to next node:", error);
            // Optionally show error to user using ui module if available
            // if (modules && modules.ui) modules.ui.showNotification("Could not navigate to next node.", "error");
        }
    }


    /**
     * Navigate to the previous node using the loader's history-prioritized logic
     */
     async navigateToPreviousNode() {
        if (this.elements.prevButton.disabled || !this.state.nodeLoader) {
            console.warn("Previous button disabled or nodeLoader not available.");
            return;
        }

        try {
             console.log("Calling nodeLoader.loadPreviousNode()");
             // Use the loader's logic which prioritizes history
             await this.state.nodeLoader.loadPreviousNode();
         } catch (error) {
             console.error("Failed to navigate to previous node:", error);
             // Optionally show error to user
             // if (modules && modules.ui) modules.ui.showNotification("Could not navigate to previous node.", "error");
         }
    }


    /**
     * Sanitize HTML to prevent XSS attacks
     * @param {string} html - HTML string to sanitize
     * @returns {string} - Sanitized HTML
     */
    sanitizeHTML(html) {
        if (typeof html !== 'string') return '';
        const temp = document.createElement('div');
        temp.textContent = html;
        return temp.innerHTML;
    }
}