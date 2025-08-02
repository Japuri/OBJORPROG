// Mobile menu toggle
const mobileMenuButton = document.getElementById('mobileMenuButton');
const mobileMenu = document.getElementById('mobileMenu');
if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}

// Main script, runs after the page is loaded
document.addEventListener('DOMContentLoaded', () => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (!isAuthenticated) return;

    // --- 1. HOSPITAL MAP LOGIC ---
    const initMap = () => {
        const geoapifyApiKey = '8a2011283bd148e489e83a87175f641d';
        const mapElement = document.getElementById('map');
        if (!mapElement) return;

        const resultsListElement = document.getElementById('results-list');
        const mapErrorElement = document.getElementById('map-error');
        const mapLayoutContainer = document.querySelector('.map-layout-container');

        const showError = (message) => {
            if (mapErrorElement) {
                mapErrorElement.textContent = message;
                mapErrorElement.classList.remove('hidden');
            }
            if (mapLayoutContainer) mapLayoutContainer.style.display = 'none';
        };

        if (!navigator.geolocation) {
            showError("Geolocation is not supported by your browser.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLat = position.coords.latitude;
                const userLon = position.coords.longitude;
                const map = L.map('map').setView([userLat, userLon], 13);
                L.tileLayer(`https://maps.geoapify.com/v1/tile/osm-bright/{z}/{x}/{y}.png?apiKey=${geoapifyApiKey}`, {
                    attribution: 'Powered by <a href="https://www.geoapify.com/" target="_blank">Geoapify</a> | © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
                }).addTo(map);

                const userIcon = L.icon({ iconUrl: `https://api.geoapify.com/v1/icon/?type=material&color=%231e90ff&icon=person&iconSize=large&apiKey=${geoapifyApiKey}`, iconSize: [38, 55], iconAnchor: [19, 53] });
                const hospitalIcon = L.icon({ iconUrl: `https://api.geoapify.com/v1/icon/?type=material&color=%23ff3333&icon=local_hospital&iconSize=large&apiKey=${geoapifyApiKey}`, iconSize: [38, 55], iconAnchor: [19, 53] });
                const hospitalIconHighlight = L.icon({ iconUrl: `https://api.geoapify.com/v1/icon/?type=material&color=%23b60000&icon=local_hospital&iconSize=xlarge&apiKey=${geoapifyApiKey}`, iconSize: [46, 66], iconAnchor: [23, 64] });

                L.marker([userLat, userLon], { icon: userIcon }).addTo(map).bindTooltip("Your Location");
                const placesApiUrl = `https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=circle:${userLon},${userLat},5000&bias=proximity:${userLon},${userLat}&limit=20&apiKey=${geoapifyApiKey}`;

                fetch(placesApiUrl)
                    .then(response => response.json())
                    .then(data => {
                        resultsListElement.innerHTML = '';
                        if (data.features.length === 0) {
                            resultsListElement.innerHTML = '<div class="p-4 text-center text-gray-500">No hospitals found within 5km.</div>';
                            return;
                        }

                        const foundHospitals = data.features.map(feature => feature.properties.name || 'Unnamed Hospital');
                        const doctorCards = document.querySelectorAll('.doctor-card-dark');

                        doctorCards.forEach((card, index) => {
                            const hospitalName = foundHospitals[index % foundHospitals.length];
                            card.dataset.hospitalName = hospitalName;
                        });

                        const allPossibleServices = ['Emergency Care', 'Cardiology', 'X-Ray', 'Pediatrics', 'Neurology', 'Oncology', 'Orthopedics'];
                        const getRandomServices = (count) => {
                            const shuffled = [...allPossibleServices].sort(() => 0.5 - Math.random());
                            return shuffled.slice(0, count);
                        };

                        data.features.forEach(place => {
                            const placeProps = place.properties;
                            const marker = L.marker([placeProps.lat, placeProps.lon], { icon: hospitalIcon }).addTo(map);
                            const listItem = document.createElement('div');
                            listItem.className = 'result-item';

                            const randomServices = getRandomServices(Math.floor(Math.random() * 2) + 2);
                            const servicesHTML = randomServices.map(service => `<span class="service-tag">${service}</span>`).join('');
                            const hospitalName = placeProps.name || 'N/A';

                            listItem.innerHTML = `
                                <div class="result-item-name">${hospitalName}</div>
                                <div class="result-item-address">${placeProps.address_line2 || ''}</div>
                                <div class="services-container">${servicesHTML}</div>
                                <button class="view-doctors-button" data-hospital-name="${hospitalName}">View Doctors & Book</button>
                            `;
                            resultsListElement.appendChild(listItem);

                            listItem.querySelector('.result-item-name').addEventListener('click', () => map.flyTo([placeProps.lat, placeProps.lon], 15));
                            listItem.addEventListener('mouseover', () => { marker.setIcon(hospitalIconHighlight); marker.setZIndexOffset(1000); });
                            listItem.addEventListener('mouseout', () => { marker.setIcon(hospitalIcon); marker.setZIndexOffset(0); });

                            listItem.querySelector('.view-doctors-button').addEventListener('click', (e) => {
                                const selectedHospital = e.target.dataset.hospitalName;
                                document.getElementById('booking-section').scrollIntoView({ behavior: 'smooth' });
                                window.filterDoctorsByHospital(selectedHospital);
                            });
                        });
                    }).catch(err => showError("Could not fetch nearby hospitals."));
            },
            (error) => { /* Error handling */ }
        );
    };

    // --- 2. APPOINTMENT BOOKING LOGIC ---
    const initBooking = () => {
        const step1 = document.getElementById('step1');
        if (!step1) return;

        const bookingState = { hospitalName: null, doctorId: null, doctorName: null, date: null, time: null };
        const step2 = document.getElementById('step2');
        const step3 = document.getElementById('step3');
        const specialtyFilter = document.getElementById('specialty');
        const doctorCards = document.querySelectorAll('.doctor-card-dark');
        const timeSlots = document.querySelectorAll('.time-slot-dark:not(.cursor-not-allowed)');
        const datePicker = document.getElementById('appointmentDate');
        const selectedDoctorNameEl = document.getElementById('selectedDoctorName');
        const confirmDoctorEl = document.getElementById('confirmDoctor');
        const confirmDateEl = document.getElementById('confirmDate');
        const confirmTimeEl = document.getElementById('confirmTime');
        const backButton = document.getElementById('backButton');
        const confirmBookingButton = document.getElementById('confirmBookingButton');
        const csrfToken = document.getElementById('csrf_token_input').value;
        const bookingTitleEl = document.getElementById('booking-section-title');
        const bookingSubtitle = document.getElementById('booking-subtitle');
        const showAllDoctorsBtn = document.getElementById('show-all-doctors');

        // --- NEW: Add specialty text dynamically ---
        doctorCards.forEach(card => {
            const specialty = card.dataset.specialty;
            const specialtyEl = document.createElement('p');
            specialtyEl.className = 'text-indigo-400 doctor-specialty-display';
            specialtyEl.textContent = specialty.charAt(0).toUpperCase() + specialty.slice(1);
            card.appendChild(specialtyEl);
        });
        // --- END NEW ---

        const filterDoctors = (hospitalName) => {
            bookingState.hospitalName = hospitalName;
            bookingTitleEl.textContent = `Book at ${hospitalName}`;
            bookingSubtitle.textContent = `Showing doctors for ${hospitalName}.`;
            showAllDoctorsBtn.classList.remove('hidden');
            let visibleDoctors = 0;

            doctorCards.forEach(card => {
                if (card.dataset.hospitalName === hospitalName) {
                    card.style.display = 'block';
                    visibleDoctors++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (visibleDoctors === 0) {
                bookingSubtitle.innerHTML = `No doctors found for ${hospitalName}. <span class="text-amber-400">Showing all doctors instead.</span>`;
                showAllDoctors();
            }
        };

        window.filterDoctorsByHospital = filterDoctors;

        const showAllDoctors = () => {
            doctorCards.forEach(card => {
                card.style.display = 'block';
                const specialtyEl = card.querySelector('.doctor-specialty-display');
                if (specialtyEl) specialtyEl.style.display = 'block'; // Ensure it's visible
            });
            bookingTitleEl.textContent = 'Book an Appointment';
            bookingSubtitle.textContent = 'Select a hospital from the map above or choose from the doctors below.';
            showAllDoctorsBtn.classList.add('hidden');
            specialtyFilter.value = 'all';
            bookingState.hospitalName = null;
        };

        showAllDoctorsBtn.addEventListener('click', showAllDoctors);

        // --- UPDATED: Specialty filter logic ---
        specialtyFilter.addEventListener('change', (e) => {
            const selectedSpecialty = e.target.value;
            doctorCards.forEach(card => {
                const specialtyEl = card.querySelector('.doctor-specialty-display');

                // Logic to show/hide the whole card
                if (selectedSpecialty === 'all' || card.dataset.specialty === selectedSpecialty) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }

                // Logic to show/hide the specialty text inside the card
                if (specialtyEl) {
                    if (selectedSpecialty === 'all') {
                        specialtyEl.style.display = 'block';
                    } else {
                        specialtyEl.style.display = 'none';
                    }
                }
            });
        });
        // --- END UPDATE ---

        doctorCards.forEach(card => {
            card.addEventListener('click', () => {
                bookingState.hospitalName = card.dataset.hospitalName;
                bookingState.doctorId = card.dataset.doctorId;
                bookingState.doctorName = card.dataset.doctorName;

                doctorCards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                selectedDoctorNameEl.textContent = bookingState.doctorName;

                step1.style.opacity = '0.5';
                step2.classList.remove('hidden');
                step3.classList.add('hidden');
            });
        });

        timeSlots.forEach(slot => {
            slot.addEventListener('click', () => {
                if (!datePicker.value) { alert('Please select a date first.'); return; }
                bookingState.date = datePicker.value;
                bookingState.time = slot.textContent;
                timeSlots.forEach(s => s.classList.remove('selected'));
                slot.classList.add('selected');
                confirmDoctorEl.textContent = bookingState.doctorName;
                confirmDateEl.textContent = new Date(bookingState.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
                confirmTimeEl.textContent = bookingState.time;
                step2.style.opacity = '0.5';
                step3.classList.remove('hidden');
            });
        });

        backButton.addEventListener('click', () => {
            step3.classList.add('hidden');
            step2.style.opacity = '1';
        });

        confirmBookingButton.addEventListener('click', () => {
            if (!bookingState.doctorId) {
                alert('Please select a doctor first.');
                return;
            }
            confirmBookingButton.disabled = true;
            confirmBookingButton.textContent = 'Booking...';

            fetch('/api/book-appointment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(bookingState)
            })
            .then(response => {
                if (response.ok) { return response.json(); }
                throw new Error('Server responded with an error.');
            })
            .then(data => {
                alert('Booking Confirmed! A confirmation email has been sent.');
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to book appointment. Please try again.');
                confirmBookingButton.disabled = false;
                confirmBookingButton.textContent = 'Confirm Booking';
            });
        });
    };

    // Initialize both features safely
    try {
        initMap();
    } catch (e) {
        console.error("Error initializing map:", e);
    }

    try {
        initBooking();
    } catch (e) {
        console.error("Error initializing booking form:", e);
    }
});


// ... (keep your existing mobile menu, initMap, and initBooking functions)

// Main script, runs after the page is loaded
document.addEventListener('DOMContentLoaded', () => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (!isAuthenticated) return;

    // ... (initMap and initBooking functions)

    // --- 3. UPDATED: AI CHAT ASSISTANT LOGIC ---
    const initAIChat = () => {
        const chatBubble = document.getElementById('ai-chat-bubble');
        const chatWindow = document.getElementById('ai-chat-window');
        const closeChatButton = document.getElementById('close-chat-button');
        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        const chatMessages = document.getElementById('chat-messages');
        const csrfToken = document.getElementById('csrf_token_input').value;

        if (!chatBubble) return;

        const toggleChatWindow = () => {
            chatWindow.classList.toggle('visible');
        };

        chatBubble.addEventListener('click', toggleChatWindow);
        closeChatButton.addEventListener('click', toggleChatWindow);

        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const userMessage = chatInput.value.trim();
            if (!userMessage) return;

            appendMessage(userMessage, 'user');
            chatInput.value = '';
            appendMessage('...', 'ai', true); // Show a "typing" indicator

            // --- UPDATED: Send message to the Django backend ---
            fetch('/api/ai-chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                if (data.reply) {
                    updateTypingIndicator(data.reply);
                } else {
                    updateTypingIndicator('Sorry, an error occurred.');
                }
            })
            .catch(error => {
                console.error('AI Chat Error:', error);
                updateTypingIndicator('Sorry, I was unable to connect. Please try again later.');
            });
        });

        const appendMessage = (text, sender, isTyping = false) => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}-message`;

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'chat-bubble';
            bubbleDiv.textContent = text;

            if (isTyping) {
                bubbleDiv.id = 'typing-indicator';
            }

            messageDiv.appendChild(bubbleDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        const updateTypingIndicator = (text) => {
            const typingBubble = document.getElementById('typing-indicator');
            if (typingBubble) {
                typingBubble.textContent = text;
                typingBubble.id = '';
            }
        };
    };

    // Initialize all features safely
    try {
        initMap();
    } catch (e) {
        console.error("Error initializing map:", e);
    }
    try {
        initBooking();
    } catch (e) {
        console.error("Error initializing booking form:", e);
    }
    try {
        initAIChat();
    } catch (e) {
        console.error("Error initializing AI Chat:", e);
    }
});

