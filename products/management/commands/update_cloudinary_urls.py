import os
from django.core.management.base import BaseCommand
from products.models import Product

CLOUDINARY_BASE = "https://res.cloudinary.com/dalw18spe/image/upload/v1/"

class Command(BaseCommand):
    help = "Update product.image_url from image file paths (assuming they've been uploaded to Cloudinary)"

    def handle(self, *args, **options):
        updated = 0
        for product in Product.objects.all():
            if product.image and not product.image_url:
                filename = os.path.basename(product.image.name)
                cloudinary_url = CLOUDINARY_BASE + filename

                product.image_url = cloudinary_url
                product.save(update_fields=["image_url"])
                self.stdout.write(self.style.SUCCESS(f"Updated {product.name}: {cloudinary_url}"))
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done. {updated} products updated."))
