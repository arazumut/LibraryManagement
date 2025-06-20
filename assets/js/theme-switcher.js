// Theme Switcher
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
});

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Set the new theme
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Save preference to localStorage
    localStorage.setItem('theme', newTheme);
    
    // Update toggle button state
    updateThemeToggleState();
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
