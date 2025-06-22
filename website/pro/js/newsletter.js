/**
 * newsletter.js
 *
 * Handles the newsletter subscription form functionality for the professional (B2B) footer.
 * It sends the subscription request to the specific B2B newsletter endpoint.
 */

document.addEventListener('DOMContentLoaded', () => {
    const proNewsletterForm = document.getElementById('pro-newsletter-form');

    if (proNewsletterForm) {
        proNewsletterForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const emailInput = document.getElementById('pro-newsletter-email');
            const feedbackDiv = document.getElementById('pro-newsletter-feedback');
            const email = emailInput.value;

            // Simple email validation
            if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
                feedbackDiv.textContent = 'Please enter a valid email address.';
                feedbackDiv.className = 'newsletter-feedback error';
                return;
            }

            try {
                // This endpoint should correspond to your B2B newsletter route in the backend
                const response = await fetch('/api/newsletter/b2b/subscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: email }),
                });

                const result = await response.json();

                if (response.ok) {
                    feedbackDiv.textContent = result.message || 'Thank you for subscribing!';
                    feedbackDiv.className = 'newsletter-feedback success';
                    emailInput.value = ''; // Clear the input on success
                } else {
                    // Display specific error from API or a generic one
                    throw new Error(result.message || 'Subscription failed. Please try again.');
                }
            } catch (error) {
                feedbackDiv.textContent = error.message;
                feedbackDiv.className = 'newsletter-feedback error';
            }
        });
    }
});
