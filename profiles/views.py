# Importing necessary Django utilities
from django.shortcuts import render, get_object_or_404  # Used to render templates and safely fetch objects
from django.contrib import messages  # Used to pass one-time messages to templates (like success notifications)
from django.contrib.auth.decorators import login_required
# Importing the UserProfile model and associated form
from .models import UserProfile
from .forms import UserProfileForm

# Importing the Order model from the checkout app
from checkout.models import Order

@login_required
def profile(request):
    """
    Display the user's profile and allow updates via a form.
    Also fetch and display the user's past orders.
    """
    # Get the UserProfile object for the currently logged-in user
    profile = get_object_or_404(UserProfile, user=request.user)

    # If the form has been submitted (POST request)
    if request.method == 'POST':
        # Populate form with POST data and bind it to the existing profile
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Save the updated profile data
            form.save()
            # Display a success message to the user
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:  # If not POST, display the form pre-filled with existing profile data
        form = UserProfileForm(instance=profile)

    # Retrieve all orders associated with this user profile
    orders = profile.orders.all()

    # Render the profile page with the form and order list
    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True  # Optional context variable that may be used for conditional display in the template
    }

    return render(request, template, context)


def order_history(request, order_number):
    """
    Display a past order confirmation page from the user's order history.
    """
    # Safely fetch the Order by its number or return 404 if not found
    order = get_object_or_404(Order, order_number=order_number)

    # Notify the user that this is a historical confirmation (not a new order)
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    # Render the same template used for a successful checkout, but indicate this came from the profile
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True  # This flag can help modify display in the template (e.g., hide "continue shopping" links)
    }

    return render(request, template, context)
