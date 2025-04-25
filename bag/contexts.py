# Import necessary modules
from decimal import Decimal  # For precise decimal calculations (important for money)
from django.conf import settings  # To access project-wide settings
from django.shortcuts import get_object_or_404  # To fetch objects or return 404 if not found
from products.models import Product  # Import the Product model

def bag_contents(request):
    """
    Process the user's shopping bag stored in the session,
    calculate totals, delivery cost, and prepare context data
    for templates (like a bag summary or checkout page).
    """

    bag_items = []  # List to hold detailed info about each item in the bag
    total = 0  # Total cost of all items
    product_count = 0  # Total number of items
    bag = request.session.get('bag', {})  # Get the bag dictionary from session, or empty dict if none

    # Ensure bag is a dictionary
    if not isinstance(bag, dict):
        bag = {}

    # Loop through each item in the bag
    for item_id, item_data in bag.items():
        try:
            # If item_data is just an integer, it's a simple product without size options
            if isinstance(item_data, int):
                product = get_object_or_404(Product, pk=item_id)  # Fetch product or 404
                total += item_data * product.price  # Add to total cost
                product_count += item_data  # Add to total quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': item_data,
                    'product': product,
                })
            
            # If item_data is a dictionary, it has size variations
            elif isinstance(item_data, dict):
                product = get_object_or_404(Product, pk=item_id)  # Fetch product or 404
                items_by_size = item_data.get('items_by_size', {})
                if isinstance(items_by_size, dict):
                    for size, quantity in items_by_size.items():
                        total += quantity * product.price  # Add to total cost
                        product_count += quantity  # Add to total quantity
                        bag_items.append({
                            'item_id': item_id,
                            'quantity': quantity,
                            'product': product,
                            'size': size,
                        })
        except (Product.DoesNotExist, KeyError, TypeError):
            # Skip invalid items
            continue

    # Check if total is below the free delivery threshold
    if total < settings.FREE_DELIVERY_THRESHOLD:
        # Calculate delivery charge as a percentage of the total
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # Calculate how much more the user needs to spend to qualify for free delivery
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        # No delivery charge if threshold met
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context

    #
