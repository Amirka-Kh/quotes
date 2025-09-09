from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.random_quote, name="random"),
    path("add/", views.add_quote, name="add"),
]
