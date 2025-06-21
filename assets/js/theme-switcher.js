// Theme Switcher with enhanced functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use user's system preference
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        // Check user's system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }
    
    // Update toggle button state based on current theme
    updateThemeToggleState();
    
    // Add listener for system theme preference change
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        if (!localStorage.getItem('theme')) {
            // Only update if user hasn't explicitly set a theme preference
            const newTheme = event.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            updateThemeToggleState();
        }
    });
    
    // Add smooth transition class to body
    document.body.classList.add('theme-transition');
});

function toggleTheme() {
    // Add transition effect class
    document.body.classList.add('theme-transition');
    
    // Get current theme and toggle it
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Add animation class
    document.body.classList.add('theme-changing');
    
    // Set the new theme with slight delay for animation
    setTimeout(() => {
        document.documentElement.setAttribute('data-theme', newTheme);
        
        // Save preference to localStorage
        localStorage.setItem('theme', newTheme);
        
        // Update toggle button state
        updateThemeToggleState();
        
        // Remove animation class after transition
        setTimeout(() => {
            document.body.classList.remove('theme-changing');
        }, 500);
    }, 50);
}

function updateThemeToggleState() {
    const themeToggles = document.querySelectorAll('.theme-toggle');
    const currentTheme = document.documentElement.getAttribute('data-theme');
    
    themeToggles.forEach(toggle => {
        if (currentTheme === 'dark') {
            toggle.innerHTML = '<i class="fas fa-sun"></i>';
            toggle.setAttribute('title', 'Açık temaya geç');
        } else {
            toggle.innerHTML = '<i class="fas fa-moon"></i>';
            toggle.setAttribute('title', 'Koyu temaya geç');
        }
    });
}

// Add CSS for transition animation
if (!document.getElementById('theme-transition-style')) {
    const style = document.createElement('style');
    style.id = 'theme-transition-style';
    style.textContent = `
        .theme-transition {
            transition: background-color 0.4s ease, color 0.4s ease;
        }
        .theme-changing {
            animation: theme-fade 0.4s ease;
        }
        @keyframes theme-fade {
            0% {
                opacity: 1;
            }
            50% {
                opacity: 0.8;
            }
            100% {
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
}
