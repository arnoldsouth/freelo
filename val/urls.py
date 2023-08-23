from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_val, name="landing_val"),
    path("profile/", views.search_val, name="search_val"),
    path("leaderboards/", views.leaderboards_val, name="leaderboards_val"),
]
