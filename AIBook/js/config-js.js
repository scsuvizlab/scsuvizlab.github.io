/**
 * config.js - Configuration and Constants for Life in 2045 Interactive Reader
 * 
 * This module contains default configuration, constants, and settings
 * that can be used throughout the application.
 */

 const config = {
    /**
     * Application defaults
     */
    defaultNodeId: 'ch1-scene1-restaurant',
    defaultPOV: 'Omniscient',
    
    /**
     * Character configurations
     */
    characters: {
        main: ['Zach', 'Nicole', 'Steve', 'Alec'],
        secondary: ['Rhett', 'Seth', 'Daria', 'Marcus'],
        narrators: ['Omniscient'],
        all: function() {
            return [...this.narrators, ...this.main, ...this.secondary];
        }
    },
    
    /**
     * Node types and their display properties
     */
    nodeTypes: {
        fiction: {
            icon: 'fas fa-book',
            color: '#6ecff6',
            label: 'Fiction'
        },
        nonfiction: {
            icon: 'fas fa-brain',
            color: '#9370db',
            label: 'Non-Fiction'
        },
        character: {
            icon: 'fas fa-user',
            color: '#20b2aa',
            label: 'Character Profile'
        },
        interactive: {
            icon: 'fas fa-gamepad',
            color: '#ba55d3',
            label: 'Interactive Element'
        },
        world: {
            icon: 'fas fa-globe',
            color: '#cd853f',
            label: 'World Entity'
        }
    },
    
    /**
     * Connection types and their display properties
     */
    connectionTypes: {
        'critical-path': {
            color: '#ffd700',
            label: 'Critical Path',
            description: 'Main storyline sequence'
        },
        'character-pov': {
            color: '#6ecff6',
            label: 'Character POV',
            description: 'Alternative character perspectives'
        },
        'branch-point': {
            color: '#ff8c00',
            label: 'Branch Point',
            description: 'Story branches and decisions'
        },
        'concept-sequence': {
            color: '#9370db',
            label: 'Concept Sequence',
            description: 'Educational concept flow'
        },
        'related-concept': {
            color: '#3cb371',
            label: 'Related Concept',
            description: 'Connected educational topics'
        },
        'fiction-nonfiction': {
            color: '#ff69b4',
            label: 'Fiction-Nonfiction Link',
            description: 'Connections between story and concepts'
        }
    },
    
    /**
     * Reading modes
     */
    readingModes: {
        reading: {
            icon: 'fas fa-paragraph',
            label: 'Traditional Reading',
            description: 'Standard text-based reading experience'
        },
        tts: {
            icon: 'fas fa-volume-up',
            label: 'Text-to-Speech',
            description: 'Audio narration of content'
        },
        images: {
            icon: 'fas fa-image',
            label: 'Generated Images',
            description: 'AI-generated illustrations of scenes'
        }
    },
    
    /**
     * UI text and messages
     */
    ui: {
        errors: {
            loadFailed: 'Failed to load content. Please try again.',
            unsupportedBrowser: 'This feature is not supported in your browser.',
            navigationFailed: 'Unable to navigate to the requested content.'
        },
        notifications: {
            pov: {
                changed: 'Perspective changed to {0}',
                unavailable: 'This perspective is not available for this scene'
            },
            branch: {
                followed: 'Following story branch...',
                unavailable: 'This branch is not available yet'
            },
            mode: {
                tts: {
                    started: 'Reading content aloud...',
                    stopped: 'Speech stopped'
                },
                images: {
                    generating: 'Generating images...',
                    complete: 'Images generated'
                }
            }
        },
        confirmations: {
            leaveReader: 'You are about to leave the reader. Any unsaved progress may be lost. Continue?'
        }
    },
    
    /**
     * Chapter information for navigation
     */
    chapters: [
        {
            id: 'chapter1',
            title: 'A New Beginning',
            startNode: 'ch1-scene1-restaurant',
            description: 'Introduces the family and their conflicting worldviews about AI governance'
        },
        {
            id: 'chapter2',
            title: 'Growing Tensions',
            startNode: 'ch2-scene1-morning-commute',
            description: 'Daily life in 2045 and the seeds of discontent'
        },
        {
            id: 'chapter3',
            title: 'The Device',
            startNode: 'ch3-scene1-alec-bedroom',
            description: 'Alec installs a mysterious device that begins to change everything'
        }
    ],
    
    /**
     * Sample nodes for demo purposes
     */
    sampleNodes: {
        fiction: 'ch1-scene1-restaurant',
        nonfiction: 'nf-what-is-ai',
        character: 'character-alec',
        interactive: 'interactive-ai-quiz',
        world: 'zachs-restaurant'
    }
};