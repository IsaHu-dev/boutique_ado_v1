from django.contrib import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
]