/**
 * HealthCode Design System — Vanilla JS Animations
 * Version: 3.0.0 — No external dependencies (replaced GSAP with IntersectionObserver + CSS)
 */

(function () {
    'use strict';

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var CONFIG = {
        staggerDelay: 120,
        revealDistance: 40,
        particleCount: 35,
        particleColors: ['#06b6d4', '#3b82f6', '#8b5cf6', '#10b981']
    };

    /* ------------------------------------------------------------------
       UTILITY: Observe elements and trigger callback on enter
       ------------------------------------------------------------------ */
    function observeOnce(elements, callback, options) {
        if (!elements || elements.length === 0) return;
        var defaults = { threshold: 0.1, rootMargin: '0px 0px -15% 0px' };
        var opts = Object.assign({}, defaults, options || {});

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    callback(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, opts);

        elements.forEach(function (el) { observer.observe(el); });
    }

    /* ------------------------------------------------------------------
       UTILITY: Animate element with CSS transition
       ------------------------------------------------------------------ */
    function animateIn(el, delay) {
        delay = delay || 0;
        setTimeout(function () {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, delay);
    }

    function prepareHidden(el, distance) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(' + (distance || CONFIG.revealDistance) + 'px)';
        el.style.transition = 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
    }

    /* ------------------------------------------------------------------
       0. FORCE DARK BACKGROUNDS — Override inline white styles via JS
       ------------------------------------------------------------------ */
    function forceDarkBackgrounds() {
        var everything = document.querySelectorAll('*');
        everything.forEach(function (el) {
            var computed = window.getComputedStyle(el);
            var bg = computed.backgroundColor;
            if (bg && isLightColor(bg)) {
                var tag = el.tagName.toLowerCase();
                if (tag === 'button' || tag === 'svg' || tag === 'img') return;
                if (el.classList.contains('elementor-button')) return;
                if (el.classList.contains('nsl-button-svg-container')) return;
                if (el.closest && (el.closest('.elementor-button') || el.closest('.nsl-button'))) return;

                el.style.setProperty('background-color', 'transparent', 'important');
            }
        });

        document.querySelectorAll('style').forEach(function (sheet) {
            var text = sheet.textContent;
            var newText = text
                .replace(/background-color\s*:\s*#(?:fff(?:fff)?|E8EAFF|f8faff|ECEFF3|F9FAFB|f9f9f9|FFFFFF)\s*;/gi, 'background-color: transparent !important;')
                .replace(/background\s*:\s*#(?:fff(?:fff)?|E8EAFF|f8faff|ECEFF3|F9FAFB|f9f9f9|FFFFFF)\s*;/gi, 'background: transparent !important;')
                .replace(/background-color\s*:\s*white\s*;/gi, 'background-color: transparent !important;');
            if (newText !== text) {
                sheet.textContent = newText;
            }
        });
    }

    function isLightColor(color) {
        if (!color || color === 'transparent' || color === 'rgba(0, 0, 0, 0)') return false;
        var match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (match) {
            var r = parseInt(match[1]);
            var g = parseInt(match[2]);
            var b = parseInt(match[3]);
            var brightness = (r * 299 + g * 587 + b * 114) / 1000;
            return brightness > 180;
        }
        return false;
    }

    /* ------------------------------------------------------------------
       1. PAGE ENTRANCE
       ------------------------------------------------------------------ */
    function initPageEntrance() {
        if (prefersReducedMotion) return;
        var pageContent = document.querySelector('[data-elementor-type="wp-page"]') ||
                          document.querySelector('.elementor-page .elementor');
        if (pageContent) {
            pageContent.style.opacity = '0';
            pageContent.style.transition = 'opacity 0.6s ease-out';
            requestAnimationFrame(function () {
                pageContent.style.opacity = '1';
            });
        }
    }

    /* ------------------------------------------------------------------
       2. SCROLL REVEALS — e-con sections
       ------------------------------------------------------------------ */
    function initScrollReveals() {
        if (prefersReducedMotion) return;

        var sections = document.querySelectorAll('[data-elementor-type="wp-page"] .e-con.e-parent');
        var revealSections = [];
        sections.forEach(function (section, index) {
            if (index === 0) return;
            prepareHidden(section);
            revealSections.push(section);
        });

        observeOnce(revealSections, function (section) {
            animateIn(section);

            // Stagger widgets within
            var widgets = section.querySelectorAll('.elementor-widget');
            if (widgets.length < 2) return;
            widgets.forEach(function (widget, i) {
                widget.style.opacity = '0';
                widget.style.transform = 'translateY(25px)';
                widget.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
                animateIn(widget, i * CONFIG.staggerDelay);
            });
        });
    }

    /* ------------------------------------------------------------------
       3. HERO SECTION — First e-con.e-parent
       ------------------------------------------------------------------ */
    function initHero() {
        if (prefersReducedMotion) return;

        var hero = document.querySelector('[data-elementor-type="wp-page"] > .e-con.e-parent:first-child');
        if (!hero) return;

        var groups = [
            { els: hero.querySelectorAll('.elementor-heading-title'), delay: 200, distance: 30, duration: 1000 },
            { els: hero.querySelectorAll('.elementor-widget-image'), delay: 400, distance: 0, scale: true, duration: 1000 },
            { els: hero.querySelectorAll('.elementor-text-editor'), delay: 600, distance: 20, duration: 800 },
            { els: hero.querySelectorAll('.elementor-button-wrapper'), delay: 800, distance: 20, duration: 600 }
        ];

        groups.forEach(function (group) {
            group.els.forEach(function (el, i) {
                el.style.opacity = '0';
                if (group.scale) {
                    el.style.transform = 'scale(0.9)';
                } else {
                    el.style.transform = 'translateY(' + group.distance + 'px)';
                }
                el.style.transition = 'opacity ' + group.duration + 'ms cubic-bezier(0.16, 1, 0.3, 1), transform ' + group.duration + 'ms cubic-bezier(0.16, 1, 0.3, 1)';

                setTimeout(function () {
                    el.style.opacity = '1';
                    el.style.transform = group.scale ? 'scale(1)' : 'translateY(0)';
                }, group.delay + i * 150);
            });
        });

        injectECGPulse(hero);
    }

    /* ------------------------------------------------------------------
       4. ECG PULSE LINE
       ------------------------------------------------------------------ */
    function injectECGPulse(container) {
        if (!container) return;
        var ecgContainer = document.createElement('div');
        ecgContainer.className = 'hc-ecg-container';

        var ecgLine = document.createElement('div');
        ecgLine.className = 'hc-ecg-line';

        var svgMarkup =
            '<svg viewBox="0 0 600 80" preserveAspectRatio="none">' +
            '<path d="M0,40 L100,40 L120,40 L140,20 L160,60 L170,10 L180,70 L190,30 L200,40 L300,40 L320,40 L340,25 L360,55 L370,15 L380,65 L390,35 L400,40 L600,40"/>' +
            '</svg>';

        ecgLine.innerHTML = svgMarkup + svgMarkup;
        ecgContainer.appendChild(ecgLine);
        container.style.position = 'relative';
        container.appendChild(ecgContainer);
    }

    /* ------------------------------------------------------------------
       5. COUNTER ANIMATIONS
       ------------------------------------------------------------------ */
    function initCounterAnimations() {
        if (prefersReducedMotion) return;
        var counters = document.querySelectorAll('.elementor-counter-number');

        observeOnce(counters, function (counter) {
            var endValue = parseInt(counter.getAttribute('data-to-value') || counter.textContent, 10);
            if (isNaN(endValue)) return;

            var startTime = null;
            var duration = 2000;

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                var progress = Math.min((timestamp - startTime) / duration, 1);
                // ease-out quad
                var eased = 1 - (1 - progress) * (1 - progress);
                counter.textContent = Math.round(eased * endValue).toLocaleString();
                if (progress < 1) {
                    requestAnimationFrame(step);
                }
            }
            requestAnimationFrame(step);
        }, { rootMargin: '0px 0px -15% 0px' });
    }

    /* ------------------------------------------------------------------
       6. HOVER EFFECTS (CSS transitions, no library needed)
       ------------------------------------------------------------------ */
    function initHoverEffects() {
        if (prefersReducedMotion) return;

        function addHover(selector, enterTransform, duration) {
            document.querySelectorAll(selector).forEach(function (el) {
                el.style.transition = 'transform ' + duration + 's ease-out';
                el.addEventListener('mouseenter', function () { el.style.transform = enterTransform; });
                el.addEventListener('mouseleave', function () { el.style.transform = ''; });
            });
        }

        addHover('.elementor-widget-icon-box .elementor-icon-box-wrapper', 'translateY(-4px)', 0.3);
        addHover('.elementor-post, .jet-listing-grid__item', 'translateY(-6px)', 0.3);
        addHover('.elementor-widget-image img', 'scale(1.03)', 0.4);

        // Buttons get press effect too
        document.querySelectorAll('.elementor-button').forEach(function (btn) {
            btn.style.transition = 'transform 0.2s ease-out';
            btn.addEventListener('mouseenter', function () { btn.style.transform = 'scale(1.03)'; });
            btn.addEventListener('mouseleave', function () { btn.style.transform = ''; });
            btn.addEventListener('mousedown', function () { btn.style.transform = 'scale(0.97)'; });
            btn.addEventListener('mouseup', function () { btn.style.transform = 'scale(1.03)'; });
        });
    }

    /* ------------------------------------------------------------------
       7. FLOATING PARTICLES (already pure canvas — no GSAP)
       ------------------------------------------------------------------ */
    function initParticles() {
        if (window.innerWidth < 768 || prefersReducedMotion) return;

        var canvas = document.createElement('canvas');
        canvas.id = 'hc-particles-canvas';
        document.body.appendChild(canvas);

        var ctx = canvas.getContext('2d');
        var particles = [];
        var mouse = { x: -1000, y: -1000 };

        function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        resize();
        window.addEventListener('resize', resize);
        document.addEventListener('mousemove', function (e) { mouse.x = e.clientX; mouse.y = e.clientY; });

        for (var i = 0; i < CONFIG.particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                radius: Math.random() * 2 + 0.5,
                color: CONFIG.particleColors[Math.floor(Math.random() * CONFIG.particleColors.length)],
                alpha: Math.random() * 0.5 + 0.2
            });
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(function (p, i) {
                p.x += p.vx;
                p.y += p.vy;
                var dx = p.x - mouse.x;
                var dy = p.y - mouse.y;
                var dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    var force = (120 - dist) / 120 * 0.02;
                    p.vx += dx * force;
                    p.vy += dy * force;
                }
                p.vx *= 0.99;
                p.vy *= 0.99;
                if (p.x < -10) p.x = canvas.width + 10;
                if (p.x > canvas.width + 10) p.x = -10;
                if (p.y < -10) p.y = canvas.height + 10;
                if (p.y > canvas.height + 10) p.y = -10;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.fill();

                for (var j = i + 1; j < particles.length; j++) {
                    var p2 = particles[j];
                    var ddx = p.x - p2.x;
                    var ddy = p.y - p2.y;
                    var distance = Math.sqrt(ddx * ddx + ddy * ddy);
                    if (distance < 150) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = p.color;
                        ctx.globalAlpha = (1 - distance / 150) * 0.15;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            });
            ctx.globalAlpha = 1;
            requestAnimationFrame(draw);
        }
        draw();
    }

    /* ------------------------------------------------------------------
       8. MAGNETIC BUTTONS
       ------------------------------------------------------------------ */
    function initMagneticButtons() {
        if (window.innerWidth < 1024 || prefersReducedMotion) return;
        document.querySelectorAll('.elementor-button').forEach(function (el) {
            el.addEventListener('mousemove', function (e) {
                var rect = el.getBoundingClientRect();
                var x = (e.clientX - rect.left - rect.width / 2) * 0.15;
                var y = (e.clientY - rect.top - rect.height / 2) * 0.15;
                el.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
            });
            el.addEventListener('mouseleave', function () {
                el.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
                el.style.transform = '';
                setTimeout(function () { el.style.transition = ''; }, 500);
            });
        });
    }

    /* ------------------------------------------------------------------
       9. STICKY HEADER — handled by plugin
       ------------------------------------------------------------------ */
    function initHeaderEffects() {
        /* no-op — plugin handles sticky */
    }

    /* ------------------------------------------------------------------
       10. COLUMN STAGGER — e-child containers within e-parent
       ------------------------------------------------------------------ */
    function initColumnStagger() {
        if (prefersReducedMotion) return;
        var parents = document.querySelectorAll('[data-elementor-type="wp-page"] .e-con.e-parent');
        var targets = [];

        parents.forEach(function (parent, index) {
            if (index === 0) return;
            var children = parent.querySelectorAll(':scope > .e-con-inner > .e-con.e-child');
            if (children.length < 2) return;

            children.forEach(function (child) {
                prepareHidden(child, 30);
                child.style.transitionDuration = '0.7s';
            });
            targets.push({ parent: parent, children: children });
        });

        targets.forEach(function (t) {
            observeOnce([t.parent], function () {
                t.children.forEach(function (child, i) {
                    animateIn(child, i * 150);
                });
            });
        });
    }

    /* ------------------------------------------------------------------
       11. POPUP BACKGROUND FIX
       ------------------------------------------------------------------ */
    function initPopupFix() {
        function fixPopup() {
            var content = document.querySelector('.hca-popup-content');
            if (content) {
                content.style.setProperty('background-color', 'rgba(15, 18, 37, 0.97)', 'important');
                content.style.setProperty('border', '1px solid rgba(255,255,255,0.1)', '');
                content.style.setProperty('border-radius', '16px', '');
                content.style.setProperty('padding', '32px', '');
                content.style.setProperty('max-width', '440px', '');
                content.style.setProperty('width', '100%', '');
                content.style.setProperty('box-shadow', '0 20px 60px rgba(0,0,0,0.6)', '');
            }
        }

        var obs = new MutationObserver(function () { fixPopup(); });
        obs.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['style'] });

        var checks = 0;
        var interval = setInterval(function () {
            fixPopup();
            checks++;
            if (checks > 20) clearInterval(interval);
        }, 500);
    }

    /* ------------------------------------------------------------------
       12. FIX NEUROSCAN AJAX FILTER — Patch broken sibling selector
       The Code Snippets JS uses container.next('.neuro-grid-instance')
       but Elementor wraps filter and grid in separate containers,
       so they're not DOM siblings. This patches the click handler.
       ------------------------------------------------------------------ */
    function fixNeuroFilter() {
        var buttons = document.querySelectorAll('.neuro-filter-btn');
        if (!buttons.length) return;

        buttons.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                // Find the grid anywhere on the page (not just siblings)
                var grid = document.querySelector('.neuro-grid-instance');
                if (!grid || typeof jQuery === 'undefined') return;

                var slug = btn.getAttribute('data-slug');
                var container = btn.closest('.neuro-filter-container');

                // Update button visual state
                if (container) {
                    container.querySelectorAll('.neuro-filter-btn').forEach(function (b) {
                        b.classList.remove('active');
                    });
                }
                btn.classList.add('active');

                // Call the existing runGridUpdate via jQuery trigger
                var $grid = jQuery(grid);
                var cfg = $grid.data('config') || {};

                $grid.css('opacity', '0.5');

                jQuery.ajax({
                    url: window.location.origin + '/wp-admin/admin-ajax.php',
                    type: 'POST',
                    data: {
                        action: 'neuro_update_components',
                        category: slug,
                        search: '',
                        paged: 1,
                        count: cfg.count,
                        hero: cfg.hero,
                        featured_id: cfg.featured_id,
                        sort: cfg.sort,
                        pagination: cfg.pagination,
                        columns: cfg.columns,
                        hide_meta: cfg.hide_meta,
                        hide_author: cfg.hide_author,
                        offset: cfg.offset
                    },
                    success: function (response) {
                        $grid.html(response);
                        $grid.css('opacity', '1');
                        $grid.data('current-cat', slug);
                    },
                    error: function () {
                        $grid.css('opacity', '1');
                    }
                });

                // Stop the broken original handler from also firing
                e.stopImmediatePropagation();
            });
        });
    }

    /* ------------------------------------------------------------------
       INIT
       ------------------------------------------------------------------ */
    function init() {
        forceDarkBackgrounds();
        initPageEntrance();
        initHero();
        initScrollReveals();
        initColumnStagger();
        initCounterAnimations();
        initHoverEffects();
        initMagneticButtons();
        initParticles();
        initHeaderEffects();
        initPopupFix();
        fixNeuroFilter();

        setTimeout(forceDarkBackgrounds, 1000);
        setTimeout(forceDarkBackgrounds, 3000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
