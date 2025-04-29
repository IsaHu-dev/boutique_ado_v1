# Django imports for views, redirection, messaging, settings, and database access
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

# Import local forms and models
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

# Import Stripe API
import stripe

def checkout(request):
    """
    Handle the checkout process:
    - If GET: display the checkout form and create Stripe payment intent
    - If POST: validate form, create order, create line items, handle errors, redirect to success
    """
    # Retrieve Stripe keys from settings
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Handle form submission
    if request.method == 'POST':
        bag = request.session.get('bag', {})  # Get bag contents from session

        # Collect form input data
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }

        # Instantiate and validate order form
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()  # Save the order object

            # Create line items for each product in the bag
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    # If item_data is just a quantity
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    # If item_data includes sizes (e.g., clothing)
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    # If the product is not found, show error and delete incomplete order
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Store user's save-info preference in session
            request.session['save_info'] = 'save-info' in request.POST

            # Redirect to success page
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            # If form is invalid, show an error message
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:
        # If GET request and bag is empty, redirect user to products page
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))
        
        # Prepare Stripe payment intent
        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)  # Convert to smallest currency unit (e.g., pence)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        
        order_form = OrderForm()  # Instantiate empty order form

        # Warn if Stripe public key is not configured
        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. \
                Did you forget to set it in your environment?')

        # Render checkout page
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,  # Used by Stripe JS
        }

        return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts:
    - Display confirmation
    - Clear session bag
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    # Show success message with order number and email
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # Remove bag from session after checkout is completed
    if 'bag' in request.session:
        del request.session['bag']

    # Render checkout success page
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
