from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_lol, name="landing_lol"),
    path("profile/", views.search_lol, name="search_lol"),
    path("leaderboards/", views.leaderboards_lol, name="leaderboards_lol"),
]
