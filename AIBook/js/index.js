/**
 * JavaScript for the index/home page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if this is the first visit
    initWelcomeModal();
    
    // Initialize tool cards
    initToolCards();
    
    // Initialize navigation links
    initNavigationLinks();
});

/**
 * Initialize the welcome modal for first-time visitors
 */
function initWelcomeModal() {
    const hasVisitedBefore = getFromLocalStorage('hasVisitedBefore', false);
    const welcomeModal = document.getElementById('welcome-modal');
    
    if (!hasVisitedBefore && welcomeModal) {
        welcomeModal.style.display = 'flex';
        saveToLocalStorage('hasVisitedBefore', true);
        
        // Modal close button
        document.getElementById('close-modal').addEventListener('click', function() {
            welcomeModal.style.display = 'none';
        });
        
        // Get started button
        document.getElementById('start-button').addEventListener('click', function() {
            welcomeModal.style.display = 'none';
        });
    }
}

/**
 * Initialize tool cards with hover effects and click handlers
 */
function initToolCards() {
    const toolCards = document.querySelectorAll('.tool-card');
    
    toolCards.forEach(card => {
        // Get the tool button
        const toolButton = card.querySelector('.tool-button');
        
        // Add click handler to the entire card to navigate to the tool
        card.addEventListener('click', function(event) {
            // Don't trigger if clicking on the actual button (it has its own handler)
            if (!event.target.closest('.tool-button')) {
                if (toolButton) {
                    // Navigate to the same URL as the button
                    navigateWithConfirmation(toolButton.getAttribute('href'));
                }
            }
        });
    });
}

/**
 * Initialize navigation links
 */
function initNavigationLinks() {
    // Footer links
    document.querySelectorAll('.footer-link').forEach(link => {
        link.addEventListener('click', function(event) {
            // For demo purposes, prevent navigation for now
            event.preventDefault();
            const linkText = this.textContent;
            showModal('Feature Coming Soon', `<p>The "${linkText}" page is under development.</p>`);
        });
    });
}

/**
 * Reset all project data (for debugging/testing)
 */
function resetAllData() {
    confirmAction('This will reset ALL project data. This action cannot be undone. Are you sure?', () => {
        // Get all keys in localStorage that belong to the app
        const keys = Object.keys(localStorage).filter(key => 
            key.startsWith('life2045_') || 
            key === 'hasVisitedBefore'
        );
        
        // Remove all keys
        keys.forEach(key => localStorage.removeItem(key));
        
        // Show confirmation
        showModal('Data Reset', '<p>All project data has been reset successfully.</p>', () => {
            // Reload the page
            window.location.reload();
        });
    });
}
