/**
 * HealthCode Design System — GSAP Animations
 * Version: 2.0.0 — Rewritten for Elementor Flexbox Containers (e-con)
 */

(function () {
    'use strict';

    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        console.warn('[HC Design] GSAP or ScrollTrigger not loaded.');
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var CONFIG = {
        staggerDelay: 0.12,
        revealDuration: 0.8,
        revealDistance: 40,
        heroParallaxSpeed: 0.3,
        particleCount: 35,
        particleColors: ['#06b6d4', '#3b82f6', '#8b5cf6', '#10b981']
    };

    /* ------------------------------------------------------------------
       0. FORCE DARK BACKGROUNDS — Override inline white styles via JS
       ------------------------------------------------------------------ */
    function forceDarkBackgrounds() {
        /* 1. Nuke ALL inline white backgrounds on every element */
        var everything = document.querySelectorAll('*');
        everything.forEach(function (el) {
            var computed = window.getComputedStyle(el);
            var bg = computed.backgroundColor;
            if (bg && isLightColor(bg)) {
                /* Skip buttons, social icons, tiny UI */
                var tag = el.tagName.toLowerCase();
                if (tag === 'button' || tag === 'svg' || tag === 'img') return;
                if (el.classList.contains('elementor-button')) return;
                if (el.classList.contains('nsl-button-svg-container')) return;
                if (el.closest && (el.closest('.elementor-button') || el.closest('.nsl-button'))) return;

                el.style.setProperty('background-color', 'transparent', 'important');
            }
        });

        /* 2. Rewrite ALL Elementor-generated <style> blocks — replace white with transparent */
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
        /* Parse rgb/rgba */
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
        gsap.fromTo('body', { opacity: 0 }, { opacity: 1, duration: 0.6, ease: 'power2.out' });
    }

    /* ------------------------------------------------------------------
       2. SCROLL REVEALS — e-con sections
       ------------------------------------------------------------------ */
    function initScrollReveals() {
        if (prefersReducedMotion) return;

        /* Parent containers = main sections */
        var sections = document.querySelectorAll('.e-con.e-parent');
        sections.forEach(function (section, index) {
            if (index === 0) return; /* Skip hero */

            gsap.fromTo(section,
                { opacity: 0, y: CONFIG.revealDistance },
                {
                    opacity: 1, y: 0,
                    duration: CONFIG.revealDuration,
                    ease: 'power3.out',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top 85%',
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
                    opacity: 1, y: 0,
                    duration: 0.6,
                    stagger: CONFIG.staggerDelay,
                    ease: 'power3.out',
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
       3. HERO SECTION — First e-con.e-parent
       ------------------------------------------------------------------ */
    function initHero() {
        if (prefersReducedMotion) return;

        var hero = document.querySelector('.elementor-page .elementor > .e-con.e-parent:first-child') ||
                   document.querySelector('.elementor > .e-con.e-parent:first-child');
        if (!hero) return;

        var heroHeadings = hero.querySelectorAll('.elementor-heading-title');
        var heroTexts = hero.querySelectorAll('.elementor-text-editor');
        var heroButtons = hero.querySelectorAll('.elementor-button-wrapper');
        var heroImages = hero.querySelectorAll('.elementor-widget-image');

        var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        /* Word-by-word text reveal */
        heroHeadings.forEach(function (heading) {
            var text = heading.textContent.trim();
            if (!text) return;
            heading.innerHTML = '';
            heading.style.opacity = '1';

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

                if (i < words.length - 1) {
                    heading.appendChild(document.createTextNode('\u00A0'));
                }
            });

            tl.fromTo(heading.querySelectorAll('.hc-word-reveal'),
                { y: '110%', opacity: 0 },
                { y: '0%', opacity: 1, duration: 0.8, stagger: 0.06, ease: 'power3.out' },
                0.3
            );
        });

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

        /* Parallax on hero */
        gsap.to(hero, {
            y: function () { return window.innerHeight * CONFIG.heroParallaxSpeed; },
            ease: 'none',
            scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: 1 }
        });

        /* ECG pulse line */
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
       6. HOVER EFFECTS
       ------------------------------------------------------------------ */
    function initHoverEffects() {
        if (prefersReducedMotion) return;

        /* Icon boxes */
        document.querySelectorAll('.elementor-widget-icon-box .elementor-icon-box-wrapper').forEach(function (box) {
            box.addEventListener('mouseenter', function () { gsap.to(box, { y: -4, duration: 0.3, ease: 'power2.out' }); });
            box.addEventListener('mouseleave', function () { gsap.to(box, { y: 0, duration: 0.3, ease: 'power2.out' }); });
        });

        /* Post cards */
        document.querySelectorAll('.elementor-post, .jet-listing-grid__item').forEach(function (card) {
            card.addEventListener('mouseenter', function () { gsap.to(card, { y: -6, duration: 0.3, ease: 'power2.out' }); });
            card.addEventListener('mouseleave', function () { gsap.to(card, { y: 0, duration: 0.3, ease: 'power2.out' }); });
        });

        /* Buttons */
        document.querySelectorAll('.elementor-button').forEach(function (btn) {
            btn.addEventListener('mouseenter', function () { gsap.to(btn, { scale: 1.03, duration: 0.2, ease: 'power2.out' }); });
            btn.addEventListener('mouseleave', function () { gsap.to(btn, { scale: 1, duration: 0.2, ease: 'power2.out' }); });
            btn.addEventListener('mousedown', function () { gsap.to(btn, { scale: 0.97, duration: 0.1 }); });
            btn.addEventListener('mouseup', function () { gsap.to(btn, { scale: 1.03, duration: 0.1 }); });
        });

        /* Images */
        document.querySelectorAll('.elementor-widget-image img').forEach(function (img) {
            img.addEventListener('mouseenter', function () { gsap.to(img, { scale: 1.03, duration: 0.4, ease: 'power2.out' }); });
            img.addEventListener('mouseleave', function () { gsap.to(img, { scale: 1, duration: 0.4, ease: 'power2.out' }); });
        });
    }

    /* ------------------------------------------------------------------
       7. FLOATING PARTICLES
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
                var x = e.clientX - rect.left - rect.width / 2;
                var y = e.clientY - rect.top - rect.height / 2;
                gsap.to(el, { x: x * 0.15, y: y * 0.15, duration: 0.3, ease: 'power2.out' });
            });
            el.addEventListener('mouseleave', function () {
                gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.5)' });
            });
        });
    }

    /* ------------------------------------------------------------------
       9. STICKY HEADER — Glassmorphic, always visible
       ------------------------------------------------------------------ */
    function initHeaderEffects() {
        var header = document.querySelector('[data-elementor-type="header"]') ||
                     document.querySelector('.site-header') ||
                     document.querySelector('#masthead');
        if (!header) return;

        /* Ensure header is fixed positioned */
        header.style.setProperty('position', 'fixed', 'important');
        header.style.setProperty('top', '0', 'important');
        header.style.setProperty('left', '0', 'important');
        header.style.setProperty('right', '0', 'important');
        header.style.setProperty('z-index', '9999', 'important');
        header.style.setProperty('width', '100%', 'important');

        /* Increase blur on scroll */
        if (!prefersReducedMotion) {
            ScrollTrigger.create({
                start: 'top -50',
                end: 'max',
                onUpdate: function (self) {
                    if (self.scroll() > 50) {
                        header.style.setProperty('background', 'rgba(10, 14, 26, 0.95)', 'important');
                        header.style.setProperty('box-shadow', '0 4px 30px rgba(0,0,0,0.5)', 'important');
                    } else {
                        header.style.setProperty('background', 'rgba(10, 14, 26, 0.85)', 'important');
                        header.style.setProperty('box-shadow', '0 2px 8px rgba(0,0,0,0.3)', 'important');
                    }
                }
            });
        }
    }

    /* ------------------------------------------------------------------
       10. COLUMN STAGGER — e-child containers within e-parent
       ------------------------------------------------------------------ */
    function initColumnStagger() {
        if (prefersReducedMotion) return;
        var parents = document.querySelectorAll('.e-con.e-parent');
        parents.forEach(function (parent, index) {
            if (index === 0) return;
            var children = parent.querySelectorAll(':scope > .e-con-inner > .e-con.e-child');
            if (children.length < 2) return;

            gsap.fromTo(children,
                { opacity: 0, y: 30 },
                {
                    opacity: 1, y: 0,
                    duration: 0.7,
                    stagger: 0.15,
                    ease: 'power3.out',
                    scrollTrigger: { trigger: parent, start: 'top 80%', once: true }
                }
            );
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

        /* Re-force dark backgrounds after a short delay (for lazy-loaded content) */
        setTimeout(forceDarkBackgrounds, 1000);
        setTimeout(forceDarkBackgrounds, 3000);

        window.addEventListener('load', function () {
            forceDarkBackgrounds();
            ScrollTrigger.refresh();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
