from django.http import HttpResponse

class StripeWebhookHandler:
    """
    Stripe webhook handler
    """
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        pass

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
