(function () {
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        document.querySelectorAll('.theme-toggle-icon').forEach(function (el) {
            el.textContent = theme === 'dark' ? '☀️' : '🌙';
        });
    }

    window.togglePsTheme = function () {
        var current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        var next = current === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('ps-theme', next); } catch (e) { /* ignore */ }
        applyTheme(next);
    };

    document.addEventListener('DOMContentLoaded', function () {
        var saved = 'light';
        try { saved = localStorage.getItem('ps-theme') || 'light'; } catch (e) { /* ignore */ }
        applyTheme(saved);
    });
})();