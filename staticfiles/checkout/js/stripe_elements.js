/*
    Core logic/payment flow from Stripe docs:
    https://stripe.com/docs/payments/accept-a-payment
*/

// Get Stripe public key and client secret from hidden HTML elements and parse them from JSON
const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);

// Initialize Stripe and set up Elements
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

// Define the style for the card input
const style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'  // Light grey placeholder
        }
    },
    invalid: {
        color: '#dc3545',       // Red text for invalid input
        iconColor: '#dc3545'    // Red icon color
    }
};

// Create the card element using defined style and mount it to the DOM
const card = elements.create('card', { style: style });
card.mount('#card-element');

// Handle real-time validation errors from Stripe Elements
card.addEventListener('change', function (event) {
    const errorDiv = document.getElementById('card-errors');
    if (event.error) {
        // Display error message with icon
        const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        errorDiv.innerHTML = html;
    } else {
        // Clear error message
        errorDiv.textContent = '';
    }
});

// Handle the payment form submission
const form = document.getElementById('payment-form');

form.addEventListener('submit', function (ev) {
    ev.preventDefault();  // Prevent default form submission

    // Disable card input and button to prevent multiple submissions
    card.update({ disabled: true });
    document.getElementById('submit-button').disabled = true;

    // Toggle UI to show loading spinner
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // Get user preference to save info and CSRF token
    const saveInfo = $('#id-save-info').prop('checked');
    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Data to cache checkout info in the session before confirming payment
    const postData = {
        csrfmiddlewaretoken: csrfToken,
        client_secret: clientSecret,
        save_info: saveInfo,
    };

    const url = '/checkout/cache_checkout_data/';

    // Post data to Django view to cache user checkout info
    $.post(url, postData).done(function () {
        // After successful caching, confirm the card payment
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        }).then(function (result) {
            // If there is an error, show it and re-enable the form
            if (result.error) {
                const errorDiv = document.getElementById('card-errors');
                const html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>
                `;
                errorDiv.innerHTML = html;
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ disabled: false });
                document.getElementById('submit-button').disabled = false;
            } else {
                // If payment was successful, submit the form
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // If the POST to cache data fails, reload the page to trigger Django error messages
        location.reload();
    });
});
