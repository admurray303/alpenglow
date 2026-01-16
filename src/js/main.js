// Load business information from info.json and update the page
async function loadBusinessInfo() {
  try {
    const response = await fetch('assets/info.json');
    if (!response.ok) {
      throw new Error('Failed to load business information');
    }
    
    const info = await response.json();
    const phoneNumber = info.contact.phone.primary;
    
    if (phoneNumber) {
      updatePhoneNumbers(phoneNumber);
    }
    
    // Update service area if element exists
    if (info.service && info.service.serviceArea && info.service.serviceArea.length > 0) {
      updateServiceArea(info.service.serviceArea);
    }
    
    // Update contact information
    updateContactInfo(info);
    
    // Update business hours
    if (info.service && info.service.hours) {
      updateBusinessHours(info.service.hours);
    }
  } catch (error) {
    console.error('Error loading business information:', error);
  }
}

// Update all phone number displays and links
function updatePhoneNumbers(phoneNumber) {
  // Extract digits for tel: link (remove formatting)
  const phoneDigits = phoneNumber.replace(/\D/g, '');
  const telLink = `tel:${phoneDigits}`;
  
  // Find all elements with data-phone-display attribute
  const phoneElements = document.querySelectorAll('[data-phone-display]');
  
  phoneElements.forEach(element => {
    // Always update the href for tel: links
    if (element.tagName === 'A') {
      element.href = telLink;
    }
    
    // Update the displayed text only if it looks like a phone number placeholder
    // Don't update buttons that say "Call Now" or similar action text
    const currentText = element.textContent.trim();
    
    // Check if this is a phone number placeholder pattern (e.g., "(970) 000-0000")
    const isPhonePlaceholder = currentText.match(/\(?\d{3}\)?\s*000[-\s]?0000/) || 
                                currentText.includes('000-0000');
    
    // Check if this is an action button (like "Call Now") - action buttons should keep their text
    const isActionButton = !isPhonePlaceholder && 
                          (currentText.toLowerCase().includes('call') || 
                           currentText.toLowerCase().includes('phone') ||
                           currentText.toLowerCase().includes('contact'));
    
    // Only update text if it's a placeholder and not an action button
    if (isPhonePlaceholder && !isActionButton) {
      element.textContent = phoneNumber;
    }
  });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', loadBusinessInfo);

// Update service area display
function updateServiceArea(serviceAreas) {
  const serviceAreaElements = document.querySelectorAll('[data-service-area]');
  if (!serviceAreaElements || serviceAreaElements.length === 0) {
    return;
  }
  
  // Update all service area elements on the page
  serviceAreaElements.forEach(serviceAreaElement => {
    // Clear any existing content
    serviceAreaElement.innerHTML = '';
    
    // Check if this is a footer service area (should be bulleted list)
    const isFooter = serviceAreaElement.classList.contains('footer-service-areas');
    
    // Create elements for each service area
    serviceAreas.forEach(area => {
      if (isFooter) {
        // For footer: create list items
        const areaItem = document.createElement('li');
        const span = document.createElement('span');
        span.className = 'service-area-item';
        span.textContent = area;
        areaItem.appendChild(span);
        serviceAreaElement.appendChild(areaItem);
      } else {
        // For other pages: create spans (boxes)
        const areaItem = document.createElement('span');
        areaItem.className = 'service-area-item';
        areaItem.textContent = area;
        serviceAreaElement.appendChild(areaItem);
      }
    });
  });
}

// Update contact information (email and address)
function updateContactInfo(info) {
  // Update email
  const emailElement = document.querySelector('[data-email-display]');
  if (emailElement && info.contact && info.contact.email) {
    const emailLink = emailElement.querySelector('[data-email-link]');
    if (emailLink && info.contact.email.primary) {
      emailLink.href = `mailto:${info.contact.email.primary}`;
      emailLink.textContent = info.contact.email.primary;
    }
  }
  
  // Update address
  const addressElement = document.querySelector('[data-address-display]');
  if (addressElement && info.contact && info.contact.address) {
    const address = info.contact.address.fullAddress || 
                   `${info.contact.address.street}, ${info.contact.address.city}, ${info.contact.address.state} ${info.contact.address.zipCode}`;
    const addressText = addressElement.querySelector('.contact-address');
    if (addressText) {
      addressText.textContent = address;
    }
  }
}

// Update business hours display
function updateBusinessHours(hours) {
  const hoursElement = document.querySelector('[data-hours-display]');
  if (!hoursElement) {
    return;
  }
  
  // Check if this is the simplified format (contact page)
  if (hoursElement.classList.contains('contact-hours-simple')) {
    // For simplified format: Mon-Sat 8am - 5pm, Sun Closed
    if (hours.monday && hours.saturday) {
      const monTime = hours.monday.split(' - ')[0]; // Get start time from Monday
      const satTime = hours.saturday.split(' - ')[1]; // Get end time from Saturday
      // Always show "Closed" for Sunday on contact page
      hoursElement.innerHTML = `Mon-Sat ${monTime} - ${satTime}<br>Sun Closed`;
    }
    return;
  }
  
  // Clear any existing content for detailed format
  hoursElement.innerHTML = '';
  
  // Days of the week in order
  const days = [
    { key: 'monday', label: 'Monday' },
    { key: 'tuesday', label: 'Tuesday' },
    { key: 'wednesday', label: 'Wednesday' },
    { key: 'thursday', label: 'Thursday' },
    { key: 'friday', label: 'Friday' },
    { key: 'saturday', label: 'Saturday' },
    { key: 'sunday', label: 'Sunday' }
  ];
  
  // Create hour items for each day
  days.forEach(day => {
    if (hours[day.key]) {
      const hourItem = document.createElement('div');
      hourItem.className = 'hours-item';
      hourItem.innerHTML = `<strong>${day.label}</strong><span>${hours[day.key]}</span>`;
      hoursElement.appendChild(hourItem);
    }
  });
  
  // Add emergency hours if available
  if (hours.emergency) {
    const emergencyItem = document.createElement('div');
    emergencyItem.className = 'hours-item';
    emergencyItem.innerHTML = `<strong>Emergency</strong><span>${hours.emergency}</span>`;
    hoursElement.appendChild(emergencyItem);
  }
}

// Also update the year (existing functionality)
document.addEventListener('DOMContentLoaded', function() {
  const yearElement = document.getElementById('year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
  
  // Initialize gallery slideshow
  initGallerySlideshow();
});

// Gallery Slideshow
function initGallerySlideshow() {
  const galleryTrack = document.getElementById('galleryTrack');
  const prevButton = document.getElementById('galleryPrev');
  const nextButton = document.getElementById('galleryNext');
  
  if (!galleryTrack) return;
  
  // Gallery images - using the images from the Gallery folder
  const galleryImages = [
    'assets/images/Gallery/gallery-1.png',
    'assets/images/Gallery/gallery-2.png',
    'assets/images/Gallery/gallery-3.png',
    'assets/images/Gallery/gallery-4.png',
    'assets/images/Gallery/gallery-5.png'
  ];
  
  let currentIndex = galleryImages.length; // Start in the middle set for seamless looping
  let autoSlideInterval;
  let isTransitioning = false;
  
  // Function to create all images in the track with duplicates for seamless loop
  function initializeTrack() {
    galleryTrack.innerHTML = '';
    
    // Add duplicate images: [copy] [original] [copy] for seamless looping both ways
    const imagesToShow = [...galleryImages, ...galleryImages, ...galleryImages];
    
    imagesToShow.forEach((imageSrc, index) => {
      const img = document.createElement('img');
      img.src = imageSrc;
      img.alt = `Gallery image ${(index % galleryImages.length) + 1}`;
      img.className = 'gallery-image';
      galleryTrack.appendChild(img);
    });
  }
  
  // Function to update the track position with smooth transition
  function updateTrackPosition(instant = false) {
    if (isTransitioning && !instant) return;
    isTransitioning = true;
    
    // Calculate transform value - each image is 100% width (one photo at a time)
    const translateX = -(currentIndex * 100);
    galleryTrack.style.transition = instant ? 'none' : 'transform 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
    galleryTrack.style.transform = `translateX(${translateX}%)`;
    
    setTimeout(() => {
      isTransitioning = false;
      
      // If we've reached the end of the original set, jump to the duplicate set without animation
      if (currentIndex >= galleryImages.length * 2) {
        currentIndex = currentIndex - galleryImages.length;
        updateTrackPosition(true);
      }
      // If we've gone before the start of the original set, jump to the duplicate set at the end
      else if (currentIndex < galleryImages.length) {
        currentIndex = galleryImages.length + currentIndex;
        updateTrackPosition(true);
      }
    }, instant ? 0 : 1200); // Match transition duration
  }
  
  // Function to go to next slide
  function nextSlide() {
    if (isTransitioning) return;
    currentIndex++;
    updateTrackPosition();
  }
  
  // Function to go to previous slide
  function prevSlide() {
    if (isTransitioning) return;
    currentIndex--;
    updateTrackPosition();
  }
  
  // Function to restart auto-slide
  function restartAutoSlide() {
    clearInterval(autoSlideInterval);
    autoSlideInterval = setInterval(nextSlide, 5000); // 4 seconds
  }
  
  // Initialize
  initializeTrack();
  updateTrackPosition();
  
  // Event listeners
  if (nextButton) {
    nextButton.addEventListener('click', () => {
      nextSlide();
      restartAutoSlide();
    });
  }
  
  if (prevButton) {
    prevButton.addEventListener('click', () => {
      prevSlide();
      restartAutoSlide();
    });
  }
  
  // Auto-advance every 2 seconds
  restartAutoSlide();
}

// Mobile menu toggle
function initMobileMenu() {
  const toggle = document.querySelector('.mobile-menu-toggle');
  const header = document.querySelector('.site-header');
  
  if (toggle && header) {
    toggle.addEventListener('click', () => {
      header.classList.toggle('nav-open');
    });
  }
}

// Initialize mobile menu on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMobileMenu);
} else {
  initMobileMenu();
}

