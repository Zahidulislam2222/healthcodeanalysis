/**
 * HealthCode Design System — GSAP Animations
 * Smooth scroll reveals, staggered entrances, counter animations,
 * hero parallax, ECG pulse, floating particles, micro-interactions.
 *
 * Dependencies: GSAP 3.12+, ScrollTrigger
 * Version: 1.0.0
 */

(function () {
    'use strict';

    /* ------------------------------------------------------------------
       0. WAIT FOR DOM + GSAP READY
       ------------------------------------------------------------------ */
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        console.warn('[HC Design] GSAP or ScrollTrigger not loaded.');
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    /* Respect reduced-motion preference */
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
        document.querySelectorAll('.hc-reveal, .hc-reveal-left, .hc-reveal-right, .hc-reveal-scale').forEach(function (el) {
            el.style.opacity = '1';
            el.style.transform = 'none';
        });
        return;
    }

    /* ------------------------------------------------------------------
       1. CONFIGURATION
       ------------------------------------------------------------------ */
    var CONFIG = {
        staggerDelay: 0.12,
        revealDuration: 0.8,
        revealDistance: 40,
        spring: { ease: 'power3.out' },
        heroParallaxSpeed: 0.3,
        particleCount: 35,
        particleColors: ['#06b6d4', '#3b82f6', '#8b5cf6', '#10b981']
    };

    /* ------------------------------------------------------------------
       2. PAGE ENTRANCE ANIMATION
       ------------------------------------------------------------------ */
    function initPageEntrance() {
        gsap.fromTo('body',
            { opacity: 0 },
            { opacity: 1, duration: 0.6, ease: 'power2.out' }
        );
    }

    /* ------------------------------------------------------------------
       3. SCROLL REVEAL — Sections & Widgets
       ------------------------------------------------------------------ */
    function initScrollReveals() {
        /* Generic: all Elementor sections fade-up on scroll */
        var sections = document.querySelectorAll('.elementor-section, .e-con');
        sections.forEach(function (section, index) {
            /* Skip the hero (first section) — it has its own animation */
            if (index === 0) return;

            gsap.fromTo(section,
                { opacity: 0, y: CONFIG.revealDistance },
                {
                    opacity: 1,
                    y: 0,
                    duration: CONFIG.revealDuration,
                    ease: CONFIG.spring.ease,
                    scrollTrigger: {
                        trigger: section,
                        start: 'top 85%',
                        end: 'top 40%',
                        toggleActions: 'play none none none',
                        once: true
                    }
                }
            );
        });

        /* Staggered widgets within each section */
        sections.forEach(function (section, index) {
            if (index === 0) return;

            var widgets = section.querySelectorAll('.elementor-widget');
            if (widgets.length < 2) return;

            gsap.fromTo(widgets,
                { opacity: 0, y: 25 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.6,
                    stagger: CONFIG.staggerDelay,
                    ease: CONFIG.spring.ease,
                    scrollTrigger: {
                        trigger: section,
                        start: 'top 80%',
                        toggleActions: 'play none none none',
                        once: true
                    }
                }
            );
        });
    }

    /* ------------------------------------------------------------------
       4. HERO SECTION — Entrance + Parallax
       ------------------------------------------------------------------ */
    function initHero() {
        var hero = document.querySelector('.elementor-page .elementor > .elementor-section:first-child') ||
                   document.querySelector('.elementor-page .elementor > .e-con:first-child');

        if (!hero) return;

        /* Hero content entrance */
        var heroHeadings = hero.querySelectorAll('.elementor-heading-title');
        var heroTexts = hero.querySelectorAll('.elementor-text-editor');
        var heroButtons = hero.querySelectorAll('.elementor-button-wrapper');
        var heroImages = hero.querySelectorAll('.elementor-widget-image');

        var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        if (heroHeadings.length) {
            tl.fromTo(heroHeadings,
                { opacity: 0, y: 40, clipPath: 'inset(0 0 100% 0)' },
                { opacity: 1, y: 0, clipPath: 'inset(0 0 0% 0)', duration: 1, stagger: 0.15 },
                0.2
            );
        }

        if (heroTexts.length) {
            tl.fromTo(heroTexts,
                { opacity: 0, y: 20 },
                { opacity: 1, y: 0, duration: 0.8, stagger: 0.1 },
                0.6
            );
        }

        if (heroButtons.length) {
            tl.fromTo(heroButtons,
                { opacity: 0, y: 20, scale: 0.95 },
                { opacity: 1, y: 0, scale: 1, duration: 0.6, stagger: 0.1 },
                0.8
            );
        }

        if (heroImages.length) {
            tl.fromTo(heroImages,
                { opacity: 0, scale: 0.9 },
                { opacity: 1, scale: 1, duration: 1 },
                0.4
            );
        }

        /* Parallax on hero background */
        var heroBg = hero.querySelector('.elementor-background-overlay') ||
                     hero.querySelector('.elementor-section-background') ||
                     hero;

        gsap.to(heroBg, {
            y: function () { return window.innerHeight * CONFIG.heroParallaxSpeed; },
            ease: 'none',
            scrollTrigger: {
                trigger: hero,
                start: 'top top',
                end: 'bottom top',
                scrub: 1
            }
        });

        /* Inject ECG pulse line into hero */
        injectECGPulse(hero);
    }

    /* ------------------------------------------------------------------
       5. ECG PULSE LINE — Medical heartbeat animation
       ------------------------------------------------------------------ */
    function injectECGPulse(container) {
        if (!container) return;

        var ecgContainer = document.createElement('div');
        ecgContainer.className = 'hc-ecg-container';

        var ecgLine = document.createElement('div');
        ecgLine.className = 'hc-ecg-line';

        /* SVG heartbeat path */
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
       6. COUNTER ANIMATIONS — Animate numbers when visible
       ------------------------------------------------------------------ */
    function initCounterAnimations() {
        var counters = document.querySelectorAll('.elementor-counter-number');
        counters.forEach(function (counter) {
            var endValue = parseInt(counter.getAttribute('data-to-value') || counter.textContent, 10);
            if (isNaN(endValue)) return;

            var obj = { val: 0 };

            ScrollTrigger.create({
                trigger: counter,
                start: 'top 85%',
                once: true,
                onEnter: function () {
                    gsap.to(obj, {
                        val: endValue,
                        duration: 2,
                        ease: 'power2.out',
                        onUpdate: function () {
                            counter.textContent = Math.round(obj.val).toLocaleString();
                        }
                    });
                }
            });
        });
    }

    /* ------------------------------------------------------------------
       7. ICON BOX & CARD HOVER EFFECTS
       ------------------------------------------------------------------ */
    function initHoverEffects() {
        /* Icon boxes */
        var iconBoxes = document.querySelectorAll('.elementor-widget-icon-box .elementor-icon-box-wrapper');
        iconBoxes.forEach(function (box) {
            box.addEventListener('mouseenter', function () {
                gsap.to(box, { y: -4, duration: 0.3, ease: 'power2.out' });
            });
            box.addEventListener('mouseleave', function () {
                gsap.to(box, { y: 0, duration: 0.3, ease: 'power2.out' });
            });
        });

        /* Post cards */
        var postCards = document.querySelectorAll('.elementor-post, .jet-listing-grid__item');
        postCards.forEach(function (card) {
            card.addEventListener('mouseenter', function () {
                gsap.to(card, { y: -6, duration: 0.3, ease: 'power2.out' });
            });
            card.addEventListener('mouseleave', function () {
                gsap.to(card, { y: 0, duration: 0.3, ease: 'power2.out' });
            });
        });

        /* Buttons — micro-interaction */
        var buttons = document.querySelectorAll('.elementor-button');
        buttons.forEach(function (btn) {
            btn.addEventListener('mouseenter', function () {
                gsap.to(btn, { scale: 1.03, duration: 0.2, ease: 'power2.out' });
            });
            btn.addEventListener('mouseleave', function () {
                gsap.to(btn, { scale: 1, duration: 0.2, ease: 'power2.out' });
            });
            btn.addEventListener('mousedown', function () {
                gsap.to(btn, { scale: 0.97, duration: 0.1 });
            });
            btn.addEventListener('mouseup', function () {
                gsap.to(btn, { scale: 1.03, duration: 0.1 });
            });
        });

        /* Images — subtle zoom on hover */
        var images = document.querySelectorAll('.elementor-widget-image img');
        images.forEach(function (img) {
            img.addEventListener('mouseenter', function () {
                gsap.to(img, { scale: 1.03, duration: 0.4, ease: 'power2.out' });
            });
            img.addEventListener('mouseleave', function () {
                gsap.to(img, { scale: 1, duration: 0.4, ease: 'power2.out' });
            });
        });

        /* Testimonials */
        var testimonials = document.querySelectorAll('.elementor-widget-testimonial .elementor-testimonial-wrapper');
        testimonials.forEach(function (card) {
            card.addEventListener('mouseenter', function () {
                gsap.to(card, { y: -3, duration: 0.3, ease: 'power2.out' });
            });
            card.addEventListener('mouseleave', function () {
                gsap.to(card, { y: 0, duration: 0.3, ease: 'power2.out' });
            });
        });
    }

    /* ------------------------------------------------------------------
       8. FLOATING PARTICLES — Canvas-based ambient effect
       ------------------------------------------------------------------ */
    function initParticles() {
        /* Skip on mobile for performance */
        if (window.innerWidth < 768) return;

        var canvas = document.createElement('canvas');
        canvas.id = 'hc-particles-canvas';
        document.body.appendChild(canvas);

        var ctx = canvas.getContext('2d');
        var particles = [];
        var mouse = { x: -1000, y: -1000 };

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        /* Track mouse for interactive particles */
        document.addEventListener('mousemove', function (e) {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        /* Create particles */
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

        function drawParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(function (p, i) {
                /* Move */
                p.x += p.vx;
                p.y += p.vy;

                /* Mouse interaction — subtle push */
                var dx = p.x - mouse.x;
                var dy = p.y - mouse.y;
                var dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    var force = (120 - dist) / 120 * 0.02;
                    p.vx += dx * force;
                    p.vy += dy * force;
                }

                /* Damping */
                p.vx *= 0.99;
                p.vy *= 0.99;

                /* Wrap around edges */
                if (p.x < -10) p.x = canvas.width + 10;
                if (p.x > canvas.width + 10) p.x = -10;
                if (p.y < -10) p.y = canvas.height + 10;
                if (p.y > canvas.height + 10) p.y = -10;

                /* Draw particle */
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.fill();

                /* Draw connections to nearby particles */
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
            requestAnimationFrame(drawParticles);
        }

        drawParticles();
    }

    /* ------------------------------------------------------------------
       9. MAGNETIC CURSOR EFFECT — Buttons attract cursor subtly
       ------------------------------------------------------------------ */
    function initMagneticButtons() {
        if (window.innerWidth < 1024) return;

        var magneticElements = document.querySelectorAll('.elementor-button, .elementor-widget-social-icons .elementor-icon');

        magneticElements.forEach(function (el) {
            el.addEventListener('mousemove', function (e) {
                var rect = el.getBoundingClientRect();
                var x = e.clientX - rect.left - rect.width / 2;
                var y = e.clientY - rect.top - rect.height / 2;
                gsap.to(el, {
                    x: x * 0.15,
                    y: y * 0.15,
                    duration: 0.3,
                    ease: 'power2.out'
                });
            });

            el.addEventListener('mouseleave', function () {
                gsap.to(el, {
                    x: 0,
                    y: 0,
                    duration: 0.5,
                    ease: 'elastic.out(1, 0.5)'
                });
            });
        });
    }

    /* ------------------------------------------------------------------
       10. SMOOTH HEADER BEHAVIOR — Glassmorphic on scroll
       ------------------------------------------------------------------ */
    function initHeaderEffects() {
        var header = document.querySelector('.site-header, #masthead, .ast-primary-header-bar');
        if (!header) return;

        ScrollTrigger.create({
            start: 'top -80',
            end: 'max',
            onUpdate: function (self) {
                if (self.direction === 1 && self.scroll() > 200) {
                    /* Scrolling down — hide header */
                    gsap.to(header, { y: -100, duration: 0.3, ease: 'power2.in' });
                } else {
                    /* Scrolling up — show header */
                    gsap.to(header, { y: 0, duration: 0.3, ease: 'power2.out' });
                }
            }
        });
    }

    /* ------------------------------------------------------------------
       11. COLUMN STAGGER — Side-by-side columns animate in sequence
       ------------------------------------------------------------------ */
    function initColumnStagger() {
        var rows = document.querySelectorAll('.elementor-row, .e-con[data-element_type="container"]');
        rows.forEach(function (row) {
            var cols = row.querySelectorAll('.elementor-column, .e-con > .e-con');
            if (cols.length < 2) return;

            gsap.fromTo(cols,
                { opacity: 0, y: 30 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.7,
                    stagger: 0.15,
                    ease: CONFIG.spring.ease,
                    scrollTrigger: {
                        trigger: row,
                        start: 'top 80%',
                        once: true
                    }
                }
            );
        });
    }

    /* ------------------------------------------------------------------
       12. TEXT REVEAL — Character-by-character for hero headings
       ------------------------------------------------------------------ */
    function initTextReveal() {
        var hero = document.querySelector('.elementor-page .elementor > .elementor-section:first-child') ||
                   document.querySelector('.elementor-page .elementor > .e-con:first-child');
        if (!hero) return;

        var headings = hero.querySelectorAll('.elementor-heading-title');
        headings.forEach(function (heading) {
            var text = heading.textContent;
            heading.innerHTML = '';
            heading.style.opacity = '1';

            /* Wrap each word in a span */
            var words = text.split(' ');
            words.forEach(function (word, i) {
                var wordSpan = document.createElement('span');
                wordSpan.style.display = 'inline-block';
                wordSpan.style.overflow = 'hidden';

                var innerSpan = document.createElement('span');
                innerSpan.textContent = word;
                innerSpan.style.display = 'inline-block';
                innerSpan.className = 'hc-word-reveal';

                wordSpan.appendChild(innerSpan);
                heading.appendChild(wordSpan);

                /* Add space between words */
                if (i < words.length - 1) {
                    heading.appendChild(document.createTextNode('\u00A0'));
                }
            });

            /* Animate words */
            gsap.fromTo(heading.querySelectorAll('.hc-word-reveal'),
                { y: '110%', opacity: 0 },
                {
                    y: '0%',
                    opacity: 1,
                    duration: 0.8,
                    stagger: 0.06,
                    ease: 'power3.out',
                    delay: 0.3
                }
            );
        });
    }

    /* ------------------------------------------------------------------
       INIT — Run everything when DOM is ready
       ------------------------------------------------------------------ */
    function init() {
        initPageEntrance();
        initTextReveal();
        initHero();
        initScrollReveals();
        initColumnStagger();
        initCounterAnimations();
        initHoverEffects();
        initMagneticButtons();
        initParticles();
        initHeaderEffects();

        /* Refresh ScrollTrigger after all images/fonts load */
        window.addEventListener('load', function () {
            ScrollTrigger.refresh();
        });
    }

    /* Run on DOMContentLoaded */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
