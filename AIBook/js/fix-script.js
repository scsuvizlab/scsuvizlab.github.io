/**
 * Emergency fix for content display issues
 * Add this script to your HTML just before the closing </body> tag
 */
(function() {
    console.log("Running emergency content fix script");

    // Function to attempt multiple ways to set content
    function forceContentDisplay(content) {
        console.log("FORCE CONTENT: Attempting to force content display");
        let displaySuccess = false;

        // Try method 1: Look for scene-content by ID
        const sceneContentById = document.getElementById('scene-content');
        if (sceneContentById) {
            console.log("FORCE CONTENT: Found scene-content by ID");
            sceneContentById.innerHTML = content;
            displaySuccess = true;
        }

        // Try method 2: Look for scene-content by class
        if (!displaySuccess) {
            const sceneContentByClass = document.querySelector('.scene-content');
            if (sceneContentByClass) {
                console.log("FORCE CONTENT: Found scene-content by class");
                sceneContentByClass.innerHTML = content;
                displaySuccess = true;
            }
        }

        // Try method 3: Create scene-content if it doesn't exist
        if (!displaySuccess) {
            console.log("FORCE CONTENT: Creating scene-content element");
            const contentDisplay = document.getElementById('content-display');
            if (contentDisplay) {
                const newSceneContent = document.createElement('div');
                newSceneContent.id = 'scene-content';
                newSceneContent.className = 'scene-content';
                newSceneContent.innerHTML = content;
                
                // Add it after chapter-title if it exists
                const chapterTitle = document.getElementById('chapter-title');
                if (chapterTitle && chapterTitle.parentNode === contentDisplay) {
                    console.log("FORCE CONTENT: Inserting after chapter-title");
                    chapterTitle.after(newSceneContent);
                } else {
                    console.log("FORCE CONTENT: Appending to content-display");
                    contentDisplay.appendChild(newSceneContent);
                }
                displaySuccess = true;
            }
        }

        // Try method 4: Last resort, create a floating content box
        if (!displaySuccess) {
            console.log("FORCE CONTENT: Creating floating content box");
            const floatingContent = document.createElement('div');
            floatingContent.style.position = 'fixed';
            floatingContent.style.top = '50%';
            floatingContent.style.left = '50%';
            floatingContent.style.transform = 'translate(-50%, -50%)';
            floatingContent.style.width = '80%';
            floatingContent.style.maxHeight = '80%';
            floatingContent.style.overflow = 'auto';
            floatingContent.style.backgroundColor = 'white';
            floatingContent.style.color = 'black';
            floatingContent.style.padding = '20px';
            floatingContent.style.border = '1px solid black';
            floatingContent.style.zIndex = '1000';
            floatingContent.innerHTML = content;
            document.body.appendChild(floatingContent);
            displaySuccess = true;
        }

        return displaySuccess;
    }

    // Override the updateContentDisplay method to include our forcing function
    if (typeof ui !== 'undefined' && ui.updateContentDisplay) {
        const originalUpdateContentDisplay = ui.updateContentDisplay;
        ui.updateContentDisplay = function(node) {
            console.log("FORCE CONTENT: Intercepting updateContentDisplay");
            // First try the original method
            originalUpdateContentDisplay.call(this, node);
            
            // Then force display regardless
            const content = node.data.content || '<p>No content available for this node.</p>';
            setTimeout(() => {
                forceContentDisplay(content);
                console.log("FORCE CONTENT: Content should now be visible");
            }, 100); // Small delay to ensure DOM is ready
        };
        console.log("FORCE CONTENT: Successfully overrode updateContentDisplay");
    } else {
        console.error("FORCE CONTENT: Could not find ui.updateContentDisplay to override");
    }

    // Try to immediately fix the current content if available
    setTimeout(() => {
        if (window.nodeLoader && window.nodeLoader.currentNode && window.nodeLoader.currentNode.data) {
            const currentContent = window.nodeLoader.currentNode.data.content;
            if (currentContent) {
                console.log("FORCE CONTENT: Applying fix to current content");
                forceContentDisplay(currentContent);
            }
        }
    }, 500); // Wait a bit longer for initial load
})();
