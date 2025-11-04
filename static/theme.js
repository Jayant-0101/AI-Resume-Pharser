// Theme Toggle Functionality
(function() {
    'use strict';

    // Get theme toggle elements
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const body = document.body;

    // Check for saved theme preference or default to dark mode
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    // Apply saved theme
    if (savedTheme === 'light') {
        body.classList.add('light-mode');
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }

    // Theme toggle handler
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('light-mode');
            
            const isLightMode = body.classList.contains('light-mode');
            
            // Update icon
            if (themeIcon) {
                if (isLightMode) {
                    themeIcon.classList.remove('fa-moon');
                    themeIcon.classList.add('fa-sun');
                } else {
                    themeIcon.classList.remove('fa-sun');
                    themeIcon.classList.add('fa-moon');
                }
            }
            
            // Save preference
            localStorage.setItem('theme', isLightMode ? 'light' : 'dark');
            
            // Add animation effect
            themeToggle.style.transform = 'rotate(360deg) scale(0.8)';
            setTimeout(() => {
                themeToggle.style.transform = '';
            }, 300);
        });
    }

    // Add smooth page transitions
    document.addEventListener('DOMContentLoaded', () => {
        // Fade in on page load
        document.body.style.opacity = '0';
        setTimeout(() => {
            document.body.style.transition = 'opacity 0.5s ease';
            document.body.style.opacity = '1';
        }, 100);
    });
})();

