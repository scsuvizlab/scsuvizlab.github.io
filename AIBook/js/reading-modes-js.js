/**
 * readingModes.js - Reading Experience Modes for Life in 2045 Interactive Reader
 * 
 * This module handles different reading modes including:
 * - Traditional text reading
 * - Text-to-speech narration
 * - Image generation (conceptual implementation)
 */

 class ReadingModes {
    /**
     * Initialize ReadingModes
     * @param {Object} elements - DOM element references
     * @param {Object} state - Global application state
     */
    constructor(elements, state) {
        this.elements = elements;
        this.state = state;
        this.currentMode = 'reading'; // Default mode
        this.speechSynthesis = window.speechSynthesis;
        this.utterance = null; // Current speech utterance
        
        // Mode button references for easier access
        this.modeButtons = {
            reading: document.getElementById('reading-btn'),
            tts: document.getElementById('tts-btn'),
            images: document.getElementById('images-btn')
        };
    }

    /**
     * Switch to text reading mode (default)
     */
    activateReadingMode() {
        // Stop any ongoing speech
        this.stopSpeech();
        
        // Hide any generated images (if implemented)
        this.hideGeneratedImages();
        
        // Update UI to reflect mode change
        this.updateModeButtonStates('reading');
        
        this.currentMode = 'reading';
    }
    
    /**
     * Switch to text-to-speech mode
     */
    activateTtsMode() {
        if (!this.speechSynthesis) {
            console.warn('Text-to-speech not supported in this browser');
            return;
        }
        
        // Update UI to reflect mode change
        this.updateModeButtonStates('tts');
        
        // Start reading the current content
        this.startSpeech();
        
        this.currentMode = 'tts';
    }
    
    /**
     * Switch to image generation mode
     */
    activateImagesMode() {
        // Update UI to reflect mode change
        this.updateModeButtonStates('images');
        
        // Stop any ongoing speech
        this.stopSpeech();
        
        // Generate images based on content (would be implemented in a full version)
        this.generateImages();
        
        this.currentMode = 'images';
    }
    
    /**
     * Update UI state for mode buttons
     * @param {string} activeMode - The mode to set as active
     */
    updateModeButtonStates(activeMode) {
        // Remove active class from all buttons
        Object.values(this.modeButtons).forEach(button => {
            if (button) button.classList.remove('active');
        });
        
        // Add active class to the selected mode button
        if (this.modeButtons[activeMode]) {
            this.modeButtons[activeMode].classList.add('active');
        }
    }
    
    /**
     * Start text-to-speech for current content
     */
    startSpeech() {
        // Stop any ongoing speech first
        this.stopSpeech();
        
        // Get content text from the content display
        const contentText = this.getContentText();
        
        if (contentText && this.speechSynthesis) {
            // Create a new speech utterance
            this.utterance = new SpeechSynthesisUtterance(contentText);
            
            // Configure utterance properties
            this.utterance.rate = 1.0; // Normal speaking rate
            this.utterance.pitch = 1.0; // Normal pitch
            
            // Use a voice appropriate for the POV character if available
            this.setVoiceForCharacter(this.state.currentPOV);
            
            // Add event handlers
            this.utterance.onend = () => {
                console.log('Speech finished');
            };
            
            this.utterance.onerror = (event) => {
                console.error('Speech error:', event);
            };
            
            // Start speaking
            this.speechSynthesis.speak(this.utterance);
        }
    }
    
    /**
     * Stop any ongoing text-to-speech
     */
    stopSpeech() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
            this.utterance = null;
        }
    }
    
    /**
     * Set a voice based on the character POV
     * @param {string} character - The POV character
     */
    setVoiceForCharacter(character) {
        if (!this.utterance || !this.speechSynthesis) return;
        
        // Get available voices
        const voices = this.speechSynthesis.getVoices();
        if (voices.length === 0) return;
        
        // Character voice mapping (would be more sophisticated in a full implementation)
        const characterVoices = {
            'Zach': { gender: 'male', age: 'adult' },
            'Nicole': { gender: 'female', age: 'adult' },
            'Steve': { gender: 'male', age: 'older' },
            'Alec': { gender: 'male', age: 'young' }
        };
        
        const characterPrefs = characterVoices[character] || { gender: 'male', age: 'adult' };
        
        // Simple voice selection based on gender
        let selectedVoice = null;
        
        if (characterPrefs.gender === 'female') {
            // Find a female voice
            selectedVoice = voices.find(voice => voice.name.includes('female') || voice.name.includes('woman'));
        } else {
            // Find a male voice
            selectedVoice = voices.find(voice => voice.name.includes('male') || voice.name.includes('man'));
        }
        
        // Fallback to any voice if we couldn't find an appropriate one
        if (!selectedVoice && voices.length > 0) {
            selectedVoice = voices[0];
        }
        
        // Set the voice if we found one
        if (selectedVoice) {
            this.utterance.voice = selectedVoice;
        }
    }
    
    /**
     * Get text content for TTS, removing any UI elements
     * @returns {string} Clean text content
     */
    getContentText() {
        // Create a clone of the content element
        const contentClone = this.elements.contentDisplay.cloneNode(true);
        
        // Remove any branch points or interactive elements
        const branchPoints = contentClone.querySelectorAll('.branch-point');
        branchPoints.forEach(element => {
            // Replace with the text content
            const textNode = document.createTextNode(element.textContent);
            element.parentNode.replaceChild(textNode, element);
        });
        
        // Get the text content
        return contentClone.textContent || '';
    }
    
    /**
     * Generate images based on content (placeholder implementation)
     */
    generateImages() {
        console.log('Image generation would be implemented in a full version');
        // In a full implementation, this would call an API to generate images
        // based on the content of the current node
        
        // For now, let's show a placeholder message in the content
        const contentDisplay = this.elements.contentDisplay;
        const originalContent = contentDisplay.innerHTML;
        
        // Store original content for reverting later
        this._originalContent = originalContent;
        
        // Add a placeholder image note at the top
        contentDisplay.innerHTML = `
            <div class="image-generation-notice">
                <p><strong>Image Generation Mode</strong></p>
                <p>In a full implementation, this mode would generate images based on the scene description.</p>
                <div class="placeholder-image">Scene Visualization Placeholder</div>
            </div>
            ${originalContent}
        `;
    }
    
    /**
     * Hide any generated images and restore original content
     */
    hideGeneratedImages() {
        if (this._originalContent) {
            this.elements.contentDisplay.innerHTML = this._originalContent;
            this._originalContent = null;
        }
    }
    
    /**
     * Handle content updates by adjusting active mode if needed
     */
    handleContentUpdate() {
        // If we're in TTS mode, restart speech with new content
        if (this.currentMode === 'tts') {
            this.startSpeech();
        }
        
        // If we're in image mode, regenerate images
        if (this.currentMode === 'images') {
            this.generateImages();
        }
    }
    
    /**
     * Clean up resources when switching pages or closing
     */
    cleanup() {
        this.stopSpeech();
        this.hideGeneratedImages();
    }
}