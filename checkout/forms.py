# Import Django's built-in forms module
from django import forms

# Import the Order model from the current app's models
from .models import Order


# Define a form class based on the Order model
class OrderForm(forms.ModelForm):
    # Meta subclass to specify form settings
    class Meta:
        # Link this form to the Order model
        model = Order
        # Specify the fields from the model to include in the form
        fields = (
            'full_name', 'email', 'phone_number',
            'street_address1', 'street_address2',
            'town_or_city', 'postcode', 'country',
            'county',
        )

    # Override the __init__ method to customize the form fields
    def __init__(self, *args, **kwargs):
        """
        Customize form fields:
        - Add placeholders
        - Add CSS classes
        - Remove auto-generated labels
        - Set autofocus on the first field
        """
        # Call the parent __init__ method to initialize the form
        super().__init__(*args, **kwargs)

        # Define placeholder text for each field
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        # Set the autofocus attribute on the 'full_name' field
        self.fields['full_name'].widget.attrs['autofocus'] = True

        # Loop through all fields in the form
        for field in self.fields:
            # If the field is required, add an asterisk to the placeholder
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]

            # Set the placeholder text for the field
            self.fields[field].widget.attrs['placeholder'] = placeholder
            # Add a custom CSS class to the field (for Stripe styling)
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            # Remove the default label for a cleaner look (using placeholders instead)
            self.fields[field].label = False
