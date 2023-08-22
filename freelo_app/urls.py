from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_freelo_app, name="landing_freelo_app"),
]
