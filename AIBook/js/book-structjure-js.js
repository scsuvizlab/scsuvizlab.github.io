/**
 * Book structure for Life in 2045 Interactive Reader
 * Defines the complete critical path of the book
 */
const bookStructure = {
    title: "Life in 2045",
    defaultStartNode: "ch1-scene1-restaurant",
    criticalPath: [
        {
            id: "ch1-scene1-restaurant",
            title: "Chapter 1: Restaurant Scene",
            defaultPOV: "Zach",
            nextNode: "ch1-scene2-alec-bedroom",
            chapter: "chapter1",
            type: "fiction"
        },
        {
            id: "ch1-scene2-alec-bedroom",
            title: "Alec's Bedroom",
            defaultPOV: "Alec",
            nextNode: "nf-what-is-ai",
            chapter: "chapter1",
            type: "fiction"
        },
        {
            id: "nf-what-is-ai",
            title: "What is AI?",
            nextNode: "ch1-scene3-family-discussion",
            chapter: "chapter1",
            type: "nonfiction"
        },
        {
            id: "ch1-scene3-family-discussion",
            title: "Family Discussion",
            defaultPOV: "Nicole",
            nextNode: "ch2-scene1-nicole-work",
            chapter: "chapter1",
            type: "fiction"
        },
        {
            id: "ch2-scene1-nicole-work",
            title: "Nicole's Project",
            defaultPOV: "Nicole",
            nextNode: "nf-ai-governance",
            chapter: "chapter2",
            type: "fiction"
        },
        {
            id: "nf-ai-governance",
            title: "AI Governance Systems",
            nextNode: "ch2-scene2-late-night",
            chapter: "chapter2",
            type: "nonfiction"
        }
        // Add more nodes as needed for your structure
    ],
    
    chapters: [
        {
            id: "chapter1",
            title: "A New Beginning",
            startNode: "ch1-scene1-restaurant",
            description: "Introduces the family and their conflicting worldviews"
        },
        {
            id: "chapter2",
            title: "Nicole's Work",
            startNode: "ch2-scene1-nicole-work",
            description: "Explores the AI governance systems Nicole develops"
        }
        // Add more chapters as needed
    ]
};