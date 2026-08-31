// E-Learning Platform - minimal JS
// Only used for the responsive mobile navigation toggle.

document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('navToggle');
    var nav = document.getElementById('navLinks');

    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
        var isOpen = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
});
