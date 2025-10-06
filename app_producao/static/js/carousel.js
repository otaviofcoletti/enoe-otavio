// Modern Carousel with auto-play and improved UX
class ModernCarousel {
    constructor() {
        this.slideIndex = 1;
        this.autoSlideInterval = null;
        this.autoSlideDelay = 5000; // 5 seconds
        this.isHovered = false;
        
        this.init();
    }
    
    init() {
        this.showSlides(this.slideIndex);
        this.startAutoSlide();
        this.addEventListeners();
    }
    
    // Controle "Próximo/Anterior"
    plusSlides(n) {
        this.showSlides(this.slideIndex += n);
        this.resetAutoSlide();
    }
    
    // Controle dos Indicadores
    currentSlide(n) {
        this.showSlides(this.slideIndex = n);
        this.resetAutoSlide();
    }
    
    showSlides(n) {
        const slides = document.getElementsByClassName("mySlides");
        const dots = document.getElementsByClassName("dot");
        
        if (!slides.length) return;
        
        if (n > slides.length) { this.slideIndex = 1; }
        if (n < 1) { this.slideIndex = slides.length; }
        
        // Hide all slides
        for (let i = 0; i < slides.length; i++) {
            slides[i].classList.remove("active");
            slides[i].style.display = "none";
        }
        
        // Remove active class from dots
        for (let i = 0; i < dots.length; i++) {
            dots[i].classList.remove("active");
        }
        
        // Show current slide
        if (slides[this.slideIndex - 1]) {
            slides[this.slideIndex - 1].style.display = "block";
            slides[this.slideIndex - 1].classList.add("active");
        }
        
        // Activate current dot
        if (dots[this.slideIndex - 1]) {
            dots[this.slideIndex - 1].classList.add("active");
        }
    }
    
    nextSlide() {
        this.plusSlides(1);
    }
    
    prevSlide() {
        this.plusSlides(-1);
    }
    
    startAutoSlide() {
        if (this.autoSlideInterval) return;
        
        this.autoSlideInterval = setInterval(() => {
            if (!this.isHovered) {
                this.nextSlide();
            }
        }, this.autoSlideDelay);
    }
    
    stopAutoSlide() {
        if (this.autoSlideInterval) {
            clearInterval(this.autoSlideInterval);
            this.autoSlideInterval = null;
        }
    }
    
    resetAutoSlide() {
        this.stopAutoSlide();
        this.startAutoSlide();
    }
    
    addEventListeners() {
        const container = document.querySelector('.slideshow-container');
        if (!container) return;
        
        // Pause auto-slide on hover
        container.addEventListener('mouseenter', () => {
            this.isHovered = true;
        });
        
        container.addEventListener('mouseleave', () => {
            this.isHovered = false;
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.prevSlide();
            } else if (e.key === 'ArrowRight') {
                this.nextSlide();
            }
        });
        
        // Touch/swipe support for mobile
        this.addTouchSupport(container);
    }
    
    addTouchSupport(container) {
        let startX = 0;
        let endX = 0;
        
        container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });
        
        container.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            this.handleSwipe();
        });
        
        const handleSwipe = () => {
            const swipeThreshold = 50;
            const diff = startX - endX;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    this.nextSlide(); // Swipe left - next slide
                } else {
                    this.prevSlide(); // Swipe right - previous slide
                }
            }
        };
        
        this.handleSwipe = handleSwipe;
    }
}

// Global functions for backward compatibility
let carousel;

function plusSlides(n) {
    if (carousel) {
        carousel.plusSlides(n);
    }
}

function currentSlide(n) {
    if (carousel) {
        carousel.currentSlide(n);
    }
}

// Initialize carousel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    carousel = new ModernCarousel();
});

// Fallback initialization if DOMContentLoaded already fired
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!carousel) {
            carousel = new ModernCarousel();
        }
    });
} else {
    carousel = new ModernCarousel();
}
