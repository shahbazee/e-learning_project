// E-Learning Platform - main JavaScript
// Responsible for the responsive mobile nav toggle and the home hero banner.

// ---- Responsive mobile navigation toggle ----
document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('navToggle');
    var nav = document.getElementById('navLinks');

    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
        var isOpen = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
});

// ---- Sticky navbar scroll state ----
// Adds a soft shadow to the header once the user scrolls past the top edge.
(function () {
    var header = document.getElementById('siteNav');
    if (!header) return;

    function updateNavbarState() {
        if (window.scrollY > 12) {
            header.classList.add('is-scrolled');
        } else {
            header.classList.remove('is-scrolled');
        }
    }

    window.addEventListener('scroll', updateNavbarState, { passive: true });
    updateNavbarState();
})();

// ---- Home hero banner ----
// Animates the progress ring + bar when the banner scrolls into view, and adds
// a subtle parallax tilt on the dashboard screen for pointer devices. All
// effects stay off for anyone who prefers reduced motion.
document.addEventListener('DOMContentLoaded', function () {
    var banner = document.getElementById('heroBanner');
    if (!banner) return;

    // prefers-reduced-motion guard (older browsers may not implement matchMedia)
    var reducedMotion = false;
    if (window.matchMedia) {
        try {
            reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        } catch (e) { /* fall through to false */ }
    }
    var ring = banner.querySelector('.hero__ring-fill');
    var bar = banner.querySelector('.hero__progress-fill');
    var circ = null;

    if (ring) {
        var r = parseFloat(ring.getAttribute('r')) || 52;
        circ = 2 * Math.PI * r;
        ring.style.strokeDasharray = circ;
        ring.style.strokeDashoffset = circ; // starts empty, animated below
    }

    function runProgress() {
        if (ring) {
            var p = parseFloat(ring.getAttribute('data-progress')) || 75;
            ring.style.strokeDashoffset = circ * (1 - p / 100);
        }
        if (bar) {
            bar.style.width = (bar.getAttribute('data-progress') || '78') + '%';
        }
    }

    if (reducedMotion) {
        runProgress(); // fill instantly for reduced-motion users
    } else if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    runProgress();
                    io.disconnect();
                }
            });
        }, { threshold: 0.25 });
        io.observe(banner);
    } else {
        // Fallback for older browsers without IntersectionObserver
        window.setTimeout(runProgress, 250);
    }

    // Subtle parallax tilt on the dashboard screen (pointer / desktop only).
    var finePointer = false;
    if (window.matchMedia) {
        try {
            finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
        } catch (e) { /* fall through to false */ }
    }
    var screen = banner.querySelector('.hero__screen');
    if (finePointer && !reducedMotion && screen) {
        var MAX_TILT = 6;
        banner.addEventListener('mousemove', function (ev) {
            var rect = banner.getBoundingClientRect();
            var px = ((ev.clientX - rect.left) / rect.width) - 0.5;
            var py = ((ev.clientY - rect.top) / rect.height) - 0.5;
            screen.style.transform =
                'translate(-50%, -50%) rotateX(' + (-py * MAX_TILT) + 'deg) rotateY(' + (px * MAX_TILT) + 'deg)';
        });
        banner.addEventListener('mouseleave', function () {
            screen.style.transform = 'translate(-50%, -50%)';
        });
    }
});
