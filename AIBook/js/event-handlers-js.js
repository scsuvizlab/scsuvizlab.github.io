/**
 * eventHandlers.js - UI Event Listeners for Life in 2045 Interactive Reader
 * 
 * This module sets up all event listeners for UI elements and delegates
 * to appropriate modules based on user actions.
 */

/**
 * Set up all event handlers for the application
 * @param {Object} elements - DOM element references
 * @param {Object} state - Global application state
 * @param {Object} modules - References to other application modules
 */
 function setupEventHandlers(elements, state, modules) {
    const { contentLoader, ui, sidebar, navigation, readingModes } = modules;
    
    // Set up navigation button handlers
    setupNavigationButtonHandlers(elements, navigation);
    
    // Set up custom event handlers
    setupCustomEventHandlers(state, contentLoader);
    
    // Set up reading mode button handlers
    setupReadingModeHandlers(elements, readingModes);
    
    // Set up main navigation sidebar handlers
    setupSidebarNavHandlers(elements, state);
    
    // Set up external navigation button handlers
    setupExternalNavHandlers(elements);
}

/**
 * Set up handlers for navigation buttons
 * @param {Object} elements - DOM element references
 * @param {Object} navigation - Navigation manager module
 */
function setupNavigationButtonHandlers(elements, navigation) {
    // Previous button
    elements.prevButton.addEventListener('click', () => {
        navigation.navigateToPreviousNode();
    });
    
    // Next button
    elements.nextButton.addEventListener('click', () => {
        navigation.navigateToNextNode();
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (event) => {
        // Left arrow key for previous
        if (event.key === 'ArrowLeft' && !elements.prevButton.disabled) {
            navigation.navigateToPreviousNode();
        }
        
        // Right arrow key for next
        if (event.key === 'ArrowRight' && !elements.nextButton.disabled) {
            navigation.navigateToNextNode();
        }
    });
}

/**
 * Set up handlers for custom events
 * @param {Object} state - Global application state
 * @param {Object} contentLoader - Content loader module
 */
function setupCustomEventHandlers(state, contentLoader) {
    // Handle node navigation event
    document.addEventListener('navigateToNode', (event) => {
        const { nodeId, pov } = event.detail;
        contentLoader.loadContent(nodeId, pov || state.currentPOV);
    });
    
    // Handle POV change event
    document.addEventListener('changePOV', (event) => {
        const { nodeId, pov } = event.detail;
        contentLoader.loadContent(nodeId || state.currentNodeId, pov);
    });
    
    // Handle related non-fiction loading
    document.addEventListener('loadRelatedNonFiction', (event) => {
        const { index } = event.detail;
        contentLoader.loadRelatedNonFiction(index);
    });
}

/**
 * Set up handlers for reading mode buttons
 * @param {Object} elements - DOM element references
 * @param {Object} readingModes - Reading modes module
 */
function setupReadingModeHandlers(elements, readingModes) {
    // Text reading mode
    if (elements.modeControls) {
        const readingButton = document.getElementById('reading-btn');
        if (readingButton) {
            readingButton.addEventListener('click', () => {
                readingModes.activateReadingMode();
            });
        }
        
        // Text-to-speech mode
        const ttsButton = document.getElementById('tts-btn');
        if (ttsButton) {
            ttsButton.addEventListener('click', () => {
                readingModes.activateTtsMode();
            });
        }
        
        // Image generation mode
        const imagesButton = document.getElementById('images-btn');
        if (imagesButton) {
            imagesButton.addEventListener('click', () => {
                readingModes.activateImagesMode();
            });
        }
    }
}

/**
 * Set up handlers for main navigation sidebar
 * @param {Object} elements - DOM element references
 * @param {Object} state - Global application state
 */
function setupSidebarNavHandlers(elements, state) {
    // Continue reading button
    const continueReadingBtn = document.getElementById('continue-reading-btn');
    if (continueReadingBtn) {
        continueReadingBtn.addEventListener('click', () => {
            // Dispatch a custom event to navigate to the current node
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: state.currentNodeId,
                    pov: state.currentPOV
                }
            });
            document.dispatchEvent(event);
        });
    }
    
    // Chapter list button
    const chapterListBtn = document.getElementById('chapter-list-btn');
    if (chapterListBtn) {
        chapterListBtn.addEventListener('click', () => {
            alert('Chapter list feature would be implemented in a full version');
        });
    }
    
    // Bookmarks button
    const bookmarksBtn = document.getElementById('bookmarks-btn');
    if (bookmarksBtn) {
        bookmarksBtn.addEventListener('click', () => {
            alert('Bookmarks feature would be implemented in a full version');
        });
    }
    
    // Fiction track button
    const fictionTrackBtn = document.getElementById('fiction-track-btn');
    if (fictionTrackBtn) {
        fictionTrackBtn.addEventListener('click', () => {
            // Simulate switching to fiction track by navigating to a fiction node
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: 'ch1-scene1-restaurant',
                    pov: state.currentPOV
                }
            });
            document.dispatchEvent(event);
            
            // Update active state
            setActiveSidebarButton(fictionTrackBtn);
        });
    }
    
    // Non-fiction track button
    const nonfictionTrackBtn = document.getElementById('nonfiction-track-btn');
    if (nonfictionTrackBtn) {
        nonfictionTrackBtn.addEventListener('click', () => {
            // Simulate switching to non-fiction track by navigating to a non-fiction node
            const event = new CustomEvent('navigateToNode', {
                detail: {
                    nodeId: 'nf-what-is-ai',
                    pov: state.currentPOV
                }
            });
            document.dispatchEvent(event);
            
            // Update active state
            setActiveSidebarButton(nonfictionTrackBtn);
        });
    }
    
    // Character buttons
    setupCharacterButtons(state);
    
    // Preferences and help buttons
    setupUtilityButtons();
}

/**
 * Set up character navigation buttons
 * @param {Object} state - Global application state
 */
function setupCharacterButtons(state) {
    const characters = ['zach', 'nicole', 'steve', 'alec'];
    
    characters.forEach(character => {
        const btn = document.getElementById(`${character}-character-btn`);
        if (btn) {
            btn.addEventListener('click', () => {
                // Capitalize first letter for POV
                const pov = character.charAt(0).toUpperCase() + character.slice(1);
                
                // Dispatch a POV change event
                const event = new CustomEvent('changePOV', {
                    detail: {
                        nodeId: state.currentNodeId,
                        pov: pov
                    }
                });
                document.dispatchEvent(event);
            });
        }
    });
}

/**
 * Set up preferences and help buttons
 */
function setupUtilityButtons() {
    // Preferences button
    const preferencesBtn = document.getElementById('preferences-btn');
    if (preferencesBtn) {
        preferencesBtn.addEventListener('click', () => {
            alert('Preferences feature would be implemented in a full version');
        });
    }
    
    // Help button
    const helpBtn = document.getElementById('help-btn');
    if (helpBtn) {
        helpBtn.addEventListener('click', () => {
            alert('Help feature would be implemented in a full version');
        });
    }
}

/**
 * Set up external navigation buttons
 * @param {Object} elements - DOM element references
 */
function setupExternalNavHandlers(elements) {
    // Scene editor button
    const sceneEditorBtn = document.getElementById('scene-editor-btn');
    if (sceneEditorBtn) {
        sceneEditorBtn.addEventListener('click', () => {
            if (confirmNavigation('Scene Editor')) {
                window.location.href = 'node-editor.html';
            }
        });
    }
    
    // Critical path button
    const criticalPathBtn = document.getElementById('critical-path-btn');
    if (criticalPathBtn) {
        criticalPathBtn.addEventListener('click', () => {
            if (confirmNavigation('Critical Path Editor')) {
                window.location.href = 'critical-path-navigator.html';
            }
        });
    }
    
    // Home button
    const homeBtn = document.getElementById('home-btn');
    if (homeBtn) {
        homeBtn.addEventListener('click', () => {
            if (confirmNavigation('Home page')) {
                window.location.href = 'index.html';
            }
        });
    }
}

/**
 * Confirm navigation away from the reader
 * @param {string} destination - Name of the destination
 * @returns {boolean} - True if navigation confirmed, false otherwise
 */
function confirmNavigation(destination) {
    return confirm(`Go to the ${destination}? You will leave the reader view.`);
}

/**
 * Set a sidebar button as active and deactivate others in the same section
 * @param {HTMLElement} activeButton - The button to set as active
 */
function setActiveSidebarButton(activeButton) {
    // Get the parent section
    const section = activeButton.closest('.nav-section');
    if (!section) return;
    
    // Remove active class from all buttons in this section
    const buttons = section.querySelectorAll('.nav-button');
    buttons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Add active class to the selected button
    activeButton.classList.add('active');
}