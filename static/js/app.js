document.addEventListener('DOMContentLoaded', () => {

    // --- Mobile Navigation Toggle ---
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-links');

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            // Change icon from bars to 'X' and back
            if (navMenu.classList.contains('active')) {
                navToggle.innerHTML = '<i class="fas fa-times"></i>';
            } else {
                navToggle.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
    }

    // --- Footer: Auto-update Current Year ---
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // --- NEW: Staggered Fade-in Animation Logic ---
    const animatedElements = document.querySelectorAll('.hero-animate');
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1 // Trigger when 10% of the element is visible
        });

        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }

    // --- NEW: Typing Effect Logic ---
    const typingElement = document.getElementById('typing-effect');
    if (typingElement) {
        const words = ["Data Scientist", "ML Engineer", "Data Engineer", "Data Analyst"];
        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;

        function typeWriter() {
            const currentWord = words[wordIndex];
            
            if (isDeleting) {
                // Remove characters
                typingElement.textContent = currentWord.substring(0, charIndex - 1);
                charIndex--;
            } else {
                // Add characters
                typingElement.textContent = currentWord.substring(0, charIndex + 1);
                charIndex++;
            }

            let typeSpeed = 150;
            if (isDeleting) {
                typeSpeed /= 2; // Faster when deleting
            }

            // Check if word is fully typed
            if (!isDeleting && charIndex === currentWord.length) {
                typeSpeed = 2000; // Pause at end of word
                isDeleting = true;
            } 
            // Check if word is fully deleted
            else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex = (wordIndex + 1) % words.length; // Move to next word
                typeSpeed = 500; // Pause before new word
            }

            setTimeout(typeWriter, typeSpeed);
        }
        typeWriter(); // Start the effect
    }

    // --- NEW: 3D Tilt Effect Logic ---
    const heroSection = document.getElementById('hero-section');
    const featuredGrid = document.getElementById('featured-grid');

    if (heroSection && featuredGrid) {
        heroSection.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            const { width, height, left, top } = heroSection.getBoundingClientRect();

            // Get mouse position relative to the center of the hero section
            const x = (clientX - left - width / 2) / (width / 2); // -1 to 1
            const y = (clientY - top - height / 2) / (height / 2); // -1 to 1

            const tiltAmount = 10; // Max tilt in degrees

            // Apply the 3D rotation
            featuredGrid.style.transform = `rotateY(${x * tiltAmount}deg) rotateX(${-y * tiltAmount}deg)`;
        });

        // Reset when mouse leaves
        heroSection.addEventListener('mouseleave', () => {
            featuredGrid.style.transform = `rotateY(0deg) rotateX(0deg)`;
        });
    }


    // --- Project Page Filtering Logic ---
    // (This code remains unchanged, it just runs when on the /projects page)
    const projectGrid = document.getElementById('project-grid');
    const searchFilter = document.getElementById('search-filter');
    const roleFilter = document.getElementById('role-filter');
    const techFilter = document.getElementById('tech-filter');
    
    const allProjectCards = projectGrid ? Array.from(projectGrid.getElementsByClassName('project-card')) : [];
    
    let currentFilters = {
        search: '',
        role: 'All',
        tech: 'All'
    };

    function applyProjectFilters() {
        if (!projectGrid) return; // Exit if not on project page

        let visibleCount = 0;

        allProjectCards.forEach(card => {
            const title = card.querySelector('h4').textContent.toLowerCase();
            const description = card.querySelector('.project-card-desc').textContent.toLowerCase();
            const cardRole = card.dataset.role;
            const cardTechs = card.dataset.tech.toLowerCase();

            // 1. Check Search Filter
            const searchMatch = (
                title.includes(currentFilters.search) || 
                description.includes(currentFilters.search)
            );

            // 2. Check Role Filter
            const roleMatch = (
                currentFilters.role === 'All' || 
                cardRole === currentFilters.role
            );
            
            // 3. Check Tech Filter
            const techMatch = (
                currentFilters.tech === 'All' || 
                cardTechs.includes(currentFilters.tech.toLowerCase())
            );

            // Show or hide the card
            if (searchMatch && roleMatch && techMatch) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Show 'no results' message
        let noResultsMessage = document.getElementById('project-grid-message');
        if (!noResultsMessage && allProjectCards.length > 0) {
            noResultsMessage = document.createElement('p');
            noResultsMessage.id = 'project-grid-message';
            noResultsMessage.className = 'text-secondary';
            noResultsMessage.style.textAlign = 'center';
            projectGrid.appendChild(noResultsMessage);
        }
        
        if (noResultsMessage) {
            if (visibleCount === 0) {
                noResultsMessage.textContent = 'No projects match your filters.';
                noResultsMessage.style.display = 'block';
            } else {
                noResultsMessage.style.display = 'none';
            }
        }
    }

    // Add Event Listeners to filters
    if (searchFilter) {
        searchFilter.addEventListener('keyup', (e) => {
            currentFilters.search = e.target.value.toLowerCase();
            applyProjectFilters();
        });
    }

    if (roleFilter) {
        roleFilter.addEventListener('change', (e) => {
            if (e.target.name === 'role') {
                currentFilters.role = e.target.value;
                applyProjectFilters();
            }
        });
    }

    if (techFilter) {
        techFilter.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-tag')) {
                techFilter.querySelectorAll('.filter-tag').forEach(tag => tag.classList.remove('active'));
                e.target.classList.add('active');
                
                currentFilters.tech = e.target.dataset.tech;
                applyProjectFilters();
            }
        });
    }

    // Trigger filter logic on load ONLY if we are on the projects page
    if (projectGrid) {
        applyProjectFilters();
    }
});