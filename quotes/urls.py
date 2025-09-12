from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.random_quote, name="random"),
    path("add/", views.add_quote, name="add"),
    path("like/<int:pk>/", views.like_quote, name="like"),
    path("dislike/<int:pk>/", views.dislike_quote, name="dislike"),
    path("<int:pk>/edit/", views.edit_quote, name="edit"),
    path("popular/", views.popular_quotes, name="popular"),
    path("health/", views.health_check, name="health"),
]
